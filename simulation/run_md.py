#!/usr/bin/env python3
"""Run a paired OpenMM pilot from previously validated AMBER inputs."""
import json
from pathlib import Path
import openmm as mm
from openmm import app, unit

prepared=Path("prepared")
approval=json.loads((prepared/"chemistry_approved.json").read_text())
if approval.get("approved") is not True:
    raise RuntimeError("Chemistry approval required")
Path("results").mkdir(exist_ok=True)

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
    simulation.context.setPeriodicBoxVectors(*coordinates.boxVectors)
    simulation.minimizeEnergy(maxIterations=1000)
    simulation.context.setVelocitiesToTemperature(300*unit.kelvin,seed)
    simulation.reporters.append(app.DCDReporter("results/"+label+".dcd",500))
    simulation.reporters.append(app.StateDataReporter("results/"+label+".csv",500,step=True,potentialEnergy=True,temperature=True))
    simulation.step(50000)
    with open("results/"+label+"_final.pdb","w") as output:
        app.PDBFile.writeFile(topology.topology,simulation.context.getState(getPositions=True).getPositions(),output)
