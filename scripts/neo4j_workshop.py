"""Graphdaten und isolierte Neo4j-Arbeitsbereiche für den Storage-Kurs.

Keine Dienste werden gestartet. JSONL-/CSV-Vorbereitung funktioniert offline.
Importe ersetzen genau einen Kursbereich in einer Datentransaktion.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from contextlib import contextmanager
import csv
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LABELS = {x: "Storage" + x for x in
          ("User", "Post", "CatalogEntry", "Agency", "Asset", "Release")}
EDGE_TYPES = {"FOLLOWS", "AUTHORED", "LIKES", "COMMENTED", "CATALOG_AGENCY",
              "LINKS_ASSET", "IN_RELEASE", "PORTAL_PAIRS_WITH"}
SCOPES = {"microblogging_demo", "uap_task", "uap_solution"}


def graph_scope(dataset, solution=False):
    if dataset not in {"uap", "microblogging"}:
        raise ValueError("Datensatz muss uap oder microblogging sein.")
    base = "microblogging_demo" if dataset == "microblogging" else "uap_solution" if solution else "uap_task"
    token = os.getenv("STORAGE_NEO4J_TEST_TOKEN")
    scope = f"test_{token}_{base}" if token else base
    validate_scope(scope)
    return scope


def validate_scope(scope):
    if scope not in SCOPES and not re.fullmatch(
            r"test_[0-9a-f]{32}_(microblogging_demo|uap_task|uap_solution)", scope):
        raise ValueError("Unbekannter Kursbereich; kein Zugriff oder Reset ausgeführt.")


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def csv_rows(name):
    with (ROOT / "data/microblogging/relational" / f"{name}.csv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def utc(value):
    """Explizite UTC-Lehrkonvention für ursprünglich zeitzonenlose Demo-Daten."""
    parsed = datetime.fromisoformat(value)
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def prepare_graph(dataset):
    if dataset == "uap":
        nodes = jsonl(ROOT / "data/input/graph/nodes.jsonl")
        edges = jsonl(ROOT / "data/input/graph/edges.jsonl")
    elif dataset == "microblogging":
        nodes, edges = [], []
        for r in csv_rows("users"):
            uid = int(r["user_id"])
            nodes.append({"node_id": f"user:{uid}", "label": "User", "properties":
                          {"user_id": uid, "username": r["username"], "created_at": date.fromisoformat(r["created_at"])}})
        for r in csv_rows("posts"):
            pid, uid = int(r["post_id"]), int(r["user_id"])
            nodes.append({"node_id": f"post:{pid}", "label": "Post", "properties":
                          {"post_id": pid, "text": r["text"], "created_at": utc(r["created_at"])}})
            edges.append({"edge_id": f"authored:{pid}", "source": f"user:{uid}", "target": f"post:{pid}",
                          "type": "AUTHORED", "properties": {"at": utc(r["created_at"])}})
        for r in csv_rows("follows"):
            src, dst = int(r["src_user_id"]), int(r["dst_user_id"])
            edges.append({"edge_id": f"follow:{src}:{dst}", "source": f"user:{src}", "target": f"user:{dst}",
                          "type": "FOLLOWS", "properties": {"since": date.fromisoformat(r["since"])}})
        for table, typ, id_field in [("likes", "LIKES", "like_id"), ("comments", "COMMENTED", "comment_id")]:
            for r in csv_rows(table):
                event_id = int(r[id_field])
                props = {id_field: event_id, "at": utc(r["created_at"])}
                if "text" in r:
                    props["text"] = r["text"]
                edges.append({"edge_id": f"{table}:{event_id}", "source": f"user:{int(r['user_id'])}",
                              "target": f"post:{int(r['post_id'])}", "type": typ, "properties": props})
    else:
        raise ValueError("Unbekannter Datensatz")
    graph = {"nodes": nodes, "edges": edges}
    validate_graph(graph)
    return graph


def validate_graph(graph):
    ids = [n["node_id"] for n in graph["nodes"]]
    eids = [e["edge_id"] for e in graph["edges"]]
    if len(set(ids)) != len(ids) or len(set(eids)) != len(eids):
        raise ValueError("Doppelte technische Knoten- oder Kanten-ID.")
    known = set(ids)
    for node in graph["nodes"]:
        if node["label"] not in LABELS:
            raise ValueError("Unbekanntes Label")
    for edge in graph["edges"]:
        if edge["type"] not in EDGE_TYPES or edge["source"] not in known or edge["target"] not in known:
            raise ValueError("Unbekannter Beziehungstyp oder fehlender Endpunkt.")
    for item in graph["nodes"] + graph["edges"]:
        props = item["properties"]
        if {"scope", "node_id", "edge_id"} & props.keys():
            raise ValueError("Reservierte Identitätsfelder in Quellproperties.")
        if any(v is not None and not isinstance(v, (str, bool, int, float, date, datetime)) for v in props.values()):
            raise ValueError("Nur skalare Quellproperties werden in diesem Paket unterstützt.")


def expected_counts(graph):
    return {"nodes": len(graph["nodes"]), "edges": len(graph["edges"]),
            "labels": dict(Counter(n["label"] for n in graph["nodes"])),
            "types": dict(Counter(e["type"] for e in graph["edges"]))}


@contextmanager
def graph_session():
    from storage_runtime import neo4j_driver, neo4j_database
    with neo4j_driver() as driver:
        with driver.session(database=neo4j_database()) as session:
            yield session


def query_graph(scope, query, **params):
    validate_scope(scope)
    with graph_session() as session:
        return session.execute_read(lambda tx: tx.run(query, scope=scope, **params).data())


def ensure_schema(session):
    # Labels sind bewusst kursspezifisch; vorhandene User-/Post-Schemata bleiben unabhängig.
    session.run("CREATE CONSTRAINT storage_node_scope_id IF NOT EXISTS "
                "FOR (n:StorageNode) REQUIRE (n.scope, n.node_id) IS UNIQUE").consume()


def _delete_scope(tx, scope):
    # DELETE statt eines globalen DETACH DELETE: Fremdverbindungen verhindern den Reset.
    foreign = tx.run("""MATCH (n:StorageNode {scope:$scope})-[r]-(m)
        WHERE NOT m:StorageNode OR coalesce(m.scope,'') <> $scope OR coalesce(r.scope,'') <> $scope
        RETURN count(r) AS n""", scope=scope).single()["n"]
    if foreign:
        raise ValueError("Fremdverbindung im Kursbereich: Import abgebrochen, Bestand bleibt erhalten.")
    tx.run("MATCH (:StorageNode {scope:$scope})-[r {scope:$scope}]->(:StorageNode {scope:$scope}) DELETE r",
           scope=scope).consume()
    tx.run("MATCH (n:StorageNode {scope:$scope}) DELETE n", scope=scope).consume()


def delete_scope(scope):
    validate_scope(scope)
    with graph_session() as session:
        session.execute_write(_delete_scope, scope)


def _counts(tx, scope):
    labels = tx.run("""MATCH (n:StorageNode {scope:$scope})
        UNWIND [l IN labels(n) WHERE l <> 'StorageNode'] AS label
        RETURN label, count(n) AS n""", scope=scope).data()
    types = tx.run("""MATCH (:StorageNode {scope:$scope})-[r {scope:$scope}]->(:StorageNode {scope:$scope})
        RETURN type(r) AS type, count(r) AS n""", scope=scope).data()
    return {"nodes": sum(r["n"] for r in labels), "edges": sum(r["n"] for r in types),
            "labels": {r["label"].removeprefix("Storage"): r["n"] for r in labels},
            "types": {r["type"]: r["n"] for r in types}}


def graph_counts(scope):
    validate_scope(scope)
    with graph_session() as session:
        return session.execute_read(_counts, scope)


def import_snapshot(dataset, scope, include_pairings=True, graph=None):
    validate_scope(scope)
    graph = prepare_graph(dataset) if graph is None else graph
    validate_graph(graph)  # vor dem ersten Schreibzugriff
    selected = {"nodes": graph["nodes"], "edges": [e for e in graph["edges"]
                 if include_pairings or e["type"] != "PORTAL_PAIRS_WITH"]}
    expected = expected_counts(selected)
    def write(tx):
        _delete_scope(tx, scope)
        for label in sorted({n["label"] for n in selected["nodes"]}):
            rows = [n for n in selected["nodes"] if n["label"] == label]
            tx.run(f"""UNWIND $rows AS row
                CREATE (n:StorageNode:{LABELS[label]} {{scope:$scope, node_id:row.node_id}})
                SET n += row.properties""", scope=scope, rows=rows).consume()
        for typ in sorted({e["type"] for e in selected["edges"]}):
            rows = [e for e in selected["edges"] if e["type"] == typ]
            tx.run(f"""UNWIND $rows AS row
                MATCH (a:StorageNode {{scope:$scope, node_id:row.source}})
                MATCH (b:StorageNode {{scope:$scope, node_id:row.target}})
                CREATE (a)-[r:{typ} {{scope:$scope, edge_id:row.edge_id}}]->(b)
                SET r += row.properties""", scope=scope, rows=rows).consume()
        actual = _counts(tx, scope)
        if actual != expected:
            raise ValueError("Importzahlen stimmen nicht; Datentransaktion wird zurückgerollt.")
        return actual
    with graph_session() as session:
        ensure_schema(session)
        return session.execute_write(write)


PAIRING_QUERY = """UNWIND $rows AS row
MATCH (a:StorageNode:StorageCatalogEntry {scope:$scope, node_id:row.source})
MATCH (b:StorageNode:StorageCatalogEntry {scope:$scope, node_id:row.target})
MERGE (a)-[r:PORTAL_PAIRS_WITH {scope:$scope, edge_id:row.edge_id}]->(b)
SET r += row.properties
RETURN count(r) AS processed
"""


def write_pairings(scope, query):
    """Studentisches Cypher ausführen; alle gerichteten Belegkanten vor Commit vergleichen."""
    validate_scope(scope)
    rows = [e for e in prepare_graph("uap")["edges"] if e["type"] == "PORTAL_PAIRS_WITH"]
    expected = {e["edge_id"]: (e["source"], e["target"], e["properties"]) for e in rows}
    def write(tx):
        tx.run(query, scope=scope, rows=rows).consume()
        found = tx.run("""MATCH (a:StorageNode {scope:$scope})-[r:PORTAL_PAIRS_WITH {scope:$scope}]->(b:StorageNode {scope:$scope})
            RETURN a.node_id AS source, b.node_id AS target, properties(r) AS props""", scope=scope).data()
        actual = {}
        for item in found:
            props = dict(item["props"])
            edge_id = props.pop("edge_id")
            props.pop("scope")
            actual[edge_id] = (item["source"], item["target"], props)
        if (len(found) != len(expected) or actual != expected
                or _counts(tx, scope) != expected_counts(prepare_graph("uap"))):
            raise ValueError("Typ, Richtung oder Belegproperties stimmen nicht; Änderung zurückgerollt.")
        return len(found)
    with graph_session() as session:
        return session.execute_write(write)


def two_hop_reference(start_key="DOW-UAP-D077"):
    """Unabhängige JSONL-Referenz, ohne Neo4j und ohne Interpretation als Ereignisgraph."""
    graph = prepare_graph("uap")
    nodes = {n["node_id"]: n for n in graph["nodes"]}
    starts = [n["node_id"] for n in graph["nodes"] if n["properties"].get("source_key") == start_key]
    if len(starts) != 1:
        raise ValueError("Startkürzel ist nicht eindeutig.")
    start = starts[0]
    out = defaultdict(list)
    for edge in graph["edges"]:
        if edge["type"] == "PORTAL_PAIRS_WITH":
            out[edge["source"]].append(edge)
    paths = []
    for first in out[start]:
        for second in out[first["target"]]:
            if second["target"] == start:
                continue
            ids = [start, first["target"], second["target"]]
            paths.append({"node_ids": ids, "source_keys": [nodes[i]["properties"]["source_key"] for i in ids],
                          "edge_ids": [first["edge_id"], second["edge_id"]]})
    return sorted(paths, key=lambda p: (p["source_keys"][-1], p["node_ids"][-1], p["edge_ids"]))


def draw_paths(paths, title):
    """Kleine, exakte Pfadauswahl aus Abfrageergebnissen; keine zusätzliche Bibliothek."""
    import matplotlib.pyplot as plt
    from textwrap import fill
    paths = list(paths)
    if not paths:
        print("Keine Pfade zum Zeichnen.")
        return None
    if len(paths) > 5 or len({len(p) for p in paths}) != 1:
        raise ValueError("Wähle höchstens fünf gleich lange Pfade.")
    layers = [sorted({p[i] for p in paths}) for i in range(len(paths[0]))]
    positions = {(i, name): (i, (len(names)-1)/2-j) for i,names in enumerate(layers) for j,name in enumerate(names)}
    fig, ax = plt.subplots(figsize=(11, max(3.6, 1.2*max(map(len,layers)))))
    links = {(i,p[i],p[i+1]) for p in paths for i in range(len(p)-1)}
    for i,a,b in sorted(links):
        ax.annotate("", xy=positions[(i+1,b)], xytext=positions[(i,a)],
                    arrowprops={"arrowstyle":"-|>", "color":"#608796", "lw":1.7, "shrinkA":60, "shrinkB":60}, zorder=1)
    for (i,name),(x,y) in positions.items():
        ax.text(x,y,fill(str(name),22),ha="center",va="center",fontsize=10,
                bbox={"boxstyle":"round,pad=0.65", "fc":"#E7F2F4", "ec":"#176B87"},zorder=2)
    height=max(map(len,layers))
    ax.set(xlim=(-.45,len(layers)-.55), ylim=(-height/2-.5,height/2+.5),title=title)
    ax.axis("off"); fig.tight_layout(); plt.show()
    return fig
