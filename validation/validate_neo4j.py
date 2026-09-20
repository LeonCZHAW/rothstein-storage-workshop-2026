"""Neo4j-Paket prüfen: offline oder mit --server [--kernel].

Server-/Kerneltests verwenden zufällige, eigene Kursbereiche. Es wird keine
vorhandene Demo oder Aufgabe zurückgesetzt. --server benötigt echtes Neo4j.
"""
import argparse
import ast
from collections import Counter, defaultdict, deque
import contextlib
from copy import deepcopy
import csv
from datetime import datetime, timedelta, timezone
import io
import json
import os
from pathlib import Path
import sys
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from neo4j_workshop import (prepare_graph, validate_graph, graph_scope, expected_counts,
    two_hop_reference, graph_session, graph_counts, query_graph, delete_scope,
    import_snapshot, write_pairings, PAIRING_QUERY, _delete_scope)

NOTEBOOKS=("demos/microblogging/03_neo4j.ipynb", "tasks/03_neo4j/task.ipynb",
           "tasks/03_neo4j/task_sample_solution.ipynb")


def read_csv(relative):
    with (ROOT/relative).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))


def execute_notebook(path,server):
    import nbformat
    import matplotlib.pyplot as plt
    book=nbformat.read(path,as_version=4)
    nbformat.validate(book)
    ns={"__name__":"__main__"}
    executed=skipped=0
    with contextlib.redirect_stdout(io.StringIO()):
        for i,cell in enumerate(book.cells):
            if cell.cell_type!="code":continue
            if cell.outputs or cell.execution_count is not None:
                raise AssertionError("Auslieferungsnotebook enthält gespeicherte Ausgaben.")
            ast.parse(cell.source)
            if "neo4j-server" in cell.metadata.get("tags",[]) and not server:
                skipped+=1;continue
            exec(compile(cell.source,f"{path.name}:cell{i+1}","exec"),ns)
            executed+=1
    plt.close("all")
    return ns,{"executed_code_cells":executed,"skipped_server_cells":skipped}


def offline_checks(demo,student,solution):
    micro=prepare_graph("microblogging");uap=prepare_graph("uap")
    assert expected_counts(micro)=={"nodes":1065,"edges":5690,"labels":{"User":200,"Post":865},
        "types":{"FOLLOWS":3047,"AUTHORED":865,"LIKES":1266,"COMMENTED":512}}
    assert expected_counts(uap)=={"nodes":764,"edges":1483,
        "labels":{"Agency":10,"Asset":374,"CatalogEntry":375,"Release":5},
        "types":{"CATALOG_AGENCY":375,"LINKS_ASSET":397,"IN_RELEASE":375,"PORTAL_PAIRS_WITH":336}}
    # Vergleich mit dem separaten Original-Graphformat, einschliesslich Mehrfachkommentaren.
    old=read_csv("data/microblogging/graph/edges.csv")
    assert Counter((e["src"],e["dst"],e["type"]) for e in old)==Counter(
        (e["source"],e["target"],e["type"]) for e in micro["edges"])
    comments=read_csv("data/microblogging/relational/comments.csv")
    edges={e["properties"]["comment_id"]:e for e in micro["edges"] if e["type"]=="COMMENTED"}
    for c in comments:
        edge=edges[int(c["comment_id"])]
        assert edge["source"]==f"user:{c['user_id']}" and edge["target"]==f"post:{c['post_id']}"
        assert edge["properties"]["text"]==c["text"]
        assert edge["properties"]["at"].replace(tzinfo=None)==datetime.fromisoformat(c["created_at"])
    multiplicities=Counter((c["user_id"],c["post_id"]) for c in comments)
    assert sum(v-1 for v in multiplicities.values())==3
    for change in ("duplicate_node","missing_endpoint"):
        bad=deepcopy(uap)
        if change=="duplicate_node":bad["nodes"].append(bad["nodes"][0])
        else:bad["edges"][0]["target"]="missing"
        try:validate_graph(bad)
        except ValueError:pass
        else:raise AssertionError(change)
    assert student["SCOPE"]!=solution["SCOPE"]!=demo["SCOPE"]
    assert "__TYP__" in student["pairing_query"] and "__PFADMUSTER__" in student["query_two_hop"]
    assert "__" not in solution["pairing_query"] and "__" not in solution["query_two_hop"]
    # Referenzen zusätzlich über die eigenständige relationale Pairing-Datei ermitteln.
    raw_pairs=read_csv("data/input/relational/portal_pairings.csv")
    raw_entries=read_csv("data/input/relational/catalog_entries.csv")
    by_id={r["entry_id"]:r for r in raw_entries}
    out=defaultdict(list)
    for r in raw_pairs:out[r["source_entry_id"]].append(r)
    references={}
    for key in ("DOW-UAP-D077","DOW-UAP-D080"):
        sid=next(r["entry_id"] for r in raw_entries if r["source_key"]==key)
        paths=[]
        for a in out[sid]:
            for b in out[a["target_entry_id"]]:
                if b["target_entry_id"]!=sid:
                    ids=[sid,a["target_entry_id"],b["target_entry_id"]]
                    paths.append({"node_ids":ids,"source_keys":[by_id[i]["source_key"] for i in ids],
                                  "edge_ids":[a["pairing_id"],b["pairing_id"]]})
        paths.sort(key=lambda p:(p["source_keys"][-1],p["node_ids"][-1],p["edge_ids"]))
        assert paths==two_hop_reference(key)
        references[key]={"paths":len(paths),"targets":len({p["node_ids"][-1] for p in paths})}
    assert references=={"DOW-UAP-D077":{"paths":17,"targets":17},"DOW-UAP-D080":{"paths":24,"targets":18}}
    gap=demo["complete_calendar"]([{"day":"2025-01-01","posts":1},{"day":"2025-01-03","posts":1}])
    assert gap["posts"].tolist()==[1,0,1] and abs(gap.iloc[2]["rolling_7d"]-2/3)<1e-10
    return {"input_counts": {"microblogging":expected_counts(micro),"uap":expected_counts(uap)},
        "original_graph_topology_preserved":"passed","all_comment_ids_texts_timestamps":"passed",
        "three_repeated_user_post_comments_preserved":"passed",
        "invalid_ids_and_endpoints_rejected":"passed","task_solution_scopes_and_todos":"passed",
        "uap_paths_against_relational_input":references,"pandas_calendar_gap":"passed",
        "cypher_execution":"not_checked_offline"}


def server_checks(demo,student,solution):
    users=read_csv("data/microblogging/relational/users.csv")
    posts=read_csv("data/microblogging/relational/posts.csv")
    comments=read_csv("data/microblogging/relational/comments.csv")
    likes=read_csv("data/microblogging/relational/likes.csv")
    follows=read_csv("data/microblogging/relational/follows.csv")
    counts=[Counter(int(r["user_id"]) for r in data) for data in (posts,comments,likes)]
    assert set(demo["engagement"]["user_id"])=={int(r["user_id"]) for r in users}
    for r in demo["engagement"].to_dict("records"):
        assert [r[k] for k in ("posts_count","comments_made","likes_made")]==[c[r["user_id"]] for c in counts]
    by_post=Counter(int(r["post_id"]) for r in likes)
    assert dict(zip(demo["popular_posts"]["post_id"],demo["popular_posts"]["like_count"]))=={int(p["post_id"]):by_post[int(p["post_id"])] for p in posts}
    inc=Counter(int(f["dst_user_id"]) for f in follows);out=Counter(int(f["src_user_id"]) for f in follows)
    for row in demo["degrees"].to_dict("records"):
        assert row["followers"]==inc[row["user_id"]] and row["following"]==out[row["user_id"]]
    adjacency=defaultdict(set)
    for f in follows:adjacency[int(f["src_user_id"])].add(int(f["dst_user_id"]))
    queue=deque([[1]]);seen={1};expected_path=None
    while queue:
        p=queue.popleft()
        if p[-1]==3:expected_path=p;break
        for dst in sorted(adjacency[p[-1]]-seen):seen.add(dst);queue.append(p+[dst])
    assert demo["path_rows"]==[{"hops":len(expected_path)-1,"user_ids":expected_path}]
    day_counts=Counter(datetime.fromisoformat(p["created_at"]).date() for p in posts)
    days=[min(day_counts)+timedelta(days=i) for i in range((max(day_counts)-min(day_counts)).days+1)]
    for i,row in enumerate(demo["trend"].to_dict("records")):
        window=days[max(0,i-6):i+1]
        assert row["day"].date()==days[i] and row["posts"]==day_counts[days[i]]
        assert abs(row["rolling_7d"]-sum(day_counts[d] for d in window)/len(window))<1e-10
    authors={int(f["dst_user_id"]) for f in follows if int(f["src_user_id"])==1 and f["since"]<=demo["since"].date().isoformat()}
    feed=[p for p in posts if int(p["user_id"]) in authors and demo["since"]<=datetime.fromisoformat(p["created_at"]).replace(tzinfo=timezone.utc)<demo["until"]]
    feed.sort(key=lambda p:int(p["post_id"]));feed.sort(key=lambda p:p["created_at"],reverse=True)
    assert demo["feed"]["post_id"].tolist()==[int(p["post_id"]) for p in feed[:50]]
    assert solution["paths"]==two_hop_reference()
    assert student["completed"]=={"Grundimport"}
    assert solution["completed"]=={"Grundimport","Portalverweise","Pfadabfrage","Belegprüfung"}
    assert graph_counts(student["SCOPE"])["edges"]==1147
    assert graph_counts(solution["SCOPE"])["edges"]==1483
    # Ein inaktiver Nutzer muss null Aktivitäten und null Follows erhalten.
    with graph_session() as session:
        session.run("CREATE (:StorageNode:StorageUser {scope:$scope,node_id:'user:99999',user_id:99999,username:'quiet_probe'})",
                    scope=demo["SCOPE"]).consume()
    quiet=next(r for r in query_graph(demo["SCOPE"],demo["query_q1"]) if r["user_id"]==99999)
    assert quiet["engagement_score"]==0
    quiet_degree=next(r for r in query_graph(demo["SCOPE"],demo["query_degrees"]) if r["user_id"]==99999)
    assert quiet_degree["followers"]==quiet_degree["following"]==0
    # Rollen bleiben getrennt; ein bewusst abgebrochener Reset muss atomar sein.
    before=graph_counts(solution["SCOPE"])
    def abort(tx):
        _delete_scope(tx,solution["SCOPE"])
        raise RuntimeError("intentional_rollback_probe")
    with graph_session() as session:
        try:session.execute_write(abort)
        except RuntimeError as error:assert str(error)=="intentional_rollback_probe"
        else:raise AssertionError("Rollbackprobe hat nicht abgebrochen.")
    assert graph_counts(solution["SCOPE"])==before
    # Falsch gerichtete Schülerabfrage wird zurückgerollt.
    reversed_query=PAIRING_QUERY.replace("MERGE (a)-[r:","MERGE (b)-[r:").replace("]->(b)","]->(a)")
    try:write_pairings(student["SCOPE"],reversed_query)
    except ValueError:pass
    else:raise AssertionError("Falsche Richtung akzeptiert")
    assert graph_counts(student["SCOPE"])["edges"]==1147
    assert write_pairings(student["SCOPE"],PAIRING_QUERY)==336
    assert write_pairings(student["SCOPE"],PAIRING_QUERY)==336
    assert graph_counts(solution["SCOPE"])==before
    return {"all_five_queries_against_csv":"passed","inactive_user_optional_match":"passed",
            "comment_multiplicity":"passed","uap_paths_and_evidence":"passed",
            "isolated_reimports":"passed","transaction_rollback":"passed",
            "wrong_direction_rollback":"passed"}


def run(server=False,kernel=False):
    os.environ.setdefault("MPLBACKEND","Agg")
    from IPython.core.interactiveshell import InteractiveShell
    InteractiveShell.instance()
    previous=Path.cwd();old_token=os.environ.get("STORAGE_NEO4J_TEST_TOKEN")
    os.environ["STORAGE_NEO4J_TEST_TOKEN"]=uuid4().hex
    report={"server":"not_run","jupyter_kernel":"not_run","notebooks":{}}
    try:
        namespaces=[]
        for relative in NOTEBOOKS:
            path=ROOT/relative;os.chdir(path.parent)
            for _ in range(2):ns,detail=execute_notebook(path,server)
            namespaces.append(ns);report["notebooks"][relative]={**detail,"runs":2}
        report["offline_checks"]=offline_checks(*namespaces)
        if server:
            report["server_checks"]=server_checks(*namespaces)
            with graph_session() as session:
                report["server_version"]=session.run("CALL dbms.components() YIELD versions RETURN versions[0] AS version").single()["version"]
            report["server"]="passed"
        if kernel:
            import nbformat
            from nbclient import NotebookClient
            output=ROOT/"data/work/neo4j_execution";output.mkdir(parents=True,exist_ok=True)
            backend=os.environ.pop("MPLBACKEND",None)
            try:
                for relative in NOTEBOOKS:
                    path=ROOT/relative;book=nbformat.read(path,as_version=4)
                    NotebookClient(book,timeout=180,kernel_name="rothstein-storage-workshop-2026",
                        resources={"metadata":{"path":str(path.parent)}}).execute()
                    name="microblogging_03_neo4j.ipynb" if relative==NOTEBOOKS[0] else path.name
                    nbformat.write(book,output/name)
            finally:
                if backend is not None:os.environ["MPLBACKEND"]=backend
            report["jupyter_kernel"]="passed"
        report["status"]="passed" if server else "offline_checks_passed_server_not_tested"
        return report
    finally:
        os.chdir(previous)
        try:
            if server:
                for scope in [graph_scope("microblogging"),graph_scope("uap"),graph_scope("uap",True)]:delete_scope(scope)
        finally:
            if old_token is None:os.environ.pop("STORAGE_NEO4J_TEST_TOKEN",None)
            else:os.environ["STORAGE_NEO4J_TEST_TOKEN"]=old_token


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server",action="store_true")
    parser.add_argument("--kernel",action="store_true")
    parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    if args.kernel and not args.server:parser.error("--kernel benötigt --server")
    result=run(args.server,args.kernel)
    text=json.dumps(result,ensure_ascii=False,indent=2)+"\n";print(text)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(text,encoding="utf-8")
