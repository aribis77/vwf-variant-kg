"""Check sourced edge review queue is exhaustive and not eligible for scoring."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "benchmark"
audit = json.loads((root / "edge_provenance_review.json").read_text())
assert audit["status"] == "candidate_review_only_not_scoring_eligible"
assert sum(audit["classifications"].values()) == audit["edge_count"]
assert len(audit["candidate_sourced_edges"]) == audit["classifications"].get("candidate_independent_requires_adjudication", 0)
assert all(e["independence_verified"] is False and e["scoring_eligible"] is False for e in audit["candidate_sourced_edges"])
print("Graph edge provenance review queue checked; no candidate sourced edges promoted to scoring.")
