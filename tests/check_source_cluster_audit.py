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
print("Leakage cluster audit validated; no train/test partition assigned.")
