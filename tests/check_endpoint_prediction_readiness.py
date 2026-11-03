"""Regression checks for endpoint gating, source verification and label isolation."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "benchmark"))
from prepare_endpoint_predictions import evaluate_case

case = {"case_id": "TEST_001", "variant": "H1786D", "endpoint": "collagen binding"}
observations = [
    {"observation_id": "OBS_TEST1", "subject_id": "VWF_pH1786D",
     "endpoint": "collagen binding", "source_url": "https://example.org/independent"},
    {"observation_id": "OBS_TEST2", "subject_id": "VWF_pH1786D",
     "endpoint": "ADAMTS13 proteolysis", "source_url": "https://example.org/independent"},
    {"observation_id": "OBS_TEST3", "subject_id": "VWF_pR1315L",
     "endpoint": "collagen binding", "source_url": "https://example.org/independent"},
]
first = evaluate_case(case, observations)
assert len(first) == 3
assert all(x["predicted_direction"] == "abstain" for x in first)
assert all(x["candidate_exact_endpoint_observation_ids"] == ["OBS_TEST1"] for x in first)
assert all(not x["verified_exact_endpoint_observation_ids"] for x in first)
assert all("no_preregistered_calibrated_direction_rule" in x["blockers"] for x in first)

verified = {"https://example.org/independent": {
    "independent_of_reference": True, "adjudicated": True}}
structural = {"TEST_001": {"verified_mapping": True,
    "endpoint_specific_validation": True, "independent_of_reference": True}}
second = evaluate_case(case, observations, verified, structural)
assert all(x["predicted_direction"] == "abstain" for x in second)
assert all(x["verified_exact_endpoint_observation_ids"] == ["OBS_TEST1"] for x in second)
assert all(x["structural_report_verified"] for x in second)
assert all(x["blockers"] == ["endpoint_direction_rule_not_calibrated", "no_preregistered_calibrated_direction_rule"] for x in second)
assert [x["record_hash"] for x in first] == [x["record_hash"] for x in evaluate_case(case, observations)]
assert [x["record_hash"] for x in first] == [x["record_hash"] for x in evaluate_case({**case, "expected_direction": "reduced"}, observations)]

result = json.loads((root / "benchmark/endpoint_prediction_readiness.json").read_text())
assert result["status"] == "abstention_only_not_frozen_not_scoring_eligible"
assert len(result["predictions"]) == result["case_count"] * result["method_count"]
assert all(x["predicted_direction"] == "abstain" and x["eligible_for_scoring"] is False for x in result["predictions"])
print("Endpoint gating, label isolation, and fail-closed abstentions verified.")
