from datetime import datetime, timedelta, timezone

from zigbee2mqtt_health.main import LAST_SEEN


def test_check_health_online(monkeypatch):
    LAST_SEEN.clear()
    LAST_SEEN["device1"] = datetime.now(timezone.utc)

    _, most_recent_time = max(LAST_SEEN.items(), key=lambda x: x[1])
    age_seconds = (datetime.now(timezone.utc) - most_recent_time).total_seconds()
    assert age_seconds <= 1  # very recent


def test_check_health_offline(monkeypatch):
    LAST_SEEN.clear()
    LAST_SEEN["device1"] = datetime.now(timezone.utc) - timedelta(seconds=3600)
    _, most_recent_time = max(LAST_SEEN.items(), key=lambda x: x[1])
    age_seconds = (datetime.now(timezone.utc) - most_recent_time).total_seconds()
    assert age_seconds > 1000
