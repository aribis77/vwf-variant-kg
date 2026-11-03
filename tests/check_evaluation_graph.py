"""Guard against reference-derived graph edges leaking into evaluation."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "benchmark"
graph = json.loads((root / "evaluation_graph_snapshot.json").read_text())
observations = json.loads((root / "evaluation_evidence_snapshot.json").read_text())
counts = graph["counts"]
assert graph["status"] == "quarantined_not_eligible_for_scoring"
assert graph["policy"] == "retain_only_source_free_ontology_edges"
assert counts["original_edges"] == counts["retained_ontology_edges"] + counts["quarantined_edges"]
assert len(graph["edges"]) == counts["retained_ontology_edges"]
assert all(not str(e.get("source_id", "")).strip() and e.get("evidence_level") == "ontology" for e in graph["edges"])
assert graph["observations"] == observations["retained_observations"]
assert counts["original_observations"] == observations["counts"]["original_observations"]
print("Fail-closed evaluation graph snapshot verified; scoring remains prohibited.")
