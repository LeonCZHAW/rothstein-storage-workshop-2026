"""MongoDB-Paket prüfen. Ohne --server: Vorbereitung, BSON, Referenzen und Syntax.

--server führt alle Notebook-Codezellen gegen echte MongoDB-Collections aus.
--server --kernel ergänzt einen echten Jupyter-Durchlauf. Prüf-Collections liegen
mit zufälligem Präfix ausschliesslich in storage_setup und werden gezielt entfernt.
"""
import argparse
import ast
from collections import Counter, defaultdict, deque
import contextlib
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import io
import json
import os
from pathlib import Path
import sys
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[1]
NOTEBOOKS=("demos/microblogging/02_mongodb.ipynb","tasks/02_mongodb/task.ipynb","tasks/02_mongodb/task_sample_solution.ipynb")
sys.path.insert(0,str(ROOT/"scripts"))
from bson import BSON
from bson.codec_options import CodecOptions
from pymongo.errors import BulkWriteError
from mongodb_workshop import (prepare_documents, validate_batch, validate_note, jsonl,
                               mongo_workspace, sync_collection)


def execute_notebook(path, server):
    import nbformat
    import matplotlib.pyplot as plt
    book=nbformat.read(path,as_version=4)
    nbformat.validate(book)
    namespace={"__name__":"__main__"}
    executed=skipped=0
    with contextlib.redirect_stdout(io.StringIO()):
        for i,cell in enumerate(book.cells):
            if cell.cell_type != "code":
                continue
            assert not cell.outputs and cell.execution_count is None
            ast.parse(cell.source)
            is_server="mongodb-server" in cell.metadata.get("tags",[])
            if is_server and not server:
                skipped+=1
                continue
            exec(compile(cell.source,f"{path.name}:cell{i+1}","exec"),namespace)
            executed+=1
    plt.close("all")
    return namespace,{"executed_code_cells":executed,"skipped_server_cells":skipped}


def offline_checks(demo,student,solution):
    options=CodecOptions(tz_aware=True,tzinfo=timezone.utc)
    batches={kind:prepare_documents(kind) for kind in ("microblogging","uap")}
    for batch in batches.values():
        for documents in batch.values():
            for document in documents:
                assert BSON(BSON.encode(document)).decode(codec_options=options)==document
    raw=jsonl(ROOT/"data/input/document/catalog_documents.jsonl")
    prepared=batches["uap"]["catalog"]
    assert len(prepared)==375
    for a,b in zip(raw,prepared):
        copy=deepcopy(b);assert copy.pop("_id")==a["entry_id"] and copy==a
    assert len({a["asset_id"] for d in raw for a in d["assets"]})==374
    assert sum(len(d["assets"]) for d in raw)==397
    assert sum(d["source_key"]=="FBI-UAP-D014" for d in raw)==2
    paired=[d for d in raw if "PDF Pairing" in d["source_metadata"]]
    assert len(paired)==111
    assert Counter(d["media_type"] for d in paired)=={"PDF":62,"VID":25,"IMG":24}
    assert sum(d["incident_year"] is not None and d["annual_eligible"] and 2020<=d["incident_year"]<2024 for d in raw)==116
    micro=batches["microblogging"]
    assert sum(len(p["comments"]) for p in micro["posts"])==512
    assert len({c["comment_id"] for p in micro["posts"] for c in p["comments"]})==512
    # Das Eingabeformat ist unverändert; naive Originaldaten erhalten nur hier die UTC-Konvention.
    assert all(p["created_at"].tzinfo is not None for p in micro["posts"])
    invalid=deepcopy(prepared[:2]);invalid[1]["_id"]=invalid[0]["_id"]
    try:
        validate_batch(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("Doppelte _id wurde nicht erkannt.")
    note=solution["reading_note"]
    validate_note(note,solution["source"])
    bad_note=deepcopy(note);bad_note["review"]["evidence"]["pdf_pages"]="5"
    try:
        validate_note(bad_note,solution["source"])
    except ValueError:
        pass
    else:
        raise AssertionError("Seitenzahltyp wurde nicht geprüft.")
    assert student["reading_note"] is None and student["pairing_filter"] is None and student["pipeline_media"] is None
    assert student["names"]["catalog"] != solution["names"]["catalog"]
    for ns in (demo,solution):
        for name,value in ns.items():
            if name.startswith("pipeline_") and isinstance(value,list):
                BSON.encode({"pipeline":value})  # Nur Serialisierbarkeit, KEIN MongoDB-Ausführungsnachweis.
    authors=sorted({d["dst_user_id"] for d in micro["follows"] if d["src_user_id"]==1 and d["since"]<=demo["since"]})
    BSON.encode({"pipeline":demo["feed_pipeline"](authors)})
    gap=demo["complete_calendar"]([{"day":datetime(2025,1,1,tzinfo=timezone.utc),"posts":1},
                                    {"day":datetime(2025,1,3,tzinfo=timezone.utc),"posts":1}])
    assert gap["posts"].tolist()==[1,0,1] and abs(gap.iloc[2]["rolling_7d"]-2/3)<1e-10
    return {"prepared_documents_bson_roundtrip":"passed","original_uap_fields_preserved":"passed",
            "duplicate_ids_rejected_before_write":"passed","embedded_comments_preserved":"passed",
            "manual_note_structure_and_bad_page_type":"passed","independent_task_and_solution_collections":"passed",
            "query_definitions":"python_syntax_and_bson_only","pandas_calendar_gap":"passed",
            "reference_counts":{"catalog_entries":375,"asset_links":397,"distinct_assets":374,
                                "with_pdf_pairing_field":111,"without_pdf_pairing_field":264,
                                "filtered_media_counts":{"PDF":62,"VID":25,"IMG":24}}}


def server_checks(demo,student,solution,token):
    micro=prepare_documents("microblogging")
    post_counts=Counter(p["author_id"] for p in micro["posts"])
    comment_counts=Counter(c["user_id"] for p in micro["posts"] for c in p["comments"])
    like_counts=Counter(l["user_id"] for l in micro["likes"])
    likes_by_post=Counter(l["post_id"] for l in micro["likes"])
    for r in demo["engagement"].to_dict("records"):
        uid=r["user_id"]
        assert (r["posts_count"],r["comments_made"],r["likes_made"])==(post_counts[uid],comment_counts[uid],like_counts[uid])
    assert set(demo["engagement"]["user_id"])=={u["user_id"] for u in micro["users"]}
    assert dict(zip(demo["popular_posts"]["post_id"],demo["popular_posts"]["like_count"]))=={p["_id"]:likes_by_post[p["_id"]] for p in micro["posts"]}
    incoming=Counter(f["dst_user_id"] for f in micro["follows"])
    outgoing=Counter(f["src_user_id"] for f in micro["follows"])
    for r in demo["degrees"].to_dict("records"):
        assert r["followers"]==incoming[r["user_id"]] and r["following"]==outgoing[r["user_id"]]
    adjacency=defaultdict(set)
    for f in micro["follows"]:adjacency[f["src_user_id"]].add(f["dst_user_id"])
    queue,seen=deque([(1,0)]),{1}
    while queue:
        node,dist=queue.popleft()
        if node==3:break
        for v in adjacency[node]-seen:
            seen.add(v);queue.append((v,dist+1))
    assert demo["distance"]==[{"hops":dist}]
    daily=Counter(p["created_at"].date() for p in micro["posts"])
    days=[min(daily)+timedelta(days=i) for i in range((max(daily)-min(daily)).days+1)]
    for i,r in enumerate(demo["trend"].to_dict("records")):
        assert r["day"].date()==days[i] and r["posts"]==daily[days[i]]
        window=days[max(0,i-6):i+1]
        assert abs(r["rolling_7d"]-sum(daily[d] for d in window)/len(window))<1e-10
    authors={f["dst_user_id"] for f in micro["follows"] if f["src_user_id"]==1 and f["since"]<=demo["since"]}
    expected=[p for p in micro["posts"] if p["author_id"] in authors and demo["since"]<=p["created_at"]<demo["until"]]
    expected.sort(key=lambda d:d["_id"]);expected.sort(key=lambda d:d["created_at"],reverse=True)
    assert demo["feed"]["post_id"].tolist()==[p["_id"] for p in expected[:50]]
    assert student["completed"]=={"Import"}
    assert solution["completed"]=={"Import","Lesernotiz","Optionales Quellfeld","Aggregation"}
    with mongo_workspace("uap",True) as (db,names):
        before=db[names["reading_notes"]].find_one({"_id":solution["reading_note"]["_id"]})
        solution["import_snapshot"](db,names,"uap")
        assert db[names["reading_notes"]].find_one({"_id":before["_id"]})==before
        actual={d["_id"]:d for d in db[names["catalog"]].find({})}
        assert actual=={d["_id"]:d for d in prepare_documents("uap")["catalog"]}
        fixture=db[f"_mongodb_{token}_semantics"]
        fixture.insert_many([{"_id":1},{"_id":2,"optional":None},{"_id":3,"optional":"x"},
            {"_id":4,"assets":[{"locator_type":"url","format_hint":"img"},{"locator_type":"dvids_video_id","format_hint":"pdf"}]}])
        assert fixture.count_documents({"optional":{"$exists":True}})==2
        assert fixture.count_documents({"optional":{"$exists":False}})==2
        assert fixture.count_documents({"assets.locator_type":"url","assets.format_hint":"pdf"})==1
        assert fixture.count_documents(solution["pdf_asset_filter"])==0
        recovery=db.create_collection(f"_mongodb_{token}_recovery",validator={"value":{"$type":"int"}})
        sync_collection(recovery,[{"_id":1,"value":0},{"_id":2,"value":0}])
        try:
            sync_collection(recovery,[{"_id":1,"value":1},{"_id":2,"value":"invalid"}])
        except BulkWriteError:
            pass
        else:
            raise AssertionError("Fehlerhafter Server-Import wurde akzeptiert.")
        assert recovery.find_one({"_id":1})["value"]==1 and recovery.find_one({"_id":2})["value"]==0
        sync_collection(recovery,[{"_id":1,"value":2},{"_id":2,"value":2}])
        assert all(d["value"]==2 for d in recovery.find({}))
    # Inaktive Person / Post ohne Kommentare und Likes in separaten Collections.
    with mongo_workspace("microblogging") as (db,names):
        db[names["users"]].insert_one({"_id":99999,"user_id":99999,"username":"quiet_probe"})
        quiet=next(d for d in db[names["users"]].aggregate(demo["pipeline_q1"]) if d["user_id"]==99999)
        assert quiet["engagement_score"]==0
    return {"all_q1_q5_results_against_inputs":"passed","zero_activity_user":"passed",
            "all_catalog_document_values":"passed","notes_survive_reimport":"passed",
            "exists_null_missing_and_elemMatch_counterexample":"passed",
            "server_schema_validation":"passed","partial_import_and_repeat_recovery":"passed"}


def run(server=False,kernel=False):
    os.environ.setdefault("MPLBACKEND","Agg")
    from IPython.core.interactiveshell import InteractiveShell
    InteractiveShell.instance()
    import nbformat
    previous_cwd=Path.cwd()
    previous_token=os.environ.get("STORAGE_MONGO_TEST_TOKEN")
    token=uuid4().hex
    os.environ["STORAGE_MONGO_TEST_TOKEN"]=token
    report={"server":"not_run","jupyter_kernel":"not_run","notebooks":{}}
    try:
        namespaces=[]
        for relative in NOTEBOOKS:
            path=ROOT/relative
            os.chdir(path.parent)
            for _ in range(2):ns,details=execute_notebook(path,server)
            namespaces.append(ns)
            report["notebooks"][relative]={**details,"runs":2}
        report["offline_checks"]=offline_checks(*namespaces)
        if server:
            report["server_checks"]=server_checks(*namespaces,token)
            report["server"]="passed"
        if kernel:
            from nbclient import NotebookClient
            output=ROOT/"data/work/mongodb_execution";output.mkdir(parents=True,exist_ok=True)
            backend=os.environ.pop("MPLBACKEND",None)
            try:
                for relative in NOTEBOOKS:
                    path=ROOT/relative;book=nbformat.read(path,as_version=4)
                    NotebookClient(book,timeout=180,kernel_name="rothstein-storage-workshop-2026",
                        resources={"metadata":{"path":str(path.parent)}}).execute()
                    name="microblogging_02_mongodb.ipynb" if relative==NOTEBOOKS[0] else path.name
                    nbformat.write(book,output/name)
            finally:
                if backend is not None:os.environ["MPLBACKEND"]=backend
            report["jupyter_kernel"]="passed"
        report["status"]="passed" if server else "offline_checks_passed_server_not_tested"
    finally:
        os.chdir(previous_cwd)
        try:
            if server:
                with mongo_workspace("uap") as (db,_):
                    for name in db.list_collection_names():
                        if name.startswith(f"_mongodb_{token}_"):db.drop_collection(name)
        finally:
            if previous_token is None:os.environ.pop("STORAGE_MONGO_TEST_TOKEN",None)
            else:os.environ["STORAGE_MONGO_TEST_TOKEN"]=previous_token
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server",action="store_true")
    parser.add_argument("--kernel",action="store_true")
    parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    if args.kernel and not args.server:parser.error("--kernel benötigt --server")
    result=run(args.server,args.kernel)
    text=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    print(text)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(text,encoding="utf-8")
