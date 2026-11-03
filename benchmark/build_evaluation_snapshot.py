"""Build a separate, conservative evaluation evidence snapshot.

Original portal data are never modified. This excludes exact normalized reference
URLs, and flags possible identifier aliases for manual review. Not a blind evaluation.
"""
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "index.html").read_text()
begin = html.index("const DATA=") + len("const DATA=")
end = html.index(";const $=id=>", begin)
data = json.loads(html[begin:end])
panel = json.loads((ROOT / "benchmark/candidate_reference_panel.json").read_text())
controls = json.loads((ROOT / "benchmark/endpoint_control_candidates.json").read_text())["records"]

def canonical(url):
    parsed = urlsplit(str(url).strip())
    if not parsed.hostname:
        return ""
    return (parsed.hostname.lower().removeprefix("www.") +
            unquote(parsed.path).rstrip("/")).lower()

excluded_sources = {canonical(x["source"]) for x in panel + controls}
kept, excluded, unresolved = [], [], []
for observation in data["observations"]:
    source = canonical(observation.get("source_url", ""))
    if not source:
        unresolved.append(observation)
    elif source in excluded_sources:
        excluded.append(observation)
    else:
        kept.append(observation)

out = {
    "schema": "vwf-evaluation-evidence-snapshot/0.1",
    "status": "quarantined_not_eligible_for_scoring",
    "exclusion_rule": "exact_canonical_source_url_only",
    "counts": {
        "original_observations": len(data["observations"]),
        "excluded_observations": len(excluded),
        "unresolved_source_observations": len(unresolved),
        "retained_observations": len(kept),
    },
    "excluded_observation_ids": sorted(str(x.get("observation_id", "")) for x in excluded),
    "unresolved_observation_ids": sorted(str(x.get("observation_id", "")) for x in unresolved),
    "retained_observations": kept,
    "limitations": [
        "DOI, PMID, PMCID and mirrored publication aliases are not fully resolved",
        "Derived evidence, graph edges and narrative summaries may still contain reference information",
        "Structural reports and external retrieval tools are not filtered",
        "No independent predictions or performance calculations are authorized",
    ],
}
assert len(kept) + len(excluded) + len(unresolved) == len(data["observations"])
assert not {canonical(x.get("source_url", "")) for x in kept} & excluded_sources
path = ROOT / "benchmark/evaluation_evidence_snapshot.json"
path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out["counts"], indent=2))
