import importlib
import os
from unittest.mock import patch


def test_shhh_secret_max_length_invalid_value():
    with patch.dict(os.environ, {"SHHH_SECRET_MAX_LENGTH": "invalid"}):
        from shhh import config
        importlib.reload(config)
        assert config.DefaultConfig.SHHH_SECRET_MAX_LENGTH == 250


def test_shhh_db_liveness_retry_count_invalid_value():
    with patch.dict(os.environ, {"SHHH_DB_LIVENESS_RETRY_COUNT": "invalid"}):
        from shhh import config
        importlib.reload(config)
        assert config.DefaultConfig.SHHH_DB_LIVENESS_RETRY_COUNT == 5


def test_shhh_db_liveness_sleep_interval_invalid_value():
    with patch.dict(os.environ,
                    {"SHHH_DB_LIVENESS_SLEEP_INTERVAL": "invalid"}):
        from shhh import config
        importlib.reload(config)
        assert config.DefaultConfig.SHHH_DB_LIVENESS_SLEEP_INTERVAL == 1
