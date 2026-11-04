#!/usr/bin/env python3
"""Build a read-only, versioned source audit summary for portal review.

Only source metadata and review outcomes are exported. No patient data, no raw
ClinVar assertions, and no unreviewed genomic mappings are promoted.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

def summarize(audit):
    allowed = {
        "partial_concordance_requires_allele_and_transcript_review",
        "insufficient_primary_sources", "clinvar_identifier_unverified",
        "ensembl_protein_consequence_unverified",
    }
    variants = []
    for item in audit.get("reconciliation", []):
        status = item.get("status")
        if status not in allowed:
            status = "unrecognized_review_status"
        variants.append({
            "variant": item["variant"],
            "status": status,
            "clinical_classification_verified": False,
            "population_frequency_verified": False,
            "allele_mapping_verified": False,
            "integrated_clinical_score_available": False,
        })
    return {
        "schema": "vwf-source-audit-summary/0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "research_review_only",
        "variants": variants,
        "disclaimer": "This audit describes source retrieval and reconciliation, not variant pathogenicity.",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", default="data/pilot_raw/audit.json")
    parser.add_argument("--output", default="data/pilot_raw/source-audit-summary.json")
    args = parser.parse_args()
    data = json.loads(Path(args.audit).read_text(encoding="utf-8"))
    if data.get("audit_schema") != "vwf-source-audit/0.1":
        raise ValueError("Unexpected audit schema")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summarize(data), indent=2) + "\n", encoding="utf-8")
    print(f"Review-only summary saved: {output}")

if __name__ == "__main__":
    main()
