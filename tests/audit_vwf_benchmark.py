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
    assert row["curation_status"] in {"candidate_requires_primary_functional_validation","primary_quantitative_functional_evidence_extracted"}, row
    assert row["benchmark_split"] is None, row
    if row["curation_status"]=="primary_quantitative_functional_evidence_extracted":
        assert row["primary_functional_evidence"] and row["measured_effect"], row
        for record in row["primary_functional_evidence"]:
            assert record["source"].startswith("https://") and record["unit"] and record["phenotype_axis"], record
    else:
        assert row["measured_effect"] is None, row
print(json.dumps({"candidate_count":len(seen),"subtypes":sorted({x["reported_subtype"] for x in data["variants"]}),"primary_functionally_curated":sum(x["curation_status"]=="primary_quantitative_functional_evidence_extracted" for x in data["variants"]),"validated_training_labels":0,"status":"candidates_only; quantitative benchmarking must await primary functional measurements"},indent=2))
