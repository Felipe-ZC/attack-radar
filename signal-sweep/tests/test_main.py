from typing import List

from unittest.mock import AsyncMock, patch

from signal_sweep.main import main
from signal_sweep.container import ApplicationContainer
from signal_sweep.core.models import StreamData, Source


@patch("signal_sweep.main.ingest_stream_data")
@patch("signal_sweep.main.handle_data_source")
async def test_main(
    mock_handle_data_source: AsyncMock,
    mock_ingest_stream_data: AsyncMock,
    mock_container: ApplicationContainer,
    sample_sources: List[Source],
):
    await main()

    expected_stream_data = [
        StreamData(ip="someIP", source_url=source.url)
        for source in sample_sources
    ]

    for source in sample_sources:
        mock_handle_data_source.assert_any_call(source)
    # mock_ingest_stream_data.assert_called()
