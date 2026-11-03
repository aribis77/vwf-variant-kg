"""Check publication identity audit counts and unresolved provenance."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "benchmark"
audit = json.loads((root / "publication_identity_audit.json").read_text())
assert audit["status"] == "partial_deterministic_identifier_resolution"
assert sum(audit["observation_source_classifications"].values()) == 112
assert sum(audit["edge_source_classifications"].values()) == 290
assert audit["unresolved_internal_edge_source_ids"], "Internal source identifiers must not silently disappear" 
assert audit["edge_source_classifications"].get("unresolved_internal_source_id", 0) > 0
assert all(x.startswith("SRC_") for x in audit["unresolved_internal_edge_source_ids"])
assert audit["reference_identifier_count"] == len(set(audit["reference_identifiers"]))
assert audit["observation_source_classifications"].get("reference_overlap", 0) > 0
print("Publication identifier audit validated; unresolved aliases are not cleared.")
