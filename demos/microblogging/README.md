[Workshop-Übersicht](../../README.md) · [Technische Vorbereitung](../../README_technical_preparation.md) · [Microblogging-Beispiele](README.md) · [UAP-Aufgaben](../../tasks/README.md)

# Demonstrationen: Microblogging-Plattform

Der bekannte Fall umfasst 200 Nutzerkonten, 865 Posts, 1'266 Likes, 512 Kommentare und 3'047 Follow-Beziehungen. Die synthetischen Originaleingaben aus dem Vorjahr liegen unter [data/microblogging](../../data/microblogging/README.md), mit dokumentierten Prüfsummen.

## Orientierung

[Einstieg ohne Docker](#ohne-docker-einsteigen) · [Neo4j-Graph anzeigen](#nach-dem-import-graph-anzeigen-optional) · [Notebooks und Kernfragen](#verfügbare-demonstrationen) · [Modellvergleich](#cheat-sheet-modelle-im-vergleich) · [Abfragemuster](#cheat-sheet-abfragemuster) · [Q1–Q5 je Modell](#q1q5-umsetzung-je-modell) · [Fehlerbehebung](#fehlerbehebung) · [Vertiefungen](#optionale-vertiefungen)

## Ohne Docker einsteigen

**Dieser Schnellstart gehört zu Weg B.** Bei [Weg A: lokal mit Docker](../../README_technical_preparation.md#weg-a-lokal-mit-docker) oder [Weg C: Codespaces](../../README_technical_preparation.md#weg-c-codespaces) die bereits eingerichtete Umgebung und die laufenden Container verwenden; die lokale Installation und den Desktop-Start hier überspringen.

Du kannst alle vier Beispiele lokal ohne Docker bearbeiten. Für SQLite und TinyFlux genügt die Python-Kursumgebung. MongoDB und Neo4j benötigen zusätzlich ihren jeweiligen laufenden Datenbankserver. Die [vollständige Anleitung ohne Docker](../../docs/setup/OHNE_DOCKER.md) führt durch Installation, Anmeldung, Start und Wiederaufnahme.

| Beispiel | Was zusätzlich zur Kursumgebung laufen muss | Anleitung |
| --- | --- | --- |
| [SQLite](01_sqlite.ipynb) | Kein Server; lokale Datenbankdatei | [Python-Umgebung einrichten](../../docs/setup/OHNE_DOCKER.md#2-repo-und-python-umgebung-vorbereiten) |
| [MongoDB](02_mongodb.ipynb) | MongoDB Community Server 8.0.x mit Kursbenutzer | [Installation und Benutzeranlage](../../docs/setup/MONGODB_LOKAL.md) |
| [Neo4j](03_neo4j.ipynb) | Gestartete Neo4j-5.26.x-Instanz in Neo4j Desktop | [Desktop-Anleitung](../../docs/setup/NEO4J_DESKTOP.md) |
| [TinyFlux](04_tinyflux.ipynb) | Kein Server; lokale TinyFlux-Datei | Dieselbe Python-Kursumgebung |

### Python-Umgebung und Notebooks

Öffne den vollständig entpackten Repo-Hauptordner; dort liegt `environment.yml`. Unter Windows verwende **Anaconda Prompt** oder eingerichtetes **Git Bash**, unter macOS/Linux das Terminal. [Bash-Einrichtung](../../docs/setup/BASH.md). Conda muss nach der [Installationsanleitung](../../docs/setup/INSTALLATION.md#1-conda-bereitstellen) vorhanden sein.

Bei der ersten Einrichtung im Repo-Hauptordner ausführen:

```bash
conda env create -f environment.yml
conda activate rothstein-storage-workshop-2026
python -m ipykernel install --user --name rothstein-storage-workshop-2026 --display-name "Python (rothstein-storage-workshop-2026)"
```

Wenn die Kursumgebung bereits eingerichtet ist, genügt `conda activate rothstein-storage-workshop-2026`. Danach die benötigten Dienste starten und JupyterLab öffnen:

```bash
jupyter lab
```

Öffne unter `demos/microblogging/` das gewünschte Notebook, wähle **Python (rothstein-storage-workshop-2026)** und führe die Zellen von oben nach unten aus. Das Terminal mit JupyterLab bleibt für dessen Server belegt. Für weitere Befehle ein zweites Terminal öffnen und ebenfalls die Kursumgebung aktivieren. Alternativ das Repo in VS Code öffnen und dort denselben Notebook-Kernel wählen.

### Vor der ersten Codezelle: den gewählten Neo4j-Dienst verwenden

**Wähle genau einen Betriebsweg. Eine neue Desktop-Instanz ist nur für Weg B nötig, wenn noch keine passende Instanz vorhanden ist.**

| Weg | Vor dem Notebook | Graphansicht nach dem Import |
| --- | --- | --- |
| **A: lokal mit Docker** | Neo4j-Desktop-Instanzen stoppen; den eingerichteten Neo4j-Container verwenden. | [Neo4j Browser](http://localhost:7474/browser/) mit `bolt://127.0.0.1:7687` |
| **B: lokal ohne Docker** | Einen laufenden Neo4j-Kurscontainer zuerst stoppen; die Desktop-Kursinstanz starten. | Bei derselben Instanz **Open → Neo4j Browser** (1.x) bzw. **Connect → Query** (2.x) |
| **C: Codespaces** | Den automatischen Dienststart abwarten; den Host `neo4j` aus der Containerkonfiguration verwenden. | **Ports → 8080 → Open in Browser → Neo4j Browser öffnen**; [Anleitung](../../docs/setup/NEO4J_START.md#weg-c-codespaces). |

**Portkonflikt vermeiden:** Weg A und B belegen lokal standardmässig `7474` (Weboberfläche) und `7687` (Bolt). Betreibe dort nur einen Neo4j-Server. Beim Wechsel zu Weg B im bisherigen Repo-Ordner `docker compose stop neo4j` ausführen, solange noch die bisherige Compose-Konfiguration vorliegt. Andere Neo4j-Container gegebenenfalls in Docker Desktop stoppen. Docker darf für MongoDB weiterlaufen.

Die [Neo4j-Startanleitung für A, B und C](../../docs/setup/NEO4J_START.md) beschreibt Start, Verbindung, Graphansicht und den Wechsel zwischen den Wegen. **Nur für Weg B:** [Desktop einrichten](../../docs/setup/NEO4J_DESKTOP.md). Eine bestehende Kursinstanz weiterverwenden. Anzeigename: **rothstein-storage-workshop-2026**, Benutzer: `neo4j`, Standardpasswort: `Storage-Neo4j-2026`, Datenbank: `neo4j`.

Lokal verwenden die Notebooks bei den Standardwerten `127.0.0.1:7687`. Abweichende Zugangsdaten in einer vorhandenen `.env` anpassen; danach den Kernel neu starten. Codespaces setzt die internen Hosts und Ports automatisch. **Erst nach erfolgreichem Dienststart die Python-Codezellen ausführen.**

## Verfügbare Demonstrationen

[01_sqlite.ipynb](01_sqlite.ipynb), [02_mongodb.ipynb](02_mongodb.ipynb), [03_neo4j.ipynb](03_neo4j.ipynb) und [04_tinyflux.ipynb](04_tinyflux.ipynb) sind ausgearbeitet. Öffne sie mit dem Kernel **Python (rothstein-storage-workshop-2026)** und führe die Zellen von oben nach unten aus. Bei SQLite bilden Q1 und Q5 den Kern; bei MongoDB der Dokumentblick und Q1. Die übrigen Fragen und der Indexblick dienen der Vertiefung.

| Frage | Einheit und Zugriff |
| --- | --- |
| Q1: Aktivität | Verfasste Posts + verfasste Kommentare + gegebene Likes pro Person, gesamter Eingabebestand |
| Q2: Beliebtheit | Empfangene Likes pro Post; Posts ohne Likes bleiben erhalten |
| Q3: Beziehungen | Follower-/Following-Zahlen und gerichteter Pfad; festes Beispiel 1 → 3 |
| Q4: Zeitlicher Verlauf | Posts pro Kalendertag; gleitender Durchschnitt über bis zu sieben Tage |
| Q5: Feed | Posts für Nutzer 1 im Fenster [8. September 2025, 11. September 2025); bereits zu Fensterbeginn bestehende Follows |

Das Datenfenster richtet sich nach dem gelieferten Bestand. Die Plattformdaten liefern keine Unfollow-Historie. Alle vier Modellpakete verwenden diese Definitionen. Die TinyFlux-Demo erklärt zusätzlich die kürzere Abdeckung der ursprünglichen Tagesübersicht.

## Hinweise zur SQLite-Demonstration und zu den Vergleichswerten

- Zuerst Schlüssel und Beziehungen am [DDL](../../schemas/sqlite/microblogging.sql) erklären, dann den wiederholbaren Import zeigen.
- Q1 aggregiert die Detailtabellen vor dem Join; das verhindert die Multiplikation von Aktivitäten.
- Q5 verwendet Parameter und einen festen Bezug auf das Ende des Bestands. Die Abfrage liefert im Snapshot vier Posts: 23, 399, 204, 396 in dieser Reihenfolge.
- Q3 verwendet eine begrenzte rekursive CTE mit korrekter Zyklusprüfung. Das Beispiel liefert `/1/2/3/` mit zwei gerichteten Schritten. Es ist keine Aussage über die allgemeine Skalierbarkeit von Graphabfragen in SQL.
- Q4 ergänzt einen Kalender vor der gleitenden Berechnung, damit sieben Zeilen sieben Kalendertage abdecken.
- Top-Engagement: Nutzer 94 und 107 haben je 26 Aktivitäten, Nutzer 35 hat 25. Eine zusätzliche Sortierung nach ID macht Gleichstände reproduzierbar.

## Technische Einstiege

SQLite benötigt keinen Server und keine separate Installation; die Kursumgebung genügt. Die Demo speichert in `data/work/microblogging/storage.sqlite`. Wiederholtes Laden ersetzt ausschliesslich die Inhalte der fünf Demo-Tabellen, gemeinsam in einer Transaktion. Die UAP-Aufgabe besitzt eine eigene Datei.

Die [gemeinsame Vorbereitung](../../README_technical_preparation.md) bietet für den gesamten Block lokale Docker-Dienste, lokale Dienste ohne Docker und Codespaces. Für Neo4j bleibt die [Desktop-Option](../../docs/setup/NEO4J_DESKTOP.md) verfügbar; für MongoDB gibt es die [native Installation](../../docs/setup/MONGODB_LOKAL.md). MongoDB und Neo4j verwenden auf allen Betriebswegen dieselben Verbindungseinstellungen der Repo.

Die MongoDB-Demo speichert in `storage_microblogging` und verwendet `users`, `posts`, `follows` und `likes`. Kommentare sind in den Posts eingebettet; die Likes-CSV wird vollständig benötigt. Der Like-Zähler im Post wird gegen diese Ereignisse geprüft.

MongoDB Q3 gibt die begrenzte minimale **Distanz** 1 → 3 aus, keine geordnete Knotenfolge. Q4 zählt serverseitig pro Tag; Kalenderergänzung und gleitender Durchschnitt erfolgen anschliessend in pandas. Für die synthetischen, ursprünglich zeitzonenlosen Plattformzeitstempel gilt eine dokumentierte UTC-Lehrkonvention.

Die Eingaben für alle vier Modelle liegen im Repo bereit.


## Neo4j-Demonstration

In der [Neo4j-Demo](03_neo4j.ipynb) bilden Modellblick und Q3 den Kern. Alle fünf Fragen bleiben vollständig ausführbar. Der Import liest die vorhandenen relationalen CSV-Dateien, damit eindeutige Kommentar-/Like-IDs, Texte und Zeitpunkte erhalten bleiben; eine SQLite-Datenbank ist nicht erforderlich. Die Original-Graphdateien bleiben als Vergleich erhalten.

Der Graph speichert Nutzer, Posts sowie FOLLOWS-, AUTHORED-, LIKES- und COMMENTED-Beziehungen. 512 Kommentare bleiben 512 Beziehungen, auch bei wiederholten Kommentaren derselben Person zum selben Post. Q1 und Q3 zählen tatsächliche Beziehungen mit `count(r)` und vermeiden vervielfachte Treffer. Der Pfad 1 → 2 → 3 und das feste Feed-Fenster entsprechen den bisherigen Vergleichsdefinitionen.

Die Demo verwendet kursspezifische Labels und den Bereich `microblogging_demo` in der bestehenden Datenbank `neo4j`. Importe ersetzen nur diesen Bereich. Die UAP-Aufgabe und Musterlösung liegen getrennt.

### Nach dem Import: Graph anzeigen (optional)

Führe in [03_neo4j.ipynb](03_neo4j.ipynb) die Codezellen der Abschnitte **0 und 1** bis zur Ausgabe **IMPORT OK** aus. Das Notebook hat direkt in die laufende Datenbank geschrieben; Du musst keine Datei übertragen.

1. Die Oberfläche passend zu Deinem Weg öffnen: **A:** [Neo4j Browser](http://localhost:7474/browser/) der laufenden Docker-Datenbank; **B:** bei der laufenden Desktop-Kursinstanz **Open → Neo4j Browser** (1.x) oder **Connect → Query** (2.x); **C:** [Neo4j Browser im Codespace](../../docs/setup/NEO4J_START.md#weg-c-codespaces). Immer dieselbe Instanz wie im Notebook und die Datenbank **neo4j** verwenden. Benutzer **neo4j**, Passwort **`Storage-Neo4j-2026`** beziehungsweise Dein tatsächliches Passwort.
2. Die folgende Abfrage in das **Cypher-Eingabefeld dieser Oberfläche** kopieren, mit dem Play-Schalter ausführen und im Ergebnis **Graph** wählen. Diese Abfrage wird in Neo4j ausgeführt, nicht in einer Python-Codezelle.

```cypher
MATCH p = (:StorageUser {scope: 'microblogging_demo', user_id: 1})
          -[:FOLLOWS]->(:StorageUser {scope: 'microblogging_demo'})
RETURN p LIMIT 25;
```

Du siehst, wem Nutzer 1 folgt. Klicke auf einen Knoten oder eine Beziehung, um die Eigenschaften anzusehen. Nach Änderungen im Notebook genügt es, die Abfrage erneut auszuführen.

**Für die Graphansicht keinen zweiten Neo4j-Server starten.** Notebook und Oberfläche greifen auf dieselbe Instanz zu. Daten einer lokalen Instanz und Daten im Codespace sind getrennte Bestände.


## TinyFlux-Demonstration

In der [TinyFlux-Demo](04_tinyflux.ipynb) bilden Punktmodell, Zeitfenster und Q4 den Kern. Q1–Q3 und Q5 sind ausführbare Vertiefungen; täglich aktive Personen (DAU) ergänzen das ursprüngliche Beispiel. Zeit-, Tag- und Feldfilter liegen bei TinyFlux; Aggregation, Join, Pfadsuche, Kalenderergänzung und gleitender Durchschnitt bei Python/pandas.

Die vollständigen relationalen CSV-Eingaben liefern 5'690 einzelne Ereignisse. Ein erneuter Import ersetzt nur `data/work/microblogging/04_events.tinyflux.csv`. Es wird keine SQLite-Datenbank benötigt. Die vorhandene `daily_activity.csv` endet am 10. September 2025 und enthält dadurch 19 Likes und 18 Kommentare weniger als die Detaildaten. Die Demo zeigt diese Abweichung ausdrücklich; innerhalb des gemeinsamen Fensters stimmen die Zahlen überein.


## Cheat Sheet: Modelle im Vergleich

Die folgenden Abschnitte übernehmen Modellvergleich, Abfragestrukturen, Q1–Q5-Zuordnung, Setup-Hinweise, Fehlerbehebung und Vertiefungen aus dem ursprünglichen `00_workshop_handout.ipynb`. Namen, Pfade und Beispiele beziehen sich auf den aktuellen Repo-Stand. Die Einordnung beschreibt unseren Anwendungsfall; sie ist keine allgemeine Leistungsrangliste.

| Aspekt | SQLite / SQL | MongoDB / MQL | Neo4j / Cypher | TinyFlux / Python |
| --- | --- | --- | --- | --- |
| Modell | Tabellen, Zeilen, Spalten und Schlüssel | BSON-Dokumente mit Arrays, eingebetteten Objekten und Referenzen | Knoten und gerichtete Beziehungen mit Labels, Typen und Properties | Punkte mit `measurement`, `time`, `tags` und numerischen `fields` |
| Abfrageprinzip | `SELECT`, `JOIN`, `WHERE`, `GROUP BY` | `find` und Aggregation-Pipeline | `MATCH`, `WHERE`, `WITH`, `RETURN` | `TimeQuery`, `TagQuery`, `FieldQuery` |
| Modellierung im Beispiel | Getrennte Detailtabellen; Primär-/Fremdschlüssel und Constraints | Kommentare im Post eingebettet; Nutzer und Likes separat; kontrollierter Like-Zähler | Nutzer und Posts als Knoten; Follow-, Autor-, Like- und Kommentar-Beziehungen | Einzelne Aktivitätsereignisse; IDs und Typ als Tags, Zählwert als Field |
| Indizes und Identität | Indizes auf Such-/Join-Spalten; Fremdschlüsselprüfung pro Verbindung aktiviert | Eindeutige IDs und einfache/zusammengesetzte Indizes | Constraint auf Kursbereich und Knoten-ID; Beziehungen besitzen eigene Identitäten | Interne Indexierung; eindeutige Ereignis-/Serienidentitäten prüft unser Importcode |
| Stärken für diesen Fall | Verknüpfungen, tabellarische Auswertungen und Transaktionen | Akten-/Postansichten mit verschachtelten oder unterschiedlichen Feldern | Nachbarschaften, gerichtete Pfade und belegte Verbindungen direkt ausdrücken | Zeitfenster über explizite Ereignis- oder Intervallpunkte abfragen |
| Grenzen im Beispiel | Mehrschrittige Graphfragen benötigen zusätzliche SQL-Logik; Schemaänderungen sind bewusst zu behandeln | Redundante Zähler und Einbettung benötigen passende Änderungsregeln; geordnete Graphpfade erfordern Zusatzlogik | Reine tabellarische Auswertungen profitieren nicht automatisch vom Graphmodell | Joins, Gruppierung, Pfadsuche, Rolling und Resampling erfolgen in Python/pandas |
| Typische Einsatzfelder | Transaktionsdaten und Berichte | Inhalte, Kataloge und flexible Profile | Soziale Netze, Routing und Wissensgraphen | Messwerte, Telemetrie und zeitbezogene Kennzahlen |

Ein **Fremdschlüssel** ist eine Integritätsregel und nicht dasselbe wie ein Index. Im SQLite-Beispiel aktiviert der Verbindungscode die Prüfung ausdrücklich. Die Indizes stehen separat im [DDL](../../schemas/sqlite/microblogging.sql). [SQLite: Fremdschlüssel](https://www.sqlite.org/foreignkeys.html)

TinyFlux ist hier eine lokale Lernumgebung. Es unterstützt auch Änderungen und Löschungen; «append-only» wäre keine allgemeine Systemeigenschaft. Rolling, Resampling, DAU und Retention-Analysen sind nicht automatisch eingebaute Operationen dieses Beispiels. [TinyFlux: Projekt und API](https://github.com/citrusvanilla/tinyflux)

## Cheat Sheet: Abfragemuster

Die folgenden Muster setzen voraus, dass Du den Import im jeweiligen Demo-Notebook ausgeführt hast. SQL wird über die SQLite-Verbindung ausgeführt, Cypher in Neo4j Query oder über den Treiber, Python im jeweiligen Notebook. Eine SQL-/Cypher-Abfrage nicht unverändert in eine Python-Zelle kopieren: Die Notebooks zeigen den passenden Aufruf.

### SQL: gruppieren und auch Posts ohne Likes erhalten

Grundform: `SELECT … FROM … LEFT JOIN … WHERE … GROUP BY … ORDER BY … LIMIT …`.

```sql
SELECT p.post_id, COUNT(l.like_id) AS like_count
FROM posts AS p
LEFT JOIN likes AS l ON l.post_id = p.post_id
GROUP BY p.post_id
ORDER BY like_count DESC, p.post_id
LIMIT 5;
```

`COUNT(l.like_id)` zählt tatsächliche Likes. `COUNT(*)` würde beim Left Join auch die Ergebniszeile eines Posts ohne Like zählen. `GROUP BY` bestimmt die Zähleinheit; die zusätzliche ID-Sortierung löst Gleichstände reproduzierbar auf.

### MongoDB: filtern, projizieren und aggregieren

- Filter verwenden Operatoren wie `$gt` und `$in`; Gleichheit kann direkt als Feldwert stehen.
- Projektion wählt Felder mit `1` aus oder schliesst sie mit `0` aus. Beide Formen nicht mischen; `_id: 0` ist bei einer einschliessenden Projektion die übliche Ausnahme.
- `sort` und `limit` ordnen und begrenzen das Ergebnis auf dem Server.
- Eine Pipeline kombiniert beispielsweise `$match → $project → $group → $sort → $limit`. Die Reihenfolge richtet sich nach der Frage; benötigte Felder nicht vorzeitig entfernen. [MongoDB: find und Projektion](https://www.mongodb.com/docs/manual/reference/method/db.collection.find/)

**Python/PyMongo**, nach den Setup- und Importzellen in `02_mongodb.ipynb`:

```python
with mongo_workspace("microblogging") as (db, names):
    top_posts = list(db[names["posts"]].find(
        {}, {"_id": 1, "author_id": 1, "like_count": 1}
    ).sort([("like_count", -1), ("_id", 1)]).limit(5))
display(pd.DataFrame(top_posts))
```

`_id` ist hier die Post-ID. Auch Posts mit `like_count=0` bleiben in der Ausgangsmenge. Der Zähler wird beim Import gegen die Like-Ereignisse geprüft.

Die Zusatzfrage aus dem Handout, **empfangene Likes je Autor**, verwendet dagegen eine Aggregation:

```python
with mongo_workspace("microblogging") as (db, names):
    author_likes = list(db[names["posts"]].aggregate([
        {"$group": {"_id": "$author_id", "likes_received": {"$sum": "$like_count"}}},
        {"$sort": {"likes_received": -1, "_id": 1}},
        {"$limit": 5},
        {"$project": {"_id": 0, "author_id": "$_id", "likes_received": 1}}
    ]))
display(pd.DataFrame(author_likes))
```

Das ist eine andere Kennzahl als Q1: Dort zählen **gegebene** Likes zur Aktivität einer Person, hier die Likes, die ihre Posts empfangen haben.

### Cypher: Muster und tatsächliche Beziehungen zählen

Grundform: `MATCH (a)-[r:TYP]->(b) WHERE … WITH … RETURN … ORDER BY … LIMIT …`.

```cypher
MATCH (p:StoragePost {scope: 'microblogging_demo'})
OPTIONAL MATCH (:StorageUser {scope: 'microblogging_demo'})
               -[l:LIKES {scope: 'microblogging_demo'}]->(p)
RETURN p.post_id AS post_id, count(l) AS like_count
ORDER BY like_count DESC, post_id
LIMIT 5;
```

Die Labels und `scope` entsprechen der aktuellen Demo. `OPTIONAL MATCH` erhält Posts ohne Likes; `count(l)` zählt gefundene Beziehungen. Bei mehreren optionalen Beziehungsmustern zuerst pro Teilfrage aggregieren, damit die Kombination der Treffer keine Aktivitäten vervielfacht.

### TinyFlux: festes Zeitfenster und anschliessende Aggregation

**Python**, nach den Setup- und Importzellen in `04_tinyflux.ipynb`:

```python
since = datetime(2025, 9, 8, tzinfo=timezone.utc)
until = datetime(2025, 9, 11, tzinfo=timezone.utc)
query = (Time >= since) & (Time < until) & (Tag.type == "like")
like_points = search_points("microblogging", query)
like_rows = points_frame(like_points)
if like_rows.empty:
    print("Keine Like-Ereignisse in diesem Zeitfenster.")
else:
    like_rows["post_id"] = like_rows["post_id"].astype(int)
    top = like_rows.groupby("post_id")["value"].sum().astype(int).rename("like_count").reset_index()
    display(top.sort_values(["like_count", "post_id"], ascending=[False, True]).head(5))
```

TinyFlux führt den Filter aus; pandas summiert danach die Zählfelder. Das feste halboffene Fenster liegt im gelieferten Datenbestand. Diese Zusatzabfrage zählt nur Likes im Fenster und zeigt nur Posts mit solchen Likes; Q2 im vollständigen Notebook umfasst dagegen den gesamten Bestand und erhält auch Posts ohne Likes. `Field.value > 0` wäre ein Beispiel für einen zusätzlichen numerischen Feldfilter.

## Q1–Q5: Umsetzung je Modell

| Frage | SQLite | MongoDB | Neo4j | TinyFlux |
| --- | --- | --- | --- | --- |
| Q1: Aktivität | Detailtabellen zuerst aggregieren, dann verknüpfen | `$unwind`, `$unionWith`, `$group`; Nutzer ohne Aktivität erhalten | Beziehungen getrennt zählen und Teilergebnisse zusammenführen | Aktivitätstypen filtern; pandas gruppiert je Nutzer und Typ |
| Q2: Likes pro Post | Left Join und `COUNT(like_id)` | Den geprüften `like_count` im Post verwenden | `OPTIONAL MATCH` und `count(l)` | Like-Ereignisse filtern; pandas zählt und ergänzt alle Posts |
| Q3: Beziehungen | Degree-Zählungen und rekursive CTE mit Zyklusprüfung | Aggregation und begrenztes `$graphLookup`; die Demo liefert die Distanz | Gerichtetes Pfadmuster mit `shortestPath` | Follow-Ereignisse abrufen; Degrees und Breitensuche in Python |
| Q4: Tagesverlauf | Tagesaggregation, Kalender und Window-Funktion | Tagesaggregation auf dem Server; Kalender und Rolling in pandas | Tagesaggregation per Cypher; Kalender und Rolling in pandas | Posts filtern; Tagesaggregation, Kalender und Rolling in pandas |
| Q5: Feed | Follow-/Post-Verknüpfung und Zeitfilter | Follow-Ziele bestimmen, Post-Abfrage mit Zeitfilter | Pfadmuster Nutzer → Follow-Ziel → Post mit Zeitfilter | Follow- und Post-Ereignisse filtern; Verknüpfung in Python/pandas |

Für den Modellvergleich gelten die oben definierten Kennzahlen und Zeitfenster. Modellspezifische Zusatzfragen haben ihre eigene Zähleinheit. Die gewählte Implementierung in der Demo ist jeweils eine Möglichkeit, keine vollständige Aufzählung der Fähigkeiten des Systems.

## Dateien und Arbeitsbereiche auf einen Blick

| Bereich | Inhalt |
| --- | --- |
| `demos/microblogging/` | Vier ausführbare Demo-Notebooks und dieses Handout |
| `data/microblogging/relational/` | Nutzer, Posts, Likes, Kommentare und Follow-Beziehungen als CSV |
| `data/microblogging/document/` | Vorbereitete JSONL-Dokumente |
| `data/microblogging/graph/` | Ursprüngliche Knoten-/Kanten-CSVs als Vergleich |
| `data/microblogging/timeseries/` | Ursprüngliche Tagesübersicht mit dokumentierter Abdeckung |
| `data/work/microblogging/` | Erzeugte SQLite-/TinyFlux-Dateien |
| MongoDB `storage_microblogging` | Collections der MongoDB-Demo |
| Neo4j `neo4j`, Scope `microblogging_demo` | Bereich der Neo4j-Demo |

Die Umgebung heisst **rothstein-storage-workshop-2026**. Die gemeinsame Paketliste steht in [requirements.txt](../../requirements.txt). Für diese Beispiele keine zweite Umgebung `dbworkshop` und keine abweichenden Einzelinstallationen anlegen. Die Originaldaten werden nicht durch erzeugte Arbeitsdaten überschrieben.

## Fehlerbehebung

| Beobachtung | Nächster Schritt |
| --- | --- |
| Tabelle wird im Notebook nicht lesbar dargestellt | Den konkreten DataFrame beispielsweise mit `print(df.head(10).to_string(index=False))` anzeigen; `df` durch Deinen Variablennamen ersetzen. Der alte Helfer `show_df` wird nicht vorausgesetzt. |
| Neo4j/Bolt nicht erreichbar | Zuerst den Betriebsweg prüfen: **A:** Neo4j-Container; **B:** Desktop-Kursinstanz; **C:** automatischer Neo4j-Service. [Startanleitung](../../docs/setup/NEO4J_START.md). Unter Windows lokal optional **in PowerShell** `Test-NetConnection 127.0.0.1 -Port 7687`; das prüft nur den Port, nicht die Datenbankanmeldung. |
| `localhost`/IPv6-Verbindung problematisch | Die Repo verwendet lokal ausdrücklich `127.0.0.1`; `NEO4J_HOST`, Port und tatsächliches Passwort kontrollieren. |
| MongoDB nicht erreichbar | Den [nativen Serverdienst](../../docs/setup/MONGODB_LOKAL.md#dienst-starten-und-stoppen) starten; Benutzer und Anmeldung prüfen. Compass und der Python-Treiber ersetzen den Server nicht. |
| Nach Änderung des Passworts weiter ein Fehler | Tatsächliches Serverpasswort in `.env` hinterlegen und Kernel neu starten. `.env` setzt kein Datenbankpasswort zurück. |
| Port bereits belegt | Prüfen, ob noch ein Container oder eine andere lokale Instanz denselben Port verwendet. Den im Kurs tatsächlich verwendeten Dienst und dessen Port eindeutig wählen. |
| TinyFlux-Datei fehlt oder Abfrage ist leer | Importzellen ausführen und das feste Zeitfenster prüfen. Die Demo leitet Ereignisse aus den vorhandenen relationalen CSVs ab; eine zusätzliche `events.csv` wird nicht benötigt. |
| Python-Paket nicht gefunden | Notebook-Kernel **Python (rothstein-storage-workshop-2026)** und aktives Conda-Environment prüfen; siehe [Vorbereitung](../../README_technical_preparation.md). |

## Optionale Vertiefungen

| Modell | Vertiefung aus dem ursprünglichen Handout, auf den Kurs bezogen |
| --- | --- |
| SQLite | Abfragepläne mit/ohne passenden Index vergleichen; eine View für wiederkehrende Auswertungen formulieren. Eine materialisierte Ergebnistabelle wäre eine eigene Ableitung mit expliziter Aktualisierung, kein eingebautes `CREATE MATERIALIZED VIEW`. [SQLite: Views](https://www.sqlite.org/lang_createview.html) |
| MongoDB | Eine Suchpipeline mit `$search` untersuchen. Dafür eine unterstützte Suchumgebung und einen Suchindex gesondert bereitstellen; die Kurs-Community-Installation setzt dies nicht voraus. [MongoDB: Suchstufe](https://www.mongodb.com/docs/manual/reference/operator/aggregation/search/) |
| Neo4j | PageRank oder Community Detection auf einem bewusst gewählten Graphen untersuchen. Dafür ist etwa die Graph Data Science Library zusätzlich nötig; die Pflichtdemo benötigt weder GDS noch APOC. [Neo4j GDS: PageRank](https://neo4j.com/docs/graph-data-science/current/algorithms/page-rank/) |
| TinyFlux | Aktivität nach anderen Intervallen aggregieren und auffällige Werte, etwa mit einem z-Score, diskutieren. Resampling und Bewertung erfolgen nach dem Abruf in Python/pandas; ein auffälliger Wert ist nicht automatisch ein Datenfehler. |

