"""Prepare a leakage-aware blinded evaluation manifest, without exposing reference labels.

Usage: python benchmark/prepare_blind_manifest.py
Creates benchmark/blind_manifest.json containing only variant, endpoint, and
reference provenance hash. Labels and expected directions are deliberately omitted.
No predictive accuracy is calculated.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
candidates = json.loads((ROOT / "benchmark/candidate_reference_panel.json").read_text())
controls = json.loads((ROOT / "benchmark/endpoint_control_candidates.json").read_text())["records"]

rows = []
for source_name, items in (("reference_panel", candidates), ("endpoint_controls", controls)):
    for row in items:
        identifier = "|".join((row["variant"], row["endpoint"], row["source"]))
        rows.append({
            "case_id": hashlib.sha256(identifier.encode()).hexdigest()[:16],
            "variant": row["variant"],
            "endpoint": row["endpoint"],
            "source_group_id": hashlib.sha256(row["source"].encode()).hexdigest()[:16],
            "reference_set": source_name,
            "evaluation_status": "not_eligible_unfrozen",
        })
rows.sort(key=lambda x: (x["variant"], x["endpoint"], x["case_id"]))
assert len({x["case_id"] for x in rows}) == len(rows), "Repeated variant-endpoint-source cases"
out = {
    "schema": "vwf-blinded-evaluation-manifest/0.1",
    "status": "design_only_not_a_blind_evaluation",
    "label_access": "withheld",
    "warning": "Source-group hashes can reveal study membership. Prediction operators must not access original candidate labels or control files.",
    "cases": rows,
}
path = ROOT / "benchmark/blind_manifest.json"
path.write_text(json.dumps(out, indent=2) + "\n")
print(f"Wrote {len(rows)} unfrozen cases to {path}")
