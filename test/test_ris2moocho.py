"""Integration test: ris2moocho converts test/Reading.ris to expected collection JSON."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

MOOCHO_DATA = Path(__file__).resolve().parent.parent
RIS2MOOCHO = MOOCHO_DATA / "ris2moocho.py"
READING_RIS = MOOCHO_DATA / "test" / "Reading.ris"

EXPECTED_READING_JSON: dict = {
    "id": "reading",
    "name": "Reading",
    "shortName": "Reading",
    "items": [
        {
            "littlePrinceItem": {
                "title": "From Apartheid to Democracy",
                "author": "Michael Schaeffer Omer-Man, Sarah Leah Whitson",
                "year": "2025",
                "date-added": "2025-09-30",
                "language": "English",
                "publisher": "University of California Press",
                "isbn13": "9780520402010",
                "itemUrl": "https://www.perlego.com/book/4986171/from-apartheid-to-democracy-a-blueprint-for-peace-in-israelpalestine-pdf",
                "ris-type": "BOOK",
            }
        },
        {
            "littlePrinceItem": {
                "title": "The AI Ideal",
                "author": "Niklas Lidströmer",
                "year": "2026",
                "date-added": "2026-03-30",
                "language": "English",
                "publisher": "Morgan Kaufmann",
                "isbn13": "9780443449734",
                "itemUrl": "https://www.perlego.com/book/5445528/the-ai-ideal-aidealism-and-the-governance-of-ai-pdf",
                "ris-type": "BOOK",
            }
        },
    ],
}


class TestRis2MoochoReading(unittest.TestCase):
    def test_converts_reading_ris_to_expected_json(self) -> None:
        self.assertTrue(RIS2MOOCHO.is_file(), f"missing script: {RIS2MOOCHO}")
        self.assertTrue(READING_RIS.is_file(), f"missing fixture: {READING_RIS}")

        proc = subprocess.run(
            [sys.executable, str(RIS2MOOCHO), str(READING_RIS)],
            cwd=str(MOOCHO_DATA),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            f"ris2moocho failed:\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}",
        )
        self.assertEqual(proc.stderr.strip(), "", proc.stderr)

        got = json.loads(proc.stdout)
        self.assertEqual(got, EXPECTED_READING_JSON)

    def test_help_flags_print_usage_and_exit_zero(self) -> None:
        for flag in ("-h", "--help"):
            with self.subTest(flag=flag):
                proc = subprocess.run(
                    [sys.executable, str(RIS2MOOCHO), flag],
                    cwd=str(MOOCHO_DATA),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("usage:", proc.stdout)
                self.assertIn("file.ris", proc.stdout)
                self.assertEqual(proc.stderr.strip(), "", proc.stderr)


if __name__ == "__main__":
    unittest.main()
