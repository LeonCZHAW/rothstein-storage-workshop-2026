[Haupt-README](../README.md) · [Microblogging-Beispiele](../demos/microblogging/README.md) · [Datengrundlage](../data/README.md) · [Ingestion-Code](../ingestion/README.md)

# Quellenprüfung und Entscheidung zum Workshop-Case

## Ergebnis

**Der PURSUE-Katalog eignet sich als gemeinsamer Fall für den Vergleich der vier Speicherperspektiven.** Seine Metadaten sind ausreichend reichhaltig für relationale Beziehungen, verschachtelte Dokumente, explizite Verknüpfungen und Jahreszählungen. Die Daten sind überschaubar und enthalten tatsächliche Modellierungsprobleme.

Für Zeitreihen verwenden wir eine ausdrücklich definierte Archivkennzahl: die Anzahl der Katalogeinträge je genanntem Ereignisjahr und Katalogstelle. Der Bestand beschreibt weder eine vollständige Erfassung von Sichtungen noch einen laufenden Sensorstrom. Ein produktives Zeitreihensystem ist für diese geringe Datenmenge technisch nicht erforderlich; TinyFlux eignet sich hier zum Erproben des Speicher- und Abfragemodells.

Der vollständige Katalog enthält 375 Einträge und umfasst als Roh-CSV weniger als ein Megabyte. Dadurch bleiben alle vorhandenen Pairing-Verweise für die Prüfung zugänglich. Die Originaldateien werden als kleine, gezielt ausgewählte PDF-Stichprobe mitgeliefert.

## Geprüfte Quellen

| Quelle | Befund | Entscheidung |
| --- | --- | --- |
| [PURSUE-Portal](https://www.war.gov/ufo/) und sein verlinkter [CSV-Katalog](https://www.war.gov/Portals/1/Interactive/2026/UFO/uap-data.csv?release=5) | Einzeleinträge mit Titel, Beschreibung, Typ, Stelle, Veröffentlichung, Incident Date, Ort, Dateilinks und Pairing-Feldern | Gemeinsamer Workshop-Datenbestand |
| [NARA: UAP-Bulk-Downloads](https://www.archives.gov/research/catalog/catalog-bulk-downloads/uap-bulk-download) | Originalmaterial und Katalogmetadaten, teilweise auf Ebene ganzer Serien | Mögliche spätere Erweiterung |
| NARA-Exporte 493468575, 542184, 595175 und 595466 | Die vier JSON-Dateien enthalten jeweils einen Serien-Datensatz, obwohl die Serie viele Unterlagen umfasst | Für diese Aufgabe allein keine ausreichende Einzeldokumenttabelle |

Die vollständigen Bytes des PURSUE-Katalogs sind im Paket enthalten. Der Abruf erfolgt direkt vom offiziellen Server. Ein Suchergebnis oder eine nachträglich zusammengestellte Beispieltabelle bildet keine Datenquelle dieser Pipeline.

## Umfang des ausgewählten Bestands

| Kennzahl | Ergebnis |
| --- | ---: |
| Katalogeinträge | 375 |
| Katalogstellen | 10 |
| Veröffentlichungsrunden | 5 |
| Eindeutige Asset-Locators | 374 |
| Eintrag-Asset-Verknüpfungen | 397 |
| Aufgelöste gerichtete Pairing-Verweise | 336 |
| Nicht eindeutig aufgelöste Pairing-Token | 13 |
| Knoten in der vorbereiteten Graphsicht | 764 |
| Kanten in der vorbereiteten Graphsicht | 1’483 |
| Einer Jahreszählung zuordenbare Einträge | 292 |
| Von dieser Zählung ausgeschlossene Einträge | 83 |
| Verschiedene Jahre mit geeigneten Einträgen | 47 |
| Zeitspanne der genannten Ereignisjahre | 1945–2026 |
| Original-PDFs im Paket | 7 |

Die Werte beziehen sich auf den im Herkunftsmanifest festgehaltenen Snapshot. Die fünf Katalogveröffentlichungen sind vom 8. Mai, 22. Mai, 12. Juni, 10. Juli und 7. August 2026. Veröffentlichung und berichteter Ereigniszeitpunkt sind unterschiedliche Datumsarten.

## Eignung für die vier Workshops

| Modell | Konkreter Datenbeleg | Daraus abgeleitete Aufgabe |
| --- | --- | --- |
| SQLite | 375 Einträge und 397 Verknüpfungen auf 374 Asset-Locators | Schlüssel und Zwischentabellen verwenden; verschiedene Einträge und referenzierte Dateien korrekt zählen |
| MongoDB | Unterschiedliche gefüllte Quellfelder, lange Beschreibungen, Medienkennungen und Arrays von Verweisen | Vollständige Katalogansicht als verschachteltes Dokument abrufen; Einbettung und Referenzen vergleichen |
| Neo4j | 336 aufgelöste Verweise, auch zwischen Einträgen unterschiedlicher Katalogstellen | Portalzuordnungen über mehrere Beziehungsschritte verfolgen und die Bedeutung der Pfade erklären |
| TinyFlux | 292 eindeutig einem Jahr zugeordnete Einträge; 820 Jahres-/Stellenkombinationen einschliesslich Nullwerten | Jahreszählungen mit Tags speichern, ein Zeitfenster auswählen und mit SQL-Referenzwerten vergleichen |

Die Ersatzidee, Import-Betriebskennzahlen für den Zeitreihenworkshop zu messen, wird für diesen Stand nicht benötigt.

## Graphbeispiel mit tatsächlich vorhandenen Verweisen

Der vorbereitete Pfad verbindet:

1. **FBI-UAP-D021**: eine im Portal als künstlerische Interpretation bezeichnete Darstellung.
2. **DOW-UAP-D079**: zugeordneter Bericht eines Zeugen.
3. **Western US Event**: ein übergeordneter Katalogeintrag.
4. **DOW-UAP-D080**: ein weiterer zugeordneter Zeugenbericht.

Jede dieser Verbindungen ist in einer Pairing-Spalte ausdrücklich angegeben. Die Original-PDFs D079 und D080 nennen auf ihrer ersten Seite selbst den übergeordneten Portalverweis. Der Pfad erschliesst die Dokumentation. Er beweist keine Ursache des berichteten Phänomens.

## Inhaltliche Originalstichprobe

Die Auswahl wurde nach der ersten Quellenprüfung gezielt auf anschauliche Inhalte und nachvollziehbare Gegenprüfung ausgerichtet. Der [Aktenleseführer](AKTENLESEFUEHRER.md) enthält Seitenangaben, Quellenarten und Recherchefragen.

| Datei im Paket | Prüfung und Relevanz |
| --- | --- |
| [DOW-UAP-D079.pdf](../data/raw/originals/DOW-UAP-D079.pdf) | Zeugenschilderung mit ungewöhnlichen Lichtern und scheinbar schwebenden Objekten; expliziter Verweis auf Western US Event |
| [DOW-UAP-D080.pdf](../data/raw/originals/DOW-UAP-D080.pdf) | Weiterer Bericht zum selben Dokumentationskomplex; Seite 5 kennzeichnet die nachfolgenden Abbildungen ausdrücklich als nachträglich KI-generiert |
| [DOW-UAP-D077.pdf](../data/raw/originals/DOW-UAP-D077.pdf) | Datierte AARO-Analyse zum Teilkomplex der Lichtkugeln; nennt Hypothesen und Aussagegrenzen |
| [FBI-UAP-D024.pdf](../data/raw/originals/FBI-UAP-D024.pdf) | Piloteninterview mit Schilderungen aus mehreren Jahren; eine Datei ist keine einzelne datierte Beobachtung |
| [FBI-UAP-D026.pdf](../data/raw/originals/FBI-UAP-D026.pdf) | Bericht über ein dreieckig wirkendes Objekt; Interview- und Beobachtungsdatum unterscheiden sich |
| [DOS-UAP-D001.pdf](../data/raw/originals/DOS-UAP-D001.pdf) | Diplomatische Rückfrage zu einer spektakulären Pressemeldung; enthält bereits eine negative Auskunft |
| [DOS-UAP-D002.pdf](../data/raw/originals/DOS-UAP-D002.pdf) | Verknüpfter Folgebericht mit negativer Überprüfung; zusätzlicher Datumswiderspruch im Scan |

Die schwer lesbaren Scans CIA-UAP-D020 und CIA-UAP-D021 sind über ihre Einträge und Dateilinks im Katalog erreichbar. Alle 375 Katalogeinträge und ihre technischen Kennungen bleiben erhalten; die gezielte PDF-Auswahl verändert weder die Modellansichten noch die Referenzwerte.

Prüfe Angaben aus den PDF-Textebenen immer auch direkt auf der abgebildeten Originalseite. Die Texterkennung der historischen Scans ist teilweise fehlerhaft oder unvollständig. Die Aufbereitung nutzt deshalb weiterhin die offiziellen Katalogbeschreibungen. Sie enthält keine automatisch extrahierten Aktenvolltexte. Die Original-PDFs bleiben unverändert.

## Tatsächliche Qualitätsprobleme und ihre Behandlung

### Eine Kennung bezeichnet zwei Einträge

`FBI-UAP-D014` steht einmal für eine Illustration zum Western-US-Komplex und einmal für historische Korrespondenz. Veröffentlichungsdatum, Titel und Dateilink unterscheiden sich. Ein UNIQUE-Constraint allein auf `source_key` würde entweder einen gültigen Eintrag verhindern oder bei einem Upsert Informationen überschreiben.

Die Aufbereitung bildet deshalb eine technische Eintrags-ID aus Veröffentlichungsdatum und Quellschlüssel. Beide Einträge bleiben erhalten. Zwei nicht ausreichend eindeutige Pairing-Verweise auf diese Kennung erzeugen keine automatisch gewählte Kante.

### Nicht jeder Verweistoken ist auflösbar

Von 349 ausgewerteten Pairing-Token lassen sich 336 eindeutig zuordnen. Zwei sind mehrdeutig, elf bleiben unaufgelöst. Die elf umfassen sechs Angaben `DOW-UAP-PR-101` und fünf Aktenkennungen aus State-Department-Einträgen. Eine ähnlich aussehende Kennung wird nicht allein aufgrund ihrer Schreibweise als Ziel angenommen.

Drei klar belegte Varianten mit fehlendem `D` sind in `ingestion/reference_aliases.json` dokumentiert. Die Zielkennungen stehen ausdrücklich in den jeweiligen Beschreibungen. Originaltoken und angewendete Auflösungsregel bleiben in der Ausgabetabelle erhalten.

### Jahreszählung mit klarer Abdeckung

Die 83 ausgeschlossenen Einträge bestehen aus 73 fehlenden Datumsangaben, neun mehrjährigen Angaben und einer Jahrzehntangabe. Ein Eintrag mit `Late 2025` bleibt innerhalb des Jahres ungenau, ist aber dem Jahr 2025 zuordenbar. Für eine tagesgenaue Analyse wäre er ungeeignet.

Der jährliche Zeitstempel der aggregierten Sicht ist der Beginn des Zählintervalls. Er stellt keine Ergänzung eines unbekannten Sichtungsdatums dar. Nullwerte bedeuten, dass im ausgewählten Snapshot für diese Stelle und dieses Jahr keine geeigneten Einträge vorliegen.

### Aussagegrenzen der Quelle

Die Spaltenbezeichnung Incident Date garantiert noch keine inhaltlich validierte Ereignisdatierung. Die historische Korrespondenz mit der Kennung FBI-UAP-D014 zeigt beispielsweise, dass eine Datumsangabe mit der Dokumentation statt mit dem beschriebenen historischen Vorfall zusammenhängen kann. Der Workshop verwendet die explizite Semantik «im Katalog genanntes Ereignisjahr».

29 Einträge enthalten im Titel oder in der Beschreibung einen Hinweis auf künstlerische Interpretation, digitale Darstellung oder zusammengesetzte Skizze. Die Aufbereitung markiert diese Hinweise regelbasiert. Daraus entsteht kein Modell zur Bewertung der Glaubwürdigkeit von Meldungen.

## Daten selbst prüfen

Im Repo-Hauptordner mit aktivierter Workshop-Umgebung ausführen:

```bash
python ingestion/ingest.py verify
python validation/validate_data.py --with-tinyflux
```

Die erste Prüfung vergleicht die Originaldateien, die Pipeline und die generierten Eingaben mit ihren Prüfsummen. Die zweite prüft unter anderem Fremdschlüssel, die Abdeckung der vier Datenmodelle und die Jahreszählungen. Für die Katalogjahre 2020–2023 beträgt der Referenzwert 116 Einträge. Hinweise zur Aufbereitung findest Du im [Ingestion-Bereich](../ingestion/README.md).

## Verwendung im Workshop

Alle vier Aufgaben nutzen denselben Snapshot und besitzen einen unabhängigen Einstieg mit bereits aufbereiteten Daten. Die vollständige Quellenbeschaffung und Aufbereitung kannst Du zusätzlich im Ingestion-Bereich nachvollziehen.
