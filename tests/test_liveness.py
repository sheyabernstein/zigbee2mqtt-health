import pytest

from zigbee2mqtt_health import liveness
from zigbee2mqtt_health.config import config


def test_liveness_file_exists(tmp_path, monkeypatch):
    file = tmp_path / "liveness"
    file.touch()

    monkeypatch.setattr(config, "HEALTH_FILE_PATH", file)

    with pytest.raises(SystemExit) as e:
        liveness.main()
    assert e.value.code == 0


def test_liveness_file_missing(tmp_path, monkeypatch):
    file = tmp_path / "liveness"
    monkeypatch.setattr(config, "HEALTH_FILE_PATH", file)

    with pytest.raises(SystemExit) as e:
        liveness.main()
    assert e.value.code == 1
