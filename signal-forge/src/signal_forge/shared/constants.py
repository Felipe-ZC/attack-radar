HOST_META_TABLE_NAME = "host_metadata"
REPORTS_TABLE_NAME = "abuse_ipdb_reports"

CREATE_HOST_META_TABLE_QUERY = f"""
    CREATE TABLE IF NOT EXISTS {HOST_META_TABLE_NAME} (
        ip_address VARCHAR UNIQUE NOT NULL,
        country_code VARCHAR,
        country_name VARCHAR,
        usage_type VARCHAR,
        domain VARCHAR,
        isp VARCHAR
    );
"""
CREATE_ABUSE_REPORTS_TABLE_QUERY = f"""
    CREATE TABLE IF NOT EXISTS {REPORTS_TABLE_NAME} (
        ip_address VARCHAR NOT NULL,
        report_timestamp TIMESTAMP NOT NULL,
        report_comment TEXT,
        report_categories INTEGER[],
        -- Not enforced by default, this constraint serves as documentation
        FOREIGN KEY (ip_address) REFERENCES host_metadata(ip_address)
    );
"""

CREATE_ABUSE_REPORTS_TABLE_IP_INDEX = f"""CREATE INDEX IF NOT EXISTS idx_abuse_reports_ip ON {REPORTS_TABLE_NAME}(ip_address);"""
