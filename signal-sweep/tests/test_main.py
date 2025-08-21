from unittest.mock import AsyncMock, patch

from signal_sweep.main import main
from signal_sweep.container import ApplicationContainer


@patch('signal_sweep.main.ingest_stream_data')
@patch('signal_sweep.main.handle_data_source')
async def test_main(mock_ingest_stream_data: AsyncMock, mock_handle_data_source: AsyncMock, mock_container: ApplicationContainer):
    await main()
