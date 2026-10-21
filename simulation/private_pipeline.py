#!/usr/bin/env python3
"""Private-only production orchestration. Execute outside a public CI workspace.

Example:
  python simulation/private_pipeline.py --private-dir /secure/vwf/approved --results-dir /secure/vwf/results --steps 50000

Chemically approved, periodic WT/H1786D .prmtop/.inpcrd files must be prepared
independently. They are never uploaded to GitHub by this script.
"""
import argparse,hashlib,json,os,pathlib,subprocess,sys
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--private-dir",required=True)
    p.add_argument("--results-dir",required=True)
    p.add_argument("--steps",type=int,default=50000)
    p.add_argument("--validate-only",action="store_true")
    a=p.parse_args()
    if a.steps<1 or a.steps>500000: p.error("steps must be 1..500000")
    private=pathlib.Path(a.private_dir).expanduser().resolve()
    results=pathlib.Path(a.results_dir).expanduser().resolve()
    repo=pathlib.Path(__file__).resolve().parent.parent
    if private.is_relative_to(repo) or results.is_relative_to(repo):
        p.error("Private inputs and results must be stored OUTSIDE the public repository")
    if not private.is_dir():p.error("Private input directory does not exist")
    results.mkdir(parents=True,exist_ok=True)
    filenames=[f"{variant}.{ext}" for variant in ("WT","H1786D") for ext in ("prmtop","inpcrd")]
    filenames.append("chemistry_approved.json")
    for filename in filenames:
        f=private/filename
        if not f.is_file() or f.stat().st_size==0:p.error("Missing or empty "+filename)
    approval=json.loads((private/"chemistry_approved.json").read_text())
    required=("approved","prepared_by","chemistry_protocol","forcefield","protonation","hydroxyproline","termini","disulfide","solvent_ions")
    if approval.get("approved") is not True or any(not approval.get(k) for k in required):
        p.error("Explicit documented scientific chemistry approval is required")
    checks={name:hashlib.sha256((private/name).read_bytes()).hexdigest() for name in filenames}
    (results/"input_checksums.json").write_text(json.dumps(checks,indent=2))
    validator=pathlib.Path(__file__).with_name("validate_topologies.py")
    cmd=[sys.executable,str(validator),"--prepared",str(private),"--report",str(results/"topology_qa.json")]
    subprocess.run(cmd,check=True)
    if a.validate_only:
        print("QA completed. No molecular dynamics was run.")
        return
    runner=pathlib.Path(__file__).with_name("run_md.py")
    subprocess.run([sys.executable,str(runner),"--prepared",str(private),"--out",str(results),"--steps",str(a.steps)],check=True)
    print("Paired pilot complete. Results remain local/private:",results)
if __name__=="__main__":main()
