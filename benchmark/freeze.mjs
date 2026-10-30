/** Produce an evaluation reference file only from fully audited candidate records. */
import fs from 'node:fs';
import {audit} from './audit.mjs';
export function freeze(candidates){
 const checks=audit(candidates);
 const problems=checks.filter(x=>x.errors.length);
 if(problems.length)throw Error('Invalid candidate records: '+JSON.stringify(problems));
 const eligible=candidates.filter((c,i)=>checks[i].eligible);
 if(!eligible.length)throw Error('No independently verified reference records; refusing to freeze an empty benchmark');
 return eligible.map(c=>({
  variant:c.variant,endpoint:c.endpoint,label:c.reference_label,
  source:c.source,review_status:'verified',assay_type:c.assay_type,
  organism:c.organism,numbering_reference:c.numbering_reference,
  effect_measure:c.effect_measure,comparator:c.comparator,
  reviewer:c.reviewer,independent_reviewer:c.independent_reviewer,
  review_date:c.review_date
 }));
}
if(process.argv[1]&&import.meta.url===new URL('file://'+process.argv[1]).href){
 const path=process.argv[2];if(!path)throw Error('Usage: node benchmark/freeze.mjs candidate_reference_panel.json');
 console.log(JSON.stringify(freeze(JSON.parse(fs.readFileSync(path,'utf8'))),null,2));
}
