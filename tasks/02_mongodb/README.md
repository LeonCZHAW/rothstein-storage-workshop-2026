[Workshop-Übersicht](../../README.md) · [Technische Vorbereitung](../../README_technical_preparation.md) · [Microblogging-Beispiele](../../demos/microblogging/README.md) · [SQLite](../01_sqlite/README.md) · [MongoDB](README.md) · [Neo4j](../03_neo4j/README.md) · [TinyFlux](../04_tinyflux/README.md)

---

# Aufgabe 2: Aktenansicht und belegte Lesernotizen

Eine Zeugenaussage enthält eindrucksvolle Abbildungen. Die Redaktion möchte wissen: Sind das Aufnahmen des beschriebenen Ereignisses oder spätere Illustrationen? Gleichzeitig soll sie Akten mit unterschiedlich gefüllten Quellmetadaten gezielt finden können.

**Dein Ergebnis:** eine gespeicherte, mit PDF-Seiten belegte Lesernotiz, ein Filter auf ein optionales Quellfeld, eine Aggregation und Deine Entscheidung zu Einbettung und Referenzen.

## Dateien und Einstieg

| Datei | Zweck |
| --- | --- |
| [task.ipynb](task.ipynb) | Dein Aufgaben-Notebook mit TODO-Zellen |
| [task_sample_solution.ipynb](task_sample_solution.ipynb) | Separate, eigenständig ausführbare Musterlösung |
| [WALKTHROUGH.md](WALKTHROUGH.md) | Referenzwerte, Interpretation und typische Fehler |
| [Dokumentmodell](../../schemas/mongodb/README.md) | Collections, Schlüssel und Importverhalten |
| [Aktenleseführer](../../docs/AKTENLESEFUEHRER.md) | Quellenarten und konkrete PDF-Seiten |

Verwende die bestehende Kursumgebung mit dem Kernel **Python (rothstein-storage-workshop-2026)**. MongoDB muss tatsächlich laufen: [Docker/Codespaces](../../README_technical_preparation.md) oder [MongoDB Community Server ohne Docker](../../docs/setup/MONGODB_LOKAL.md). Für diesen Modellblock ist der MongoDB-Dienst erforderlich; Neo4j wird von den MongoDB-Notebooks nicht angesprochen. Weitere Pakete, Atlas-Konten oder ein Replica Set brauchst Du für diese Aufgabe nicht.

Die Aufgabe startet direkt mit `data/input/document/catalog_documents.jsonl`. Sie benötigt weder die SQLite-Datenbank noch den Import der Microblogging-Demo. Die Originaldateien bleiben erhalten.

## Lernziele

Nach dieser Aufgabe kannst Du:

- ein Dokument mit eingebetteten Metadaten und Array-Feldern lesen;
- Einbettung, redundante Snapshot-Angaben und Referenzen begründen;
- eigene Interpretationen getrennt vom Originalkatalog mit Belegen speichern;
- fehlende Quellfelder und vorhandene Werte unterscheiden;
- mit einer Aggregation die gewünschte Einheit zählen;
- Schemavalidierung von referentieller Integrität und inhaltlicher Richtigkeit unterscheiden.

## Teil A: Akte und Lesernotiz

Lade den vorbereiteten Dokumentbestand und öffne `DOW-UAP-D080`. Untersuche die eingebetteten Felder `agency`, `assets`, `source_metadata` und die Verweise in `related_entries`.

Lies anschliessend [D080, besonders Seite 5](../../data/raw/originals/DOW-UAP-D080.pdf). Ergänze im Notebook eine eigene Notiz mit verschachtelten Feldern für Befund und Beleg. `entry_id` und `asset_id` referenzieren die gelesene Akte; `pdf_pages` enthält die belegenden Seitenzahlen. `origin="workshop_manual_review"` kennzeichnet Deine eigene Einordnung.

Speichere dieselbe Notiz zweimal. Es soll eine Notiz pro Katalogeintrag und Arbeitsbereich bestehen bleiben. Öffne eine neue Verbindung und prüfe, ob der gespeicherte Inhalt erhalten ist.

Begründe, welche Informationen Du zusammen einbettest und welche Du referenzierst. Erkläre auch, weshalb ein erneuter Quellenimport Deine Notiz nicht überschreiben soll.

## Teil B: Heterogene Metadaten abfragen

1. Filtere auf das vorhandene Originalfeld `source_metadata.PDF Pairing` mit `$exists`.
2. Prüfe zusätzlich die Gegenmenge ohne dieses Feld. Erkläre den Unterschied zwischen fehlend und vorhanden mit `null`.
3. Gruppiere die gefilterten Einträge nach `media_type`. Die Ausgabefelder heissen `media_type` und `catalog_entries`.
4. Formuliere die Grenze der Aussage: Was sagt ein fehlender Katalogverweis über den tatsächlichen Zusammenhang zwischen Akten aus?

Zähle **Katalogdokumente**, keine Pairing-Token, Assets oder Ereignisse. Ein Dokument der Medienart PDF kann Illustrationen enthalten; ein Videoeintrag kann zusätzlich einen PDF-Verweis besitzen.

## Teil C: Vertiefung

- Verwende `$elemMatch`, um zwei Bedingungen an dasselbe Asset-Element zu stellen: `locator_type="url"` und `format_hint="pdf"`.
- Prüfe einen vorbereiteten JSON-Schema-Validator auf einer eigenen Probe-Collection. Beobachte, warum eine Seitenangabe als Text abgelehnt wird, eine formal passende Referenz auf einen nicht vorhandenen Eintrag aber die Typprüfung bestehen kann.

## Arbeitsbereiche und Wiederholung

| Verwendung | Datenbank | Collections |
| --- | --- | --- |
| Deine Aufgabe | storage_uap | catalog, reading_notes |
| Musterlösung | storage_uap | catalog_sample_solution, reading_notes_sample_solution |
| Microblogging-Demo | storage_microblogging | users, posts, follows, likes |

Der Katalogimport stellt die Dokumente der gewählten `catalog`-Collection aus dem festen Snapshot wieder her. Änderungen an diesen importierten Katalogdokumenten werden dabei überschrieben. Die separate Notiz-Collection bleibt erhalten. Die Notiz-ID `note:<entry_id>` definiert hier bewusst **eine** Notiz pro Eintrag; eine Anwendung mit mehreren Autorinnen oder einer Versionshistorie würde ein erweitertes Schlüsselmodell benötigen.

Der gesamte Import ist auf dem verwendeten Einzelserver nicht atomar. Nach einem Abbruch wiederholst Du ihn und arbeitest erst nach `IMPORT OK` weiter. Vollständig ausgefüllte Kernaufgaben melden **MONGODB AUFGABE TECHNISCH OK**; die schriftliche Interpretation prüfst Du zusätzlich.

Die Daten liegen auf dem MongoDB-Server beziehungsweise in dessen Volume, nicht in Deiner Conda-Umgebung. Ein Git-Push sichert keine MongoDB-Inhalte. Ein Wechsel zwischen Docker und nativer Installation wechselt den Datenbestand, sofern er nicht ausdrücklich übertragen wird.

## Technische Rückmeldungen

Bei `ServerSelectionTimeoutError` zuerst Dienststart, Host/Port und Anmeldung mit der [technischen Vorbereitung](../../README_technical_preparation.md#mongodb-oder-neo4j-meldet-failed) prüfen. Codespaces verwendet den Host `mongodb`; lokal ist es standardmässig `127.0.0.1`. Das Notebook übernimmt dies aus den gemeinsamen Verbindungshilfen.

Die optionale Schema-Probe verwendet nur ihre selbst erzeugte Collection und entfernt sie danach. Sie erfordert keine Erweiterung des dokumentierten nativen Kurskontos.
