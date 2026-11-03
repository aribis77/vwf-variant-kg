"""Generate a readable evidence-isolation report from actual pipeline artifacts.

Report is an audit, not a prediction or validation result.
"""
import html
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "benchmark"
snapshot = json.loads((root / "evaluation_evidence_snapshot.json").read_text())
graph = json.loads((root / "evaluation_graph_snapshot.json").read_text())
identities = json.loads((root / "publication_identity_audit.json").read_text())
provenance = json.loads((root / "internal_source_provenance.json").read_text())
edges = json.loads((root / "edge_provenance_review.json").read_text())
counts = snapshot["counts"]
gcounts = graph["counts"]
rows = provenance["records"]

def cell(value):
    return html.escape(str(value))

table_rows = "".join(
    "<tr><td>" + cell(r["source_id"]) + "</td><td>" +
    cell(r["node_label"]) + "</td><td>" +
    cell(r["linked_observation_count"]) + "</td><td>" +
    cell(r["reference_overlap_status"]) + "</td><td>" +
    cell(", ".join(r["canonical_observation_source_urls"]) or "Not established") +
    "</td></tr>"
    for r in rows
)
class_rows = "".join(
    "<tr><td>" + cell(k.replace("_", " ")) + "</td><td>" + cell(v) + "</td></tr>"
    for k, v in sorted(edges["classifications"].items())
)
doc = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VWF-KG evidence isolation audit</title>
<style>
:root{font-family:system-ui,Arial,sans-serif;color:#eaf0f8;background:#101b2e}
body{max-width:1100px;margin:0 auto;padding:36px 22px;line-height:1.55}
h1{font-size:2rem}h2{margin-top:34px}p{color:#c5d4e5}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.card{background:#20334c;border:1px solid #3a506a;border-radius:12px;padding:16px}
.big{font-size:2rem;font-weight:700;color:#86d7db}
small{display:block;color:#c5d4e5}
table{border-collapse:collapse;width:100%;font-size:14px}
td,th{padding:11px;text-align:left;border-bottom:1px solid #3a506a;overflow-wrap:anywhere}
th{color:#86d7db}.scroll{overflow-x:auto}
.warning{padding:16px;border:1px solid #d0a85b;border-radius:10px;background:#352d25;color:#ffe4a9}
</style></head><body>
<h1>VWF-KG evidence isolation audit</h1>
<p>Provisional benchmark evidence, provenance and graph-edge review. This report does not establish biological accuracy.</p>
<div class="warning"><strong>Not cleared for performance scoring.</strong> Publication aliases, derived graph assertions, node labels, external retrieval and structural inputs still require independent verification.</div>
<div class="cards">
<div class="card"><span class="big">""" + cell(counts["original_observations"]) + """</span><small>Original observations</small></div>
<div class="card"><span class="big">""" + cell(counts["excluded_observations"]) + """</span><small>Excluded by reference URL</small></div>
<div class="card"><span class="big">""" + cell(counts["retained_observations"]) + """</span><small>Provisionally retained observations</small></div>
<div class="card"><span class="big">""" + cell(gcounts["quarantined_edges"]) + """</span><small>Quarantined graph edges</small></div>
</div>
<h2>Graph relationship classifications</h2><div class="scroll"><table>
<thead><tr><th>Classification</th><th>Relationships</th></tr></thead><tbody>""" + class_rows + """</tbody></table></div>
<h2>Internal source provenance</h2><p>Single URL mappings are inferred from linked KG observations, not independent bibliographic adjudication.</p>
<div class="scroll"><table><thead><tr><th>Internal source</th><th>KG label</th><th>Linked observations</th><th>Reference overlap</th><th>Source URL</th></tr></thead>
<tbody>""" + table_rows + """</tbody></table></div>
<h2>Outstanding checks</h2>
<p>Verify DOI, PMID and PMCID aliases, inspect source-derived nodes and assertions, audit external retrieval, independently adjudicate reference assays, and freeze predictions before comparing methods.</p>
<p>Known reference identifier count: """ + cell(identities["reference_identifier_count"]) + """. Candidate sourced edges awaiting review: """ + cell(len(edges["candidate_sourced_edges"])) + """.</p>
</body></html>"""
out = root / "evaluation_audit_report.html"
out.write_text(doc)
assert "Not cleared for performance scoring" in doc
print(f"Generated {out.name}: {len(rows)} internal sources, {len(edges['candidate_sourced_edges'])} candidate edges")
