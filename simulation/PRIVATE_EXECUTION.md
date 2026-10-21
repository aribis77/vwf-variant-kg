# Private execution protocol

**Public GitHub Actions now runs only non-sensitive smoke checks.** The WT/H1786D
coordinate models, solvated topologies, trajectories, chemistry approval records
and numerical energies must remain outside this public repository.

## One-command simulation after scientific chemistry signoff

On a private workstation, HPC job, or an access-controlled container with
Python 3.11 and OpenMM 8.x installed, place the following files in an
OUTSIDE-repository directory such as `/secure/vwf/approved/`:

- `WT.prmtop`, `WT.inpcrd`
- `H1786D.prmtop`, `H1786D.inpcrd`
- `chemistry_approved.json` documenting actual force-field chemistry decisions
  (approved=true, prepared_by, chemistry_protocol, forcefield, protonation,
  hydroxyproline, termini, disulfide, solvent_ions).

Run:
```bash
python -m pip install "openmm>=8.2,<9"
python simulation/private_pipeline.py \
  --private-dir /secure/vwf/approved \
  --results-dir /secure/vwf/results \
  --validate-only
# only after the preceding gate succeeds:
python simulation/private_pipeline.py \
  --private-dir /secure/vwf/approved \
  --results-dir /secure/vwf/results --steps 50000
```

The orchestrator writes SHA256 checksums and a topology QA report before it
allows the real pilot. It prevents output paths inside the public checkout.

**Limitations:** Neither the script nor OpenMM can decide the scientifically
correct collagen peptide caps, disulfide chemistry, hydroxyproline stereochemistry,
force-field compatibility or WT His1786 protonation. Those must be justified
and tested before `chemistry_approved.json` is marked approved. The QA code is a
second line of defence, not scientific approval. There is no simulated trajectory
until this pipeline runs successfully with valid systems.

To automate on a remote scheduler, run the same command in a **private**
repository or private HPC/runner. Do not use public GitHub Actions with private
molecular inputs.
