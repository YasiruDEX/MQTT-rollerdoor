# Use Eclipse Mosquitto as the base image
FROM eclipse-mosquitto:latest

# Set working directory
WORKDIR /mosquitto

# Copy configuration files
COPY mosquitto.conf /mosquitto/config/mosquitto.conf
COPY passwd /mosquitto/config/passwd

# Create necessary directories
RUN mkdir -p /mosquitto/data /mosquitto/log

# Set proper permissions for passwd file (fix security warning)
RUN chmod 0700 /mosquitto/config/passwd && \
    chown -R mosquitto:mosquitto /mosquitto/data /mosquitto/log /mosquitto/config

# Expose MQTT ports
# 1883 - MQTT
# 9001 - MQTT over WebSockets
EXPOSE 1883 9001

# Run mosquitto
CMD ["/usr/sbin/mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
