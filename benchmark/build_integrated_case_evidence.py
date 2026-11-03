"""Join structural consensus and KG observations into case-specific evidence summaries.

This is a descriptive integration, not a prediction. No outcome labels are
read. Structural features are never converted into assay direction.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "benchmark"

def integrate(cases, observations, consensus):
    by_variant = {x["variant"]: x for x in consensus}
    results = []
    for case in cases:
        variant = case["variant"]
        endpoint = " ".join(str(case["reference_endpoint"]).lower().split())
        exact = [o for o in observations
                 if o.get("subject_id") == "VWF_p" + variant
                 and " ".join(str(o.get("endpoint", "")).lower().split()) == endpoint
                 and not o.get("duplicate_of")]
        structure = by_variant.get(variant)
        results.append({
            "case_id": case["case_id"],
            "variant": variant,
            "endpoint": case["reference_endpoint"],
            "kg": {
                "exact_endpoint_observation_ids": sorted(o["observation_id"] for o in exact),
                "observation_count": len(exact),
                "provenance_status": "url_filtered_not_independently_adjudicated",
            },
            "structural": {
                "consensus_available": structure is not None,
                "distinct_pdb_count": structure["independent_pdb_count"] if structure else 0,
                "report_count": structure["report_count"] if structure else 0,
                "contact_change": structure["contact_change"] if structure else None,
                "delta_g_kcal_mol": structure["delta_g_kcal_mol"] if structure else None,
                "conservation_score": structure["conservation_score"] if structure else None,
                "per_structure": structure["per_structure"] if structure else [],
                "endpoint_specific_validation": False,
            },
            "integrated": {
                "evidence_present_in_both_arms": bool(exact and structure),
                "predicted_direction": "abstain",
                "functional_effect_conclusion": "not_established",
                "reason": "Structural features lack endpoint-specific calibration; KG source independence is not adjudicated.",
                "scoring_eligible": False,
            },
        })
    return results

def main():
    inventory = json.loads((B / "case_evidence_inventory.json").read_text())
    snapshot = json.loads((B / "evaluation_evidence_snapshot.json").read_text())
    structural = json.loads((B / "structural_feature_consensus.json").read_text())
    rows = integrate(inventory["cases"], snapshot["retained_observations"], structural["variants"])
    result = {
        "schema": "vwf-integrated-case-evidence/0.1",
        "status": "descriptive_not_calibrated",
        "case_count": len(rows),
        "cases_with_structural_consensus": sum(r["structural"]["consensus_available"] for r in rows),
        "cases_with_both_evidence_arms": sum(r["integrated"]["evidence_present_in_both_arms"] for r in rows),
        "cases": rows,
        "warning": "Not a functional predictor, independent validation, or clinical classification.",
    }
    assert all(r["integrated"]["predicted_direction"] == "abstain" for r in rows)
    (B / "integrated_case_evidence.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("case_count", "cases_with_structural_consensus", "cases_with_both_evidence_arms")}, indent=2))

if __name__ == "__main__":
    main()
