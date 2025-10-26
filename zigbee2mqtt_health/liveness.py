import sys

from zigbee2mqtt_health.config import config


def main():
    sys.exit(0 if config.HEALTH_FILE_PATH.exists() else 1)


if __name__ == "__main__":
    main()
