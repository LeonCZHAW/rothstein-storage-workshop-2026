[Workshop-Übersicht](../README.md) · [Technische Vorbereitung](../README_technical_preparation.md) · [Microblogging-Beispiele](../demos/microblogging/README.md)

# Vier Perspektiven auf denselben UAP-Katalog

Jede Aufgabe startet unabhängig mit den vorbereiteten Dateien unter `data/input/`. Die eigene Datenbank entsteht im jeweils vorgesehenen Arbeitsbereich. Der eigenständige Ingestion-Bereich ist ein Zusatzangebot.

| Aufgabe | Eingang | Recherchefokus |
| --- | --- | --- |
| [1: SQLite](01_sqlite/README.md) | Relationale Tabellen | Schlüssel und Verknüpfungen; Einträge und Dateien unterscheiden |
| [2: MongoDB](02_mongodb/README.md) | Verschachtelte JSONL-Dokumente | Aktenansicht und unterschiedliche Metadaten |
| [3: Neo4j](03_neo4j/README.md) | Knoten und gerichtete Kanten | Dokumentierte Zusammenhänge über mehrere Schritte |
| [4: TinyFlux](04_tinyflux/README.md) | Jahreszählungen | Zeitfenster und fachlich richtige Zähleinheit |

**Alle vier Modelle sind als vollständige Materialpakete verfügbar.** Jeder Aufgabenordner enthält direkt `README.md`, `task.ipynb`, `task_sample_solution.ipynb` und `WALKTHROUGH.md`.

TinyFlux ergänzt Jahres-/Stellenpunkte, feste Zeitfenster und die Interpretation von Zählwerten anhand der Datumsgrundlage.

Neo4j ergänzt gerichtete Portalpfade, Belegtabellen und eine Graphansicht.

MongoDB ergänzt die Aktenansicht um eine separate eigene Lesernotiz mit Seitenbeleg.
