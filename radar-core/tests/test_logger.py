import logging
import os
from unittest.mock import patch

from radar_core.logger import get_log_level_from_env, setup_logger

LEVEL_MAP: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def test_get_log_level_from_env():
    for env_var, expected_result in LEVEL_MAP.items():
        with patch.dict(os.environ, {"LOG_LEVEL": env_var}):
            assert get_log_level_from_env() == expected_result


def test_setup_logger():
    for logging_level in LEVEL_MAP.values():
        expected_name = f"test_logger_{logging_level}"
        log_obj = setup_logger(name=expected_name, log_level=logging_level)
        assert log_obj.name == expected_name
        assert log_obj.level == logging_level
        # TODO: Check that log_obj has the right formatter and handlers...
        # TODO: Check that this function creates the logs directory if needed...
        # TODO: Check that the rotation file handler was created with the correct params...
