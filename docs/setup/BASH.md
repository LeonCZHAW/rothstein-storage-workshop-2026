[Workshop-Übersicht](../../README.md) · [Technische Vorbereitung](../../README_technical_preparation.md)

# Die Workshop-Befehle in Bash ausführen

**Ja.** Die Befehle mit `conda`, `python`, `jupyter`, `git` und `docker compose` funktionieren auch in Bash, sofern das jeweilige Programm installiert und erreichbar ist. Du verwendest dieselbe `environment.yml`, dieselbe `requirements.txt` und dieselben Notebooks. Nur einige Windows-Befehle für Ordner, Dateien und Dienste unterscheiden sich.

## Windows: Git Bash einmalig für Conda einrichten

1. Anaconda oder Miniconda muss bereits installiert sein. Git Bash gehört zu [Git für Windows](https://git-scm.com/install/windows).
2. Einmalig **Anaconda Prompt** öffnen und ausführen:

```bat
conda init bash
```

3. Alle Git-Bash-Fenster schliessen und Git Bash neu öffnen; bei Verwendung in VS Code auch das dortige Terminal neu öffnen.
4. In **Git Bash** prüfen:

```bash
conda --version
```

Falls `conda` weiterhin nicht gefunden wird: Im Anaconda Prompt mit `conda info --base` den Installationsordner ermitteln. Dann in Git Bash dessen `etc/profile.d/conda.sh` laden. Beispiel für den Installationsordner `C:\Users\DEIN-NAME\miniconda3`:

```bash
source "/c/Users/DEIN-NAME/miniconda3/etc/profile.d/conda.sh"
conda --version
```

Den Pfad an Deine Installation anpassen. Dieser `source`-Befehl gilt für das aktuelle Bash-Fenster. Ist die Initialisierung noch nicht wirksam, ihn beim nächsten Öffnen erneut verwenden. Kein zweites Conda installieren.

## macOS und Linux

Wenn `conda activate` in Bash bereits funktioniert, ist nichts zu ändern. Andernfalls in einem Terminal, in dem `conda` verfügbar ist, einmalig `conda init bash` ausführen und Bash neu öffnen. Bei macOS ist das Standardterminal häufig **zsh**; dafür lautet der Befehl `conda init zsh`. Auch dort funktionieren die folgenden Workshop-Befehle.

Ist `conda` gar nicht verfügbar, zunächst [Conda installieren](INSTALLATION.md#1-conda-bereitstellen) beziehungsweise die `etc/profile.d/conda.sh` Deiner vorhandenen Installation laden. [Conda: Shell initialisieren](https://docs.conda.io/projects/conda/en/stable/commands/init.html)

## Lokal: Workshop in Bash starten

In den entpackten Repo-Hauptordner wechseln. Beispiel **Windows/Git Bash**:

```bash
cd "/c/Users/DEIN-NAME/Documents/rothstein-storage-workshop-2026"
ls environment.yml
```

Unter macOS beginnt ein entsprechender Benutzerpfad mit `/Users/…`, unter Linux häufig mit `/home/…`. Den tatsächlichen Ordner verwenden. `environment.yml` muss gefunden werden.

Nur bei der **ersten Einrichtung**:

```bash
conda env create -f environment.yml
conda activate rothstein-storage-workshop-2026
python -m ipykernel install --user --name rothstein-storage-workshop-2026 --display-name "Python (rothstein-storage-workshop-2026)"
```

Bei späteren Starts genügt:

```bash
conda activate rothstein-storage-workshop-2026
```

Danach die Datenbanken passend zum gewählten Weg starten:

- **Weg A:** Docker Desktop/Engine starten, konkurrierende native Datenbankinstanzen stoppen und `docker compose up -d --wait` ausführen.
- **Weg B:** MongoDB-Dienst und Neo4j-Kursinstanz in Desktop starten, wie in [Lokal ohne Docker](OHNE_DOCKER.md) beschrieben.

Wenn beide Datenbanken laufen:

```bash
python scripts/verify_setup.py
```

Erst nach **SETUP OK**:

```bash
jupyter lab
```

Im Notebook den Kernel **Python (rothstein-storage-workshop-2026)** wählen. Das Jupyter-Terminal geöffnet lassen.

## Kleine Unterschiede zur Windows-Anleitung

| Anaconda Prompt / cmd | Bash, einschliesslich Git Bash |
| --- | --- |
| `cd /d "C:\Ordner\Workshop"` | `cd "/c/Ordner/Workshop"` unter Windows |
| `dir environment.yml` | `ls environment.yml` |
| `copy .env.example .env` | `cp .env.example .env` |

`.env` nur kopieren, wenn noch keine vorhanden ist und Du von den Kursstandards abweichen musst. Eine vorhandene Datei bearbeiten.

Ausdrücklich als **PowerShell** markierte Befehle wie `Test-NetConnection` oder Windows-Dienstbefehle dort ausführen. Sie werden durch Git Bash nicht zu Bash-Befehlen. Die Python-Prüfung oben funktioniert in beiden Shells und prüft auch die Datenbankanmeldung.

**Git Bash und WSL sind verschieden:** Git Bash verwendet hier Deine Windows-Conda-Installation. WSL ist eine eigene Linux-Umgebung und benötigt eine eigene Linux-Python-Umgebung; die Windows-Environmentdateien auf der Festplatte ersetzen deren Installation nicht. Für Weg B unter Windows empfiehlt diese Anleitung Git Bash oder Anaconda Prompt, damit Python und die nativen Datenbankdienste im selben System laufen.

## Codespaces

Das integrierte Terminal ist bereits für den Workshop vorbereitet. Dort weder Conda installieren noch `conda activate` ausführen. Nach dem automatischen Aufbau genügt:

```bash
python scripts/verify_setup.py
```

Notebooks direkt in VS Code im Browser öffnen. Für die Graphansicht: [Neo4j Browser in Codespaces starten](NEO4J_START.md#weg-c-codespaces).
