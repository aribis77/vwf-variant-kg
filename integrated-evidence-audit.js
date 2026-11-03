(function(){
  'use strict';
  const reportPanel=document.getElementById('variant-report');
  const input=document.getElementById('vrvariant');
  if(!reportPanel||!input)return;
  const section=document.createElement('section');
  section.id='vwf-audited-integration';
  section.setAttribute('aria-live','polite');
  section.innerHTML='<h3>Audited KG + structural evidence</h3><p class="vwf-audit-status">Loading independent evidence audit…</p>';
  reportPanel.append(section);
  let dataset=null,loadFailed=false,token=0;
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt=v=>typeof v==='number'&&Number.isFinite(v)?Number(v.toPrecision(4)).toString():'Not measured';
  const valid=v=>/^[ACDEFGHIKLMNPQRSTVWY][0-9]{1,5}[ACDEFGHIKLMNPQRSTVWY]$/.test(v);
  function render(){
    const variant=input.value.trim().toUpperCase();
    if(!valid(variant)){
      section.querySelector('.vwf-audit-status')?.remove();
      section.innerHTML='<h3>Audited KG + structural evidence</h3><p>Select a valid variant to inspect its evidence audit.</p>';return;
    }
    if(!dataset){
      section.innerHTML='<h3>Audited KG + structural evidence</h3><p>'+(
        loadFailed?'No generated benchmark audit is published yet. This does not mean that the variant has no evidence.':'Loading audited evidence…')+'</p>';
      return;
    }
    const cases=dataset.cases.filter(x=>x.variant===variant);
    if(!cases.length){
      section.innerHTML='<h3>Audited KG + structural evidence</h3><p>This variant is not in the provisional benchmark panel. The main KG report remains available above.</p>';return;
    }
    section.innerHTML='<h3>Audited KG + structural evidence</h3><p class="vwf-audit-caution">Research-only evidence inventory. Reference outcomes are withheld; no validated functional prediction or pathogenicity score is available.</p>'+
    cases.map(c=>{
      const st=c.structural||{},kg=c.kg||{},joined=c.integrated||{};
      const metric=(label,entry)=>'<div class="vwf-audit-metric"><strong>'+label+'</strong><span>'+fmt(entry?.median)+'</span><small>Range: '+fmt(entry?.minimum)+' to '+fmt(entry?.maximum)+'</small></div>';
      const pdbs=(st.per_structure||[]).map(p=>'<tr><td>'+esc(p.pdb_id)+'</td><td>'+fmt(p.contact_change_median)+'</td><td>'+fmt(p.delta_g_kcal_mol_median)+'</td><td>'+fmt(p.conservation_score_median)+'</td></tr>').join('');
      return '<article class="vwf-audit-case"><h4>'+esc(c.endpoint)+'</h4><div class="vwf-audit-grid"><div><strong>KG evidence</strong><p>'+Number(kg.observation_count||0)+' exact-endpoint observations, provisionally URL-filtered</p><small>Independent source adjudication pending</small></div><div><strong>Protein Workbench consensus</strong><p>'+Number(st.distinct_pdb_count||0)+' distinct PDBs; '+Number(st.report_count||0)+' reports</p><small>'+(st.consensus_available?'Descriptive structural evidence':'No imported validated structural reports')+'</small></div></div>'+
      (st.consensus_available?'<div class="vwf-audit-grid">'+metric('Contact change',st.contact_change)+metric('Free energy (kcal/mol)',st.delta_g_kcal_mol)+metric('Conservation',st.conservation_score)+'</div><div class="vwf-audit-table"><table><thead><tr><th>PDB</th><th>Contact Δ</th><th>Free energy</th><th>Conservation</th></tr></thead><tbody>'+pdbs+'</tbody></table></div>':'')+
      '<p class="vwf-audit-caution">Integrated assessment: '+esc(joined.functional_effect_conclusion||'not established')+'. '+esc(joined.reason||'No validated endpoint-specific prediction.')+'</p></article>';
    }).join('');
  }
  async function load(){
    try{
      const response=await fetch('./benchmark/integrated_case_evidence.json',{cache:'no-store'});
      if(!response.ok)throw new Error('not published');
      const value=await response.json();
      if(value.schema!=='vwf-integrated-case-evidence/0.1'||!Array.isArray(value.cases))throw new Error('schema mismatch');
      dataset=value;
    }catch(e){loadFailed=true;}
    render();
  }
  input.addEventListener('input',()=>{const current=++token;setTimeout(()=>{if(current===token)render()},180)});
  input.addEventListener('change',render);
  document.getElementById('vrshow')?.addEventListener('click',render);
  window.addEventListener('vwf-select-variant',()=>setTimeout(render,100));
  load();
})();
