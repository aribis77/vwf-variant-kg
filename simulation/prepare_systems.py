#!/usr/bin/env python3
"""Diagnostic CHARMM36 preparation; reports are NOT chemical approval."""
import argparse,collections,json,pathlib,traceback,xml.etree.ElementTree as ET
def main():
 from openmm import app
 import openmm
 ap=argparse.ArgumentParser()
 ap.add_argument("--input-dir",default="private_inputs")
 ap.add_argument("--output-dir",default="prep_reports")
 args=ap.parse_args()
 base=pathlib.Path(args.input_dir);out=pathlib.Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
 ff=app.ForceField("charmm36.xml")
 templ=ff._templates.get("HYP")
 if templ is None:raise RuntimeError("No CHARMM36 HYP template")
 parents={}
 for i,j in templ.bonds:
  a,b=templ.atoms[i],templ.atoms[j]
  if a.element.symbol=="H" and b.element.symbol!="H":parents[a.name]=b.name
  if b.element.symbol=="H" and a.element.symbol!="H":parents[b.name]=a.name
 needed={a.name for a in templ.atoms if a.element.symbol=="H"}
 if set(parents)!=needed:raise RuntimeError("HYP hydrogen connectivity incomplete")
 root=ET.Element("Residues");r=ET.SubElement(root,"Residue",name="HYP")
 for name in sorted(parents):ET.SubElement(r,"H",name=name,parent=parents[name])
 path=out/"hyp_hydrogen_definitions.xml";ET.ElementTree(root).write(path,encoding="unicode",xml_declaration=True)
 app.Modeller.loadHydrogenDefinitions(str(path))
 result={"openmm":openmm.__version__,"chemistry_approved":False,"simulation_ready":False,"systems":{}}
 for label in ("WT","H1786D"):
  entry={"status":"BLOCKED"}
  try:
   pdb=app.PDBFile(str(base/(label+".pdb")))
   mod=app.Modeller(pdb.topology,pdb.positions)
   mod.addHydrogens(pH=7.0)
   unmatched=ff.getUnmatchedResidues(mod.topology)
   entry["unmatched"]=[{"chain":r.chain.id,"id":r.id,"name":r.name} for r in unmatched]
   entry["counts"]=dict(collections.Counter(r.name for r in unmatched))
   if unmatched:entry["status"]="BLOCKED_UNMATCHED_RESIDUES"
   else:
    ff.createSystem(mod.topology,nonbondedMethod=app.NoCutoff)
    entry["status"]="UNSOLVATED_NOT_CHEMICALLY_APPROVED"
  except Exception as e:
   entry.update(status="BLOCKED_EXCEPTION",error=str(e),traceback=traceback.format_exc()[-2500:])
  result["systems"][label]=entry
  (out/(label+".json")).write_text(json.dumps(entry,indent=2))
  print(label,entry["status"],flush=True)
 (out/"summary.json").write_text(json.dumps(result,indent=2))
 print("PREPARATION_DIAGNOSTICS_ONLY_NOT_MD_READY")
if __name__=="__main__":main()
