import os
import socket
from pathlib import Path

from paho.mqtt.client import topic_matches_sub


class Config:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_USERNAME = os.getenv("MQTT_USERNAME")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
    MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", socket.gethostname())
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "60"))
    HEALTH_TOPIC = os.getenv("HEALTH_TOPIC", "zigbee2mqtt/healthz")
    DEVICE_TOPIC_PREFIX = os.getenv("DEVICE_TOPIC_PREFIX", "zigbee2mqtt/")
    EXCLUDED_TOPICS = set(
        os.getenv("EXCLUDED_TOPICS", "zigbee2mqtt/bridge/#,zigbee2mqtt/default/#").split(",") + [HEALTH_TOPIC],
    )
    HEALTH_FILE_PATH = Path(os.getenv("HEALTH_FILE_PATH", "/tmp/liveness"))
    STALE_TOPIC_AGE_SECONDS = int(os.getenv("STALE_TOPIC_AGE_SECONDS", 60 * 60 * 24))

    def __init__(self):
        if not all([self.MQTT_BROKER, self.MQTT_PORT, self.MQTT_USERNAME, self.MQTT_PASSWORD]):
            raise Exception("Invalid config")

    def is_topic_excluded(self, topic: str) -> str | None:
        """Return the matching excluded pattern if topic matches an excluded MQTT pattern."""
        for pattern in self.EXCLUDED_TOPICS:
            if topic_matches_sub(pattern, topic):
                return pattern
        return None


config = Config()
