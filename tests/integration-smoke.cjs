const { chromium } = require('playwright');
(async () => {
 const browser = await chromium.launch({headless:true,args:['--no-sandbox']});
 const page = await browser.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const url='https://aribis77.github.io/protein-workbench/?pdb=4DMU&chain=B&mutation=H1786D&analysis=kg_integrated';
 await page.goto(url,{waitUntil:'domcontentloaded',timeout:90000});
 const status=page.locator('#automatic-mechanistic-report');
 const outcome=await Promise.race([
  status.waitFor({state:'visible',timeout:240000}).then(()=>({report:true})).catch(()=>({report:false})),
  page.getByText(/Automatic analysis failed:|Analysis incomplete:/).first().waitFor({state:'visible',timeout:240000}).then(()=>({failure:true})).catch(()=>({failure:false}))
 ]);
 const data=await page.evaluate(()=>({title:document.title,report:document.querySelector('#automatic-mechanistic-report')?.innerText?.slice(0,2500)||null,body:document.body.innerText.slice(-1800)}));
 console.log(JSON.stringify({outcome,errors,data},null,2));
 await browser.close();
 if(!data.report||errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});