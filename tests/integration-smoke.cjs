const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
(async () => {
 const browser = await chromium.launch({headless:true,args:['--no-sandbox']});
 const context = await browser.newContext();
 const errors=[];const requests=[];
 const kg=await context.newPage();
 kg.on('pageerror',e=>errors.push('KG: '+e.message));
 kg.on('response',r=>{if(r.status()>=400)requests.push('KG '+r.status()+' '+r.url());});
 try {
  await kg.goto('https://aribis77.github.io/vwf-variant-kg/',{waitUntil:'domcontentloaded',timeout:90000});
  await kg.locator('#simple-variant').fill('H1786D');
  const popupPromise=context.waitForEvent('page',{timeout:30000});
  await kg.locator('#simple-run').click();
  const wb=await popupPromise;
  wb.on('pageerror',e=>errors.push('Workbench: '+e.message));
  wb.on('response',r=>{if(r.status()>=400)requests.push('Workbench '+r.status()+' '+r.url());});
  await wb.waitForLoadState('domcontentloaded');
  assert.match(wb.url(),/analysis=kg_integrated/,'The KG must launch integrated analysis');
  await wb.waitForFunction(()=>document.querySelector('#automatic-mechanistic-report')!==null,null,{timeout:240000});
  const report=await wb.evaluate(()=>{
   const raw=localStorage.getItem('vwf-workbench-result-v1');
   return raw?JSON.parse(raw).report:null;
  });
  assert.ok(report,'Workbench must publish a machine-readable result');
  assert.equal(report.schema,'protein-workbench-mechanistic-report/0.1');
  assert.equal(report.mutation,'H1786D');
  assert.equal(report.pdb,'4DMU');
  assert.equal(report.coordinate_mapping?.verified_in_loaded_coordinates,true);
  assert.equal(report.analysis_mode,'kg_integrated');
  for(const key of ['lost','gained','kept'])assert.ok(Number.isFinite(report.metrics?.contacts?.[key]),'Missing contact count: '+key);
  assert.ok(report.metrics?.energetics,'Energetic scoring must be present');
  assert.ok(report.metrics?.conservation,'Conservation must be present');
  assert.equal(report.metrics?.sampling,null,'MD and sampling must not run');
  await kg.waitForFunction(()=>{try{return JSON.parse(localStorage.getItem('vwf-validated-workbench-reports-v1')||'[]').some(r=>r.mutation==='H1786D'&&r.pdb==='4DMU');}catch{return false;}},null,{timeout:30000});
  const state=await kg.evaluate(()=>({storedKeys:Object.keys(localStorage).filter(k=>k.includes('workbench')),body:document.body.innerText.slice(-3000)}));
  assert.ok(state.body.includes('H1786D'),'KG must show selected variant');
  assert.deepEqual(errors,[],'Unexpected browser errors');
  console.log(JSON.stringify({status:'PASS',pdb:report.pdb,mutation:report.mutation,contacts:report.metrics.contacts,energetics:report.metrics.energetics,conservation:report.metrics.conservation,kg:state.storedKeys},null,2));
 } catch(e) {
  console.error('INTEGRATION FAILURE:',e.stack||e);
  console.error('KG URL:',kg.url());
  console.error('BROWSER ERRORS:',JSON.stringify(errors));
  console.error('FAILED REQUESTS:',JSON.stringify(requests));
  fs.mkdirSync('test-results',{recursive:true});
  await kg.screenshot({path:'test-results/kg-failure.png',fullPage:true}).catch(()=>{});
  for(const page of context.pages())if(page!==kg){await page.screenshot({path:'test-results/workbench-failure.png',fullPage:true}).catch(()=>{});fs.writeFileSync('test-results/workbench-text.txt',(await page.locator('body').innerText().catch(()=>'' )).slice(-12000));}
  fs.writeFileSync('test-results/errors.json',JSON.stringify({errors,requests},null,2));
  process.exitCode=1;
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
