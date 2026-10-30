import test from 'node:test';
import assert from 'node:assert/strict';
import {evaluate} from './evaluate.mjs';
const refs=[
 {variant:'R1306W',endpoint:'GPIb binding',label:'functional_effect',source:'doi:example-positive',review_status:'verified'},
 {variant:'R1308C',endpoint:'GPIb binding',label:'no_demonstrated_effect',source:'doi:example-negative',review_status:'verified'}
];
// Synthetic fixtures only: names and labels are not biological assertions.
test('coverage and conditional performance',()=>{
 const result=evaluate(refs,[{variant:'R1306W',endpoint:'GPIb binding',label:'functional_effect'},{variant:'R1308C',endpoint:'GPIb binding',label:'uncertain'}]);
 assert.equal(result.coverage,0.5);
 assert.equal(result.selective_accuracy,1);
 assert.equal(result.sensitivity,1);
 assert.equal(result.specificity,null);
});
test('no predictions produces null accuracy, zero coverage',()=>{
 const result=evaluate(refs,[]);
 assert.equal(result.coverage,0);
 assert.equal(result.selective_accuracy,null);
 assert.equal(result.missing_predictions.length,2);
});
test('reject unverified reference',()=>{
 assert.throws(()=>evaluate([{...refs[0],review_status:'pending'}],[]),/Unverified/);
});
test('reject duplicate predictions',()=>{
 assert.throws(()=>evaluate(refs,[{variant:'R1306W',endpoint:'GPIb binding'},{variant:'R1306W',endpoint:'GPIb binding'}]),/duplicate/);
});

test('same variant across distinct endpoints remains independent',()=>{
 const reference=[
  {...refs[0],variant:'R1306W',endpoint:'GPIb binding'},
  {...refs[0],variant:'R1306W',endpoint:'secretion',label:'no_demonstrated_effect'}
 ];
 const result=evaluate(reference,[
  {variant:'R1306W',endpoint:'GPIb binding',label:'functional_effect'},
  {variant:'R1306W',endpoint:'secretion',label:'no_demonstrated_effect'}
 ]);
 assert.equal(result.n_called,2);
 assert.equal(result.selective_accuracy,1);
});
test('a prediction for the wrong endpoint does not count',()=>{
 const result=evaluate([refs[0]],[{variant:'R1306W',endpoint:'secretion',label:'functional_effect'}]);
 assert.equal(result.n_called,0);
 assert.deepEqual(result.missing_predictions,[{variant:'R1306W',endpoint:'GPIb binding'}]);
});
