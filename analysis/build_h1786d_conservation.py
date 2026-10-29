"""Build a reproducible VWF ortholog alignment from UniProt and score H1786.

Requires MAFFT on PATH and network access. Fails closed on missing orthologs,
reference mismatch, ambiguous candidates, or alignment errors.
"""
import json
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from analysis.conservation import assess, read_fasta

REFERENCE="P04275"
TAXA={"mouse":10090,"rat":10116,"dog":9615,"cow":9913,"pig":9823,
      "rabbit":9986,"chimpanzee":9598,"macaque":9544,"horse":9796,
      "sheep":9940,"cat":9685,"chicken":9031}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"vwf-variant-kg/1.0","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=35) as response:
        return json.load(response)

def get_fasta(accession):
    url="https://rest.uniprot.org/uniprotkb/"+urllib.parse.quote(accession,safe="")+".fasta"
    req=urllib.request.Request(url,headers={"User-Agent":"vwf-variant-kg/1.0"})
    with urllib.request.urlopen(req,timeout=35) as response:
        text=response.read().decode("utf-8")
    return "".join(line.strip() for line in text.splitlines() if not line.startswith(">")).upper()

def select_ortholog(taxon):
    query=f"(gene_exact:VWF) AND (organism_id:{taxon})"
    url="https://rest.uniprot.org/uniprotkb/search?"+urllib.parse.urlencode({
        "query":query,"format":"json","size":100,
        "fields":"accession,reviewed,length,gene_primary,organism_id"})
    entries=get_json(url).get("results",[])
    # Only unambiguous reviewed, full-length proteins are accepted.
    candidates=[entry for entry in entries if entry.get("entryType")=="UniProtKB reviewed (Swiss-Prot)"
                and 1500<=entry.get("sequence",{}).get("length",0)<=4000]
    if len(candidates)!=1:
        raise ValueError(f"Taxon {taxon}: expected one reviewed full-length VWF, got {len(candidates)}")
    return candidates[0]["primaryAccession"]

def run(output):
    reference=get_fasta(REFERENCE)
    if len(reference)<1786 or reference[1785]!="H":
        raise ValueError("P04275 reference sequence does not contain H1786")
    sequences={"P04275":reference}
    provenance={}
    failures={}
    for species,taxon in TAXA.items():
        try:
            accession=select_ortholog(taxon)
            seq=get_fasta(accession)
            if not 1500<=len(seq)<=4000 or any(c not in "ACDEFGHIKLMNPQRSTVWY" for c in seq):
                raise ValueError("Noncanonical or fragment sequence")
            if accession in sequences:
                raise ValueError("Duplicate accession")
            sequences[accession]=seq
            provenance[species]={"taxon_id":taxon,"uniprot_accession":accession}
        except (ValueError,KeyError,TimeoutError,OSError) as exc:
            failures[species]=str(exc)
    if len(sequences)<6:
        raise ValueError("Fewer than five curated orthologs retrieved: "+repr(failures))
    with tempfile.TemporaryDirectory() as tmp:
        inp=Path(tmp)/"input.fasta"
        inp.write_text("".join(f">{key}\n{seq}\n" for key,seq in sequences.items()))
        proc=subprocess.run(["mafft","--auto","--quiet",str(inp)],capture_output=True,text=True,timeout=240)
        if proc.returncode:
            raise RuntimeError("MAFFT failed: "+proc.stderr[-1000:])
        aligned=Path(tmp)/"aligned.fasta"
        aligned.write_text(proc.stdout)
        records=read_fasta(aligned)
        if set(records)!=set(sequences):
            raise ValueError("Alignment lost an input accession")
        for accession,sequence in sequences.items():
            if records[accession].replace("-","")!=sequence:
                raise ValueError("Alignment altered sequence "+accession)
        result=assess(records,REFERENCE,1786,"H")
    result["source"]="UniProtKB REST; reviewed full-length VWF orthologs"
    result["alignment_method"]="MAFFT --auto"
    result["ortholog_provenance"]=provenance
    result["excluded_taxa"]=failures
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,indent=2)+"\n")
    return result

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="analysis/H1786D_conservation.json")
    args=p.parse_args()
    print(json.dumps(run(args.output),indent=2))
