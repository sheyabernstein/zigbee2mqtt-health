import threading
import time
from unittest.mock import Mock

import zigbee2mqtt_health.main as app
from tests.client import FakeMQTTClient
from zigbee2mqtt_health.config import config


def test_health_check(monkeypatch):
    """Full integration: simulate a device message, run health check, verify MQTT publish."""
    client = FakeMQTTClient()

    monkeypatch.setattr(app.mqtt, "Client", lambda *a, **kw: client)

    monkeypatch.setattr(config, "CHECK_INTERVAL", 0.1)
    monkeypatch.setattr(config, "TIMEOUT_SECONDS", 5)
    monkeypatch.setattr(config, "STALE_TOPIC_AGE_SECONDS", 3600)
    monkeypatch.setattr(config, "HEALTH_TOPIC", "zigbee2mqtt/health")

    # Simulate MQTT connection event
    app.on_connect(client, None, None, 0, None)

    # Simulate receiving a Zigbee message
    topic = f"{config.DEVICE_TOPIC_PREFIX}sensor/test"
    payload = b'{"temperature": 23.5}'
    app.on_message(client, None, Mock(topic=topic, payload=payload))

    # Ensure LAST_SEEN updated
    assert topic in app.LAST_SEEN

    # Run one health check iteration manually (we don't want infinite loop)
    now = app.now_utc()
    most_recent_topic, most_recent_time = max(app.LAST_SEEN.items(), key=lambda x: x[1])
    age_seconds = (now - most_recent_time).total_seconds()
    status = "online" if age_seconds <= config.TIMEOUT_SECONDS else "offline"

    # Trigger check_health() logic once
    thread = threading.Thread(target=app.check_health, args=(client,), daemon=True)
    thread.start()
    time.sleep(0.1)  # give the thread one iteration
    thread.join(timeout=0.3)

    # Assert that something was published to the health topic
    assert any(msg[0] == config.HEALTH_TOPIC for msg in client.published)

    # Inspect payload structure
    published_topic, published_payload, retain = client.published[-1]
    assert "status" in published_payload
    assert "age_seconds" in published_payload
    assert "last_seen" in published_payload
    assert published_payload["status"] == status
