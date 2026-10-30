# VWF variant consensus benchmark

## Objective
Test whether integrated KG, structural, conservation and empirical-energy evidence improves prediction of **experimentally observed functional effects**. Do not equate this endpoint with clinical pathogenicity or VWD subtype diagnosis.

## Reference-set curation
Create a frozen, independently reviewed `reference.json` containing one record per variant and pre-specified functional endpoint. Each entry requires:
- `variant`: full-length VWF protein substitution (e.g. `R1306W`), with numbering verified against UniProt P04275.
- `endpoint`: named assay endpoint (e.g. GPIb binding, collagen binding, FVIII binding, secretion, multimerization).
- `label`: `functional_effect`, `no_demonstrated_effect`, or `uncertain`.
- `source`: primary publication DOI/PMID with assay and comparison.
- `review_status`: `verified` only after independent review.

Do not assume that lack of reported effect is evidence of no effect. Avoid reusing a single variant across contradictory endpoints in the initial variant-level evaluation; later stratify by endpoint.

## Leakage prevention
1. Freeze the reference set and analysis plan before reviewing model predictions.
2. Exclude the reference assay evidence from the KG features for a true held-out evaluation, or explicitly label the result **evidence-retrieval agreement**, not prediction.
3. Group related variants, studies and overlapping patient cohorts to reduce leakage.
4. Stratify by VWF domain, phenotype and structure availability.
5. Report missingness and abstentions alongside performance; never force a conclusion when evidence is insufficient.
6. Compare KG-only, structural-only and combined consensus using identical held-out variants.
7. Treat multiple PDB structures of one variant as correlated evidence, not independent replicates.

## Input and evaluation
`predictions.json` is an array with `variant`, `endpoint`, `label`, optional `score` and `version`. Labels must be `functional_effect`, `no_demonstrated_effect`, or `uncertain`.

Run:
```sh
node benchmark/evaluate.mjs benchmark/reference.json benchmark/predictions.json > benchmark/results.json
```

The evaluator returns coverage, selective accuracy, sensitivity, specificity and row-level audit data. Null metrics mean there was no evaluable denominator. These are descriptive statistics, not clinical validation.

## Next integration
Export variant-independent consensus results from the KG as predictions.json. Assemble a DOI-backed, dual-reviewed reference set and perform the held-out comparison. Do not publish benchmark performance before reference data and predictions are available.

## Reference eligibility audit
Run `node benchmark/audit.mjs benchmark/candidate_reference_panel.json`.
Pending records are listed but never marked eligible. For verified records, the audit requires `reviewer`, `independent_reviewer`, `review_date`, `assay_type`, `organism`, `numbering_reference`, `effect_measure` and `comparator`. This is a completeness gate, not independent verification of a paper's contents. Audit records remain pending until the actual experimental evidence has been checked. Never turn a candidate into a negative control based on absence of a reported effect.

The evaluator matches reference and prediction records by the compound key `variant + endpoint`. The endpoint string must be identical after case/whitespace normalization in both inputs. Do not merge distinct functional endpoints into a single label.

## Assay-specific evidence candidates
`assay_evidence_candidates.json` contains literature-derived assay comparisons including collagen I/III versus collagen IV for H1786D and S1731T. These are **pending curation**, not frozen verified references. Qualitative 'unaltered' reports are candidates for `no_demonstrated_effect`, not proof of equivalence. Before verification, capture effect size, variability, assay sensitivity, biological replicates, species, collagen type, and DOI/figure/table. Preserve the human-versus-mouse distinction for R1597W.

This file deliberately separates endpoint-specific negative controls from variant-wide benign assertions. No benchmark accuracy may be calculated using pending records.
