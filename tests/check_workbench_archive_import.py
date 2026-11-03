"""Synthetic tests for browser Workbench archive import review."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmark"))
from import_workbench_archive import convert

report={
 "schema":"protein-workbench-mechanistic-report/0.1",
 "mutation":"H1786D","pdb":"4DMU","chain":"B",
 "coordinate_mapping":{"verified_in_loaded_coordinates":True,"author_residue":1786},
 "metrics":{
  "contacts":{"delta_contacts":-3,"method":"contact-count","unit":"contacts"},
  "energetics":{"delta_delta_g":1.4,"method":"synthetic","unit":"kcal/mol"},
  "conservation":{"score":0.8,"method":"synthetic","unit":"fraction"}
 }
}
archive={"schema":"vwf-browser-workbench-archive/0.1","reports":[report]}
result=convert(archive)
assert result["report_count"]==1 and result["rejected_count"]==0
record=result["records"][0]
assert record["contacts_delta"]["value"]==-3
assert record["energy"]["value"]==1.4
assert record["admitted_to_training"] is False
assert record["review_status"]=="pending_independent_mapping_and_method_review"
bad=convert({**archive,"reports":[{**report,"coordinate_mapping":{}}]})
assert "mapping_not_coordinate_verified" in bad["records"][0]["review_errors"]
bad=convert({**archive,"reports":[{**report,"metrics":{"energetics":{"ddg":1.0}}}]})
assert "energy_method_or_unit_missing" in bad["records"][0]["review_errors"]
assert convert({**archive,"reports":[]})["report_count"]==0
print("Workbench archive import review tests passed.")
