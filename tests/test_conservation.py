import unittest
from analysis.conservation import assess

class ConservationTests(unittest.TestCase):
    def test_reference_gap_mapping_and_fraction(self):
        records={"human":"A-CHE","mouse":"ATCHE","rat":"ATCHE",
                 "dog":"ATCDE","cow":"ATCHE","pig":"ATCDE","cat":"ATCHE"}
        result=assess(records,"human",3,"H")
        self.assertEqual(result["alignment_column_1based"],4)
        self.assertEqual(result["ortholog_count"],6)
        self.assertEqual(result["reference_residue_fraction"],round(4/6,4))
    def test_reject_wrong_reference_residue(self):
        with self.assertRaisesRegex(ValueError,"mismatch"):
            assess({"human":"AC","mouse":"AC"},"human",2,"H",minimum_orthologs=1)
    def test_reject_insufficient_coverage(self):
        with self.assertRaisesRegex(ValueError,"Insufficient"):
            assess({"human":"AH","mouse":"AH"},"human",2,"H")
    def test_reject_unaligned_input(self):
        with self.assertRaisesRegex(ValueError,"aligned"):
            assess({"human":"AH","mouse":"AHH"},"human",2,"H",minimum_orthologs=1)

if __name__=="__main__":unittest.main()
