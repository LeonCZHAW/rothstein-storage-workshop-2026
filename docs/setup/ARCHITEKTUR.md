[Workshop-Übersicht](../../README.md) · [Technische Vorbereitung](../../README_technical_preparation.md) · [Microblogging-Beispiele](../../demos/microblogging/README.md)

# Technischer Rahmen und Modellgrenzen

## Ein Python-Stack, drei Betriebswege

Lokal erzeugt Conda eine Umgebung mit Python 3.12 und installiert die Pakete aus `requirements.txt`. Codespaces verwendet eine Python-3.12-Umgebung im Arbeitscontainer und dieselbe Datei. Die direkt verwendeten Bibliotheken sind auf konkrete Versionen festgelegt; indirekte Abhängigkeiten werden vom Paketmanager aufgelöst. Die Paketliste legt daher nicht sämtliche indirekten Abhängigkeiten plattformübergreifend fest.

Die beiden Referenz-Repos liefern die Navigationsstruktur, die Kernelbenennung und die Aufgabenorganisation. Storage ergänzt eigene Datenbankdienste und bietet lokal zwei Varianten: Docker-Container oder MongoDB Community Server mit Neo4j Desktop. Codespaces bildet den dritten Weg. Die Inhalte beider Fälle bleiben in getrennten Eingabe- und Arbeitsbereichen.

## Dienste und Adressen

Die Wege heissen **A: lokal mit Docker**, **B: lokal ohne Docker** und **C: Codespaces**. Weg A und B sind lokale Alternativen: Ein Neo4j-Container und eine Desktop-Instanz dürfen dort nicht gleichzeitig `7474`/`7687` belegen. Für die Graphansicht wird derselbe Server wie im Notebook verwendet. Codespaces läuft auf einem separaten GitHub-Rechner.

| Baustein | Lokal mit Docker | Lokal ohne Docker | Im Codespaces-Arbeitscontainer |
| --- | --- | --- | --- |
| Python | Conda-Environment `rothstein-storage-workshop-2026` | Gleiches Conda-Environment | `/opt/storage-venv` |
| MongoDB | 8.0.30, `127.0.0.1:27017` | Community 8.0.x, `127.0.0.1:27017` | 8.0.30, `mongodb:27017` |
| Neo4j | Community 5.26.30, `127.0.0.1:7687` | Desktop 2.x mit DBMS 5.26.x, `127.0.0.1:7687` | Community 5.26.30, `neo4j:7687` |
| SQLite | Datei unter `data/work/` | Datei unter `data/work/` | Datei unter `data/work/` |
| TinyFlux 1.2.0 | CSV-basierte Datenbankdatei unter `data/work/` | Gleiche Ablage | Gleiche Ablage |

`compose.yaml` definiert die beiden Dienste und die benannten Volumes. Die ergänzende Codespaces-Datei fügt den Arbeitscontainer hinzu. Die Compose-Pfade beziehen sich auf die erste Compose-Datei im Repo-Hauptordner. `depends_on` mit `service_healthy` lässt den Arbeitscontainer auf die Datenbanken warten. Der Setup-Check prüft zusätzlich die Anmeldung und tatsächliche Schreib-/Leseoperationen.

Die Verbindungshilfen in `scripts/storage_runtime.py` nutzen zuerst die Prozessumgebung, danach eine optionale `.env`, zuletzt die Kursstandards. Dadurch überschreibt eine lokale `.env` nicht die internen Codespaces-Adressen. Passwörter werden von den Setup-Prüfungen nicht ausgegeben.

Der native Weg verwendet diese gleichen Verbindungshilfen. MongoDB authentifiziert `workshop` in `admin`; Neo4j verwendet den Benutzer `neo4j` und die konfigurierbare Datenbank, standardmässig `neo4j`. Der native MongoDB-Kursbenutzer erhält `readWrite` auf `storage_uap`, `storage_microblogging` und `storage_setup`. Die Docker-Referenz verwendet ihren initialen Root-Benutzer; spätere Aufgaben müssen mit dem eingeschränkten nativen Rollenprofil auskommen.

Der Setup-Check und die Persistenzprüfung rufen keine Docker-Kommandos auf. Der Dienstneustart zwischen Schreiben und Lesen wird passend zum Betriebsweg ausgelöst. Docker-Volumes, native MongoDB-Datenverzeichnisse und Desktop-Instanzen sind verschiedene Bestände; ein Wechsel der Verbindung migriert keine Daten.

## Trennung der Fälle

Für dateibasierte Speicher entstehen getrennte Ordner. MongoDB verwendet zwei Datenbanken. Neo4j Community verwendet eine gemeinsame fachliche Datenbank; die Neo4j-Demo, Aufgabe und Musterlösung kennzeichnen ihre Knoten, Beziehungen und Abfragen mit `scope`. Die Bereiche heissen `microblogging_demo`, `uap_task` und `uap_solution`.

Für die Neo4j-Umsetzung gelten deshalb folgende Vorgaben:

- Knoten und Beziehungen nur im jeweiligen Datensatzbereich importieren und abfragen.
- Eine technische ID zusammen mit dem Kursbereich identifizieren, beispielsweise `(scope, node_id)`.
- Keine globale Löschung aller Knoten zum Zurücksetzen einer Aufgabe.
- Wiederholte Interaktionen nicht versehentlich durch zu grobe `MERGE`-Muster zusammenfassen.

Die technischen Probeobjekte nutzen eine eigene Kennzeichnung und zufällige Token. Ein Setup-Durchlauf löscht ausschliesslich seine eigenen Token. Die Persistenzprüfung legt ihre Token vor dem Schreiben ab, sodass sich auch teilweise ausgeführte Tests gezielt bereinigen lassen.

## Was der Stack demonstriert

SQLite und TinyFlux zeigen dateibasierte Speicher mit unterschiedlichen Modellen. MongoDB läuft als authentifizierter einzelner Server, Neo4j als einzelne Instanz. Bei Docker verwenden wir Community, bei Desktop dessen Developer-Edition mit Enterprise-Funktionen. Die Aufgaben bleiben beim gemeinsamen Funktionsumfang und bei einer fachlichen Datenbank. Diese Konfiguration demonstriert keine Replikation, keinen Cluster-Failover und keine Netzwerkpartition.

MongoDB-Transaktionen über mehrere Dokumente setzen eine geeignete Replica-Set- oder Sharding-Konfiguration voraus; sie gehören nicht zum hier konfigurierten Standalone-Server. Die CAP-Diskussion im Unterricht benötigt daher einen eigenen fachlichen Fall und lässt sich nicht aus dem Verhalten dieses Einzelserver-Setups ableiten.

TinyFlux ist eine kleine Python-Bibliothek für Zeitreihendaten. Der Workshop verwendet sie zum Speichern und Abfragen der Jahreszählungen. Ein Vergleich produktiver Durchsatz- oder Clusterleistungen ist damit nicht beabsichtigt.

## Eingaben und Prüfungen

Der UAP-Snapshot, die sieben Original-PDFs und die Microblogging-Eingaben haben Herkunftsnachweise und Prüfsummen. `.gitattributes` schützt die Rohbytes vor einer automatischen Umwandlung der Zeilenenden, insbesondere beim Checkout unter Windows.

Die repräsentativen Speichertests prüfen Schreiben, erneutes Öffnen, Lesen und gezielte Bereinigung. Die separate Persistenzprüfung prüft markierte Daten nach einem selbst ausgelösten Dienst- beziehungsweise Codespace-Neustart. Ein erfolgreicher Verbindungscheck allein würde diese Aussage nicht erlauben.

## Weiterführende Originaldokumentation

- [Dev-Container-Konfiguration mit Docker Compose](https://code.visualstudio.com/docs/devcontainers/create-dev-container)
- [Dev-Container-Metadatenreferenz](https://containers.dev/implementors/json_reference/)
- [Docker-Volumes](https://docs.docker.com/engine/storage/volumes/)
- [MongoDB-Transaktionen: Voraussetzungen](https://www.mongodb.com/docs/manual/core/transactions-production-consideration/)
- [MongoDB-Image](https://hub.docker.com/_/mongo)
- [Neo4j-Image](https://hub.docker.com/_/neo4j)
- [TinyFlux](https://github.com/citrusvanilla/tinyflux)

## Neo4j Browser in Codespaces

Der Arbeitscontainer startet `scripts/neo4j_browser.py` mit der Python-Standardbibliothek als Hauptprozess. Dafür ist keine zusätzliche Bibliothek und keine Änderung der gemeinsamen Environmentdateien nötig. Die Dev-Container-Konfiguration leitet nur Port `8080` weiter. Der Dienst bindet an `127.0.0.1` im Arbeitscontainer; GitHub übernimmt die private Weiterleitung und die externe TLS-Verbindung.

Normale HTTP-Anfragen werden an `neo4j:7474` weitergegeben, WebSocket-Upgrades an `neo4j:7687`. Die Workshop-Startseite berechnet die passende `bolt+s`-Adresse aus ihrer eigenen HTTPS-Adresse und übergibt sie dem Browser über `connectURL`. UI und WebSocket verwenden dadurch denselben Ursprung und dieselbe GitHub-Portanmeldung. GitHub-Cookies und `X-GitHub-Token` werden nicht an Neo4j weitergereicht; das Neo4j-Passwort wird ausschliesslich im Neo4j-Anmeldedialog eingegeben. Notebook-Verbindungen bleiben bei `bolt://neo4j:7687`.

Der Dienst ist für den privaten Workshop-Codespace vorgesehen. Er besitzt keine eigene TLS-Terminierung oder Zugriffskontrolle und wird nicht als öffentlicher Server betrieben. Start-, Anmelde- und Fehlerhinweise stehen in [Neo4j starten](NEO4J_START.md#weg-c-codespaces).
