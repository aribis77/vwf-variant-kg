# VWF-KG multi-source integration: implementation specification

Status: **design proposal, not implemented source ingestion**. Scope: VWF only.

## Current baseline
The browser graph contains 192 nodes, 290 edges and 112 observations in its embedded data snapshot (checked 2026-11-04). These are not evidence of complete ClinVar/gnomAD/LOVD ingestion. Existing literature observations, curated endpoint records and structural reports must remain distinguishable from external database assertions.

## Source registry and access
| Source | Purpose | First implementation |
|---|---|---|
| ClinVar | VWF allele assertions, condition, classification, review status, submitter and dates | Versioned API/VCF ingestion with stable variation/allele IDs |
| Ensembl / HGVS reference sequences | Genomic coordinates, transcript mapping and consequence | Pin assembly, transcript accession and transcript version |
| gnomAD | Population allele frequencies, allele counts, ancestry-specific denominators and filters | Match normalized allele and genome build; never use absence as proof of pathogenicity |
| UniProt P04275 | Protein sequence, domain features and numbering | Versioned sequence reference |
| RCSB PDB / PDBe | Structures, chain mappings and experimental provenance | Coordinate-verified mapping; store accession, chain, residue numbering and structure context |
| LOVD / VWF-specific databases | Curated variant and phenotype assertions | Assess availability, license, attribution and export/API terms before implementation |
| Primary literature | Endpoint-specific experimental measurements and clinical observations | Retain assay conditions, source location and primary-study identity |

HGMD is a licensed resource; do not scrape or redistribute restricted records.

## Minimal typed schema
- `SourceRecord`: source, source_record_id, source_url, retrieved_at, source_release, license, raw_record_checksum.
- `VariantAllele`: canonical SPDI or VRS ID, assembly, chromosome, position, reference, alternate; do not use protein substitution alone as allele identity.
- `VariantProteinEffect`: UniProt accession and sequence version, HGVS p., transcript accession/version, reference sequence, mapping confidence.
- `Assertion`: source_record_id, subject_id, predicate, object_id/value, evidence_type (clinical_assertion, population_observation, functional_assay, structural_model, curated_literature), original_text/value, review_status, assertion_date.
- `AssayObservation`: variant/construct, endpoint ontology ID, value, unit, assay, control, sample size, conditions, species, study_id.
- `Provenance`: originating publication, submitter, DOI/PMID, database accession, deduplication cluster, conflicts, curator decisions.

## Non-negotiable harmonization rules
1. Distinguish a genomic allele from a protein-level substitution: multiple alleles can map to the same amino-acid change.
2. Record genome assembly, transcript version, VWF precursor/mature-protein numbering and PDB author/label numbering.
3. Never convert a ClinVar classification or cohort phenotype into a direct functional-assay measurement.
4. Do not count database summaries and their underlying paper as independent evidence.
5. Preserve conflicting classifications and source-specific timestamps rather than overwriting them.
6. Keep collagen I/III/VI binding, GPIb binding, ADAMTS13 proteolysis, FVIII binding and clearance separate.
7. Keep exploratory Protein Workbench empirical energy and conservation scores separate from experimental free energies and functional assays.
8. Missing evidence is `not_evaluated`, not benign; do not create unvalidated pathogenicity scores.

## Implementation sequence
**Stage A: inventory and schema.** Audit current graph node/edge identifiers and provenance; create JSON schema and fixtures for the types above. No live data changes.

**Stage B: pilot ingestion.** Choose 5-10 VWF variants (including R1315L and H1786D), import ClinVar and Ensembl records with stable identifiers, and show source-specific assertions. Capture unavailable sources explicitly.

**Stage C: population and molecular context.** Add gnomAD allele-specific population frequencies, UniProt features and existing verified PDB mappings. Validate assembly and residue numbering.

**Stage D: literature reconciliation.** Link imported assertions to existing observations and original publications, detect duplicates and contradictory claims, display independent evidence counts.

**Stage E: portal views.** Add source filters, variant identity panel, source disagreement table, update timestamps, provenance drill-down and a multi-source integrated report.

**Stage F: quality gates.** Automated schema, normalization, provenance, duplicate and endpoint-isolation tests; manual review of 10 pilot variants; freeze snapshots for reproducibility.

## Definition of done for pilot
- Every displayed assertion has source accession, retrieval date and traceable provenance.
- Genomic and protein numbering are cross-checked and discrepancies flagged.
- Distinct clinical, population, functional and structural evidence categories remain separable.
- Duplicate primary evidence is counted once.
- At least one disagreement and one missing-data case are correctly displayed.
- No source silently determines a clinical classification or numerical score.

## Presentation alignment
The revised VWF-KG presentation introduces this as a planned multi-source evidence layer, not a capability already deployed.
