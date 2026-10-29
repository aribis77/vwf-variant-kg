import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from analysis import build_h1786d_conservation as pipeline


class ConservationPipelineTests(unittest.TestCase):
    def test_complete_pipeline_with_mocked_uniprot_and_mafft(self):
        # End-to-end offline test: retrieval, alignment, reference verification,
        # deduplication, provenance, and published JSON.
        reference="A"*1785+"H"+"A"*300
        species=list(pipeline.TAXA)
        accessions={taxon:"TEST"+str(taxon) for taxon in pipeline.TAXA.values()}
        sequences={"P04275":reference}
        for i,taxon in enumerate(pipeline.TAXA.values()):
            seq=list(reference)
            seq[100]= "ACDEFGHIKLMNPQRSTVWY"[i]
            seq[1785]="H" if i%2==0 else "D"
            sequences[accessions[taxon]]="".join(seq)
        def fake_mafft(args,**kwargs):
            self.assertEqual(args[0],"mafft")
            return SimpleNamespace(returncode=0,stderr="",stdout="".join(
                f">{name}\n{seq}\n" for name,seq in sequences.items()))
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"result.json"
            with patch.object(pipeline,"get_fasta",side_effect=lambda a:sequences[a]),\
                 patch.object(pipeline,"select_ortholog",side_effect=lambda t:accessions[t]),\
                 patch.object(pipeline.subprocess,"run",side_effect=fake_mafft):
                result=pipeline.run(path)
            self.assertTrue(path.exists())
            self.assertEqual(result["position"],1786)
            self.assertEqual(result["wild_type"],"H")
            self.assertEqual(result["ortholog_count"],12)
            self.assertEqual(len(result["ortholog_accessions_used"]),12)
            self.assertAlmostEqual(result["reference_residue_fraction"],0.5)

    def test_unreviewed_unique_full_length_fallback(self):
        entry={"primaryAccession":"A12345","entryType":"UniProtKB unreviewed (TrEMBL)",
               "sequence":{"length":2813}}
        with patch.object(pipeline,"get_json",return_value={"results":[entry]}):
            self.assertEqual(pipeline.select_ortholog(10116),"A12345")

    def test_ambiguous_unreviewed_orthologs_rejected(self):
        entries=[{"primaryAccession":a,"entryType":"UniProtKB unreviewed (TrEMBL)",
                  "sequence":{"length":2813}} for a in ("A12345","B12345")]
        with patch.object(pipeline,"get_json",return_value={"results":entries}):
            with self.assertRaisesRegex(ValueError,"unambiguous"):
                pipeline.select_ortholog(10116)

    def test_alignment_sequence_mutation_rejected(self):
        reference="A"*1785+"H"+"A"*300
        accessions={taxon:"TEST"+str(taxon) for taxon in pipeline.TAXA.values()}
        def fake_mafft(args,**kwargs):
            sequences={"P04275":reference[:-1]+"G"}
            for accession in accessions.values():
                sequences[accession]=reference
            return SimpleNamespace(returncode=0,stderr="",stdout="".join(
                f">{name}\n{seq}\n" for name,seq in sequences.items()))
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(pipeline,"get_fasta",return_value=reference),\
                 patch.object(pipeline,"select_ortholog",side_effect=lambda t:accessions[t]),\
                 patch.object(pipeline.subprocess,"run",side_effect=fake_mafft):
                with self.assertRaisesRegex(ValueError,"Alignment altered sequence"):
                    pipeline.run(Path(folder)/"result.json")


if __name__=="__main__":
    unittest.main()
