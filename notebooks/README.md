[Workshop-Übersicht](../README.md) · [Technische Vorbereitung](../README_technical_preparation.md) · [Microblogging-Beispiele](../demos/microblogging/README.md) · [Aufgaben](../tasks/README.md)

# Gemeinsamer Einstieg

[00_setup_check.ipynb](00_setup_check.ipynb) prüft Python, Paketversionen, Eingaben und alle vier Speicher. Verwende den Kernel **Python (rothstein-storage-workshop-2026)** und führe alle Zellen aus.

Die Standardeinstellung prüft MongoDB und Neo4j tatsächlich. Für eine bewusst eingeschränkte Diagnose lässt sich `OFFLINE_ONLY = True` setzen; das Notebook weist die ausgelassenen Dienste dann ausdrücklich aus.

Das gleiche Notebook gilt für Docker, [lokale Dienste ohne Docker](../docs/setup/OHNE_DOCKER.md) und Codespaces. Ohne Docker bleibt `OFFLINE_ONLY = False`, sobald MongoDB und Neo4j Desktop laufen. Nach Änderungen an den Verbindungseinstellungen den Kernel neu starten.
