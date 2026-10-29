"""Reproducible VWF residue-contact analysis. Standard-library only.

Requires an experimentally determined PDB coordinate file and a VERIFIED
author-chain/author-residue mapping. Never equates a residue substitution with
a modeled mutant; no free energies or pathogenicity are inferred.
"""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

AA3 = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLU":"E","GLN":"Q","GLY":"G","HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}

def atoms_from_pdb(path):
    residues = defaultdict(list)
    names = {}
    for line in Path(path).read_text().splitlines():
        if not line.startswith("ATOM  ") or len(line) < 54:
            continue
        if line[16] not in (" ", "A") or line[76:78].strip().upper() in ("H","D"):
            continue
        try:
            xyz = tuple(float(line[i:i+8]) for i in (30,38,46))
            key = (line[21], int(line[22:26]), line[26].strip())
        except ValueError:
            continue
        if line[12:16].strip().startswith("H"):
            continue
        residues[key].append((line[12:16].strip(),xyz))
        names[key] = line[17:20].strip()
    return residues,names

def distances(a,b,cutoff):
    c2=cutoff*cutoff
    return [(x[0],y[0],round(math.sqrt(sum((p-q)**2 for p,q in zip(x[1],y[1]))),3))
            for x in a for y in b if sum((p-q)**2 for p,q in zip(x[1],y[1])) <= c2]

def analyse(path,chain,position,wt,mut,cutoff=4.5,insertion=""):
    residues,names=atoms_from_pdb(path)
    site=(chain,position,insertion)
    if site not in residues:
        raise ValueError(f"Unresolved author residue {chain}:{position}{insertion}")
    observed=AA3.get(names[site])
    if observed != wt:
        raise ValueError(f"Wild-type mismatch at {chain}:{position}: expected {wt}, coordinates contain {names[site]} ({observed})")
    partners=[]
    for key,atoms in residues.items():
        if key==site:continue
        hits=distances(residues[site],atoms,cutoff)
        if hits:
            partners.append({"chain":key[0],"author_residue":key[1],"insertion_code":key[2],
                             "residue":AA3.get(names[key],names[key]),"atom_pairs":len(hits),
                             "minimum_distance_angstrom":min(h[2] for h in hits),
                             "inter_chain":key[0]!=chain})
    partners.sort(key=lambda x:(not x["inter_chain"],x["minimum_distance_angstrom"],x["chain"],x["author_residue"]))
    return {"schema":"vwf-structural-analysis/1.0","mutation":f"{wt}{position}{mut}",
            "structure":Path(path).name,"site":{"chain":chain,"author_residue":position,"insertion_code":insertion,"wild_type_verified":True},
            "cutoff_angstrom":cutoff,"wild_type_contacts":{"partner_residues":partners,
            "partner_count":len(partners),"interchain_partner_count":sum(p["inter_chain"] for p in partners),
            "atom_pair_count":sum(p["atom_pairs"] for p in partners)},
            "mutant_contacts":None,"delta_contacts":None,"energetics":None,"conservation":None,
            "interpretation":"Verified WT structural environment only. Mutation effects cannot be inferred without a separately modeled and validated mutant; no free-energy or clinical pathogenicity conclusion.",
            "status":"wild_type_environment_measured"}

def compare_models(wild_type_path, mutant_path, chain, position, wt, mut, cutoff=4.5, insertion=""):
    """Compare two independently provided coordinate models; never invent mutant atoms.

    WT and mutant must both resolve the requested author-chain and author-residue.
    This is a geometric comparison, not a thermodynamic free-energy calculation.
    """
    wild=analyse(wild_type_path,chain,position,wt,mut,cutoff,insertion)
    residues,names=atoms_from_pdb(mutant_path)
    site=(chain,position,insertion)
    if site not in residues:
        raise ValueError("Mutant coordinate model is missing the requested site")
    if AA3.get(names[site])!=mut:
        raise ValueError(f"Mutant coordinate mismatch: expected {mut}, found {names[site]}")
    partners=[]
    for key,atoms in residues.items():
        if key==site:continue
        hits=distances(residues[site],atoms,cutoff)
        if hits:
            partners.append({"chain":key[0],"author_residue":key[1],"insertion_code":key[2],
                             "residue":AA3.get(names[key],names[key]),"atom_pairs":len(hits),
                             "minimum_distance_angstrom":min(h[2] for h in hits),
                             "inter_chain":key[0]!=chain})
    partners.sort(key=lambda x:(not x["inter_chain"],x["minimum_distance_angstrom"],x["chain"],x["author_residue"]))
    old=wild["wild_type_contacts"]["partner_residues"]
    key=lambda p:(p["chain"],p["author_residue"],p["insertion_code"])
    before={key(p):p for p in old}
    after={key(p):p for p in partners}
    wild["mutant_structure"]=Path(mutant_path).name
    wild["mutant_contacts"]={"partner_residues":partners,"partner_count":len(partners),
                             "interchain_partner_count":sum(p["inter_chain"] for p in partners),
                             "atom_pair_count":sum(p["atom_pairs"] for p in partners)}
    wild["delta_contacts"]={"lost_partner_residues":[before[k] for k in before.keys()-after.keys()],
                            "gained_partner_residues":[after[k] for k in after.keys()-before.keys()],
                            "retained_partner_count":len(before.keys()&after.keys()),
                            "delta_atom_pairs":wild["mutant_contacts"]["atom_pair_count"]-wild["wild_type_contacts"]["atom_pair_count"]}
    wild["status"]="coordinate_models_compared"
    wild["interpretation"]="Measured geometric differences between supplied WT and mutant coordinate models. Model quality and side-chain rotamers affect results. No binding free energy or clinical classification calculated."
    return wild

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pdb",required=True)
    p.add_argument("--chain",required=True)
    p.add_argument("--position",type=int,required=True)
    p.add_argument("--wt",required=True)
    p.add_argument("--mut",required=True)
    p.add_argument("--cutoff",type=float,default=4.5)
    p.add_argument("--insertion",default="")
    p.add_argument("--output")
    p.add_argument("--mutant-pdb",help="Optional independently generated mutant PDB with verified substitution")
    a=p.parse_args()
    if a.mutant_pdb:
        result=compare_models(a.pdb,a.mutant_pdb,a.chain,a.position,a.wt.upper(),a.mut.upper(),a.cutoff,a.insertion)
    else:
        result=analyse(a.pdb,a.chain,a.position,a.wt.upper(),a.mut.upper(),a.cutoff,a.insertion)
    output=json.dumps(result,indent=2)
    if a.output:Path(a.output).write_text(output+"\n")
    else:print(output)

if __name__=="__main__":main()
