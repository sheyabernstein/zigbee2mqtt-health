from unittest.mock import MagicMock

import pytest
from paho.mqtt.client import Client


@pytest.fixture
def client():
    yield MagicMock(spec=Client)
