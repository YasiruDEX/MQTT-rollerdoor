#!/bin/sh
# Entrypoint script to run MQTT broker and HTTP health check server

# Start mosquitto in background
/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf &
MQTT_PID=$!

# Start a simple HTTP health check server on port 8080 using Python
python3 -m http.server 8080 > /dev/null 2>&1 &
HTTP_PID=$!

# Wait for MQTT process to exit
wait $MQTT_PID
EXIT_CODE=$?

# Kill the HTTP server if MQTT exits
kill $HTTP_PID 2>/dev/null || true

exit $EXIT_CODE
