/**
 * VWF consensus benchmark evaluator.
 * Reference labels must be independently curated, source-backed and frozen
 * before inspecting predictions. This module never invents reference labels.
 * Usage: node benchmark/evaluate.mjs reference.json predictions.json
 */
import fs from 'node:fs';
const LABELS = new Set(['functional_effect','no_demonstrated_effect','uncertain']);
const normalize = x => String(x ?? '').trim().toLowerCase();
export function evaluate(reference, predictions) {
  if (!Array.isArray(reference) || !Array.isArray(predictions)) throw Error('Expected arrays');
  const refs = new Map();
  for (const r of reference) {
    if (!r.variant || refs.has(r.variant)) throw Error('Missing/duplicate reference variant');
    if (!LABELS.has(normalize(r.label))) throw Error('Invalid reference label: '+r.variant);
    if (!r.source || !r.endpoint || !r.review_status || r.review_status !== 'verified') throw Error('Unverified reference: '+r.variant);
    refs.set(r.variant,r);
  }
  const pred = new Map();
  for (const p of predictions) {
    if (!p.variant || pred.has(p.variant)) throw Error('Missing/duplicate prediction variant');
    pred.set(p.variant,p);
  }
  const rows = [...refs.values()].map(r => {
    const p = pred.get(r.variant);
    const label = normalize(p?.label);
    const valid = LABELS.has(label);
    const abstained = !valid || label === 'uncertain';
    return {variant:r.variant,endpoint:r.endpoint,reference:r.label,prediction:valid?label:null,
      abstained,correct:!abstained && label===normalize(r.label),
      source:r.source,score:p?.score??null,version:p?.version??null};
  });
  const determinate = rows.filter(r=>r.reference!=='uncertain');
  const called = determinate.filter(r=>!r.abstained);
  const positive = called.filter(r=>r.reference==='functional_effect');
  const allPositive = determinate.filter(r=>r.reference==='functional_effect');
  const allNegative = determinate.filter(r=>r.reference==='no_demonstrated_effect');
  const negative = called.filter(r=>r.reference==='no_demonstrated_effect');
  const tp=positive.filter(r=>r.correct).length, fn=positive.length-tp;
  const tn=negative.filter(r=>r.correct).length, fp=negative.length-tn;
  const fraction=(n,d)=>d?n/d:null;
  return {n_reference:rows.length,n_determinate:determinate.length,n_called:called.length,
    coverage:fraction(called.length,determinate.length),
    selective_accuracy:fraction(called.filter(r=>r.correct).length,called.length),
    sensitivity:fraction(tp,positive.length),
    specificity:fraction(tn,negative.length),
    positive_coverage:fraction(positive.length,allPositive.length),
    negative_coverage:fraction(negative.length,allNegative.length),
    confusion_matrix_called:{true_positive:tp,false_negative:fn,true_negative:tn,false_positive:fp},
    warning:'Sensitivity and specificity are conditional on non-abstained predictions; inspect class-specific coverage.',
    missing_predictions:rows.filter(r=>!pred.has(r.variant)).map(r=>r.variant),
    rows};
}
if (process.argv[1] && import.meta.url === new URL('file://'+process.argv[1]).href) {
  const [a,b]=process.argv.slice(2);
  if (!a||!b) {console.error('Usage: node benchmark/evaluate.mjs reference.json predictions.json');process.exit(2);}
  console.log(JSON.stringify(evaluate(JSON.parse(fs.readFileSync(a)),JSON.parse(fs.readFileSync(b))),null,2));
}
