#!/usr/bin/env python3
"""Offline regression checks for source auditing and non-promotion."""
import json
import hashlib
import tempfile
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location

root = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("audit", root / "scripts" / "audit_vwf_pilot.py")
module = module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp)
    clinvar = {"result": {"100312": {"uid": "100312", "title": "VWF test record"}}}
    ensembl = [{"input": "NM_000552.5:c.3944G>T", "assembly_name": "GRCh38",
                "seq_region_name": "12", "start": 6019474, "allele_string": "C/A",
                "transcript_consequences": [{"gene_symbol": "VWF", "protein_start": 1315,
                                             "amino_acids": "R/L", "transcript_id": "ENSTTEST"}]}]
    for name, obj in (("R1315L_clinvar", clinvar), ("R1315L_ensembl", ensembl)):
        (path / (name + ".json")).write_text(json.dumps(obj))
    manifest = {"records": [
        {"variant": "R1315L", "provider": "clinvar", "status": "retrieved_not_adjudicated",
         "raw_path": str(path / "R1315L_clinvar.json")},
        {"variant": "R1315L", "provider": "ensembl", "status": "retrieved_not_adjudicated",
         "raw_path": str(path / "R1315L_ensembl.json")},
        {"variant": "H1786D", "status": "requires_verified_nucleotide_hgvs"}
    ]}
    for item in manifest["records"]:
        if item.get("raw_path"):
            item["sha256"] = hashlib.sha256(Path(item["raw_path"]).read_bytes()).hexdigest()
    (path / "manifest.json").write_text(json.dumps(manifest))
    result = module.review(path)
    assert len(result["findings"]) == 3
    assert result["findings"][0]["status"] == "identifier_verified"
    assert result["findings"][1]["status"] == "protein_consequence_candidate"
    assert result["findings"][2]["status"] == "requires_verified_nucleotide_hgvs"
    assert all(not item["promotion_allowed"] for item in result["findings"])
    assert result["reconciliation"][0]["status"] == "partial_concordance_requires_allele_and_transcript_review"
    assert result["reconciliation"][1]["status"] == "insufficient_primary_sources"
    assert all(not x["promotion_allowed"] for x in result["reconciliation"])
    # A mismatched checksum must be rejected, not treated as a source hit.
    manifest["records"][0]["sha256"] = "0" * 64
    (path / "manifest.json").write_text(json.dumps(manifest))
    tampered = module.review(path)
    assert tampered["findings"][0]["status"] == "checksum_mismatch"
    assert tampered["reconciliation"][0]["status"] == "clinvar_identifier_unverified"
print("Offline source-audit tests passed; no records promoted.")
