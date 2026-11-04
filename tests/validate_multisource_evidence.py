#!/usr/bin/env python3
"""Validate the VWF multi-source evidence snapshot without external dependencies."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/multisource-evidence.json').read_text())
assert data['schema_version']=='vwf-multisource-evidence/0.1'
assert isinstance(data['sources'],list) and isinstance(data['alleles'],list) and isinstance(data['assertions'],list)
valid_status={'not_ingested','ingested','unavailable','requires_license','error'}
sources=set()
for s in data['sources']:
    assert s['source'] not in sources, 'duplicate source'
    sources.add(s['source'])
    assert s['status'] in valid_status
    assert isinstance(s['record_count'],int) and s['record_count']>=0
    if s['status']=='ingested':
        assert s.get('retrieved_at') and s.get('release'), 'ingested source must be versioned'
alleles={}
for a in data['alleles']:
    assert a['allele_id'] not in alleles,'duplicate allele ID'
    alleles[a['allele_id']]=a
    assert a['assembly'] and a['chromosome'] and a['position']>0 and a['reference'] and a['alternate']
    assert a['provenance']['source_record_id'] and a['provenance']['source_url']
    for p in a['protein_effects']:
        assert p['uniprot_accession']=='P04275'
        assert p['mapping_status'] in {'verified','unverified','ambiguous'}
assertions=set()
for a in data['assertions']:
    assert a['assertion_id'] not in assertions,'duplicate assertion ID'
    assertions.add(a['assertion_id'])
    assert a['allele_id'] in alleles,'orphan assertion'
    assert a['evidence_type'] in {'source_record','clinical_assertion','population_observation','functional_assay','structural_model','curated_literature'}
    assert a['provenance']['source_record_id'] and a['provenance']['source_url']
    if a['evidence_type']=='clinical_assertion':
        assert not str(a['provenance'].get('review_status', '')).startswith('provisional'), 'provisional identity must not be clinical evidence'
    if a['evidence_type']=='functional_assay':
        assert a.get('endpoint') and a.get('assay_context'), 'functional assays need endpoint and context'
print(f"Validated: {len(sources)} sources, {len(alleles)} alleles, {len(assertions)} assertions")
