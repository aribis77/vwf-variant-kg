"""Download 4DMU and calculate verified WT residue environment for H1786D."""
from pathlib import Path
from urllib.request import Request, urlopen
import json
from structural_contacts import analyse

root=Path(__file__).resolve().parent
pdb=root/"4DMU.pdb"
if not pdb.exists():
    req=Request("https://files.rcsb.org/download/4DMU.pdb",headers={"User-Agent":"VWF-KG-structural-analysis/1.0"})
    with urlopen(req,timeout=60) as response:pdb.write_bytes(response.read())
report=analyse(pdb,"B",1786,"H","D")
output=root/"H1786D_contacts.json"
output.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"output":str(output),"status":report["status"],"contacts":report["wild_type_contacts"]},indent=2))
