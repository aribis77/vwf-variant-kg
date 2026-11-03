"""Construct a fail-closed graph snapshot for evaluation research.

No score is authorized. Source-bearing edges are quarantined because source_id
aliases cannot yet be mapped reliably to the reference-source register.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
snapshot = json.loads((ROOT / "benchmark/evaluation_evidence_snapshot.json").read_text())
html = (ROOT / "index.html").read_text()
start = html.index("const DATA=") + len("const DATA=")
end = html.index(";const $=id=>", start)
graph = json.loads(html[start:end])
edges = graph["edges"]
safe_edges = [edge for edge in edges if not str(edge.get("source_id", "")).strip()
              and str(edge.get("evidence_level", "")).lower() == "ontology"]
quarantined_edges = [edge for edge in edges if edge not in safe_edges]
assert all(not e.get("source_id") and e.get("evidence_level") == "ontology" for e in safe_edges)
assert len(safe_edges) + len(quarantined_edges) == len(edges)
result = {
    "schema": "vwf-evaluation-graph-snapshot/0.1",
    "status": "quarantined_not_eligible_for_scoring",
    "policy": "retain_only_source_free_ontology_edges",
    "nodes": graph["nodes"],
    "edges": safe_edges,
    "observations": snapshot["retained_observations"],
    "counts": {
        "original_edges": len(edges),
        "retained_ontology_edges": len(safe_edges),
        "quarantined_edges": len(quarantined_edges),
        "retained_observations": len(snapshot["retained_observations"]),
        "original_observations": len(graph["observations"]),
    },
    "limitations": [
        "Retained observations are URL-filtered, not fully publication-identity resolved",
        "Nodes may encode source-derived information and are not eligible as predictive features",
        "All source-bearing graph edges are quarantined, including potentially useful non-reference evidence",
        "No browser analysis, Protein Workbench or external evidence retrieval uses this snapshot yet",
        "No performance or clinical inference is permitted",
    ],
}
out = ROOT / "benchmark/evaluation_graph_snapshot.json"
out.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result["counts"], indent=2))
