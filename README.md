# MQTT Broker for IoT Devices - Render.com Deployment

This repository contains a Dockerized MQTT broker (Eclipse Mosquitto) optimized for deployment on Render.com for IoT devices.

## Features

- **Eclipse Mosquitto** - Lightweight and reliable MQTT broker
- **MQTT Protocol** on port 1883
- **WebSocket Support** on port 9001 for web-based clients
- **Password Authentication** for security
- **Persistent Storage** for messages
- **Docker-based** deployment

## Setup Instructions

### 1. Generate Password File

Before deploying, you need to create a password file with hashed credentials:

```bash
# Using Docker locally
docker run -it --rm eclipse-mosquitto mosquitto_passwd -c passwd admin
```

This will prompt you to enter a password. Copy the generated hash and add it to the `passwd` file.

Alternatively, if you have mosquitto installed locally:

```bash
mosquitto_passwd -c passwd admin
```

The `passwd` file should look like:
```
admin:$7$101$xxxxxxxxxxxxx...
```

### 2. Deploy to Render.com

#### Option A: Using Render Dashboard

1. Go to [Render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: mqtt-broker (or your preferred name)
   - **Environment**: Docker
   - **Plan**: Starter or higher
   - **Docker Context**: `.`
   - **Dockerfile Path**: `./Dockerfile`

5. **Important**: Add the following in the "Advanced" section:
   - Set health check to disabled (MQTT doesn't have HTTP endpoints)
   - Configure environment variables if needed

6. Click **"Create Web Service"**

#### Option B: Using render.yaml (Infrastructure as Code)

1. Push this repository to GitHub
2. In Render Dashboard, click **"New +"** → **"Blueprint"**
3. Connect your repository
4. Render will detect the `render.yaml` file and set up the service automatically

### 3. Connect Your IoT Devices

Once deployed, Render will provide you with a URL. Your MQTT broker will be accessible at:

- **MQTT**: `mqtt://your-service-name.onrender.com:1883`
- **WebSocket**: `ws://your-service-name.onrender.com:9001`

#### Example Connection (Python with paho-mqtt):

```python
import paho.mqtt.client as mqtt

# Connection settings
broker = "your-service-name.onrender.com"
port = 1883
username = "admin"
password = "your-password"

# Create client
client = mqtt.Client("IoTDevice1")
client.username_pw_set(username, password)

# Connect to broker
client.connect(broker, port, 60)

# Publish message
client.publish("sensor/temperature", "25.5")

# Disconnect
client.disconnect()
```

#### Example Connection (Arduino/ESP32):

```cpp
#include <WiFi.h>
#include <PubSubClient.h>

const char* mqtt_server = "your-service-name.onrender.com";
const int mqtt_port = 1883;
const char* mqtt_user = "admin";
const char* mqtt_password = "your-password";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  client.setServer(mqtt_server, mqtt_port);
  client.connect("ESP32Client", mqtt_user, mqtt_password);
  
  if (client.connected()) {
    client.publish("sensor/status", "online");
  }
}
```

## Configuration

### Mosquitto Configuration (`mosquitto.conf`)

The configuration file includes:
- **Authentication**: Password-based authentication enabled
- **Persistence**: Message persistence enabled
- **Logging**: Comprehensive logging to file and stdout
- **WebSocket**: Enabled on port 9001
- **Security**: Anonymous connections disabled

### Modify Configuration

To change settings, edit `mosquitto.conf` and redeploy:

```conf
# Allow anonymous connections (not recommended for production)
allow_anonymous true

# Change max message size (in bytes)
message_size_limit 10485760

# Adjust log levels
log_type all
```

## Security Best Practices

1. **Always use strong passwords** for MQTT authentication
2. **Never commit passwords** to version control (add to .gitignore if needed)
3. **Use TLS/SSL** for production (requires additional configuration)
4. **Rotate credentials** regularly
5. **Monitor logs** for suspicious activity
6. Consider adding **IP whitelisting** if your IoT devices have static IPs

## Troubleshooting

### Connection Refused
- Check if the service is running on Render dashboard
- Verify port numbers (1883 for MQTT, 9001 for WebSocket)
- Check firewall settings

### Authentication Failed
- Verify username and password in the `passwd` file
- Ensure the password hash was generated correctly
- Check that `allow_anonymous false` is set in config

### Service Won't Start
- Check Render logs for errors
- Verify Docker build succeeded
- Ensure `passwd` file has valid entries

## Local Testing

Test the setup locally before deploying:

```bash
# Build the Docker image
docker build -t mqtt-broker .

# Run the container
docker run -d -p 1883:1883 -p 9001:9001 mqtt-broker

# Test connection
mosquitto_pub -h localhost -p 1883 -u admin -P your-password -t "test/topic" -m "Hello MQTT"
```

## Costs

Render.com pricing for MQTT broker:
- **Starter Plan**: ~$7/month (512MB RAM, shared CPU)
- **Standard Plan**: ~$25/month (2GB RAM, dedicated CPU)

Note: MQTT is lightweight and the Starter plan should be sufficient for most IoT projects with moderate traffic.

## Support

For issues related to:
- **Mosquitto**: See [Eclipse Mosquitto documentation](https://mosquitto.org/documentation/)
- **Render.com**: See [Render documentation](https://render.com/docs)
- **This setup**: Open an issue in this repository

## License

This project uses Eclipse Mosquitto which is licensed under the EPL/EDL.

## Additional Resources

- [MQTT Protocol](https://mqtt.org/)
- [Eclipse Mosquitto](https://mosquitto.org/)
- [Render Docker Deployment](https://render.com/docs/docker)
