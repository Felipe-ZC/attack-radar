-- Adds created_at/modified_at audit columns to both tables, plus a shared
-- trigger function that keeps modified_at current on every UPDATE (Postgres
-- has no built-in "ON UPDATE" column clause the way MySQL does).

ALTER TABLE host_metadata
    ADD COLUMN IF NOT EXISTS created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    ADD COLUMN IF NOT EXISTS modified_at TIMESTAMPTZ NOT NULL DEFAULT now();

ALTER TABLE abuse_ipdb_reports
    ADD COLUMN IF NOT EXISTS created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    ADD COLUMN IF NOT EXISTS modified_at TIMESTAMPTZ NOT NULL DEFAULT now();

CREATE OR REPLACE FUNCTION set_modified_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_host_metadata_set_modified_at ON host_metadata;
CREATE TRIGGER trg_host_metadata_set_modified_at
    BEFORE UPDATE ON host_metadata
    FOR EACH ROW
    EXECUTE FUNCTION set_modified_at();

DROP TRIGGER IF EXISTS trg_abuse_ipdb_reports_set_modified_at ON abuse_ipdb_reports;
CREATE TRIGGER trg_abuse_ipdb_reports_set_modified_at
    BEFORE UPDATE ON abuse_ipdb_reports
    FOR EACH ROW
    EXECUTE FUNCTION set_modified_at();
