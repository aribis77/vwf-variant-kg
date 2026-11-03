"""Audit publication clusters and repeated variants before any benchmark split."""
import json
from collections import defaultdict
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "benchmark/blind_manifest.json").read_text())
cases = manifest["cases"]
by_source = defaultdict(list)
by_variant = defaultdict(list)
for case in cases:
    by_source[case["source_group_id"]].append(case["case_id"])
    by_variant[case["variant"]].append(case["case_id"])
assert all(case["evaluation_status"] == "not_eligible_unfrozen" for case in cases)
assert all(len(group) > 0 for group in by_source.values())
assert sum(map(len, by_source.values())) == len(cases)
assert sum(map(len, by_variant.values())) == len(cases)

# A connected component joins cases that share either a variant or a source.
# Such cases must never be assigned to different benchmark partitions.
parent = list(range(len(cases)))
def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i
def union(a, b):
    parent[find(a)] = find(b)

first_source = {}
first_variant = {}
for i, case in enumerate(cases):
    for lookup, key in ((first_source, case["source_group_id"]), (first_variant, case["variant"])):
        if key in lookup:
            union(i, lookup[key])
        else:
            lookup[key] = i
components = defaultdict(list)
for i, case in enumerate(cases):
    components[find(i)].append(case["case_id"])
component_sizes = sorted((len(v) for v in components.values()), reverse=True)
assert sum(component_sizes) == len(cases)

audit = {
    "schema": "vwf-benchmark-source-cluster-audit/0.1",
    "status": "provisional_no_holdout_assigned",
    "case_count": len(cases),
    "source_cluster_count": len(by_source),
    "variant_count": len(by_variant),
    "multi_case_source_clusters": sum(len(v) > 1 for v in by_source.values()),
    "multi_endpoint_variants": sum(len(v) > 1 for v in by_variant.values()),
    "largest_source_cluster_size": max(map(len, by_source.values()), default=0),
    "largest_variant_cluster_size": max(map(len, by_variant.values()), default=0),
    "source_cluster_sizes": sorted((len(v) for v in by_source.values()), reverse=True),
    "leakage_connected_component_count": len(components),
    "leakage_connected_component_sizes": component_sizes,
    "largest_leakage_component_size": max(component_sizes, default=0),
    "largest_leakage_component_fraction": (max(component_sizes, default=0) / len(cases)) if cases else 0,
    "component_assignment_status": "not_assigned_all_cases_unfrozen",
    "holdout_feasibility": "not_assessable_without_frozen_independent_references",
    "warning": "Never split cases from one publication or one variant across training and test partitions; labels are public and no blind performance may be reported.",
}
(root / "benchmark/source_cluster_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
print(json.dumps(audit, indent=2))
