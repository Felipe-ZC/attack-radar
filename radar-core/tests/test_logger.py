import logging
import os
from unittest.mock import patch

from radar_core.logger import get_log_level_from_env, setup_logger, LOG_LEVEL_MAP


def test_get_log_level_from_env():
    for env_var, expected_result in LOG_LEVEL_MAP.items():
        with patch.dict(os.environ, {"LOG_LEVEL": env_var}):
            assert get_log_level_from_env() == expected_result


def test_setup_logger():
    for logging_level in LOG_LEVEL_MAP.keys():
        expected_name = f"test_logger_{logging_level}"
        log_obj = setup_logger(name=expected_name, log_level_str=logging_level)

        assert isinstance(log_obj, logging.Logger)
        assert log_obj.name == expected_name
        assert log_obj.level == LOG_LEVEL_MAP[logging_level]
        # TODO: Check that log_obj has the right formatter and handlers...
        # TODO: Check that this function creates the logs directory if needed...
        # TODO: Check that the rotation file handler was created with the correct params...
