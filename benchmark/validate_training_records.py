"""Validate independently curated training records before any model calibration.

Training data must be supplied separately from the candidate reference panel.
No data are fabricated, and this script never fits a threshold.
"""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "benchmark"
ALLOWED = {"increased", "reduced", "preserved"}
FIELDS = {"variant", "endpoint", "direction", "source", "source_group",
          "assay", "construct", "species", "reference_control",
          "adjudicated_by", "adjudication_date", "independence_verified"}
def canonical(url):
    p = urlsplit(str(url or "").strip())
    return (p.hostname.lower().removeprefix("www.") + unquote(p.path).rstrip("/")).lower() if p.hostname else ""

def validate(training, reference_cases):
    errors = []
    reference_sources = {canonical(c["source"]) for c in reference_cases}
    reference_variants = {c["variant"].upper() for c in reference_cases}
    reference_groups = {str(c.get("source_group") or "").lower() for c in reference_cases if c.get("source_group")}
    seen = set()
    for i, item in enumerate(training):
        missing = sorted(FIELDS - set(item))
        if missing:
            errors.append(f"row {i}: missing fields {missing}")
            continue
        variant = str(item["variant"]).upper()
        endpoint = " ".join(str(item["endpoint"]).lower().split())
        key = (variant, endpoint, str(item["source_group"]))
        if key in seen:
            errors.append(f"row {i}: repeated variant-endpoint-source group")
        seen.add(key)
        if not re.fullmatch(r"[A-Z][0-9]+[A-Z*]", variant):
            errors.append(f"row {i}: invalid variant")
        if item["direction"] not in ALLOWED:
            errors.append(f"row {i}: invalid direction")
        if not canonical(item["source"]):
            errors.append(f"row {i}: source must be an absolute URL")
        if canonical(item["source"]) in reference_sources:
            errors.append(f"row {i}: benchmark reference publication overlap")
        if variant in reference_variants:
            errors.append(f"row {i}: benchmark variant overlap")
        if str(item["source_group"]).lower() in reference_groups:
            errors.append(f"row {i}: benchmark source group overlap")
        if item["independence_verified"] is not True:
            errors.append(f"row {i}: independent provenance not verified")
        for field in ("assay", "construct", "species", "reference_control", "adjudicated_by", "adjudication_date", "source_group"):
            if not str(item[field]).strip():
                errors.append(f"row {i}: empty {field}")
    return errors

def main():
    panel = json.loads((B / "candidate_reference_panel.json").read_text())
    controls = json.loads((B / "endpoint_control_candidates.json").read_text())["records"]
    training_path = B / "independent_training_records.json"
    data = json.loads(training_path.read_text())
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise ValueError("Training data must contain a records array")
    errors = validate(data["records"], panel + controls)
    status = "empty_training_set" if not data["records"] else "validated" if not errors else "rejected"
    out = {"schema": "vwf-training-admission/0.1", "status": status,
           "records_checked": len(data["records"]), "errors": errors,
           "calibration_authorized": bool(data["records"]) and not errors and False,
           "note": "Passing record checks alone does not establish independent publication identity, sufficient class balance, or authorize model calibration."}
    (B / "training_admission_audit.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
