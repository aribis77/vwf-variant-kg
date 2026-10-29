# VWF Variant Knowledge Graph

Live demonstration: https://aribis77.github.io/vwf-variant-kg/

This browser-based evidence graph links VWF variants, experimental observations, published sources and selected structural interpretations. It is **not** a clinical variant-classification system or a substitute for source verification.

## Protein Workbench integration (experimental)

The KG can open the independent [Protein Workbench](https://aribis77.github.io/protein-workbench/) with a selected substitution, a user-supplied PDB accession, an optional chain identifier and the requested analysis mode. Workbench is a reusable protein-analysis tool, not a VWF-specific calculation engine.

The interface currently supports the following requests:

| Analysis | Current behavior |
| --- | --- |
| Interface contacts | Runs structural contact mapping and mutant construction after validating the PDB residue mapping |
| Relative binding energy | Runs empirical energy scoring; this **does not establish a binding ΔΔG** |
| Conformational sampling | Runs an exploratory quick ensemble, not validated production MD |
| Sequence conservation | Attempts automatic RCSB PDB homologue search and query-anchored alignment; a custom HTTPS FASTA/CLUSTAL alignment is optional |
| Combined | Attempts contact, mutant, empirical-energy and quick-ensemble analyses, optionally conservation, and exports a machine-readable analysis-status report |

### How to use

Select a variant, enter a validated four-character PDB accession, optionally supply the chain; a custom HTTPS alignment URL is available under Advanced, choose the analysis and click **Load structure in Workbench**. A PDB residue number can differ from the numbering of full-length VWF. The Workbench validates the expected wild-type amino acid and requires an unambiguous residue match before attempting mutation analysis.

The **Export request JSON** action is a separate metadata-only export, not an executable computational job. The standalone **Open Protein Workbench** link opens Workbench without a configured job.

### Limitations and status

- The KG does not yet maintain a validated automatic variant-to-PDB residue mapping. The PDB ID must be supplied by the user.
- The workflow is a cross-site URL handoff, not embedded computing or server-side job orchestration.
- Results do not automatically return to the KG or update evidence records.
- Automatic conservation uses structurally characterized PDB homologues and may be biased by PDB coverage. A curated alignment is recommended for evolutionary conclusions. Network or cross-origin restrictions may prevent automatic retrieval.
- Combined reports record which analyses ran, but do not yet generate an evidence-weighted causal explanation from KG literature.
- Exploratory conformational ensembles and empirical scores should not be described as production MD or validated binding free energies.
- The implementation has been committed, but no independently documented end-to-end live-browser validation has been completed.

## Scientific practice

Keep primary experimental observations, published computational claims, and new Workbench predictions separate. Record structural accession, chain, residue-numbering correspondence, model and alignment provenance, computational settings, uncertainty and independent validation. Missing evidence should be marked *not evaluated*.

## Related project

[The Protein Workbench](https://github.com/aribis77/protein-workbench) is developed and maintained as an independent, general-purpose structural biology application.

### Quantitative evidence profile

When a compatible Workbench combined JSON report contains `metrics`, the variant report displays measured contact turnover and conservation fractions and records available empirical energy and sampling evidence. The downloadable integrated JSON includes a `derived_quantitative_profile` and `analysis_coverage`. No functional-impact, evidence-confidence, mechanistic-concordance or overall 0–100 score is assigned until calibration and evidence auditing. Imported results remain local to the browser.

### Multi-structure workflow (experimental)

Use **Discover suitable PDBs**, then **Prepare multi-PDB runs** to obtain up to eight separate combined-analysis links. Each PDB must independently validate residue mapping in Workbench. Download its combined JSON result and import multiple JSON files simultaneously into the variant report. The report displays per-structure measurements and descriptive ranges for contact turnover and conservation. This is **not yet unattended batch execution**: the browser-based Workbench runs remain separate, RCSB discovery and mapping require live validation, and structures must not be treated as independent biological replicates. Reports are session-local; export the integrated JSON to preserve results.

### Automatic KG result return (experimental)

When Workbench is launched from the KG with a one-time random launch token and an approved return origin, its combined JSON report is sent back to the originating KG browser tab via `postMessage`. The KG validates the message origin, token, PDB and mutation before adding the result to its session-local variant report. Keep the KG tab open. This is a browser-to-browser handoff, not a server-side job queue or durable storage; it has not yet been validated in a live browser. Standalone Workbench remains independent and still exports JSON. Manual import/reset in the KG is under Advanced.
