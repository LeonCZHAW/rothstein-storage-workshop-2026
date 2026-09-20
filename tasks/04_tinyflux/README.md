[Workshop-Übersicht](../../README.md) · [Technische Vorbereitung](../../README_technical_preparation.md) · [Microblogging-Beispiele](../../demos/microblogging/README.md) · [SQLite](../01_sqlite/README.md) · [MongoDB](../02_mongodb/README.md) · [Neo4j](../03_neo4j/README.md) · [TinyFlux](README.md)

---

# Aufgabe 4: Jahreszählungen mit TinyFlux

Die Forschungsredaktion möchte den zeitlichen Verlauf ihres Katalogbestands zeigen. Du bereitest eine Jahresreihe auf und beantwortest: **Wie viele geeignete FBI-Katalogeinträge entfallen auf die Jahre 2020 bis einschliesslich 2023? Was sagt die Zahl aus?**

## Deine Dateien

- [task.ipynb](task.ipynb): Deine Bearbeitung;
- [task_sample_solution.ipynb](task_sample_solution.ipynb): eigenständige Musterlösung;
- [WALKTHROUGH.md](WALKTHROUGH.md): gemeinsame Erläuterung;
- [Microblogging-Demo](../../demos/microblogging/04_tinyflux.ipynb): Ereignispunkte und Zeitfenster;
- [Aktenleseführer](../../docs/AKTENLESEFUEHRER.md): Quellenkontext und PDF-Seitenbelege.

## Einstieg

Wähle den Kernel **Python (rothstein-storage-workshop-2026)**. TinyFlux 1.2.0 ist bereits installiert. Für diese Aufgabe brauchst Du keinen Datenbankserver und keine Ergebnisse aus früheren Workshops. Lokal und in Codespaces wird derselbe Python-Code verwendet.

Die Eingabe `data/input/timeseries/annual_catalog_counts.csv` enthält 820 Jahres-/Stellenpunkte mit einer Zählsumme von 292 geeigneten Katalogeinträgen. Die weiteren 83 Einträge haben keine eindeutige Jahreszuordnung. Die sieben Original-PDFs und alle Eingaben liegen bereits im Repository.

## Dein Auftrag

| Teil | Tätigkeit | Ergebnis |
| --- | --- | --- |
| A | Zeitpunkt, Tags und numerisches Zählfeld eines TinyFlux-Punkts ergänzen; Import wiederholen | Jahresreihe mit 820 Punkten ohne Doppelzählung; begründete Modellierung |
| B | FBI-Zeitfenster mit eingeschlossener Unter- und ausgeschlossener Obergrenze abfragen; Zählwerte summieren und Grafik beschriften | Jahrestabelle und Grafik mit korrekter Veröffentlichungsaussage |
| C, optional | Positive Zählwerte filtern und Dekadensummen vergleichen | Unterschied zwischen Nullpunkt, ausgeschlossenem Eintrag und gröberem Intervall erläutern |

Ergänze die markierten Stellen. Unbearbeitete Zellen melden **OFFEN**; das Aufgaben-Notebook lässt sich bereits im Ausgangszustand von oben nach unten ausführen. Die Musterlösung ersetzt Dein Notebook nicht.

## Was die Reihe bedeutet

Ein Punkt zählt geeignete Katalogeinträge für eine Stelle und ein Jahr. `period_start` ist der technische Beginn dieses Jahresintervalls; der 1. Januar ist kein erschlossenes Ereignisdatum. `date_basis` und `snapshot_sha256` erhalten die Datumsgrundlage und die Herkunft der Ableitung.

Ein Nullwert bedeutet, dass der fixierte Snapshot für diese Kombination keinen geeigneten Katalogeintrag enthält. Er bedeutet nicht «keine Sichtung». Mehrdeutige Jahre werden nicht geschätzt oder mehrfach verteilt. Der Bestand ist keine vollständige Erhebung realer Ereignisse; 2026 ist zusätzlich durch den Abrufstand begrenzt.

Die Akten FBI-UAP-D024 und FBI-UAP-D026 zeigen, weshalb Katalog-Ereignisjahr, Interviewjahr und eine Angabe über mehrere Jahre nicht austauschbar sind.

## Arbeitsdateien und Wiederholung

| Verwendung | Datei |
| --- | --- |
| Microblogging-Demo | `data/work/microblogging/04_events.tinyflux.csv` |
| Deine Aufgabe | `data/work/uap/04_annual_task.tinyflux.csv` |
| Musterlösung | `data/work/uap/04_annual_solution.tinyflux.csv` |

Der Import schreibt und prüft eine neue Datei und ersetzt erst danach die ausgewählte Arbeitsdatei. Eine Wiederholung setzt eigene Änderungen innerhalb dieser Datei zurück. Die anderen Arbeitsdateien bleiben erhalten. Pro Datei arbeitet ein schreibender Notebook-Ablauf; gleichzeitige Importe in dieselbe Datei sind nicht Teil des Beispiels.

Abgabe: ausgeführtes Notebook, Modellbegründung, Interpretation mit PDF-Seitenbeleg und Beitrag zur gemeinsamen Modellvergleichstabelle. Details zur Technik stehen unter [Modell und Import](../../schemas/tinyflux/README.md).
