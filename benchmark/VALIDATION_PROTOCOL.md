# VWF variant KG: reference benchmark validation protocol

Status: **candidate panel under source review; not frozen; no validated predictive accuracy**.

## Reference inclusion criteria

1. Verify variant identity and residue numbering against the primary paper and UniProt P04275; retain species, construct and expression system.
2. Specify one **exact** assay endpoint and direction with controls, conditions, effect size and uncertainty where reported.
3. Do not substitute clinical subtype, thrombocytopenia or bleeding for a direct platelet-binding assay.
4. Document source provenance, figure/table location, curator and review date. Abstract-only records remain provisional.
5. Detect overlapping cohorts and duplicated measurements. Count independently validated experimental systems separately from observations and source URLs.
6. Keep the reference label inaccessible to the prediction process. Identify publications already represented in KG training/curation; remove overlapping sources or mark them as leakage.
7. Freeze the benchmark with a versioned manifest and checksum **only after** independent review and a predeclared endpoint-specific scoring rule.

## Candidate panel audit (3 November 2026)

| Variant | Endpoint | Primary source | Evidence scope | Freeze |
|---|---|---|---|---|
| H1786D | Collagen binding | PMID 25051961 | Mouse VWF model; collagen/adhesion findings; human transfer not established | No |
| R1597W | ADAMTS13 proteolysis | PMID 16322474 | Recombinant human VWF; qualitative increased susceptibility; effect size pending | No |
| R854Q | FVIII binding | Blood 2023 abstract 190788 | HEK293 surface-tethered VWF; abstract-only | No |
| D879N | FVIII binding | Blood 2023 abstract 190788 | HEK293 surface-tethered VWF; abstract-only | No |
| R1306W | Thrombocytopenia occurrence | JTH 2024, DOI 10.1016/j.jtha.2024.08.028 | Longitudinal type 2B clinical cohort; not a GPIb assay | No |
| R1308C | Thrombocytopenia occurrence | JTH 2024, DOI 10.1016/j.jtha.2024.08.028 | Same cohort, distinct genotype group; not an independent study | No |

## Prespecified evaluation once frozen

- Unit of evaluation: unique variant–assay–experimental-context pair, not number of observations.
- Stratify by collagen subtype, ADAMTS13 proteolysis, FVIII binding, platelet GPIb assays and clinical endpoints. Never pool into one unvalidated binary label.
- For a direction classifier, calculate per-endpoint confusion matrices, balanced accuracy and abstention rate; report sample sizes and confidence intervals. Do not calculate accuracy when predictions are all abstentions.
- Report source overlap, cohort overlap and structural model availability for every evaluated pair.
- Run leave-publication-out evaluation only where multiple independent publications support a sufficiently sized endpoint-specific test.
- Benchmark against a literature-retrieval baseline and a model-assisted literature baseline using the same blinded references. Record versions, prompts and retrieval dates.
- Do not interpret benchmark agreement as clinical pathogenicity classification.

## Current gate

The portal exports a **readiness audit**, not a performance benchmark. None of the six candidates has been frozen or independently replicated within the benchmark metadata. No predictive accuracy claim is justified.
