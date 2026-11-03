"""Validate the leakage-connected-component audit generated from the manifest."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "benchmark"
audit = json.loads((root / "source_cluster_audit.json").read_text())
manifest = json.loads((root / "blind_manifest.json").read_text())
cases = manifest["cases"]
assert audit["case_count"] == len(cases)
assert sum(audit["source_cluster_sizes"]) == len(cases)
assert sum(audit["leakage_connected_component_sizes"]) == len(cases)
assert audit["largest_leakage_component_size"] == max(audit["leakage_connected_component_sizes"])
assert audit["leakage_connected_component_count"] <= audit["source_cluster_count"]
assert audit["leakage_connected_component_count"] <= audit["variant_count"]
assert audit["status"] == "provisional_no_holdout_assigned"
assert audit["component_assignment_status"] == "not_assigned_all_cases_unfrozen"
assert audit["holdout_feasibility"] == "not_assessable_without_frozen_independent_references"
assert 0 <= audit["largest_leakage_component_fraction"] <= 1
assert abs(audit["largest_leakage_component_fraction"] * len(cases) - audit["largest_leakage_component_size"]) < 1e-9
assert sorted(audit["leakage_connected_component_sizes"], reverse=True) == audit["leakage_connected_component_sizes"]
print("Leakage cluster audit validated; no train/test partition assigned.")
