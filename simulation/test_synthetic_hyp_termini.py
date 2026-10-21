#!/usr/bin/env python3
"""Construct synthetic GLY-HYP peptides from CHARMM36 patched templates.
No private coordinates. This tests atom graph -> exact force-field system creation.
Synthetic topologies are NOT simulation-quality geometries or capped VWF models.
"""
import json
from pathlib import Path
from openmm import app
import openmm

def synthetic_chain(ff,n_patch,c_patch):
    g=ff._templates["GLY"]
    h=ff._templates["HYP"]
    if n_patch:
        g=ff._patches[n_patch].createPatchedTemplates([g])[0]
    if c_patch:
        h=ff._patches[c_patch].createPatchedTemplates([h])[0]
    # Patched templates must be explicitly exposed as candidates for this synthetic test.
    for template in (g,h):
        if template not in ff._templates.values():
            ff.registerResidueTemplate(template)
    t=app.Topology()
    ch=t.addChain("P")
    objects=[]
    for name,tmpl in [("GLY",g),("HYP",h)]:
        residue=t.addResidue(name,ch)
        atoms=[t.addAtom(a.name,a.element,residue) for a in tmpl.atoms]
        for i,j in tmpl.bonds:t.addBond(atoms[i],atoms[j])
        objects.append((tmpl,atoms))
    # Link amide C-N explicitly across the two peptide residues.
    def get_atom(which,name):
        atoms=objects[which][1]
        return next(a for a in atoms if a.name==name)
    t.addBond(get_atom(0,"C"),get_atom(1,"N"))
    unmatched=ff.getUnmatchedResidues(t)
    report={"n_patch":n_patch or "NONE","c_patch":c_patch or "NONE",
            "residues":[{"name":r.name,"atoms":len(list(r.atoms()))} for r in t.residues()],
            "unmatched":[{"name":r.name,"id":r.id} for r in unmatched]}
    if not unmatched:
        system=ff.createSystem(t,nonbondedMethod=app.NoCutoff)
        report["system_particles"]=system.getNumParticles()
        report["status"]="SYSTEM_CONSTRUCTED_SYNTHETIC"
    else:
        report["status"]="BLOCKED_TEMPLATE_MISMATCH"
    return report

def main():
    report={"openmm":openmm.__version__,"forcefield":"charmm36.xml","tests":[]}
    for n,c in [("GLYP","CTER"),("NTER","CTER"),("GLYP",None),(None,"CTER")]:
        try:result=synthetic_chain(app.ForceField("charmm36.xml"),n,c)
        except Exception as e:result={"n_patch":n,"c_patch":c,"status":"FAILED_EXCEPTION","error":str(e)}
        report["tests"].append(result)
    Path("simulation/synthetic_terminal_test.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    if not any(r["status"]=="SYSTEM_CONSTRUCTED_SYNTHETIC" for r in report["tests"]):
        raise SystemExit("No synthetic peptide parameterized successfully")
if __name__=="__main__":main()
