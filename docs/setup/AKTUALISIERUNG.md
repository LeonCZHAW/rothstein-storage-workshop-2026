[Workshop-Übersicht](../../README.md) · [Technische Vorbereitung](../../README_technical_preparation.md) · [Neo4j starten](NEO4J_START.md)

# Bestehende Workshop-Umgebungen aktualisieren

Der Workshop wird unter **rothstein-storage-workshop-2026** für verschiedene Klassen verwendet. Projektname, lokale Conda-Umgebung und Notebook-Kernel sind entsprechend benannt. Die Wege heissen **A: lokal mit Docker**, **B: lokal ohne Docker** und **C: Codespaces**.

## 1. Vor dem Einspielen der neuen Dateien

Eigene Notebook-Bearbeitungen speichern und sichern. Die neue ZIP enthält auch Aufgaben und Musterlösungen; beim Kopieren keine eigenen Lösungen ungeprüft überschreiben. Eine vorhandene `.env`, Datenbank-Volumes und Arbeitsdaten weiterverwenden und erhalten. Die ZIP enthält die Projektdateien; ein bestehendes Git-Repository behält seinen eigenen `.git`-Ordner und seine Remote-Adresse.

**Bei einer bisherigen lokalen Docker-Installation:** Noch mit der bisherigen Compose-Konfiguration im bisherigen Repo-Ordner den Projektnamen ansehen und die Container stoppen:

```bash
docker compose ls
docker compose stop
```

Den bisherigen Projektnamen für den nächsten Abschnitt notieren. `stop` erhält die Container und Volumes. Danach die neuen Projektdateien einspielen. Alte Datenbanken nicht durch Löschen von Volumes zurücksetzen.

Die Umbenennung der Projektdateien benennt kein bestehendes GitHub-Repository um. Zum Klonen stets die tatsächliche HTTPS-Adresse des eigenen Forks verwenden; der lokale Zielordner kann `rothstein-storage-workshop-2026` heissen.

## 2. Bestehende Datenbankbestände erhalten

Der neue Standardname in `compose.yaml` lautet `rothstein-storage-workshop-2026`. Docker Compose ordnet seine benannten Volumes dem Projektnamen zu. Ein neuer Projektname kann deshalb neue, leere Volumes verwenden, während die bisherigen Volumes weiter vorhanden sind.

**Wenn Du Deine bisherigen lokalen Docker-Datenbanken weiterverwenden willst:** In der vorhandenen `.env` ergänzen beziehungsweise den bestehenden Wert prüfen:

```dotenv
COMPOSE_PROJECT_NAME=DEIN_BISHERIGER_PROJEKTNAME
```

Den Platzhalter durch den zuvor mit `docker compose ls` ermittelten Namen dieses Workshopprojekts ersetzen. Der Name muss zum bisher verwendeten Projekt und seinen Volumes gehören. Diese Einstellung behält die Zuordnung bei; sie kopiert oder migriert keine Daten. Falls `COMPOSE_PROJECT_NAME` bereits als Prozessvariable gesetzt ist, hat diese Vorrang. [Docker Compose: Projektname](https://docs.docker.com/compose/how-tos/project-name/)

Bei einer bewusst frischen Umgebung kann der neue Standardname verwendet und der Graph über die Notebook-Importzellen neu aufgebaut werden. Vorher die alten Container stoppen, damit sie die Ports nicht weiter belegen. Eigene Änderungen in den alten Datenbanken werden durch einen Neuimport aus den Workshopdateien nicht übertragen.

**Bei Neo4j Desktop:** Dieselbe vorhandene Datenbankinstanz weiterverwenden. Ein neuer Anzeigename erfordert keine neue Instanz. Tatsächliche Ports und Zugangsdaten beibehalten.

## 3. Lokale Python-Umgebung und Kernel

Für die nun allgemein benannte Umgebung einmalig ausführen:

```bash
conda env create -f environment.yml
conda activate rothstein-storage-workshop-2026
python -m ipykernel install --user --name rothstein-storage-workshop-2026 --display-name "Python (rothstein-storage-workshop-2026)"
```

Falls eine Umgebung mit diesem neuen Namen bereits existiert, stattdessen `conda env update -n rothstein-storage-workshop-2026 -f environment.yml --prune` verwenden und anschliessend aktivieren. Eine bisher anders benannte Umgebung wird dadurch nicht entfernt.

In VS Code den passenden Python-Interpreter und im Notebook den Kernel **Python (rothstein-storage-workshop-2026)** auswählen. Bestehende Notebook-Kernel neu starten. `environment.yml` bindet weiterhin die gemeinsame Paketliste `requirements.txt` ein; für Codespaces wird dieselbe Paketliste verwendet.

## 4. Codespaces

Eigene Dateien speichern und wichtige Datenbankänderungen vor einem Umbau sichern. Die neue Konfiguration einspielen und **Codespaces: Rebuild Container** ausführen. Das Setup registriert den neuen Kernel und richtet die Neo4j-Portweiterleitungen ein. Eine lokale Docker-Installation ist dafür nicht erforderlich.

Bei wichtigen vorhandenen Datenbankbeständen vor dem Rebuild die verwendeten Volumes beziehungsweise einen Export sichern: Eine veränderte Compose-Projektzuordnung kann zu neuen leeren Datenbanken führen. Danach prüfen, ob der erwartete Bestand vorhanden ist. Die ursprünglichen Workshopdaten können bei Bedarf über die Notebook-Importzellen geladen werden.

## 5. Gewählten Weg prüfen

Die Dienste genau eines Betriebswegs starten. Lokal dürfen Neo4j-Desktop-Instanz und Neo4j-Container nicht gleichzeitig die Standardports verwenden. Dann im Repo-Hauptordner:

```bash
python scripts/verify_setup.py
```

**SETUP OK** bestätigt die vorgesehenen Setup-Schreib-/Lesetests, nicht automatisch sämtliche fachlichen Notebook-Aufgaben. Anschliessend ein Notebook und dessen zugehörige Graphansicht an derselben Neo4j-Instanz prüfen. Die [Startanleitung](NEO4J_START.md) zeigt die Schritte für A, B und C.

## Ergänzung: Bash und Codespaces-Browser

Die aktuellen Dateien enthalten eine [Bash-Anleitung](BASH.md) und den gemeinsamen Browserzugang über Port `8080`. Für bestehende Codespaces die aktualisierten Repo-Dateien übernehmen, eigene Änderungen sichern und **Codespaces: Rebuild Container** ausführen. Nicht benötigte alte Weiterleitungen von `7474`/`7687` können im Register Ports entfernt werden; die Datenbankdienste selbst bleiben bestehen. Details: [Neo4j in Codespaces](NEO4J_START.md#weg-c-codespaces).
