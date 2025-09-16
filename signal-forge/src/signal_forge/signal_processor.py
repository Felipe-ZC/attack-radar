from logging import Logger

from radar_core import SignalStream

from .core.models import AbuseIPDBReport, HostMetadata
from .ipdb import AbuseIPDB

DEFAULT_GROUP_NAME = "signal-forge"
DEFAULT_CONSUMER_NAME = "signal-processor"


class SignalProcessor:
    def __init__(
        self,
        abuse_ipdb: AbuseIPDB,
        logger: Logger,
        signal_stream: SignalStream,
    ):
        self.abuse_ipdb = abuse_ipdb
        self.signal_stream = signal_stream
        self.logger = logger

    async def process_signals(self):
        # Try to setup consumer group...
        await self.signal_stream.create_group(DEFAULT_GROUP_NAME)
        # Start processing messages
        while True:
            try:
                messages = await self.signal_stream.read_group_messages(
                    DEFAULT_CONSUMER_NAME, DEFAULT_GROUP_NAME
                )
                for _, stream_msgs in messages:
                    for _, message_data in stream_msgs:
                        print("message_data is: ", message_data)
                        response = await self.abuse_ipdb.check(
                            message_data["ip"]
                        )
                        host_metadata, reports_list = self.format_data(
                            response
                        )
                        print(host_metadata, reports_list)

                if not messages:
                    self.logger.warning("No messages...")
                    continue

                self.logger.info(messages)
            except Exception as e:
                self.logger.error(e)
                raise

    def format_data(
        self, response: dict
    ) -> tuple[HostMetadata, list[AbuseIPDBReport]]:
        """
        TODO: Create a dataclass for the optimized data..
        We need to grab the following fields from response
        and perform a transformation on the reports field

        1) ipAddress
        2) countryCode
        3) countryName
        4) usageType
        5) domain
        6) isp
        7) report timestamp
        8) report comments
        9) report category

        * We'll need to use some external data source to get the physical address using the IP.
        * For now let's just use these fields and add more later.

        We need to group the reports in the reports list by date reported and category.
        So the result object looks like this:

        {
            ipAddress,
            countryCode,
            ...
            reports: {
                "2025-09-11": {
                    14: [{ timestamp: "...", comment: "..." }]
                }
            }
        }
        """
        data = response["data"]
        host_metadata = HostMetadata(
            ip_address=data["ipAddress"],
            country_code=data["countryCode"],
            country_name=data["countryName"],
            usage_type=data["usageType"],
            domain=data["domain"],
            isp=data["isp"],
        )
        abuse_reports = [
            AbuseIPDBReport(
                ip_address=data["ipAddress"],
                report_timestamp=report["reportedAt"],
                report_comment=report["comment"],
                report_categories=report["categories"],
            )
            for report in data["reports"]
        ]
        return host_metadata, abuse_reports
