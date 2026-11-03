"""Validate the prospective prediction contract without reading reference labels."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
contract = json.loads((root / "benchmark/prediction_contract.json").read_text())
assert contract["status"] == "protocol_only_no_predictions_frozen"
assert contract["unit_of_evaluation"] == "variant_and_exact_functional_endpoint"
assert set(contract["allowed_predictions"]) == {"increased", "reduced", "preserved", "abstain"}
assert set(contract["methods"]) == {
    "integrated_KG_and_structural", "KG_evidence_only", "structural_only"
}
required = set(contract["required_prediction_fields"])
assert {"variant", "endpoint", "prediction_timestamp", "method_version",
        "evidence_cutoff_date", "excluded_reference_source_ids",
        "evidence_source_ids", "prediction_record_hash"}.issubset(required)
assert any("abstention" in item.lower() for item in contract["reporting"])
assert any("unfrozen" in item.lower() for item in contract["prohibitions"])
print("Prospective prediction contract validated; no predictions or accuracy calculated.")
