"""Audit whether endpoint-specific calibration can begin without reference leakage.

No candidate reference case is used to fit thresholds or select features.
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "benchmark"
registry = json.loads((B / "endpoint_rule_registry.json").read_text())
panel = json.loads((B / "candidate_reference_panel.json").read_text())
controls = json.loads((B / "endpoint_control_candidates.json").read_text())["records"]
cases = panel + controls

def normalize(x):
    return " ".join(str(x or "").lower().split())

def family_for(endpoint):
    ep = normalize(endpoint)
    for family in registry["endpoint_families"]:
        if ep in [normalize(a) for a in family["endpoint_aliases"]]:
            return family["family"]
    return None

families = defaultdict(lambda: {"candidate_cases": 0, "frozen_cases": 0,
    "independently_adjudicated_cases": 0, "preserved_controls_verified": 0,
    "candidate_source_groups": set(), "unmapped_endpoints": set()})
unmapped = []
for case in cases:
    family = family_for(case["endpoint"])
    if family is None:
        unmapped.append({"variant": case["variant"], "endpoint": case["endpoint"]})
        continue
    item = families[family]
    item["candidate_cases"] += 1
    item["candidate_source_groups"].add(case.get("source_group") or case["source"])
    if case.get("reference_freeze_status") == "frozen":
        item["frozen_cases"] += 1
    if case.get("independent_adjudication") is True:
        item["independently_adjudicated_cases"] += 1
        if case.get("observed_direction") == "preserved":
            item["preserved_controls_verified"] += 1

rows = []
for family in registry["endpoint_families"]:
    item = families[family["family"]]
    rows.append({
        "family": family["family"],
        "candidate_cases": item["candidate_cases"],
        "candidate_source_groups": len(item["candidate_source_groups"]),
        "frozen_cases": item["frozen_cases"],
        "independently_adjudicated_cases": item["independently_adjudicated_cases"],
        "independently_adjudicated_preserved_controls": item["preserved_controls_verified"],
        "calibration_eligible": False,
        "blockers": [
            "no_separate_verified_training_cohort",
            "no_source_cluster_separated_calibration",
            "no_calibrated_direction_rule",
            "no_held_out_reference_freeze",
        ],
    })
out = {
    "schema": "vwf-calibration-readiness-audit/0.1",
    "status": "calibration_blocked",
    "candidate_case_count": len(cases),
    "mapped_candidate_case_count": sum(r["candidate_cases"] for r in rows),
    "unmapped_cases": unmapped,
    "endpoint_families": rows,
    "guardrail": "Candidate reference cases are counted only for feasibility; their outcome labels must never be used to train or tune prediction thresholds.",
}
assert out["mapped_candidate_case_count"] + len(unmapped) == len(cases)
assert not any(r["calibration_eligible"] for r in rows)
(B / "calibration_readiness_audit.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"candidate_cases": len(cases), "unmapped": len(unmapped),
                  "family_counts": {r["family"]: r["candidate_cases"] for r in rows}}, indent=2))
