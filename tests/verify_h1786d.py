"""Fail-closed, reproducible UniProt H1786 to PDB coordinate validation.
This does not model H1786D or establish functional effects.
"""
import json
import urllib.request

ACCESSION = "P04275"
POSITION = 1786
WT = "H"
AA3 = {"HIS": "H"}
STRUCTURES = ("4DMU", "1AO3")

def download(url):
    req = urllib.request.Request(url, headers={"User-Agent": "vwf-variant-kg-acceptance-test/1.0"})
    with urllib.request.urlopen(req, timeout=35) as response:
        return response.read().decode("utf-8")

def validate(pdb):
    payload = json.loads(download(f"https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/{pdb.lower()}"))
    entry = payload.get(pdb.lower()) or payload.get(pdb.upper()) or {}
    mappings = entry.get("UniProt", {}).get(ACCESSION, {}).get("mappings", [])
    coords = download(f"https://files.rcsb.org/download/{pdb}.pdb")
    matches = []
    diagnostics = []
    for mapping in mappings:
        start, end = mapping.get("start", {}), mapping.get("end", {})
        lo, hi = mapping.get("unp_start"), mapping.get("unp_end")
        if not isinstance(lo, int) or not isinstance(hi, int) or not lo <= POSITION <= hi:
            continue
        begin, finish = start.get("author_residue_number"), end.get("author_residue_number")
        chain = mapping.get("chain_id")
        try:
            begin, finish = int(begin), int(finish)
        except (TypeError, ValueError):
            diagnostics.append(f"{chain}: missing author numbering {begin!r}-{finish!r}")
            continue
        if finish - begin != hi - lo:
            diagnostics.append(f"{chain}: noncontiguous mapping {begin}-{finish} / {lo}-{hi}")
            continue
        if not chain:
            diagnostics.append("mapping missing chain_id")
            continue
        number = begin + POSITION - lo
        atoms = [line for line in coords.splitlines()
                 if line.startswith("ATOM  ") and line[21:22] == chain
                 and line[22:26].strip().lstrip("-").isdigit()
                 and int(line[22:26]) == number and line[26:27] == " "]
        if any(AA3.get(line[17:20].strip()) == WT for line in atoms):
            matches.append({"pdb": pdb, "chain": chain, "author_residue": number,
                            "uniprot": f"{ACCESSION}:{POSITION}", "wild_type": WT,
                            "atom_count": len(atoms)})
        else:
            diagnostics.append(f"{chain}:{number} has {len(atoms)} ATOM lines; no resolved HIS")
    unique = list({(m["chain"], m["author_residue"]): m for m in matches}.values())
    if not unique:
        raise AssertionError(f"{pdb}: no verified histidine. SIFTS mappings={len(mappings)}; diagnostics={diagnostics[:12]}")
    return unique

def main():
    results = {pdb: validate(pdb) for pdb in STRUCTURES}
    print(json.dumps({"status": "coordinate_mapping_verified", "results": results,
                      "limitations": ["No mutation performed", "No structural energies calculated",
                                      "No KG/Workbench browser roundtrip tested"]}, indent=2))

if __name__ == "__main__":
    main()
