from unittest.mock import MagicMock, patch

import pytest
from paho.mqtt.client import Client


@pytest.fixture
def client():
    yield MagicMock(spec=Client)


@pytest.fixture(autouse=True)
def mock_sleep():
    with patch("time.sleep", lambda x: None) as mock_sleep:
        yield mock_sleep
