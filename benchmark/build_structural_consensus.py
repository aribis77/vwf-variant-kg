"""Aggregate validated Protein Workbench structural features across PDB structures.

Descriptive consensus only. Multiple chains in one PDB are not independent
experimental replicates. No functional direction or clinical score is inferred.
"""
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "benchmark"
from validate_structural_reports import validate_report

def aggregate(reports):
    groups = defaultdict(list)
    rejected = []
    for report in reports:
        errors = validate_report(report)
        if errors:
            rejected.append({"report_id": report.get("report_id"), "errors": errors})
        else:
            groups[report["variant"]].append(report)
    results = []
    for variant, rows in sorted(groups.items()):
        structures = defaultdict(list)
        for r in rows:
            structures[r["pdb_id"].upper()].append(r)
        summaries = []
        for pdb, replicates in sorted(structures.items()):
            # Report medians per structure, never inflate N with alternate chains.
            def median(field):
                vals = [float(r[field]) for r in replicates if r[field] is not None]
                return statistics.median(vals) if vals else None
            summaries.append({
                "pdb_id": pdb,
                "report_ids": sorted(r["report_id"] for r in replicates),
                "chain_count": len({r["chain"] for r in replicates}),
                "contact_change_median": statistics.median(
                    [r["contacts_mutant"] - r["contacts_wt"] for r in replicates]),
                "delta_g_kcal_mol_median": median("delta_g_kcal_mol"),
                "conservation_score_median": median("conservation_score"),
            })
        def between_structure(field):
            values = [s[field] for s in summaries if s[field] is not None]
            return {
                "median": statistics.median(values) if values else None,
                "minimum": min(values) if values else None,
                "maximum": max(values) if values else None,
                "structure_count_with_value": len(values),
            }
        results.append({
            "variant": variant,
            "independent_pdb_count": len(structures),
            "report_count": len(rows),
            "per_structure": summaries,
            "contact_change": between_structure("contact_change_median"),
            "delta_g_kcal_mol": between_structure("delta_g_kcal_mol_median"),
            "conservation_score": between_structure("conservation_score_median"),
            "interpretation": "Descriptive structural feature consensus only; no assay direction or pathogenicity inferred.",
            "functional_prediction_eligible": False,
            "limitations": [
                "PDB structures may share underlying experimental constructs or datasets",
                "Cross-PDB differences reflect structural contexts, not independent biological replicates",
                "Free-energy methods and conservation definitions must be comparable before quantitative pooling",
                "Source-report checksums are declared, not independently authenticated",
            ],
        })
    return results, rejected

def main():
    data = json.loads((B / "structural_training_reports.json").read_text())
    results, rejected = aggregate(data["reports"])
    out = {
        "schema": "vwf-structural-feature-consensus/0.1",
        "status": "descriptive_only_not_calibrated",
        "variant_count": len(results),
        "rejected_report_count": len(rejected),
        "variants": results,
        "rejected_reports": rejected,
        "warning": "These summaries cannot establish increased, reduced, or preserved functional activity.",
    }
    (B / "structural_feature_consensus.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"variants": len(results), "rejected": len(rejected)}, indent=2))
    if rejected:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
