"""Check provisional VWF benchmark metadata without claiming predictive accuracy."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
panel = json.loads((ROOT / "benchmark/candidate_reference_panel.json").read_text())
design = json.loads((ROOT / "benchmark/reference_design_matrix.json").read_text())
assert isinstance(panel, list) and panel, "Reference panel must be nonempty"
assert len({(x["variant"], x["endpoint"]) for x in panel}) == len(panel), "Duplicate variant-endpoint entries"
assert len(design["mechanisms"]) == len(set(design["mechanisms"])), "Duplicate mechanisms"
assert design["current_verified_preserved_controls"] >= 0
for row in panel:
    for field in ("variant", "endpoint", "source", "reference_freeze_status", "review_status"):
        assert row.get(field), f"Missing {field}: {row}"
    assert row["reference_freeze_status"] in ("not_frozen", "frozen")
    if row["reference_freeze_status"] == "frozen":
        assert row.get("independent_replication_verified") is True, (
            "Frozen references require explicit independent replication verification"
        )
        assert row.get("evaluation_eligibility") != "exploratory_only", (
            "Frozen references must have a reviewed evaluation status"
        )
print(f"Validated metadata structure for {len(panel)} provisional benchmark entries; no accuracy calculated.")
