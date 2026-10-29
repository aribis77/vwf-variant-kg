import tempfile
import unittest
from pathlib import Path
from analysis.structural_contacts import analyse, compare_models

def atom(serial,name,res,chain,num,x,y,z):
    return f"ATOM  {serial:5d} {name:4s} {res:3s} {chain}{num:4d}    {x:8.3f}{y:8.3f}{z:8.3f}{1.0:6.2f}{20.0:6.2f}           {name.strip()[0]:>2s}\n"

class StructuralTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/"synthetic.pdb"
        self.path.write_text(atom(1,"CA","HIS","B",1786,0,0,0)+atom(2,"CA","GLY","A",10,0,0,3)+atom(3,"CA","ALA","B",1787,0,0,9))
    def tearDown(self):self.tmp.cleanup()
    def test_contacts_and_no_invented_mutant(self):
        r=analyse(self.path,"B",1786,"H","D")
        self.assertEqual(r["wild_type_contacts"]["interchain_partner_count"],1)
        self.assertEqual(r["wild_type_contacts"]["partner_residues"][0]["author_residue"],10)
        self.assertIsNone(r["energetics"])
        self.assertIsNone(r["mutant_contacts"])
    def test_wrong_wild_type_rejected(self):
        with self.assertRaisesRegex(ValueError,"Wild-type mismatch"):
            analyse(self.path,"B",1786,"R","D")
    def test_missing_site_rejected(self):
        with self.assertRaisesRegex(ValueError,"Unresolved"):
            analyse(self.path,"B",1785,"H","D")

    def test_mutant_comparison(self):
        mutant=Path(self.tmp.name)/"mutant.pdb"
        mutant.write_text(atom(1,"CA","ASP","B",1786,0,0,0)+atom(2,"CA","GLY","A",10,0,0,3)+atom(3,"CA","ALA","B",1787,0,0,9)+atom(4,"OD1","ASP","B",1786,0,0,7))
        r=compare_models(self.path,mutant,"B",1786,"H","D")
        self.assertEqual(r["status"],"coordinate_models_compared")
        self.assertEqual(r["delta_contacts"]["lost_partner_residues"],[])
        self.assertEqual(r["delta_contacts"]["gained_partner_residues"][0]["author_residue"],1787)
        self.assertIsNone(r["energetics"])
    def test_local_backbone_movement_rejected(self):
        mutant=Path(self.tmp.name)/"shifted.pdb"
        mutant.write_text(atom(1,"CA","ASP","B",1786,0,0,0)+
                          atom(2,"CA","GLY","A",10,0,0,7)+
                          atom(3,"CA","ALA","B",1787,0,0,9))
        with self.assertRaisesRegex(ValueError,"changed local backbone"):
            compare_models(self.path,mutant,"B",1786,"H","D")

    def test_heavy_atom_named_hg_is_not_dropped(self):
        # The element field takes precedence over an atom name starting with H.
        heavy=atom(1,"HG","HIS","B",1786,0,0,0)
        heavy=heavy[:76]+"HG"+heavy[78:]
        partner=atom(2,"CA","GLY","A",10,0,0,3)
        self.path.write_text(heavy+partner)
        result=analyse(self.path,"B",1786,"H","D")
        self.assertEqual(result["wild_type_contacts"]["interchain_partner_count"],1)

    def test_unmutated_model_rejected(self):
        with self.assertRaisesRegex(ValueError,"Mutant coordinate mismatch"):
            compare_models(self.path,self.path,"B",1786,"H","D")

if __name__=="__main__":unittest.main()
