#!/bin/sh
# Health check script for MQTT broker
# Checks if MQTT is listening on port 1883

# Try to connect to MQTT port
if nc -zv 127.0.0.1 1883 > /dev/null 2>&1; then
  exit 0
else
  exit 1
fi
