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

controls = json.loads((ROOT / "benchmark/endpoint_control_candidates.json").read_text())
records = controls["records"]
assert records, "Endpoint controls must be nonempty"
assert len({(x["variant"], x["endpoint"], x["source_group"]) for x in records}) == len(records), (
    "Duplicate control observations"
)
for row in records:
    assert row["observed_direction"] in ("preserved", "reduced", "increased")
    assert row["reference_freeze_status"] == "not_frozen" or (
        row["independent_adjudication"] is True
        and row["independent_replication_verified"] is True
    ), "Controls cannot be frozen without independent review and replication"
    assert row["source"] and row["source_figure"] and row["model"] and row["assay"]
assert design["current_verified_preserved_controls"] <= sum(
    row["observed_direction"] == "preserved"
    and row["reference_freeze_status"] == "frozen"
    for row in records
), "Verified controls cannot exceed frozen preserved-function records"
print(f"Checked {len(records)} endpoint-specific control observations; no predictive accuracy calculated.")
