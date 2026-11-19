import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import build_data as bd  # noqa: E402


def row(**overrides):
    base = {
        "id": "1", "journal": "Test Journal", "publisher": "Pub", "subjects": "AI/ML;Medical imaging",
        "access_model": "Subscription (hybrid)", "indexing": "SCIE", "quartile": "Q1",
        "impact_factor": "6.3", "if_verified": "yes", "speed": "Fast",
        "green_oa": "Yes", "url": "https://example.org/j", "notes": "",
    }
    base.update(overrides)
    return base


class ValidateTests(unittest.TestCase):
    def test_real_dataset_is_valid(self):
        header, rows = bd.load()
        self.assertEqual(bd.validate_rows(rows, header), [])
        self.assertGreater(len(rows), 0)

    def test_valid_row(self):
        self.assertEqual(bd.validate_rows([row()], bd.COLUMNS), [])

    def test_bad_header(self):
        self.assertTrue(bd.validate_rows([row()], ["id", "journal"]))

    def test_missing_required(self):
        errs = bd.validate_rows([row(publisher="")], bd.COLUMNS)
        self.assertTrue(any("publisher" in e for e in errs))

    def test_duplicates(self):
        errs = bd.validate_rows([row(), row(id="1", journal="Other")], bd.COLUMNS)
        self.assertTrue(any("duplicate id" in e for e in errs))
        errs = bd.validate_rows([row(), row(id="2", journal="test journal")], bd.COLUMNS)
        self.assertTrue(any("listed twice" in e for e in errs))

    def test_bad_values(self):
        for bad in [dict(quartile="Q5"), dict(speed="Instant"), dict(if_verified="maybe"),
                    dict(impact_factor="~6"), dict(url="http://insecure.org"), dict(id="abc")]:
            with self.subTest(bad=bad):
                self.assertTrue(bd.validate_rows([row(**bad)], bd.COLUMNS))

    def test_to_record(self):
        rec = bd.to_record(row(impact_factor="", speed=""))
        self.assertEqual(rec["subjects"], ["AI/ML", "Medical imaging"])
        self.assertIsNone(rec["impactFactor"])
        self.assertIsNone(rec["speed"])
        self.assertTrue(rec["ifVerified"])


if __name__ == "__main__":
    unittest.main()
