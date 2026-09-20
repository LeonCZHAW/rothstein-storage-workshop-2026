-- Basis bereitgestellt; entry_assets ergänzt die Gruppe im Aufgaben-Notebook.
-- release_date liegt normalisiert in releases. Ungeklärte Pairings bleiben
-- im Qualitätsbericht; hier nur tatsächlich aufgelöste Katalogbeziehungen.
CREATE TABLE IF NOT EXISTS agencies (
    agency_id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL UNIQUE
) STRICT;
CREATE TABLE IF NOT EXISTS releases (
    release_id TEXT PRIMARY KEY NOT NULL,
    release_date TEXT NOT NULL UNIQUE
) STRICT;
CREATE TABLE IF NOT EXISTS catalog_entries (
    entry_id TEXT PRIMARY KEY NOT NULL,
    source_key TEXT NOT NULL,
    source_row INTEGER NOT NULL UNIQUE CHECK (source_row > 0),
    title TEXT NOT NULL,
    agency_id TEXT NOT NULL REFERENCES agencies(agency_id),
    release_id TEXT NOT NULL REFERENCES releases(release_id),
    media_type TEXT NOT NULL CHECK (media_type IN ('PDF','VID','IMG','AUD')),
    description TEXT,
    location_raw TEXT,
    redaction_reported INTEGER NOT NULL CHECK (redaction_reported IN (0,1)),
    description_category TEXT NOT NULL,
    incident_date_raw TEXT,
    incident_date_precision TEXT NOT NULL,
    incident_year INTEGER,
    incident_month INTEGER CHECK (incident_month BETWEEN 1 AND 12),
    incident_day TEXT,
    annual_eligible INTEGER NOT NULL CHECK (annual_eligible IN (0,1)),
    date_exclusion_reason TEXT,
    CHECK (annual_eligible = 0 OR incident_year IS NOT NULL)
) STRICT;
CREATE TABLE IF NOT EXISTS assets (
    asset_id TEXT PRIMARY KEY NOT NULL,
    locator_type TEXT NOT NULL,
    locator TEXT NOT NULL,
    format_hint TEXT,
    UNIQUE (locator_type, locator)
) STRICT;
CREATE TABLE IF NOT EXISTS portal_pairings (
    pairing_id TEXT PRIMARY KEY NOT NULL,
    source_entry_id TEXT NOT NULL REFERENCES catalog_entries(entry_id),
    target_entry_id TEXT NOT NULL REFERENCES catalog_entries(entry_id),
    source_field TEXT NOT NULL,
    raw_reference TEXT NOT NULL,
    resolution_rule TEXT NOT NULL
) STRICT;
