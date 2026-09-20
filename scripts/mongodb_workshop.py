"""Vorbereitung und wiederholbare MongoDB-Imports für den festen Lehrsnapshot.

Keine globale Löschung, kein collMod und keine Mehrdokument-Transaktionen.
Serverzugriffe erfolgen ausschliesslich innerhalb von mongo_workspace().
"""
from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from uuid import uuid4

from bson import BSON
from bson.codec_options import CodecOptions
from pymongo import ReplaceOne
from pymongo.errors import WriteError
from storage_runtime import ROOT, mongo_client, mongo_database_name

UTC = timezone.utc


def jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


def utc_for_synthetic_platform(value):
    """Explizite Lehrkonvention: zeitzonenlose synthetische Plattformdaten als UTC."""
    result = datetime.fromisoformat(value)
    return result.replace(tzinfo=UTC) if result.tzinfo is None else result.astimezone(UTC)


def prepare_documents(dataset):
    if dataset == "uap":
        documents = deepcopy(jsonl(ROOT / "data/input/document/catalog_documents.jsonl"))
        for d in documents:
            d["_id"] = d["entry_id"]
        result = {"catalog": documents}
    elif dataset == "microblogging":
        base = ROOT / "data/microblogging"
        result = {name: deepcopy(jsonl(base / f"document/{name}.jsonl")) for name in ("users", "posts", "follows")}
        for d in result["users"]:
            d["_id"] = d["user_id"]
            d["created_at"] = utc_for_synthetic_platform(d["created_at"])
        for d in result["posts"]:
            d["created_at"] = utc_for_synthetic_platform(d["created_at"])
            for comment in d["comments"]:
                comment["created_at"] = utc_for_synthetic_platform(comment["created_at"])
        for d in result["follows"]:
            d["_id"] = f"{d['src_user_id']}:{d['dst_user_id']}"
            d["since"] = utc_for_synthetic_platform(d["since"])
        with (base / "relational/likes.csv").open(encoding="utf-8", newline="") as f:
            result["likes"] = [dict(_id=int(r["like_id"]), like_id=int(r["like_id"]),
                                    post_id=int(r["post_id"]), user_id=int(r["user_id"]),
                                    created_at=utc_for_synthetic_platform(r["created_at"])) for r in csv.DictReader(f)]
        likes = Counter(d["post_id"] for d in result["likes"])
        assert all(d["like_count"] == likes[d["_id"]] for d in result["posts"])
    else:
        raise ValueError("dataset muss uap oder microblogging sein.")
    for documents in result.values():
        validate_batch(documents)
    return result


def validate_batch(documents):
    if not documents:
        raise ValueError("Leere Eingabe wird nicht als Löschauftrag interpretiert.")
    ids = [d.get("_id") for d in documents]
    if any(x is None for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("Jedes Dokument benötigt eine eindeutige, stabile _id.")
    for document in documents:
        if len(BSON.encode(document)) > 16 * 1024 * 1024:
            raise ValueError("Dokument überschreitet die BSON-Grössengrenze.")


def collection_names(dataset, solution=False):
    names = ("users", "posts", "follows", "likes") if dataset == "microblogging" else ("catalog", "reading_notes")
    suffix = "_sample_solution" if solution else ""
    token = os.getenv("STORAGE_MONGO_TEST_TOKEN", "")
    if token and not re.fullmatch(r"[0-9a-f]{32}", token):
        raise ValueError("Ungültiger Prüf-Token.")
    prefix = f"_mongodb_{token}_{dataset}_" if token else ""
    return {name: prefix + name + suffix for name in names}


@contextmanager
def mongo_workspace(dataset, solution=False):
    """Kursverbindung; Prüfläufe nutzen nur eigene Collections in storage_setup."""
    names = collection_names(dataset, solution)
    database_name = "storage_setup" if os.getenv("STORAGE_MONGO_TEST_TOKEN") else mongo_database_name(dataset)
    with mongo_client() as client:
        client.admin.command("ping")
        db = client.get_database(database_name, codec_options=CodecOptions(tz_aware=True, tzinfo=UTC))
        yield db, names


def sync_collection(collection, documents):
    """Bestand einer ausdrücklich gewählten Workshop-Collection wiederherstellen.

    Pro Dokument atomar, insgesamt NICHT atomar. Bei einem unterbrochenen Import
    denselben Snapshot erneut laden und erst nach IMPORT OK auswerten.
    """
    validate_batch(documents)  # Fehlerhafte Eingabe vor dem ersten Schreibzugriff ablehnen.
    operations = [ReplaceOne({"_id": d["_id"]}, deepcopy(d), upsert=True) for d in documents]
    collection.bulk_write(operations, ordered=True)
    # Erst nach erfolgreichen Upserts überholte IDs in genau dieser Collection entfernen.
    collection.delete_many({"_id": {"$nin": [d["_id"] for d in documents]}})
    count = collection.count_documents({})
    if count != len(documents):
        raise RuntimeError("Import nicht vollständig: Snapshot erneut laden.")
    return count


def import_snapshot(db, names, dataset, documents=None):
    documents = prepare_documents(dataset) if documents is None else documents
    for batch in documents.values():
        validate_batch(batch)
    counts = {name: sync_collection(db[names[name]], batch) for name, batch in documents.items()}
    if dataset == "microblogging":
        db[names["users"]].create_index("user_id", unique=True)
        db[names["follows"]].create_index([("src_user_id", 1), ("dst_user_id", 1)], unique=True)
        db[names["follows"]].create_index("dst_user_id")
        db[names["posts"]].create_index([("author_id", 1), ("created_at", -1)])
        db[names["posts"]].create_index([("like_count", -1), ("_id", 1)])
        db[names["likes"]].create_index("user_id")
    else:
        db[names["catalog"]].create_index("entry_id", unique=True)
        db[names["catalog"]].create_index("source_key")  # Quelle enthält dieselbe Kennung zweimal.
    return counts


def validate_note(note, source):
    """Anwendungsprüfung; keine automatisch durch MongoDB erzwungenen Fremdschlüssel."""
    if not isinstance(note, dict):
        raise ValueError("Ergänze Deine Lesernotiz als Python-Dictionary.")
    if note.get("_id") != "note:" + source["entry_id"] or note.get("entry_id") != source["entry_id"]:
        raise ValueError("Notiz-ID und entry_id müssen zum gewählten Katalogeintrag passen.")
    if note.get("origin") != "workshop_manual_review":
        raise ValueError("Eigene Interpretation als workshop_manual_review kennzeichnen.")
    review = note.get("review", {})
    if not isinstance(review, dict) or not all(isinstance(review.get(k), str) and review[k].strip() for k in ("finding", "statement")):
        raise ValueError("review benötigt finding und statement als nicht leere Texte.")
    evidence = review.get("evidence", {})
    if not isinstance(evidence, dict) or evidence.get("asset_id") not in {a["asset_id"] for a in source["assets"]}:
        raise ValueError("Beleg muss ein Asset dieses Katalogeintrags referenzieren.")
    pages = evidence.get("pdf_pages")
    if not isinstance(pages, list) or not pages or any(type(p) is not int or p < 1 for p in pages):
        raise ValueError("pdf_pages benötigt eine nicht leere Liste positiver Seitenzahlen.")
    BSON.encode(note)


def save_note(db, names, note):
    source = db[names["catalog"]].find_one({"_id": note.get("entry_id")})
    if source is None:
        raise ValueError("Der referenzierte Katalogeintrag fehlt.")
    validate_note(note, source)
    return db[names["reading_notes"]].replace_one({"_id": note["_id"]}, deepcopy(note), upsert=True)


def probe_note_schema(db, validator, valid_note):
    """Eigene kurzlebige Collection; readWrite genügt, kein collMod erforderlich."""
    name = "_mongodb_schema_probe_" + uuid4().hex
    collection = db.create_collection(name, validator=validator, validationLevel="strict", validationAction="error")
    try:
        collection.insert_one(deepcopy(valid_note))
        invalid = deepcopy(valid_note)
        invalid["_id"] = "probe:invalid_pages"
        invalid["review"]["evidence"]["pdf_pages"] = "5"
        try:
            collection.insert_one(invalid)
        except WriteError as error:
            if error.code != 121:
                raise
        else:
            raise AssertionError("Schema akzeptiert pdf_pages als Text statt Array.")
        # Ein korrekt geformter, aber nicht existierender Verweis wird akzeptiert.
        unlinked = deepcopy(valid_note)
        unlinked["_id"] = "note:_nonexistent_probe_entry"
        unlinked["entry_id"] = "_nonexistent_probe_entry"
        collection.insert_one(unlinked)
        assert collection.count_documents({}) == 2
        return {"invalid_type_rejected": True, "reference_existence_not_enforced": True}
    finally:
        collection.drop()
