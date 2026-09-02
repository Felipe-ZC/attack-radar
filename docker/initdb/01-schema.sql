CREATE TABLE IF NOT EXISTS public.host_metadata
(
    ip_address inet NOT NULL,
    country_code text COLLATE pg_catalog."default",
    country_name text COLLATE pg_catalog."default",
    usage_type text COLLATE pg_catalog."default",
    domain text COLLATE pg_catalog."default",
    isp text COLLATE pg_catalog."default",
    lat double precision,
    lon double precision,
    CONSTRAINT host_metadata_ip_address_key UNIQUE (ip_address)
);

CREATE TABLE IF NOT EXISTS abuse_ipdb_reports (
    ip_address INET NOT NULL REFERENCES host_metadata(ip_address),
    report_timestamp TIMESTAMPTZ NOT NULL,
    report_comment TEXT,
    report_categories INTEGER[],
    UNIQUE (ip_address, report_timestamp)
);

CREATE INDEX IF NOT EXISTS idx_abuse_reports_ip ON abuse_ipdb_reports(ip_address);
