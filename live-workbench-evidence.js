/* Live, session-scoped Workbench evidence bridge. No server upload or invented metrics. */
(function(){
'use strict';
const frame=document.getElementById('kg-structural-analysis');
const input=document.getElementById('vrvariant');
const host=document.getElementById('variant-report');
if(!frame||!input||!host)return;
const reports=new Map();
const valid=v=>/^[ACDEFGHIKLMNPQRSTVWY][0-9]{1,5}[ACDEFGHIKLMNPQRSTVWY]$/.test(v);
const num=(o,keys)=>{for(const k of keys)if(typeof o?.[k]==='number'&&Number.isFinite(o[k]))return o[k];return null;};
const measure=(r,paths)=>{for(const path of paths){let x=r;for(const k of path)x=x?.[k];if(x&&typeof x==='object'&&!['unavailable','failed','not_run','pending'].includes(x.status))return x;}return null;};
const median=values=>{if(!values.length)return null;const a=[...values].sort((x,y)=>x-y);return a.length%2?a[(a.length-1)/2]:(a[a.length/2-1]+a[a.length/2])/2;};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>n===null?'Not measured':Number(n.toPrecision(4)).toString();
const section=document.createElement('section');section.id='vwf-live-workbench-evidence';
section.style.cssText='margin:16px;padding:18px;border:1px solid #53798e;border-radius:12px;background:#203b52;color:#e9f4fa';
host.append(section);
function render(){
 const v=input.value.trim().toUpperCase();
 if(!valid(v)){section.innerHTML='<h3>Live Protein Workbench measurements</h3><p>Select a variant to view its current structural reports.</p>';return;}
 const entries=[...(reports.get(v)?.values()||[])],groups=new Map();
 for(const r of entries){const pdb=String(r.pdb||r.structure?.pdb_id||r.coordinate_mapping?.pdb||'').toUpperCase();if(!/^[0-9][A-Z0-9]{3}$/.test(pdb))continue;if(!groups.has(pdb))groups.set(pdb,[]);groups.get(pdb).push(r);}
 const specs=[
 ['Contact change',[['metrics','contacts'],['results','contacts'],['contacts']],['delta_contacts','contact_delta','net_contact_change','delta']],
 ['Energetics (reported units)',[['metrics','energetics'],['results','energetics'],['energetics'],['metrics','energy'],['energy']],['delta_delta_g','ddg','delta_g','delta_energy','energy_delta']],
 ['Conservation',[['metrics','conservation'],['results','conservation'],['conservation']],['score','conservation_score','normalized_score']]
 ];
 const rows=[...groups].map(([pdb,rs])=>({pdb,chains:rs.length,values:specs.map(([_,paths,keys])=>median(rs.map(r=>num(measure(r,paths),keys)).filter(Number.isFinite)))}));
 const summary=specs.map((spec,i)=>({label:spec[0],value:median(rows.map(r=>r.values[i]).filter(Number.isFinite)),count:rows.filter(r=>r.values[i]!==null).length}));
 section.innerHTML='<h3 style="color:#b6e8e2">Live Protein Workbench measurements · '+esc(v)+'</h3>'+
 '<p>'+entries.length+' verified-coordinate chain reports received in this browser session, across '+groups.size+' distinct PDB entries. Per-PDB medians prevent chain-count inflation.</p>'+
 (entries.length?'<div style="display:flex;gap:12px;flex-wrap:wrap">'+summary.map(x=>'<div style="flex:1;min-width:145px;padding:12px;background:#2b5068;border-radius:9px"><strong>'+esc(x.label)+'</strong><div style="font-size:22px">'+fmt(x.value)+'</div><small>'+x.count+' PDB(s) with values</small></div>').join('')+'</div>':'<p>Run structural analysis above to populate this section. No measurements have been received for this variant.</p>')+
 (rows.length?'<div style="overflow-x:auto"><table style="width:100%;margin-top:12px"><thead><tr><th>PDB</th><th>Chains</th>'+specs.map(s=>'<th>'+esc(s[0])+'</th>').join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr><td>'+esc(r.pdb)+'</td><td>'+r.chains+'</td>'+r.values.map(v=>'<td>'+fmt(v)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>':'')+
 '<p style="margin-top:14px;color:#e6cc96">Live session measurements are separate from the published, independently audited benchmark dataset. They are not validated endpoint predictions or a pathogenicity score. Energetic values are not pooled across different methods or units for scientific inference.</p>';
}
window.addEventListener('message',e=>{
 if(e.origin!==location.origin||e.source!==frame.contentWindow||e.data?.type!=='vwf-workbench-report')return;
 const r=e.data.report,v=String(r?.mutation||'').toUpperCase(),m=r?.coordinate_mapping||{};
 if(r?.schema!=='protein-workbench-mechanistic-report/0.1'||!valid(v)||v!==input.value.trim().toUpperCase())return;
 if(m.verified_in_loaded_structure!==true&&m.verified_in_loaded_coordinates!==true)return;
 const pdb=String(r.pdb||r.structure?.pdb_id||m.pdb||'').toUpperCase(),chain=String(r.chain||m.chain||'');
 if(!/^[0-9][A-Z0-9]{3}$/.test(pdb)||!chain)return;
 if(!reports.has(v))reports.set(v,new Map());
 reports.get(v).set(pdb+':'+chain,r);
 render();
});
input.addEventListener('input',render);input.addEventListener('change',render);
window.addEventListener('vwf-select-variant',()=>setTimeout(render,0));
render();
})();
