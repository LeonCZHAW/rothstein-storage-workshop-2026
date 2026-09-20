#!/usr/bin/env python3
"""PURSUE-Katalog beschaffen und deterministisch aufbereiten (Python >= 3.10).

Nur Python-Standardbibliothek. Keine Datenbankdienste erforderlich.
Siehe README.md für Quellen, Zähleinheiten und Grenzen der Normalisierung.
"""
from __future__ import annotations

import argparse
import calendar
from collections import Counter, defaultdict
import csv
from datetime import date, datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import tempfile
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CATALOG_URL = "https://www.war.gov/Portals/1/Interactive/2026/UFO/uap-data.csv?release=5"
REQUIRED = {"Title", "Agency", "Type", "Release Date", "Incident Date",
            "Incident Location", "Description Blurb", "PDF Pairing",
            "Video Pairing", "PDF | Image Link", "DVIDS Video ID"}
MONTHS = {calendar.month_name[i].lower(): i for i in range(1, 13)}


def clean(value):
    return " ".join(str(value or "").split())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def ident(prefix, value):
    return prefix + "_" + digest(value.encode("utf-8"))[:20]


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(value))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def read_catalog(path):
    payload = path.read_bytes()
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig"), newline=""))
    if not REQUIRED.issubset(reader.fieldnames or []):
        raise ValueError(f"Quellschema unvollständig: {sorted(REQUIRED - set(reader.fieldnames or []))}")
    rows = list(reader)
    if not rows or any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError("Leerer oder beschädigter CSV-Katalog")
    return payload, rows


def parse_us_date(text, latest_year):
    month, day, year = (int(x) for x in text.split("/"))
    if year < 100:
        year += 2000
        if year > latest_year:
            year -= 100
    return date(year, month, day)


def incident_date(raw, latest_year):
    """Nur eindeutig einem Jahr zuordenbare Katalogeinträge jahresweise zählen.

    Tages-/Monatsdaten werden nur bei expliziten Quellangaben ausgegeben.
    Zeiträume und Jahrzehnte bleiben als solche erkennbar.
    """
    s = clean(raw)
    result = {"incident_date_raw": raw, "incident_date_precision": "unparsed",
              "incident_year": None, "incident_month": None, "incident_day": None,
              "annual_eligible": False, "date_exclusion_reason": "unparsed"}
    if s.lower() in {"", "n/a", "undated", "unknown"}:
        result.update(incident_date_precision="missing", date_exclusion_reason="missing")
        return result
    if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{2,4}", s):
        d = parse_us_date(s, latest_year)
        result.update(incident_year=d.year, incident_month=d.month,
                      incident_day=d.isoformat(), incident_date_precision="day")
    elif re.fullmatch(r"(?:19|20)\d{2}", s):
        result.update(incident_year=int(s), incident_date_precision="year")
    elif re.fullmatch(r"(?:19|20)\d0s", s):
        result.update(incident_date_precision="decade", date_exclusion_reason="multiple_years")
    else:
        month_match = re.fullmatch(r"([A-Za-z]+),?\s+((?:19|20)\d{2})", s)
        if month_match and month_match[1].lower() in MONTHS:
            result.update(incident_year=int(month_match[2]),
                          incident_month=MONTHS[month_match[1].lower()],
                          incident_date_precision="month")
        elif re.fullmatch(r"Late\s+(?:19|20)\d{2}", s, re.I):
            result.update(incident_year=int(s[-4:]), incident_date_precision="approximate_within_year")
        else:
            # Zeiträume mit expliziten Datumsgrenzen prüfen.
            endpoints = re.fullmatch(r"(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})", s)
            if endpoints:
                start, end = (parse_us_date(endpoints[i], latest_year) for i in [1, 2])
                if end < start:
                    raise ValueError(f"Umgekehrter Datumsbereich: {s}")
                years = {start.year, end.year}
            else:
                years = {int(y) for y in re.findall(r"\b(?:19|20)\d{2}\b", s)}
            if len(years) > 1:
                result.update(incident_date_precision="multiple_years", date_exclusion_reason="multiple_years")
            elif len(years) == 1 and (endpoints or re.fullmatch(
                    r"[A-Za-z]+\s+\d{1,2}\s*-\s*(?:[A-Za-z]+\s+)?\d{1,2},\s*(?:19|20)\d{2}", s)):
                result.update(incident_year=next(iter(years)), incident_date_precision="period_within_year")
    if result["incident_year"] is not None:
        if result["incident_year"] > latest_year:
            raise ValueError(f"Ereignisjahr nach Snapshot-Jahr: {s}")
        result.update(annual_eligible=True, date_exclusion_reason="")
    return result


def fetch_bytes(url, limit=20_000_000):
    if urllib.parse.urlsplit(url).scheme != "https":
        raise ValueError("Nur HTTPS-Quellen sind zugelassen")
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Rothstein-Storage-Workshop-Educational-Ingestion/1.0"})
            with urllib.request.urlopen(req, timeout=40) as response:
                data = response.read(limit + 1)
                if len(data) > limit:
                    raise ValueError("Quelldatei überschreitet das Download-Limit")
                headers = {k: response.headers.get(k) for k in ["Content-Type", "Last-Modified", "ETag"]}
                return data, response.geturl(), headers
        except (OSError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def fetch_snapshot(destination):
    if destination.exists():
        raise FileExistsError("Für einen Live-Abruf einen neuen Zielordner wählen")
    data, final_url, headers = fetch_bytes(CATALOG_URL)
    # Erst prüfen, dann einen neuen Snapshot-Ordner anlegen.
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "catalog.csv"
        p.write_bytes(data)
        _, rows = read_catalog(p)
    destination.mkdir(parents=True)
    (destination / "pursue_catalog.csv").write_bytes(data)
    write_json(destination / "source_manifest.json", {
        "source_url": CATALOG_URL, "resolved_url": final_url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": digest(data), "size_bytes": len(data), "row_count": len(rows),
        "http_headers": headers, "snapshot_kind": "live_download",
    })
    print(f"Neuer Snapshot: {destination} ({len(rows)} Katalogeinträge)")


def build(raw_dir, output_dir):
    payload, raw_rows = read_catalog(raw_dir / "pursue_catalog.csv")
    manifest = read_json(raw_dir / "source_manifest.json")
    if digest(payload) != manifest["sha256"]:
        raise ValueError("Prüfsumme des Rohkatalogs stimmt nicht mit dem Manifest überein")
    if len(raw_rows) != manifest["row_count"]:
        raise ValueError("Zeilenzahl weicht vom Snapshot-Manifest ab")
    # Das seit 2026 veröffentlichte Portal verwendet zweistellige Release-Jahre
    # des 21. Jahrhunderts. Dieser Bezug ist von historischen Incident Dates getrennt.
    releases = [parse_us_date(clean(r["Release Date"]), 2099) for r in raw_rows]
    latest_year = max(d.year for d in releases)
    entries, agencies, release_rows, assets, entry_assets = [], {}, {}, {}, []
    issues, lookups, raw_by_id = [], defaultdict(list), {}
    for row_number, (raw, released) in enumerate(zip(raw_rows, releases), start=2):
        title = clean(raw["Title"])
        source_key = title.split(",", 1)[0].strip()
        entry_id = ident("entry", released.isoformat() + "|" + source_key)
        if entry_id in raw_by_id:
            raise ValueError(f"Mehrdeutiger Identitätsschlüssel in Quellzeile {row_number}")
        raw_by_id[entry_id] = raw
        agency_name = clean(raw["Agency"])
        agency_id = ident("agency", agency_name)
        agencies[agency_id] = {"agency_id": agency_id, "name": agency_name}
        release_id = "release_" + released.isoformat()
        release_rows[release_id] = {"release_id": release_id, "release_date": released.isoformat()}
        description = raw["Description Blurb"].strip()
        evidence_kind = "artistic_interpretation" if re.search(r"artistic interpretation|digital rendering|composite sketch", description + " " + title, re.I) else "not_classified"
        entry = {"entry_id": entry_id, "source_key": source_key, "source_row": row_number,
                 "title": title, "agency_id": agency_id, "release_id": release_id,
                 "release_date": released.isoformat(), "media_type": clean(raw["Type"]).upper(),
                 "description": description, "location_raw": raw["Incident Location"],
                 "redaction_reported": clean(raw["Redaction"]).upper() == "TRUE",
                 "description_category": evidence_kind,
                 **incident_date(raw["Incident Date"], latest_year)}
        entries.append(entry)
        for value in {title.casefold(), source_key.casefold()}:
            lookups[value].append(entry_id)
        file_url = clean(raw["PDF | Image Link"])
        if file_url:
            if not file_url.startswith("https://"):
                raise ValueError(f"Ungültiger Datei-Link: {file_url}")
            asset_id = ident("asset", file_url)
            assets[asset_id] = {"asset_id": asset_id, "locator_type": "url", "locator": file_url,
                                "format_hint": Path(urllib.parse.urlsplit(file_url).path).suffix.lstrip(".").lower()}
            entry_assets.append({"entry_id": entry_id, "asset_id": asset_id, "source_field": "PDF | Image Link"})
        video = clean(raw["DVIDS Video ID"])
        if video:
            if not video.isdigit():
                raise ValueError(f"Unerwartete DVIDS-Kennung: {video}")
            asset_id = ident("asset", "dvids:" + video)
            assets[asset_id] = {"asset_id": asset_id, "locator_type": "dvids_video_id", "locator": video, "format_hint": "media"}
            entry_assets.append({"entry_id": entry_id, "asset_id": asset_id, "source_field": "DVIDS Video ID"})
    entries.sort(key=lambda x: x["entry_id"])
    aliases_path = ROOT / "ingestion" / "reference_aliases.json"
    aliases = read_json(aliases_path) if aliases_path.exists() else {}
    pairs = []
    for entry in entries:
        raw = raw_by_id[entry["entry_id"]]
        for field in ["PDF Pairing", "Video Pairing"]:
            for token in filter(None, (clean(s) for s in raw[field].split("|"))):
                candidates = lookups.get(token.casefold(), [])
                rule = "exact_normalized_label"
                if not candidates and token in aliases:
                    candidates = lookups.get(aliases[token]["target_source_key"].casefold(), [])
                    rule = "documented_alias"
                if not candidates and re.fullmatch(r"PR-\d+", token, re.I):
                    # Portal-Kurzform nur bei global eindeutiger Zielkennung erweitern.
                    suffix = "-uap-pr" + token.split("-")[1].zfill(3)
                    candidates = [e["entry_id"] for e in entries if e["source_key"].lower().endswith(suffix)]
                    rule = "unique_portal_pr_shorthand"
                if len(candidates) != 1:
                    issues.append({"source_entry_id": entry["entry_id"], "source_key": entry["source_key"],
                                   "source_field": field, "raw_reference": token,
                                   "status": "ambiguous" if candidates else "unresolved",
                                   "candidate_entry_ids": candidates})
                    continue
                if candidates[0] == entry["entry_id"]:
                    issues.append({"source_entry_id": entry["entry_id"], "source_key": entry["source_key"],
                                   "source_field": field, "raw_reference": token, "status": "self_reference",
                                   "candidate_entry_ids": candidates})
                    continue
                pairs.append({"pairing_id": ident("pair", entry["entry_id"] + "|" + field + "|" + token),
                              "source_entry_id": entry["entry_id"], "target_entry_id": candidates[0],
                              "source_field": field, "raw_reference": token, "resolution_rule": rule})
    pairs.sort(key=lambda x: x["pairing_id"])
    eligible = [e for e in entries if e["annual_eligible"]]
    if not eligible:
        raise ValueError("Keine jahresweise auswertbaren Katalogeinträge")
    year_min, year_max = min(e["incident_year"] for e in eligible), max(e["incident_year"] for e in eligible)
    counts = Counter((e["incident_year"], e["agency_id"]) for e in eligible)
    annual = [{"period_start": f"{year}-01-01T00:00:00Z", "incident_year": year,
               "agency_id": aid, "catalog_entries": counts[year, aid],
               "date_basis": "catalog_incident_year", "snapshot_sha256": manifest["sha256"]}
              for year in range(year_min, year_max + 1) for aid in sorted(agencies)]
    by_entry_assets, by_entry_pairs = defaultdict(list), defaultdict(list)
    for link in entry_assets:
        by_entry_assets[link["entry_id"]].append(assets[link["asset_id"]])
    for pair in pairs:
        by_entry_pairs[pair["source_entry_id"]].append(pair)
    documents = []
    for entry in entries:
        doc = dict(entry)
        doc["agency"] = agencies[entry["agency_id"]]
        doc["assets"] = sorted(by_entry_assets[entry["entry_id"]], key=lambda x: x["asset_id"])
        doc["related_entries"] = sorted(by_entry_pairs[entry["entry_id"]], key=lambda x: x["pairing_id"])
        doc["source_metadata"] = {k: v for k, v in raw_by_id[entry["entry_id"]].items() if k and v.strip()}
        documents.append(doc)
    nodes, edges = [], []
    for e in entries:
        nodes.append({"node_id": e["entry_id"], "label": "CatalogEntry", "properties": e})
        for target, typ in [(e["agency_id"], "CATALOG_AGENCY"), (e["release_id"], "IN_RELEASE")]:
            edges.append({"edge_id": ident("edge", e["entry_id"] + "|" + typ),
                          "source": e["entry_id"], "target": target, "type": typ,
                          "properties": {"source_row": e["source_row"]}})
    for aid, value in agencies.items():
        nodes.append({"node_id": aid, "label": "Agency", "properties": value})
    for rid, value in release_rows.items():
        nodes.append({"node_id": rid, "label": "Release", "properties": value})
    for aid, value in assets.items():
        nodes.append({"node_id": aid, "label": "Asset", "properties": value})
    for link in entry_assets:
        edges.append({"edge_id": ident("edge", link["entry_id"] + "|" + link["asset_id"]),
                      "source": link["entry_id"], "target": link["asset_id"], "type": "LINKS_ASSET",
                      "properties": {"source_field": link["source_field"]}})
    for p in pairs:
        edges.append({"edge_id": p["pairing_id"], "source": p["source_entry_id"],
                      "target": p["target_entry_id"], "type": "PORTAL_PAIRS_WITH", "properties": p})
    # Alle bekannten Dateien werden bewusst benannt; fremde Dateien werden nicht gelöscht.
    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "catalog_entries.jsonl", entries)
    write_csv(output_dir / "relational/catalog_entries.csv", entries, list(entries[0]))
    write_csv(output_dir / "relational/agencies.csv", sorted(agencies.values(), key=lambda x: x["agency_id"]), ["agency_id", "name"])
    write_csv(output_dir / "relational/releases.csv", sorted(release_rows.values(), key=lambda x: x["release_id"]), ["release_id", "release_date"])
    write_csv(output_dir / "relational/assets.csv", sorted(assets.values(), key=lambda x: x["asset_id"]), ["asset_id", "locator_type", "locator", "format_hint"])
    write_csv(output_dir / "relational/entry_assets.csv", sorted(entry_assets, key=lambda x: (x["entry_id"], x["asset_id"])), ["entry_id", "asset_id", "source_field"])
    write_csv(output_dir / "relational/portal_pairings.csv", pairs, ["pairing_id", "source_entry_id", "target_entry_id", "source_field", "raw_reference", "resolution_rule"])
    write_jsonl(output_dir / "document/catalog_documents.jsonl", documents)
    write_jsonl(output_dir / "graph/nodes.jsonl", sorted(nodes, key=lambda x: x["node_id"]))
    write_jsonl(output_dir / "graph/edges.jsonl", sorted(edges, key=lambda x: x["edge_id"]))
    write_csv(output_dir / "timeseries/annual_catalog_counts.csv", annual, list(annual[0]))
    write_json(output_dir / "quality/unresolved_pairings.json", sorted(issues, key=lambda x: (x["source_entry_id"], x["source_field"], x["raw_reference"])))
    ambiguous_codes = {k: v for k, v in lookups.items() if len(v) > 1}
    entry_by_id = {e["entry_id"]: e for e in entries}
    excluded = [{k: e[k] for k in ["entry_id", "source_key", "incident_date_raw", "incident_date_precision", "date_exclusion_reason"]} for e in entries if not e["annual_eligible"]]
    write_json(output_dir / "quality/date_exclusions.json", excluded)
    write_json(output_dir / "quality/duplicate_source_keys.json", ambiguous_codes)
    # Graph-Pfadbeispiele aus belegten Portalverweisen, ohne erfundene Ereignisknoten.
    neighbours = defaultdict(set)
    for p in pairs:
        neighbours[p["source_entry_id"]].add(p["target_entry_id"])
    examples = []
    for a in sorted(neighbours):
        for b in sorted(neighbours[a]):
            for c in sorted(neighbours[b] - {a, b}):
                if len({entry_by_id[x]["agency_id"] for x in [a, b, c]}) > 1:
                    examples.append({"entry_ids": [a, b, c],
                                     "source_keys": [entry_by_id[x]["source_key"] for x in [a, b, c]]})
                if len(examples) >= 5:
                    break
            if len(examples) >= 5:
                break
        if len(examples) >= 5:
            break
    stats = {
        "catalog_entries": len(entries), "agencies": len(agencies), "releases": len(release_rows),
        "distinct_asset_locators": len(assets), "entry_asset_links": len(entry_assets),
        "resolved_directed_portal_pairings": len(pairs), "unresolved_pairing_tokens": len(issues),
        "pairing_issue_statuses": dict(sorted(Counter(x["status"] for x in issues).items())),
        "graph_nodes": len(nodes), "graph_edges": len(edges), "cross_agency_two_hop_examples": examples,
        "annual_eligible_entries": len(eligible), "annual_excluded_entries": len(excluded),
        "annual_year_min": year_min, "annual_year_max": year_max,
        "years_with_eligible_entries": len({e["incident_year"] for e in eligible}),
        "annual_count_points": len(annual), "annual_count_sum": sum(x["catalog_entries"] for x in annual),
        "date_precision_counts": dict(sorted(Counter(e["incident_date_precision"] for e in entries).items())),
        "media_type_counts": dict(sorted(Counter(e["media_type"] for e in entries).items())),
        "agency_counts": dict(sorted(Counter(agencies[e["agency_id"]]["name"] for e in entries).items())),
        "release_counts": dict(sorted(Counter(e["release_date"] for e in entries).items())),
        "artistic_interpretation_entries": sum(e["description_category"] == "artistic_interpretation" for e in entries),
        "missing_location_entries": sum(clean(e["location_raw"]).lower() in {"", "n/a"} for e in entries),
        "snapshot_sha256": manifest["sha256"],
    }
    write_json(output_dir / "reference_metrics.json", stats)
    # Kontrollen gegen stille Verluste und verwaiste Beziehungen.
    assert len({n["node_id"] for n in nodes}) == len(nodes)
    assert len({e["edge_id"] for e in edges}) == len(edges)
    node_ids = {n["node_id"] for n in nodes}
    assert all(e["source"] in node_ids and e["target"] in node_ids for e in edges)
    assert stats["annual_count_sum"] == len(eligible)
    assert len(eligible) + len(excluded) == len(entries)
    generated_names = ["catalog_entries.jsonl", "relational/catalog_entries.csv",
                       "relational/agencies.csv", "relational/releases.csv", "relational/assets.csv",
                       "relational/entry_assets.csv", "relational/portal_pairings.csv",
                       "document/catalog_documents.jsonl", "graph/nodes.jsonl", "graph/edges.jsonl",
                       "timeseries/annual_catalog_counts.csv", "quality/unresolved_pairings.json",
                       "quality/date_exclusions.json", "quality/duplicate_source_keys.json",
                       "reference_metrics.json"]
    file_hashes = {name: digest((output_dir / name).read_bytes()) for name in sorted(generated_names)}
    write_json(output_dir / "build_manifest.json", {
        "source_sha256": digest(payload), "pipeline_version": "1.0.0",
        "pipeline_sha256": digest(Path(__file__).read_bytes()),
        "reference_aliases_sha256": digest(aliases_path.read_bytes()) if aliases_path.exists() else None,
        "id_scheme": "sha256(release_date|normalized_source_key), first 20 hex; catalog-entry identity",
        "two_digit_year_rule": f"100-year window ending in {latest_year}",
        "outputs_sha256": file_hashes,
    })
    return stats


def verify(raw_dir, output_dir):
    expected = read_json(output_dir / "build_manifest.json")
    if expected.get("pipeline_sha256") != digest(Path(__file__).read_bytes()):
        raise ValueError(
            "Pipeline-Prüfsumme stimmt nicht: ingestion/ingest.py und "
            "data/input/build_manifest.json müssen aus derselben Workshop-Version stammen."
        )
    for name, value in expected["outputs_sha256"].items():
        if digest((output_dir / name).read_bytes()) != value:
            raise ValueError(f"Ausgabedatei verändert: {name}")
    with tempfile.TemporaryDirectory() as tmp:
        stats = build(raw_dir, Path(tmp))
        actual = read_json(Path(tmp) / "build_manifest.json")
    if expected != actual:
        differences = sorted(key for key in expected.keys() | actual.keys()
                             if expected.get(key) != actual.get(key))
        raise ValueError("Neuberechnung weicht vom mitgelieferten Datenstand ab: " + ", ".join(differences))
    sample_manifest = raw_dir / "sample_assets.json"
    sample_count = 0
    if sample_manifest.exists():
        for item in read_json(sample_manifest):
            path = raw_dir / item["relative_path"]
            if digest(path.read_bytes()) != item["sha256"]:
                raise ValueError(f"Originalstichprobe verändert: {path.name}")
            sample_count += 1
    print(f"Prüfung erfolgreich: {stats['catalog_entries']} Katalogeinträge; reproduzierbare Ausgaben; {sample_count} Originaldateien geprüft.")


def fetch_samples(raw_dir, destination):
    if destination.exists():
        raise FileExistsError("Für Originaldateien einen neuen Zielordner wählen")
    samples = read_json(raw_dir / "sample_assets.json")
    destination.mkdir(parents=True)
    results = []
    for sample in samples:
        data, resolved_url, headers = fetch_bytes(sample["source_url"])
        if not data.startswith(b"%PDF-"):
            raise ValueError("PDF-Stichprobe lieferte keine PDF-Datei")
        name = Path(sample["relative_path"]).name
        (destination / name).write_bytes(data)
        results.append({"file": name, "source_url": sample["source_url"],
                        "resolved_url": resolved_url, "sha256": digest(data), "http_headers": headers,
                        "matches_workshop_snapshot": digest(data) == sample["sha256"]})
    write_json(destination / "download_manifest.json", results)
    print(f"Originaldateien abgerufen: {len(results)}. Prüfsummenvergleich: download_manifest.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ["build", "verify"]:
        p = sub.add_parser(command)
        p.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw")
        p.add_argument("--output-dir", type=Path, default=ROOT / "data/input")
    p = sub.add_parser("fetch")
    p.add_argument("--output-dir", type=Path, required=True)
    p = sub.add_parser("fetch-samples")
    p.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw")
    p.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "fetch":
        fetch_snapshot(args.output_dir)
    elif args.command == "fetch-samples":
        fetch_samples(args.raw_dir, args.output_dir)
    elif args.command == "build":
        stats = build(args.raw_dir, args.output_dir)
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        verify(args.raw_dir, args.output_dir)


if __name__ == "__main__":
    main()
