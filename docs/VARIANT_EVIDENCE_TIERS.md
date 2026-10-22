# Variant evidence tiers (draft)

This branch adds a machine-readable, **user-reported** 20-ps VWF H1786D endpoint observation. It is not a claim of validated binding affinity, pathogenicity, or production MD. It has not yet been wired into the website.

## Evidence policy

- Tier 1: literature/database evidence, including source accession, publication, transcript version, assertion date, review status and clinical context. Preserve conflicting assertions.
- Tier 2: computational structural annotations, including model accession/version, residue mapping, method and uncertainty.
- Tier 3: selected exploratory MD observations, with starting structures, force field, checkpoint provenance, per-replicate metrics, atom selections, cutoffs and QC.

All variants may enter Tier 1; Tier 2 and Tier 3 are optional. Absence of simulation evidence is **not** evidence of no effect.

## First record

`data/simulation_evidence/VWF_H1786D_20ps.json` contains six endpoint observations (WT 3, H1786D 3), from the user's validation output. Contact and distance definitions remain to be audited against analysis code. Replicates share variant-specific starting models, so they do not establish independent biological replication. This record should not be surfaced as experimentally verified.

## Next integration gates

1. Confirm transcript/protein numbering and mapping of residue 1786.
2. Verify contact cutoff, residue selections and structural input provenance.
3. Add a separate evidence entity and links in the graph UI, explicitly labeled exploratory simulation.
4. Ingest external ClinVar/EAHAD/LOVD records only with source identifiers, licensing checks and date-stamped assertions; never infer clinical significance from the simulation.
5. Add schema tests and conflict handling before scaling ingestion.
