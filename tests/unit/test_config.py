from unittest.mock import patch

import pytest

from zigbee2mqtt_health.config import config


@pytest.mark.parametrize(
    "excluded_topics, topic, matching_pattern",
    [
        [["home/+/temperature"], "home/livingroom/temperature", "home/+/temperature"],
        [["home/+/temperature"], "home/kitchen/humidity", None],
        [["sensor/#", "home/+/temperature"], "sensor/garage/temp", "sensor/#"],
        [[], "any/topic", None],
    ],
    ids=[
        "single wildcard, match",
        "single wildcard, no match",
        "match multiple patterns first",
        "no excluded topics",
    ],
)
@patch("zigbee2mqtt_health.config.topic_matches_sub")
def test_config__is_topic_excluded(mock_topic_matches, excluded_topics, topic, matching_pattern):
    config.EXCLUDED_TOPICS = excluded_topics

    def side_effect(pattern, t):
        return pattern == matching_pattern

    mock_topic_matches.side_effect = side_effect

    result = config.is_topic_excluded(topic)

    assert result == matching_pattern
