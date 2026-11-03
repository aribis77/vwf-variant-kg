"""Synthetic integration checks ensure variant/endpoint matching and label isolation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmark"))
from build_integrated_case_evidence import integrate

cases = [{"case_id": "CASE_X", "variant": "H1786D",
          "reference_endpoint": "collagen VI binding", "observed_direction": "reduced"},
         {"case_id": "CASE_Y", "variant": "R1315L", "reference_endpoint": "FVIII binding"}]
obs = [{"observation_id": "O1", "subject_id": "VWF_pH1786D", "endpoint": "collagen VI binding"},
       {"observation_id": "O2", "subject_id": "VWF_pH1786D", "endpoint": "collagen I binding"},
       {"observation_id": "O3", "subject_id": "VWF_pR1315L", "endpoint": "collagen VI binding"}]
structure = [{"variant": "H1786D", "independent_pdb_count": 2, "report_count": 3,
              "contact_change": {"median": -2}, "delta_g_kcal_mol": {"median": 1.2},
              "conservation_score": {"median": .8}, "per_structure": []}]
rows = integrate(cases, obs, structure)
assert rows[0]["kg"]["exact_endpoint_observation_ids"] == ["O1"]
assert rows[0]["structural"]["distinct_pdb_count"] == 2
assert rows[0]["integrated"]["evidence_present_in_both_arms"]
assert not rows[1]["structural"]["consensus_available"]
assert not rows[1]["integrated"]["evidence_present_in_both_arms"]
assert all(r["integrated"]["predicted_direction"] == "abstain" for r in rows)
assert rows == integrate([{k:v for k,v in c.items() if k != "observed_direction"} for c in cases], obs, structure)
print("Integrated evidence join, endpoint isolation and withheld-label tests passed.")
