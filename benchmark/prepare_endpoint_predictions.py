"""Fail-closed endpoint-specific prediction preparation.

This module intentionally receives only a case ID, variant and endpoint, never
experimental outcome labels. It requires adjudicated publication provenance and
endpoint-matched evidence before a method can emit a directional prediction.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmark"
METHODS = ("KG_evidence_only", "structural_only", "integrated_KG_and_structural")
DIRECTIONS = {"increased", "reduced", "preserved", "abstain"}

def norm_endpoint(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower())

def evaluate_case(case, observations, verified_sources=None, structural_reports=None):
    """Return three auditable abstentions until verified endpoint evidence exists.

    verified_sources maps canonical publication URL to independently verified
    provenance metadata; structural_reports maps case ID to validated reports.
    Neither is populated automatically from the benchmark reference labels.
    """
    verified_sources = verified_sources or {}
    structural_reports = structural_reports or {}
    case_id, variant, endpoint = case["case_id"], case["variant"], case["endpoint"]
    matched = [
        o for o in observations
        if o.get("subject_id") == "VWF_p" + variant
        and norm_endpoint(o.get("endpoint")) == norm_endpoint(endpoint)
        and not o.get("duplicate_of")
    ]
    verified = [
        o for o in matched
        if verified_sources.get(o.get("source_url"), {}).get("independent_of_reference") is True
        and verified_sources[o["source_url"]].get("adjudicated") is True
    ]
    structural = structural_reports.get(case_id)
    valid_structural = bool(
        isinstance(structural, dict)
        and structural.get("verified_mapping") is True
        and structural.get("endpoint_specific_validation") is True
        and structural.get("independent_of_reference") is True
    )
    decisions = []
    for method in METHODS:
        blockers = []
        if method in ("KG_evidence_only", "integrated_KG_and_structural") and not verified:
            blockers.append("no_independently_adjudicated_endpoint_matched_kg_evidence")
        if method in ("structural_only", "integrated_KG_and_structural") and not valid_structural:
            blockers.append("no_validated_endpoint_specific_structural_report")
        # No calibrated decision rule is currently registered. Never derive
        # assay direction from qualitative text or generic contact/free-energy data.
        blockers.append("no_preregistered_calibrated_direction_rule")
        record = {
            "case_id": case_id,
            "variant": variant,
            "endpoint": endpoint,
            "method": method,
            "method_version": "prevalidation-0.1",
            "predicted_direction": "abstain",
            "eligible_for_scoring": False,
            "blockers": blockers,
            "candidate_exact_endpoint_observation_ids": [o["observation_id"] for o in matched],
            "verified_exact_endpoint_observation_ids": [o["observation_id"] for o in verified],
            "structural_report_verified": valid_structural,
        }
        record["record_hash"] = hashlib.sha256(
            json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        decisions.append(record)
    return decisions

def build():
    inventory = json.loads((BENCH / "case_evidence_inventory.json").read_text())
    snapshot = json.loads((BENCH / "evaluation_evidence_snapshot.json").read_text())
    # Explicit allowlist remains empty until independently curated and approved.
    verified_sources = {}
    structural_reports = {}
    decisions = []
    for case in inventory["cases"]:
        safe_case = {
            "case_id": case["case_id"],
            "variant": case["variant"],
            "endpoint": case["reference_endpoint"],
        }
        decisions.extend(evaluate_case(safe_case, snapshot["retained_observations"],
                                       verified_sources, structural_reports))
    assert len(decisions) == 3 * len(inventory["cases"])
    assert all(d["predicted_direction"] in DIRECTIONS and not d["eligible_for_scoring"]
               for d in decisions)
    out = {
        "schema": "vwf-endpoint-prediction-readiness/0.1",
        "status": "abstention_only_not_frozen_not_scoring_eligible",
        "method_count": len(METHODS),
        "case_count": len(inventory["cases"]),
        "predictions": decisions,
        "warning": "No directional predictions are permitted until source adjudication, structural endpoint validation, calibrated rules, and a frozen reference split are in place.",
    }
    (BENCH / "endpoint_prediction_readiness.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"cases": out["case_count"], "methods": out["method_count"],
                      "abstentions": len(decisions)}, indent=2))

if __name__ == "__main__":
    build()
