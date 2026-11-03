"""Generate an auditable reference-source exclusion register.

This register identifies sources that must not enter prediction inputs.
It is NOT proof that the deployed KG has excluded them.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
panel = json.loads((ROOT / "benchmark/candidate_reference_panel.json").read_text())
controls = json.loads((ROOT / "benchmark/endpoint_control_candidates.json").read_text())["records"]
rows = panel + controls

def normalized(url):
    return url.strip().rstrip("/").lower()

sources = {}
for row in rows:
    url = normalized(row["source"])
    source_id = hashlib.sha256(url.encode()).hexdigest()[:16]
    entry = sources.setdefault(source_id, {
        "source_id": source_id,
        "source_url": url,
        "variants": set(),
        "endpoints": set(),
        "case_count": 0,
        "exclusion_required": True,
        "exclusion_verified_in_KG": False,
        "exclusion_verified_in_workbench": False,
    })
    entry["variants"].add(row["variant"])
    entry["endpoints"].add(row["endpoint"])
    entry["case_count"] += 1

for entry in sources.values():
    entry["variants"] = sorted(entry["variants"])
    entry["endpoints"] = sorted(entry["endpoints"])

register = {
    "schema": "vwf-reference-source-exclusion/0.1",
    "status": "candidate_exclusions_not_enforced",
    "warning": "Source URLs are not sufficient to identify all mirrors, DOI aliases, derived records, or secondary citations. Manual provenance mapping is required.",
    "reference_case_count": len(rows),
    "source_count": len(sources),
    "sources": sorted(sources.values(), key=lambda x: x["source_id"]),
}
out = ROOT / "benchmark/reference_source_exclusions.json"
out.write_text(json.dumps(register, indent=2) + "\n")
assert sum(x["case_count"] for x in register["sources"]) == len(rows)
print(f"Generated {len(sources)} provisional source exclusions for {len(rows)} cases; none verified as enforced.")
