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
audit = {
    "schema": "vwf-benchmark-source-cluster-audit/0.1",
    "status": "provisional_no_holdout_assigned",
    "case_count": len(cases),
    "source_cluster_count": len(by_source),
    "variant_count": len(by_variant),
    "multi_case_source_clusters": sum(len(v) > 1 for v in by_source.values()),
    "multi_endpoint_variants": sum(len(v) > 1 for v in by_variant.values()),
    "warning": "Never split cases from one publication or one variant across training and test partitions; labels are public and no blind performance may be reported.",
}
(root / "benchmark/source_cluster_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
print(json.dumps(audit, indent=2))
