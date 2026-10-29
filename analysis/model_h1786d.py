"""Generate a testable H1786D structural model from experimental 4DMU.

This is an initial side-chain replacement, not a relaxed or validated energetic model.
Preserves author residue identifiers by operating on an extracted local complex.
"""
from pathlib import Path
import json
from urllib.request import Request, urlopen
from pdbfixer import PDBFixer
from openmm.app import PDBFile

ROOT=Path(__file__).resolve().parent
source=ROOT/"4DMU.pdb"
if not source.exists():
    req=Request("https://files.rcsb.org/download/4DMU.pdb",headers={"User-Agent":"VWF-KG/1.0"})
    with urlopen(req,timeout=90) as r:source.write_bytes(r.read())

# PDBFixer reads author numbering from PDB, but requires a consistent protein
# chain; reject any unverified output instead of silently remapping the site.
fixer=PDBFixer(filename=str(source))
chains=list(fixer.topology.chains())
matches=[]
for chain in chains:
    if chain.id!="B":continue
    for residue in chain.residues():
        if residue.id=="1786" and residue.name=="HIS":matches.append((chain,residue))
if len(matches)!=1:
    raise RuntimeError(f"Expected exactly one chain B HIS1786; found {len(matches)}")
fixer.applyMutations(["HIS-1786-ASP"],"B")
fixer.findMissingResidues()
# Do not invent missing backbone segments; only construct missing side-chain atoms.
fixer.missingResidues={}
fixer.findMissingAtoms()
fixer.addMissingAtoms()
after=[r for c in fixer.topology.chains() if c.id=="B" for r in c.residues() if r.id=="1786"]
if len(after)!=1 or after[0].name!="ASP":
    raise RuntimeError("PDBFixer mutation did not produce ASP at B:1786")
# Mutation creates new atom topology and coordinates, but does not imply
# side-chain minimization, relaxation, or binding-energy validation.
output=ROOT/"4DMU_H1786D_unrelaxed.pdb"
with output.open("w") as handle:
    PDBFile.writeFile(fixer.topology,fixer.positions,handle,keepIds=True)
from structural_contacts import compare_models
result=compare_models(source,output,"B",1786,"H","D")
result["modeling"]={"method":"PDBFixer.applyMutations","relaxed":False,
                    "interpretation_limit":"Unrelaxed side-chain replacement; geometric comparison only"}
(ROOT/"H1786D_model_comparison.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"status":result["status"],"model":str(output),
                  "contact_delta":result["delta_contacts"]},indent=2))
