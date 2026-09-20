[Workshop-Übersicht](../../README.md) · [Microblogging-Beispiele](../../demos/microblogging/README.md) · [Microblogging](../../demos/microblogging/04_tinyflux.ipynb) · [UAP-Aufgabe](../../tasks/04_tinyflux/README.md)

# TinyFlux: Punktmodell und Import

Das Paket verwendet die bereits festgelegte Version **TinyFlux 1.2.0** mit lokalem CSV-Backend. Die [Projektbeispiele](https://github.com/citrusvanilla/tinyflux) erläutern `Point`, `TinyFlux` und Abfragen.

## Zwei unterschiedliche Punktgranularitäten

| Eigenschaft | Microblogging | UAP |
| --- | --- | --- |
| Measurement | `microblogging_events` | `uap_annual_catalog` |
| Ein Punkt | Ein Post-, Like-, Kommentar- oder Follow-Ereignis | Zählung geeigneter Katalogeinträge je Jahr und Stelle |
| Zeit | Ereigniszeit in UTC; Follow-Tagesmarke | Beginn des Jahresintervalls in UTC |
| Tags | `type`, `user_id`, `event_id`; `post_id` oder `target_user_id` | `agency_id`, `date_basis`, `snapshot_sha256` |
| Numerisches Field | `value=1` | `catalog_entries` einschliesslich Null |
| Identität im Import | Ereignis-ID | Measurement + Zeit + Tags |
| Umfang | 5'690 Ereignisse | 820 Punkte mit Summe 292 |

Tags sind Strings; Fields sind numerische Werte. Zahlen werden beim Lesen des CSV-Backends als Floats geliefert. Die fachliche Prüfung verlangt nicht negative ganzzahlige Zählwerte. Zeitstempel müssen eine Zeitzone tragen; zeitzonenlose Plattform-Eingaben erhalten die dokumentierte UTC-Lehrkonvention.

Die UAP-Reihe enthält 82 Jahre × 10 Stellen, davon 72 positive und 748 Nullpunkte. 83 Einträge ohne eindeutiges Katalog-Ereignisjahr bleiben ausgeschlossen. Für die Tages- beziehungsweise Jahresmarke wird keine höhere Datumspräzision beansprucht, als die Quelle bietet.

## Was TinyFlux und was der Anwendungscode tun

`TimeQuery`, `TagQuery` und `FieldQuery` filtern Punkte in TinyFlux. Klammern und die Operatoren `&` beziehungsweise `|` verbinden Bedingungen. Die Notebooks verwenden halboffene Zeitfenster mit eingeschlossener Unter- und ausgeschlossener Obergrenze.

Gruppierung, Tabellenverknüpfung, Follow-Pfadsuche, Kalenderergänzung, gleitende Durchschnitte und Diagramme erfolgen in Python/pandas. Automatische Aggregation, eine Aufbewahrungsregel oder ein eindeutiger Zeitstempelschlüssel werden nicht vorausgesetzt. TinyFlux bietet selbst auch `update` und `remove`; die Kursnotebooks benötigen diese Operationen nicht.

## Wiederholbarer Import und Dateien

[`scripts/tinyflux_workshop.py`](../../scripts/tinyflux_workshop.py) verwendet für jeden Import diesen Ablauf:

1. Punkte, Zählfelder, Zeitangaben und doppelte Identitäten prüfen.
2. Eine temporäre Datei im selben Verzeichnis schreiben und schliessen.
3. Datei wieder öffnen, sämtliche Punkte mit dem vorbereiteten Bestand vergleichen und erneut schliessen.
4. Erst danach genau die gewählte Arbeitsdatei mit `os.replace` ersetzen.

Bei abgewiesenen Duplikaten oder einem Fehler vor dem Ersetzen bleibt die zuvor gespeicherte Arbeitsdatei erhalten. Eine erfolgreiche Wiederholung ersetzt eigene Änderungen innerhalb dieser Datei. Diese Importregel ist keine TinyFlux-Transaktion über mehrere Dateien und keine Garantie für konkurrierende Schreibprozesse. Pro Datei schreibt ein Notebook-Ablauf. Alle Dateihandles werden vor dem Ersetzen geschlossen.

Die Dateien liegen getrennt unter `data/work/`: `microblogging/04_events.tinyflux.csv`, `uap/04_annual_task.tinyflux.csv` und `uap/04_annual_solution.tinyflux.csv`. Ältere, generische Setup-Pfade werden von diesem Import nicht verwendet. Für Tests verlegt `STORAGE_TINYFLUX_TEST_DIR` diese drei Dateien in ein temporäres Verzeichnis. Im normalen Unterricht wird diese Variable nicht gesetzt.

Der vollständige Microblogging-Import liest die relationalen CSV-Eingaben ohne SQLite-Zugriff. Die ursprüngliche Tagesübersicht bleibt als Vergleich erhalten: Sie endet vor den letzten 19 Likes und 18 Kommentaren. Bei gleichen Fenstern stimmen ihre Werte mit den Detailereignissen überein.
