#!/usr/bin/env python3
"""Regression tests for review-only source summaries."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=spec_from_file_location("summary",root/"scripts"/"build_vwf_source_summary.py")
module=module_from_spec(spec)
spec.loader.exec_module(module)
sample={"reconciliation":[
 {"variant":"R1315L","status":"partial_concordance_requires_allele_and_transcript_review","promotion_allowed":False},
 {"variant":"H1786D","status":"insufficient_primary_sources","promotion_allowed":False},
 {"variant":"R1306W","status":"unknown_external_status","promotion_allowed":True}
]}
result=module.summarize(sample)
assert result["schema"]=="vwf-source-audit-summary/0.1"
assert len(result["variants"])==3
assert result["variants"][2]["status"]=="unrecognized_review_status"
assert all(not row["clinical_classification_verified"] for row in result["variants"])
assert all(not row["allele_mapping_verified"] for row in result["variants"])
assert all(not row["integrated_clinical_score_available"] for row in result["variants"])
print("Source-summary regression checks passed")
