import os
import socket
from dataclasses import dataclass, field
from pathlib import Path

from paho.mqtt.client import topic_matches_sub


@dataclass
class Config:
    """Application configuration with env var loading and validation."""

    LOG_LEVEL: str = field(default="INFO")
    MQTT_BROKER: str = field(default="localhost")
    MQTT_PORT: int = field(default=1883)
    MQTT_USERNAME: str | None = field(default=None)
    MQTT_PASSWORD: str | None = field(default=None)
    MQTT_CLIENT_ID: str = field(default_factory=socket.gethostname)

    CHECK_INTERVAL: int = field(default=30)
    TIMEOUT_SECONDS: int = field(default=60)

    HEALTH_TOPIC: str = field(default="zigbee2mqtt/healthz")
    DEVICE_TOPIC_PREFIX: str = field(default="zigbee2mqtt/")
    EXCLUDED_TOPICS: set[str] = field(default_factory=lambda: {"zigbee2mqtt/bridge/#", "zigbee2mqtt/default/#"})

    HEARTBEAT_PATH: Path = field(default=Path("/tmp/heartbeat"))
    STALE_TOPIC_AGE_SECONDS: int = field(default=60 * 60 * 24)

    def __post_init__(self) -> None:
        """Load from env vars and validate."""
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", self.LOG_LEVEL).upper()
        self.MQTT_BROKER = os.getenv("MQTT_BROKER", self.MQTT_BROKER)
        self.MQTT_PORT = int(os.getenv("MQTT_PORT", str(self.MQTT_PORT)))
        self.MQTT_USERNAME = os.getenv("MQTT_USERNAME") or None
        self.MQTT_PASSWORD = os.getenv("MQTT_PASSWORD") or None
        self.MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", self.MQTT_CLIENT_ID)
        self.CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", str(self.CHECK_INTERVAL)))
        self.TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", str(self.TIMEOUT_SECONDS)))
        self.HEALTH_TOPIC = os.getenv("HEALTH_TOPIC", self.HEALTH_TOPIC)
        self.DEVICE_TOPIC_PREFIX = os.getenv("DEVICE_TOPIC_PREFIX", self.DEVICE_TOPIC_PREFIX)
        self.HEARTBEAT_PATH = Path(os.getenv("HEARTBEAT_PATH", str(self.HEARTBEAT_PATH)))
        self.STALE_TOPIC_AGE_SECONDS = int(os.getenv("STALE_TOPIC_AGE_SECONDS", str(self.STALE_TOPIC_AGE_SECONDS)))

        if raw := os.getenv("EXCLUDED_TOPICS"):
            self.EXCLUDED_TOPICS = {t.strip() for t in raw.split(",") if t.strip()}

        self.EXCLUDED_TOPICS.add(self.HEALTH_TOPIC)

        if not self.MQTT_BROKER or not self.MQTT_PORT:
            raise ValueError("MQTT_BROKER and MQTT_PORT must be set")

    def is_topic_excluded(self, topic: str) -> str | None:
        """Return the matching excluded pattern if topic matches an excluded MQTT pattern."""
        for pattern in self.EXCLUDED_TOPICS:
            if topic_matches_sub(pattern, topic):
                return pattern
        return None


try:
    config = Config()
except (ValueError, TypeError) as e:
    raise SystemExit(f"Invalid configuration:\n{e}") from None
