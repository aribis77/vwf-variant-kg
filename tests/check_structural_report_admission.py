"""Structural report schema tests use synthetic data only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmark"))
from validate_structural_reports import validate_report

row = {
    "report_id": "TEST", "variant": "H1786D", "uniprot_accession": "P04275",
    "pdb_id": "4DMU", "chain": "B", "uniprot_residue": 1786,
    "pdb_author_residue": 1786, "mapped_wild_type": "H",
    "mapping_verified": True, "source_report_sha256": "a" * 64,
    "contacts_wt": 10, "contacts_mutant": 8, "delta_g_kcal_mol": 1.2,
    "conservation_score": 0.8, "calculation_method": "synthetic-test",
    "analysis_version": "test-only",
}
assert validate_report(row) == []
assert "uniprot_residue_mismatch" in validate_report({**row, "uniprot_residue": 1785})
assert "unverified_residue_mapping" in validate_report({**row, "mapping_verified": False})
assert "missing_report_checksum" in validate_report({**row, "source_report_sha256": ""})
assert "invalid_delta_g_kcal_mol" in validate_report({**row, "delta_g_kcal_mol": float("nan")})
assert "invalid_contacts_wt" in validate_report({**row, "contacts_wt": -1})
assert "invalid_conservation_score" in validate_report({**row, "conservation_score": "high"})
print("Structural report admission schema checks passed.")
