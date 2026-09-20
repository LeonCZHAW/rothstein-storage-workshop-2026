[Workshop-Übersicht](../../README.md) · [Technische Vorbereitung](../../README_technical_preparation.md) · [Microblogging-Beispiele](../../demos/microblogging/README.md) · [Ohne Docker](OHNE_DOCKER.md) · [Neo4j Desktop](NEO4J_DESKTOP.md)

# MongoDB Community Server lokal installieren

Diese Anleitung richtet eine neue lokale Kursinstallation von **MongoDB Community Server 8.0.x** ein. Sie gilt für das Microblogging-Beispiel und den UAP-Workshop. Der Server speichert die Daten; **mongosh** ist die Shell für seine Einrichtung. **MongoDB Compass** ist eine optionale grafische Oberfläche. Das Python-Paket **pymongo** ist der bereits im Kurs-Environment enthaltene Treiber.

Falls auf Deinem Rechner bereits MongoDB mit eigenen Daten läuft, keine vorhandene Installation, Konfiguration oder Benutzer überschreiben. Einen vorhandenen Administrator für die unten beschriebene Kursbenutzer-Anlage verwenden oder eine separate Kursinstanz einrichten. Die nachfolgende Erstbenutzer-Anlage gilt ausschliesslich für eine neue Instanz ohne Benutzer.

Ein noch laufender MongoDB-Kurscontainer muss vor der nativen Nutzung des Standardports gestoppt werden. Bei einem Rechner ohne Docker entfällt dieser Schritt. Die Einordnung steht unter [Weg B](OHNE_DOCKER.md).

## 1. Server und Shell installieren

### Windows

1. Über die [MongoDB-8.0-Anleitung für Windows](https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-windows/) den **Community Server 8.0.x als MSI** herunterladen. Vorzugsweise 8.0.30 verwenden, sofern angeboten. Die Installation erfolgt direkt unter Windows.
2. Den Installer ausführen und **Complete** wählen. Die Einrichtung als Windows-Dienst **MongoDB** aktiviert lassen; der vorgeschlagene Dienstbenutzer kann für die neue Kursinstallation verwendet werden.
3. Daten- und Log-Verzeichnis aus dem Installer notieren. Compass ist optional.
4. **mongosh separat installieren**: Die Server-MSI enthält diese Shell nicht. Die [mongosh-Installationsanleitung](https://www.mongodb.com/docs/mongodb-shell/install/) verwenden und die Shell ausführbar über `PATH` einrichten. Anschliessend ein neues Terminal öffnen.
5. Versionen im Anaconda Prompt prüfen. Bei anderem Installationsort den Serverpfad anpassen:

```bat
"C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --version
mongosh --version
```

Die Serverversion soll mit `8.0.` beginnen. Die Shell hat eine eigene Versionsnummer. Der Installer startet den Windows-Dienst normalerweise direkt; für die nachfolgende Konfiguration wird er gezielt gestoppt.

### macOS

Die [MongoDB-8.0-Anleitung für macOS](https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-os-x/) nennt die unterstützten Systeme und verwendet Homebrew. Sie setzt derzeit macOS 14 oder neuer auf geeignetem Intel- oder Apple-Silicon-Rechner voraus.

Wenn noch nicht vorhanden, zuerst die **Xcode Command Line Tools** installieren:

```bash
xcode-select --install
```

Danach **Homebrew** nach der [offiziellen Homebrew-Anleitung](https://brew.sh/) installieren und deren Shell-Einrichtung abschliessen. Mit `brew --version` prüfen. Anschliessend im Terminal:

```bash
brew update
brew tap mongodb/brew
brew trust mongodb/brew
brew install mongodb-community@8.0
mongod --version
mongosh --version
```

Das offizielle Homebrew-Paket enthält Server und Shell. Falls eine ältere Homebrew-Version `brew trust` noch nicht kennt, die aktuelle Homebrew-/MongoDB-Anleitung für die Tap-Einrichtung verwenden. Der Server wird nach der Konfiguration in Abschnitt 2 als Benutzerdienst gestartet.

### Linux

Die folgenden Befehle gelten für eine **neue Installation auf Ubuntu 24.04 LTS, x86-64**. Für andere unterstützte Distributionen oder Prozessoren in der [MongoDB-Installationsübersicht](https://www.mongodb.com/docs/manual/administration/install-community/) die passende Plattform und Dokumentationsversion **8.0** wählen; die Ubuntu-Paketquelle nicht unverändert auf ein anderes System übertragen.

Gemäss der [Ubuntu-Anleitung](https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-ubuntu/) zuerst Paketwerkzeuge, Signaturschlüssel und die Paketquelle der Reihe 8.0 einrichten:

```bash
sudo apt-get update
sudo apt-get install gnupg curl
curl -fsSL https://pgp.mongodb.com/server-8.0.asc -o /tmp/rothstein-storage-mongodb-8.0.asc
sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg /tmp/rothstein-storage-mongodb-8.0.asc
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
sudo apt-get update
sudo apt-get install mongodb-org
mongod --version
mongosh --version
```

`mongodb-org` installiert den Server und die benötigten Komponenten einschliesslich `mongosh`. Bei einer bereits vorhandenen passenden Paketquelle Schlüssel und Quelldatei nicht erneut anlegen. Bei Konflikten mit anderen MongoDB-Paketen die offizielle Anleitung auf die vorhandene Installation anwenden; keine bestehenden Datenbestände löschen.

## 2. Lokalen Zugriff und Anmeldung konfigurieren

Den neu installierten Dienst zunächst gemäss der [Diensttabelle](#dienst-starten-und-stoppen) stoppen, falls er läuft. Die tatsächlich verwendete Konfigurationsdatei öffnen; zum Bearbeiten einer systemweiten Datei können Administratorrechte nötig sein:

| Installation | Typische Konfigurationsdatei |
| --- | --- |
| Windows-MSI | `C:\Program Files\MongoDB\Server\8.0\bin\mongod.cfg` |
| macOS, Apple Silicon/Homebrew | `/opt/homebrew/etc/mongod.conf` |
| macOS, Intel/Homebrew | `/usr/local/etc/mongod.conf` |
| Ubuntu-Pakete | `/etc/mongod.conf` |

Bei abweichenden Installationspfaden die Dienstkonfiguration beziehungsweise unter macOS `brew --prefix` prüfen. Eine Kopie der Konfiguration als Rückfallmöglichkeit aufbewahren. Die vorhandenen Abschnitte **net** und **security** wie folgt setzen oder ergänzen:

```yaml
net:
  bindIp: 127.0.0.1
  port: 27017
security:
  authorization: enabled
```

Dies ist ein **Ausschnitt**, keine vollständige Ersatzdatei. Vorhandene `storage`-, `systemLog`- und sonstige Einstellungen erhalten; die obersten Schlüssel nicht doppelt anlegen. `storage.dbPath` bezeichnet den Datenordner. YAML mit Leerzeichen statt Tabulatoren einrücken.

Den Dienst danach wieder starten. MongoDB ist nun auf den eigenen Rechner beschränkt und verlangt eine Anmeldung. Für eine neue Instanz erlaubt die **Localhost Exception** noch die Anlage des ersten Benutzeradministrators. [Zugriffsschutz](https://www.mongodb.com/docs/manual/tutorial/configure-scram-client-authentication/), [Localhost Exception](https://www.mongodb.com/docs/v8.0/core/localhost-exception/)

## 3. Benutzer einmalig einrichten

### Ersten Benutzeradministrator anlegen

Nur bei einer frischen Instanz ohne Benutzer: Im Terminal lokal verbinden:

```bash
mongosh --host 127.0.0.1 --port 27017
```

Die folgenden Zeilen gehören in **mongosh**, nicht in den Anaconda Prompt oder die PowerShell. Für `storage_admin` ein eigenes Passwort wählen und aufbewahren:

```javascript
use admin
db.createUser({
  user: "storage_admin",
  pwd: passwordPrompt(),
  roles: [{ role: "userAdminAnyDatabase", db: "admin" }]
})
exit
```

`passwordPrompt()` fragt das Passwort verdeckt ab. Mit dem ersten Benutzer endet die Localhost Exception. Wenn stattdessen `Unauthorized` oder ein bereits vorhandener Benutzer gemeldet wird, mit dem bestehenden Administrator fortfahren; die Authentifizierung nicht abschalten. [MongoDB: erster Benutzer](https://www.mongodb.com/docs/v8.0/core/localhost-exception/)

### Kursbenutzer mit Zugriff auf die drei Kursdatenbanken anlegen

Im normalen Terminal als Benutzeradministrator anmelden; das Passwort wird abgefragt:

```bash
mongosh --host 127.0.0.1 --port 27017 --username storage_admin --authenticationDatabase admin --password
```

Dann in **mongosh** den Kursbenutzer anlegen:

```javascript
use admin
db.createUser({
  user: "workshop",
  pwd: passwordPrompt(),
  roles: [
    { role: "readWrite", db: "storage_uap" },
    { role: "readWrite", db: "storage_microblogging" },
    { role: "readWrite", db: "storage_setup" }
  ]
})
exit
```

Für `workshop` entweder den Standard der lokalen Lernumgebung **Storage-Mongo-2026** oder ein eigenes Passwort setzen. Den tatsächlichen Wert anschliessend als `MONGO_PASSWORD` hinterlegen. Die drei Datenbanken entstehen beim ersten Schreiben; eine leere Datenbank muss nicht vorab angelegt werden. Die Rollen erlauben die Arbeit in den beiden Fällen und in der Setup-Datenbank. [MongoDB: Benutzer und Rollen](https://www.mongodb.com/docs/manual/tutorial/configure-scram-client-authentication/)

Der Administrator wird nur für die Einrichtung verwendet. Im Notebook arbeitet `workshop`; er wird in der Anmeldedatenbank `admin` verwaltet. Die Docker-Referenz verwendet dagegen ihren initialen Root-Benutzer `workshop`. Alle Kursabfragen müssen auch mit den hier vergebenen, eingeschränkten Rechten auskommen.

## 4. Anmeldung und Python-Verbindung prüfen

Im Terminal:

```bash
mongosh --host 127.0.0.1 --port 27017 --username workshop --authenticationDatabase admin --password
```

In **mongosh** die tatsächlich authentifizierte Identität prüfen:

```javascript
db.runCommand({ connectionStatus: 1 }).authInfo.authenticatedUsers
exit
```

Die Ausgabe muss `workshop` in `admin` enthalten. Ein `ping` allein würde nicht belegen, dass ein Benutzer korrekt angemeldet ist. [MongoDB: connectionStatus](https://www.mongodb.com/docs/manual/reference/command/connectionStatus/)

Die [Verbindungseinstellungen für Weg B](OHNE_DOCKER.md#4-zugangsdaten-für-die-notebooks-hinterlegen) gelten auch hier. Im Repo-Hauptordner und aktivierten Kurs-Environment kannst Du die Anmeldung über den Python-Treiber prüfen:

```bash
python -c "from scripts.storage_runtime import mongo_client; c=mongo_client(); print(c.admin.command('connectionStatus')['authInfo']['authenticatedUsers']); c.close()"
```

Sobald auch Neo4j läuft, `python scripts/verify_setup.py` ausführen. **SETUP OK** bestätigt dann das tatsächliche Schreiben und Lesen in allen vier Speichern.

## Dienst starten und stoppen

Diese Befehle gelten für die oben beschriebenen Installationen. Auf Windows die Dienstaktionen in **PowerShell als Administrator** ausführen; der übrige Kurscode läuft im normalen Anaconda Prompt. Bei eigenem Dienstnamen diesen entsprechend ersetzen.

| System | Starten | Stoppen | Status |
| --- | --- | --- | --- |
| Windows | `Start-Service MongoDB` | `Stop-Service MongoDB` | `Get-Service MongoDB` |
| macOS/Homebrew | `brew services start mongodb-community@8.0` | `brew services stop mongodb-community@8.0` | `brew services list` |
| Linux/systemd | `sudo systemctl start mongod` | `sudo systemctl stop mongod` | `sudo systemctl status mongod --no-pager` |

Unter Windows ist alternativ die Anwendung **Dienste / Services** verwendbar. Nach einer Konfigurationsänderung stoppen und erneut starten. Meldet systemd nach der erstmaligen Paketinstallation einen unbekannten Dienst, `sudo systemctl daemon-reload` ausführen und erneut prüfen. [Windows-Dienst](https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-windows/), [macOS-Dienst](https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-os-x/), [Ubuntu-Dienst](https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-ubuntu/)

Stoppen erhält den unter `storage.dbPath` konfigurierten Datenbestand. Die Benutzeranlage wird beim nächsten Start nicht wiederholt. Die gemeinsame [Persistenzprüfung](OHNE_DOCKER.md#6-stoppen-fortsetzen-und-persistenz) prüft die Daten nach einem echten Dienstneustart.

## Häufige Stolperstellen

| Beobachtung | Nächster Schritt |
| --- | --- |
| `mongosh` nicht gefunden | Shell installieren beziehungsweise den Shell-Pfad einrichten und ein neues Terminal öffnen. |
| Server startet nach Konfigurationsänderung nicht | Log unter `systemLog.path` prüfen; YAML-Einrückung, doppelte Schlüssel und Erreichbarkeit des Datenverzeichnisses kontrollieren. |
| `ServerSelectionTimeoutError` | Dienststatus, `bindIp`, Port und Verbindungsziel prüfen. Unter Windows kann ein TCP-Test aus der allgemeinen Fehlerdiagnose helfen. |
| Port bereits belegt | Einen noch laufenden MongoDB-Kurscontainer oder die konkurrierende Instanz stoppen; bei bewusst geändertem Port auch `MONGO_PORT` anpassen. |
| `AuthenticationFailed` / `OperationFailure` | Tatsächliches Passwort, Benutzer und Anmeldedatenbank `admin` prüfen. Bei fehlenden Berechtigungen die drei `readWrite`-Rollen prüfen. |
| Erster Benutzer lässt sich nicht ohne Anmeldung anlegen | Die Ausnahme gilt nur für eine neue Instanz. Den vorhandenen Benutzeradministrator verwenden. |
| Compass offen, Python-Verbindung schlägt fehl | Den Serverdienst prüfen; Compass startet ihn nicht automatisch. |

Bei einem bestehenden passenden Benutzer dessen Rollen kontrollieren, statt die Anlage blind zu wiederholen. Die Zugangsdaten nicht durch Löschen des Datenverzeichnisses zurücksetzen.
