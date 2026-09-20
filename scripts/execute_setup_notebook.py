#!/usr/bin/env python3
"""Das Setup-Notebook ohne Änderung der Vorlage ausführen."""
import argparse
import json
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    notebook = nbformat.read(ROOT / "notebooks/00_setup_check.ipynb", as_version=4)
    if args.offline:
        for cell in notebook.cells:
            if "setup-configuration" in cell.metadata.get("tags", []):
                cell.source = cell.source.replace("OFFLINE_ONLY = False", "OFFLINE_ONLY = True")
    client = NotebookClient(notebook, timeout=180, kernel_name="rothstein-storage-workshop-2026",
                            resources={"metadata": {"path": str(ROOT / "notebooks")}})
    client.execute()
    out = ROOT / "data/work/setup_execution"
    out.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, out / "00_setup_check_executed.ipynb")
    report = {"status": "passed", "scope": "offline" if args.offline else "all_four_stores",
              "code_cells_executed": sum(c.cell_type == "code" for c in notebook.cells),
              "template_modified": False}
    (out / "notebook_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
