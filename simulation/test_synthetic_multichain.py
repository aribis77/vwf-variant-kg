#!/usr/bin/env python3
"""Synthetic *topology-only* validation of three collagen peptides and disulfide patches.
Uses CHARMM36's patched templates, no private structures or generated coordinates.
A successful System establishes atom/bond/parameter compatibility ONLY.
"""
import json
from pathlib import Path
import openmm
from openmm import app

def patched(ff,name,patch=None):
    t=ff._templates[name]
    if patch:t=ff._patches[patch].createPatchedTemplates([t])[0]
    if patch:ff.registerResidueTemplate(t)
    return t

def add_residue(t,chain,resname,template):
    r=t.addResidue(resname,chain)
    atoms={a.name:t.addAtom(a.name,a.element,r) for a in template.atoms}
    for i,j in template.bonds:
        t.addBond(atoms[template.atoms[i].name],atoms[template.atoms[j].name])
    return atoms

def check(t,ff):
    bad=ff.getUnmatchedResidues(t)
    result={"chains":len(list(t.chains())),"residues":len(list(t.residues())),
            "atoms":len(list(t.atoms())),
            "unmatched":[{"residue":r.name,"id":r.id,"chain":r.chain.id} for r in bad]}
    if bad:
        result["status"]="BLOCKED_TEMPLATE_MISMATCH"
    else:
        system=ff.createSystem(t,nonbondedMethod=app.NoCutoff)
        result["status"]="SYSTEM_CONSTRUCTED_SYNTHETIC"
        result["particles"]=system.getNumParticles()
        result["forces"]=[f.__class__.__name__ for f in system.getForces()]
    return result

def collagen_three():
    ff=app.ForceField("charmm36.xml")
    first=patched(ff,"GLY","GLYP")
    last=patched(ff,"HYP","CTER")
    t=app.Topology()
    for chain_id in "XYZ":
        c=t.addChain(chain_id)
        a=add_residue(t,c,"GLY",first)
        b=add_residue(t,c,"HYP",last)
        t.addBond(a["C"],b["N"])
    return check(t,ff)

def disulfide_two():
    ff=app.ForceField("charmm36.xml")
    first=patched(ff,"GLY","GLYP")
    last=patched(ff,"SER","CTER")
    pair=ff._patches["DISU"].createPatchedTemplates([ff._templates["CYS"],ff._templates["CYS"]])
    for tpl in pair:ff.registerResidueTemplate(tpl)
    t=app.Topology()
    cysteines=[]
    for idx,chain_id in enumerate("AB"):
        c=t.addChain(chain_id)
        a=add_residue(t,c,"GLY",first)
        b=add_residue(t,c,"CYS",pair[idx])
        d=add_residue(t,c,"SER",last)
        t.addBond(a["C"],b["N"])
        t.addBond(b["C"],d["N"])
        cysteines.append(b)
    t.addBond(cysteines[0]["SG"],cysteines[1]["SG"])
    return check(t,ff)

def main():
    result={"openmm":openmm.__version__,"forcefield":"charmm36.xml",
            "scientific_scope":"synthetic topology only; no coordinates, no MD, no proof of real complex chemistry"}
    for key,fn in [("three_collagen_chains",collagen_three),("interchain_disulfide_control",disulfide_two)]:
        try:result[key]=fn()
        except Exception as exc:result[key]={"status":"FAILED_EXCEPTION","error":str(exc)}
    out=Path("simulation/synthetic_multi_chain_report.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    if any(result[key].get("status")!="SYSTEM_CONSTRUCTED_SYNTHETIC" for key in ("three_collagen_chains","interchain_disulfide_control")):
        raise SystemExit(2)
if __name__=="__main__":main()
