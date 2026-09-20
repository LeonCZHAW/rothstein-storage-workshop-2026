"""Regression checks for bundled data integrity and useful setup diagnostics.

Run with: python -m unittest discover -s validation -p test_input_verification.py
Only temporary copies are modified; no database services are needed.
"""

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import verify_setup


class InputVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="storage-input-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("ingestion", "data/raw", "data/input", "data/microblogging"):
            shutil.copytree(ROOT / name, self.root / name, ignore=shutil.ignore_patterns("__pycache__"))
        self.root_patch = patch.object(verify_setup, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def test_complete_distribution_passes(self):
        verify_setup.verify_input_data()

    def test_stale_pipeline_fingerprint_is_explained(self):
        path = self.root / "data/input/build_manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["pipeline_sha256"] = "0" * 64
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Pipeline-Prüfsumme.*derselben Workshop-Version"):
            verify_setup.verify_input_data()

    def test_modified_source_is_rejected(self):
        path = self.root / "data/raw/pursue_catalog.csv"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "Prüfsumme des Rohkatalogs"):
            verify_setup.verify_input_data()

    def test_modified_output_is_named(self):
        path = self.root / "data/input/relational/agencies.csv"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "Ausgabedatei verändert: relational/agencies.csv"):
            verify_setup.verify_input_data()

    def test_missing_original_pdf_is_named(self):
        manifest = json.loads((self.root / "data/raw/sample_assets.json").read_text(encoding="utf-8"))
        path = self.root / "data/raw" / manifest[0]["relative_path"]
        path.unlink()
        with self.assertRaises(ValueError) as caught:
            verify_setup.verify_input_data()
        self.assertIn("FileNotFoundError", str(caught.exception))
        self.assertIn(path.name, str(caught.exception))

    def test_modified_microblogging_input_is_named(self):
        manifest = json.loads((self.root / "data/microblogging/manifest.json").read_text(encoding="utf-8"))
        path = self.root / "data/microblogging" / manifest["files"][0]["path"]
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaises(ValueError) as caught:
            verify_setup.verify_input_data()
        self.assertIn("Microblogging-Datei verändert", str(caught.exception))
        self.assertIn(path.name, str(caught.exception))


if __name__ == "__main__":
    unittest.main()
