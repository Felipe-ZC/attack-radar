from datetime import datetime

from pydantic import BaseModel, Field, IPvAnyAddress


class HostMetadata(BaseModel):
    ip_address: IPvAnyAddress
    country_code: str | None = None
    country_name: str | None = None
    usage_type: str | None = None
    domain: str | None = None
    isp: str | None = None
    lat: float | None = Field(default=None, ge=-90, le=90)
    lon: float | None = Field(default=None, ge=-180, le=180)


class AbuseReport(BaseModel):
    ip_address: IPvAnyAddress
    report_timestamp: datetime
    report_comment: str | None = None
    report_categories: list[int] = Field(default_factory=list)
