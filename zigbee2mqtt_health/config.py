import socket
from pathlib import Path
from typing import Optional, Set

from paho.mqtt.client import topic_matches_sub
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application configuration with env var loading and validation"""

    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    MQTT_BROKER: str = Field(default="localhost", description="MQTT broker hostname or IP")
    MQTT_PORT: int = Field(default=1883, description="MQTT broker port")
    MQTT_USERNAME: Optional[str] = Field(default=None, description="MQTT username")
    MQTT_PASSWORD: Optional[str] = Field(default=None, description="MQTT password")
    MQTT_CLIENT_ID: str = Field(default_factory=socket.gethostname, description="MQTT client ID")

    CHECK_INTERVAL: int = Field(default=30, description="Seconds between health checks")
    TIMEOUT_SECONDS: int = Field(default=60, description="Max age before considering offline")

    HEALTH_TOPIC: str = Field(default="zigbee2mqtt/healthz", description="MQTT topic for health status")
    DEVICE_TOPIC_PREFIX: str = Field(default="zigbee2mqtt/", description="Prefix for device topics")
    EXCLUDED_TOPICS: Set[str] = Field(
        default_factory=lambda: {"zigbee2mqtt/bridge/#", "zigbee2mqtt/default/#"},
        description="Comma-separated MQTT topics to ignore",
    )

    HEALTH_FILE_PATH: Path = Field(default=Path("/tmp/liveness"), description="Liveness file path")
    STALE_TOPIC_AGE_SECONDS: int = Field(default=60 * 60 * 24, description="Max topic age to be considered")

    class ConfigDict:
        env_prefix = ""  # No prefix (use bare env vars)
        case_sensitive = False

    def model_post_init(self, __context):
        self.EXCLUDED_TOPICS.add(self.HEALTH_TOPIC)

        if not all([self.MQTT_BROKER, self.MQTT_PORT, self.MQTT_USERNAME, self.MQTT_PASSWORD]):
            raise ValueError("MQTT_BROKER and MQTT_PORT must be set")

    def is_topic_excluded(self, topic: str) -> str | None:
        """Return the matching excluded pattern if topic matches an excluded MQTT pattern."""
        for pattern in self.EXCLUDED_TOPICS:
            if topic_matches_sub(pattern, topic):
                return pattern
        return None


try:
    config = Config()
except ValidationError as e:
    raise SystemExit(f"Invalid configuration:\n{e}") from None
