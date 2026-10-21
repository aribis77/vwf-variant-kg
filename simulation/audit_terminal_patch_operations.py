#!/usr/bin/env python3
"""Audit CHARMM36 patch applicability to truncated VWF A3 and collagen.
No private structures are read. Reports candidate patch atom/bond operations;
does not treat patch presence as successful parameterization.
"""
import json
from pathlib import Path
from openmm import app
import openmm

residue_names=("HYP","GLY","SER","CYS")
patch_prefixes=("NTER","CTER","GLYP","PROP","CYSD","DISU","ACE","CT3","CNEU","NNEU")

def atoms(p):
    return sorted(getattr(a,"name",str(a)) for a in getattr(p,"addedAtoms",[]))
def deleted(p):
    return sorted(str(a) for a in getattr(p,"deletedAtoms",[]))
def bond_entries(items):
    return [str(x) for x in items]
def main():
    ff=app.ForceField("charmm36.xml")
    data={"openmm":openmm.__version__,"forcefield":"charmm36.xml","HYP_present":"HYP" in ff._templates,
          "candidate_termini":[{"chain_type":"collagen","N":"GLY","C":"HYP"},
                              {"chain_type":"VWF_A3","N":"CYS","C":"SER"}],"patches":{}}
    for prefix in patch_prefixes:
        choices={k:v for k,v in ff._patches.items() if k==prefix or k.startswith(prefix+"_")}
        group={}
        for name,patch in choices.items():
            group[name]={"num_residues":getattr(patch,"numResidues",None),
                         "added_atoms":atoms(patch),"deleted_atoms":deleted(patch),
                         "added_bonds":bond_entries(getattr(patch,"addedBonds",[])),
                         "deleted_bonds":bond_entries(getattr(patch,"deletedBonds",[])),
                         "external_bonds_added":bond_entries(getattr(patch,"addedExternalBonds",[])),
                         "external_bonds_deleted":bond_entries(getattr(patch,"deletedExternalBonds",[]))}
        data["patches"][prefix]=group
    print(json.dumps(data,indent=2))
    Path("simulation/terminal_patch_operations.json").write_text(json.dumps(data,indent=2))
if __name__=="__main__":main()
