[Workshop-Übersicht](../../README.md) · [Microblogging](../../demos/microblogging/README.md) · [MongoDB-Aufgabe](../../tasks/02_mongodb/README.md)

# MongoDB-Dokumentmodell und Import

Der [Helfer](../../scripts/mongodb_workshop.py) verwendet ausschliesslich die vorhandene Kursumgebung und die gemeinsamen Verbindungseinstellungen. Die Datenbanknamen bleiben `storage_microblogging` und `storage_uap`. Aufgaben- und Lösungs-Collections sind getrennt; neue Datenbankberechtigungen sind nicht nötig.

## Microblogging

| Collection | Identität und Inhalt |
| --- | --- |
| users | `_id=user_id`, Nutzerprofil |
| posts | Originale Post-ID als `_id`, Referenz `author_id`, eingebettete Kommentare, vorberechneter `like_count` |
| follows | `_id="src:dst"`, gerichtete Beziehung und Beginn |
| likes | `_id=like_id`, Referenzen auf Post und Nutzer; vollständige Eingabe für gegebene Likes |

Die Vorbereitung prüft `like_count` gegen die Like-Eingaben. Jede Kommentar-ID bleibt erhalten. Zeitzonenlose synthetische Zeitangaben werden aufgrund einer ausdrücklichen Lehrkonvention als UTC gespeichert; BSON-Dates werden mit Zeitzoneninformation gelesen.

## UAP

`catalog` enthält den vorbereiteten JSONL-Bestand unverändert plus `_id=entry_id`. Kalendertage und ungenaue Datierungen werden nicht in erfundene Ereigniszeitpunkte umgerechnet. `source_metadata` enthält die tatsächlich vorhandenen, nicht leeren Quellfelder.

`reading_notes` enthält eigene Interpretationen mit Referenzen und verschachtelten Belegen. Die Musterlösung verwendet die Suffixe `_sample_solution` für beide Collections. Die mitgelieferte [Schemaregel](reading_note_validator.json) dient einer optionalen Probe-Collection; sie verändert keine bestehenden Benutzerregeln per `collMod`.

## Wiederholung und Grenzen

Der Import validiert eindeutige IDs und BSON-Serialisierbarkeit vor dem Schreiben. Dann ersetzt er Dokumente unter stabilen IDs und entfernt überholte IDs ausschliesslich aus der ausdrücklich gewählten Workshop-Collection. Der Notizbestand bleibt beim Katalogimport erhalten.

Es gibt keinen atomaren Austausch aller Collections. Nach einem Abbruch kann ein teilweise erneuerter Stand vorliegen; erst ein vollständig erfolgreicher Wiederholungslauf stellt den Snapshot wieder her. Das kleine Lehrmodell benötigt weder einen Cluster noch eine Konfigurationsänderung für Mehrdokument-Transaktionen.

MongoDB begrenzt ein BSON-Dokument auf 16 MiB. Eingebettete Arrays müssen deshalb auch hinsichtlich Wachstum und Änderungen beurteilt werden. Die Dokumentgrössen dieses festen Bestands werden in der Vorbereitung geprüft. [MongoDB: Grössenlimits](https://www.mongodb.com/docs/manual/reference/limits/), [Bulk-Schreibzugriffe](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/bulk-write/).

Der automatische Servertest nutzt einen zufälligen `STORAGE_MONGO_TEST_TOKEN`. Nur während dieses Tests werden eigene Collection-Namen in `storage_setup` verwendet und danach entfernt. Für die normale Notebook-Nutzung ist diese Variable nicht zu setzen.
