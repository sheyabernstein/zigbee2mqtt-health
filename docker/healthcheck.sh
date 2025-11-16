#!/bin/sh

set -e

test $(find "${HEALTH_FILE_PATH:-/tmp/heartbeat}" -mmin -1) || exit 1
