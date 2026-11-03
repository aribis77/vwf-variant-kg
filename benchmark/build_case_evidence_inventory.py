"""Produce case-specific, leakage-screened evidence inventories.

Only observation-level literature evidence is inventoried. This is not an
independent prediction and cannot be used for performance scoring.
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "benchmark"
panel = json.loads((root / "candidate_reference_panel.json").read_text())
controls = json.loads((root / "endpoint_control_candidates.json").read_text())["records"]
snapshot = json.loads((root / "evaluation_evidence_snapshot.json").read_text())
edge_audit = json.loads((root / "edge_provenance_review.json").read_text())
graph = json.loads((root / "evaluation_graph_snapshot.json").read_text())
observations = snapshot["retained_observations"]
all_cases = panel + controls
records = []
for i, case in enumerate(all_cases, 1):
    variant = case["variant"]
    subject = "VWF_p" + variant
    evidence = [o for o in observations if o.get("subject_id") == subject]
    records.append({
        "case_id": f"CASE_{i:03d}",
        "variant": variant,
        "reference_endpoint": case["endpoint"],
        "reference_freeze_status": case.get("reference_freeze_status", "unknown"),
        "retained_variant_observation_ids": [o["observation_id"] for o in evidence],
        "retained_variant_observation_endpoints": sorted({o.get("endpoint", "") for o in evidence}),
        "retained_variant_observation_count": len(evidence),
        "reference_direction_withheld_from_prediction_features": True,
        "kg_prediction": "abstain_not_run",
        "structure_prediction": "abstain_not_run",
        "integrated_prediction": "abstain_not_run",
        "evaluation_eligible": False,
        "limitations": "Variant-level evidence inventory is not endpoint-matched, independently adjudicated, or leakage-free at the derived-graph level.",
    })
assert len(records) == len(all_cases)
assert all(r["evaluation_eligible"] is False for r in records)
assert all(r["kg_prediction"] == "abstain_not_run" for r in records)
assert all(r["reference_direction_withheld_from_prediction_features"] for r in records)
result = {
    "schema": "vwf-case-evidence-inventory/0.1",
    "status": "audit_only_no_prediction_scoring",
    "cases": records,
    "counts": {
        "cases": len(records),
        "cases_with_retained_variant_observations": sum(r["retained_variant_observation_count"] > 0 for r in records),
        "cases_without_retained_variant_observations": sum(r["retained_variant_observation_count"] == 0 for r in records),
        "candidate_edges_excluded_from_prediction": len(edge_audit["candidate_sourced_edges"]),
        "retained_ontology_edges": len(graph["edges"]),
    },
    "warning": "No predictions have been generated; source filtering and evidence inventory do not demonstrate endpoint-specific predictive ability.",
}
(root / "case_evidence_inventory.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result["counts"], indent=2))
