"""Render a standalone, readable, provenance-aware structural report.

Only values present in the validated JSON input are displayed. This report does
not infer pathogenicity, conservation, or binding free energy from contacts.
"""
import argparse
import html
import json
from pathlib import Path

def esc(value):
    return html.escape(str(value), quote=True)

def render(data):
    if not data.get("site", {}).get("wild_type_verified") or not data.get("mutation"):
        raise ValueError("Report requires a verified coordinate mapping and variant identifier")
    site=data["site"]
    wt=data["wild_type_contacts"]
    mutant=data.get("mutant_contacts")
    delta=data.get("delta_contacts")
    def rows(partners):
        return "".join("<tr><td>"+esc(p["chain"])+":"+esc(p["author_residue"])+
                       "</td><td>"+esc(p["residue"])+"</td><td>"+
                       esc(p["minimum_distance_angstrom"])+"</td><td>"+
                       esc(p["atom_pairs"])+"</td><td>"+
                       ("Yes" if p["inter_chain"] else "No")+"</td></tr>"
                       for p in partners)
    def table(title,contacts):
        return "<h2>"+esc(title)+"</h2><p>"+esc(contacts["partner_count"])+               " contacting residues; "+esc(contacts["interchain_partner_count"])+               " interchain partners; "+esc(contacts["atom_pair_count"])+               " atom-pair contacts within "+esc(data["cutoff_angstrom"])+               " Å.</p><table><thead><tr><th>Chain:residue</th><th>Amino acid</th><th>Closest distance (Å)</th><th>Atom pairs</th><th>Interchain</th></tr></thead><tbody>"+               rows(contacts["partner_residues"])+"</tbody></table>"
    content=table("Experimental wild-type environment",wt)
    if mutant and delta:
        content+=table("Modeled "+esc(data["mutation"])+" environment",mutant)
        content+="<h2>WT versus mutant</h2><p>Atom-pair contact change: "+esc(delta["delta_atom_pairs"])+                 "; lost residue partners: "+esc(len(delta["lost_partner_residues"]))+                 "; gained residue partners: "+esc(len(delta["gained_partner_residues"]))+".</p>"
        content+="<h3>Lost residue contacts</h3>"+table("WT-only partners",{
            "partner_count":len(delta["lost_partner_residues"]),
            "interchain_partner_count":sum(p["inter_chain"] for p in delta["lost_partner_residues"]),
            "atom_pair_count":sum(p["atom_pairs"] for p in delta["lost_partner_residues"]),
            "partner_residues":delta["lost_partner_residues"]})
        content+="<h3>Gained residue contacts</h3>"+table("Mutant-only partners",{
            "partner_count":len(delta["gained_partner_residues"]),
            "interchain_partner_count":sum(p["inter_chain"] for p in delta["gained_partner_residues"]),
            "atom_pair_count":sum(p["atom_pairs"] for p in delta["gained_partner_residues"]),
            "partner_residues":delta["gained_partner_residues"]})
    else:
        content+="<p class='notice'>Mutant model not available. These are WT contacts, not measured mutation effects.</p>"
    model=data.get("modeling",{})
    content+="<h2>Evidence and limitations</h2><dl><dt>Experimental structure</dt><dd>"+esc(data["structure"])+             " — chain "+esc(site["chain"])+", author residue "+esc(site["author_residue"])+             "</dd><dt>Model status</dt><dd>"+esc(model.get("method","No mutant model"))+             "; relaxed: "+esc(model.get("relaxed",False))+             "</dd><dt>Energetics</dt><dd>"+("Reported separately" if data.get("energetics") is not None else "Not calculated — no ΔΔG claim")+             "</dd><dt>Conservation</dt><dd>"+("Reported separately" if data.get("conservation") is not None else "Not calculated")+             "</dd><dt>Clinical classification</dt><dd>Not established from structural contacts alone</dd></dl>"
    content+="<p>"+esc(data.get("interpretation","No interpretation available"))+"</p>"
    return """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VWF """+esc(data["mutation"])+""" structural evidence</title><style>
body{font:16px/1.55 system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#172536;background:#fafbfd}
h1{color:#153a61}h2{margin-top:2rem}table{border-collapse:collapse;width:100%;font-size:.92rem}
th,td{text-align:left;padding:.55rem;border-bottom:1px solid #d4dce6}th{background:#eaf0f7}
.notice{padding:1rem;border-left:4px solid #a66a1b;background:#fff7e8}
dt{font-weight:700;margin-top:.6rem}dd{margin-left:0}a{color:#164d89}
</style></head><body><main><h1>VWF """+esc(data["mutation"])+""" — structural evidence</h1>
<p>Residue-resolved coordinate evidence. Geometry is not a clinical pathogenicity prediction.</p>"""+content+"</main></body></html>"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    data=json.loads(Path(args.input).read_text())
    Path(args.output).write_text(render(data),encoding="utf-8")

if __name__=="__main__":
    main()
