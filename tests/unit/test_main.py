import signal
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from zigbee2mqtt_health.config import config
from zigbee2mqtt_health.main import LAST_SEEN, handle_exit, logger, on_connect, on_disconnect


def test_on_connect(client):
    on_connect(client=client, userdata=None, flags=None, rc=1, properties=None)

    client.subscribe.assert_called_once_with(f"{config.DEVICE_TOPIC_PREFIX}#")


@patch("zigbee2mqtt_health.main.sys.exit")
def test_on_disconnect(mock_exit):
    config.HEALTH_FILE_PATH.touch()
    on_disconnect(mqttc=None, obj=None, flags=None, rc=1, properties=None)

    assert not config.HEALTH_FILE_PATH.exists()
    mock_exit.assert_called_once_with(1)


@pytest.mark.parametrize(
    ["args", "expected_exit_code", "expected_log_method"],
    [
        [(signal.SIGTERM,), 0, "info"],
        [(signal.SIGINT,), 0, "info"],
        [(), 1, "warning"],
    ],
    ids=[
        "sigterm exit, info",
        "sigint exit, info",
        "manual exit, warning",
    ],
)
def test_handle_exit(args, expected_exit_code, expected_log_method, caplog):
    config.HEALTH_FILE_PATH.touch()

    with (
        patch.object(Path, "unlink") as mock_unlink,
        patch.object(logger, expected_log_method) as mock_logger,
        patch("sys.exit") as mock_exit,
    ):
        handle_exit(*args)

        mock_unlink.assert_called_once_with(missing_ok=True)
        mock_exit.assert_called_once_with(expected_exit_code)
        assert mock_logger.called


def test_check_health__online(monkeypatch):
    LAST_SEEN.clear()
    LAST_SEEN["device1"] = datetime.now(timezone.utc)

    _, most_recent_time = max(LAST_SEEN.items(), key=lambda x: x[1])
    age_seconds = (datetime.now(timezone.utc) - most_recent_time).total_seconds()
    assert age_seconds <= 1  # very recent


def test_check_health__offline(monkeypatch):
    LAST_SEEN.clear()
    LAST_SEEN["device1"] = datetime.now(timezone.utc) - timedelta(seconds=3600)
    _, most_recent_time = max(LAST_SEEN.items(), key=lambda x: x[1])
    age_seconds = (datetime.now(timezone.utc) - most_recent_time).total_seconds()
    assert age_seconds > 1000
