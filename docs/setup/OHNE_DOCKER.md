[Workshop-Übersicht](../../README.md) · [Technische Vorbereitung](../../README_technical_preparation.md) · [Microblogging-Beispiele](../../demos/microblogging/README.md) · [MongoDB lokal](MONGODB_LOKAL.md) · [Neo4j Desktop](NEO4J_DESKTOP.md)

# Weg B: lokal ohne Docker

Du verwendest dieselbe Conda-Umgebung, dieselben Daten und dieselben Notebooks wie beim Docker-Weg. Die beiden Datenbankserver laufen direkt auf Deinem Rechner: **MongoDB Community Server** als Dienst und **Neo4j über Neo4j Desktop**. SQLite und TinyFlux speichern weiterhin Dateien.

**Du möchtest zunächst nur ein Beispiel ausführen?** Der [Microblogging-Schnellstart](../../demos/microblogging/README.md#ohne-docker-einsteigen) zeigt die Voraussetzungen je Datenbank. SQLite und TinyFlux benötigen keinen Server; für die Neo4j-Demo genügt zunächst die gestartete Desktop-Instanz. Der gemeinsame Setup-Check in Abschnitt 5 setzt anschliessend beide Datenbankdienste voraus.

## 1. Voraussetzungen und Versionen

| Baustein | Vorbereitung |
| --- | --- |
| Conda | Vorhandenes Anaconda/Miniconda verwenden oder nach [Installation, Abschnitt 1](INSTALLATION.md#1-conda-bereitstellen) einrichten. |
| MongoDB | Community Server **8.0.x** und Shell **mongosh** gemäss [MongoDB lokal](MONGODB_LOKAL.md). Docker-Referenzversion: 8.0.30. |
| Neo4j | Desktop **2.x** mit einer lokalen Datenbankinstanz **5.26.x**, vorzugsweise 5.26.30, gemäss [Neo4j Desktop](NEO4J_DESKTOP.md). Die Desktop-App und die Datenbank haben unterschiedliche Versionsnummern. |
| Oberfläche | JupyterLab aus der Kursumgebung oder optional VS Code mit Python-/Jupyter-Erweiterungen. |
| Git | Optional; die vollständig entpackte Repo-ZIP genügt. |

Die native Variante sieht dieselben Datenbank-Versionsreihen vor wie Docker. Abweichende Patchversionen sind möglich; der gemeinsame Setup-Check zeigt die tatsächlich laufenden Serverversionen. Das ist keine Zusage für beliebige neuere Hauptversionen.

Für diesen Weg brauchst Du weder Docker Desktop noch WSL. Neo4j Desktop stellt die benötigte Java-Laufzeit bereit beziehungsweise lädt sie nach. MongoDB Compass ist optional und ersetzt keinen MongoDB-Server. [Neo4j: Installation](https://neo4j.com/docs/desktop/current/installation/), [MongoDB: Compass](https://www.mongodb.com/docs/compass/)

## 2. Repo und Python-Umgebung vorbereiten

Die Repo über [Git oder ZIP](../../README_technical_preparation.md#a1-mit-git) beziehen und im Terminal in den enthaltenen Ordner mit `environment.yml` wechseln. Pfade mit Leerzeichen in Anführungszeichen setzen. Windows: **Anaconda Prompt** oder eingerichtetes **Git Bash**; macOS/Linux: Terminal. [Conda in Bash einrichten](BASH.md).

Bei der ersten Einrichtung:

```bash
conda env create -f environment.yml
conda activate rothstein-storage-workshop-2026
python -m ipykernel install --user --name rothstein-storage-workshop-2026 --display-name "Python (rothstein-storage-workshop-2026)"
```

Wenn die Kursumgebung bereits erfolgreich eingerichtet wurde, genügt `conda activate rothstein-storage-workshop-2026`. Die Docker-Prüfungen und Docker-Startbefehle aus Weg A werden bei Weg B ausgelassen.

## 3. Beide Datenbankserver einrichten und starten

**Zuerst konkurrierende Container stoppen.** Wenn Du vorher mit Docker gearbeitet hast, im bisherigen Repo-Ordner mit der bisherigen Compose-Konfiguration ausführen:

```bash
docker compose stop mongodb neo4j
```

Bei einem Rechner ohne Docker entfällt dieser Schritt. Prüfe in Docker Desktop auch andere noch laufende Neo4j-/MongoDB-Container. Native Dienste und Container dürfen lokal nicht gleichzeitig dieselben Ports belegen: Neo4j `7474` und `7687`, MongoDB `27017`. Danach die nativen Server einrichten:

1. [MongoDB Community Server installieren, Zugriffsschutz und Kursbenutzer einrichten](MONGODB_LOKAL.md).
2. [Neo4j Desktop installieren, eine Kursinstanz erstellen und starten](NEO4J_DESKTOP.md).

Ein laufendes Desktop-Fenster allein bestätigt noch keine gestartete Neo4j-Instanz. Bei MongoDB muss der Datenbankdienst laufen. Die beiden Detailanleitungen enthalten jeweils eine eigene Verbindungsprüfung.

## 4. Zugangsdaten für die Notebooks hinterlegen

Bei den Kursstandards funktioniert die Verbindung ohne zusätzliche Datei. Wenn Du eigene Passwörter oder Ports gewählt hast, `.env.example` einmalig als `.env` kopieren. Eine bereits vorhandene `.env` bearbeiten, statt sie zu überschreiben.

Windows – Anaconda Prompt:

```bat
copy .env.example .env
```

Bash (Windows/Git Bash, macOS oder Linux):

```bash
cp .env.example .env
```

Die Werte müssen den **tatsächlich eingerichteten** Diensten entsprechen:

| Einstellung | Kursstandard |
| --- | --- |
| `MONGO_HOST` / `MONGO_PORT` | `127.0.0.1` / `27017` |
| `MONGO_USERNAME` / `MONGO_PASSWORD` | `workshop` / `Storage-Mongo-2026` |
| MongoDB-Anmeldedatenbank | `admin`; im Verbindungscode festgelegt. Der Kursbenutzer wird dort angelegt. |
| `NEO4J_HOST` / `NEO4J_PORT` | `127.0.0.1` / `7687` |
| Neo4j-Benutzer | `neo4j`; bei der Erstellung der Desktop-Instanz verwenden. |
| `NEO4J_PASSWORD` | `Storage-Neo4j-2026` oder Dein tatsächlich gesetztes Passwort |
| `NEO4J_DATABASE` | `neo4j`, die Datenbank innerhalb der Instanz; nicht deren frei gewählter Anzeigename |

Die Passwortwerte in `.env` ändern keine Passwörter im Datenbankserver. Bei Sonderzeichen oder Leerzeichen den Wert mit einfachen Anführungszeichen umschliessen, beispielsweise `NEO4J_PASSWORD='Mein#Passwort'`. Die Datei nicht veröffentlichen.

Prozess-Umgebungsvariablen haben Vorrang vor `.env`. Nach einer Änderung die Notebook-Kernel neu starten, damit keine bereits geladenen Einstellungen weiterverwendet werden. Die verwendeten Ziele ohne Passwörter anzeigen:

```bash
python -c "from scripts.storage_runtime import connection_summary; print(connection_summary())"
```

## 5. Gemeinsamen Setup-Check ausführen

Während beide Datenbankserver laufen:

```bash
python scripts/verify_setup.py
```

Erwartet wird **SETUP OK**. Die Prüfung verwendet keinen Docker-Befehl: Sie prüft die Python-Umgebung, Daten und tatsächliche Schreib-/Leseoperationen in allen vier Speichern. Bei einem Fehler die jeweilige Detailanleitung verwenden.

Danach `jupyter lab` starten oder das Repo in VS Code öffnen. In `notebooks/00_setup_check.ipynb` den Kernel **Python (rothstein-storage-workshop-2026)** wählen und **Run All** ausführen. Die Einstellung `OFFLINE_ONLY` bleibt `False`, auch bei einem Betrieb ohne Docker: Beide nativen Dienste sollen vollständig geprüft werden.

## 6. Stoppen, Fortsetzen und Persistenz

Die Start-/Stoppbefehle für MongoDB stehen in der [Diensttabelle](MONGODB_LOKAL.md#dienst-starten-und-stoppen). Neo4j in Desktop mit dem Play-/Stop-Schalter der **gleichen** Kursinstanz steuern.

Eine Persistenzprüfung vollständig auf demselben Betriebsweg durchführen:

```bash
python scripts/persistence_check.py write
```

MongoDB stoppen und wieder starten. Die Neo4j-Kursinstanz stoppen und dieselbe Instanz wieder starten. Erst wenn beide bereit sind:

```bash
python scripts/persistence_check.py read
python scripts/persistence_check.py cleanup
```

`read` muss für alle vier Speicher erfolgreich sein; `cleanup` entfernt ausschliesslich die markierten Probeobjekte. Zwischen `write`, `read` und `cleanup` keine Verbindungsziele ändern.

| Speicher | Wo die nativen Arbeitsdaten liegen |
| --- | --- |
| SQLite / TinyFlux | Unter `data/work/` im Repo. |
| MongoDB | Im `storage.dbPath` der tatsächlich verwendeten MongoDB-Konfiguration. |
| Neo4j Desktop | Im Datenverzeichnis der Kursinstanz; über die Instanzkarte beziehungsweise **Open → Instance folder** erreichbar. |

Stoppen erhält diese Daten. Das Löschen der Desktop-Instanz oder der Datenverzeichnisse entfernt sie. Ein Git-Push sichert die Datenbankbestände nicht. Der Docker-Weg hat eigene Volumes: Ein Wechsel des Betriebswegs überträgt keine vorhandenen MongoDB-/Neo4j-Daten. Die späteren Imports verwenden auf jedem Weg dieselben vorbereiteten Eingaben.

Beim nächsten Arbeiten die beiden Dienste starten, `conda activate rothstein-storage-workshop-2026` und `python scripts/verify_setup.py` ausführen. Die Installationen und Benutzeranlage werden nicht wiederholt.

## Optional: Neo4j Desktop mit MongoDB in Docker kombinieren

Wenn Du Neo4j über Desktop betreiben möchtest und Docker für MongoDB weiter nutzt, im bisherigen Repo zuerst den Neo4j-Container stoppen:

```bash
docker compose stop neo4j
```

Danach ausschliesslich MongoDB starten:

```bash
docker compose up -d --wait mongodb
```

Nun die Desktop-Kursinstanz starten und deren tatsächliche Zugangsdaten in `.env` verwenden, falls sie vom Standard abweichen. Die separate VS-Code-Aktion **Mischbetrieb: nur MongoDB in Docker starten (Neo4j über Desktop)** führt genau diesen MongoDB-Start aus. Andere Neo4j-Container aus früheren Projekten bei Bedarf über Docker Desktop stoppen.

Auch hierbei gelten derselbe Setup-Check und getrennte Datenbestände. `docker compose up` ohne Servicenamen würde beide Container starten und kann dadurch einen Portkonflikt mit Neo4j Desktop verursachen.
