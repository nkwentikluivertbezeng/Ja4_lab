import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from blocklist import is_blocked, load_blocklist  # noqa: E402


class BlocklistTests(unittest.TestCase):
    def test_loads_hashes_and_full_fingerprints_ignoring_comments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "blocklist.txt"
            path.write_text(
                "# JA4C hashes\n"
                "  2B729B4BF6F3  # known client\n"
                "\n"
                "t13d201261_8daaf6152771_36bf25f296df\n",
                encoding="utf-8",
            )

            self.assertEqual(
                load_blocklist(path),
                frozenset(
                    {
                        "2b729b4bf6f3",
                        "t13d201261_8daaf6152771_36bf25f296df",
                    }
                ),
            )

    def test_matches_ja4c_and_full_fingerprints(self):
        ja4c = "t13d201261_2b729b4bf6f3_36bf25f296df"
        full = "t13d201261_8daaf6152771_36bf25f296df"

        self.assertTrue(is_blocked(ja4c, {"2b729b4bf6f3"}))
        self.assertTrue(is_blocked(full, {full}))
        self.assertFalse(is_blocked(ja4c, {"8daaf6152771"}))

    def test_rejects_invalid_entries_with_line_number(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "blocklist.txt"
            path.write_text("not-a-fingerprint\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "line 1"):
                load_blocklist(path)


if __name__ == "__main__":
    unittest.main()
