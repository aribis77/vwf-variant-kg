import test from 'node:test';
import assert from 'node:assert/strict';
import {audit} from './audit.mjs';
const candidate={variant:'H1786D',endpoint:'collagen binding',reference_label:'functional_effect',source:'https://example.org/primary',review_status:'pending'};
test('pending candidates are never eligible',()=>{const a=audit([candidate]);assert.equal(a[0].eligible,false);assert.deepEqual(a[0].errors,[]);});
test('verified requires independent review and effect measurement',()=>{const a=audit([{...candidate,review_status:'verified'}]);assert.equal(a[0].eligible,false);assert.ok(a[0].errors.length>=2);});
test('verified audited reference becomes eligible',()=>{const a=audit([{...candidate,review_status:'verified',reviewer:'A',independent_reviewer:'B',review_date:'2026-10-30',assay_type:'binding assay',organism:'human',numbering_reference:'P04275',effect_measure:'normalized binding',comparator:'wild type'}]);assert.equal(a[0].eligible,true);});
test('same variant with different endpoints is permitted',()=>{const a=audit([candidate,{...candidate,endpoint:'secretion'}]);assert.ok(a.every(x=>!x.errors.length));});
test('duplicate variant-endpoint is rejected',()=>{const a=audit([candidate,candidate]);assert.match(a[1].errors.join(','),/duplicate/);});
