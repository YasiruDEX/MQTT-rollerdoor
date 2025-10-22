#!/bin/bash
# Generate password hash for MQTT

# Create temporary files
TEMP_PASSWD=$(mktemp)
DOCKER_PATH="/Applications/Docker.app/Contents/Resources/bin/docker"

# Generate password file in container
$DOCKER_PATH run --rm -v "$TEMP_PASSWD:/tmp/passwd" eclipse-mosquitto mosquitto_passwd -c -b /tmp/passwd admin password

# Display result
echo "Password hash generated:"
cat "$TEMP_PASSWD"

# Copy to passwd file
echo ""
echo "Copying to passwd file..."
cp "$TEMP_PASSWD" passwd
chmod 700 passwd

# Clean up
rm "$TEMP_PASSWD"

echo "Done! Updated passwd file."
