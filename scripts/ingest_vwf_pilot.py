#!/usr/bin/env python3
"""Fetch auditable ClinVar and Ensembl pilot records; fail closed on mapping uncertainty.

Run: python scripts/ingest_vwf_pilot.py --out-dir data/pilot_raw
No claims are promoted to the KG merely because a network request succeeds.
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TARGETS = {
    "R1315L": {"clinvar_id": None, "hgvs": None, "protein": "R1315L"},
    "H1786D": {"clinvar_id": None, "hgvs": None},
}
HEADERS = {"Accept": "application/json", "User-Agent": "vwf-variant-kg-research/0.1"}
def retrieve(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))
def save_record(root, variant, provider, url, data):
    payload = json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    sha = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    path = root / (variant + "_" + provider + ".json")
    path.write_text(payload, encoding="utf-8")
    return {"provider": provider, "variant": variant, "url": url,
            "raw_path": str(path), "sha256": sha, "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "status": "retrieved_not_adjudicated"}
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="data/pilot_raw")
    parser.add_argument("--strict", action="store_true", help="exit nonzero when a source is unavailable")
    args = parser.parse_args()
    root = Path(args.out_dir)
    root.mkdir(parents=True, exist_ok=True)
    manifest = []
    failures = []
    for variant, target in TARGETS.items():
        endpoints = []
        if target["clinvar_id"]:
            endpoints.append(("clinvar", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" +
                urllib.parse.urlencode({"db": "clinvar", "id": target["clinvar_id"], "retmode": "json"})))
        if target["hgvs"]:
            endpoints.append(("ensembl", "https://rest.ensembl.org/vep/human/hgvs/" +
                urllib.parse.quote(target["hgvs"], safe="") + "?" + urllib.parse.urlencode({"content-type": "application/json"})))
        if target.get("protein"):
            endpoints.append(("clinvar_discovery", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" +
                urllib.parse.urlencode({"db": "clinvar", "term": 'VWF[gene] AND "' + target["protein"] + '"',
                                        "retmode": "json", "retmax": 25})))
        if not endpoints:
            manifest.append({"variant": variant, "status": "requires_verified_nucleotide_hgvs",
                             "reason": "Do not infer a unique genomic allele from a protein substitution."})
        for provider, url in endpoints:
            try:
                record = retrieve(url)
                if provider == "clinvar":
                    result = record.get("result", {})
                    item = result.get(target["clinvar_id"], {})
                    if str(item.get("uid", "")) != target["clinvar_id"]:
                        raise ValueError("ClinVar primary response does not match requested UID")
                elif provider == "clinvar_discovery":
                    if not isinstance(record.get("esearchresult", {}).get("idlist"), list):
                        raise ValueError("ClinVar discovery returned no identifier list")
                elif not isinstance(record, list) or not record:
                    raise ValueError("Ensembl VEP returned no variant predictions")
                manifest.append(save_record(root, variant, provider, url, record))
                if provider == "clinvar_discovery":
                    ids = [str(x) for x in record["esearchresult"]["idlist"] if str(x).isdigit()]
                    if ids:
                        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(
                            {"db": "clinvar", "id": ",".join(ids), "retmode": "json"})
                        try:
                            summary = retrieve(summary_url)
                            result = summary.get("result", {})
                            if not all(str(result.get(cid, {}).get("uid", "")) == cid for cid in ids):
                                raise ValueError("ClinVar candidate summary returned mismatched identifiers")
                            manifest.append(save_record(root, variant, "clinvar_candidates", summary_url, summary))
                        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError, OSError) as exc:
                            failures.append({"variant": variant, "provider": "clinvar_candidates", "error": str(exc)})
                            manifest.append({"variant": variant, "provider": "clinvar_candidates", "status": "fetch_failed"})
            except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError, OSError) as exc:
                failures.append({"variant": variant, "provider": provider, "error": str(exc)})
                manifest.append({"variant": variant, "provider": provider, "status": "fetch_failed"})
    result = {"schema_version": "vwf-source-fetch/0.1", "records": manifest, "failures": failures,
              "policy": "Raw records are not normalized assertions. Validate transcript, GRCh38 REF/ALT, source release, clinical assertion date and review status before promotion."}
    (root / "manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(manifest), "failures": len(failures), "manifest": str(root / "manifest.json")}))
    if args.strict and failures:
        sys.exit(1)
if __name__ == "__main__":
    main()
