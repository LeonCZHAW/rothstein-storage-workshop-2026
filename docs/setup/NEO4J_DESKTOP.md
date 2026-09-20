[Workshop-Übersicht](../../README.md) · [Technische Vorbereitung](../../README_technical_preparation.md) · [Microblogging-Beispiele](../../demos/microblogging/README.md) · [Ohne Docker](OHNE_DOCKER.md) · [MongoDB lokal](MONGODB_LOKAL.md)

# Neo4j lokal mit Neo4j Desktop

**Diese Anleitung gilt nur für Weg B: lokal ohne Docker sowie den ausdrücklich gewählten Mischbetrieb.** Bei Weg A oder C verwendest Du den bereits gestarteten Neo4j-Container; [Start und Graphansicht für alle Wege](NEO4J_START.md).

Diese Anleitung gilt für das Graph-Modell im Microblogging-Beispiel und im UAP-Workshop. Verwende eine eigene lokale Kursinstanz. Die Anleitung berücksichtigt **Neo4j Desktop 1.x und 2.x**, mit einer Datenbankversion aus **Neo4j 5.26.x**. Die Instanz muss vor der ersten Python-Codezelle laufen. Mit den Kurswerten ist keine `.env` erforderlich.

## Installieren

Die [offizielle Installationsanleitung](https://neo4j.com/docs/desktop/current/installation/) führt zum Download und beschreibt die Systemvoraussetzungen:

| System | Schritte |
| --- | --- |
| Windows | Windows-Installer herunterladen, ausführen und Neo4j Desktop öffnen. PowerShell 5.1 oder neuer muss vorhanden sein. |
| macOS | Passenden Download öffnen, Neo4j Desktop nach **Applications / Programme** ziehen und starten. |
| Linux | AppImage herunterladen, ausführbar machen, beispielsweise `chmod +x "Neo4j-Desktop.AppImage"` mit dem tatsächlichen Dateinamen, und öffnen. |

Desktop liefert die für die Datenbank benötigte Java-Laufzeit mit beziehungsweise lädt sie bei Bedarf nach. Für den Download der gewählten Datenbankversion ist Internetzugriff nötig. Eine separate Java-Installation ist für diesen Desktop-Weg nicht vorgesehen.

Desktop umfasst eine Developer-Lizenz mit Enterprise-Funktionen. Die Kursaufgaben verwenden trotzdem nur den für die Docker-Community-Variante vorgesehenen Funktionsumfang und die gemeinsame Datenbank `neo4j`. [Neo4j Desktop](https://neo4j.com/docs/desktop/current/)

## Kursinstanz vor dem Notebook erstellen

**Vor Create/Start:** Falls bisher ein Neo4j-Container lief, diesen zuerst im bisherigen Repo mit `docker compose stop neo4j` stoppen. Andere Neo4j-Container beziehungsweise lokale Instanzen in Docker Desktop oder Neo4j Desktop prüfen. Nur eine lokale Neo4j-Instanz darf die Standardports `7474` und `7687` belegen. Bei einem Rechner ohne Docker ist kein Docker-Befehl erforderlich.

Für diesen Weg laufen Notebook und Neo4j Desktop **lokal auf Deinem Rechner**. Docker ist dafür nicht erforderlich.

1. **Bestehende Kursinstanz weiterverwenden oder einmalig eine neue anlegen:** In Desktop **1.x** im Projekt **Add → Local DBMS** wählen. In Desktop **2.x** heisst dies **Instances → Create instance**. Ist Deine Kursinstanz bereits vorhanden, verwende sie weiter.
2. **Kurswerte verwenden:** Name **rothstein-storage-workshop-2026**, Passwort **`Storage-Neo4j-2026`**, Datenbankversion **5.26.x**, sofern angeboten. Der Datenbankbenutzer ist **neo4j**; falls ein Benutzerfeld angezeigt wird, diesen Namen eintragen. Die Standardports beibehalten.
3. **Create → Start:** Erstellung abschliessen, die Kursinstanz starten und warten, bis sie läuft. Desktop geöffnet lassen. **Erst jetzt die Python-Codezellen im Notebook ausführen.**

**Keine `.env` nötig:** Ohne eigene Konfiguration verwenden die Notebooks automatisch `127.0.0.1:7687`, Benutzer `neo4j`, das obige Kurspasswort und die Datenbank `neo4j`.

**Optional – eigene Zugangsdaten:** Nur bei abweichendem Passwort oder Port `.env.example` als `.env` kopieren und die abweichenden Werte eintragen; eine vorhandene `.env` direkt bearbeiten. Bereits gesetzte eigene Werte haben Vorrang vor den Kursstandards. Nach einer Änderung den Notebook-Kernel neu starten. [Details zur optionalen Konfiguration](OHNE_DOCKER.md#4-zugangsdaten-für-die-notebooks-hinterlegen)

**rothstein-storage-workshop-2026** ist der Anzeigename der Instanz; die Datenbank darin heisst **neo4j**. [Desktop 2.x: Instanzverwaltung](https://neo4j.com/docs/desktop/current/operations/instance-management/)

## Verbindung und Datenbank prüfen

In **Desktop 1.x** bei der gestarteten Kursinstanz **Open → Neo4j Browser** wählen, in **Desktop 2.x** **Connect → Query**. Falls eine Anmeldung erscheint: Benutzer `neo4j` und Dein Instanzpasswort verwenden. Die Datenbank **neo4j** auswählen und im Cypher-Eingabefeld ausführen:

```cypher
RETURN 1 AS verbindung_ok;
```

Die Ergebniszeile muss `1` zeigen. Danach die Version abfragen:

```cypher
CALL dbms.components() YIELD name, versions, edition
RETURN name, versions, edition;
```

Die Verbindungsadresse steht in den Details der Kursinstanz; in Desktop 2.x unter **[…] → Overview**. Für unsere lokale Python-Verbindung verwenden wir `bolt://127.0.0.1:7687`. Falls Desktop einen anderen Bolt-Port angibt, `NEO4J_PORT` in der Repo-Konfiguration anpassen.

Die lokale Instanz soll nur auf dem eigenen Rechner erreichbar sein. Die entsprechenden Neo4j-5-Einstellungen sind `server.default_listen_address=127.0.0.1` und bei explizit gesetzten Connector-Adressen beispielsweise `server.bolt.listen_address=127.0.0.1:7687` sowie `server.http.listen_address=127.0.0.1:7474`. Bei Bedarf die vorhandenen Werte in den Instanzeinstellungen bearbeiten (Desktop 1.x: **Manage → Settings**; Desktop 2.x: **[…] → Open → neo4j.conf**) und die Instanz neu starten; keine doppelten Einträge anlegen. [Neo4j-5-Konfiguration](https://neo4j.com/docs/operations-manual/5/configuration/configuration-settings/)

## Optionale Konfiguration: eigene Zugangsdaten

**Mit diesen Kurswerten brauchst Du keine `.env`:** Die Notebooks verwenden sie automatisch. Nur abweichende Einstellungen in `.env` nach [Weg B, Abschnitt 4](OHNE_DOCKER.md#4-zugangsdaten-für-die-notebooks-hinterlegen) hinterlegen:

```dotenv
NEO4J_HOST=127.0.0.1
NEO4J_PORT=7687
NEO4J_PASSWORD=Storage-Neo4j-2026
NEO4J_DATABASE=neo4j
```

Nur wenn Du ein eigenes Passwort gewählt hast, `NEO4J_PASSWORD` in der optionalen `.env` entsprechend setzen. Eine bereits vorhandene `.env` kann die Kurswerte überschreiben. Nach Änderungen den Notebook-Kernel neu starten. Der Python-Verbindungshelfer verwendet den Benutzer `neo4j`. Diese Einstellungen erstellen oder starten keine Instanz.

Für eine einzelne Neo4j-Verbindungsprüfung im aktivierten Kurs-Environment und Repo-Hauptordner:

```bash
python -c "from scripts.storage_runtime import neo4j_driver; d=neo4j_driver(); d.verify_connectivity(); d.close(); print('Neo4j-Verbindung OK')"
```

Dies prüft Erreichbarkeit und Anmeldung. Sobald auch MongoDB eingerichtet ist, bestätigt erst `python scripts/verify_setup.py` mit **SETUP OK** die vollständigen Schreib-/Lesetests in allen vier Speichern.

## Starten, stoppen und Daten behalten

Die Kursinstanz in Desktop mit dem Play-/Stop-Schalter starten beziehungsweise stoppen. Desktop muss während der Arbeit mit der lokalen Instanz geöffnet bleiben. Das Datenverzeichnis findest Du in den Instanzdetails; in Desktop 2.x über **[…] → Open → Instance folder**. Die [Instanzverwaltung](https://neo4j.com/docs/desktop/current/operations/instance-management/) erklärt diese Aktionen.

Beim Fortsetzen dieselbe Instanz starten. **Delete** löscht die Instanz mitsamt ihren Datenbanken. Der Persistenztest für den Kurs steht unter [Weg B, Abschnitt 6](OHNE_DOCKER.md#6-stoppen-fortsetzen-und-persistenz).

## Häufige Stolperstellen

| Beobachtung | Nächster Schritt |
| --- | --- |
| Desktop offen, Python meldet `ServiceUnavailable` | Prüfen, ob die konkrete Kursinstanz gestartet ist; Connection URI und Bolt-Port ansehen. |
| Port bereits belegt | Einen noch laufenden Neo4j-Docker-Container oder eine andere lokale Instanz stoppen. Für einen bewussten anderen Port auch `NEO4J_PORT` anpassen. |
| Anmeldung schlägt fehl | Benutzer `neo4j` und tatsächliches Desktop-Passwort verwenden. Eine Änderung in `.env` setzt kein Serverpasswort zurück. |
| Datenbank nicht gefunden | `NEO4J_DATABASE=neo4j` verwenden; den Instanznamen nicht als Datenbanknamen einsetzen. |
| Nach Passwortänderung weiterhin Fehler im Notebook | Kernel neu starten, dann die Setup-Zellen erneut ausführen. |
| Instanzstart schlägt fehl | Die Logs der Kursinstanz öffnen (Desktop 1.x: **Manage → Logs**; Desktop 2.x: **[…] → Open → neo4j.log**) und die Fehlermeldung prüfen. |
