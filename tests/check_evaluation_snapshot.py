"""Verify reference exclusions and conservation of embedded observations."""
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote

root = Path(__file__).resolve().parents[1] / "benchmark"
snapshot = json.loads((root / "evaluation_evidence_snapshot.json").read_text())
panel = json.loads((root / "candidate_reference_panel.json").read_text())
controls = json.loads((root / "endpoint_control_candidates.json").read_text())["records"]

def canonical(url):
    p = urlsplit(str(url).strip())
    return (p.hostname.lower().removeprefix("www.") + unquote(p.path).rstrip("/")).lower() if p.hostname else ""

reference_sources = {canonical(x["source"]) for x in panel + controls}
retained = snapshot["retained_observations"]
counts = snapshot["counts"]
assert snapshot["status"] == "quarantined_not_eligible_for_scoring"
assert counts["original_observations"] == sum((
    counts["excluded_observations"],
    counts["unresolved_source_observations"],
    counts["retained_observations"],
))
assert len(retained) == counts["retained_observations"]
assert len(snapshot["excluded_observation_ids"]) == counts["excluded_observations"]
assert len(snapshot["unresolved_observation_ids"]) == counts["unresolved_source_observations"]
assert all(canonical(x.get("source_url", "")) not in reference_sources for x in retained)
assert all(canonical(x.get("source_url", "")) for x in retained)
assert len({x["observation_id"] for x in retained}) == len(retained)
print("Quarantined evaluation snapshot verified; alias and derived-evidence review still required.")
