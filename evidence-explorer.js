/* Evidence explorer: descriptive, provenance-preserving views only. */
(()=>{
const root=document.getElementById('kg-evidence-browser');
if(!root||typeof DATA==='undefined')return;
const obs=Array.isArray(DATA.observations)?DATA.observations:[];
const nodes=DATA.nodes||[],edges=DATA.edges||[];
const byId=new Map(nodes.map(n=>[n.node_id,n]));
const variantId=id=>String(id||'').match(/(?:VWF_p|p\.)([ACDEFGHIKLMNPQRSTVWY]\d{1,5}[ACDEFGHIKLMNPQRSTVWY])/i)?.[1]||null;
const safe=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const subtype=id=>{const n=byId.get(id);const label=String(n?.label||id||'');const m=label.match(/(?:type\s*|VWD_Type)(1|2A|2B|2M|2N|3)\b/i);return m?'Type '+m[1].toUpperCase():null};
const clinicalType=o=>{const str=[o.endpoint,o.result,o.unit_or_type].join(' ');const m=str.match(/\b(?:VWD\s*)?type\s*(1|2A|2B|2M|2N|3)\b/i);return m?'Type '+m[1].toUpperCase():null};
const typeRows=[];
for(const e of edges){const a=variantId(e.subject_id),b=variantId(e.object_id);const t=subtype(e.subject_id)||subtype(e.object_id);if(t&&(a||b))typeRows.push({variant:a||b,type:t,source:e.source_id||'',kind:'KG relationship'})}
for(const o of obs){const v=variantId(o.subject_id),t=clinicalType(o);if(v&&t)typeRows.push({variant:v,type:t,source:o.source_url||'',kind:'Observation'})}
const host=document.createElement('section');host.id='kg-phenotype-explorer';host.className='kg-phenotype';root.insertBefore(host,document.getElementById('oevidence-dashboard'));
let tab='phenotype',query='',selectedType='';
const categories=['Collagen I','Collagen II','Collagen III','Collagen IV','Collagen unspecified','FVIII binding','Platelet interaction','Multimerization','Secretion / antigen','Clinical phenotype'];
function category(o){const e=String(o.endpoint||'').toLowerCase();if(/collagen/.test(e)){const m=e.match(/(?:collagen(?:\s+type)?\s*|type\s+)(iv|iii|ii|i)(?![a-z])/i);return m?'Collagen '+m[1].toUpperCase():'Collagen unspecified'}if(/fviii|factor viii|factor 8/.test(e))return 'FVIII binding';if(/platelet|gpib|ristocetin/.test(e))return 'Platelet interaction';if(/multimer/.test(e))return 'Multimerization';if(/antigen|secretion|expression/.test(e))return 'Secretion / antigen';if(/bleed|clinical|phenotype/.test(e))return 'Clinical phenotype';return 'Other'}
function assay(o){const t=String(o.endpoint||'').toLowerCase();if(/vwf.?ag|antigen/.test(t))return 'VWF:Ag';if(/fviii|factor viii/.test(t))return 'FVIII:C / binding';if(/vwf.?cb|collagen/.test(t))return 'VWF:CB / collagen';if(/activity|ristocetin|gpib/.test(t))return 'VWF activity';return null}
function measurement(o){const raw=String(o.result??'').trim(),unit=String(o.unit_or_type||'');if(!/^[-+]?\d+(?:\.\d+)?$/.test(raw))return null;const value=Number(raw);if(!Number.isFinite(value))return null;return {value,unit,assay:assay(o),variant:variantId(o.subject_id),source:o.source_url||'',population:o.population||'',endpoint:o.endpoint||'',id:o.observation_id||''}}
const measures=obs.map(measurement).filter(x=>x&&x.assay);
const isClinical=m=>/patient|human|plasma|clinical/i.test(m.population)&&!/recombinant|construct|mouse/i.test(m.population);
function bars(counts,onclick){const rows=[...counts].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));const max=Math.max(1,...rows.map(x=>x[1]));return rows.length?rows.map(([k,v])=>'<button type="button" class="kgp-bar" data-choice="'+safe(k)+'"><span>'+safe(k)+'</span><span class="kgp-track"><span style="width:'+(100*v/max).toFixed(1)+'%"></span></span><b>'+v+'</b></button>').join(''):'<p class="sub">No matching curated records.</p>'}
function table(headers,rows){return '<div class="kgp-scroll"><table><thead><tr>'+headers.map(x=>'<th>'+safe(x)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+r.map(x=>'<td>'+safe(x)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>'}
function provenance(o){const link=String(o.source_url||'');return /^https:\/\//.test(link)?'<a target="_blank" rel="noopener noreferrer" href="'+safe(link)+'">Source</a>':'No source URL'}
function content(){
const selected=obs.filter(o=>!query||[o.subject_id,o.endpoint,o.result,o.population,o.source_url].some(x=>String(x||'').toLowerCase().includes(query)));
const selectedTypes=typeRows.filter(x=>!query||[x.variant,x.type].some(y=>y.toLowerCase().includes(query))).filter(x=>!selectedType||x.type===selectedType);
if(tab==='phenotype'){
 const c=new Map();for(const r of selectedTypes)c.set(r.type,(c.get(r.type)||0)+1);
 const patient=measures.filter(m=>isClinical(m)&&(!query||[m.variant,m.assay,m.endpoint].some(x=>String(x).toLowerCase().includes(query))));
 return '<div class="kgp-grid"><article><h4>Reported VWD subtype associations</h4>'+bars(c)+'<p class="sub">Counts are KG links and observations, not unique patients or diagnoses.</p></article><article><h4>Patient laboratory levels</h4><p>'+patient.length+' eligible numeric patient measurements found.</p>'+table(['Variant','Assay','Value','Units','Population'],patient.slice(0,30).map(m=>[m.variant||'Not linked',m.assay,m.value,m.unit,m.population]))+'<p class="sub">Only explicitly numeric human/patient measurements are displayed. WT-relative recombinant values are excluded. Values are not pooled across incompatible assays or units.</p></article></div>';
}
if(tab==='functional'){
 const vars=[...new Set(selected.map(o=>variantId(o.subject_id)).filter(Boolean))].sort();
 const map=new Map();for(const o of selected){const v=variantId(o.subject_id);if(!v)continue;const key=v+'|'+category(o);if(!map.has(key))map.set(key,[]);map.get(key).push(o)}
 const cols=categories.filter(c=>[...map.keys()].some(k=>k.endsWith('|'+c)));
 const body=vars.slice(0,35).map(v=>'<tr><th>'+safe(v)+'</th>'+cols.map(c=>{const records=map.get(v+'|'+c)||[];return '<td class="kgp-heat '+(records.length?'kgp-present':'')+'" title="'+safe(records.map(x=>x.observation_id).join(', '))+'">'+(records.length?records.length:'·')+'</td>'}).join('')+'</tr>').join('');
 return '<h4>Variant × functional evidence matrix</h4><p class="sub">Numbers indicate linked observations, not whether a function is impaired. No effect is inferred from missing or qualitative records.</p><div class="kgp-scroll"><table><thead><tr><th>Variant</th>'+cols.map(c=>'<th>'+safe(c)+'</th>').join('')+'</tr></thead><tbody>'+body+'</tbody></table></div>';
}
if(tab==='literature'){
 const pubs=new Map();for(const o of selected){const url=String(o.source_url||'').trim();if(!url)continue;let key=url;try{const u=new URL(url);key=u.hostname+u.pathname.replace(/\/$/,'')}catch{}if(!pubs.has(key))pubs.set(key,{url,records:0,variants:new Set()});const p=pubs.get(key);p.records++;if(variantId(o.subject_id))p.variants.add(variantId(o.subject_id))}
 return '<h4>Evidence sources and repeated hits</h4><p>'+pubs.size+' source URL identifiers among '+selected.length+' observations.</p>'+table(['Source','Observation hits','Linked variants'],[...pubs].sort((a,b)=>b[1].records-a[1].records).slice(0,35).map(([key,p])=>[key,p.records,p.variants.size]))+'<p class="sub">Publication years and study independence are not inferred from URLs. A source with many observations is not necessarily stronger evidence.</p>';
}
 const selectedVariant=query.toUpperCase().match(/[ACDEFGHIKLMNPQRSTVWY]\d{1,5}[ACDEFGHIKLMNPQRSTVWY]/)?.[0];
 const related=selectedVariant?edges.filter(e=>[e.subject_id,e.object_id].some(id=>variantId(id)===selectedVariant)):[];
 return '<h4>Genotype–phenotype links</h4><p>Search a variant above to inspect KG-linked relations. These are reported associations, not a deterministic clinical prediction.</p>'+table(['Variant','Relationship','Connected entity'],related.slice(0,45).map(e=>[selectedVariant,e.predicate,byId.get(variantId(e.subject_id)===selectedVariant?e.object_id:e.subject_id)?.label||'Unresolved']))+'<p class="sub">Structural modeling is excluded from this explorer.</p>';
}
function render(){
 host.innerHTML='<div class="kgp-heading"><div><h3>Genotype–phenotype evidence explorer</h3><p class="sub">Clinical subtypes, laboratory levels, functional evidence and literature coverage from the existing KG.</p></div><input id="kgp-search" placeholder="Search variant, assay, subtype…" value="'+safe(query)+'" aria-label="Filter phenotype explorer"/></div><div class="kgp-tabs">'+[['phenotype','VWD type & levels'],['functional','Functional heatmap'],['literature','Literature sources'],['network','Genotype–phenotype']].map(([id,label])=>'<button type="button" data-tab="'+id+'" aria-pressed="'+(tab===id)+'">'+label+'</button>').join('')+'</div><div id="kgp-content">'+content()+'</div><p class="kgp-note">Research-only descriptive views. VWD subtype requires clinical and laboratory assessment; genotype alone is insufficient. Unreviewed source records are not independently verified.</p>';
 host.querySelector('#kgp-search').addEventListener('input',e=>{query=e.target.value.trim().toLowerCase();const selection=e.target.selectionStart;host.querySelector('#kgp-content').innerHTML=content();host.querySelectorAll('.kgp-bar').forEach(b=>b.onclick=()=>{selectedType=selectedType===b.dataset.choice?'':b.dataset.choice;render()})});
 host.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{tab=b.dataset.tab;selectedType='';render()});
 host.querySelectorAll('.kgp-bar').forEach(b=>b.onclick=()=>{selectedType=selectedType===b.dataset.choice?'':b.dataset.choice;render()});
}
render();
})();