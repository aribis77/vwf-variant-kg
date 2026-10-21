"""Synthetic full-sequence topology check; no unpublished coordinates."""
import json
from pathlib import Path
from openmm import app
import openmm
S="CSQPLDVILLLDGSSSFPASYFDEMKSFAKAFISKANIGPRLTQVSVLQYGSITTIDVPWNVVPEKAHLLSLVDVMQREGGPSQIGDALGFAVRYLTSEMHGARPGASKAVVILVTDVSVDSVDAAADAARSNRVTVFPIGIGDRYDAAQLRILAGPAGDSNVVKLQRIEDLPTMVTLGNSFLHKLCS"
C="GPOGPOGPOGPRGQOGVMGFOGPOGPO"
MAP=dict(zip("ACDEFGHIKLMNPQRSTVWYO","ALA CYS ASP GLU PHE GLY HIS ILE LYS LEU MET ASN PRO GLN ARG SER THR VAL TRP TYR HYP".split()))
assert len(S)==188 and S[100]=="H" and len(C)==27
def build(mut):
 ff=app.ForceField("charmm36.xml")
 patch=ff._patches
 base=ff._templates
 cys=patch["DISU"].createPatchedTemplates([base["CYS"],base["CYS"]])[0]
 choices={"first":patch["NTER"].createPatchedTemplates([cys])[0],"other":cys,
          "ser":patch["CTER"].createPatchedTemplates([base["SER"]])[0],
          "gly":patch["GLYP"].createPatchedTemplates([base["GLY"]])[0],
          "hyp":patch["CTER"].createPatchedTemplates([base["HYP"]])[0]}
 for name,tmpl in choices.items():
  if tmpl.name not in [t.name for t in ff._templates.values()]:ff.registerResidueTemplate(tmpl)
 top=app.Topology(); b={}
 for ch,letters in [("B",S if mut=="WT" else S[:100]+"D"+S[101:])]+[(x,C) for x in "XYZ"]:
  chain=top.addChain(ch);entries=[]
  for i,aa in enumerate(letters):
   name="HSE" if aa=="H" else MAP[aa]
   tmpl=(choices["first"] if ch=="B" and i==0 else
     choices["other"] if ch=="B" and i==186 else
     choices["ser"] if ch=="B" and i==187 else
     choices["gly"] if ch!="B" and i==0 else
     choices["hyp"] if ch!="B" and i==26 else base[name])
   residue=top.addResidue(name,chain,id=str(1686+i if ch=="B" else i+1))
   atoms=[top.addAtom(a.name,a.element,residue) for a in tmpl.atoms]
   for p,q in tmpl.bonds:top.addBond(atoms[p],atoms[q])
   d={a.name:atoms[j] for j,a in enumerate(tmpl.atoms)}
   if entries:top.addBond(entries[-1]["C"],d["N"])
   entries.append(d)
  b[ch]=entries
 top.addBond(b["B"][0]["SG"],b["B"][186]["SG"])
 unmatched=ff.getUnmatchedResidues(top)
 ans={"variant":mut,"chains":len(list(top.chains())),"residues":len(list(top.residues())),"atoms":len(list(top.atoms())),"hydroxyprolines":sum(r.name=="HYP" for r in top.residues()),"unmatched":[[r.chain.id,r.id,r.name] for r in unmatched]}
 if not unmatched:
  system=ff.createSystem(top,nonbondedMethod=app.NoCutoff)
  ans["particles"]=system.getNumParticles();ans["status"]="SYNTHETIC_SYSTEM_CONSTRUCTED"
 else:ans["status"]="UNMATCHED"
 return ans
out={"scope":"sequence-only; HSE tautomer assigned provisionally, no real coordinates, solvent or MD","openmm":openmm.__version__,"variants":{}}
for name in ("WT","H1786D"):
 try:out["variants"][name]=build(name)
 except Exception as e:out["variants"][name]={"status":"ERROR","error":str(e)}
Path("simulation/full_sequence_topology_report.json").write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
if any(x.get("status")!="SYNTHETIC_SYSTEM_CONSTRUCTED" for x in out["variants"].values()):raise SystemExit(2)
