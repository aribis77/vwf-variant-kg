import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const scripts=[...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)]
 .filter(m=>!m[1].includes('src=')&&!/type\s*=\s*["'](?:application\/json|importmap)/i.test(m[1]));
if(!scripts.length)throw new Error('No inline scripts found');
let count=0;
for(const [,attrs,source] of scripts){
 if(!source.trim())continue;
 if(/type\s*=\s*["']module/i.test(attrs)){
  if(typeof vm.SourceTextModule==='function')new vm.SourceTextModule(source);
  else {
   const {spawnSync}=await import('node:child_process');
   const result=spawnSync(process.execPath,['--check','--input-type=module'],{input:source,encoding:'utf8'});
   if(result.status!==0)throw new Error(result.stderr);
  }
 }else new vm.Script(source,{filename:'index.html inline script '+(++count)});
}
console.log('Validated '+scripts.length+' inline scripts');
