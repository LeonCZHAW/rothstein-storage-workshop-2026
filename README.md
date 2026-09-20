[Workshop-Übersicht](README.md) · [Technische Vorbereitung](README_technical_preparation.md) · [Microblogging-Beispiele](demos/microblogging/README.md) · [SQLite](tasks/01_sqlite/README.md) · [MongoDB](tasks/02_mongodb/README.md) · [Neo4j](tasks/03_neo4j/README.md) · [TinyFlux](tasks/04_tinyflux/README.md)

---

**Datengrundlage und Quellen**

[UAP-Katalog und Datenwörterbuch](data/README.md) · [Microblogging-Daten](data/microblogging/README.md) · [Aktenleseführer](docs/AKTENLESEFUEHRER.md) · [Ingestion-Code](ingestion/README.md) · [Quellenprüfung](docs/QUELLENPRUEFUNG.md)

# rothstein-storage-workshop-2026

![Akten, Microblogging und Graphmodelle](assets/teaser.png)

## UFO-Akten unter der Lupe

**375 Katalogeinträge. Vier Speichermodelle. Was lässt sich aus den Akten tatsächlich ableiten?**

## Dein Rechercheauftrag

Eine leuchtende Kugel, aus der weitere Lichter zu kommen scheinen. Ein Objekt, das zunächst wie ein Auto wirkt. Ein Dreieck, durch das nach Aussage eines Beobachters der Nachthimmel sichtbar bleibt. Solche Schilderungen stehen in den hier ausgewählten Zeugenberichten. Andere Akten dokumentieren, wie spektakuläre Meldungen überprüft und zurückgewiesen wurden.

Du arbeitest im Data-Engineering-Team einer fiktiven Forschungsredaktion. Die Redaktion möchte diese Unterlagen recherchierbar machen: Welche Dokumente gehören laut Katalog zusammen? Was ist eine Zeugenaussage, was eine nachträgliche Illustration und was eine behördliche Bewertung? Und welche Zahlen lassen sich verlässlich veröffentlichen?

Dein Team baut dafür vier Sichten auf denselben Bestand. Das Ergebnis soll jede Aussage bis zu ihrem Katalogeintrag und zur Originalquelle nachvollziehbar machen. Die Akten sind real; die Redaktion und ihre Aufträge bilden unseren didaktischen Rahmen.

## Welcher Datensatz wird verwendet?

Die Quelle ist der offizielle **PURSUE-Katalog** (*Presidential Unsealing and Reporting System for UAP Encounters*). Das US-Portal veröffentlicht UAP-bezogene Unterlagen im Rahmen der 2026 unter Präsident Trump angestossenen Freigabeinitiative. UAP steht für *Unidentified Anomalous Phenomena*, also nicht identifizierte anomale Phänomene. Die Veröffentlichung eines Berichts bestätigt zunächst dessen Zugänglichkeit; sie bestätigt keine darin vermutete Erklärung. [Offizielles Portal und Hintergrund](https://www.war.gov/ufo/)

Wir verwenden einen festgehaltenen Download des [offiziellen CSV-Katalogs](https://www.war.gov/Portals/1/Interactive/2026/UFO/uap-data.csv?release=5). Dadurch arbeiten alle Teilnehmenden mit demselben Datenstand, auch wenn das Portal später ergänzt wird.

| Merkmal | Unser Workshop-Bestand |
| --- | --- |
| Abrufdatum | 10. September 2026 |
| Umfang | 375 Katalogeinträge aus fünf Veröffentlichungsrunden vom 8. Mai bis 7. August 2026 |
| Katalogstellen | Zehn Stellen, darunter FBI, CIA, NASA sowie die US-Ministerien für Verteidigung und Aussenpolitik; Quellbezeichnungen bleiben erhalten |
| Originalfelder | Titel, Beschreibung, Stelle, Medientyp, Veröffentlichungsdatum, Incident Date, Ort, Datei-/Medienverweise und Pairing-Verweise |
| Medienarten | Dokumente, Bilder, Videos und Audio; der Medientyp folgt der Kennzeichnung des Portals |
| Lokal enthalten | Vollständiger Rohkatalog, aufbereitete Modellansichten und sieben gezielt ausgewählte Original-PDFs |
| Weitere Originalmedien | Über die offiziellen Links beziehungsweise Medienkennungen erreichbar |
| Sprache | Originalquellen auf Englisch; Workshop-Erklärungen auf Deutsch |

**Eine Zeile ist ein Katalogeintrag, keine einzelne Sichtung.** Eine Akte kann mehrere geschilderte Ereignisse umfassen; mehrere Einträge können auf dieselbe Datei verweisen. Die Beschreibungen stammen aus dem Portal und sind keine vollständigen PDF-Transkriptionen. Die sieben PDFs dienen als ausgewählte Lesestichprobe; die Datenmodelle nutzen alle 375 Katalogeinträge.

## Drei Einstiege in die Akten

| Recherchespur | Warum sie interessant ist | Direkt zu den Originalen |
| --- | --- | --- |
| **Western USA: Was wurde beobachtet – und was später illustriert?** | Zwei Zeugen schildern ungewöhnliche Lichter und scheinbar schwebende Objekte. Ein Bericht enthält ausdrücklich nachträglich KI-generierte Bilder. Eine separate AARO-Analyse prüft Erklärungen und benennt offene Fragen. | [Zeuge 1](data/raw/originals/DOW-UAP-D079.pdf), [Zeuge 2](data/raw/originals/DOW-UAP-D080.pdf), [Analyse vom 5. Juni 2026](data/raw/originals/DOW-UAP-D077.pdf) |
| **FBI-Interviews: Eine Akte, mehrere Beobachtungen** | Ein Pilot berichtet von Lichtern auf Flügen und einer älteren Dreiecksbeobachtung. Ein weiteres Interview beschreibt ein scheinbar durchscheinendes Dreieck. Beobachtungs-, Interview- und Veröffentlichungsdatum unterscheiden sich. | [Piloteninterview](data/raw/originals/FBI-UAP-D024.pdf), [Colorado Springs](data/raw/originals/FBI-UAP-D026.pdf) |
| **Brasilien 1963: Was bleibt von einer Absturzmeldung?** | Diplomatische Korrespondenz greift eine spektakuläre Pressemeldung auf und dokumentiert anschliessend eine negative Überprüfung. Beide Dokumente müssen gemeinsam gelesen werden. | [Depesche vom 14. November](data/raw/originals/DOS-UAP-D001.pdf), [Folgebericht vom 20. November](data/raw/originals/DOS-UAP-D002.pdf) |

Der [Aktenleseführer](docs/AKTENLESEFUEHRER.md) nennt konkrete Seiten, die jeweilige Quellenart und Fragen für Deine Recherche. Er erklärt auch die Auswahl der PDFs.

## Welche Fragen beantworten die Speichermodelle?

| Modell | Recherchefrage | Modellierungsentscheidung |
| --- | --- | --- |
| **SQLite** | Wie viele verschiedene Einträge und verlinkte Dateien enthält ein Dokumentationskomplex? | Schlüssel, Fremdschlüssel und Zwischentabellen; Mehrfachzählungen vermeiden |
| **MongoDB** | Wie lässt sich eine Akte mit ihren unterschiedlich gefüllten Metadaten und Verweisen zusammen abrufen? | Verschachtelte Dokumente; Einbettung und Referenzen abwägen |
| **Neo4j** | Welche ausdrücklich verknüpften Unterlagen erreiche ich über mehrere Schritte? | Knoten und gerichtete Portalverweise; Bedeutung eines Pfads begründen |
| **TinyFlux** | Wie verteilen sich die geeigneten Katalogeinträge auf die genannten Ereignisjahre und Stellen? | Jahreszählungen mit Tags und definierten Zeitfenstern speichern |

Die vier Sichten dienen dem Vergleich der Modelle. Die geringe Datenmenge erfordert technisch keine vier verschiedenen Datenbanksysteme.

## So bleiben Aussagen nachvollziehbar

- **Aussage, Abbildung und Bewertung unterscheiden.** Eine Zeugenschilderung ist eine Aussage über eine Wahrnehmung. Eine spätere Rekonstruktion ist keine Aufnahme des Ereignisses. Eine Bewertung hat einen Urheber, einen Geltungsbereich und einen Stand.
- **Verknüpfungen präzise benennen.** Die 336 aufgelösten Pairing-Verweise belegen Portalzuordnungen. Ein Graphpfad beweist weder eine gemeinsame Ursache noch mehrere unabhängige Beobachtungen. 13 nicht eindeutig aufgelöste Token bleiben dokumentiert.
- **Schlüssel prüfen.** `FBI-UAP-D014` bezeichnet im Quellkatalog zwei unterschiedliche Einträge. Beide bleiben unter getrennten technischen IDs erhalten.
- **Zeitreihen richtig lesen.** 292 Einträge sind einem Jahr zuordenbar; 83 werden wegen fehlender oder mehrdeutiger Datumsangaben ausgeschlossen. Gezählt werden die im Katalog genannten Ereignisjahre. Das ist keine Statistik der tatsächlichen Sichtungshäufigkeit. Ein Nullwert bedeutet nur, dass dieser Snapshot keinen geeigneten Eintrag für die Kombination enthält.
- **Quellengenauigkeit erhalten.** Fehlende Angaben bleiben fehlend. Ungenaue Datierungen, Schwärzungen und Widersprüche werden kenntlich gemacht. Der Katalog ist kein repräsentativer Gesamtdatensatz aller UAP-Meldungen.

## Datenaufbereitung selbst nachvollziehen

Im Repo-Ordner mit Python ab Version 3.10:

```bash
python ingestion/ingest.py verify
python ingestion/ingest.py build
```

Diese Befehle benötigen nur die Python-Standardbibliothek und den mitgelieferten Snapshot. Im separaten [Ingestion-Bereich](ingestion/README.md) findest Du auch den Code für einen neuen Quellenabruf. Für die Storage-Aufgaben steht der aufbereitete Bestand bereits zur Verfügung.

## Einstieg und Arbeitsweise

Beginne mit der [technischen Vorbereitung](README_technical_preparation.md) und führe das [Setup-Notebook](notebooks/00_setup_check.ipynb) aus. Die [Microblogging-Demonstrationen](demos/microblogging/README.md) und die [vier UAP-Aufgaben](tasks/README.md) erhalten getrennte Eingaben und Arbeitsbereiche. Jede Aufgabe kann direkt mit ihrem vorbereiteten Eingabestand starten.

Die [technische Vorbereitung](README_technical_preparation.md) bietet drei Einstiege: **Weg A: lokal mit Docker**, **Weg B: lokal ohne Docker** und **Weg C: Codespaces**. Alle drei verwenden dieselben Notebooks und die gemeinsame Python-Paketliste in `requirements.txt`.

Die lokalen Befehle können auch in [Bash oder Git Bash](docs/setup/BASH.md) ausgeführt werden. Für [Neo4j im Codespaces-Browser](docs/setup/NEO4J_START.md#weg-c-codespaces): **Ports → 8080 → Open in Browser → Neo4j Browser öffnen**.

**Für Neo4j genau einen Server wählen:** [Start und Graphansicht für alle drei Wege](docs/setup/NEO4J_START.md). Lokal dürfen der Neo4j-Container und eine Desktop-Instanz nicht gleichzeitig die Standardports belegen. Bereits eingerichtete Umgebungen: [Aktualisierungshinweise](docs/setup/AKTUALISIERUNG.md).

Für den Docker-Weg gibt es eine [Installationsanleitung](docs/setup/INSTALLATION.md). Der [Weg ohne Docker](docs/setup/OHNE_DOCKER.md) verwendet MongoDB Community Server und Neo4j Desktop und erklärt auch Benutzeranlage, Dienststart und Persistenz. Alle Wege führen zum gleichen Python-Setup-Check mit **SETUP OK**.

Halte bei den Aufgaben fest, welche Speicherentscheidung Du triffst, welche Abfrage sie unterstützt und welche Information dabei erhalten bleiben muss. Aufgabe, Musterlösung und Walkthrough liegen für alle vier Modelle als eigenständige Dateien direkt im jeweiligen Aufgabenordner.

## Verfügbare Modellpakete

| Modell | Demonstration | Deine Aufgabe | Gemeinsame Besprechung |
| --- | --- | --- | --- |
| SQLite | [Microblogging](demos/microblogging/01_sqlite.ipynb) | [Katalog, Schlüssel und Zähleinheiten](tasks/01_sqlite/task.ipynb) | [Musterlösung](tasks/01_sqlite/task_sample_solution.ipynb) · [Walkthrough](tasks/01_sqlite/WALKTHROUGH.md) |
| MongoDB | [Microblogging](demos/microblogging/02_mongodb.ipynb) | [Aktenansicht und belegte Lesernotizen](tasks/02_mongodb/task.ipynb) | [Musterlösung](tasks/02_mongodb/task_sample_solution.ipynb) · [Walkthrough](tasks/02_mongodb/WALKTHROUGH.md) |
| Neo4j | [Microblogging](demos/microblogging/03_neo4j.ipynb) | [Belegte Verbindungen](tasks/03_neo4j/task.ipynb) | [Musterlösung](tasks/03_neo4j/task_sample_solution.ipynb) · [Walkthrough](tasks/03_neo4j/WALKTHROUGH.md) |
| TinyFlux | [Microblogging](demos/microblogging/04_tinyflux.ipynb) | [Jahreszählungen und Zeitfenster](tasks/04_tinyflux/task.ipynb) | [Musterlösung](tasks/04_tinyflux/task_sample_solution.ipynb) · [Walkthrough](tasks/04_tinyflux/WALKTHROUGH.md) |

SQLite und TinyFlux laufen direkt in der Kursumgebung. MongoDB verwendet den eingerichteten Server über Docker, die native Installation oder Codespaces. Aufgabe und Musterlösung besitzen jeweils getrennte Arbeitsbereiche.

Im MongoDB-Auftrag ergänzt Du eine eigene Lesernotiz zur Originalakte D080, mit technischem Verweis und PDF-Seitenbeleg. Die Notiz liegt getrennt vom Katalog und bleibt bei einem erneuten Quellenimport erhalten. Ein Filter auf unterschiedliche Quellmetadaten und eine Aggregation führen die Recherche weiter.

Im Neo4j-Auftrag verfolgst Du gerichtete Portalverweise ab D077, prüfst ihre Belege und unterscheidest Pfade von erreichbaren Zielakten. Demo, Aufgabe und Musterlösung verwenden separate Graphbereiche.

Im TinyFlux-Auftrag speicherst Du Jahreszählungen, filterst ein FBI-Zeitfenster und interpretierst die Summe anhand der Datumsgrundlage. Ein Jahrespunktsatz ist kein einzelnes Ereignis; Nullwerte und ausgeschlossene Einträge haben unterschiedliche Bedeutungen. Aufgabe und Musterlösung verwenden eigene Dateien.

## Umgebung prüfen

Die [technische Vorbereitung](README_technical_preparation.md) führt durch Deinen Betriebsweg und die Verbindungsprüfung. Für die Beispiele ohne Docker findest Du zusätzlich einen [Microblogging-Schnellstart](demos/microblogging/README.md#ohne-docker-einsteigen).

Das [Datenwörterbuch](data/README.md) erklärt die Felder. Die [Quellenprüfung](docs/QUELLENPRUEFUNG.md) erklärt die Datengrundlage und ihre Grenzen. Herkunft und Prüfsummen stehen im [Katalogmanifest](data/raw/source_manifest.json) und im [PDF-Manifest](data/raw/sample_assets.json). Die Originaldateien bleiben unverändert.
