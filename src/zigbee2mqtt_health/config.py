import os
from pathlib import Path


class Config:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_USERNAME = os.getenv("MQTT_USERNAME")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "60"))
    HEALTH_TOPIC = os.getenv("HEALTH_TOPIC", "zigbee2mqtt/healthz")
    DEVICE_TOPIC_PREFIX = os.getenv("DEVICE_TOPIC_PREFIX", "zigbee2mqtt/")
    EXCLUDED_TOPICS = set(
        os.getenv("EXCLUDED_TOPICS", "zigbee2mqtt/bridge,zigbee2mqtt/bridge/state").split(",") + [HEALTH_TOPIC],
    )
    HEALTH_FILE_PATH = Path(os.getenv("HEALTH_FILE_PATH", "/tmp/liveness"))
    STALE_TOPIC_AGE_SECONDS = int(os.getenv("STALE_TOPIC_AGE_SECONDS", 60 * 60 * 24))


config = Config()
