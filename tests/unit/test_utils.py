from datetime import datetime, timezone

import pytest

from zigbee2mqtt_health.utils import isoformat_z, now_utc


def test_now_utc_returns_datetime():
    dt = now_utc()
    assert isinstance(dt, datetime)
    assert dt.tzinfo == timezone.utc


@pytest.mark.parametrize(
    ["dt", "expected"],
    [
        [datetime(2025, 10, 22, 15, 30, 45, 123456, tzinfo=timezone.utc), "2025-10-22T15:30:45.123Z"],
        [datetime(2020, 1, 1, 0, 0, 0, 999999, tzinfo=timezone.utc), "2020-01-01T00:00:00.999Z"],
    ],
    ids=[
        "milliseconds",
        "round microseconds",
    ],
)
def test_isoformat_z(dt, expected):
    assert isoformat_z(dt=dt) == expected
