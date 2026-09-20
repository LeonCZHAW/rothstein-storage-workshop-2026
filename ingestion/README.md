[Haupt-README](../README.md) · [Microblogging-Beispiele](../demos/microblogging/README.md) · [Datengrundlage](../data/README.md) · [Quellenprüfung](../docs/QUELLENPRUEFUNG.md)

# Ingestion: Den Workshop-Datenbestand nachvollziehen

Der Code in [ingest.py](ingest.py) beschafft den offiziellen PURSUE-Katalog und bereitet daraus die gemeinsamen Storage-Eingaben auf. Er verwendet Python ab Version 3.10 und ausschliesslich die Standardbibliothek. Die Befehle gelten in Windows, macOS, Linux und Codespaces mit einer entsprechenden Python-Installation. Die gemeinsame Kursumgebung mit Python 3.12 ist in der [technischen Vorbereitung](../README_technical_preparation.md) beschrieben.

## Den mitgelieferten Stand prüfen

Im Repo-Ordner:

```bash
python ingestion/ingest.py verify
```

Die Prüfung kontrolliert die Original- und Ausgabeprüfsummen, baut den Datenbestand in einem temporären Ordner erneut auf und vergleicht ihn mit den mitgelieferten Dateien. Die sieben Original-PDFs werden ebenfalls anhand ihrer Prüfsummen geprüft.

## Den mitgelieferten Stand erneut aufbereiten

```bash
python ingestion/ingest.py build
```

Der Befehl schreibt die benannten generierten Dateien unter `data/input/` neu. Studentische Notebooks und Datenbankdienste sind davon unabhängig. Ein alternatives Ziel ist möglich:

```bash
python ingestion/ingest.py build --output-dir data/work/rebuilt
```

Für denselben Rohkatalog und dieselbe Pipeline entstehen dieselben Ausgabebytes. Der aktuelle Systemzeitpunkt beeinflusst die Aufbereitung nicht. Die Kennungen der Katalogeinträge leiten sich aus Veröffentlichungsdatum und Quellschlüssel ab. Sie bleiben bei erneutem Import stabil; sie sind keine universellen Ereignis-IDs.

## Einen neuen Live-Snapshot abrufen

```bash
python ingestion/ingest.py fetch --output-dir data/work/live_snapshot
python ingestion/ingest.py build --raw-dir data/work/live_snapshot --output-dir data/work/live_input
```

Der Zielordner des Abrufs muss neu sein. Ein Abruf erzeugt Roh-CSV und Herkunftsmanifest, ohne den Kurs-Snapshot zu ersetzen. Das Schema wird geprüft; Herkunft, Prüfsumme und Abrufdatum werden festgehalten. Die bekannten Portal-Kurzformen werden nach denselben transparenten Regeln aufgelöst. Neue oder mehrdeutige Verweise landen im Qualitätsbericht.

Die Datenquelle kann neue Einträge oder Korrekturen enthalten. Ein Live-Abruf reproduziert deshalb nicht zwingend den früheren Snapshot. Der Queryparameter `release=5` stammt aus dem Portalcode; der mitgelieferte Snapshot umfasst alle fünf Veröffentlichungsrunden.

## Die sieben Original-PDFs erneut abrufen

```bash
python ingestion/ingest.py fetch-samples --output-dir data/work/originals_download
```

Die URLs stammen aus dem beigefügten Stichprobenmanifest. Das Skript prüft das PDF-Dateiformat und vergleicht die Download-Prüfsummen mit den mitgelieferten Dateien. Es lädt nur diese Stichprobe. Die anderen Dateien und die Videos bleiben über die Katalogverweise erreichbar.

## Verarbeitungsschritte

1. Rohdatei und Quellschema prüfen.
2. Katalogeinträge identifizieren; Leerzeichen und Mediencodes vereinheitlichen.
3. Katalogstellen, Veröffentlichungsrunden und unterschiedliche Dateiverweise normalisieren.
4. Portalverweise anhand eindeutiger Bezeichner auflösen; belegte Schreibvarianten aus [reference_aliases.json](reference_aliases.json) verwenden.
5. Datumstexte konservativ auswerten und ihre Genauigkeit festhalten.
6. Relationale Tabellen, verschachtelte Dokumente, Graphdaten und Jahreszählungen erzeugen.
7. Referenzwerte und Qualitätsberichte schreiben.

Die Pipeline nutzt die Katalogmetadaten und die dortigen Beschreibungen. Die beigefügten PDFs sind Originalmaterial für die Inhaltsprüfung. OCR oder eine KI-Extraktion aus den PDFs ist für den hier erzeugten Eingabestand nicht erforderlich.

## Bewusst erhaltene Unklarheiten

- Der Quellschlüssel `FBI-UAP-D014` bezeichnet im Katalog zwei verschiedene Einträge. Ihre Veröffentlichungen und Dateien unterscheiden sich. Beide bleiben erhalten.
- Zwei Verweistoken auf diese Kennung bleiben mehrdeutig. Eine automatische Zuordnung wäre fachlich nicht gesichert.
- Elf weitere Token lassen sich nicht eindeutig auflösen. Dazu gehören sechs Verweise auf `DOW-UAP-PR-101` und fünf externe Aktenkennungen. Sie bleiben im Qualitätsbericht und erzeugen keine behaupteten Graphverbindungen.
- Drei fehlende Buchstaben in FBI-Verweisen sind durch ausdrücklich genannte Zielkennungen in den Beschreibungen belegt; ihre Zuordnungen sind separat dokumentiert.
- Mehrjährige Ereignisangaben werden für die Jahreszählung nicht auf mehrere Jahre verteilt. Der vollständige Eintrag bleibt im Katalog.

## Ergänzende Datenprüfung

```bash
python validation/validate_data.py
```

Diese Prüfung lädt Schlüssel und Verbindungen tatsächlich in SQLite, prüft referenzielle Integrität und vergleicht die Jahresaggregation mit einer SQL-Abfrage. Die Dokument- und Graphdateien werden auf gemeinsame Abdeckung und gültige Referenzen geprüft.

Optional lässt sich die Zeitreihe mit TinyFlux auf Datenträger schreiben und nach erneutem Öffnen abfragen:

```bash
python -m pip install tinyflux==1.2.0
python validation/validate_data.py --with-tinyflux
```

TinyFlux ist bereits in der gemeinsamen Workshop-Umgebung enthalten. Den Import in die vier Datenbanksysteme führst Du in den jeweiligen Demos und Aufgaben aus.
