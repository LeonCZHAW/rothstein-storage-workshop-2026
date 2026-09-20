"""TinyFlux 1.2.0: reproduzierbare Ereignis-/Jahressichten und eigene Dateien.

Jeder Import schreibt eine neue temporäre Datei, prüft sie nach erneutem Öffnen
und ersetzt erst danach genau die gewählte Arbeitsdatei. Keine Serverdienste.
"""
from __future__ import annotations

from collections import Counter
import csv
from datetime import datetime, timezone
import os
from pathlib import Path
import tempfile

from tinyflux import Point, TinyFlux

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENTS = {"microblogging": "microblogging_events", "uap": "uap_annual_catalog"}


def csv_rows(relative):
    with (ROOT / relative).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def parse_time(value):
    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def database_path(dataset, solution=False):
    if dataset not in MEASUREMENTS:
        raise ValueError("Datensatz muss uap oder microblogging sein.")
    test_root = os.getenv("STORAGE_TINYFLUX_TEST_DIR")
    base = Path(test_root).resolve() if test_root else ROOT / "data/work"
    folder = base / dataset
    folder.mkdir(parents=True, exist_ok=True)
    filename = "04_events.tinyflux.csv" if dataset == "microblogging" else (
        "04_annual_solution.tinyflux.csv" if solution else "04_annual_task.tinyflux.csv")
    return folder / filename


def annual_inputs():
    return csv_rows("data/input/timeseries/annual_catalog_counts.csv")


def agency_names():
    return {r["agency_id"]: r["name"] for r in csv_rows("data/input/relational/agencies.csv")}


def annual_point(row):
    return Point(time=parse_time(row["period_start"]), measurement=MEASUREMENTS["uap"],
                 tags={"agency_id": row["agency_id"], "date_basis": row["date_basis"],
                       "snapshot_sha256": row["snapshot_sha256"]},
                 fields={"catalog_entries": int(row["catalog_entries"])})


def prepare_points(dataset):
    if dataset == "uap":
        return [annual_point(row) for row in annual_inputs()]
    if dataset != "microblogging":
        raise ValueError("Unbekannter Datensatz")
    points = []
    for table, kind, id_field in [("posts", "post", "post_id"), ("likes", "like", "like_id"),
                                  ("comments", "comment", "comment_id")]:
        for r in csv_rows(f"data/microblogging/relational/{table}.csv"):
            points.append(Point(time=parse_time(r["created_at"]), measurement=MEASUREMENTS[dataset],
                tags={"type":kind,"user_id":r["user_id"],"post_id":r["post_id"],
                      "event_id":f"{kind}:{r[id_field]}"}, fields={"value":1}))
    for r in csv_rows("data/microblogging/relational/follows.csv"):
        points.append(Point(time=parse_time(r["since"]), measurement=MEASUREMENTS[dataset],
            tags={"type":"follow","user_id":r["src_user_id"],"target_user_id":r["dst_user_id"],
                  "event_id":f"follow:{r['src_user_id']}:{r['dst_user_id']}"}, fields={"value":1}))
    return sorted(points,key=lambda p:(p.time,p.tags["event_id"]))


def point_signature(p):
    return (p.time.isoformat(),p.measurement,tuple(sorted(p.tags.items())),tuple(sorted(p.fields.items())))


def validate_points(points,dataset):
    if dataset not in MEASUREMENTS or not points:
        raise ValueError("Unbekannter Datensatz oder leerer Import.")
    identities = []
    for p in points:
        if not isinstance(p,Point) or p.measurement != MEASUREMENTS[dataset]:
            raise ValueError("Falscher Point-Typ oder Measurement.")
        if p.time.tzinfo is None or p.time.utcoffset() is None:
            raise ValueError("Zeitstempel muss eine Zeitzone besitzen.")
        if any(not isinstance(v,str) or not v for v in p.tags.values()):
            raise ValueError("Tags müssen nicht leere Strings sein.")
        if dataset == "uap":
            if set(p.tags)!={"agency_id","date_basis","snapshot_sha256"} or set(p.fields)!={"catalog_entries"}:
                raise ValueError("Jahrespunkt benötigt Stelle, Datumsgrundlage, Snapshot und Zählfeld.")
            if p.tags["date_basis"]!="catalog_incident_year" or p.time!=datetime(p.time.year,1,1,tzinfo=timezone.utc):
                raise ValueError("Jahresmarke oder Datumsgrundlage ist falsch.")
            identities.append((p.measurement, p.time, tuple(sorted(p.tags.items()))))
            value=p.fields["catalog_entries"]
        else:
            if p.tags.get("type") not in {"post","like","comment","follow"} or "event_id" not in p.tags:
                raise ValueError("Ungültiger Ereignistyp oder fehlende Ereignis-ID.")
            if set(p.fields)!={"value"}:raise ValueError("Ereignisse benötigen das Zählfeld value.")
            identities.append(p.tags["event_id"])
            value=p.fields["value"]
        if isinstance(value,bool) or not isinstance(value,(int,float)) or value < 0 or int(value)!=value:
            raise ValueError("Zählfelder müssen nicht negative ganze Zahlen sein.")
    if len(set(identities))!=len(identities):
        raise ValueError("Doppelte Punktidentität im Import; keine Datei ersetzt.")


def replace_snapshot(dataset,solution=False,points=None):
    points=list(prepare_points(dataset) if points is None else points)
    validate_points(points,dataset)
    path=database_path(dataset,solution)
    descriptor,tmp_name=tempfile.mkstemp(prefix=path.stem+"_",suffix=".csv",dir=path.parent)
    os.close(descriptor)
    tmp=Path(tmp_name)
    try:
        with TinyFlux(str(tmp),encoding="utf-8") as db:
            inserted=db.insert_multiple(points)
            if inserted!=len(points):raise ValueError("Unvollständiger TinyFlux-Import.")
        with TinyFlux(str(tmp),encoding="utf-8") as db:
            reloaded=db.all()
        if Counter(map(point_signature,reloaded))!=Counter(map(point_signature,points)):
            raise ValueError("Wiederöffnen liefert abweichende Punktwerte; keine Datei ersetzt.")
        os.replace(tmp,path)
    finally:
        tmp.unlink(missing_ok=True)
    return {"path":str(path),"points":len(points)}


def search_points(dataset,query=None,solution=False):
    path=database_path(dataset,solution)
    if not path.exists():raise FileNotFoundError("Zuerst den Import ausführen: "+str(path))
    with TinyFlux(str(path),encoding="utf-8") as db:
        return db.all() if query is None else db.search(query)


def points_frame(points):
    import pandas as pd
    points=list(points)
    rows=[{"time":p.time,"measurement":p.measurement,**p.tags,**p.fields} for p in points]
    if not rows:return pd.DataFrame(columns=["time","measurement"])
    result=pd.DataFrame(rows)
    result["time"]=pd.to_datetime(result["time"],utc=True)
    return result.sort_values("time",kind="stable").reset_index(drop=True)


def yearly_frame(points):
    import pandas as pd
    records=[{"year":p.time.year,"agency_id":p.tags["agency_id"],
              "catalog_entries":int(p.fields["catalog_entries"])} for p in points]
    return pd.DataFrame(records,columns=["year","agency_id","catalog_entries"]).sort_values(
        ["year","agency_id"]).reset_index(drop=True)


def daily_posts(records):
    """Kalenderergänzung und gleitender Durchschnitt: bewusst pandas, nicht TinyFlux."""
    import pandas as pd
    events=records.copy()
    events["day"]=pd.to_datetime(events["time"],utc=True).dt.floor("D")
    counts=events.groupby("day")["value"].sum()
    days=pd.date_range(counts.index.min(),counts.index.max(),freq="D")
    result=counts.reindex(days,fill_value=0).rename("posts").rename_axis("day").reset_index()
    result["rolling_7d"]=result["posts"].rolling(7,min_periods=1).mean()
    return result
