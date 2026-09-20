"""SQLite-Paket in einer temporären Repo-Kopie prüfen; eigene Arbeitsdaten bleiben erhalten.

Standard: Codezellen ohne Kernelprozess ausführen und unabhängig gegen CSV prüfen.
--kernel: zusätzlich alle drei Notebooks mit echtem Jupyter-Kernel ausführen.
"""
import argparse
from collections import Counter, defaultdict, deque
import contextlib
from copy import deepcopy
import csv
from datetime import date, timedelta
import io
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = (
    "demos/microblogging/01_sqlite.ipynb",
    "tasks/01_sqlite/task.ipynb",
    "tasks/01_sqlite/task_sample_solution.ipynb",
)


def csv_rows(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_results(demo, solution, workspace):
    """Erwartungen separat aus den ursprünglichen CSV-Zeilen berechnen."""
    base = workspace / "data/microblogging/relational"
    rows = {name: csv_rows(base / f"{name}.csv") for name in ("users", "posts", "likes", "comments", "follows")}
    users = {int(r["user_id"]): r for r in rows["users"]}
    posts = {int(r["post_id"]): r for r in rows["posts"]}
    activity = {name: Counter(int(r["user_id"]) for r in rows[name]) for name in ("posts", "likes", "comments")}
    for r in demo["engagement"].to_dict("records"):
        uid = r["user_id"]
        assert r["posts_count"] == activity["posts"][uid]
        assert r["comments_made"] == activity["comments"][uid]
        assert r["likes_made"] == activity["likes"][uid]
        assert r["engagement_score"] == sum(c[uid] for c in activity.values())
    assert set(demo["engagement"]["user_id"]) == set(users)
    likes = Counter(int(r["post_id"]) for r in rows["likes"])
    assert dict(zip(demo["popular_posts"]["post_id"], demo["popular_posts"]["like_count"])) == {pid: likes[pid] for pid in posts}
    incoming = Counter(int(r["dst_user_id"]) for r in rows["follows"])
    outgoing = Counter(int(r["src_user_id"]) for r in rows["follows"])
    for r in demo["degrees"].to_dict("records"):
        assert r["followers"] == incoming[r["user_id"]]
        assert r["following"] == outgoing[r["user_id"]]
    daily = Counter(r["created_at"][:10] for r in rows["posts"])
    start, end = date.fromisoformat(min(daily)), date.fromisoformat(max(daily))
    days = [(start + timedelta(days=i)).isoformat() for i in range((end-start).days+1)]
    assert demo["trend"]["day"].tolist() == days
    for i, r in enumerate(demo["trend"].to_dict("records")):
        window = days[max(0, i-6):i+1]
        assert r["posts"] == daily[r["day"]]
        assert abs(r["rolling_7d"] - sum(daily[d] for d in window)/len(window)) < 1e-10
    parameters = demo["feed_parameters"]
    follows = {int(r["dst_user_id"]) for r in rows["follows"]
               if int(r["src_user_id"]) == parameters["viewer"] and r["since"] <= parameters["since"]}
    expected = [r for r in rows["posts"] if int(r["user_id"]) in follows
                and parameters["since"] <= r["created_at"] < parameters["until"]]
    expected.sort(key=lambda r: int(r["post_id"]))
    expected.sort(key=lambda r: r["created_at"], reverse=True)
    assert demo["feed"]["post_id"].tolist() == [int(r["post_id"]) for r in expected[:50]] == [23,399,204,396]
    adjacency = defaultdict(set)
    for r in rows["follows"]:
        adjacency[int(r["src_user_id"])].add(int(r["dst_user_id"]))
    queue, visited = deque([(1, 0)]), {1}
    while queue:
        node, distance = queue.popleft()
        if node == 3:
            break
        for neighbour in adjacency[node] - visited:
            visited.add(neighbour)
            queue.append((neighbour, distance + 1))
    assert int(demo["path_result"].iloc[0]["depth"]) == distance == 2
    path = [int(s) for s in demo["path_result"].iloc[0]["path"].strip("/").split("/")]
    assert len(set(path)) == len(path) and all(b in adjacency[a] for a,b in zip(path,path[1:]))

    # Alle importierten Spalten prüfen, nicht bloss Zeilenzahlen.
    with solution["connect"](solution["DB_PATH"]) as con:
        source = solution["read_snapshot"]("uap")
        for table, records in source.items():
            columns = list(records[0])
            names = ", ".join(f'"{c}"' for c in columns)
            actual = con.execute(f'SELECT {names} FROM "{table}"').fetchall()
            assert set(actual) == {tuple(r[c] for c in columns) for r in records}
        assert con.execute("SELECT COUNT(*) FROM catalog_entries WHERE source_key='FBI-UAP-D014'").fetchone()[0] == 2
        assert con.execute("SELECT COUNT(*) FROM catalog_entries WHERE annual_eligible=1 AND incident_year>=2020 AND incident_year<2024").fetchone()[0] == 116
        assert con.execute("SELECT COUNT(*) FROM catalog_entries WHERE annual_eligible=0").fetchone()[0] == 83
        before = list(con.iterdump())
        invalid = deepcopy(source)
        invalid["entry_assets"][0]["entry_id"] = "_invalid_entry_for_rollback_test"
        try:
            solution["load_snapshot"](con, "uap", rows=invalid)
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Ungültiger Import wurde akzeptiert.")
        assert list(con.iterdump()) == before, "Ein fehlgeschlagener Import hat den Bestand verändert."
        assert not con.in_transaction

    # Gegenbeispiele: Null-Aktivität, Post ohne Like, fehlender Kalendertag.
    fixture = workspace / "data/work/validation_fixture.sqlite"
    with demo["connect"](fixture) as con:
        demo["create_schema"](con, "microblogging")
        con.executemany("INSERT INTO users VALUES (?, ?, ?)", [(1,"active","2025-01-01"),(2,"quiet","2025-01-01")])
        con.executemany("INSERT INTO posts VALUES (?, ?, ?, ?)", [(1,1,"2025-01-01T00:00:00","one"),(2,1,"2025-01-03T00:00:00","two")])
    quiet = demo["query"](fixture, demo["sql_q1"]).set_index("user_id").loc[2]
    assert quiet["engagement_score"] == 0
    assert demo["query"](fixture, demo["sql_q2"])["like_count"].tolist() == [0, 0]
    gap = demo["query"](fixture, demo["sql_trend"])
    assert gap["posts"].tolist() == [1, 0, 1]
    assert abs(gap.iloc[2]["rolling_7d"] - 2/3) < 1e-10
    # Ein Katalogeintrag ohne Asset: LEFT JOIN erhält ihn, COUNT(asset_id) bleibt null.
    with solution["connect"](solution["DB_PATH"]) as con:
        con.execute("BEGIN")
        try:
            original = con.execute("SELECT entry_id FROM catalog_entries WHERE source_key='DOW-UAP-D079'").fetchone()[0]
            con.execute("DELETE FROM entry_assets WHERE entry_id=?", (original,))
            result = con.execute(solution["sql_dossier"], solution["case_parameters"]).fetchall()
            assert len(result) == 3
            assert next(r[-1] for r in result if r[1] == "DOW-UAP-D079") == 0
        finally:
            con.execute("ROLLBACK")
    return {
        "microblogging_all_q1_q5_against_csv": "passed",
        "bounded_path_against_breadth_first_search": "passed",
        "zero_activity_zero_likes_missing_day": "passed",
        "uap_all_imported_columns": "passed",
        "failed_import_preserves_previous_snapshot": "passed",
        "entry_without_asset_preserved": "passed",
        "date_exclusions_and_cross_model_year_count": "passed",
    }


def run(with_kernel=False):
    os.environ.setdefault("MPLBACKEND", "Agg")
    import nbformat
    import matplotlib.pyplot as plt
    # IPython-Darstellung initialisieren, ohne Kernel oder Netzwerkports zu öffnen.
    from IPython.core.interactiveshell import InteractiveShell
    InteractiveShell.instance()
    original_cwd = Path.cwd()
    original_path = list(sys.path)
    report = {"mode": "sequential_python_code_cells_without_jupyter_kernel", "notebooks": {},
              "jupyter_kernel": "not_requested", "sqlite_version": sqlite3.sqlite_version}
    with tempfile.TemporaryDirectory(prefix="storage_sqlite_validation_") as tmp:
        workspace = Path(tmp) / "rothstein-storage-workshop-2026"
        # Nur die für dieses Paket benötigten Dateien kopieren, keine eigenen DBs.
        for directory in ("scripts", "schemas/sqlite", "data/input/relational", "data/microblogging/relational"):
            shutil.copytree(ROOT / directory, workspace / directory,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for filename in NOTEBOOKS:
            dest = workspace / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / filename, dest)
        namespaces = {}
        saved_module = sys.modules.pop("sqlite_workshop", None)
        try:
            for filename in NOTEBOOKS:
                book = nbformat.read(workspace / filename, as_version=4)
                nbformat.validate(book)
                assert all(c.get("execution_count") is None and not c.get("outputs")
                           for c in book.cells if c.cell_type == "code"), "Notebook enthält gespeicherte Ausgaben."
                for repetition in range(2):
                    os.chdir((workspace / filename).parent)
                    ns = {"__name__": "__main__"}
                    with contextlib.redirect_stdout(io.StringIO()):
                        for i, cell in enumerate(book.cells):
                            if cell.cell_type == "code":
                                exec(compile(cell.source, f"{filename}:cell{i+1}", "exec"), ns)
                    plt.close("all")
                namespaces[filename] = ns
                report["notebooks"][filename] = {"code_cells": sum(c.cell_type == "code" for c in book.cells), "runs":2, "status":"passed"}
            student = namespaces[NOTEBOOKS[1]]
            assert not student["ready"] and not student["completed"] and not student["DB_PATH"].exists()
            report["untouched_task_reports_open"] = "passed"
            report["checks"] = check_results(namespaces[NOTEBOOKS[0]], namespaces[NOTEBOOKS[2]], workspace)
            if with_kernel:
                from nbclient import NotebookClient
                executed_dir = ROOT / "data/work/sqlite_execution"
                executed_dir.mkdir(parents=True, exist_ok=True)
                # Den für den kopflosen Codezellentest gesetzten Backend-Wert
                # nicht an neue Notebook-Kernel vererben.
                backend = os.environ.pop("MPLBACKEND", None)
                try:
                    for filename in NOTEBOOKS:
                        notebook = nbformat.read(workspace / filename, as_version=4)
                        NotebookClient(notebook, timeout=180, kernel_name="rothstein-storage-workshop-2026",
                                       resources={"metadata":{"path":str((workspace / filename).parent)}}).execute()
                        name = "microblogging_01_sqlite.ipynb" if filename == NOTEBOOKS[0] else Path(filename).name
                        nbformat.write(notebook, executed_dir / name)
                finally:
                    if backend is not None:
                        os.environ["MPLBACKEND"] = backend
                report["jupyter_kernel"] = "passed"
        finally:
            os.chdir(original_cwd)
            sys.path[:] = original_path
            sys.modules.pop("sqlite_workshop", None)
            if saved_module is not None:
                sys.modules["sqlite_workshop"] = saved_module
    report["status"] = "passed"
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", action="store_true", help="Zusätzlich echten Jupyter-Kernel starten.")
    parser.add_argument("--report", type=Path, help="JSON-Prüfbericht speichern.")
    args = parser.parse_args()
    result = run(args.kernel)
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    print(output)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
