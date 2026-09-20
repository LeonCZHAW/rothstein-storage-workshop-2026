"""TinyFlux-Material prüfen, optional mit echtem Jupyter-Kernel (--kernel).

Alle Datenbankzugriffe liegen in einem temporären Verzeichnis. Ausgeführte
Notebook-Kopien des Kerneltests werden unter data/work/tinyflux_execution abgelegt.
"""
import argparse
import ast
from collections import Counter, defaultdict, deque
import contextlib
import csv
from datetime import datetime, timedelta, timezone
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from tinyflux_workshop import (annual_inputs, annual_point, prepare_points, replace_snapshot,
    search_points, point_signature, database_path, daily_posts, points_frame, parse_time)
from tinyflux import Point, TinyFlux, TimeQuery, TagQuery, FieldQuery

NOTEBOOKS = ("demos/microblogging/04_tinyflux.ipynb", "tasks/04_tinyflux/task.ipynb",
             "tasks/04_tinyflux/task_sample_solution.ipynb")

def read_csv(relative):
    with (ROOT / relative).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def execute(path):
    import nbformat
    import matplotlib.pyplot as plt
    book = nbformat.read(path, as_version=4)
    nbformat.validate(book)
    ns = {"__name__": "__main__"}
    count = 0
    with contextlib.redirect_stdout(io.StringIO()):
        for i, cell in enumerate(book.cells):
            if cell.cell_type != "code": continue
            assert not cell.outputs and cell.execution_count is None, "Gespeicherte Ausgaben im Lieferstand"
            ast.parse(cell.source)
            exec(compile(cell.source, f"{path.name}:cell{i+1}", "exec"), ns)
            count += 1
    plt.close("all")
    return ns, count

def check_results(demo, task, solution):
    # Unabhängige Kennzahlen aus den Detail-CSV-Dateien, ohne Notebook-Hilfsaggregation.
    posts, likes, comments, follows, users = [read_csv(f"data/microblogging/relational/{n}.csv")
        for n in ["posts", "likes", "comments", "follows", "users"]]
    scores = Counter()
    for row in posts + likes + comments: scores[int(row["user_id"])] += 1
    expected_rank = sorted(((int(u["user_id"]), scores[int(u["user_id"])]) for u in users),
                           key=lambda pair: (-pair[1], pair[0]))
    assert list(demo["q1"][["user_id", "engagement_score"]].itertuples(index=False, name=None)) == expected_rank
    received = Counter(int(row["post_id"]) for row in likes)
    assert dict(demo["q2"][["post_id", "like_count"]].itertuples(index=False, name=None)) == {
        int(p["post_id"]): received[int(p["post_id"])] for p in posts}
    outdegree = Counter(int(r["src_user_id"]) for r in follows)
    indegree = Counter(int(r["dst_user_id"]) for r in follows)
    for row in demo["q3_degrees"].itertuples():
        assert (row.following, row.followers) == (outdegree[row.user_id], indegree[row.user_id])
    graph = defaultdict(set)
    for f in follows: graph[int(f["src_user_id"])].add(int(f["dst_user_id"]))
    queue, visited = deque([[1]]), {1}
    while queue:
        path = queue.popleft()
        if path[-1] == 3: break
        for target in sorted(graph[path[-1]]):
            if target not in visited:
                visited.add(target); queue.append(path + [target])
    assert demo["q3_path"] == path == [1, 2, 3]
    daily = Counter(p["created_at"][:10] for p in posts)
    for i, row in enumerate(demo["q4"].itertuples()):
        assert row.posts == daily[row.day.date().isoformat()]
        values = [daily[(row.day - timedelta(days=k)).date().isoformat()] for k in range(min(i+1, 7))]
        assert abs(row.rolling_7d - sum(values)/len(values)) < 1e-10
    # Ein echtes Kalenderloch muss als Nulltag in das gleitende Fenster eingehen.
    gap = points_frame([Point(time=datetime(2025, 1, d, tzinfo=timezone.utc), fields={"value": 1}) for d in [1, 3]])
    gap_result = daily_posts(gap)
    assert gap_result["posts"].tolist() == [1, 0, 1]
    assert abs(gap_result["rolling_7d"].iloc[-1] - 2/3) < 1e-10
    since, until = datetime(2025, 9, 8, tzinfo=timezone.utc), datetime(2025, 9, 11, tzinfo=timezone.utc)
    followed = {int(f["dst_user_id"]) for f in follows if int(f["src_user_id"]) == 1 and parse_time(f["since"]) <= since}
    feed = sorted([p for p in posts if int(p["user_id"]) in followed and since <= parse_time(p["created_at"]) < until],
                  key=lambda p: (-parse_time(p["created_at"]).timestamp(), int(p["post_id"])))[:50]
    assert demo["q5"]["post_id"].tolist() == [int(p["post_id"]) for p in feed] == [23, 399, 204, 396]
    active_by_day = defaultdict(set)
    for row in posts + likes + comments: active_by_day[row["created_at"][:10]].add(int(row["user_id"]))
    for day, row in demo["dau"].iterrows(): assert row["dau"] == len(active_by_day[day.date().isoformat()])
    # Die alte Tagesübersicht stimmt innerhalb ihres Fensters in allen Zellen überein.
    detail = Counter((r["user_id"], r["created_at"][:10], name) for name, rows in
                     [("posts", posts), ("likes", likes), ("comments", comments)] for r in rows)
    old = read_csv("data/microblogging/timeseries/daily_activity.csv")
    for row in old:
        for name in ["posts", "likes", "comments"]:
            assert int(row[name]) == detail[(row["user_id"], row["day"], name)]
    last_day = max(row["day"] for row in old)
    assert [sum(r["created_at"][:10] > last_day for r in rows) for rows in [posts, likes, comments]] == [0, 19, 18]
    assert not task["model_ready"] and task["annual_query"] is None and task["window_total"] is None
    assert solution["model_ready"] and solution["window_total"] == 25
    # Jahreswerte aus dem Detailkatalog herleiten, nicht aus dem gespeicherten Zählfeld.
    catalog = read_csv("data/input/relational/catalog_entries.csv")
    eligible = [r for r in catalog if r["annual_eligible"] == "True"]
    assert len(eligible) == 292 and len(catalog) - len(eligible) == 83
    counts = Counter((int(r["incident_year"]), r["agency_id"]) for r in eligible)
    annual = search_points("uap", solution=True)
    assert len(annual) == 820
    assert {(p.time.year, p.tags["agency_id"]): int(p.fields["catalog_entries"]) for p in annual} == {
        (year, a): counts[(year, a)] for year in range(1945, 2027) for a in solution["names"]}
    fbi = solution["fbi_id"]
    assert sum(1 for r in eligible if r["agency_id"] == fbi and 2020 <= int(r["incident_year"]) < 2024) == 25
    assert sum(1 for r in eligible if 2020 <= int(r["incident_year"]) < 2024) == 116
    assert sum(p.fields["catalog_entries"] for p in annual) == 292
    assert all(len([p for p in annual if p.time.year == year]) == 10 for year in range(1945, 2027))
    Time, Tag, Field = TimeQuery(), TagQuery(), FieldQuery()
    bounds = (Tag.agency_id == fbi) & (Time >= datetime(2020, 1, 1, tzinfo=timezone.utc)) & (Time < datetime(2024, 1, 1, tzinfo=timezone.utc))
    assert [p.time.year for p in search_points("uap", bounds, solution=True)] == [2020, 2021, 2022, 2023]
    positive = search_points("uap", Field.catalog_entries > 0, solution=True)
    zero = search_points("uap", Field.catalog_entries == 0, solution=True)
    assert len(positive) + len(zero) == 820 and sum(p.fields["catalog_entries"] for p in positive) == 292
    assert all(r["annual_eligible"] == "False" for r in catalog if r["source_key"] == "FBI-UAP-D024")
    assert all(r["incident_year"] == "2023" for r in catalog if r["source_key"] == "FBI-UAP-D026")
    return {"microblogging_points": len(demo["all_events"]), "annual_points": len(annual),
            "annual_count_sum": 292, "excluded_catalog_entries": 83, "positive_annual_points": len(positive),
            "zero_annual_points": len(zero), "fbi_2020_2023": 25, "all_agencies_2020_2023": 116,
            "legacy_omitted_likes": 19, "legacy_omitted_comments": 18}

def storage_checks():
    # Reales Dateiformat: nach Schliessen/Wiederöffnen und wiederholtem Import identisch.
    for dataset in ["microblogging", "uap"]:
        expected = Counter(map(point_signature, prepare_points(dataset)))
        for _ in range(2):
            replace_snapshot(dataset)
            with TinyFlux(str(database_path(dataset)), encoding="utf-8") as db:
                assert Counter(map(point_signature, db.all())) == expected
    task_file = database_path("uap")
    before = task_file.read_bytes()
    replace_snapshot("uap", solution=True)
    assert task_file.read_bytes() == before
    assert task_file != database_path("uap", solution=True)
    # Derselbe Punkt doppelt: Import muss vor dem Ersetzen abbrechen.
    points = prepare_points("uap")
    try:
        replace_snapshot("uap", points=points + points[:1])
    except ValueError:
        pass
    else:
        raise AssertionError("Doppelter Punkt nicht zurückgewiesen")
    assert task_file.read_bytes() == before
    # Auch bei einem Fehler am letzten Schreibschritt bleibt der alte Bestand bestehen.
    from unittest.mock import patch
    with patch("tinyflux_workshop.os.replace", side_effect=OSError("simulierter Dateifehler")):
        try: replace_snapshot("uap")
        except OSError: pass
        else: raise AssertionError("Dateifehler nicht weitergegeben")
    assert task_file.read_bytes() == before
    assert not list(task_file.parent.glob(task_file.stem + "_*.csv"))
    return {"reopen_and_repeat": "passed", "separate_task_solution": "passed",
            "duplicate_input_preserves_file": "passed", "failed_replace_preserves_file": "passed"}

def kernel_checks():
    import nbformat
    from nbclient import NotebookClient
    output = ROOT / "data/work/tinyflux_execution"
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for relative in NOTEBOOKS:
        for run in [1, 2]:
            book = nbformat.read(ROOT / relative, as_version=4)
            client = NotebookClient(book, timeout=180, kernel_name="rothstein-storage-workshop-2026",
                resources={"metadata": {"path": str((ROOT / relative).parent)}})
            client.execute()
            code_cells = [c for c in book.cells if c.cell_type == "code"]
            assert all(c.execution_count is not None for c in code_cells)
            assert not any(o.output_type == "error" for c in code_cells for o in c.outputs)
            images = sum("image/png" in o.get("data", {}) for c in code_cells for o in c.outputs)
            target = output / (relative.replace("/", "__"))
            if run == 2: nbformat.write(book, target)
            results.append({"notebook": relative, "run": run, "code_cells": len(code_cells), "figures": images})
            print("KERNEL OK:", relative, "Lauf", run, flush=True)
    return results

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", action="store_true")
    args = parser.parse_args()
    os.chdir(ROOT)
    previous = os.environ.get("STORAGE_TINYFLUX_TEST_DIR")
    report = {"status": "running", "python": platform.python_version(), "versions": {
        name: importlib.metadata.version(name) for name in ["tinyflux", "pandas", "matplotlib", "nbformat", "nbclient"]}}
    try:
        with tempfile.TemporaryDirectory(prefix="storage_tinyflux_validation_") as temporary:
            os.environ["STORAGE_TINYFLUX_TEST_DIR"] = temporary
            runs = []
            for run in [1, 2]:
                namespaces = []
                for relative in NOTEBOOKS:
                    ns, count = execute(ROOT / relative)
                    namespaces.append(ns)
                    runs.append({"notebook": relative, "run": run, "code_cells": count})
                report["reference_results"] = check_results(*namespaces)
            report["code_cell_runs"] = runs
            report["storage_checks"] = storage_checks()
            # Kernelprozesse erben den isolierten Datenpfad, keine regulären Arbeitsdateien.
            report["kernel_runs"] = kernel_checks() if args.kernel else []
            report["kernel_status"] = "passed" if args.kernel else "not_run"
            report["status"] = "passed"
            report["limits"] = ["Windows/macOS und Codespaces als Plattform nicht ausgeführt.",
                                "Vollständige Integration aller vier Speicher und Dienstneustarts bleibt offen."]
            if not args.kernel:
                report["limits"].append("Dieser Lauf startet keinen Jupyter-Kernel; siehe separaten Kernelversuch.")
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        if previous is None: os.environ.pop("STORAGE_TINYFLUX_TEST_DIR", None)
        else: os.environ["STORAGE_TINYFLUX_TEST_DIR"] = previous
        (ROOT / "validation/tinyflux_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("TINYFLUX OK", json.dumps(report["reference_results"], ensure_ascii=False))

if __name__ == "__main__":
    main()
