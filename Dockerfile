# Use Eclipse Mosquitto as the base image
FROM eclipse-mosquitto:latest

# Install Python and netcat for health checks
RUN apk add --no-cache python3 netcat-openbsd

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

# Create a health check script
COPY healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Create entrypoint script that runs both mosquitto and HTTP health check server
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose MQTT ports and HTTP health check port
# 1883 - MQTT
# 9001 - MQTT over WebSockets
# 8080 - HTTP health check (for Render.com)
EXPOSE 1883 9001 8080

# Health check configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD /usr/local/bin/healthcheck.sh

# Run entrypoint
CMD ["/bin/sh", "/usr/local/bin/entrypoint.sh"]
