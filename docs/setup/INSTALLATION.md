[Workshop-Übersicht](../../README.md) · [Technische Vorbereitung](../../README_technical_preparation.md) · [Microblogging-Beispiele](../../demos/microblogging/README.md)

# Lokale Software installieren und Docker prüfen

Diese Anleitung beschreibt **Weg A: lokal mit Docker**. Für **Weg B: lokal ohne Docker** gelten die separaten [Installationsschritte mit MongoDB Community und Neo4j Desktop](OHNE_DOCKER.md); nur die Conda- und optionalen Editor-/Git-Schritte auf dieser Seite sind gemeinsam. Für GitHub Codespaces im Browser sind diese lokalen Installationen nicht nötig. Dort gilt [Weg C der technischen Vorbereitung](../../README_technical_preparation.md#weg-c-codespaces).

Bereits installierte Komponenten kannst Du weiterverwenden, wenn die beschriebenen Prüfungen erfolgreich sind. Führe nur den Abschnitt für Dein Betriebssystem aus.

**Bash ist ebenfalls möglich:** Die [Bash-Anleitung](BASH.md) erklärt die einmalige Conda-Einrichtung, Windows/Git-Bash-Pfade und die wenigen abweichenden Befehle.

## 1. Conda bereitstellen

Wenn Anaconda oder Miniconda bereits installiert ist, öffne unter Windows **Anaconda Prompt**, unter macOS/Linux ein Terminal, und prüfe:

```bash
conda --version
```

Wird eine Version angezeigt, ist keine zweite Installation nötig. Fehlt Conda, öffne die [offizielle Installationsauswahl](https://www.anaconda.com/docs/getting-started/installation), wähle **Miniconda**, Dein Betriebssystem und den passenden Prozessor, und folge dem dortigen Installer:

| Betriebssystem | Installation und anschliessender Einstieg |
| --- | --- |
| Windows | Den Windows-Installer ausführen. Danach **Anaconda Prompt** aus dem Startmenü öffnen; hier sind die Conda-Befehle eingerichtet. |
| macOS | Installer passend zu Apple Silicon oder Intel wählen. Die Shell-Einrichtung gemäss Installer abschliessen und ein neues Terminal öffnen. |
| Linux | Installer passend zur Prozessorarchitektur wählen. Die Shell-Initialisierung gemäss Anleitung durchführen und ein neues Terminal öffnen. |

Danach `conda --version` erneut prüfen. Die Kursumgebung mit Python 3.12 wird erst im Repo mit `environment.yml` erstellt. Ein separat installierter System-Python ist dafür nicht erforderlich.

## 2. Docker für Dein Betriebssystem einrichten

### Windows: Docker Desktop mit WSL 2

Die [Docker-Anleitung für Windows](https://docs.docker.com/desktop/setup/install/windows-install/) enthält die aktuellen Systemanforderungen und den Installer. Für den Kursweg benötigst Du einen unterstützten Windows-Rechner mit aktivierter Hardwarevirtualisierung sowie WSL 2.

**WSL prüfen:** In PowerShell oder Anaconda Prompt ausführen:

```bat
wsl --version
```

Docker Desktop setzt gemäss der oben verlinkten Anleitung mindestens WSL-Version **2.1.5** voraus. Die Paketversion ist von der Bezeichnung des Backends **WSL 2** zu unterscheiden.

Wenn WSL fehlt, **PowerShell als Administrator** öffnen und installieren:

```powershell
wsl --install --no-distribution
```

Wenn WSL bereits vorhanden ist und aktualisiert werden muss, stattdessen:

```powershell
wsl --update
```

Einen angeforderten Windows-Neustart durchführen und `wsl --version` erneut prüfen. `--no-distribution` installiert WSL ohne zusätzliche Ubuntu-Umgebung. Docker Desktop benötigt für Befehle aus dem Windows-Terminal keine separat eingerichtete Linux-Distribution. [Microsoft: WSL-Befehle](https://learn.microsoft.com/en-us/windows/wsl/basic-commands), [Docker: WSL-Backend](https://docs.docker.com/desktop/features/wsl/)

**Docker Desktop installieren und starten:**

1. Den passenden Windows-Installer auf der oben verlinkten Docker-Seite herunterladen und ausführen.
2. Falls die Backend-Auswahl erscheint, **WSL 2** wählen. Die Einrichtung vollständig abschliessen, einschliesslich eines angeforderten Neustarts.
3. **Docker Desktop** im Windows-Startmenü öffnen und den Einrichtungsdialog abschliessen.
4. Unter **Settings → General**, soweit sichtbar, **Use WSL 2 based engine** aktivieren und anwenden. Bei manchen Installationen ist WSL 2 bereits voreingestellt und die Auswahl nicht sichtbar.
5. Falls das Menü des Docker-Symbols neben der Windows-Uhr **Switch to Linux containers** anbietet, diesen Eintrag wählen. Steht dort **Switch to Windows containers**, ist bereits der richtige Modus aktiv.
6. Warten, bis die Engine gestartet ist, und anschliessend Abschnitt 3 durchführen.

Die WSL- und Linux-Container-Einstellungen erläutert die [Docker-Dokumentation](https://docs.docker.com/desktop/features/wsl/). Wenn Docker einen Virtualisierungsfehler meldet, den Status unter **Task-Manager → Leistung → CPU → Virtualisierung** prüfen; eine deaktivierte Hardwarevirtualisierung muss in den Geräteeinstellungen beziehungsweise durch die zuständige IT aktiviert werden. Die genaue Docker-Meldung für die Fehlerklärung festhalten.

Docker Desktop muss während der lokalen Arbeit laufen. Die Aktivierung eines Conda-Environments startet Docker nicht.

### macOS: Docker Desktop

1. Unter **Apple-Menü → Über diesen Mac** prüfen, ob Dein Mac Apple Silicon oder einen Intel-Prozessor verwendet.
2. Auf der [Docker-Installationsseite für macOS](https://docs.docker.com/desktop/setup/install/mac-install/) die passende Variante herunterladen.
3. Die DMG-Datei öffnen, Docker nach **Programme / Applications** ziehen und dort **Docker.app** starten.
4. Die Ersteinrichtung abschliessen. Wenn die gewählten Installationseinstellungen ein Passwort verlangen, den vorgesehenen macOS-Dialog verwenden.
5. Die gestartete Engine abwarten und Abschnitt 3 durchführen. Docker Desktop während der lokalen Arbeit laufen lassen.

Die Kurs-Images bieten Intel- und ARM-Varianten. Eine erzwungene Intel-Emulation auf Apple Silicon ist in der Repo-Konfiguration nicht vorgesehen.

### Linux: Docker Engine und Compose

1. Die [offizielle Docker-Engine-Anleitung](https://docs.docker.com/engine/install/) öffnen und Deine Distribution wählen, beispielsweise [Ubuntu](https://docs.docker.com/engine/install/ubuntu/) oder [Debian](https://docs.docker.com/engine/install/debian/).
2. Die dort beschriebene Paketquelle einrichten und die Engine einschliesslich CLI, Container-Laufzeit und Compose-Plugin installieren. Bei Ubuntu/Debian heissen die offiziellen Pakete `docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin` und `docker-compose-plugin`. Die distributionsspezifischen Schritte gehören zur Installation; ein Python-Paket namens `docker` ersetzt diese Komponenten nicht.
3. Bei einer Standardinstallation mit systemd den Dienst prüfen und bei Bedarf starten:

```bash
sudo systemctl start docker
sudo systemctl status docker --no-pager
```

4. Den Zugriff Deines Benutzerkontos nach den [Docker-Schritten nach der Installation](https://docs.docker.com/engine/install/linux-postinstall/) einrichten. Die dort beschriebene Mitgliedschaft in der Gruppe `docker` gewährt weitreichende Systemrechte. Nach einer Gruppenänderung vollständig ab- und wieder anmelden. Alternativ eine bereits eingerichtete Rootless-Installation verwenden. Die Kursbefehle setzen anschliessend Docker-Zugriff aus Deinem normalen Benutzerterminal voraus.
5. Falls die Engine bereits installiert ist, Compose aber fehlt, das [Compose-Plugin](https://docs.docker.com/compose/install/linux/) über die eingerichtete Docker-Paketquelle ergänzen. Danach Abschnitt 3 durchführen.

Die `systemctl`-Befehle oben gelten für die normale systemweite Engine. Eine Rootless-Installation verwendet ihren eigenen Benutzerdienst. Verwende die zu Deiner bestehenden Installation gehörenden Startschritte.

## 3. Die Installation wirklich prüfen

Im Terminal, das Du später für den Kurs verwendest:

```bash
docker version
docker compose version
```

**Beide Befehle müssen erfolgreich sein.** `docker version` zeigt Versionsinformationen sowohl für **Client** als auch für **Server**. Nur eine Client-Version mit anschliessendem Verbindungsfehler bestätigt keine laufende Engine. [Docker: version](https://docs.docker.com/reference/cli/docker/version/)

Danach einen kleinen Testcontainer ausführen:

```bash
docker run --rm hello-world
```

Bei Erfolg erscheint **Hello from Docker!**. Damit sind auch der Abruf eines Images und der Containerstart geprüft. Der Testcontainer wird danach entfernt. Die MongoDB-/Neo4j-Container werden durch diesen Test noch nicht gestartet.

| Meldung | Was Du als Nächstes prüfst |
| --- | --- |
| `docker` nicht gefunden | Docker installieren beziehungsweise nach der Installation ein neues Terminal öffnen. |
| `compose` ist kein Docker-Befehl | Compose-Plugin installieren; bei Docker Desktop ist es enthalten. |
| `dockerDesktopLinuxEngine` nicht gefunden | Docker Desktop öffnen, Linux-Engine vollständig starten lassen und ihre Fenstermeldung prüfen. |
| `permission denied` auf den Docker-Socket unter Linux | Benutzerzugriff gemäss Linux-Abschnitt einrichten. |
| Registry-/Downloadfehler | Die genaue Meldung sowie Netzwerk- oder Proxyzugang prüfen; auch ein laufender Docker-Server benötigt Zugriff auf das Image. |

## 4. Optional: VS Code und Git

Für **VS Code** den [Editor](https://code.visualstudio.com/download) installieren. In der Erweiterungsansicht nach **Python** und **Jupyter** suchen und jeweils die Erweiterung von **Microsoft** installieren. Danach wird im Kursnotebook der Kernel des Storage-Environments ausgewählt. [Microsoft: Jupyter-Notebooks](https://code.visualstudio.com/docs/datascience/jupyter-notebooks)

Für **Fork/Clone** [Git installieren](https://git-scm.com/downloads), ein neues Terminal öffnen und `git --version` prüfen. Bei der ZIP-Variante ist Git optional. JupyterLab wird mit der Kursumgebung installiert und benötigt keinen separaten Installer.

## 5. Zurück zur Repo-Einrichtung

**Vor dem Containerstart** eine laufende Neo4j-Desktop-Instanz und einen nativen MongoDB-Server stoppen, falls sie die Standardports belegen. [Neo4j-Startanleitung](NEO4J_START.md).

Jetzt die [technische Vorbereitung ab A1 oder A2](../../README_technical_preparation.md#weg-a-lokal-mit-docker) durchführen: Repo öffnen, Kursumgebung erstellen, Images herunterladen, **beide Datenbankcontainer starten**, deren Zustand prüfen und danach den Python-Setup-Check ausführen.

Für den Containerweg werden MongoDB, Neo4j, Java, MongoDB Compass und Neo4j Desktop nicht zusätzlich auf dem Host benötigt. Die beiden letzten Programme sind für die Kursaufgaben keine Voraussetzung.
