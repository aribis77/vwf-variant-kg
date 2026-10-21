# VWF A3–collagen III paired MD automation

**Status: runner prepared; topology construction and real MD not yet completed.**

This public repository stores automation **code only**, not unpublished VWF/collagen structure coordinates or force-field input files. The original v1–v17 preparation tests established hydroxyproline connectivity but did not validate chain termini, disulfide-specific parameterization, or solvated periodic systems.

The workflow runs manually from the GitHub Actions tab. It installs OpenMM, checks for four periodic AMBER files (`WT.prmtop`, `WT.inpcrd`, `H1786D.prmtop`, `H1786D.inpcrd`) and a **genuine** `chemistry_approved.json`, then performs a 100-ps paired smoke test. It fails safely until inputs are available.

**Do not mark chemistry approved merely to bypass the check.** Chemically validated 4R-hydroxyproline, chain ends/caps, VWF C1686–C1872 disulfide, histidine protonation, ions and solvent are mandatory. Identical choices are required for WT and H1786D. Store unpublished topologies in a private compute repository, not here.

Outputs, if a calculation is genuinely successful, are DCD trajectories, state-data CSV, starting/final coordinates, and a manifest; errors are uploaded as workflow artifacts.

This is an execution scaffold, **not** an unattended CHARMM-GUI topology builder or an affinity/ΔΔG calculation.
