from dataclasses import asdict
from logging import Logger

import pandas as pd
from radar_core import AsyncDuckDb, SignalStream

from ..shared.constants import (
    CREATE_ABUSE_REPORTS_TABLE_IP_INDEX,
    CREATE_ABUSE_REPORTS_TABLE_QUERY,
    CREATE_HOST_META_TABLE_QUERY,
    HOST_META_TABLE_NAME,
    REPORTS_TABLE_NAME,
)
from .ipdb import AbuseIPDB
from .models import AbuseIPDBReport, HostMetadata

DEFAULT_GROUP_NAME = "signal-forge"
DEFAULT_CONSUMER_NAME = "signal-processor"


class SignalProcessor:
    def __init__(
        self,
        abuse_ipdb: AbuseIPDB,
        logger: Logger,
        signal_stream: SignalStream,
        duck_db: AsyncDuckDb,
    ):
        self.abuse_ipdb = abuse_ipdb
        self.duck_db = duck_db
        self.signal_stream = signal_stream
        self.logger = logger

    async def process_signals(self):
        # Try to setup consumer group...
        await self.signal_stream.create_group(DEFAULT_GROUP_NAME)
        # Create duckdb tables if they do not exist...
        await self.create_tables()
        # Start processing messages
        # while True:
        try:
            messages = await self.signal_stream.read_group_messages(
                DEFAULT_CONSUMER_NAME, DEFAULT_GROUP_NAME
            )

            if not messages:
                self.logger.warning("No messages...")
                return

            host_list, reports_list = [], []
            for _, stream_msgs in messages:
                for _, message_data in stream_msgs:
                    print("message_data is: ", message_data)
                    response = await self.abuse_ipdb.check(message_data["ip"])
                    host_metadata, host_abuse_reports = self.format_data(
                        response
                    )
                    host_list.append(host_metadata)
                    reports_list.extend(host_abuse_reports)
                    # Write batch...
                    self.logger.info("Writing data lists to duckdb...")
                    await self.write_data_lists(host_list, reports_list)

        except Exception as e:
            self.logger.error(e)
            raise

    async def create_tables(self):
        create_host_meta_result = await self.duck_db.execute_query(
            CREATE_HOST_META_TABLE_QUERY
        )
        create_abuse_reports_result = await self.duck_db.execute_query(
            CREATE_ABUSE_REPORTS_TABLE_QUERY
        )
        create_abuse_reports_ip_index_result = (
            await self.duck_db.execute_query(
                CREATE_ABUSE_REPORTS_TABLE_IP_INDEX
            )
        )
        return (
            create_host_meta_result,
            create_abuse_reports_result,
            create_abuse_reports_ip_index_result,
        )

    async def write_data_lists(
        self,
        host_meta_list: list[HostMetadata],
        reports_list: list[AbuseIPDBReport],
    ):
        host_meta_df = pd.DataFrame(asdict(host) for host in host_meta_list)
        reports_df = pd.DataFrame(asdict(report) for report in reports_list)
        await self.duck_db.bulk_insert_from_dataframe(
            table_name=HOST_META_TABLE_NAME,
            df_name="host_meta_df",
            df=host_meta_df,
            has_primary_key=True,
        )
        await self.duck_db.bulk_insert_from_dataframe(
            table_name=REPORTS_TABLE_NAME,
            df_name="reports_df",
            df=reports_df,
        )

    def format_data(
        self, response: dict
    ) -> tuple[HostMetadata, list[AbuseIPDBReport]]:
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
