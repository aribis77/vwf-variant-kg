"""Validate externally produced Protein Workbench reports before benchmark use.

No molecular dynamics, invented energies, or structure-derived functional labels.
Only reproducible, verified mapping and numeric structural features are admitted.
"""
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "benchmark"
AA = set("ACDEFGHIKLMNPQRSTVWY")
PDB = re.compile(r"^[0-9][A-Za-z0-9]{3}$")
VARIANT = re.compile(r"^([A-Z])([1-9][0-9]*)([A-Z])$")
REQUIRED = {"report_id", "variant", "uniprot_accession", "pdb_id",
            "chain", "uniprot_residue", "pdb_author_residue", "mapped_wild_type",
            "mapping_verified", "source_report_sha256", "contacts_wt",
            "contacts_mutant", "delta_g_kcal_mol", "conservation_score",
            "calculation_method", "analysis_version"}

def validate_report(r):
    errors = []
    missing = REQUIRED - set(r)
    if missing:
        return ["missing:" + ",".join(sorted(missing))]
    match = VARIANT.fullmatch(str(r["variant"]))
    if not match or match.group(1) not in AA or match.group(3) not in AA:
        errors.append("invalid_variant")
    else:
        if r["mapped_wild_type"] != match.group(1) or r["uniprot_residue"] != int(match.group(2)):
            errors.append("uniprot_residue_mismatch")
    if r["uniprot_accession"] != "P04275":
        errors.append("unexpected_uniprot_accession")
    if not PDB.fullmatch(str(r["pdb_id"])):
        errors.append("invalid_pdb_id")
    if not str(r["chain"]).strip() or not isinstance(r["pdb_author_residue"], (str, int)):
        errors.append("invalid_pdb_coordinate")
    if r["mapping_verified"] is not True:
        errors.append("unverified_residue_mapping")
    if not re.fullmatch("[a-fA-F0-9]{64}", str(r["source_report_sha256"])):
        errors.append("missing_report_checksum")
    for field in ("contacts_wt", "contacts_mutant"):
        if type(r[field]) is not int or r[field] < 0:
            errors.append("invalid_" + field)
    for field in ("delta_g_kcal_mol", "conservation_score"):
        value = r[field]
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value)):
            errors.append("invalid_" + field)
    if not str(r["calculation_method"]).strip() or not str(r["analysis_version"]).strip():
        errors.append("missing_method_provenance")
    return errors

def main():
    data = json.loads((B / "structural_training_reports.json").read_text())
    rows = data["reports"]
    seen = set()
    failures = []
    for i, row in enumerate(rows):
        errors = validate_report(row)
        key = (row.get("report_id"), row.get("pdb_id"), row.get("chain"))
        if key in seen:
            errors.append("duplicate_report_structure")
        seen.add(key)
        if errors:
            failures.append({"index": i, "errors": errors})
    out = {"schema": "vwf-structural-report-admission/0.1",
           "status": "empty" if not rows else "rejected" if failures else "format_checked_not_independently_validated",
           "reports": len(rows), "failures": failures,
           "scoring_eligible": False,
           "warning": "Schema checks cannot independently confirm mapping, calculations, source-file authenticity or endpoint relevance."}
    (B / "structural_report_admission_audit.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    if failures:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
