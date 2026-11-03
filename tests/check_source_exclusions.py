"""Check reference-source exclusions remain explicit and unverified."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "benchmark"
register = json.loads((root / "reference_source_exclusions.json").read_text())
panel = json.loads((root / "candidate_reference_panel.json").read_text())
controls = json.loads((root / "endpoint_control_candidates.json").read_text())["records"]
assert register["status"] == "candidate_exclusions_not_enforced"
assert register["reference_case_count"] == len(panel) + len(controls)
assert register["source_count"] == len(register["sources"])
assert sum(x["case_count"] for x in register["sources"]) == register["reference_case_count"]
assert len({x["source_id"] for x in register["sources"]}) == register["source_count"]
assert all(x["exclusion_required"] is True for x in register["sources"])
assert all(x["exclusion_verified_in_KG"] is False for x in register["sources"])
assert all(x["exclusion_verified_in_workbench"] is False for x in register["sources"])
print("Reference source exclusion register checked; enforcement remains unverified.")
