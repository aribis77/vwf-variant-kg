"""Exercise training admission controls with synthetic records, never real labels."""
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "benchmark"))
from validate_training_records import validate

base = {
    "variant": "A123T", "endpoint": "collagen binding", "direction": "preserved",
    "source": "https://example.org/independent-study", "source_group": "study-new",
    "assay": "ELISA", "construct": "recombinant VWF", "species": "human",
    "reference_control": "wild type", "adjudicated_by": "two reviewers",
    "adjudication_date": "2026-11-03", "independence_verified": True,
}
refs = [{"variant": "R1315L", "source": "https://example.org/held-out",
         "source_group": "reference-study"}]
assert validate([base], refs) == []
assert any("publication overlap" in e for e in validate([{**base, "source": refs[0]["source"]}], refs))
assert any("variant overlap" in e for e in validate([{**base, "variant": "R1315L"}], refs))
assert any("source group overlap" in e for e in validate([{**base, "source_group": "reference-study"}], refs))
assert any("not verified" in e for e in validate([{**base, "independence_verified": False}], refs))
assert any("invalid direction" in e for e in validate([{**base, "direction": "pathogenic"}], refs))
assert any("repeated" in e for e in validate([base, base], refs))
print("Training admission leakage and input validation tests passed.")
