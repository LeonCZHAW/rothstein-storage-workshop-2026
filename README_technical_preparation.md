[Workshop-Übersicht](README.md) · [Technische Vorbereitung](README_technical_preparation.md) · [Microblogging-Beispiele](demos/microblogging/README.md) · [SQLite](tasks/01_sqlite/README.md) · [MongoDB](tasks/02_mongodb/README.md) · [Neo4j](tasks/03_neo4j/README.md) · [TinyFlux](tasks/04_tinyflux/README.md)

---

# rothstein-storage-workshop-2026

Du kannst lokal mit Conda oder im Browser mit GitHub Codespaces arbeiten. Lokal hast Du die Wahl zwischen Datenbankcontainern in Docker und direkt installierten Datenbankdiensten. Alle drei Wege verwenden Python 3.12 und dieselbe Paketliste. SQLite und TinyFlux schreiben Dateien; MongoDB und Neo4j laufen als eigene Dienste.

**Direkte Einstiege:** [Befehle in Bash](docs/setup/BASH.md) · [Lokal ohne Docker](docs/setup/OHNE_DOCKER.md) · [Neo4j Desktop](docs/setup/NEO4J_DESKTOP.md) · [MongoDB lokal](docs/setup/MONGODB_LOKAL.md) · [Microblogging-Schnellstart](demos/microblogging/README.md#ohne-docker-einsteigen)

## Welcher Weg passt zu Dir?

| Kriterium | [Weg A: lokal mit Docker](#weg-a-lokal-mit-docker) | [Weg B: lokal ohne Docker](#weg-b-lokal-ohne-docker) | [Weg C: Codespaces](#weg-c-codespaces) |
| --- | --- | --- | --- |
| Einrichtung | Conda und Docker mit Compose | Conda, MongoDB Community Server/mongosh und Neo4j Desktop | GitHub-Konto; Einrichtung aus der Repo-Konfiguration |
| Oberfläche | JupyterLab oder VS Code | JupyterLab oder VS Code; zusätzlich Neo4j Desktop | VS Code im Browser |
| Datenbankdienste | Docker-Container auf Deinem Rechner | MongoDB als lokaler Dienst; Neo4j als lokale Desktop-Instanz | Automatisch gestartete Begleitcontainer |
| Internet | Für Installation, Updates und neue Quellenabrufe | Für Installation, Updates und neue Quellenabrufe | Für die Arbeit im Codespace |
| Ressourcen | Eigener Rechner; für den gesamten Stack sind 8 GB verfügbarer Arbeitsspeicher sinnvoll | Eigener Rechner; dieselbe Orientierung, zusätzlich Desktop-Oberfläche | Konfiguration fordert mindestens 2 CPUs, 8 GB RAM und 32 GB Speicher |
| Ablage | Repo-Arbeitsordner und Docker-Volumes | Repo-Arbeitsordner und Datenverzeichnisse der lokalen Dienste | Arbeitsordner und Volumes innerhalb des Codespaces |
| Nutzung | Lokale Installation | Lokale Installation mit eigener Dienstverwaltung | Persönliches [Codespaces-Kontingent](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces) |

Die lokale Anleitung richtet sich an Windows/Linux auf x86-64 und macOS auf Intel oder Apple Silicon, jeweils mit einem vom Hersteller unterstützten Betriebssystem. Die ausgewählten Datenbank-Images bieten amd64- und arm64-Varianten. Die native Linux-Anleitung enthält konkrete Schritte für Ubuntu 24.04 sowie Verweise auf die anderen unterstützten Distributionen.

**Wähle einen Betriebsweg.** Neo4j im lokalen Docker-Container und eine lokale Neo4j-Desktop-Instanz verwenden standardmässig dieselben Ports `7474` und `7687`. Starte nur den Server Deines gewählten Wegs; die Graphansicht verbindet sich mit diesem Server. [Neo4j starten und anzeigen](docs/setup/NEO4J_START.md). Für bestehende Installationen zuerst die [Aktualisierungshinweise](docs/setup/AKTUALISIERUNG.md) lesen.

Die folgende Anleitung für Weg A verwendet Docker. Wenn Du ohne Docker arbeiten möchtest, beginne direkt mit [Weg B](docs/setup/OHNE_DOCKER.md). Beide lokalen Wege nutzen dieselben Python-Verbindungshilfen und denselben Setup-Check.

## Weg A: lokal mit Docker

Dieser Abschnitt beschreibt **lokal mit Docker**. Docker-Container und native Dienste dürfen nicht gleichzeitig dieselben Ports belegen.

### Voraussetzungen

| Komponente | Was Du vorher einrichten musst | Was das Repo bereitstellt |
| --- | --- | --- |
| Python-Umgebung | Miniconda oder vorhandenes Anaconda | Python 3.12, JupyterLab und alle Python-Pakete über `environment.yml` |
| Docker unter Windows | Docker Desktop mit Linux-Containern; für den hier beschriebenen Weg WSL 2 und Hardwarevirtualisierung | MongoDB- und Neo4j-Container aus `compose.yaml` |
| Docker unter macOS | Docker Desktop passend zu Apple Silicon oder Intel | Dieselben Datenbankdienste |
| Docker unter Linux | Docker Engine mit CLI und Compose-Plugin sowie Zugriff auf den laufenden Dienst | Dieselben Datenbankdienste |
| VS Code, falls verwendet | VS Code und die Microsoft-Erweiterungen **Python** und **Jupyter** | Notebook-Dateien und Auswahl des Kurs-Kernels |
| Git, falls verwendet | Git für Fork/Clone und spätere Aktualisierungen | Die ZIP-Variante funktioniert auch ohne Git |

**Beginne mit [Installation für Windows, macOS und Linux](docs/setup/INSTALLATION.md), wenn eine dieser Voraussetzungen fehlt.** Dort stehen die Installationsschritte und die Prüfung der Docker-Engine. Wenn alle Prüfungen bereits erfolgreich sind, kannst Du direkt mit A1 oder A2 fortfahren.

**MongoDB, Neo4j und Java werden für diesen Weg nicht separat auf Deinem Rechner installiert.** Die Images enthalten die Datenbankserver und ihre benötigten Laufzeiten. `pymongo` und das Python-Paket `neo4j` sind hingegen nur Treiber: Eine erfolgreiche Python-Installation startet noch keinen Datenbankserver. SQLite ist in Python enthalten; TinyFlux wird als Python-Paket installiert.

**Terminalwahl:** Anaconda Prompt ist unter Windows eine Möglichkeit. Auch **Git Bash** sowie Bash unter macOS/Linux funktionieren; Conda muss für die Shell eingerichtet sein. [Bash einmalig einrichten und Befehle vergleichen](docs/setup/BASH.md). In Codespaces ist das Terminal bereits vorbereitet.

### A1: mit Git

Einen eigenen Fork des Workshop-Repositories erstellen und dessen HTTPS-Adresse über **Code → HTTPS** kopieren. Im folgenden Befehl `DEINE-REPO-URL` durch diese Adresse ersetzen. Der lokale Ordnername ist unabhängig vom Namen des GitHub-Repositories:

```bash
git clone DEINE-REPO-URL rothstein-storage-workshop-2026
cd rothstein-storage-workshop-2026
```

### A2: als ZIP

Die bereitgestellte ZIP oder später **Code → Download ZIP** auf GitHub herunterladen und vollständig entpacken. Den enthaltenen Repo-Ordner öffnen; die Datei `environment.yml` muss direkt darin liegen.

**Windows – Anaconda Prompt:**

```bat
cd /d "C:\Users\DEIN-NAME\Documents\rothstein-storage-workshop-2026"
dir environment.yml
```

**Windows – Git Bash (nach der [Bash-Einrichtung](docs/setup/BASH.md)):**

```bash
cd "/c/Users/DEIN-NAME/Documents/rothstein-storage-workshop-2026"
ls environment.yml
```

**macOS – Terminal:**

```bash
cd "/Users/DEIN-NAME/Documents/rothstein-storage-workshop-2026"
ls environment.yml
```

**Linux – Terminal:**

```bash
cd "/home/DEIN-NAME/Documents/rothstein-storage-workshop-2026"
ls environment.yml
```

Die Beispielpfade an Deinen Speicherort anpassen. Alle folgenden Befehle werden im Repo-Hauptordner ausgeführt.

### Gemeinsame Einrichtung für A1 und A2

**1. Docker Desktop beziehungsweise Docker Engine starten.** Das Öffnen der Anwendung stellt die Container-Laufzeit bereit. Die beiden Kursdatenbanken werden erst in Schritt 4 gestartet.

Docker und Compose prüfen:

```bash
docker version
docker compose version
```

`docker version` muss unter **Client und Server** Versionsinformationen anzeigen. Eine Client-Ausgabe mit anschliessendem Serverfehler reicht nicht. `docker compose version` muss ebenfalls erfolgreich sein. Bei einem Fehler zuerst die [Installationsanleitung](docs/setup/INSTALLATION.md) verwenden.

**2. Die Python-Umgebung einmalig erstellen:**

```bash
conda env create -f environment.yml
conda activate rothstein-storage-workshop-2026
python -m ipykernel install --user --name rothstein-storage-workshop-2026 --display-name "Python (rothstein-storage-workshop-2026)"
```

Conda stellt Python bereit; die eingebundene `requirements.txt` installiert die gemeinsamen Kursbibliotheken. Bestehende Transformation-/Serving-Environments bleiben eigenständig.

Falls `rothstein-storage-workshop-2026` bereits erfolgreich eingerichtet wurde, genügt `conda activate rothstein-storage-workshop-2026`. Ein Verbindungsfehler zu MongoDB oder Neo4j erfordert keine erneute Conda-Installation.

**3. Datenbank-Images beim ersten Einrichten herunterladen:**

```bash
docker compose pull mongodb neo4j
```

Dieser Schritt benötigt Internetzugriff auf die Container-Registry. Bei einem Downloadfehler dessen Meldung prüfen; die Dienste können ohne ihre Images noch nicht starten. Bei späteren Starts ist kein erneutes `pull` nötig. `up` lädt fehlende Images auch selbst; der getrennte Download macht einen Fehler beim ersten Einrichten besser erkennbar.

**4. Vor dem Start lokale native Dienste prüfen:** Stoppe eine laufende Neo4j-Instanz über den Stop-Schalter in Neo4j Desktop und einen gegebenenfalls laufenden nativen MongoDB-Server, sofern sie die Workshopports belegen. Das Öffnen der Weboberfläche später benötigt keine zusätzliche Desktop-Instanz.

**Danach beide Docker-Datenbankdienste starten (nur Weg A):**

```bash
docker compose up -d --wait
```

Den erfolgreichen Abschluss abwarten und danach den Zustand prüfen:

```bash
docker compose ps -a
```

Für die Services **mongodb** und **neo4j** muss jeweils **healthy** erscheinen. `--wait` wartet auf die in der Repo-Konfiguration definierten Bereitschaftsprüfungen. Schlägt der Start fehl oder fehlt einer der Dienste, mit der [Fehlerdiagnose](#mongodb-oder-neo4j-meldet-failed) fortfahren. [Docker: compose up](https://docs.docker.com/reference/cli/docker/compose/up/)

**5. Erst nach erfolgreichem Dienststart die Verbindung aus Python prüfen:**

```bash
python scripts/verify_setup.py
```

Am Ende muss **SETUP OK** erscheinen. Der Check schreibt markierte Testdaten, öffnet Verbindungen beziehungsweise Dateien erneut, liest die Testdaten und entfernt anschliessend ausschliesslich seine eigenen Probeobjekte. Er importiert noch keine Workshopdaten.

### JupyterLab

```bash
conda activate rothstein-storage-workshop-2026
jupyter lab
```

`notebooks/00_setup_check.ipynb` öffnen, **Python (rothstein-storage-workshop-2026)** als Kernel wählen und **Run All** ausführen. Das Terminal mit JupyterLab bleibt für den Server belegt. Für weitere Befehle ein zweites Terminal öffnen und dort ebenfalls das Environment aktivieren. Beenden mit `Ctrl+C` im Serverterminal.

### VS Code

```bash
conda activate rothstein-storage-workshop-2026
code .
```

Alternativ VS Code starten und den Repo-Ordner über **File → Open Folder** öffnen. Über **Python: Select Interpreter** das Storage-Environment wählen. Im Setup-Notebook oben rechts zusätzlich den Kernel **Python (rothstein-storage-workshop-2026)** auswählen. Interpreter und Notebook-Kernel müssen zum selben Environment gehören.

Unter **Terminal → Run Task** stehen die gemeinsame Setup-Prüfung und das Nachladen neuer Materialien bereit. Die mit **Weg A** beschrifteten Docker-Aktionen gelten nur für Weg A. Bei Weg B verwendest Du die MongoDB-Dienststeuerung und die Start-/Stop-Schalter in Neo4j Desktop. Für den optionalen Mischbetrieb gibt es **Wechsel zu Weg B: Neo4j-Container stoppen** und **Mischbetrieb: nur MongoDB in Docker starten (Neo4j über Desktop)**. Die Aktion zum Start beider Container dort nicht verwenden. In Codespaces werden die Datenbanken automatisch gestartet.

### Optional: Neo4j Browser bei Weg A

**Keine zusätzliche Desktop-Instanz erstellen oder starten.** Nach erfolgreichem Containerstart [Neo4j Browser](http://localhost:7474/browser/) öffnen:

| Einstellung | Kursstandard |
| --- | --- |
| Connect URL | `bolt://localhost:7687` |
| Benutzer | `neo4j` |
| Passwort | `Storage-Neo4j-2026` |
| Datenbank | `neo4j` |

Die Anmeldung lässt sich mit `RETURN 1 AS verbindung_ok;` prüfen. Alle erforderlichen Cypher-Abfragen können auch direkt aus den Notebooks ausgeführt werden.

## Weg B: lokal ohne Docker

**Vor dem Start nativer Dienste:** Falls Du von Weg A wechselst, im bisherigen Repo-Ordner `docker compose stop mongodb neo4j` ausführen. Bereits laufende Container aus anderen Projekten in Docker Desktop prüfen und die konkurrierenden Datenbankcontainer stoppen. Die Docker-Startbefehle aus Weg A werden in Weg B ausgelassen.

Die vollständige [Anleitung ohne Docker](docs/setup/OHNE_DOCKER.md) führt Dich durch dieselbe Python-Einrichtung mit direkt installierten Datenbanken:

1. Conda bereitstellen und das Kurs-Environment erstellen oder aktivieren.
2. [MongoDB Community Server 8.0.x samt mongosh](docs/setup/MONGODB_LOKAL.md) installieren, Zugriffsschutz und Kursbenutzer einrichten und den Dienst starten.
3. [Neo4j Desktop 2.x](docs/setup/NEO4J_DESKTOP.md) installieren, eine Kursinstanz mit Neo4j 5.26.x erstellen und starten.
4. Tatsächliche Passwörter und gegebenenfalls Ports in der Repo-Konfiguration hinterlegen.
5. `python scripts/verify_setup.py` ausführen und auf **SETUP OK** achten; danach dasselbe Setup-Notebook verwenden.

Docker, WSL und eine separate Java-Installation sind für diesen Weg nicht erforderlich. Bei MongoDB ersetzt Compass den Server nicht. Für die Erstinstallation sind unter Windows die mongosh-Installation und unter macOS die Homebrew-Voraussetzungen ausdrücklich in den Detailanleitungen aufgeführt.

Auch eine [Kombination aus Neo4j Desktop und MongoDB in Docker](docs/setup/OHNE_DOCKER.md#optional-neo4j-desktop-mit-mongodb-in-docker-kombinieren) ist beschrieben. Ein Wechsel des Betriebswegs überträgt keine bereits gespeicherten Datenbankinhalte.

## Weg C: Codespaces

Sobald das Repo auf GitHub bereitsteht:

1. Einen eigenen Fork erstellen und öffnen.
2. **Code → Codespaces → Create codespace** auf dem tatsächlich verwendeten Branch wählen (zum Beispiel `main` oder `master`).
3. Den Aufbau der Umgebung vollständig abwarten. Die Konfiguration startet Python, MongoDB und Neo4j und installiert die Kursbibliotheken automatisch.
4. Im Terminal auf **SETUP OK** achten. Bei Bedarf `python scripts/verify_setup.py` ausführen.
5. `notebooks/00_setup_check.ipynb` öffnen, **Python (rothstein-storage-workshop-2026)** auswählen und **Run All** ausführen.

Für diesen Browser-Weg benötigst Du auf Deinem Rechner weder Docker noch Conda oder eine lokale Datenbankinstallation. Codespaces verwendet eine Python-Umgebung unter `/opt/storage-venv`; ein zusätzliches `conda activate` ist dort nicht erforderlich. Die festgelegten Python-Paketversionen stammen wie lokal aus derselben `requirements.txt`. Lokal bindet `environment.yml` diese Datei ein; Codespaces installiert sie in die vorbereitete Python-3.12-Umgebung. GitHub betreibt die Docker-Container auf seinen Servern; auf Deinem Rechner ist Docker dafür nicht erforderlich.

### Falls im Notebook ein Python-Paket fehlt

Erscheint nach Abschluss der Einrichtung beispielsweise `ModuleNotFoundError: No module named 'pandas'`, gehe so vor:

1. **Kernel prüfen:** Wähle im Notebook oben rechts **Python (rothstein-storage-workshop-2026)** oder die Python-Umgebung **storage-venv**. Mit dieser Notebook-Zelle kannst Du die Auswahl prüfen:

   ```python
   import sys
   print(sys.executable)
   ```

   Die Ausgabe muss `/opt/storage-venv/bin/python` sein.

2. **Fehlende Pakete installieren:** Wenn trotz richtigem Kernel ein Paket fehlt, öffne **Terminal → Neues Terminal** und führe dort diesen Befehl aus:

   ```bash
   /opt/storage-venv/bin/python -m pip install -r /workspaces/rothstein-storage-workshop-2026/requirements.txt
   ```

   Damit werden alle Pakete aus der gemeinsamen `requirements.txt` in die vorgesehene Codespaces-Umgebung installiert. Warte den erfolgreichen Abschluss ab. Bei einer Fehlermeldung zuerst die letzten Zeilen der Installationsausgabe prüfen.

3. **Kernel neu starten:** Klicke oben im Notebook auf **Restart** und führe die Zellen erneut von oben aus.

### Neo4j Browser öffnen und Codespace beenden

Innerhalb von Codespaces lauten die Datenbank-Hosts `mongodb` und `neo4j`. Die Hilfsfunktionen lesen sie automatisch aus der Containerkonfiguration. Es ist keine manuelle Portweiterleitung für die Notebook-Abfragen nötig. Für die Graphansicht unten **Ports → 8080 (Neo4j Browser) → Open in Browser** wählen. Auf der Startseite **Neo4j Browser öffnen** anklicken und mit Benutzer `neo4j` sowie Deinem Datenbankpasswort anmelden (Standard: `Storage-Neo4j-2026`). Die Verbindungsadresse ist vorbereitet. Port 8080 bleibt **Private / HTTP**. Die [Schritt-für-Schritt-Anleitung](docs/setup/NEO4J_START.md#weg-c-codespaces) erklärt auch den einmaligen Neuaufbau bestehender Codespaces. Eine lokale Desktop-Instanz wird dafür nicht gestartet. Der oben genannte `localhost`-Link gehört nur zu Weg A.

Beim erneuten Öffnen eines gestoppten Codespaces wird der Setup-Check wieder ausgeführt. Zum Beenden **Codespaces: Stop Current Codespace** wählen oder den Codespace auf GitHub stoppen. Die lokalen `docker compose`-Befehle gehören zu Weg A; im Arbeitscontainer ist kein Docker-Client vorgesehen.

## Wo bleiben meine Daten?

| System | Microblogging-Demo | UAP-Workshop |
| --- | --- | --- |
| SQLite | `data/work/microblogging/storage.sqlite` | `data/work/uap/storage.sqlite` |
| TinyFlux | `data/work/microblogging/04_events.tinyflux.csv` | `data/work/uap/04_annual_task.tinyflux.csv` |
| MongoDB | Datenbank `storage_microblogging` | Datenbank `storage_uap` |
| Neo4j, alle Kurswege | Datenbank `neo4j`, Bereich `scope='microblogging_demo'` | Datenbank `neo4j`, Bereich `scope='uap_task'` |

Diese Ablagen gelten für Demo und Aufgabe. Die SQLite-Musterlösung verwendet zusätzlich `data/work/uap/storage_sample_solution.sqlite`, damit sie Deinen Aufgabenstand nicht überschreibt. TinyFlux verwendet für die Musterlösung `data/work/uap/04_annual_solution.tinyflux.csv`, Neo4j den Bereich `uap_solution`. Der Setup-Test nutzt separat `data/work/_setup`, die MongoDB-Datenbank `storage_setup` und das Neo4j-Label `_StorageSetupProbe`.

**Mit Docker** liegen MongoDB- und Neo4j-Daten in benannten Volumes. Lokal behalten `docker compose stop`, ein erneutes `up` und auch `docker compose down` ohne Volume-Löschung diese Volumes. Der Befehl `docker compose down --volumes` würde sie löschen und ist kein normaler Beendigungsschritt.

**Ohne Docker** liegen MongoDB-Daten im konfigurierten `storage.dbPath` und Neo4j-Daten im Datenverzeichnis der Desktop-Instanz. Die Speicherorte und das Stoppen/Fortsetzen erklärt [Weg B](docs/setup/OHNE_DOCKER.md#6-stoppen-fortsetzen-und-persistenz). Diese Bestände sind von den Docker-Volumes getrennt.

In Codespaces bleiben Arbeitsordner und Daten bei normalem Stoppen/Fortsetzen erhalten. Ein Löschen des Codespaces entfernt auch dessen lokale Daten. Ein vollständiger Neuaufbau kann die Umgebung ersetzen; Docker-Volumes sind kein externes Backup. Eigene Notebooks committen und pushen; zusätzlich benötigte Datenexporte lokal herunterladen. `data/work/` wird bewusst nicht mit Git versioniert.

### Persistenz selbst überprüfen

Zuerst in der laufenden Umgebung:

```bash
python scripts/persistence_check.py write
```

**Lokal mit Docker (Weg A):** Beide Dienste stoppen und wieder starten:

```bash
docker compose stop
docker compose up -d --wait
```

**Lokal ohne Docker (Weg B):** Den [MongoDB-Dienst](docs/setup/MONGODB_LOKAL.md#dienst-starten-und-stoppen) und die gleiche Neo4j-Kursinstanz in Desktop stoppen und wieder starten. Keine neue Instanz anlegen und während der Prüfung keine Verbindungsziele ändern.

**Codespaces (Weg C):** Den Codespace stoppen und denselben Codespace wieder öffnen. Danach in allen Wegen:

```bash
python scripts/persistence_check.py read
python scripts/persistence_check.py cleanup
```

Die Leseprüfung muss für alle vier Systeme erfolgreich sein. Sie verwendet dieselbe gespeicherte Markierung und erzeugt beim Lesen keine Ersatzwerte. `cleanup` entfernt nur die markierten Testobjekte.

### Lokal beenden und fortsetzen

**Mit Docker (Weg A):**

```bash
docker compose stop
conda deactivate
```

Beim nächsten Mal:

Zuerst Docker Desktop beziehungsweise Docker Engine starten. Danach im Repo-Hauptordner:

```bash
conda activate rothstein-storage-workshop-2026
docker compose up -d --wait
```

Nach erfolgreichem Start:

```bash
python scripts/verify_setup.py
```

**Ohne Docker (Weg B):** Die [nativen Dienste stoppen beziehungsweise starten](docs/setup/OHNE_DOCKER.md#6-stoppen-fortsetzen-und-persistenz). Zum Fortsetzen danach das Kurs-Environment aktivieren und denselben Python-Check ausführen. Docker-Befehle sind dabei nicht erforderlich.

## Einstellungen und Fehlerbehebung

Die Kursstandards funktionieren ohne `.env`. Bei Bedarf `.env.example` als `.env` kopieren und nur die erforderlichen Werte ändern. Anaconda Prompt/cmd: `copy .env.example .env`; Bash, auch Git Bash unter Windows: `cp .env.example .env`. Eine vorhandene `.env` bearbeiten, nicht überschreiben. Die Datei `.env` bleibt ausserhalb von Git.

Die lokalen Kurswege verwenden `127.0.0.1`. Docker konfiguriert die Bindung automatisch; beim nativen Weg wird sie in der Dienstkonfiguration geprüft. Die mitgelieferten Zugangsdaten dienen der lokalen Lernumgebung. Codespaces erhält dieselben Standards direkt in den Service-Containern. Nach Änderungen an `.env` die Notebook-Kernel neu starten. Prozess-Umgebungsvariablen haben Vorrang vor `.env`.

| Beobachtung | Nächster Schritt |
| --- | --- |
| `conda` nicht gefunden | Conda für die verwendete Shell einrichten und das Terminal neu öffnen; siehe [Bash-Anleitung](docs/setup/BASH.md). Unter Windows ist Anaconda Prompt eine Alternative. |
| Environment bereits vorhanden | `conda env update -n rothstein-storage-workshop-2026 -f environment.yml --prune`, danach aktivieren. |
| Paket-/Kernelversion stimmt nicht | `python -c "import sys; print(sys.executable)"` prüfen; richtigen Interpreter und Notebook-Kernel auswählen. |
| Docker-Befehl oder Compose fehlt | Bei Weg A die [Installationsanleitung](docs/setup/INSTALLATION.md) durchführen. Bei Weg B ist Docker nicht erforderlich; die nativen Dienste verwenden. |
| Docker-Server nicht erreichbar / `dockerDesktopLinuxEngine` nicht gefunden | Docker Desktop/Engine starten und `docker version` prüfen; unter Windows Linux-Container und WSL-Start prüfen. |
| `pull` meldet Download-/Registryfehler | Die genaue `pull`-Meldung prüfen: beispielsweise Netzwerk/Proxy, Registry-Zugriff, Image-Tag oder Plattform. Der Python-Check kann das nicht beheben. |
| Port bereits belegt | Zuerst den Betriebsweg festlegen: **A:** konkurrierende Desktop-/native Instanz stoppen; **B:** konkurrierenden Datenbankcontainer stoppen. Für Neo4j beide Ports `7474` und `7687` berücksichtigen. Nur bei bewusst abweichenden Ports Server, `.env` und Browseradresse gemeinsam anpassen. [Start und Portkonflikte](docs/setup/NEO4J_START.md) |
| MongoDB/Neo4j nicht bereit | Lokal die nachfolgende [Fehlerdiagnose](#mongodb-oder-neo4j-meldet-failed) durchführen. In Codespaces die Erstellungslogs und danach die Setup-Ausgabe prüfen. |
| Anmeldung nach Passwortänderung fehlgeschlagen | Umgebungsvariablen ändern keine vorhandenen Datenbankbenutzer, weder in einem Volume noch in einer nativen Installation. Die tatsächlichen Zugangsdaten verwenden oder das Passwort kontrolliert im Dienst ändern. |
| MongoDB endet mit `Illegal instruction` | CPU-/Virtualisierungsunterstützung des Images prüfen; bei ungeeigneter lokaler Hardware Codespaces verwenden. |
| Arbeitsspeicher reicht nicht | Ressourcen für Docker beziehungsweise den Codespace erhöhen. Die Heap-/Cache-Einstellungen sind bereits auf den kleinen Kursbestand begrenzt. |
| Quelle/Prüfsumme stimmt nicht | Vollständig entpackte Originaleingaben wiederherstellen; für eigene Ergebnisse `data/work/` verwenden. |

### Die Datenprüfung meldet FAILED

Im Repo-Hauptordner die ausführliche Prüfung starten:

```bash
python ingestion/ingest.py verify
```

Die Meldung nennt die betroffene Datei oder die abweichende Prüfsumme.

- **Pipeline-Prüfsumme:** `ingestion/ingest.py` und `data/input/build_manifest.json` müssen aus derselben Workshop-Version stammen. Die zusammengehörigen Dateien aus der aktuellen ZIP beziehungsweise dem gleichen Git-Stand übernehmen.
- **Datei fehlt oder wurde verändert:** Die genannte Eingabedatei aus der vollständigen Workshop-ZIP wiederherstellen. Eigene Ergebnisse unter `data/work/` speichern.
- **Bewusst geänderte Aufbereitung:** Die neuen Eingaben mit `python ingestion/ingest.py build --output-dir data/work/rebuilt` getrennt erzeugen; die mitgelieferten Prüfsummen nicht von Hand anpassen.

Danach `python scripts/verify_setup.py` erneut ausführen. Eine erneute Installation des Conda-Environments ist bei einem reinen Datenfehler nicht erforderlich.

### MongoDB oder Neo4j meldet FAILED

Ein `ServerSelectionTimeoutError` oder `ServiceUnavailable` benennt noch nicht die genaue Ursache. Die Installation der Python-Treiber allein bestätigt keine Verbindung zum Server.

**Bei Weg B ohne Docker:** Zuerst [MongoDB-Dienst und Anmeldung](docs/setup/MONGODB_LOKAL.md) beziehungsweise [Neo4j-Desktop-Instanz und Bolt-Port](docs/setup/NEO4J_DESKTOP.md) prüfen. Die weiter unten beschriebenen Python-Verbindungsziele und Windows-Porttests gelten auch hier. Docker-Kommandos entfallen.

**Bei Weg A mit Docker:** Die folgenden Docker-Befehle aus dem Repo-Hauptordner verwenden.

**Zuerst die Engine prüfen:**

```bash
docker version
```

Wenn der Abschnitt **Server** mit Versionsinformationen fehlt, zuerst Docker zum Laufen bringen. Bei Windows zeigt das Docker-Desktop-Fenster gegebenenfalls einen WSL- oder Virtualisierungsfehler. Hilfreich sind dann die genaue Fenstermeldung und:

```bat
docker context ls
wsl --version
```

**Ist die Engine erreichbar, den Kurs-Stack starten und den Zustand samt Logs ansehen:**

```bash
docker compose up -d --wait
docker compose ps -a
docker compose logs --no-color --tail=80 mongodb neo4j
```

Die letzten beiden Befehle auch dann ausführen, wenn `up` mit einem Fehler endet. `ps -a` zeigt auch gestoppte Container; `logs` zeigt deren Meldungen. [Docker: Containerzustand](https://docs.docker.com/reference/cli/docker/compose/ps/), [Docker: Logs](https://docs.docker.com/reference/cli/docker/compose/logs/)

| Ergebnis | Bedeutung und nächster Schritt |
| --- | --- |
| Keine Zeilen für die beiden Services | Die Kurscontainer wurden in diesem Docker-Kontext noch nicht erstellt oder bereits entfernt. Repo-Ordner und vollständige Ausgabe von `up` prüfen. |
| `Created`, `Exited` oder `Restarting` | Der Dienst läuft noch nicht stabil. Die Startmeldung und die Logs sind entscheidend, etwa bei Portkonflikten, Konfigurationsfehlern oder Speicherproblemen. |
| `health: starting` | Die Bereitschaftsprüfung ist noch nicht erfolgreich abgeschlossen. Den laufenden Start abwarten; bei einem Startfehler die Logs prüfen. |
| `unhealthy` | Der Container wurde gestartet, besteht aber die Bereitschaftsprüfung nicht. Logs und Zugangsdaten prüfen. |
| Beide `healthy`, Python weiterhin `FAILED` | Die internen Dienstprüfungen funktionieren. Nun den Weg vom Python-Prozess zum veröffentlichten Port und die dort verwendeten Einstellungen prüfen. |

**Wenn beide Dienste laufen, aber Python weiterhin scheitert – alle lokalen Wege:**

Im aktivierten Storage-Environment die tatsächlich verwendeten Ziele anzeigen lassen; der Befehl gibt keine Passwörter aus:

```bash
python -c "from scripts.storage_runtime import connection_summary; print(connection_summary())"
```

Lokal sind die Standards **MongoDB: `127.0.0.1:27017`**, **Neo4j: `127.0.0.1:7687`**, Datenbank **`neo4j`**. Andere Ports müssen mit dem gewählten Server übereinstimmen: bei Weg A mit `docker compose ps -a`, bei Weg B mit den Desktop-Instanzdetails beziehungsweise der MongoDB-Dienstkonfiguration. Die Hostnamen `mongodb` und `neo4j` gehören zum internen Codespaces-Netz und sind nicht die lokalen Standardziele.

Unter Windows zusätzlich in **PowerShell** die beiden Standardports prüfen:

```powershell
Test-NetConnection -ComputerName 127.0.0.1 -Port 27017
Test-NetConnection -ComputerName 127.0.0.1 -Port 7687
```

Bei angepassten Ports die Zahlen entsprechend ersetzen. `TcpTestSucceeded: True` bestätigt eine TCP-Verbindung, aber noch keine erfolgreiche Datenbankanmeldung. Bei `False` die Portzuordnung und gegebenenfalls lokale Firewall-/VPN-Regeln für diese Verbindung prüfen. Schutzfunktionen nicht pauschal deaktivieren. [Microsoft: Test-NetConnection](https://learn.microsoft.com/en-us/powershell/module/nettcpip/test-netconnection)

Für Unterstützung die Ausgabe von **`up`**, **`ps -a`**, **`logs`** und dem aktuellen **Setup-Check** weitergeben. Falls eigene Zugangsdaten in Logs vorkommen, diese vorher ausblenden. Ein Volume-Reset oder eine Neuinstallation ist kein erster Diagnoseschritt.

### Eingeschränkte Prüfung ohne laufende Datenbankdienste

Für eine ausdrücklich eingeschränkte Diagnose ohne Datenbankdienste:

```bash
python scripts/verify_setup.py --offline
```

**BASIS OK** bestätigt dabei Python, Eingaben, SQLite und TinyFlux. Es ersetzt kein **SETUP OK** für alle vier Systeme.

## Neue Dateien nach einem Workshopblock laden

Aufgabe, Musterlösung und Walkthrough liegen direkt im jeweiligen Task-Ordner. Die Musterlösung erhält den eigenen Dateinamen `task_sample_solution.ipynb`; die eigene `task.ipynb` bleibt erhalten.

Mit Git zuerst speichern und den eigenen Stand committen/pushen, anschliessend den Fork auf GitHub über **Sync fork → Update branch** synchronisieren. Danach:

```bash
git pull --ff-only
```

Bei einem gemeldeten Konflikt die betroffenen Dateien prüfen; kein erzwungenes Zurücksetzen des eigenen Stands verwenden. Ohne Git nur die angekündigten neuen Dateien an ihren jeweiligen Platz kopieren. Ein neues Lösungsnotebook erfordert kein neues Environment.

Wenn Paketversionen geändert werden, lokal das Conda-Environment wie oben aktualisieren. In Codespaces `python -m pip install -r requirements.txt` ausführen. Nach Änderungen an Container-/Dienstkonfiguration **Codespaces: Rebuild Container** verwenden und den Setup-Check erneut ausführen; eigene Arbeit vorher sichern.

## Technische Vertiefung

[Architektur und Modellgrenzen](docs/setup/ARCHITEKTUR.md) · [Aktenleseführer](docs/AKTENLESEFUEHRER.md) · [Ingestion](ingestion/README.md)


## SQLite-Paket eigenständig prüfen

Für die [SQLite-Demo](demos/microblogging/01_sqlite.ipynb) und die [SQLite-Aufgabe](tasks/01_sqlite/task.ipynb) genügt die aktivierte Kursumgebung. Die Datenbankdienste müssen dafür nicht laufen. Öffne die Notebooks mit dem Kernel **Python (rothstein-storage-workshop-2026)**.

Ein ergänzender Materialtest führt die Codezellen in einer temporären Kopie aus und prüft die Ergebnisse, ohne Deine Arbeitsdatenbanken zu verändern:

```bash
python validation/validate_sqlite.py
```

Für den zusätzlichen echten Notebook-Kerneltest:

```bash
python validation/validate_sqlite.py --kernel
```

Ausgeführte Notebook-Kopien dieses Kerneltests liegen unter `data/work/sqlite_execution/`.


## Git: Zeilenenden und temporäre Dateien

Die Repo-Regel `* text=auto eol=lf` vereinheitlicht Textdateien auf LF, auch beim Auschecken unter Windows. Die nachfolgenden Ausnahmen in `.gitattributes` erhalten den Rohkatalog und die ursprünglichen Microblogging-Dateien bytegenau. Diese Ausnahmen beibehalten, da ihre Prüfsummen Bestandteil der Datenprüfung sind.

Eine Meldung `LF will be replaced by CRLF` bei `git add` ist eine Warnung zur Zeilenendenkonvertierung, kein fehlgeschlagener Import oder Push. Bei einem älteren Paket die erste Zeile von `.gitattributes` auf die oben genannte Regel aktualisieren und anschliessend `git add --renormalize .` ausführen. [Git: Zeilenendenregeln](https://git-scm.com/docs/gitattributes).

Temporäre Mamba-Dateien im Repo-Hauptordner werden durch `/mamba*` in `.gitignore` ausgeschlossen. Bereits zum Commit vorgemerkte Dateien entfernt eine nachträglich ergänzte Ignore-Regel nicht: In diesem Fall mit `git rm --cached -- DATEINAME` gezielt aus der Vormerkung nehmen. Die lokale Datei bleibt dabei erhalten.


## MongoDB-Modellpaket prüfen

Die [MongoDB-Demo](demos/microblogging/02_mongodb.ipynb) und die [UAP-Aufgabe](tasks/02_mongodb/task.ipynb) verwenden den vorhandenen MongoDB-Dienst. Es sind keine neuen Pakete oder Änderungen der Containerkonfiguration erforderlich. Lokal die Kursumgebung aktivieren; Codespaces verwendet die vorbereitete Python-Umgebung.

Vorbereitung ohne Datenbankzugriff prüfen:

```bash
python validation/validate_mongodb.py
```

Mit laufendem MongoDB-Server den vollständigen Codezellen- und Jupyter-Test ausführen:

```bash
python validation/validate_mongodb.py --server --kernel
```

Der Test verwendet eigene Collections in `storage_setup` und entfernt nur diese. Die UAP-Aufgabe speichert in `storage_uap.catalog` und `storage_uap.reading_notes`; die Musterlösung verwendet die Suffixe `_sample_solution`. Ein erneuter Katalogimport erhält separat gespeicherte Lesernotizen.


## Neo4j-Modellpaket prüfen

Das Neo4j-Modellpaket verwendet die gemeinsame Python-Umgebung und den gestarteten Neo4j-Dienst. [Demo](demos/microblogging/03_neo4j.ipynb), [Aufgabe](tasks/03_neo4j/task.ipynb) und [Musterlösung](tasks/03_neo4j/task_sample_solution.ipynb) liegen in getrennten Kursbereichen innerhalb der Datenbank `neo4j`. Eine neue Datenbank oder APOC ist nicht erforderlich.

Nur Vorbereitung und Notebook-Syntax prüfen:

```bash
python validation/validate_neo4j.py
```

Mit laufendem Neo4j-Server und registriertem Kurskernel:

```bash
python validation/validate_neo4j.py --server --kernel
```

Die vollständige Prüfung verwendet eigene Graphbereiche mit zufälligem Testpräfix und entfernt ausschliesslich diese Bereiche. Die normalen Demo-, Aufgaben- und Lösungsdaten bleiben erhalten. Ausgeführte Notebook-Kopien liegen unter `data/work/neo4j_execution/`. Die [Aktualisierungshinweise](docs/setup/AKTUALISIERUNG.md) beschreiben das Übernehmen der aktuellen Projektversion.


## TinyFlux-Modellpaket prüfen

[Demo](demos/microblogging/04_tinyflux.ipynb), [Aufgabe](tasks/04_tinyflux/task.ipynb) und [Musterlösung](tasks/04_tinyflux/task_sample_solution.ipynb) verwenden das vorhandene Paket TinyFlux 1.2.0. Ein zusätzlicher Server, neue Pakete oder ein Neuaufbau von Codespaces sind für diese Materialergänzung nicht erforderlich. Lokal das Kurs-Environment aktivieren und für die Notebooks den Kurskernel wählen.

Codezellen mit echten TinyFlux-Dateien und unabhängigen Referenzwerten prüfen:

```bash
python validation/validate_tinyflux.py
```

Für den zusätzlichen Jupyter-Kerneltest in Deiner Kursumgebung:

```bash
python validation/validate_tinyflux.py --kernel
```

Der Test verwendet ausschliesslich temporäre Datenbankdateien. Demo-, Aufgaben- und Lösungsdaten bleiben erhalten. Beim Kerneltest werden ausgeführte Notebook-Kopien unter `data/work/tinyflux_execution/` abgelegt; die eigentlichen Aufgaben-Notebooks werden nicht überschrieben.

Die [Aktualisierungshinweise](docs/setup/AKTUALISIERUNG.md) beschreiben das Übernehmen neuer Projektdateien.
