#!/usr/bin/env python3
"""Assay-stratified VWF benchmark audit. No simulated predictions or imputed measurements."""
import argparse, json, pathlib, collections, math
ROOT=pathlib.Path(__file__).resolve().parents[2]
AXES={"platelet_binding","collagen_binding","fviii_binding","proteolysis_multimer","clearance"}
def load():
    return json.loads((ROOT/"data/benchmark/vwf_functional_candidates.json").read_text())
def summarize(data):
    axes=collections.defaultdict(lambda:{"candidates":0,"primary_records":0,"quantitative_records":0,"variants_with_quantitative_reference":0})
    for row in data["variants"]:
        a={"2B":"platelet_binding","2M":"platelet_binding","2N":"fviii_binding","2A":"proteolysis_multimer","1 Vicenza":"clearance"}.get(row["reported_subtype"])
        if a:axes[a]["candidates"]+=1
        records=row.get("primary_functional_evidence",[])
        by_axis=collections.defaultdict(list)
        for rec in records:
            axis=rec.get("phenotype_axis")
            if axis not in AXES:raise ValueError("Unknown functional axis: "+str(axis))
            by_axis[axis].append(rec)
            axes[axis]["primary_records"]+=1
            if all(isinstance(rec.get(k),(int,float)) and math.isfinite(rec[k]) for k in ("mutant_mean","reference_mean")):
                axes[axis]["quantitative_records"]+=1
        for axis,recs in by_axis.items():
            if any(all(isinstance(rec.get(k),(int,float)) and math.isfinite(rec[k]) for k in ("mutant_mean","reference_mean")) for rec in recs):
                axes[axis]["variants_with_quantitative_reference"]+=1
    return {"axes":{a:axes[a] for a in sorted(AXES)},"total_candidates":len(data["variants"]),"calibration_status":"not_calibrated","note":"Candidate phenotype labels are not ground truth; no model accuracy or effect score is computed without independent structural predictions."}
def evaluate(data,predictions):
    reference={r["variant"]:r for r in data["variants"]}
    results=[];seen=set()
    for p in predictions:
        v=p.get("variant");axis=p.get("phenotype_axis");direction=p.get("predicted_direction")
        if (v,axis) in seen:raise ValueError("Duplicate prediction for "+str((v,axis)))
        seen.add((v,axis))
        if axis not in AXES:raise ValueError("Unknown phenotype axis")
        row=reference.get(v)
        if not row:continue
        records=[r for r in row.get("primary_functional_evidence",[]) if r.get("phenotype_axis")==axis and r.get("direction")]
        directions={r["direction"] for r in records}
        if len(directions)!=1:continue
        truth=next(iter(directions))
        results.append({"variant":v,"axis":axis,"reference_direction":truth,"predicted_direction":direction,"match":direction==truth,"source_count":len(records)})
    return {"matched_comparisons":len(results),"results":results,"accuracy":sum(r["match"] for r in results)/len(results) if results else None,"warning":"Descriptive only. No held-out evaluation or calibration demonstrated; repeated variants and correlated primary studies require independence audit."}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--predictions",type=pathlib.Path,help="JSON array of independently generated variant/phenotype_axis/predicted_direction records");ap.add_argument("--output",type=pathlib.Path);args=ap.parse_args()
    data=load();out=summarize(data)
    if args.predictions:out["evaluation"]=evaluate(data,json.loads(args.predictions.read_text()))
    result=json.dumps(out,indent=2)
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(result+"\n")
    print(result)
if __name__=="__main__":main()
