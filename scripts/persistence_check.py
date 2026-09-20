#!/usr/bin/env python3
"""Markierte Daten vor einem Neustart schreiben und danach wieder lesen."""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.setup_probes import PROBE_DIR, SYSTEMS, delete_probe, read_probe, write_probe

MARKER = PROBE_DIR / "persistence_marker.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["write", "read", "cleanup"])
    parser.add_argument("--offline", action="store_true", help="Nur SQLite/TinyFlux; Dienste bleiben ausdrücklich ungeprüft.")
    args = parser.parse_args()
    if args.action == "write":
        if MARKER.exists():
            raise SystemExit("Eine Probe ist bereits vorhanden. Zuerst read oder cleanup ausführen.")
        state = {"token": "persist-" + uuid.uuid4().hex,
                 "systems": list(SYSTEMS[:2] if args.offline else SYSTEMS)}
        PROBE_DIR.mkdir(parents=True, exist_ok=True)
        # Marker vor dem ersten Schreibversuch erhalten: Teilversuche können bereinigt werden.
        MARKER.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    elif MARKER.exists():
        state = json.loads(MARKER.read_text(encoding="utf-8"))
    else:
        raise SystemExit("Keine markierte Probe vorhanden. Zuerst write ausführen.")

    failed = False
    for system in state["systems"]:
        try:
            if args.action == "write":
                write_probe(system, state["token"])
            elif args.action == "cleanup":
                delete_probe(system, state["token"])
            else:
                if not read_probe(system, state["token"]):
                    raise ValueError("Probe fehlt oder unterscheidet sich")
            print(f"[PASSED] {system}: {args.action}")
        except Exception as error:
            print(f"[FAILED] {system}: {type(error).__name__}; Dienststatus und technische Vorbereitung prüfen.")
            failed = True
    if args.action == "cleanup" and not failed:
        MARKER.unlink()
    if state["systems"] != list(SYSTEMS):
        print("TEILPRÜFUNG: MongoDB und Neo4j nicht geprüft.")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
