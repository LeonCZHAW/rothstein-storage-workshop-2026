#!/usr/bin/env python3
"""Prüft Laufzeit, Quellen und tatsächliches Schreiben/Lesen in vier Speichern."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import platform
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

IMPORTS = {
    "pandas": "pandas", "numpy": "numpy", "matplotlib": "matplotlib", "plotly": "plotly",
    "pymongo": "pymongo", "neo4j": "neo4j", "tinyflux": "tinyflux", "python-dotenv": "dotenv",
    "jupyterlab": "jupyterlab", "ipykernel": "ipykernel", "nbclient": "nbclient", "nbformat": "nbformat",
}


def verify_input_data() -> None:
    """Validate bundled data and retain the ingestion command's actual error."""
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(ROOT / "ingestion" / "ingest.py"), "verify"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().splitlines()
        cause = detail[-1] if detail else f"Datenprüfung beendet mit Status {result.returncode}"
        raise ValueError(cause)
    manifest = json.loads((ROOT / "data/microblogging/manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = ROOT / "data/microblogging" / entry["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Microblogging-Datei verändert: data/microblogging/{entry['path']}")


def run_checks(offline: bool = False, wait: float = 0) -> dict:
    checks = []

    def record(name, status, detail):
        checks.append({"check": name, "status": status, "detail": detail})
        print(f"[{status.upper()}] {name}: {detail}")

    record("Python", "passed" if sys.version_info[:2] == (3, 12) else "failed", platform.python_version() + " (erwartet: 3.12)")
    expected = {}
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if "==" in line and not line.startswith("#"):
            name, value = line.strip().split("==", 1)
            expected[name] = value
    versions = {}
    for package, module in IMPORTS.items():
        try:
            importlib.import_module(module)
            versions[package] = importlib.metadata.version(package)
            record(package, "passed" if versions[package] == expected[package] else "failed",
                   f"{versions[package]} (erwartet: {expected[package]})")
        except Exception as error:
            record(package, "failed", f"Import fehlt oder schlägt fehl ({type(error).__name__}); requirements.txt installieren.")

    try:
        verify_input_data()
        record("Daten", "passed", "UAP-Snapshot, sieben Original-PDFs und Microblogging-Eingaben stimmen mit den Herkunftsnachweisen überein.")
    except Exception as error:
        record("Daten", "failed", f"{error}\n    Details prüfen: python ingestion/ingest.py verify")

    if any(c["status"] == "failed" for c in checks):
        record("Speichertests", "skipped", "Zuerst Laufzeit-, Paket- oder Datenfehler beheben.")
    else:
        from scripts.setup_probes import SYSTEMS, delete_probe, read_probe, server_version, write_probe
        for system in SYSTEMS:
            if offline and system in {"mongodb", "neo4j"}:
                record(system, "skipped", "Offline-Prüfung: Datenbankdienst nicht geprüft.")
                continue
            token = "setup-" + uuid.uuid4().hex
            deadline = time.monotonic() + max(0, wait)
            while True:
                try:
                    write_probe(system, token)
                    if not read_probe(system, token):
                        raise ValueError("Geschriebene Probe nicht korrekt gelesen")
                    version = server_version(system)
                    delete_probe(system, token)
                    if read_probe(system, token):
                        raise ValueError("Probe nicht entfernt")
                    record(system, "passed", f"{version}: geschrieben, Verbindung/Datei neu geöffnet, gelesen und eigene Probe entfernt.")
                    break
                except Exception as error:
                    if time.monotonic() < deadline and system in {"mongodb", "neo4j"}:
                        time.sleep(2)
                        continue
                    # Fremde Daten bleiben unberührt. Auch bei einem Teilfehler nur diese Probe entfernen.
                    try:
                        delete_probe(system, token)
                    except Exception:
                        pass
                    record(system, "failed", f"{type(error).__name__}: Dienststatus, Host/Port und Zugangsdaten gemäss technischer Vorbereitung prüfen.")
                    break

    ok = not any(c["status"] == "failed" for c in checks)
    label = "BASIS OK – MongoDB/Neo4j nicht geprüft" if offline and ok else ("SETUP OK" if ok else "SETUP FEHLER")
    print(label)
    return {"status": "passed" if ok else "failed", "scope": "offline" if offline else "all_four_stores",
            "python": platform.python_version(), "platform": platform.system(), "packages": versions, "checks": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Nur Python, Daten, SQLite und TinyFlux prüfen.")
    parser.add_argument("--wait", type=float, default=0, help="Technisches Startlimit je Dienst in Sekunden.")
    parser.add_argument("--report", type=Path, help="Optionaler JSON-Prüfbericht; enthält keine Passwörter.")
    args = parser.parse_args()
    result = run_checks(args.offline, args.wait)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
