[Workshop-Übersicht](../../README.md) · [Microblogging](../../demos/microblogging/README.md) · [SQLite-Aufgabe](../../tasks/01_sqlite/README.md)

# SQLite-Schemata

- [microblogging.sql](microblogging.sql): vollständiges Schema der Demonstration.
- [uap_base.sql](uap_base.sql): vorbereitete UAP-Tabellen; die Zwischentabelle `entry_assets` ergänzt die Gruppe im Aufgaben-Notebook.

Der [SQLite-Helfer](../../scripts/sqlite_workshop.py) liest CSV-Daten, konvertiert leere Werte zu `None`/SQL-NULL, Ganzzahlen zu `int` und die booleschen Felder zu 0/1. Er prüft die redundanten Veröffentlichungsdaten und speichert sie normalisiert in `releases`. Datumspräzision und Originalangaben bleiben erhalten.

Schemaanlage und Datenimport sind getrennt. `STRICT`-Tabellen benötigen SQLite ab 3.37; die Kursumgebung erfüllt dies. Der Helfer aktiviert Fremdschlüssel vor jeder Transaktion und verwendet explizite `BEGIN`-/`COMMIT`-/`ROLLBACK`-Statements. Verbindungen werden auch im Fehlerfall geschlossen. [SQLite: STRICT](https://www.sqlite.org/stricttables.html), [Python 3.12: sqlite3](https://docs.python.org/3.12/library/sqlite3.html).

Der Snapshot-Import ersetzt Tabelleninhalte, nicht die Tabellenstruktur. Ein fehlgeschlagener Datenimport erhält den zuletzt bestätigten Inhalt; eine falsche Tabellendefinition korrigiert er nicht. Die Anleitungen beschreiben den Neustart mit einer umbenannten Arbeitsdatei.
