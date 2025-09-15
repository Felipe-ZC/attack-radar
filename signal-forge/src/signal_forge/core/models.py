from dataclasses import dataclass
from datetime import datetime


@dataclass
class HostMetadata:
    ip_address: str
    # latitude: float
    # longitude: float
    country_code: str
    country_name: str
    usage_type: str
    domain: str
    isp: str


@dataclass
class AbuseIPDBReport:
    report_timestamp: datetime
    report_comment: str
    report_categories: list[int]
