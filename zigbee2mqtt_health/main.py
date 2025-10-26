import json
import logging
import signal
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
    logger.debug(f"Connected with result code: {rc}")
    topic_filter = f"{config.DEVICE_TOPIC_PREFIX}#"
    logger.debug(f"Subscribing to {topic_filter}")
    client.subscribe(topic_filter)
    logger.info(f"Subscribed to {topic_filter}")

    config.HEALTH_FILE_PATH.touch()
    threading.Thread(target=check_health, args=(client,), daemon=True).start()


def on_disconnect(mqttc, obj, flags, rc, properties):
    config.HEALTH_FILE_PATH.unlink(missing_ok=True)
    logger.warning(f"Disconnected with result code: {rc}")
    sys.exit(1)


def on_message(client, userdata, msg):
    topic = msg.topic

    if excluded_pattern := config.is_topic_excluded(topic):
        exclusion = excluded_pattern if excluded_pattern != topic else None
        suffix = f" ({exclusion})" if exclusion else ""
        logger.debug(f"Discarding message with excluded topic {topic}{suffix}")
        return

    now = now_utc()
    logger.debug(f"Saw {topic}")
    LAST_SEEN[topic] = now


def handle_exit(*args):
    config.HEALTH_FILE_PATH.unlink(missing_ok=True)

    if args:
        sig_num = args[0]
        sig_name = signal.Signals(sig_num).name
        logger.info(f"Exiting due to signal {sig_name} ({sig_num})")
        sys.exit(0)
    else:
        logger.warning("Exiting (manual or unknown cause)")
        sys.exit(1)


def check_health(client):
    while True:
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
    logger.debug(f"Starting with check interval {config.CHECK_INTERVAL}")

    client_id = config.MQTT_CLIENT_ID
    logger.debug(f"Connecting to mqtt://{config.MQTT_BROKER}:{config.MQTT_PORT} as {client_id}")
    mqttc = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)

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
