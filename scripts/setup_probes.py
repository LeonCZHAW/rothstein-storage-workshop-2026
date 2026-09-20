"""Markierte Schreib-/Lesetests; ausschliesslich eigene Probeobjekte löschen."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from tinyflux import Point, TagQuery, TinyFlux

from scripts.storage_runtime import ROOT, mongo_client, neo4j_database, neo4j_driver

PROBE_DIR = ROOT / "data" / "work" / "_setup"
SYSTEMS = ("sqlite", "tinyflux", "mongodb", "neo4j")


def sqlite_connection():
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(PROBE_DIR / "probe.sqlite")
    connection.execute("CREATE TABLE IF NOT EXISTS setup_probe (token TEXT PRIMARY KEY, value INTEGER NOT NULL)")
    return connection


def write_probe(system: str, token: str) -> None:
    if system == "sqlite":
        connection = sqlite_connection()
        try:
            with connection:
                connection.execute("INSERT INTO setup_probe VALUES (?, 1) ON CONFLICT(token) DO UPDATE SET value=excluded.value", (token,))
        finally:
            connection.close()
    elif system == "tinyflux":
        PROBE_DIR.mkdir(parents=True, exist_ok=True)
        db = TinyFlux(str(PROBE_DIR / "probe.tinyflux.csv"))
        db.remove(TagQuery().token == token)
        db.insert(Point(time=datetime(2026, 1, 1, tzinfo=timezone.utc),
                        measurement="setup_probe", tags={"token": token}, fields={"value": 1}))
    elif system == "mongodb":
        with mongo_client() as client:
            client.storage_setup.probes.replace_one({"_id": token}, {"_id": token, "value": 1}, upsert=True)
    elif system == "neo4j":
        with neo4j_driver() as driver:
            with driver.session(database=neo4j_database()) as session:
                session.run("MERGE (n:_StorageSetupProbe {token: $token, dataset: '_setup'}) SET n.value = 1", token=token).consume()
    else:
        raise ValueError("Unbekanntes System")


def read_probe(system: str, token: str) -> bool:
    if system == "sqlite":
        connection = sqlite_connection()
        try:
            return connection.execute("SELECT value FROM setup_probe WHERE token=?", (token,)).fetchone() == (1,)
        finally:
            connection.close()
    if system == "tinyflux":
        db = TinyFlux(str(PROBE_DIR / "probe.tinyflux.csv"))
        points = db.search(TagQuery().token == token)
        return len(points) == 1 and points[0].fields["value"] == 1
    if system == "mongodb":
        with mongo_client() as client:
            document = client.storage_setup.probes.find_one({"_id": token})
            return document is not None and document.get("value") == 1
    if system == "neo4j":
        with neo4j_driver() as driver:
            with driver.session(database=neo4j_database()) as session:
                row = session.run("MATCH (n:_StorageSetupProbe {token: $token, dataset: '_setup'}) RETURN count(n) AS n, min(n.value) AS value", token=token).single()
                return row is not None and row["n"] == 1 and row["value"] == 1
    raise ValueError("Unbekanntes System")


def delete_probe(system: str, token: str) -> None:
    if system == "sqlite":
        connection = sqlite_connection()
        try:
            with connection:
                connection.execute("DELETE FROM setup_probe WHERE token=?", (token,))
        finally:
            connection.close()
    elif system == "tinyflux":
        TinyFlux(str(PROBE_DIR / "probe.tinyflux.csv")).remove(TagQuery().token == token)
    elif system == "mongodb":
        with mongo_client() as client:
            client.storage_setup.probes.delete_one({"_id": token})
    elif system == "neo4j":
        with neo4j_driver() as driver:
            with driver.session(database=neo4j_database()) as session:
                session.run("MATCH (n:_StorageSetupProbe {token: $token, dataset: '_setup'}) DELETE n", token=token).consume()
    else:
        raise ValueError("Unbekanntes System")


def server_version(system: str) -> str:
    if system == "sqlite":
        return sqlite3.sqlite_version
    if system == "tinyflux":
        from importlib.metadata import version
        return version("tinyflux")
    if system == "mongodb":
        with mongo_client() as client:
            return client.server_info()["version"]
    with neo4j_driver() as driver:
        with driver.session(database=neo4j_database()) as session:
            return session.run("CALL dbms.components() YIELD versions RETURN versions[0] AS version").single()["version"]
