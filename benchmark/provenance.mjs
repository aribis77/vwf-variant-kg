// Canonical publication IDs for evidence deduplication. No network requests.
export function publicationKey(record={}){
 const doi=String(record.doi||record.publication_doi||'').trim().replace(/^https?:\/\/(?:dx\.)?doi\.org\//i,'').replace(/^doi:\s*/i,'').toLowerCase();
 if(/^10\.\d{4,9}\/\S+$/.test(doi))return 'doi:'+doi;
 const pmid=String(record.pmid||record.pubmed_id||'').trim();
 if(/^\d{5,9}$/.test(pmid))return 'pmid:'+pmid;
 const url=String(record.source_url||record.source||'').trim();
 if(!url)return null;
 try{
  const u=new URL(url);
  const doiUrl=u.pathname.match(/\/(10\.\d{4,9}\/[^?#]+)/i);
  if(doiUrl)return 'doi:'+decodeURIComponent(doiUrl[1]).toLowerCase();
  const pubmed=u.hostname.toLowerCase();
  const pubmedPath=u.pathname.match(/^\/(\d{5,9})\/?$/);
  if((pubmed==='pubmed.ncbi.nlm.nih.gov'||pubmed==='www.ncbi.nlm.nih.gov')&&pubmedPath)return 'pmid:'+pubmedPath[1];
  const pmc=u.pathname.match(/\/articles\/(PMC\d+)/i);
  if(pmc)return 'pmcid:'+pmc[1].toUpperCase();
  return 'url:'+u.hostname.toLowerCase()+u.pathname.replace(/\/$/,'');
 }catch{return null;}
}
export function studyKey(record={}){
 const publication=publicationKey(record);
 if(!publication)return null;
 const explicit=String(record.study_id||record.cohort_id||'').trim();
 // Without an independently curated study identifier, a publication is the unit of evidence,
 // not proof of an independent experimental cohort.
 return explicit?publication+'|study:'+explicit:publication;
}
