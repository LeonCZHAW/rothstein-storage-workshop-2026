"""Verbindungen und Arbeitsverzeichnisse für Demos und Workshopaufgaben.

Priorität der Konfiguration: Prozessumgebung, optionale .env, Kursstandard.
Dieses Modul importiert keine Workshopdaten und löscht keine Datenbestände.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase
from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)
DATASETS = {"uap", "microblogging"}


def dataset_name(dataset: str) -> str:
    if dataset not in DATASETS:
        raise ValueError("Datensatz muss uap oder microblogging sein.")
    return dataset


def work_dir(dataset: str) -> Path:
    path = ROOT / "data" / "work" / dataset_name(dataset)
    path.mkdir(parents=True, exist_ok=True)
    return path


def mongo_client() -> MongoClient:
    return MongoClient(
        host=os.getenv("MONGO_HOST", "127.0.0.1"),
        port=int(os.getenv("MONGO_PORT", "27017")),
        username=os.getenv("MONGO_USERNAME", "workshop"),
        password=os.getenv("MONGO_PASSWORD", "Storage-Mongo-2026"),
        authSource="admin",
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
    )


def mongo_database_name(dataset: str) -> str:
    return "storage_" + dataset_name(dataset)


def neo4j_driver():
    host = os.getenv("NEO4J_HOST", "127.0.0.1")
    port = int(os.getenv("NEO4J_PORT", "7687"))
    return GraphDatabase.driver(
        f"bolt://{host}:{port}",
        auth=("neo4j", os.getenv("NEO4J_PASSWORD", "Storage-Neo4j-2026")),
        connection_timeout=5,
        connection_acquisition_timeout=10,
        max_transaction_retry_time=10,
    )


def neo4j_database() -> str:
    return os.getenv("NEO4J_DATABASE", "neo4j")


def connection_summary() -> dict:
    """Nur Verbindungsziele; keine Passwörter oder Zugangsdaten ausgeben."""
    return {
        "MongoDB": f"{os.getenv('MONGO_HOST', '127.0.0.1')}:{os.getenv('MONGO_PORT', '27017')}",
        "Neo4j": f"{os.getenv('NEO4J_HOST', '127.0.0.1')}:{os.getenv('NEO4J_PORT', '7687')}",
        "Neo4j-Datenbank": neo4j_database(),
    }
