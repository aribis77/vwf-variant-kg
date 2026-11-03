"""Resolve internal KG publication IDs through their linked observation records.

No external bibliographic equivalence is inferred. Only a single consistent
observed source URL qualifies for a provisional internal-ID mapping.
"""
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "index.html").read_text()
start = html.index("const DATA=") + len("const DATA=")
end = html.index(";const $=id=>", start)
graph = json.loads(html[start:end])
observations = {x["observation_id"]: x for x in graph["observations"]}
nodes = {x["node_id"]: x for x in graph["nodes"]}
panel = json.loads((ROOT / "benchmark/candidate_reference_panel.json").read_text())
controls = json.loads((ROOT / "benchmark/endpoint_control_candidates.json").read_text())["records"]

def canonical(value):
    p = urlsplit(str(value or "").strip())
    return (p.hostname.lower().removeprefix("www.") + unquote(p.path).rstrip("/")).lower() if p.hostname else ""

references = {canonical(x["source"]) for x in panel + controls}
ids = sorted({str(e["source_id"]) for e in graph["edges"] if str(e.get("source_id", "")).startswith("SRC_")})
records = []
for source_id in ids:
    linked = [
        observations[e["subject_id"]]
        for e in graph["edges"]
        if e.get("predicate") == "REPORTED_IN"
        and e.get("object_id") == source_id
        and e.get("subject_id") in observations
    ]
    urls = sorted({canonical(x.get("source_url")) for x in linked if canonical(x.get("source_url"))})
    if len(urls) == 1 and len(linked) > 0:
        status = "single_observation_source_url"
        reference_status = "reference_overlap" if urls[0] in references else "no_known_reference_url_match"
    else:
        status = "ambiguous_or_missing_observation_source"
        reference_status = "unresolved"
    records.append({
        "source_id": source_id,
        "node_label": nodes.get(source_id, {}).get("label", ""),
        "linked_observation_count": len(linked),
        "canonical_observation_source_urls": urls,
        "resolution_status": status,
        "reference_overlap_status": reference_status,
        "independent_publication_verified": False,
    })

out = {
    "schema": "vwf-internal-source-provenance/0.1",
    "status": "provisional_internal_mapping_not_external_adjudication",
    "records": records,
    "counts": {
        "internal_source_ids": len(records),
        "single_url_mappings": sum(x["resolution_status"] == "single_observation_source_url" for x in records),
        "reference_overlapping_internal_ids": sum(x["reference_overlap_status"] == "reference_overlap" for x in records),
        "unresolved_internal_ids": sum(x["reference_overlap_status"] == "unresolved" for x in records),
    },
    "warning": "Single URL mappings are derived from the KG itself, not independent bibliographic verification. A nonmatching URL does not prove independence; graph edges and node labels may still encode source-derived assertions.",
}
(ROOT / "benchmark/internal_source_provenance.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out["counts"], indent=2))
