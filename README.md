# Zigbee2MQTT Health

Monitor Zigbee2MQTT devices and publish health status to MQTT.

## Features

- MQTT-based device monitoring
- Publishes `online/offline` status to a health topic
- Configurable via environment variables

## Environment Variables

| Variable              | Default                                       | Description                                                                              |
|-----------------------|-----------------------------------------------|------------------------------------------------------------------------------------------|
| `MQTT_BROKER`         | `localhost`                                   | MQTT broker hostname                                                                     |
| `MQTT_PORT`           | `1883`                                        | MQTT broker port                                                                         |
| `MQTT_USERNAME`       |                                               | MQTT username                                                                            |
| `MQTT_PASSWORD`       |                                               | MQTT password                                                                            |
| `MQTT_CLIENT_ID`      | `socket.gethostname()`                        | Client ID used when connecting to the broker; defaults to the host’s hostname if not set |
| `CHECK_INTERVAL`      | `30`                                          | Seconds between health checks                                                            |
| `TIMEOUT_SECONDS`     | `60`                                          | Max allowed seconds since last message to be `online`                                    |
| `HEALTH_TOPIC`        | `zigbee2mqtt/healthz`                         | MQTT topic for health status                                                             |
| `DEVICE_TOPIC_PREFIX` | `zigbee2mqtt/`                                | Device topics prefix                                                                     |
| `EXCLUDED_TOPICS`     | `zigbee2mqtt/bridge,zigbee2mqtt/bridge/state` | Comma separated topics to ignore, supports MQTT wildcards                                |
| `LOG_LEVEL`           | `info`                                        | Python log level                                                                         |

### Docker

```bash
docker run -e MQTT_BROKER="mqtt" -e MQTT_USERNAME="user" -e MQTT_PASSWORD="pass" ghcr.io/sheyabernstein/zigbee2mqtt-health:latest
```

```yaml
services:
  zigbee2mqtt-health:
    image: ghcr.io/sheyabernstein/zigbee2mqtt-health:latest
    container_name: zigbee2mqtt-health
    restart: unless-stopped
    environment:
       MQTT_BROKER: localhost
       MQTT_PORT: 1883
       MQTT_USERNAME: user
       MQTT_PASSWORD: password
```