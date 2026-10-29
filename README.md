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
| Sequence conservation | Requires an accessible HTTPS FASTA/CLUSTAL multiple-sequence alignment; no automatic homolog search or alignment construction |
| Combined | Attempts contact, mutant, empirical-energy and quick-ensemble analyses, optionally conservation, and exports a machine-readable analysis-status report |

### How to use

Select a variant, enter a validated four-character PDB accession, optionally supply the chain and an HTTPS alignment URL, choose the analysis and click **Load structure in Workbench**. A PDB residue number can differ from the numbering of full-length VWF. The Workbench validates the expected wild-type amino acid and requires an unambiguous residue match before attempting mutation analysis.

The **Export request JSON** action is a separate metadata-only export, not an executable computational job. The standalone **Open Protein Workbench** link opens Workbench without a configured job.

### Limitations and status

- The KG does not yet maintain a validated automatic variant-to-PDB residue mapping. The PDB ID must be supplied by the user.
- The workflow is a cross-site URL handoff, not embedded computing or server-side job orchestration.
- Results do not automatically return to the KG or update evidence records.
- Conservation requires a supplied, methodologically suitable alignment; browser cross-origin restrictions may prevent fetching it.
- Combined reports record which analyses ran, but do not yet generate an evidence-weighted causal explanation from KG literature.
- Exploratory conformational ensembles and empirical scores should not be described as production MD or validated binding free energies.
- The implementation has been committed, but no independently documented end-to-end live-browser validation has been completed.

## Scientific practice

Keep primary experimental observations, published computational claims, and new Workbench predictions separate. Record structural accession, chain, residue-numbering correspondence, model and alignment provenance, computational settings, uncertainty and independent validation. Missing evidence should be marked *not evaluated*.

## Related project

[The Protein Workbench](https://github.com/aribis77/protein-workbench) is developed and maintained as an independent, general-purpose structural biology application.
