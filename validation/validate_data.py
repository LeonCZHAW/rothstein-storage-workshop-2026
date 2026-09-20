"""Fachliche Datenprüfungen; optional mit einem tatsächlichen TinyFlux-Roundtrip."""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ingestion"))
from ingest import incident_date, verify


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def run(with_tinyflux=False):
    data = ROOT / "data/input"
    verify(ROOT / "data/raw", data)
    entries = jsonl(data / "catalog_entries.jsonl")
    documents = jsonl(data / "document/catalog_documents.jsonl")
    nodes = jsonl(data / "graph/nodes.jsonl")
    edges = jsonl(data / "graph/edges.jsonl")
    annual = list(csv.DictReader((data / "timeseries/annual_catalog_counts.csv").open(encoding="utf-8", newline="")))
    metrics = json.loads((data / "reference_metrics.json").read_text(encoding="utf-8"))
    # Echte Problemfälle des Quellbestands: Jahrhunderte, Zeiträume und fehlende Daten.
    assert incident_date("3/18/45", 2026)["incident_year"] == 1945
    assert incident_date("10/27/23", 2026)["incident_day"] == "2023-10-27"
    assert incident_date("2002, 2023-2024", 2026)["annual_eligible"] is False
    assert incident_date("1970s", 2026)["incident_year"] is None
    assert incident_date("Late 2025", 2026)["incident_day"] is None
    assert incident_date("4/10/2025-4/11/2025", 2026)["incident_year"] == 2025
    assert incident_date("N/A", 2026)["annual_eligible"] is False
    assert incident_date("October, 2023", 2026)["incident_month"] == 10
    assert incident_date("October, 2023", 2026)["incident_day"] is None

    # Schlüssel und Beziehungen tatsächlich in SQLite laden.
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript("""
    CREATE TABLE agencies (agency_id TEXT PRIMARY KEY, name TEXT NOT NULL);
    CREATE TABLE entries (entry_id TEXT PRIMARY KEY, source_key TEXT NOT NULL,
      agency_id TEXT NOT NULL REFERENCES agencies, incident_year INTEGER,
      eligible INTEGER NOT NULL CHECK (eligible IN (0,1)));
    CREATE TABLE assets (asset_id TEXT PRIMARY KEY);
    CREATE TABLE entry_assets (entry_id TEXT REFERENCES entries,
      asset_id TEXT REFERENCES assets, PRIMARY KEY(entry_id, asset_id));
    CREATE TABLE pairs (pairing_id TEXT PRIMARY KEY, source_id TEXT REFERENCES entries,
      target_id TEXT REFERENCES entries);
    """)
    with (data / "relational/agencies.csv").open(encoding="utf-8", newline="") as f:
        db.executemany("INSERT INTO agencies VALUES (?,?)", [(r["agency_id"], r["name"]) for r in csv.DictReader(f)])
    db.executemany("INSERT INTO entries VALUES (?,?,?,?,?)", [(e["entry_id"], e["source_key"], e["agency_id"], e["incident_year"], int(e["annual_eligible"])) for e in entries])
    with (data / "relational/assets.csv").open(encoding="utf-8", newline="") as f:
        db.executemany("INSERT INTO assets VALUES (?)", [(r["asset_id"],) for r in csv.DictReader(f)])
    with (data / "relational/entry_assets.csv").open(encoding="utf-8", newline="") as f:
        db.executemany("INSERT INTO entry_assets VALUES (?,?)", [(r["entry_id"], r["asset_id"]) for r in csv.DictReader(f)])
    with (data / "relational/portal_pairings.csv").open(encoding="utf-8", newline="") as f:
        db.executemany("INSERT INTO pairs VALUES (?,?,?)", [(r["pairing_id"], r["source_entry_id"], r["target_entry_id"]) for r in csv.DictReader(f)])
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    try:
        db.execute("INSERT INTO entry_assets VALUES ('missing', 'missing')")
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("Ungültiger Fremdschlüssel wurde akzeptiert")
    assert db.execute("SELECT count(*) FROM entries WHERE source_key = 'FBI-UAP-D014'").fetchone()[0] == 2
    assert {d["entry_id"] for d in documents} == {e["entry_id"] for e in entries}
    assert sum(len(d["assets"]) for d in documents) == metrics["entry_asset_links"]
    assert len({n["node_id"] for n in nodes}) == metrics["graph_nodes"]
    assert all(e["source"] in {n["node_id"] for n in nodes} and e["target"] in {n["node_id"] for n in nodes} for e in edges)
    entry_ids = {e["source_key"]: e["entry_id"] for e in entries if e["source_key"] != "FBI-UAP-D014"}
    path = ["FBI-UAP-D021", "DOW-UAP-D079", "Western US Event", "DOW-UAP-D080"]
    for a, b in zip(path, path[1:]):
        assert db.execute("SELECT count(*) FROM pairs WHERE source_id=? AND target_id=?", (entry_ids[a], entry_ids[b])).fetchone()[0] > 0
    sql_year_counts = {(year, aid): cnt for year, aid, cnt in db.execute("SELECT incident_year, agency_id, count(*) FROM entries WHERE eligible=1 GROUP BY incident_year, agency_id")}
    assert all(int(row["catalog_entries"]) == sql_year_counts.get((int(row["incident_year"]), row["agency_id"]), 0) for row in annual)
    selected = db.execute("SELECT count(*) FROM entries WHERE eligible=1 AND incident_year>=2020 AND incident_year<2024").fetchone()[0]
    result = {"catalog_entries": len(entries), "sqlite_foreign_keys": "passed",
              "duplicate_source_key_preserved": "passed", "document_coverage": "passed",
              "graph_path": path, "annual_aggregation_matches_sqlite": "passed",
              "catalog_entries_incident_years_2020_2023": selected,
              "tinyflux_roundtrip": "not_requested"}
    if with_tinyflux:
        from tinyflux import TinyFlux, Point, TimeQuery
        with tempfile.TemporaryDirectory() as tmp:
            ts = TinyFlux(str(Path(tmp) / "catalog.csv"))
            points = [Point(time=datetime.fromisoformat(r["period_start"].replace("Z", "+00:00")),
                            measurement="catalog_entries_by_incident_year",
                            tags={"agency_id": r["agency_id"], "date_basis": r["date_basis"]},
                            fields={"catalog_entries": int(r["catalog_entries"])}) for r in annual]
            ts.insert_multiple(points)
            assert len(ts.all()) == len(annual)
            # Erneutes Öffnen prüft Speicherung auf Datenträger.
            reopened = TinyFlux(str(Path(tmp) / "catalog.csv"))
            t = TimeQuery()
            subset = reopened.search((t >= datetime(2020, 1, 1, tzinfo=timezone.utc)) & (t < datetime(2024, 1, 1, tzinfo=timezone.utc)))
            assert sum(p.fields["catalog_entries"] for p in subset) == selected
            result["tinyflux_roundtrip"] = "passed"
            result["tinyflux_points"] = len(points)
    db.close()
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-tinyflux", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = run(args.with_tinyflux)
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    print(output)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
