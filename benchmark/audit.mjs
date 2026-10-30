/** Validate candidate reference records before freezing an endpoint-specific panel. */
import fs from 'node:fs';
const AA=/^[ACDEFGHIKLMNPQRSTVWY][1-9][0-9]{0,4}[ACDEFGHIKLMNPQRSTVWY]$/;
const LABELS=new Set(['functional_effect','no_demonstrated_effect','uncertain']);
export function audit(rows){
 if(!Array.isArray(rows))throw Error('Expected array');
 const seen=new Set();
 return rows.map((r,i)=>{
  const errors=[];
  if(!AA.test(r.variant||''))errors.push('invalid variant');
  if(!r.endpoint||typeof r.endpoint!=='string')errors.push('missing endpoint');
  const key=r.variant+'|'+r.endpoint?.trim().toLowerCase();
  if(seen.has(key))errors.push('duplicate variant-endpoint');
  seen.add(key);
  if(!LABELS.has(r.reference_label))errors.push('invalid reference label');
  if(!/^https:\/\//.test(r.source||''))errors.push('missing source URL');
  if(r.review_status==='verified'){
   if(!r.reviewer||!r.review_date||!r.assay_type||!r.organism||!r.numbering_reference)errors.push('verified record missing audit metadata');
   if(!r.independent_reviewer)errors.push('missing independent reviewer');
   if(!r.effect_measure||!r.comparator)errors.push('missing effect measure or comparator');
  }
  if(r.review_status!=='verified'&&r.review_status!=='pending'&&r.review_status!=='rejected')errors.push('invalid review status');
  return {row:i+1,variant:r.variant,endpoint:r.endpoint,status:r.review_status,eligible:!errors.length&&r.review_status==='verified',errors};
 });
}
if(process.argv[1]&&import.meta.url===new URL('file://'+process.argv[1]).href){
 const path=process.argv[2];if(!path)throw Error('Usage: node benchmark/audit.mjs candidate_reference_panel.json');
 const results=audit(JSON.parse(fs.readFileSync(path,'utf8')));
 console.log(JSON.stringify({total:results.length,eligible:results.filter(x=>x.eligible).length,results},null,2));
 if(results.some(x=>x.errors.length))process.exitCode=1;
}
