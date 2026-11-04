(function(){
'use strict';
const escapeHTML=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const section=document.createElement('section');
section.id='vwf-multisource-panel';
section.style.cssText='margin:24px auto;padding:22px;max-width:1180px;border:1px solid #b8d2e0;border-radius:14px;background:#142b42;color:#f3f7fb';
section.innerHTML='<h2 style="margin:0 0 8px;color:#7cdecf">Genetic and variant database evidence</h2><p id="vwf-multisource-status">Loading source registry…</p><div id="vwf-multisource-sources"></div><div id="vwf-multisource-variant"></div>';
const target=document.getElementById('variant-report')||document.querySelector('main')||document.querySelector('.wrap')||document.body;
target.appendChild(section);
section.setAttribute('aria-live','polite');
let snapshot=null;
const labelStatus={not_ingested:'Not ingested',ingested:'Ingested',unavailable:'Unavailable',requires_license:'License required',error:'Ingestion error'};
function renderVariant(){
 const output=document.getElementById('vwf-multisource-variant');if(!output||!snapshot)return;
 const v=String(document.getElementById('vrvariant')?.value||document.getElementById('variant')?.value||'').trim().toUpperCase();
 if(!/^[A-Z][0-9]+[A-Z]$/.test(v)){output.innerHTML='<p style="color:#c6d8e4">Select a VWF substitution to inspect linked genetic records.</p>';return;}
 const aa={Ala:'A',Arg:'R',Asn:'N',Asp:'D',Cys:'C',Gln:'Q',Glu:'E',Gly:'G',His:'H',Ile:'I',Leu:'L',Lys:'K',Met:'M',Phe:'F',Pro:'P',Ser:'S',Thr:'T',Trp:'W',Tyr:'Y',Val:'V'};
 const normalizeProtein=value=>{
   const raw=String(value||'').replace(/^p\./i,'');
   const m=raw.match(/^([A-Za-z]{3})(\d+)([A-Za-z]{3})$/);
   return m?(aa[m[1]]||'?')+m[2]+(aa[m[3]]||'?'):raw.toUpperCase();
 };
 const alleleIds=new Set(snapshot.alleles.filter(a=>(a.protein_effects||[]).some(p=>normalizeProtein(p.protein_hgvs)===v)).map(a=>a.allele_id));
 const assertions=snapshot.assertions.filter(a=>alleleIds.has(a.allele_id));
 const verified=assertions.filter(a=>a.provenance?.review_status==='verified_primary_source' && a.evidence_type!=='source_record');
 const provisional=assertions.filter(a=>!verified.includes(a));
 output.innerHTML='<h3 style="color:#b8f2e7">Database evidence for '+escapeHTML(v)+'</h3>'+
 (assertions.length?'<p style="color:#f4d6a0">'+provisional.length+' provisional record(s); '+verified.length+' independently verified evidence assertion(s). Provisional records are not verified clinical evidence.</p><ul>'+assertions.map(a=>'<li><strong>'+escapeHTML(a.predicate)+'</strong>: '+escapeHTML(a.value)+' · <a style="color:#8ee8da" target="_blank" rel="noopener noreferrer" href="'+escapeHTML(a.provenance.source_url)+'">'+escapeHTML(a.provenance.source)+' '+escapeHTML(a.provenance.source_record_id)+'</a> · '+escapeHTML(a.provenance.review_status||'Not independently adjudicated')+'</li>').join('')+'</ul>':
 '<p>No normalized external database assertions have been ingested for this substitution. This is <strong>not evidence that the variant is absent from those databases</strong>. Existing literature and structural evidence are shown separately.</p>');
}
fetch('./data/multisource-evidence.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()}).then(data=>{
 if(data.schema_version!=='vwf-multisource-evidence/0.1'||!Array.isArray(data.sources)||!Array.isArray(data.alleles)||!Array.isArray(data.assertions))throw Error('Invalid source snapshot');
 snapshot=data;
 const ingested=data.sources.filter(x=>x.status==='ingested').length;
 document.getElementById('vwf-multisource-status').textContent=ingested+' of '+data.sources.length+' registered source types ingested. The existing literature KG is separate from this new registry.';
 document.getElementById('vwf-multisource-sources').innerHTML='<div style="display:flex;flex-wrap:wrap;gap:8px;margin:16px 0">'+data.sources.map(x=>'<span style="padding:6px 10px;border:1px solid #537189;border-radius:20px;font-size:12px">'+escapeHTML(x.source)+' · '+escapeHTML(labelStatus[x.status]||x.status)+'</span>').join('')+'</div>';
 renderVariant();
}).catch(e=>{document.getElementById('vwf-multisource-status').textContent='External evidence snapshot unavailable: '+e.message;});
document.getElementById('vrvariant')?.addEventListener('input',renderVariant);
document.getElementById('vrvariant')?.addEventListener('change',renderVariant);
document.getElementById('vrshow')?.addEventListener('click',renderVariant);
window.addEventListener('vwf-select-variant',renderVariant);
})();
