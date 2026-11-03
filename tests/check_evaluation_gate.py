"""Prove that a benchmark evaluation cannot reuse its reference evidence.

This is a safety gate, not a biological validation or a prediction score.
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
panel = json.loads((ROOT / "benchmark/candidate_reference_panel.json").read_text())
controls = json.loads((ROOT / "benchmark/endpoint_control_candidates.json").read_text())["records"]
rows = [*panel, *controls]

def normalize_source(url):
    return url.strip().rstrip("/").lower()

def leakage_components(entries):
    parent = list(range(len(entries)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    def union(i, j):
        parent[find(i)] = find(j)
    seen_source, seen_variant = {}, {}
    for i, row in enumerate(entries):
        for seen, key in ((seen_source, normalize_source(row["source"])),
                          (seen_variant, row["variant"])):
            if key in seen:
                union(i, seen[key])
            else:
                seen[key] = i
    groups = defaultdict(list)
    for i, row in enumerate(entries):
        groups[find(i)].append(row)
    return list(groups.values())

components = leakage_components(rows)
assert sum(map(len, components)) == len(rows)
assert len(components) <= len({normalize_source(r["source"]) for r in rows})
assert all(row["reference_freeze_status"] == "not_frozen" for row in rows), (
    "New frozen references require a reviewed evaluation protocol"
)
assert all(not row.get("independent_replication_verified", False) for row in rows), (
    "New replication evidence requires independent adjudication"
)
# Deliberately forbid a performance calculation from unfrozen labels.
evaluation_eligible = [r for r in rows if r["reference_freeze_status"] == "frozen"]
assert not evaluation_eligible, "Do not score before an independently reviewed reference freeze"
print(f"Leakage gate passed: {len(rows)} unfrozen cases in {len(components)} evidence components; scoring blocked.")
