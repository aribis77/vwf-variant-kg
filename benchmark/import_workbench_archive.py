"""Convert exported browser Workbench archives into a review queue.

Run: python benchmark/import_workbench_archive.py path/to/export.json
This does not admit records into the training register or claim scientific verification.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "benchmark"
VARIANT = re.compile(r"^([ACDEFGHIKLMNPQRSTVWY])([1-9][0-9]*)([ACDEFGHIKLMNPQRSTVWY])$")

def metric(report, paths, keys):
    for path in paths:
        obj = report
        for part in path:
            obj = obj.get(part) if isinstance(obj, dict) else None
        if not isinstance(obj, dict) or obj.get("status") in ("unavailable", "failed", "not_run", "pending"):
            continue
        for key in keys:
            value = obj.get(key)
            if type(value) in (int, float):
                import math
                if math.isfinite(value):
                    return {"value": value, "field": ".".join(path + [key]),
                            "method": obj.get("method") or obj.get("energy_method"),
                            "unit": obj.get("units") or obj.get("unit")}
    return None

def convert(archive):
    if archive.get("schema") != "vwf-browser-workbench-archive/0.1":
        raise ValueError("Unexpected archive schema")
    if not isinstance(archive.get("reports"), list):
        raise ValueError("Missing report list")
    queue = []
    for i, report in enumerate(archive["reports"]):
        errors = []
        variant = str(report.get("mutation", "")).upper()
        match = VARIANT.fullmatch(variant)
        mapping = report.get("coordinate_mapping") or {}
        pdb = str(report.get("pdb") or (report.get("structure") or {}).get("pdb_id") or mapping.get("pdb") or "").upper()
        chain = str(report.get("chain") or mapping.get("chain") or "")
        residue = mapping.get("author_residue", mapping.get("author_residue_number", report.get("author_residue")))
        if report.get("schema") != "protein-workbench-mechanistic-report/0.1":
            errors.append("unexpected_workbench_schema")
        if not match:
            errors.append("invalid_variant")
        if not re.fullmatch(r"[0-9][A-Z0-9]{3}", pdb) or not chain:
            errors.append("invalid_structure_identifier")
        if mapping.get("verified_in_loaded_structure") is not True and mapping.get("verified_in_loaded_coordinates") is not True:
            errors.append("mapping_not_coordinate_verified")
        if residue is None:
            errors.append("missing_author_residue")
        elif not str(residue).lstrip("-").isdigit():
            errors.append("non_numeric_author_residue")
        contacts = metric(report, [["metrics","contacts"],["results","contacts"],["contacts"]],
                          ["delta_contacts","contact_delta","net_contact_change","delta"])
        energy = metric(report, [["metrics","energetics"],["results","energetics"],["energetics"],["metrics","energy"],["energy"]],
                        ["delta_delta_g","ddg","delta_g","delta_energy","energy_delta"])
        conservation = metric(report, [["metrics","conservation"],["results","conservation"],["conservation"]],
                              ["score","conservation_score","normalized_score"])
        raw = json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
        if not any((contacts, energy, conservation)):
            errors.append("no_numeric_structural_features")
        if energy and (not energy["method"] or not energy["unit"]):
            errors.append("energy_method_or_unit_missing")
        queue.append({
            "archive_index": i, "variant": variant, "pdb_id": pdb, "chain": chain,
            "pdb_author_residue": residue, "report_sha256": hashlib.sha256(raw).hexdigest(),
            "contacts_delta": contacts, "energy": energy, "conservation": conservation,
            "review_status": "rejected_format" if errors else "pending_independent_mapping_and_method_review",
            "review_errors": errors, "admitted_to_training": False,
        })
    return {"schema": "vwf-workbench-import-review/0.1", "status": "review_only_no_training_admission",
            "report_count": len(queue), "rejected_count": sum(bool(x["review_errors"]) for x in queue),
            "records": queue,
            "warning": "Browser-supplied mapping flags are not independently verified; free-energy units and methods must be reviewed before cross-PDB pooling."}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path, default=B / "workbench_import_review.json")
    args = parser.parse_args()
    result = convert(json.loads(args.archive.read_text()))
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"reports": result["report_count"], "rejected": result["rejected_count"],
                      "output": str(args.output)}, indent=2))

if __name__ == "__main__":
    main()
