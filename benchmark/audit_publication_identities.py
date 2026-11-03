"""Resolve explicitly supported publication identifiers without guessing equivalence.

The reference set is intentionally provisional. Matching is deterministic and
offline; missing DOI/PMID/PMCID crosswalks remain unresolved, not inferred.
"""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
panel = json.loads((ROOT / "benchmark/candidate_reference_panel.json").read_text())
controls = json.loads((ROOT / "benchmark/endpoint_control_candidates.json").read_text())["records"]
html = (ROOT / "index.html").read_text()
start = html.index("const DATA=") + len("const DATA=")
end = html.index(";const $=id=>", start)
graph = json.loads(html[start:end])

def identities(value):
    value = str(value or "").strip()
    if not value:
        return set()
    out = set()
    url = urlsplit(value)
    if url.hostname:
        host = url.hostname.lower().removeprefix("www.")
        path = unquote(url.path).rstrip("/").lower()
        out.add("url:" + host + path)
        if host in {"doi.org", "dx.doi.org"} and re.fullmatch(r"/10\.\d{4,9}/\S+", path):
            out.add("doi:" + path[1:])
        if host == "pubmed.ncbi.nlm.nih.gov" and re.fullmatch(r"/\d{5,9}", path):
            out.add("pmid:" + path[1:])
        if host == "pmc.ncbi.nlm.nih.gov":
            match = re.fullmatch(r"/articles/(pmc\d+)", path)
            if match:
                out.add("pmcid:" + match[1].upper())
    else:
        low = value.lower().removeprefix("doi:").strip()
        if re.fullmatch(r"10\.\d{4,9}/\S+", low):
            out.add("doi:" + low)
        if re.fullmatch(r"pmc\d+", low):
            out.add("pmcid:" + low.upper())
        if re.fullmatch(r"\d{5,9}", low):
            out.add("pmid:" + low)
    return out

reference_ids = set()
for case in panel + controls:
    for field in ("source", "doi", "pmid", "pmcid"):
        reference_ids.update(identities(case.get(field)))

def classify(value):
    ids = identities(value)
    if ids & reference_ids:
        return "reference_overlap"
    if str(value).startswith("SRC_"):
        return "unresolved_internal_source_id"
    if not ids:
        return "unresolved"
    return "not_matched_by_known_identifiers"

observations = graph["observations"]
edges = graph["edges"]
observation_counts = {}
edge_counts = {}
for o in observations:
    state = classify(o.get("source_url"))
    observation_counts[state] = observation_counts.get(state, 0) + 1
for edge in edges:
    state = classify(edge.get("source_id"))
    edge_counts[state] = edge_counts.get(state, 0) + 1

result = {
    "schema": "vwf-publication-identity-audit/0.1",
    "status": "partial_deterministic_identifier_resolution",
    "reference_identifier_count": len(reference_ids),
    "reference_identifiers": sorted(reference_ids),
    "observation_source_classifications": observation_counts,
    "edge_source_classifications": edge_counts,
    "unresolved_internal_edge_source_ids": sorted({
        str(edge["source_id"]) for edge in edges
        if classify(edge.get("source_id")) == "unresolved_internal_source_id"
    }),
    "limitations": [
        "No DOI-to-PMID-to-PMCID crosswalk is inferred without verified metadata",
        "An identifier that does not match is not proof of independent evidence",
        "Internal SRC identifiers require explicit provenance mapping",
        "No derived assertion, node attribute, Protein Workbench input or live retrieval is cleared",
        "No prediction scoring is authorized",
    ],
}
assert sum(observation_counts.values()) == len(observations)
assert sum(edge_counts.values()) == len(edges)
out = ROOT / "benchmark/publication_identity_audit.json"
out.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ("observation_source_classifications", "edge_source_classifications", "unresolved_internal_edge_source_ids")}, indent=2))
