-- Adds a surrogate BIGINT identity primary key to host_metadata.
-- This is purely additive with respect to data, but the *primary key itself*
-- may need to move: some environments already have a PRIMARY KEY on
-- ip_address (under whatever name), rather than the plain UNIQUE constraint
-- from the original schema. Either way, ip_address must keep a UNIQUE
-- constraint afterwards, since abuse_ipdb_reports.ip_address references it.

ALTER TABLE host_metadata
    ADD COLUMN IF NOT EXISTS id bigint GENERATED ALWAYS AS IDENTITY;

DO $$
DECLARE
    pk_name text;
    pk_def  text;
BEGIN
    SELECT conname, pg_get_constraintdef(oid) INTO pk_name, pk_def
    FROM pg_constraint
    WHERE conrelid = 'host_metadata'::regclass AND contype = 'p';

    IF pk_def IS DISTINCT FROM 'PRIMARY KEY (id)' THEN
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conrelid = 'host_metadata'::regclass
              AND contype = 'u'
              AND pg_get_constraintdef(oid) = 'UNIQUE (ip_address)'
        ) THEN
            ALTER TABLE host_metadata ADD CONSTRAINT host_metadata_ip_address_key UNIQUE (ip_address);
        END IF;

        IF pk_name IS NOT NULL THEN
            -- Dropping the old PK also drops abuse_ipdb_reports' FK, since it
            -- depends on the index backing the PK; recreate the FK below
            -- against the UNIQUE constraint added above.
            EXECUTE format('ALTER TABLE host_metadata DROP CONSTRAINT %I CASCADE', pk_name);
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conrelid = 'abuse_ipdb_reports'::regclass
              AND contype = 'f'
              AND confrelid = 'host_metadata'::regclass
        ) THEN
            ALTER TABLE abuse_ipdb_reports
                ADD CONSTRAINT abuse_ipdb_reports_ip_address_fkey
                FOREIGN KEY (ip_address) REFERENCES host_metadata(ip_address);
        END IF;

        ALTER TABLE host_metadata ADD CONSTRAINT host_metadata_pkey PRIMARY KEY (id);
    END IF;
END $$;
