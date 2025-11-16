#!/bin/sh

set -e

test $(find "${HEARTBEAT_PATH:-/tmp/heartbeat}" -mmin -1) || exit 1
