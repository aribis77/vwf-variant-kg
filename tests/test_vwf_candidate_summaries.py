#!/usr/bin/env python3
"""Candidate summary IDs must agree with discovery and never be promoted."""
import hashlib
import json
import tempfile
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
root=Path(__file__).resolve().parents[1]
spec=spec_from_file_location("audit",root/"scripts"/"audit_vwf_pilot.py")
module=module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)
    discovery={"esearchresult":{"idlist":["100312","106189"]}}
    summary={"result":{"uids":["100312","106189"],"100312":{"uid":"100312"},"106189":{"uid":"106189"}}}
    records=[]
    for provider,payload in (("clinvar_discovery",discovery),("clinvar_candidates",summary)):
        f=p/("R1315L_"+provider+".json")
        f.write_text(json.dumps(payload))
        records.append({"variant":"R1315L","provider":provider,"status":"retrieved_not_adjudicated",
                        "sha256":hashlib.sha256(f.read_bytes()).hexdigest()})
    (p/"manifest.json").write_text(json.dumps({"records":records}))
    result=module.review(p)
    assert result["findings"][1]["status"]=="candidate_summaries_retrieved"
    assert not result["findings"][1]["promotion_allowed"]
    assert result["reconciliation"][0]["status"]=="candidate_discovery_not_allele_verified"
    wrong={"result":{"uids":["999999"],"999999":{"uid":"999999"}}}
    f=p/"R1315L_clinvar_candidates.json"
    f.write_text(json.dumps(wrong))
    records[1]["sha256"]=hashlib.sha256(f.read_bytes()).hexdigest()
    (p/"manifest.json").write_text(json.dumps({"records":records}))
    assert module.review(p)["findings"][1]["status"]=="candidate_summaries_invalid"
print("Candidate summary ID reconciliation tests passed")
