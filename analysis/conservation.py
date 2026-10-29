"""Conservation at a verified VWF position from a pre-aligned ortholog FASTA.

No conservation percentage is returned unless the reference is verified and
there are enough independent, non-identical species sequences.
"""
from collections import Counter
from pathlib import Path
import argparse
import json

AMINO=set("ACDEFGHIKLMNPQRSTVWY")

def read_fasta(path):
    records={}
    name=None
    for raw in Path(path).read_text().splitlines():
        line=raw.strip()
        if not line:continue
        if line.startswith(">"):
            name=line[1:].strip()
            if not name or name in records:raise ValueError("Missing or duplicate FASTA identifier")
            records[name]=""
        elif name is None:raise ValueError("Sequence before FASTA identifier")
        else:records[name]+=line.upper()
    if not records:raise ValueError("Empty alignment")
    return records

def assess(records,reference,position,expected="H",minimum_orthologs=5):
    if reference not in records:raise ValueError("Reference sequence not present")
    lengths={len(s) for s in records.values()}
    if len(lengths)!=1:raise ValueError("Input must be an aligned FASTA of equal-length sequences")
    ref=records[reference]
    residues=[i for i,c in enumerate(ref) if c in AMINO]
    if position<1 or position>len(residues):raise ValueError("Reference position out of range")
    col=residues[position-1]
    if ref[col]!=expected:raise ValueError("Reference wild-type residue mismatch")
    # A FASTA identifier is not proof of an independent ortholog. Exclude exact
    # duplicate aligned sequences so redundant records cannot inflate coverage.
    valid={}
    seen_sequences=set()
    for name,seq in records.items():
        if name==reference or seq[col] not in AMINO:continue
        if seq in seen_sequences:continue
        seen_sequences.add(seq)
        valid[name]=seq[col]
    if len(valid)<minimum_orthologs:
        raise ValueError(f"Insufficient ortholog coverage: {len(valid)} of {minimum_orthologs} required")
    counts=Counter(valid.values())
    return {"schema":"vwf-conservation/1.0","reference":reference,"position":position,
            "wild_type":expected,"alignment_column_1based":col+1,
            "ortholog_count":len(valid),"duplicate_sequences_excluded":sum(name!=reference and seq[col] in AMINO for name,seq in records.items())-len(valid),"reference_residue_fraction":round(counts[expected]/len(valid),4),
            "residue_counts":dict(sorted(counts.items())),
            "method":"prealigned ortholog residues, excluding reference, gaps and exact duplicate aligned sequences",
            "caveats":"Requires curated independent ortholog sequences; not a clinical classification"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--alignment",required=True)
    p.add_argument("--reference",required=True)
    p.add_argument("--position",type=int,required=True)
    p.add_argument("--wild-type",default="H")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=assess(read_fasta(a.alignment),a.reference,a.position,a.wild_type)
    Path(a.output).write_text(json.dumps(result,indent=2)+"\n")

if __name__=="__main__":main()
