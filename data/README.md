[Haupt-README](../README.md) · [Technische Vorbereitung](../README_technical_preparation.md) · [Microblogging-Beispiele](../demos/microblogging/README.md) · [Ingestion-Code](../ingestion/README.md) · [Quellenprüfung](../docs/QUELLENPRUEFUNG.md)

# Datengrundlage und Datenwörterbuch

## Herkunft und Zähleinheiten

Ein Rohdatensatz entspricht einem **Katalogeintrag im PURSUE-Portal**. Ein Eintrag kann auf mehrere Dateien verweisen; umgekehrt kann dieselbe Datei bei mehreren Einträgen erscheinen. Ein Eintrag kann auch mehrere berichtete Ereignisse zusammenfassen. Daher werden `catalog_entries`, `assets` und tatsächliche Ereignisse fachlich getrennt betrachtet.

Der vollständige CSV-Snapshot liegt unter [raw/pursue_catalog.csv](raw/pursue_catalog.csv). Der Herkunftsnachweis steht in [raw/source_manifest.json](raw/source_manifest.json). Originalschreibweisen und leere Quellfelder bleiben dort erhalten.

## Dateien

| Pfad unter data/ | Inhalt |
| --- | --- |
| raw/pursue_catalog.csv | Unveränderte Bytes des heruntergeladenen Katalogs |
| raw/source_manifest.json | Quelle, Abruf, HTTP-Metadaten, Prüfsumme und Zeilenzahl |
| raw/originals/ | Sieben unveränderte Original-PDFs |
| raw/sample_assets.json | Links, Dateigrössen und Prüfsummen der PDF-Stichprobe |
| input/catalog_entries.jsonl | Gemeinsamer normalisierter Katalog, eine JSON-Zeile je Eintrag |
| input/relational/ | Tabellen für Katalog, Stellen, Veröffentlichungen, Dateien und Verknüpfungen |
| input/document/catalog_documents.jsonl | Verschachtelte Dokumente samt Dateiverweisen, Verknüpfungen und verfügbaren Quellmetadaten |
| input/graph/nodes.jsonl | Knoten mit node_id, label und properties |
| input/graph/edges.jsonl | Kanten mit edge_id, source, target, type und properties |
| input/timeseries/annual_catalog_counts.csv | Jahreszählungen nach Katalogstelle |
| input/quality/ | Ausgeschlossene Datumsangaben, unaufgelöste Verweistoken und mehrdeutige Quellschlüssel |
| input/reference_metrics.json | Automatisch berechnete Kennzahlen zur Prüfung |
| input/build_manifest.json | Prüfsummen der Aufbereitung und Ausgaben |

## Katalogeinträge

| Feld | Typ in JSON | Bedeutung |
| --- | --- | --- |
| entry_id | string | Deterministische ID aus Veröffentlichungsdatum und normalisiertem Quellschlüssel |
| source_key | string | Führender Bezeichner aus dem Titel; allein nicht notwendigerweise eindeutig |
| source_row | integer | Zeilennummer im Snapshot inklusive Kopfzeile; Beleg für die Ableitung |
| title | string | Titel mit vereinheitlichten Leerzeichen |
| agency_id | string | Verweis auf die im Katalog unter Agency angegebene Stelle |
| release_id | string | Verweis auf eine Veröffentlichungsrunde |
| release_date | string | Veröffentlichungsdatum im Format YYYY-MM-DD |
| media_type | string | Normalisierter Portaltyp: PDF, IMG, VID oder AUD |
| description | string | Beschreibung des Portals; kein vollständiger Akteninhalt |
| location_raw | string | Unveränderte Ortsangabe; kann breit, fehlerhaft oder leer sein |
| redaction_reported | boolean | TRUE wird gemeldet; false bedeutet lediglich, dass das Portalflag nicht gesetzt ist |
| description_category | string | artistic_interpretation bei entsprechendem Hinweis in Titel/Beschreibung, sonst not_classified |
| incident_date_raw | string | Originaltext aus Incident Date |
| incident_date_precision | string | Genauigkeit beziehungsweise Art der Datumsangabe |
| incident_year | integer/null | Genau ein zuordenbares Ereignisjahr, falls aus der Katalogangabe ableitbar |
| incident_month | integer/null | Monat nur bei expliziter Tages-/Monatsangabe |
| incident_day | string/null | Datum nur bei expliziter Tagesangabe |
| annual_eligible | boolean | Für die Jahreszählung geeignet |
| date_exclusion_reason | string | missing, multiple_years oder unparsed; leer bei Eignung |

In CSV werden fehlende Werte als leere Felder und boolesche Werte als `True`/`False` geschrieben. Beim späteren Datenbankimport sind diese Typen ausdrücklich umzusetzen. Die JSONL-Fassung enthält native JSON-Typen.

Die Kategorie `description_category` entsteht ausschliesslich aus Hinweisen im Katalogtitel und in der Portalbeschreibung. Sie erkennt keine im PDF eingebetteten Illustrationen: DOW-UAP-D080 enthält beispielsweise ausdrücklich KI-generierte Abbildungen, ohne dass dieses Feld sie identifiziert. `not_classified` bedeutet daher keine Bestätigung einer Originalaufnahme. Die manuelle Einordnung steht im [Aktenleseführer](../docs/AKTENLESEFUEHRER.md).

Die Katalogspalte Incident Date ist eine Quellenangabe. Sie kann bereits beim Herausgeber ein Dokumentdatum statt des historischen Ereignisdatums enthalten. Wir nennen die Zeitreihe deshalb ausdrücklich eine Auswertung der **im Katalog genannten Ereignisjahre**. Eine inhaltliche Neubestimmung aller Ereignisdaten ist nicht Teil dieser Datenvorbereitung.

## Relationales Modell

| Tabelle | Primärschlüssel | Verweise |
| --- | --- | --- |
| catalog_entries | entry_id | agency_id, release_id |
| agencies | agency_id | Keine |
| releases | release_id | Keine |
| assets | asset_id | Keine |
| entry_assets | entry_id und asset_id | Katalogeintrag und Dateiverweis |
| portal_pairings | pairing_id | Ausgangs- und Ziel-Katalogeintrag |

`asset_id` identifiziert eine eindeutige URL oder DVIDS-Medienkennung. Ein Asset ist damit ein **Locator**, kein Beweis, dass zwei unterschiedlich adressierte Dateien verschiedene Bytes enthalten. Nur die lokale Originalstichprobe wurde heruntergeladen und per Inhalt gehasht.

Die Relationen speichern zusätzlich `source_field`, damit etwa ein PDF-Link in einem Videoeintrag als Portalverweis nachvollziehbar bleibt. Die im Katalog angegebene Stelle ist nicht automatisch Urheber oder alleiniger Herausgeber des Originalmaterials.

## Dokumentenmodell

Ein Dokument enthält den Katalogeintrag, die Katalogstelle, ein Array der Asset-Locators, ein Array aufgelöster Verweise und `source_metadata` mit den tatsächlich gefüllten Originalfeldern. Diese verschachtelte Fassung zeigt einen möglichen Lesezugriff auf eine Akte. Die gemeinsame Speicherung kopierter Stellenangaben bringt später eine bewusste Aktualisierungsentscheidung mit sich.

## Graphmodell

| Knotentyp | Bedeutung |
| --- | --- |
| CatalogEntry | Eintrag des Portals |
| Agency | Wert der Quellspalte Agency |
| Release | Veröffentlichungsrunde |
| Asset | Dateilink oder DVIDS-Medienkennung |

| Kantentyp | Bedeutung |
| --- | --- |
| CATALOG_AGENCY | Eintrag ist dieser Katalogstelle zugeordnet |
| IN_RELEASE | Eintrag erscheint in dieser Veröffentlichungsrunde |
| LINKS_ASSET | Eintrag enthält den betreffenden Dateilink beziehungsweise Medienverweis |
| PORTAL_PAIRS_WITH | Die Pairing-Spalte des Ausgangseintrags nennt den Zieleintrag |

Gegenseitige Portalverweise werden als zwei gerichtete Kanten geführt. Ein Eintrag kann denselben anderen Eintrag in unterschiedlichen Feldern nennen; die Herkunft bleibt pro Kante erhalten. Für die Zahl verschiedener Nachbarn ist daher nach Ziel-ID zu deduplizieren.

Ein nachprüfbarer Pfad lautet: **FBI-UAP-D021 → DOW-UAP-D079 → Western US Event → DOW-UAP-D080**. Er verbindet eine Illustration mit einem zugeordneten Zeugenbericht, dem übergeordneten Katalogeintrag und einem weiteren Bericht. Die Verbindung belegt die Katalogzuordnung. Sie bewertet die Zeugenaussagen nicht.

## Zeitreihenmodell

292 Einträge lassen sich genau einem Jahr zuordnen. Daraus entstehen Zählpunkte je Jahr und Katalogstelle für 1945–2026. Die 820 Zeilen enthalten auch Nullwerte für Kombinationen ohne geeignete Katalogeinträge. Diese Nullen beziehen sich nur auf die definierte Sicht dieses Snapshots.

| Feld | Bedeutung |
| --- | --- |
| period_start | Technischer Beginn des Jahresintervalls in UTC; kein behaupteter Sichtungszeitpunkt |
| incident_year | Das Jahr, auf das sich die Zählung bezieht |
| agency_id | Gruppierung nach der Katalogstelle |
| catalog_entries | Anzahl geeigneter Katalogeinträge |
| date_basis | Fest catalog_incident_year |
| snapshot_sha256 | Identität des verwendeten Rohkatalogs |

Für TinyFlux ist `period_start` der Zeitstempel, `agency_id` und `date_basis` sind Tags, `catalog_entries` ist ein numerisches Feld. Bei mehreren Snapshots muss zusätzlich der Snapshot eindeutig getrennt werden. Der Import der Workshops verwendet jeweils genau einen festgelegten Snapshot.

`Late 2025` ist innerhalb des Jahres ungenau, aber für eine Jahreszählung geeignet. `1950, 1952`, `1970s` und fehlende Angaben sind dafür ungeeignet. Zweistellige Jahreszahlen werden in dem hundertjährigen Fenster interpretiert, das im jüngsten Veröffentlichungsjahr des Snapshots endet. Für diesen Stand ist das Fenster 1927–2026. Ein künftiger Abruf muss diese Quellenkonvention erneut prüfen.

## Referenzwerte

| Kennzahl | Wert |
| --- | ---: |
| Katalogeinträge | 375 |
| Katalogstellen | 10 |
| Veröffentlichungsrunden | 5 |
| Verschiedene Asset-Locators | 374 |
| Eintrag-Asset-Verknüpfungen | 397 |
| Aufgelöste gerichtete Pairing-Verweise | 336 |
| Nicht eindeutig aufgelöste Verweistoken | 13 |
| Für Jahreszählung geeignete Einträge | 292 |
| Für Jahreszählung ausgeschlossene Einträge | 83 |
| Graphknoten | 764 |
| Graphkanten insgesamt | 1’483 |

Die maschinenlesbaren Referenzwerte in `input/reference_metrics.json` werden direkt aus dem Rohkatalog neu berechnet.

## Weitere Eingaben und Arbeitsdaten

Die getrennten [Microblogging-Eingaben](microblogging/README.md) stammen aus dem bereitgestellten Vorjahresbeispiel. Eigene Dateien und Testproben entstehen unter [work/](work/README.md). Die Datenbankbereiche sind in der technischen Vorbereitung festgelegt.
