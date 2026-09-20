[Workshop-Übersicht](../../README.md) · [Technische Vorbereitung](../../README_technical_preparation.md) · [Microblogging-Beispiele](../../demos/microblogging/README.md)

# Eigene Arbeitsdaten

Erzeugte Dateien liegen getrennt unter `uap/`, `microblogging/` und für technische Proben unter `_setup/`. Sie werden nicht mit Git versioniert. Benötigte Ergebnisse daher zusätzlich exportieren und sichern; ein Git-Push allein sichert diese Dateien nicht.


Für SQLite sind `microblogging/storage.sqlite`, `uap/storage.sqlite` und `uap/storage_sample_solution.sqlite` getrennt vorgesehen. Der Import stellt die jeweiligen Tabellen aus dem Eingabestand wieder her. Der Materialtest verwendet temporäre Kopien; mit `--kernel` speichert er ausgeführte Notebook-Kopien unter `sqlite_execution/`.
