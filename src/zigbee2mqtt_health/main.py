import json
import logging
import signal
import socket
import sys
import threading
import time

import paho.mqtt.client as mqtt

from zigbee2mqtt_health.config import config
from zigbee2mqtt_health.utils import isoformat_z, now_utc

logger = logging.getLogger("zigbee2mqtt-health")
logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(funcName)s - %(message)s",
)

LAST_SEEN = {}


def on_connect(client, userdata, flags, rc, properties):
    logger.debug(f"Connected with result code {rc}")
    topic_filter = f"{config.DEVICE_TOPIC_PREFIX}#"
    logger.info(f"Subscribing to {topic_filter}")
    client.subscribe(topic_filter)

    config.HEALTH_FILE_PATH.touch()
    threading.Thread(target=check_health, args=(client,), daemon=True).start()


def on_disconnect(mqttc, obj, flags, rc, properties):
    config.HEALTH_FILE_PATH.unlink(missing_ok=True)
    logger.warning(f"Disconnected with result code {rc}")
    exit(1)


def on_message(client, userdata, msg):
    topic = msg.topic

    if excluded_topic := next((exclude for exclude in config.EXCLUDED_TOPICS if topic.startswith(exclude)), None):
        logger.debug(f"Discarding message with excluded topic {excluded_topic}")
        return

    now = now_utc()
    logger.debug(f"Saw {topic}")
    LAST_SEEN[topic] = now


def handle_exit(*args):
    logger.warning("Exiting")
    config.HEALTH_FILE_PATH.unlink(missing_ok=True)
    sys.exit(1)


def check_health(client):
    while True:
        status = None

        if not LAST_SEEN:
            logger.debug("No device messages seen yet")
            time.sleep(config.CHECK_INTERVAL)
            continue

        now = now_utc()
        most_recent_topic, most_recent_time = max(LAST_SEEN.items(), key=lambda x: x[1])
        age_seconds = (now - most_recent_time).total_seconds()

        status = "online" if age_seconds <= config.TIMEOUT_SECONDS else "offline"
        payload = {
            "status": status,
            "age_seconds": age_seconds,
            "last_seen": isoformat_z(most_recent_time),
        }

        logger.info(f"{status}: {most_recent_topic} seen {age_seconds:.0f} seconds ago")
        logger.debug(f"Publishing {config.HEALTH_TOPIC}: {payload}")
        client.publish(f"{config.HEALTH_TOPIC}", json.dumps(payload), retain=True)

        cutoff = now.timestamp() - config.STALE_TOPIC_AGE_SECONDS
        last_seen_copy = dict(LAST_SEEN)
        for topic, ts in last_seen_copy.items():
            if ts.timestamp() < cutoff:
                logger.debug(f"Purging stale topic {topic} last seen at {ts}")
                del LAST_SEEN[topic]

        time.sleep(config.CHECK_INTERVAL)


def main():
    if not all([config.MQTT_BROKER, config.MQTT_PORT, config.MQTT_USERNAME, config.MQTT_PASSWORD]):
        raise Exception("Invalid config")

    logger.debug(f"Start with check interval {config.CHECK_INTERVAL}")

    client_id = socket.gethostname()
    logger.debug(f"Connecting to broker as {client_id}")
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)

    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect
    mqttc.on_message = on_message
    mqttc.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handle_exit)

    mqttc.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
    mqttc.loop_forever()


if __name__ == "__main__":
    main()
