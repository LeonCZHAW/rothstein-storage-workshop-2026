[Workshop-Übersicht](../../README.md) · [Microblogging-Beispiele](../../demos/microblogging/README.md) · [Microblogging-Demo](../../demos/microblogging/03_neo4j.ipynb) · [UAP-Aufgabe](../../tasks/03_neo4j/README.md)

# Neo4j: Identität und Import

## Gemeinsamer Rahmen

Alle Kursknoten tragen `StorageNode` sowie ein fachliches Label: `StorageUser`, `StoragePost`, `StorageCatalogEntry`, `StorageAgency`, `StorageAsset` oder `StorageRelease`. Der Präfix verhindert Kollisionen mit allgemeinen `User`-/`Post`-Labels aus früheren Beispielen.

```cypher
CREATE CONSTRAINT storage_node_scope_id IF NOT EXISTS
FOR (n:StorageNode) REQUIRE (n.scope, n.node_id) IS UNIQUE;
```

Die Kombination aus `scope` und `node_id` ist eindeutig. Beide Felder werden vom Import gesetzt; der Uniqueness-Constraint allein erzwingt ihr Vorhandensein nicht. Auf zusätzliche Enterprise-Constraints wird verzichtet. Das Modell verwendet die gemeinsame Datenbank `neo4j` und benötigt weder APOC noch weitere Datenbanken.

## Microblogging

Nutzer und Posts sind Knoten. `FOLLOWS`, `AUTHORED`, `LIKES` und `COMMENTED` sind gerichtete Beziehungen. Kommentare tragen eine eigene Kommentar-ID und ihren Text. Wiederholte Kommentare derselben Person zum selben Post bleiben getrennt. Die Event-IDs werden aus den mitgelieferten relationalen CSV-Dateien gelesen; die ursprünglichen Graph-CSV-Dateien bleiben unverändert als Referenz erhalten.

Die vorbereiteten Daten enthalten dieselbe Topologie wie die Original-Graphdateien, ergänzt um stabile Kommentar-/Like-IDs, Posttexte und weitere Eigenschaften. Datum und Zeitpunkt werden als Neo4j-Temporalwerte übertragen; ursprünglich zeitzonenlose Demo-Zeitpunkte erhalten ausdrücklich UTC als Lehrkonvention.

## UAP

`CATALOG_AGENCY`, `LINKS_ASSET`, `IN_RELEASE` und `PORTAL_PAIRS_WITH` übernehmen genau die vorliegenden Graph-Eingaben. Es werden keine Ereignisknoten, Ähnlichkeitskanten oder unbelegten Verknüpfungen ergänzt. Fehlende Quellproperties werden in Neo4j nicht als gespeicherte `null`-Properties abgelegt; die unveränderten JSONL-Dateien bleiben die Quelle.

## Transaktionen und Trennung

- `microblogging_demo`, `uap_task` und `uap_solution` sind separate Werte von `scope`.
- Ein vollständiger Import ersetzt ausschliesslich seinen Bereich in einer Datentransaktion. Die Schemaanlage wird vorher separat bestätigt.
- Knoten-IDs, Kanten-IDs und Endpunkte werden vor dem ersten Schreiben geprüft; die Bestandszahlen werden vor dem Commit verglichen.
- Bereichsübergreifende Fremdverbindungen führen zum Abbruch des Resets. Es gibt kein globales `MATCH (n) DETACH DELETE n`.
- Der Kursimport ist für eine interaktive Bearbeitung pro Bereich vorgesehen. Gleichzeitige Importe in denselben Bereich sind kein zugesicherter Anwendungsfall.
- Eine Teilnehmerin kann in selbst formuliertem Cypher beliebige Abfragen ausführen. Die Kursbereiche organisieren die Daten; sie ersetzen keine Datenbankberechtigungen.

Referenzen: [Neo4j-5-Constraints](https://neo4j.com/docs/cypher-manual/5/constraints/create-constraints/), [MERGE](https://neo4j.com/docs/cypher-manual/5/clauses/merge/), [Python-Transaktionen](https://neo4j.com/docs/python-manual/current/transactions/).
