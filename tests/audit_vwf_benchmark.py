#!/usr/bin/env python3
"""Audit VWF functional benchmark candidates. Never equate reported VWD subtype with a validated structural label."""
import json, pathlib, sys
root=pathlib.Path(__file__).resolve().parents[2]
path=root/"data/benchmark/vwf_functional_candidates.json"
data=json.loads(path.read_text())
required=("variant","reported_subtype","domain","reported_function","source","curation_status")
seen=set()
for row in data["variants"]:
    assert all(row.get(k) for k in required), row
    assert row["variant"] not in seen, row["variant"]
    seen.add(row["variant"])
    assert row["source"].startswith("https://"), row
    assert row["curation_status"]=="candidate_requires_primary_functional_validation", row
    assert row["measured_effect"] is None and row["benchmark_split"] is None, row
print(json.dumps({"candidate_count":len(seen),"subtypes":sorted({x["reported_subtype"] for x in data["variants"]}),"validated_training_labels":0,"status":"candidates_only; quantitative benchmarking must await primary functional measurements"},indent=2))
