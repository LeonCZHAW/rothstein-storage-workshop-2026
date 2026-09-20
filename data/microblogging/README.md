[Workshop-Übersicht](../../README.md) · [Technische Vorbereitung](../../README_technical_preparation.md) · [Microblogging-Beispiele](../../demos/microblogging/README.md)

# Microblogging-Eingaben

Diese synthetischen Daten stammen unverändert aus dem bereitgestellten Microblogging-Beispiel. [manifest.json](manifest.json) enthält den Ursprungspfad im Upload, Dateigrösse und SHA-256. Bereits erzeugte SQLite-/TinyFlux-Datenbanken wurden nicht als Eingaben übernommen.

| Sicht | Bestand |
| --- | --- |
| Relational | 200 Nutzer, 865 Beiträge, 1’266 Likes, 512 Kommentare, 3’047 Follow-Beziehungen |
| Dokumente | Nutzer-, Beitrags- und Follow-Dokumente als JSONL |
| Graph | 1’065 Knoten und 5’690 Kanten als CSV |
| Zeitreihe | 6’000 Nutzer-/Tageszeilen mit Posts, Likes und Kommentaren |

Die Dateien bleiben Eingaben; erzeugte Datenbanken und eigene Resultate gehören nach `data/work/` beziehungsweise in die dafür vorgesehenen Datenbankbereiche. Die fachliche Abstimmung der Sichten erfolgt in den jeweiligen Demo-Paketen.
