from typing import List
from unittest.mock import AsyncMock, MagicMock, patch
from itertools import product

from src.signal_sweep.core.handlers.text_handler import (
    TextHandler,
    _parse_text,
)
from src.signal_sweep.core.models import Source
from src.signal_sweep.core.models import StreamData


async def test_text_handler(
    mock_http_response: MagicMock,
    mock_http_client: AsyncMock,
    mock_process_executor: MagicMock,
    sample_sources: List[Source],
):
    txt_handler = TextHandler(mock_http_client, mock_process_executor)

    expected_ips = ["192.168.1.1", "10.0.0.1"]
    expected_results = [
        StreamData(ip, source.url)
        for ip, source in product(expected_ips, sample_sources)
    ]

    with patch("asyncio.get_event_loop") as mock_get_event_loop:
        mock_loop = AsyncMock()
        mock_get_event_loop.return_value = mock_loop
        mock_loop.run_in_executor.return_value = expected_ips

        for source in sample_sources:
            actual_results = await txt_handler.handle(source)
            mock_http_client.get.assert_called_with(source.url)
            mock_loop.run_in_executor.assert_called_with(
                mock_process_executor, _parse_text, mock_http_response.text
            )
            assert all(
                [
                    actual_result in expected_results
                    for actual_result in actual_results
                ]
            )
