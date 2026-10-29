"""Contract tests for the user-facing H1786D structural report."""
import unittest
from analysis.render_variant_report import render

def fixture(mutant=False):
    partner={"chain":"A","author_residue":42,"insertion_code":"","residue":"G",
             "minimum_distance_angstrom":3.1,"atom_pairs":4,"inter_chain":True}
    contacts={"partner_count":1,"interchain_partner_count":1,"atom_pair_count":4,
              "partner_residues":[partner]}
    data={"mutation":"H1786D","site":{"wild_type_verified":True,"chain":"B","author_residue":1786},
          "structure":"4DMU.pdb","cutoff_angstrom":4.5,
          "wild_type_contacts":contacts,"mutant_contacts":None,
          "delta_contacts":None,"energetics":None,"conservation":None,
          "interpretation":"Measured wild-type environment only"}
    if mutant:
        data["mutant_contacts"]={"partner_count":0,"interchain_partner_count":0,
                                 "atom_pair_count":0,"partner_residues":[]}
        data["delta_contacts"]={"delta_atom_pairs":-4,"lost_partner_residues":[partner],
                                "gained_partner_residues":[],"retained_partner_count":0}
        data["modeling"]={"method":"PDBFixer","relaxed":False}
    return data

class ReportTests(unittest.TestCase):
    def test_wild_type_report_has_residue_and_no_false_mutant(self):
        page=render(fixture())
        self.assertIn("B, author residue 1786",page)
        self.assertIn("A:42",page)
        self.assertIn("Mutant model not available",page)
        self.assertIn("no ΔΔG claim",page)
        self.assertNotIn("Modeled H1786D environment",page)
    def test_mutant_report_has_comparison_and_caveat(self):
        page=render(fixture(True))
        self.assertIn("Modeled H1786D environment",page)
        self.assertIn("Atom-pair contact change: -4",page)
        self.assertIn("relaxed: False",page)
    def test_rejects_unverified_mapping(self):
        data=fixture()
        data["site"]["wild_type_verified"]=False
        with self.assertRaisesRegex(ValueError,"verified"):
            render(data)
    def test_escapes_untrusted_interpretation(self):
        data=fixture()
        data["interpretation"]="<script>alert(1)</script>"
        page=render(data)
        self.assertNotIn("<script>",page)
        self.assertIn("&lt;script&gt;",page)

if __name__=="__main__":
    unittest.main()
