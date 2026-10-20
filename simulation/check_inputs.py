#!/usr/bin/env python3
"""Fail-closed topology availability check. Chemistry approval is independently required."""
import datetime,hashlib,json,pathlib,sys
root=pathlib.Path(__file__).resolve().parent
status={"timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"inputs":{},"status":"BLOCKED"}
for name in ("WT","H1786D"):
 for ext in ("prmtop","inpcrd"):
  p=root/"prepared"/f"{name}.{ext}"
  status["inputs"][p.name]={"exists":p.is_file(),"bytes":p.stat().st_size if p.is_file() else 0}
a=root/"prepared"/"chemistry_approved.json"
try:
 d=json.loads(a.read_text()) if a.is_file() else {}
except Exception:
 d={}
required=("approved","prepared_by","chemistry_protocol","forcefield","protonation","hydroxyproline","termini","disulfide","solvent_ions")
status["approval_complete"]=d.get("approved") is True and all(d.get(k) for k in required)
status["status"]="READY_FOR_RUNTIME_VALIDATION" if all(x["exists"] and x["bytes"]>0 for x in status["inputs"].values()) and status["approval_complete"] else "BLOCKED_MISSING_APPROVED_TOPOLOGIES"
(root/"input_status.json").write_text(json.dumps(status,indent=2))
print(json.dumps(status,indent=2))
sys.exit(0 if status["status"]=="READY_FOR_RUNTIME_VALIDATION" else 2)
