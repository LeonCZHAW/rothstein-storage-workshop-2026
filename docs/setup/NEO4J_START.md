[Workshop-Übersicht](../../README.md) · [Technische Vorbereitung](../../README_technical_preparation.md) · [Neo4j Desktop](NEO4J_DESKTOP.md) · [Microblogging](../../demos/microblogging/README.md) · [Neo4j-Aufgabe](../../tasks/03_neo4j/README.md)

# Neo4j starten und den Graphen anzeigen

**Entscheide Dich vor dem Start für einen Weg.** Notebook und Graphansicht verbinden sich anschliessend mit demselben Neo4j-Server. Die Graphansicht braucht keinen zusätzlichen Datenbankserver.

| Weg | Neo4j-Server | Vor dem Notebook | Oberfläche nach dem Import |
| --- | --- | --- | --- |
| **A: lokal mit Docker** | Lokaler Neo4j-Container | Konkurrierende Desktop-Instanz stoppen; Kurscontainer starten. | Browser auf dem lokalen Port `7474` |
| **B: lokal ohne Docker** | Lokale Instanz über Neo4j Desktop | Konkurrierenden Neo4j-Container stoppen; Desktop-Kursinstanz starten. | Query/Browser der gestarteten Desktop-Instanz |
| **C: Codespaces** | Neo4j-Begleitcontainer im Codespace | Automatischen Aufbau abwarten; keine lokale Datenbank starten. | Weitergeleitete Codespaces-Adresse |

## Warum die lokalen Wege nicht gleichzeitig gestartet werden

Weg A und B verwenden standardmässig dieselben lokalen TCP-Ports: **7474 für die Weboberfläche** und **7687 für Bolt**, die Verbindung aus Python. Der Docker-Container veröffentlicht diese Ports auf `127.0.0.1`. Eine zusätzliche Desktop-Instanz mit denselben Ports kann deshalb nicht gleichzeitig laufen. [Docker-Portzuordnung](https://docs.docker.com/engine/network/port-publishing/), [Neo4j-Ports](https://neo4j.com/docs/operations-manual/current/configuration/ports/)

Docker Desktop darf geöffnet bleiben und beispielsweise MongoDB betreiben. Entscheidend ist, welcher **Neo4j-Datenbankserver** läuft. Bei einer Portfehlermeldung beide Ports prüfen, den gewählten Weg beibehalten und den konkurrierenden Server stoppen. Die Ports werden im normalen Workshopablauf nicht umgestellt.

## Weg A: lokal mit Docker

1. Eine laufende Neo4j-Instanz in **Neo4j Desktop** mit dem Stop-Schalter stoppen. Falls ein nativer MongoDB-Server den Port `27017` belegt, auch diesen vor dem Start des vollständigen Docker-Stacks stoppen.
2. Docker Desktop/Engine starten und im Repo-Hauptordner gemäss [Weg A](../../README_technical_preparation.md#weg-a-lokal-mit-docker) ausführen:

```bash
docker compose up -d --wait
docker compose ps -a
```

3. Nach erfolgreichem Start das Notebook ausführen. Für die Microblogging-Demo die Ausgabe **IMPORT OK**, für die UAP-Aufgabe **GRUNDIMPORT OK** abwarten.
4. [Neo4j Browser](http://localhost:7474/browser/) im normalen Webbrowser öffnen. Dafür keine Desktop-Instanz erstellen oder starten.

| Einstellung | Standardwert |
| --- | --- |
| Connect URL | `bolt://127.0.0.1:7687` |
| Benutzer | `neo4j` |
| Passwort | `Storage-Neo4j-2026` oder das tatsächlich gesetzte Passwort |
| Datenbank | `neo4j` |

Bei bewusst angepassten Ports die Browseradresse und Connect URL entsprechend der aktiven Konfiguration ändern. Ein Passwort in `.env` ändert nicht das Passwort einer bereits gespeicherten Datenbank.

## Weg B: lokal ohne Docker

**Wenn bisher ein Neo4j-Kurscontainer verwendet wurde, diesen vor dem Desktop-Start stoppen.** Im bisherigen Repo-Ordner mit der bisherigen Compose-Konfiguration:

```bash
docker compose stop neo4j
```

Auf einem Rechner ohne Docker entfällt dieser Befehl. Container anderer Projekte gegebenenfalls in Docker Desktop stoppen. Der Befehl trifft nur das aktuelle Compose-Projekt; beim Wechsel zu einer neu benannten Projektversion zuerst die [Aktualisierungshinweise](AKTUALISIERUNG.md) lesen.

1. Die vorhandene Desktop-Kursinstanz weiterverwenden oder gemäss [Desktop-Anleitung](NEO4J_DESKTOP.md) einmalig einrichten. Standard-Anzeigename: **rothstein-storage-workshop-2026**; die Datenbank innerhalb der Instanz heisst **neo4j**.
2. Die Kursinstanz starten, dann die Notebook-Zellen ausführen.
3. Nach dem Import bei **derselben Instanz** in Desktop 1.x **Open → Neo4j Browser**, in Desktop 2.x **Connect → Query** öffnen.
4. Benutzer `neo4j`, tatsächliches Instanzpasswort und Datenbank `neo4j` verwenden. Der lokale Standardzugang ist ebenfalls `bolt://127.0.0.1:7687`.

Die Docker-Aktion zum Start beider Datenbanken während dieses Wegs nicht verwenden. Für den optionalen Mischbetrieb mit MongoDB in Docker gilt die [separate Anleitung](OHNE_DOCKER.md#optional-neo4j-desktop-mit-mongodb-in-docker-kombinieren): Neo4j-Container stoppen, ausschliesslich `docker compose up -d --wait mongodb` ausführen, danach Neo4j Desktop verwenden.

Beim Rückwechsel zu Weg A zuerst die Desktop-Kursinstanz stoppen und danach den Neo4j-Container starten. Desktop- und Docker-Datenbanken behalten jeweils ihre eigenen Daten; ein Wechsel der Verbindung überträgt den Graphen nicht.

## Weg C: Codespaces

**Auf Deinem Rechner brauchst Du dafür nur den Webbrowser und Dein GitHub-Konto.** Neo4j startet im Codespace automatisch. Du musst weder Anaconda Prompt noch Docker oder Neo4j Desktop öffnen.

### Einmalig: aktuellen Stand verwenden

Die aktualisierten Dateien müssen im GitHub-Repository auf dem Branch liegen, aus dem Du den Codespace startest. Eine lokal entpackte ZIP aktualisiert GitHub nicht automatisch.

- **Neuer Codespace:** Im aktuellen Repo **Code → Codespaces → Create codespace** wählen und den Aufbau abwarten.
- **Bereits vorhandener Codespace:** Zuerst die aktualisierten Repo-Dateien übernehmen. Eigene Änderungen vorher sichern. Dann mit `F1` die Befehlspalette öffnen und **Codespaces: Rebuild Container** ausführen. Ein blosses Neuladen des Browser-Tabs übernimmt die neue Konfiguration nicht.

### Bei der Arbeit: öffnen, anmelden, abfragen

1. Im Codespaces-Terminal im Repo-Hauptordner ausführen:

```bash
python scripts/verify_setup.py
```

Weitergehen, sobald **SETUP OK** erscheint. Der erste automatische Aufbau muss vorher abgeschlossen sein.

2. Unten neben **Terminal** das Register **Ports** öffnen. Falls es ausgeblendet ist: **View → Terminal** öffnen, dann **Ports** wählen.
3. Bei **8080 – Neo4j Browser** auf das Globus-Symbol **Open in Browser** klicken. Einen normalen neuen Browser-Tab verwenden. Falls GitHub nach einer Anmeldung fragt, mit demselben Konto wie beim Codespace anmelden.
4. Auf der Workshop-Startseite **Neo4j Browser öffnen** anklicken. Die Verbindungsadresse und der Benutzer sind bereits vorbereitet.
5. Im Neo4j-Anmeldedialog diese Angaben verwenden und **Connect** wählen:

| Feld | Eingabe |
| --- | --- |
| Connect URL | Die vorbereitete Adresse unverändert lassen. |
| Benutzer | `neo4j` |
| Passwort | `Storage-Neo4j-2026`, sofern Du kein anderes Datenbankpasswort gesetzt hast. |
| Datenbank, falls abgefragt | `neo4j` |

6. Im Cypher-Eingabefeld ausführen:

```cypher
RETURN 1 AS verbindung_ok;
```

Das Ergebnis muss **1** sein. Danach das Neo4j-Notebook ausführen und dessen Graphabfrage in den Neo4j Browser kopieren. In der Ergebnisansicht **Graph** wählen. Knoten lassen sich anklicken und verschieben.

**Einstellungen im Register Ports:** Port **8080**, Sichtbarkeit **Private**, Portprotokoll **HTTP**. GitHub stellt die externe Adresse trotzdem verschlüsselt über HTTPS bereit. Die Ports `7474` und `7687` müssen nicht zusätzlich weitergeleitet werden. Eine lokale Adresse wie `localhost:7474` gehört nicht zu diesem Codespaces-Weg.

### Falls etwas nicht klappt

| Beobachtung | Was Du tun sollst |
| --- | --- |
| Port 8080 fehlt | Unter **Ports → Add Port** die Zahl `8080` eintragen, dann **Open in Browser**. Den aktuellen Repo-Stand und den Container-Neuaufbau wie oben prüfen. |
| Startseite nicht erreichbar oder GitHub meldet einen gestoppten Codespace | Codespace wieder starten und den Aufbau abwarten. Bei einer älteren Umgebung die aktualisierten Dateien übernehmen und **Rebuild Container** ausführen. |
| Seite meldet „Neo4j ist noch nicht erreichbar“ oder Setup-Check meldet FAILED | Den Setup-Check erneut ausführen. Bleibt der Fehler bestehen, dessen konkrete Fehlermeldung prüfen; eine neue Conda-Installation hilft hier nicht. |
| Oberfläche erscheint, aber die Connect URL ist leer oder zeigt localhost | Zur Workshop-Startseite zurückgehen und erneut **Neo4j Browser öffnen** wählen. Falls nötig die dort angezeigte Verbindungsadresse kopieren. |
| Anmeldung abgelehnt | Benutzer `neo4j` und das tatsächlich gespeicherte Datenbankpasswort verwenden. Eine Änderung in `.env` ändert kein bestehendes Datenbankpasswort. |
| WebSocket-Verbindungsfehler | Codespace muss laufen. Port 8080 auf **Private / HTTP** prüfen; Workshop-Startseite und Neo4j Browser im selben normalen Webbrowser öffnen. Manche Schul-/Firmennetze blockieren WebSockets; gegebenenfalls ein anderes erlaubtes Netz verwenden. Port nicht öffentlich stellen. |
| Anmeldung funktioniert, Graph ist leer | Zuerst das Notebook vollständig ausführen und dessen Import-Erfolg abwarten. Datenbank `neo4j` und passende Graphabfrage verwenden. |

Die Notebooks sprechen intern weiterhin `neo4j:7687` an. Die externe Browseradresse wird nicht in `.env` oder in die Notebook-Verbindung kopiert. Nach dem Import genügt es, die Graphabfrage im Neo4j Browser erneut auszuführen.

Weboberfläche und Datenbankverbindung verwenden denselben privaten Zugang auf Port 8080. Eine zweite Portweiterleitung oder das manuelle Zusammenbauen einer Verbindungsadresse ist nicht erforderlich.

[GitHub: Portweiterleitung](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace) · [Neo4j: Verbindungsfelder per URL vorbelegen](https://neo4j.com/docs/browser/operations/browser-url-parameters/)

## Verbindung und Graphansicht prüfen

Im Cypher-Eingabefeld der geöffneten Neo4j-Oberfläche:

```cypher
RETURN 1 AS verbindung_ok;
```

Nach dem Notebook-Import die dort angegebene Graphabfrage ausführen und im Ergebnis **Graph** wählen. Die Beispiele stehen in der [Microblogging-Demo](../../demos/microblogging/03_neo4j.ipynb), der [UAP-Aufgabe](../../tasks/03_neo4j/task.ipynb) und ihrer [Musterlösung](../../tasks/03_neo4j/task_sample_solution.ipynb).

Eine erfolgreiche Anmeldung allein bestätigt noch nicht den fachlichen Import. Bei einem leeren Graphen zuerst Instanz, Datenbank und Importstatus prüfen. Die Bereiche heissen `microblogging_demo`, `uap_task` beziehungsweise `uap_solution`. Nach Änderungen im Notebook die Graphabfrage erneut ausführen.
