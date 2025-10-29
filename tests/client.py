import json


class FakeMQTTClient:
    """A fake MQTT client that mimics the Paho interface but stores published messages."""

    def __init__(self):
        self.subscriptions = []
        self.published = []
        self.connected = False
        self.username = None
        self.password = None

    def username_pw_set(self, username, password):
        self.username = username
        self.password = password

    def connect(self, host, port, keepalive):
        self.connected = True

    def subscribe(self, topic_filter):
        self.subscriptions.append(topic_filter)

    def publish(self, topic, payload, retain=False):
        self.published.append((topic, json.loads(payload), retain))

    def loop_forever(self):
        # We'll manually call handlers instead
        pass
