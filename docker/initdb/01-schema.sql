CREATE TABLE IF NOT EXISTS host_metadata (
    ip_address INET UNIQUE NOT NULL,
    country_code TEXT,
    country_name TEXT,
    usage_type TEXT,
    domain TEXT,
    isp TEXT
);

CREATE TABLE IF NOT EXISTS abuse_ipdb_reports (
    ip_address INET NOT NULL REFERENCES host_metadata(ip_address),
    report_timestamp TIMESTAMPTZ NOT NULL,
    report_comment TEXT,
    report_categories INTEGER[],
    UNIQUE (ip_address, report_timestamp)
);

CREATE INDEX IF NOT EXISTS idx_abuse_reports_ip ON abuse_ipdb_reports(ip_address);
