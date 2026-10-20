#!/usr/bin/env python3
"""Run a paired OpenMM pilot from previously validated AMBER inputs."""
import argparse
import json
from pathlib import Path
import openmm as mm
from openmm import app, unit

parser=argparse.ArgumentParser()
parser.add_argument("--prepared", default="prepared")
parser.add_argument("--out", default="results")
parser.add_argument("--steps", type=int, default=50000)
args=parser.parse_args()
if not 1 <= args.steps <= 500000:
    raise ValueError("steps must be between 1 and 500000")
prepared=Path(args.prepared)
approval=json.loads((prepared/"chemistry_approved.json").read_text())
if approval.get("approved") is not True:
    raise RuntimeError("Chemistry approval required")
Path(args.out).mkdir(parents=True,exist_ok=True)

for label, seed in [("WT",1786),("H1786D",1787)]:
    topology=app.AmberPrmtopFile(str(prepared/(label+".prmtop")))
    coordinates=app.AmberInpcrdFile(str(prepared/(label+".inpcrd")),loadBoxVectors=True)
    if coordinates.boxVectors is None:
        raise RuntimeError("Periodic cell required")
    system=topology.createSystem(nonbondedMethod=app.PME,nonbondedCutoff=1.0*unit.nanometer,constraints=app.HBonds)
    system.addForce(mm.MonteCarloBarostat(1*unit.bar,300*unit.kelvin,25))
    integrator=mm.LangevinMiddleIntegrator(300*unit.kelvin,1/unit.picosecond,0.002*unit.picoseconds)
    integrator.setRandomNumberSeed(seed)
    simulation=app.Simulation(topology.topology,system,integrator,mm.Platform.getPlatformByName("CPU"))
    simulation.context.setPositions(coordinates.positions)
    if len(coordinates.positions) != system.getNumParticles():
        raise ValueError(f"Atom count mismatch for {label}")
    simulation.context.setPeriodicBoxVectors(*coordinates.boxVectors)
    simulation.minimizeEnergy(maxIterations=1000)
    simulation.context.setVelocitiesToTemperature(300*unit.kelvin,seed)
    simulation.reporters.append(app.DCDReporter(str(Path(args.out)/label)+".dcd",max(1,args.steps//100)))
    simulation.reporters.append(app.StateDataReporter("results/"+label+".csv",500,step=True,potentialEnergy=True,temperature=True))
    simulation.step(args.steps)
    with open("results/"+label+"_final.pdb","w") as output:
        app.PDBFile.writeFile(topology.topology,simulation.context.getState(getPositions=True).getPositions(),output)
