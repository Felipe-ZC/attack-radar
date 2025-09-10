from logging import Logger

from radar_core import SignalStream


DEFAULT_GROUP_NAME = "signal-forge"
DEFAULT_CONSUMER_NAME = "signal-processor"


class SignalProcessor:
    def __init__(self, logger: Logger, signal_stream: SignalStream):
        self.signal_stream = signal_stream
        self.logger = logger

    async def process_signals(self):
        # Try to setup consumer group...
        await self.signal_stream.create_group(DEFAULT_GROUP_NAME)
        # Start processing messages
        while True:
            try:
                messages = await self.signal_stream.read_group_messages(
                    DEFAULT_CONSUMER_NAME,
                    DEFAULT_GROUP_NAME
                )

                if not messages:
                    self.logger.warning("No messages...")
                    continue

                self.logger.info(messages)
            except Exception as e:
                self.logger.error(e)
                raise
