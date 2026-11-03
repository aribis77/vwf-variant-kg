"""Classify graph edges for provenance review without changing scoring eligibility."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "benchmark"
graph = json.loads((root / "evaluation_graph_snapshot.json").read_text())
provenance = json.loads((root / "internal_source_provenance.json").read_text())
records = {r["source_id"]: r for r in provenance["records"]}
retained = {o["observation_id"] for o in graph["observations"]}
html = (root.parent / "index.html").read_text()
start = html.index("const DATA=") + len("const DATA=")
end = html.index(";const $=id=>", start)
original = json.loads(html[start:end])
classes = {}
review = []
for edge in original["edges"]:
    source = str(edge.get("source_id", ""))
    linked_obs = [edge.get(k) for k in ("subject_id", "object_id") if str(edge.get(k, "")).startswith("OBS_")]
    if any(obs not in retained for obs in linked_obs):
        reason = "references_excluded_or_unresolved_observation"
    elif not source and edge.get("evidence_level") == "ontology":
        reason = "retained_ontology"
    elif source in records:
        item = records[source]
        if item["reference_overlap_status"] == "reference_overlap":
            reason = "known_reference_overlap"
        elif item["resolution_status"] == "single_observation_source_url":
            reason = "candidate_independent_requires_adjudication"
        else:
            reason = "unresolved_internal_provenance"
    else:
        reason = "unresolved_external_or_unsourced_assertion"
    classes[reason] = classes.get(reason, 0) + 1
    if reason == "candidate_independent_requires_adjudication":
        review.append({
            "source_id": source,
            "subject_id": edge.get("subject_id"),
            "predicate": edge.get("predicate"),
            "object_id": edge.get("object_id"),
            "candidate_source_urls": records[source]["canonical_observation_source_urls"],
            "independence_verified": False,
            "scoring_eligible": False,
        })
result = {
    "schema": "vwf-edge-provenance-review/0.1",
    "status": "candidate_review_only_not_scoring_eligible",
    "edge_count": len(original["edges"]),
    "classifications": classes,
    "candidate_sourced_edges": review,
    "warning": "URL nonoverlap is not publication independence. These edges are excluded from the scoring graph pending independent DOI/PMID/PMCID verification and derived-evidence review.",
}
assert sum(classes.values()) == result["edge_count"]
assert all(not e["scoring_eligible"] for e in review)
(root / "edge_provenance_review.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(classes, indent=2))
