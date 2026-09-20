"""SQLite-Dateien, typisierte CSV-Eingaben und atomarer Snapshot-Import.

Die Abfragen und die zu ergänzende UAP-Zwischentabelle stehen in den Notebooks.
Nur Python-Standardbibliothek; keine MongoDB-/Neo4j-Verbindung erforderlich.
"""
from contextlib import contextmanager
import csv
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
TABLES = {
    "microblogging": ("users", "posts", "likes", "comments", "follows"),
    "uap": ("agencies", "releases", "catalog_entries", "assets", "entry_assets", "portal_pairings"),
}
INTEGER_COLUMNS = {
    "microblogging": {"user_id", "post_id", "like_id", "comment_id", "src_user_id", "dst_user_id"},
    "uap": {"source_row", "incident_year", "incident_month"},
}
BOOLEAN_COLUMNS = {"annual_eligible", "redaction_reported"}


@contextmanager
def connect(path):
    """Explizite Transaktionen; Fremdschlüssel vor BEGIN aktivieren; immer schliessen."""
    if sqlite3.sqlite_version_info < (3, 37, 0):
        raise RuntimeError("SQLite >= 3.37 für STRICT benötigt. Kursumgebung aktivieren.")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, isolation_level=None, timeout=10)
    try:
        con.execute("PRAGMA foreign_keys = ON")
        if con.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
            raise RuntimeError("Fremdschlüsselprüfung konnte nicht aktiviert werden.")
        yield con
    finally:
        con.close()


def read_snapshot(dataset):
    """CSV-Leerfelder -> None, Ganzzahlen -> int, True/False -> 1/0.

    release_date wird im UAP-SQL-Modell ausschliesslich in releases gespeichert.
    Vor dem Weglassen der redundanten CSV-Spalte wird ihre Übereinstimmung geprüft.
    """
    tables = TABLES[dataset]
    directory = ROOT / ("data/input/relational" if dataset == "uap" else "data/microblogging/relational")
    result = {}
    for table in tables:
        with (directory / f"{table}.csv").open(encoding="utf-8", newline="") as stream:
            rows = []
            for source in csv.DictReader(stream):
                row = {}
                for key, value in source.items():
                    if value == "":
                        row[key] = None
                    elif key in INTEGER_COLUMNS[dataset]:
                        row[key] = int(value)
                    elif dataset == "uap" and key in BOOLEAN_COLUMNS:
                        row[key] = {"True": 1, "False": 0}[value]
                    else:
                        row[key] = value
                rows.append(row)
        result[table] = rows
    if dataset == "uap":
        dates = {r["release_id"]: r["release_date"] for r in result["releases"]}
        for row in result["catalog_entries"]:
            if row.pop("release_date") != dates[row["release_id"]]:
                raise ValueError("Widersprüchliches Veröffentlichungsdatum im Eingabestand.")
    return result


def create_schema(con, dataset, bridge_ddl=None):
    """DDL separat vom Datenimport. Bestehende Tabellen werden nicht ersetzt."""
    if con.in_transaction:
        raise RuntimeError("Schema nur ausserhalb einer laufenden Transaktion anlegen.")
    filename = "uap_base.sql" if dataset == "uap" else "microblogging.sql"
    con.executescript((ROOT / "schemas/sqlite" / filename).read_text(encoding="utf-8"))
    if dataset == "uap":
        if not bridge_ddl:
            raise ValueError("Ergänze zuerst das CREATE TABLE für entry_assets.")
        con.executescript(bridge_ddl)


def table_counts(con, dataset):
    return {table: con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            for table in TABLES[dataset]}


def load_snapshot(con, dataset, rows=None):
    """Ersetzt nur die Tabellen dieses Beispiels, gemeinsam in EINER Transaktion.

    Erneutes Laden stellt den vorbereiteten Snapshot wieder her. Eigene Änderungen
    in diesen Tabellen werden dabei verworfen. Andere Tabellen werden nicht gelöscht.
    Bei einem Fehler bleibt der zuvor bestätigte Datenbestand erhalten.
    """
    rows = read_snapshot(dataset) if rows is None else rows
    if con.in_transaction:
        raise RuntimeError("Vor dem Import die laufende Transaktion abschliessen.")
    if con.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        raise RuntimeError("Import verlangt aktivierte Fremdschlüsselprüfung.")
    con.execute("BEGIN IMMEDIATE")
    try:
        for table in reversed(TABLES[dataset]):
            con.execute(f'DELETE FROM "{table}"')
        for table in TABLES[dataset]:
            records = rows[table]
            if not records:
                continue
            columns = list(records[0])
            names = ", ".join(f'"{c}"' for c in columns)
            marks = ", ".join("?" for _ in columns)
            con.executemany(f'INSERT INTO "{table}" ({names}) VALUES ({marks})',
                            [tuple(r[c] for c in columns) for r in records])
        if con.execute("PRAGMA foreign_key_check").fetchall():
            raise sqlite3.IntegrityError("Fremdschlüsselprüfung fehlgeschlagen.")
        con.execute("COMMIT")
    except BaseException:
        con.execute("ROLLBACK")
        raise
    return table_counts(con, dataset)


def query(path, sql, params=()):
    """Leseverbindung immer neu öffnen; optionale Parameter getrennt von SQL."""
    import pandas as pd
    with connect(path) as con:
        con.execute("PRAGMA query_only = ON")
        return pd.read_sql_query(sql, con, params=params)
