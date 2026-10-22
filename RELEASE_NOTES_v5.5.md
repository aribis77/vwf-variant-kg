# VWF Variant Knowledge Graph — v5.5 release candidate

## Contents
- `index.html` — GitHub Pages site, with original embedded graph and H1786D evidence panel.
- `data/simulation_evidence/VWF_H1786D_20ps.json` — six user-reported 20-ps endpoint measurements (3 WT; 3 H1786D), provenance and caveats.
- `docs/VARIANT_EVIDENCE_TIERS.md` — tiered evidence policy for all VWF variants.

## Changes since v5.4
- Preserves 192 nodes, 290 relationships and 112 curated observations.
- Adds optional Tier 3 short-MD evidence for H1786D, without reclassifying clinical or functional assertions.
- Displays mean WT/mutant contact and distance endpoints, links to full per-replicate data.
- Explicitly labels simulation provenance as user-reported and not independently audited.
- Updates MD status wording to distinguish exploratory endpoints from production MD.

## Automated source-level checks
- Parsed embedded graph JSON: PASS.
- Baseline graph counts: PASS (192/290/112).
- Dangling edge references: PASS (0).
- Presence of evidence links and panel: PASS.
- Browser interaction and visual QA: NOT RUN.
- Scientific provenance audit against original trajectory/checkpoint/analysis code: NOT RUN.

## Deployment
GitHub Pages serves `index.html` from the configured branch and folder. To preview this release, use a separate Pages branch or inspect locally; uploading a ZIP does not automatically deploy it. The downloadable repository ZIP includes the complete branch snapshot.

## Scientific caution
These are six short-run endpoints, not long-timescale equilibrium estimates, binding free energies, or proof of pathogenicity. Replicates share variant-specific initial structures. Original structural input and contact-selection code should be audited before peer-reviewed quantitative claims.
