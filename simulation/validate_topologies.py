#!/usr/bin/env python3
"""Chemical-topology QA for the VWF A3–collagen III paired pilot.
Requires OpenMM, approved AMBER prmtop/inpcrd files. Exits nonzero on any failure.
This is a computational gate; it does NOT independently certify force-field chemistry.
"""
import argparse
import collections
import json
import math
from pathlib import Path

HYP_NAMES={"HYP","XPN"}
HIS_NAMES={"HIS","HID","HIE","HIP","HSD","HSE","HSP"}
ASP_NAMES={"ASP","ASH"}
WATER_NAMES={"WAT","HOH","TIP3","TIP4","SOL","SPC","TP3"}
EXPECTED_NONWATER=269
EXPECTED_HYP=21

def inspect(prmtop_path, inpcrd_path, label):
    from openmm import app, unit
    top=app.AmberPrmtopFile(str(prmtop_path))
    crd=app.AmberInpcrdFile(str(inpcrd_path), loadBoxVectors=True)
    failures=[]
    residues=list(top.topology.residues())
    atoms=list(top.topology.atoms())
    waters=[r for r in residues if r.name.upper() in WATER_NAMES]
    biomol=[r for r in residues if r not in waters and r.name.upper() not in {"NA","CL","K","MG","CA","SOD","CLA"}]
    hyp=[r for r in biomol if r.name.upper() in HYP_NAMES]
    if len(biomol)!=EXPECTED_NONWATER:
        failures.append(f"Expected {EXPECTED_NONWATER} protein/collagen residues; found {len(biomol)}")
    if len(hyp)!=EXPECTED_HYP:
        failures.append(f"Expected {EXPECTED_HYP} HYP/XPN residues; found {len(hyp)}")
    if len(waters)<100:
        failures.append(f"Insufficient solvent: {len(waters)} waters")
    if len(atoms)!=len(crd.positions):
        failures.append("Topology and coordinates have different atom counts")
    if crd.boxVectors is None:
        failures.append("No periodic box in INPCRD")
    else:
        from openmm import Vec3
        volume=crd.boxVectors[0].dot(crd.boxVectors[1].cross(crd.boxVectors[2]))
        if volume.value_in_unit(unit.nanometer**3)<=0:
            failures.append("Nonpositive periodic cell volume")
    residue_bonds=collections.defaultdict(set)
    for a,b in top.topology.bonds():
        residue_bonds[a.residue].add(frozenset((a.name,b.name)))
        residue_bonds[b.residue].add(frozenset((a.name,b.name)))
    for r in hyp:
        names={a.name for a in r.atoms()}
        if not any(n in names for n in ("OE","OD1")):
            failures.append(f"HYP {r.chain.id}:{r.id} lacks hydroxyl oxygen")
        required={frozenset(pair) for pair in [("N","CA"),("CA","CB"),("CB","CG"),("CG","CD"),("CD","N"),("CA","C"),("C","O")]}
        if not required.issubset(residue_bonds[r]):
            failures.append(f"HYP {r.chain.id}:{r.id} missing internal bonds")
    # Disulfide identity is checked by explicit SG--SG covalent bond rather than distance alone.
    ss=[]
    for a,b in top.topology.bonds():
        if a.name=="SG" and b.name=="SG" and a.residue!=b.residue:
            ss.append((a.residue,b.residue))
    if len(ss)!=1:
        failures.append(f"Expected exactly one A3 disulfide; found {len(ss)}")
    else:
        pair=ss[0]
        # Residue IDs may be renumbered by topology converters: require CYS and
        # record IDs without asserting numbering if original numbers are lost.
        if any(r.name.upper() not in {"CYS","CYX","CYM"} for r in pair):
            failures.append("Disulfide SG bond does not join cysteine residues")
    # Protein sequence discrimination: chain B is ideally retained, but AMBER
    # converters can renumber: require one unique (non-collagen) histidine or ASP
    # at the known sequential A3 position (1786-1686=100).
    candidates=[list(c.residues()) for c in top.topology.chains()]
    a3=[chain for chain in candidates if len([r for r in chain if r in biomol])==188]
    variant_ok=None
    if len(a3)==1:
        a3res=[r for r in a3[0] if r in biomol]
        mutation=a3res[100].name.upper()
        allowed=HIS_NAMES if label=="WT" else ASP_NAMES
        variant_ok=mutation in allowed
        if not variant_ok:
            failures.append(f"{label} A3 residue 101 expected {sorted(allowed)}; found {mutation}")
    else:
        failures.append("Cannot uniquely identify intact 188-residue A3 chain")
    # Confirm actual force-field system constructs and contains finite energy.
    try:
        system=top.createSystem(nonbondedMethod=app.PME,
            nonbondedCutoff=1.0*unit.nanometer,constraints=app.HBonds)
        if system.getNumParticles()!=len(atoms):
            failures.append("OpenMM System particle-count mismatch")
        from openmm import Context, VerletIntegrator, Platform
        integ=VerletIntegrator(0.001*unit.picoseconds)
        ctx=Context(system,integ,Platform.getPlatformByName("CPU"))
        ctx.setPositions(crd.positions)
        if crd.boxVectors is not None:ctx.setPeriodicBoxVectors(*crd.boxVectors)
        energy=ctx.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
        if not math.isfinite(energy):
            failures.append("Potential energy is nonfinite")
        del ctx,integ
    except Exception as exc:
        failures.append(f"OpenMM creation/energy check failed: {exc}")
    return {"variant":label,"passed":not failures,"failures":failures,
       "residues":len(biomol),"hydroxyprolines":len(hyp),
       "water_residues":len(waters),"atoms":len(atoms),
       "disulfides":len(ss),"variant_identity_checked":variant_ok}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--prepared",default="prepared")
    parser.add_argument("--report",default="topology_qa.json")
    a=parser.parse_args()
    root=Path(a.prepared)
    report={}
    for name in ("WT","H1786D"):
        try:
            report[name]=inspect(root/f"{name}.prmtop",root/f"{name}.inpcrd",name)
        except Exception as exc:
            report[name]={"variant":name,"passed":False,"failures":[str(exc)]}
    success=all(report[name]["passed"] for name in ("WT","H1786D"))
    Path(a.report).write_text(json.dumps({"passed":success,"systems":report},indent=2))
    print(json.dumps({"passed":success,"systems":report},indent=2))
    raise SystemExit(0 if success else 2)
if __name__=="__main__":
    main()
