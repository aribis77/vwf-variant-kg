/* Evidence atlas: interactive descriptive KG views, no imputed clinical values. */
(()=>{
const root=document.getElementById('kg-evidence-browser');
if(!root||typeof DATA==='undefined')return;
const observations=Array.isArray(DATA.observations)?DATA.observations:[];
const nodes=DATA.nodes||[],edges=DATA.edges||[];
const nmap=new Map(nodes.map(n=>[n.node_id,n]));
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const variant=id=>String(id||'').match(/(?:VWF_p|p\.)([ACDEFGHIKLMNPQRSTVWY]\d{1,5}[ACDEFGHIKLMNPQRSTVWY])/i)?.[1]?.toUpperCase()||null;
const getType=id=>{const t=String(nmap.get(id)?.label||id||'');const m=t.match(/(?:VWD_Type|type\s*)(1|2A|2B|2M|2N|3)\b/i);return m?'Type '+m[1].toUpperCase():null};
const allVariants=[...new Set([...nodes.map(n=>variant(n.node_id)),...observations.map(o=>variant(o.subject_id))].filter(Boolean))].sort();
const src=o=>String(o.source_url||'');
const link=o=>/^https:\/\//.test(src(o))?'<a href="'+esc(src(o))+'" target="_blank" rel="noopener noreferrer">Source</a>':'Source not linked';
const sourceKey=o=>{try{const u=new URL(src(o));return u.hostname+u.pathname.replace(/\/$/,'')}catch{return src(o)||'Unlinked'}};
const status=o=>String(o.source_audit_status||'not recorded');
const cat=o=>{const e=String(o.endpoint||'').toLowerCase();if(/collagen/.test(e)){const m=e.match(/(?:collagen(?:\s+type)?\s*|type\s+)(iv|iii|ii|i)(?![a-z])/i);return m?'Collagen '+m[1].toUpperCase():'Collagen unspecified'}if(/fviii|factor viii/.test(e))return 'FVIII';if(/platelet|gpib|ristocetin/.test(e))return 'Platelet';if(/multimer/.test(e))return 'Multimers';if(/secretion|expression|antigen/.test(e))return 'Secretion / antigen';if(/bleed|phenotype|clinical/.test(e))return 'Clinical';return 'Other'};
const numeric=o=>{const v=String(o.result||'').trim();if(!/^\d+(?:\.\d+)?$/.test(v))return null;return Number(v)};
const clinical=o=>/human|patient|plasma|clinical/i.test(String(o.population||''))&&!/mouse|recombinant|construct/i.test(String(o.population||''));
const assays=[['VWF:Ag',/vwf.?ag|antigen/i],['FVIII:C',/fviii.?c|factor viii activity/i],['VWF activity',/vwf.?act|ristocetin|gpib/i],['VWF:CB',/vwf.?cb|collagen binding/i]];
const measure=o=>{if(!clinical(o)||numeric(o)===null)return null;const a=assays.find(x=>x[1].test(o.endpoint||''));if(!a)return null;const unit=String(o.unit_or_type||'');if(/% of wt|relative|fold|pooled/i.test(unit))return null;return {o,value:numeric(o),assay:a[0],unit,variant:variant(o.subject_id)}};
const measured=observations.map(measure).filter(Boolean);
const domains=[['D1',1,741],['D2',742,1241],["D′",1242,1268],['D3',1269,1493],['A1',1494,1672],['A2',1673,1874],['A3',1875,2055],['D4',2056,2296],['C1–C6',2297,2722],['CK',2723,2813]];
const domain=v=>{const n=Number(v?.match(/\d+/)?.[0]);return domains.find(d=>n>=d[1]&&n<=d[2])?.[0]||'Unmapped'};
const subtypeRecords=[];
for(const e of edges){const v=variant(e.subject_id)||variant(e.object_id),t=getType(e.subject_id)||getType(e.object_id);if(v&&t)subtypeRecords.push({v,t,source:e.source_id||'',record:null})}
for(const o of observations){const v=variant(o.subject_id),m=[o.endpoint,o.result].join(' ').match(/\b(?:VWD\s*)?type\s*(1|2A|2B|2M|2N|3)\b/i);if(v&&m)subtypeRecords.push({v,t:'Type '+m[1].toUpperCase(),source:src(o),record:o})}
const panel=document.createElement('section');panel.id='kg-visual-atlas';panel.className='kg-atlas';root.parentNode.insertBefore(panel,root.nextSibling);
let tab='overview',selected=[],focus='',domainFilter='',filter='',onlyReviewed=false;
const types=['Type 1','Type 2A','Type 2B','Type 2M','Type 2N','Type 3'];
const patterns=[['Type 1','Reduced','Usually proportional','Generally preserved','Quantitative reduction'],['Type 2A','Variable','Often disproportionately low','HMW reduced','Qualitative multimer defect'],['Type 2B','Variable','Often disproportionately low','HMW often reduced','Increased GPIb affinity'],['Type 2M','Variable','Often disproportionately low','Generally preserved','Binding dysfunction'],['Type 2N','Variable','Often preserved','Generally preserved','Reduced FVIII binding'],['Type 3','Very low / absent','Often not calculable','Absent / nearly absent','Severe quantitative deficiency']];
const validObs=()=>observations.filter(o=>(!onlyReviewed||/reviewed|verified|audited/i.test(status(o))&&!/not_|unreviewed|not yet/i.test(status(o)))&&(!filter||[o.subject_id,o.endpoint,o.result,o.population].some(x=>String(x||'').toLowerCase().includes(filter))));
const rows=(heads,body)=>'<div class="kga-scroll"><table><thead><tr>'+heads.map(h=>'<th>'+esc(h)+'</th>').join('')+'</tr></thead><tbody>'+body.map(r=>'<tr>'+r.map(c=>'<td>'+c+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';
const detail=o=>'<details class="kga-record"><summary>'+esc(variant(o.subject_id)||o.subject_id)+' · '+esc(o.endpoint)+' · '+esc(o.result)+'</summary><p>Population: '+esc(o.population||'not reported')+' · Unit: '+esc(o.unit_or_type||'not reported')+'</p><p>Audit: '+esc(status(o))+' · Record: '+esc(o.observation_id||'unidentified')+'</p><p>'+esc(o.limitations||'No limitations supplied')+'</p>'+link(o)+'</details>';
const recordList=items=>'<div class="kga-records">'+(items.length?items.slice(0,100).map(detail).join(''):'<p class="sub">No matching observation records.</p>')+'</div>';
const plot=(items,max=12)=>{const sorted=[...items].sort((a,b)=>b[1]-a[1]).slice(0,max),peak=Math.max(1,...sorted.map(x=>x[1]));return sorted.map(([name,count])=>'<div class="kga-bar"><span>'+esc(name)+'</span><div><i style="width:'+(count/peak*100).toFixed(1)+'%"></i></div><b>'+count+'</b></div>').join('')||'<p class="sub">No records.</p>'};

// Cohort summaries are not individual patient observations.
const cohort=o=>/cohort|pooled|combined|median|comparison group/i.test([o.subject_id,o.population,o.unit_or_type].join(' '));
const clinicalAssay=o=>/^(VWF:Ag|FVIII:C|VWF:GPIbR\/VWF:Ag|VWF:CB\/VWF:Ag|VWF:RCo\/VWF:Ag|VWF:GPIbR|VWF:CB|VWF:RCo|Bleeding score|Clinical bleeding score)$/i.test(String(o.endpoint||'').trim());
const cohortAssays=o=>validObs().filter(r=>cohort(r)&&clinicalAssay(r)&&/^\d+(?:\.\d+)?$/.test(String(r.result||'').trim()));
const cohortLabel=o=>{const n=nmap.get(o.subject_id);return n?.label||String(o.subject_id).replaceAll('_',' ')};
const typeFiltered=()=>{
 const allowed=new Set(validObs().map(o=>o.observation_id));
 const term=filter;
 return subtypeRecords.filter(r=>(!onlyReviewed||(r.record&&allowed.has(r.record.observation_id)))&&(!term||[r.v,r.t,r.source].some(x=>String(x||'').toLowerCase().includes(term))||(r.record&&allowed.has(r.record.observation_id))));
};
const effect=o=>{
 const result=String(o.result||'').trim().toLowerCase(),unit=String(o.unit_or_type||'').toLowerCase(),ep=String(o.endpoint||'').toLowerCase();
 if(/pooled|range across|not individually|combined mutants/i.test([unit,o.limitations,o.population].join(' ')))return 'pooled';
 if(/reduced|decreased|diminished|loss|deficient|absent|low|impaired/.test(result))return 'reduced';
 if(/normal|preserved|unchanged|wild.?type.?like|no difference/.test(result))return 'preserved';
 if(/increased|enhanced|elevated|gain/.test(result))return 'increased';
 const val=numeric(o);
 if(val!==null&&/% of wt|% of wild.?type/i.test(unit)&&!/median|cohort|patient/i.test([unit,o.population].join(' '))){
   if(val<80)return 'reduced';if(val>120)return 'increased';return 'preserved';
 }
 return 'unclassified';
};
const effectSummary=rs=>{
 const labels=[...new Set(rs.map(effect).filter(x=>x!=='unclassified'&&x!=='pooled'))];
 return labels.length>1?'conflicting':labels[0]||'unclassified';
};
function overview(){
 const o=validObs(),vs=[...new Set(o.map(x=>variant(x.subject_id)).filter(Boolean))],sources=new Set(o.map(sourceKey).filter(x=>x!=='Unlinked'));
 const subCounts=types.map(t=>[t,new Set(typeFiltered().filter(r=>r.t===t).map(r=>r.v)).size]);
 const assays=new Map();for(const r of o)assays.set(cat(r),(assays.get(cat(r))||0)+1);
 return '<div class="kga-metrics">'+[['Variant identifiers',vs.length],['Observation hits',o.length],['Source identifiers',sources.size],['Numeric patient assay records',measured.filter(m=>o.includes(m.o)).length]].map(([k,v])=>'<div><b>'+v+'</b><span>'+esc(k)+'</span></div>').join('')+'</div><div class="kga-grid"><article><h4>VWD subtype associations</h4>'+plot(subCounts)+'<p class="sub">Unique linked variants, not patients. KG classifications are not re-diagnosed.</p></article><article><h4>Functional observation coverage</h4>'+plot(assays)+'<p class="sub">Hits count observations, not independent experiments.</p></article></div><h4>VWD diagnostic reference fingerprints</h4>'+rows(['Subtype','VWF:Ag','Activity/Ag','Multimers','Characteristic'],patterns.map(r=>r.map(esc)))+'<p class="sub">Educational patterns, not diagnostic rules or conclusions about a selected variant. Activity/antigen ratio often uses 0.7 as an interpretive threshold, depending on assay and guidance.</p>';
}
function phenotype(){
 const o=validObs(),ms=measured.filter(m=>o.includes(m.o)),coh=cohortAssays();
 const typesMap=new Map(types.map(t=>[t,typeFiltered().filter(r=>r.t===t)]));
 const table=rows(['Subtype','Variant associations','Evidence links'],[...typesMap].map(([t,r])=>[esc(t),String(new Set(r.map(x=>x.v)).size),String(r.length)]));
 const groups=new Map();
 for(const r of coh){const key=cohortLabel(r);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(r)}
 const priority=['VWF:Ag','FVIII:C','VWF:GPIbR/VWF:Ag','VWF:CB/VWF:Ag','VWF:RCo/VWF:Ag','Bleeding score'];
 const cohortRows=[...groups].map(([label,rs])=>[esc(label),...priority.map(ep=>{const match=rs.filter(r=>r.endpoint.toLowerCase()===ep.toLowerCase());return match.length?match.map(r=>'<details><summary>'+esc(r.result)+' '+esc(r.unit_or_type)+'</summary>'+link(r)+' · '+esc(status(r))+'<p>'+esc(r.population)+'</p></details>').join(''):'<span class="sub">Not indexed</span>'})]);
 return '<h4>Reported VWD subtype associations</h4>'+table+
 '<h4>Clinical cohort laboratory profiles</h4><p class="sub">Published summary measurements, usually medians. Each value retains its own cohort and source; these are not individual patient results and cannot be combined to infer patient-level correlations.</p>'+
 rows(['Cohort / group',...priority],cohortRows)+
 '<h4>Variant-associated laboratory observations</h4>'+rows(['Variant','Assay','Reported value','Population','Source / audit'],o.filter(r=>variant(r.subject_id)&&clinicalAssay(r)).slice(0,80).map(r=>[esc(variant(r.subject_id)),esc(r.endpoint),esc(r.result+' '+r.unit_or_type),esc(r.population),link(r)+' · '+esc(status(r))]))+
 '<h4>Individual-level activity versus antigen</h4><p class="sub">A patient-level scatter plot requires paired VWF:Ag and activity measurements from the same individual, with assay method and units. The present records do not establish that pairing; no scatter plot is generated.</p>'+
 '<p class="sub">'+ms.length+' numeric observations pass the broad patient-context screen, but may include summary statistics. They are not automatically treated as independent patient measurements.</p>';
}
function heatmap(){
 const o=validObs(),vs=[...new Set(o.map(x=>variant(x.subject_id)).filter(Boolean))].sort(),cats=['Collagen I','Collagen II','Collagen III','Collagen IV','Collagen unspecified','FVIII','Platelet','Multimers','Secretion / antigen','Clinical'];
 const grouped=new Map();for(const r of o){const v=variant(r.subject_id);if(!v)continue;const key=v+'|'+cat(r);if(!grouped.has(key))grouped.set(key,[]);grouped.get(key).push(r)}
 const shown=vs.slice(0,65);
 return '<h4>Functional effect and evidence matrix</h4><p class="sub">Colors indicate reported direction only where the observation supports interpretation. Unclassified and pooled results are not treated as normal. Conflicting means distinct reported directions, not necessarily independent replication.</p>'+
 '<div class="kga-legend"><span class="kga-reduced">Reduced</span><span class="kga-preserved">Preserved</span><span class="kga-increased">Increased</span><span class="kga-conflicting">Conflicting</span><span class="kga-unclassified">Unclassified</span><span>No record ·</span></div>'+
 '<div class="kga-scroll"><table><thead><tr><th>Variant</th>'+cats.map(c=>'<th>'+esc(c)+'</th>').join('')+'</tr></thead><tbody>'+shown.map(v=>'<tr><th>'+v+'</th>'+cats.map(c=>{const rr=grouped.get(v+'|'+c)||[];const state=rr.length?effectSummary(rr):'';return '<td class="'+(state?'kga-effect kga-'+state:'')+'" title="'+esc(rr.map(x=>x.observation_id+': '+x.result+' '+x.unit_or_type).join(' | '))+'">'+(rr.length?esc(state)+' ('+rr.length+')':'·')+'</td>'}).join('')+'</tr>').join('')+'</tbody></table></div>'+
 '<h4>Supporting assay records</h4>'+recordList(o.filter(r=>variant(r.subject_id)&&cats.includes(cat(r))));
}
function domainsView(){
 const o=validObs(),counts=new Map();for(const r of o){const v=variant(r.subject_id);if(v){const d=domain(v);if(!counts.has(d))counts.set(d,new Set());counts.get(d).add(v)}}
 const vals=domains.map(d=>[d[0],counts.get(d[0])?.size||0]);
 const subset=o.filter(r=>!domainFilter||domain(variant(r.subject_id))===domainFilter);
 return '<h4>VWF domain–phenotype map</h4><p class="sub">Domain boundaries are approximate VWF precursor-sequence position annotations for exploration and must be verified against a canonical domain reference before biological interpretation. Counts use distinct variant identifiers.</p><div class="kga-domainmap">'+domains.map(d=>'<button type="button" data-domain="'+esc(d[0])+'" class="'+(domainFilter===d[0]?'active':'')+'" title="Residues '+d[1]+'–'+d[2]+'">'+esc(d[0])+'<small>'+d[1]+'–'+d[2]+'</small></button>').join('')+'</div>'+plot(vals)+'<h4>'+(domainFilter?esc(domainFilter)+' domain':'All domains')+' evidence</h4>'+recordList(subset);
}
function comparison(){
 const o=validObs();
 const opts=allVariants.filter(v=>!filter||v.toLowerCase().includes(filter)).slice(0,100);
 const select='<div class="kga-choices">'+opts.map(v=>'<button type="button" data-variant="'+v+'" class="'+(selected.includes(v)?'active':'')+'">'+v+'</button>').join('')+'</div>';
 const cats=['Collagen I','Collagen III','Collagen IV','FVIII','Platelet','Multimers','Secretion / antigen','Clinical'];
 const lines=[['Reported VWD type',...selected.map(v=>[...new Set(subtypeRecords.filter(r=>r.v===v).map(r=>r.t))].join(', ')||'Not reported')],...cats.map(c=>[c,...selected.map(v=>o.filter(r=>variant(r.subject_id)===v&&cat(r)===c).length+' hit(s)')]),['Distinct source identifiers',...selected.map(v=>new Set(o.filter(r=>variant(r.subject_id)===v).map(sourceKey)).size)],['Patient numeric assays',...selected.map(v=>measured.filter(m=>m.variant===v&&o.includes(m.o)).length)]];
 return '<h4>Compare up to four variants</h4><p class="sub">Select variants to compare reported subtype links and evidence coverage. Counts are not effect magnitudes.</p>'+select+(selected.length?rows(['Measure',...selected],lines.map(r=>r.map(esc))):'<p>Select at least one variant.</p>')+'<h4>Supporting observations</h4>'+recordList(o.filter(r=>selected.includes(variant(r.subject_id))));
}
function studies(){
 const o=validObs(),grouped=new Map();for(const r of o){const k=sourceKey(r);if(!grouped.has(k))grouped.set(k,[]);grouped.get(k).push(r)}
 const rank=[...grouped].sort((a,b)=>b[1].length-a[1].length);
 return '<h4>Publication and source agreement audit</h4><p class="sub">Records are grouped by source identifier. The source count is not a count of independent experiments. Effect agreement requires assay-specific normalization and manual review.</p>'+rows(['Source identifier','Hits','Variants','Audit statuses'],rank.slice(0,60).map(([k,rs])=>[esc(k),String(rs.length),String(new Set(rs.map(x=>variant(x.subject_id)).filter(Boolean)).size),esc([...new Set(rs.map(status))].join(', '))]))+'<h4>Evidence records and provenance</h4>'+recordList(o);
}
function gaps(){
 const o=validObs(),vs=[...new Set(o.map(x=>variant(x.subject_id)).filter(Boolean))].sort(),cats=['Clinical','Secretion / antigen','Collagen I','Collagen III','FVIII','Platelet','Multimers'];
 const coverage=cats.map(c=>[c,vs.filter(v=>o.some(r=>variant(r.subject_id)===v&&cat(r)===c)).length,vs.length]);
 const missing=vs.map(v=>({v,n:cats.filter(c=>!o.some(r=>variant(r.subject_id)===v&&cat(r)===c)).length})).sort((a,b)=>b.n-a.n).slice(0,30);
 return '<h4>Knowledge gaps and assay coverage</h4><p class="sub">Missing means no indexed observation in this KG, not proof that an experiment was never performed.</p>'+rows(['Evidence category','Variants with records','Coverage of indexed variants'],coverage.map(([c,n,total])=>[esc(c),String(n),total?(100*n/total).toFixed(1)+'%':'N/A']))+'<h4>Variants with the most missing categories</h4>'+rows(['Variant','Categories without indexed observations'],missing.map(x=>[esc(x.v),String(x.n)]));
}
function render(){
 const tabs=[['overview','Overview'],['phenotype','VWD type & levels'],['heatmap','Functional heatmap'],['domains','Domain map'],['compare','Compare variants'],['studies','Studies & provenance'],['gaps','Knowledge gaps']];
 const view={overview,phenotype,heatmap,domains:domainsView,compare:comparison,studies,gaps}[tab]();
 panel.innerHTML='<div class="kga-head"><div><h3>VWF evidence atlas</h3><p class="sub">Explore subtype, laboratory, functional and literature evidence with source traceability.</p></div><label><input type="checkbox" id="kga-reviewed" '+(onlyReviewed?'checked':'')+'> Reviewed records only</label></div><div class="kga-controls"><input id="kga-filter" value="'+esc(filter)+'" placeholder="Filter variant, endpoint, observation…" aria-label="Filter atlas"><button type="button" id="kga-reset">Reset</button></div><nav class="kga-tabs" aria-label="Evidence atlas views">'+tabs.map(([id,label])=>'<button type="button" data-tab="'+id+'" aria-pressed="'+(tab===id)+'">'+label+'</button>').join('')+'</nav><div class="kga-body">'+view+'</div><p class="kga-disclaimer">KG evidence demonstrator. No diagnosis, validated pathogenicity score, or causal inference is generated. Source audits and study independence require review.</p>';
 panel.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{tab=b.dataset.tab;render()});
 panel.querySelector('#kga-filter').addEventListener('change',e=>{filter=e.target.value.trim().toLowerCase();render()});
 panel.querySelector('#kga-reviewed').onchange=e=>{onlyReviewed=e.target.checked;render()};
 panel.querySelector('#kga-reset').onclick=()=>{filter='';domainFilter='';onlyReviewed=false;render()};
 panel.querySelectorAll('[data-domain]').forEach(b=>b.onclick=()=>{domainFilter=domainFilter===b.dataset.domain?'':b.dataset.domain;render()});
 panel.querySelectorAll('[data-variant]').forEach(b=>b.onclick=()=>{const v=b.dataset.variant;selected=selected.includes(v)?selected.filter(x=>x!==v):selected.length<4?[...selected,v]:selected;render()});
}
render();
})();