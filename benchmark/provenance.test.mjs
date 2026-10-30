import test from 'node:test';
import assert from 'node:assert/strict';
import {publicationKey,studyKey} from './provenance.mjs';
test('DOI URL and explicit DOI normalize identically',()=>{
 assert.equal(publicationKey({doi:'https://doi.org/10.1111/ABC.123'}),'doi:10.1111/abc.123');
 assert.equal(publicationKey({source_url:'https://doi.org/10.1111/ABC.123'}),'doi:10.1111/abc.123');
});
test('PubMed IDs normalize',()=>{
 assert.equal(publicationKey({pmid:'22372972'}),'pmid:22372972');
 assert.equal(publicationKey({source_url:'https://pubmed.ncbi.nlm.nih.gov/22372972/'}),'pmid:22372972');
});
test('study identifiers remain subordinate to publication',()=>{
 assert.equal(studyKey({doi:'10.1111/abc.123',study_id:'cohort-a'}),'doi:10.1111/abc.123|study:cohort-a');
});
test('unlinked records do not claim independent publications',()=>{
 assert.equal(publicationKey({}),null);
});
