"""Test per-PDB aggregation with synthetic Protein Workbench-like reports."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmark"))
from build_structural_consensus import aggregate

def make(report_id, pdb, chain, contacts, dg, conservation):
    return {
        "report_id": report_id, "variant": "H1786D", "uniprot_accession": "P04275",
        "pdb_id": pdb, "chain": chain, "uniprot_residue": 1786,
        "pdb_author_residue": 1786, "mapped_wild_type": "H",
        "mapping_verified": True, "source_report_sha256": "a" * 64,
        "contacts_wt": 10, "contacts_mutant": contacts,
        "delta_g_kcal_mol": dg, "conservation_score": conservation,
        "calculation_method": "synthetic-test", "analysis_version": "test-only",
    }

rows = [make("a", "4DMU", "B", 8, 2, .7),
        make("b", "4DMU", "D", 6, 4, .9),
        make("c", "1ABC", "A", 12, 6, .5)]
results, rejected = aggregate(rows)
assert not rejected and len(results) == 1
r = results[0]
assert r["report_count"] == 3 and r["independent_pdb_count"] == 2
assert r["contact_change"]["median"] == 0
assert r["delta_g_kcal_mol"]["median"] == 4.5
assert r["conservation_score"]["median"] == .65
assert not r["functional_prediction_eligible"]
assert len(r["per_structure"]) == 2
results, rejected = aggregate(rows + [{**rows[0], "report_id": "invalid", "mapping_verified": False}])
assert len(rejected) == 1
assert results[0]["report_count"] == 3
print("PDB-level structural consensus and invalid report quarantine passed.")
