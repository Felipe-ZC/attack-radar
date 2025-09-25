import os
from unittest.mock import Mock, patch

import pandas as pd
import pytest

# Assuming your module structure
from radar_core.duck_db import AsyncDuckDb


@pytest.fixture
def sample_dataframe():
    """Create a sample pandas DataFrame for testing."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
        }
    )


def test_init_sets_attributes_correctly(mock_async_thread_pool_executor):
    """Test that __init__ sets all attributes correctly."""
    db_path = "/path/to/test.db"
    async_db = AsyncDuckDb(db_path, mock_async_thread_pool_executor)

    assert async_db.db_path == os.path.normpath(db_path)
    assert async_db.async_exectuor is mock_async_thread_pool_executor
    assert async_db.conn is None


def test_init_normalizes_path(mock_async_thread_pool_executor):
    """Test that db_path is normalized during initialization."""
    db_path = "//path//to//test.db"
    async_db = AsyncDuckDb(db_path, mock_async_thread_pool_executor)

    expected_path = os.path.normpath(db_path)
    assert async_db.db_path == expected_path


@pytest.mark.asyncio
async def test_aenter_calls_connect_with_correct_path(
    mock_duckdb_connection, mock_async_thread_pool_executor
):
    """Test that __aenter__ calls duckdb.connect with the correct path."""
    async_db = AsyncDuckDb("test.db", mock_async_thread_pool_executor)

    with patch("duckdb.connect") as mock_connect:
        mock_async_thread_pool_executor.submit.return_value = (
            mock_duckdb_connection
        )
        result = await async_db.__aenter__()

        mock_async_thread_pool_executor.submit.assert_called_once_with(
            mock_connect, "test.db"
        )
        assert async_db.conn is mock_duckdb_connection
        assert result is async_db


@pytest.mark.asyncio
async def test_aexit_calls_close_when_connection_exists(
    mock_duckdb_connection, mock_async_thread_pool_executor
):
    """Test that __aexit__ calls connection.close when connection exists."""
    async_db = AsyncDuckDb("test.db", mock_async_thread_pool_executor)
    async_db.conn = mock_duckdb_connection

    await async_db.__aexit__(None, None, None)

    mock_async_thread_pool_executor.submit.assert_called_once_with(
        mock_duckdb_connection.close
    )


@pytest.mark.asyncio
async def test_aexit_does_not_call_close_when_no_connection(
    mock_async_thread_pool_executor,
):
    """Test that __aexit__ doesn't call close when no connection exists."""
    async_db = AsyncDuckDb("test.db", mock_async_thread_pool_executor)
    # Don't set conn attribute

    await async_db.__aexit__(None, None, None)

    mock_async_thread_pool_executor.submit.assert_not_called()


@pytest.mark.asyncio
async def test_register_dataframe_calls_with_correct_params(
    mock_duckdb_connection, mock_async_thread_pool_executor, sample_dataframe
):
    """Test that register_dataframe calls conn.register with correct parameters."""
    async_db = AsyncDuckDb("test.db", mock_async_thread_pool_executor)
    async_db.conn = mock_duckdb_connection

    await async_db.register_dataframe("test_df", sample_dataframe)

    mock_async_thread_pool_executor.submit.assert_called_once_with(
        mock_duckdb_connection.register, "test_df", sample_dataframe
    )


@pytest.mark.asyncio
async def test_execute_query_without_params_calls_correctly(
    mock_duckdb_connection, mock_async_thread_pool_executor
):
    """Test that execute_query calls conn.execute with query only when no params."""
    async_db = AsyncDuckDb("test.db", mock_async_thread_pool_executor)
    async_db.conn = mock_duckdb_connection
    query = "SELECT * FROM test_table"

    await async_db.execute_query(query)

    mock_async_thread_pool_executor.submit.assert_called_once_with(
        mock_duckdb_connection.execute, query
    )


@pytest.mark.asyncio
async def test_execute_query_with_params_calls_correctly(
    mock_duckdb_connection, mock_async_thread_pool_executor
):
    """Test that execute_query calls conn.execute with query and params."""
    async_db = AsyncDuckDb("test.db", mock_async_thread_pool_executor)
    async_db.conn = mock_duckdb_connection
    query = "SELECT * FROM test_table WHERE id = ?"
    params = [1, 2, 3]

    await async_db.execute_query(query, params)

    mock_async_thread_pool_executor.submit.assert_called_once_with(
        mock_duckdb_connection.execute, query, params
    )


@pytest.mark.asyncio
async def test_execute_query_with_empty_params_calls_without_params(
    mock_duckdb_connection, mock_async_thread_pool_executor
):
    """Test that execute_query calls conn.execute without params when params is empty."""
    async_db = AsyncDuckDb("test.db", mock_async_thread_pool_executor)
    async_db.conn = mock_duckdb_connection
    query = "SELECT * FROM test_table"

    await async_db.execute_query(query, [])

    mock_async_thread_pool_executor.submit.assert_called_once_with(
        mock_duckdb_connection.execute, query
    )


@pytest.mark.asyncio
async def test_bulk_insert_without_primary_key_generates_correct_query(
    mock_duckdb_connection, mock_async_thread_pool_executor, sample_dataframe
):
    """Test bulk_insert_from_dataframe generates correct INSERT query without primary key."""
    async_db = AsyncDuckDb("test.db", mock_async_thread_pool_executor)
    async_db.conn = mock_duckdb_connection

    await async_db.bulk_insert_from_dataframe(
        "test_table", "test_df", sample_dataframe, has_primary_key=False
    )

    # Should be called twice: once for register, once for execute
    assert mock_async_thread_pool_executor.submit.call_count == 2
    calls = mock_async_thread_pool_executor.submit.call_args_list

    # First call: register dataframe
    assert calls[0].args == (
        mock_duckdb_connection.register,
        "test_df",
        sample_dataframe,
    )

    # Second call: execute INSERT query
    expected_query = "INSERT  INTO test_table SELECT * FROM test_df"
    assert calls[1].args == (mock_duckdb_connection.execute, expected_query)


@pytest.mark.asyncio
async def test_bulk_insert_with_primary_key_generates_correct_query(
    mock_duckdb_connection, mock_async_thread_pool_executor, sample_dataframe
):
    """Test bulk_insert_from_dataframe generates correct INSERT OR IGNORE query with primary key."""
    async_db = AsyncDuckDb("test.db", mock_async_thread_pool_executor)
    async_db.conn = mock_duckdb_connection

    await async_db.bulk_insert_from_dataframe(
        "test_table", "test_df", sample_dataframe, has_primary_key=True
    )

    # Should be called twice: once for register, once for execute
    assert mock_async_thread_pool_executor.submit.call_count == 2
    calls = mock_async_thread_pool_executor.submit.call_args_list

    # First call: register dataframe
    assert calls[0].args == (
        mock_duckdb_connection.register,
        "test_df",
        sample_dataframe,
    )

    # Second call: execute INSERT OR IGNORE query
    expected_query = "INSERT OR IGNORE INTO test_table SELECT * FROM test_df"
    assert calls[1].args == (mock_duckdb_connection.execute, expected_query)


@pytest.mark.asyncio
async def test_bulk_insert_calls_register_before_execute(
    mock_duckdb_connection, mock_async_thread_pool_executor, sample_dataframe
):
    """Test that bulk_insert_from_dataframe calls register before execute."""
    async_db = AsyncDuckDb("test.db", mock_async_thread_pool_executor)
    async_db.conn = mock_duckdb_connection

    # Track call order
    call_order = []

    def track_calls(func, *args):
        if func == mock_duckdb_connection.register:
            call_order.append("register")
        elif func == mock_duckdb_connection.execute:
            call_order.append("execute")
        return Mock()

    mock_async_thread_pool_executor.submit.side_effect = track_calls

    await async_db.bulk_insert_from_dataframe(
        "test_table", "test_df", sample_dataframe
    )

    assert call_order == ["register", "execute"]
