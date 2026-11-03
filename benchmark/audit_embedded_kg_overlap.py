"""Audit overlap between provisional benchmark sources and the actual embedded KG.

This does not remove evidence or establish a blinded evaluation.
"""
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "index.html").read_text()
start = html.index("const DATA=") + len("const DATA=")
end = html.index(";const $=id=>", start)
data = json.loads(html[start:end])
observations = data["observations"]
panel = json.loads((ROOT / "benchmark/candidate_reference_panel.json").read_text())
controls = json.loads((ROOT / "benchmark/endpoint_control_candidates.json").read_text())["records"]
references = panel + controls

def canonical(url):
    p = urlsplit(str(url).strip())
    return (p.netloc.lower().removeprefix("www.") + unquote(p.path).rstrip("/")).lower()

reference_urls = {canonical(x["source"]) for x in references}
matching = [o for o in observations if canonical(o.get("source_url", "")) in reference_urls]
matched_source_urls = {canonical(o["source_url"]) for o in matching}
overlap_variants = sorted({
    r["variant"] for r in references
    if any(o.get("subject_id") == "VWF_p" + r["variant"] and
           canonical(o.get("source_url", "")) == canonical(r["source"])
           for o in matching)
})
out = {
    "schema": "vwf-embedded-kg-reference-overlap/0.1",
    "status": "audit_only_no_evidence_removed",
    "embedded_observation_count": len(observations),
    "candidate_reference_count": len(references),
    "candidate_source_count": len(reference_urls),
    "matching_embedded_observation_count": len(matching),
    "matching_source_count": len(matched_source_urls),
    "direct_variant_source_overlap": overlap_variants,
    "matching_observation_ids": sorted(str(o.get("observation_id", "")) for o in matching),
    "warning": "URL matches only; aliases, DOIs, PMIDs, mirrored sources, indirect evidence and derived assertions are not excluded or audited.",
}
path = ROOT / "benchmark/embedded_kg_overlap_audit.json"
path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "matching_observation_ids"}, indent=2))
