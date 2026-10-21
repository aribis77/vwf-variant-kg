#!/usr/bin/env python3
"""Public-reference-only 4DMU preparation audit, NOT private model processing.
Downloads the PUBLISHED RCSB coordinate file; never accesses private inputs.
Reports only topology and chemistry diagnostic metadata, not coordinates.
"""
import collections,json,pathlib,urllib.request,traceback
from openmm import app
import openmm
def main():
 url="https://files.rcsb.org/download/4DMU.pdb"
 with urllib.request.urlopen(url,timeout=25) as r: raw=r.read()
 path=pathlib.Path("4DMU_PUBLIC_REFERENCE.pdb")
 path.write_bytes(raw)
 result={"source":"RCSB 4DMU public experimental entry","openmm":openmm.__version__}
 try:
  pdb=app.PDBFile(str(path))
  residues=list(pdb.topology.residues())
  result["chains"]={ch.id:{"residues":len(list(ch.residues())),"first":next(iter(ch.residues())).name} for ch in pdb.topology.chains() if list(ch.residues())}
  result["residue_names"]=dict(collections.Counter(r.name for r in residues))
  result["atoms"]=len(list(pdb.topology.atoms()))
  result["residue_1786"]=[{"chain":r.chain.id,"name":r.name} for r in residues if r.id=="1786"]
  ff=app.ForceField("charmm36.xml")
  result["unmatched_initial"]=[{"chain":r.chain.id,"name":r.name,"resid":r.id} for r in ff.getUnmatchedResidues(pdb.topology)][:32]
 except Exception as exc:result["error"]=str(exc);result["traceback"]=traceback.format_exc()[-800:]
 finally:
  path.unlink(missing_ok=True)
 out=pathlib.Path("simulation/public_4dmu_audit.json")
 out.write_text(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2))
 if "error" in result:raise SystemExit(2)
if __name__=="__main__":main()
