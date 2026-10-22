"""Colab worker: only runs authenticated owner-issued H1786D jobs; never fabricates MD."""
import os,json,time,pathlib,subprocess,datetime,urllib.request
API="https://api.github.com/repos/aribis77/vwf-variant-kg"
TOKEN=os.environ["GITHUB_TOKEN"]
RUNNER=os.environ.get("VWF_RUNNER","/content/vwf_nvt/run_restrained_nvt.py")
INPUTS=os.environ.get("VWF_INPUTS","/content/vwf_nvt/private_inputs")
OUT=pathlib.Path("/content/vwf_md_jobs")
def api(method,path,payload=None):
 data=None if payload is None else json.dumps(payload).encode()
 req=urllib.request.Request(API+path,data=data,method=method,headers={"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","Content-Type":"application/json","User-Agent":"vwf-md-colab"})
 with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
def comment(n,body):api("POST",f"/issues/{n}/comments",{"body":body})
def state(n,status,detail):comment(n,"<!-- VWF_MD_STATUS -->\n"+json.dumps({"status":status,"detail":detail,"utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}))
def valid(result):
 assert result.get("variant")=="H1786D" and result.get("status")=="completed"
 for group in ("WT","H1786D"):
  reps=result["groups"][group]
  assert len(reps)==3
  for rep in reps:
   for key in ("total_interface_contacts","residue1786_contacts","residue1786_distance_angstrom","disulfide_distance_angstrom"):
    assert isinstance(rep[key],(int,float)) and not isinstance(rep[key],bool)
 return result
def process(issue):
 n=issue["number"]
 if issue["user"]["login"].lower()!="aribis77" or issue["title"]!="[VWF-MD] H1786D 20ps x3":return
 comments=api("GET",f"/issues/{n}/comments?per_page=100")
 if any("VWF_MD_STATUS" in c.get("body","") for c in comments):return
 state(n,"accepted","Owner-authorized job accepted by active Colab worker.")
 try:
  if not pathlib.Path(RUNNER).is_file() or not pathlib.Path(INPUTS).is_dir():
   raise RuntimeError("Validated runner or private input structures unavailable in Colab. No MD started.")
  folder=OUT/str(n);folder.mkdir(parents=True,exist_ok=True)
  state(n,"running","OpenMM subprocess launched.")
  with (folder/"runner.log").open("w") as log:
   p=subprocess.run(["python",RUNNER,"--input-dir",INPUTS,"--out",str(folder)],stdout=log,stderr=subprocess.STDOUT,timeout=7200)
  if p.returncode:raise RuntimeError(f"OpenMM runner failed (exit {p.returncode}). Inspect Colab runner.log.")
  result_file=folder/"md_endpoint_results.json"
  if not result_file.exists():raise RuntimeError("Runner finished but no md_endpoint_results.json exists. Endpoint analysis must be integrated; results were NOT generated.")
  result=valid(json.loads(result_file.read_text()));result["issue_number"]=n
  result["utc"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
  body="<!-- VWF_MD_RESULT -->\n```json\n"+json.dumps(result,allow_nan=False)+"\n```"
  if len(body)>60000:raise ValueError("Result too large for GitHub issue comment")
  comment(n,body);state(n,"completed","Validated results published to issue.")
 except Exception as exc:state(n,"failed",str(exc)[:800])
 finally:api("PATCH",f"/issues/{n}",{"state":"closed"})
def main():
 print("Colab worker ONLINE. Only aribis77's exact H1786D requests are processed.")
 while True:
  try:
   for issue in api("GET","/issues?state=open&per_page=100&sort=created&direction=asc"):
    if "pull_request" not in issue:process(issue)
  except Exception as e:print("Polling error:",repr(e))
  time.sleep(30)
if __name__=="__main__":main()
