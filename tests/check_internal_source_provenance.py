"""Check internal source mappings do not falsely assert independent validation."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "benchmark"
data = json.loads((root / "internal_source_provenance.json").read_text())
records = data["records"]
assert len(records) == data["counts"]["internal_source_ids"]
assert len({r["source_id"] for r in records}) == len(records)
assert all(r["source_id"].startswith("SRC_") for r in records)
assert all(r["independent_publication_verified"] is False for r in records)
assert sum(r["resolution_status"] == "single_observation_source_url" for r in records) == data["counts"]["single_url_mappings"]
assert sum(r["reference_overlap_status"] == "reference_overlap" for r in records) == data["counts"]["reference_overlapping_internal_ids"]
assert all(r["canonical_observation_source_urls"] for r in records if r["resolution_status"] == "single_observation_source_url")
print("Internal source provenance mapping checked; external verification remains outstanding.")
