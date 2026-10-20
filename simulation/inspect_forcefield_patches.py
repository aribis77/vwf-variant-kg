#!/usr/bin/env python3
"""Inventory CHARMM36 template/patch rules in the *installed* OpenMM release.
No unpublished molecular coordinates or experimental data are required.
An available patch is not proof that it applies successfully in the full complex.
"""
import json, pathlib
from openmm import app
import openmm
from importlib.resources import files
def main():
 names=("HYP","GLY","SER","CYS","CYX","PRO")
 versions=("charmm36_2024.xml","charmm36.xml")
 output={"openmm":openmm.__version__,"forcefields":{}}
 for version in versions:
  record={"loaded":False,"residues":{},"patches":[]}
  output["forcefields"][version]=record
  try:
   force=app.ForceField(version)
   record["loaded"]=True
   record["patches"]=sorted(force._patches.keys())
   for name in names:
    template=force._templates.get(name)
    if template is None:
     record["residues"][name]={"present":False}
     continue
    hydrogens=[a.name for a in template.atoms if getattr(a.element,"symbol",None)=="H"]
    external=[a.name for a in template.atoms if a.name in [template.atoms[i].name for i in getattr(template,"externalBonds",[])]]
    record["residues"][name]={"present":True,"hydrogen_names":hydrogens,
      "atom_count":len(template.atoms),"external_bonds":external}
   for patch_name in ("NTER","CTER","GLYP","PROP","CYSD","DISU","ACE","CT3","CNEU","NNEU"):
    matches=sorted(k for k in force._patches if k==patch_name or k.startswith(patch_name+"_"))
    record.setdefault("target_patches",{})[patch_name]={"exists":bool(matches),"variants":matches}
  except Exception as exc:record["error"]=str(exc)
 pathlib.Path("simulation/forcefield_patch_inventory.json").write_text(json.dumps(output,indent=2))
 print(json.dumps(output,indent=2))
if __name__=="__main__":main()
