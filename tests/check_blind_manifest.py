"""Validate a generated, provisional VWF case manifest."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
data = json.loads((root / "benchmark/blind_manifest.json").read_text())
cases = data["cases"]
assert data["status"] == "design_only_not_a_blind_evaluation"
assert len(cases) == 22, f"Expected 22 provisional cases; got {len(cases)}"
assert len({c["case_id"] for c in cases}) == len(cases)
assert all(c["evaluation_status"] == "not_eligible_unfrozen" for c in cases)
assert all(set(c) == {"case_id", "variant", "endpoint", "source_group_id", "reference_set", "evaluation_status"} for c in cases)
assert len({c["source_group_id"] for c in cases}) < len(cases), "Source sharing should be visible"
print(f"Manifest validated: {len(cases)} provisional cases; no labels or accuracy scores.")
