# MQTT Render Pub/Sub Script - Complete Guide

## Overview
`mqtt_render_pubsub.py` is a complete Python script that publishes and subscribes to your MQTT broker on Render.com.

## Prerequisites

### 1. Update Render to TCP Service ⚠️
**IMPORTANT:** Your current Web Service only exposes HTTP/HTTPS ports (80, 443). For MQTT to work, you need a TCP Service.

Follow instructions in `RENDER_TCP_SERVICE.md` to:
1. Delete current Web Service
2. Create new Private Service (TCP) with `render-tcp.yaml`
3. Get the new connection URL (e.g., `mqtt-xxxxx.render.com:12345`)

### 2. Install Dependencies
```bash
conda run -p /Users/yasiru/miniconda3 pip install paho-mqtt
```

## Usage Modes

### 1. Publish Mode - Send Messages

**Single Message:**
```bash
conda run -p /Users/yasiru/miniconda3 python3 mqtt_render_pubsub.py \
  --mode publish \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --topic "sensor/temperature" \
  --message "25.5"
```

**Real-world Example:**
```bash
conda run -p /Users/yasiru/miniconda3 python3 mqtt_render_pubsub.py \
  --mode publish \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --topic "devices/rollerboard/command" \
  --message '{"action":"open","angle":45}'
```

### 2. Subscribe Mode - Receive Messages

**Listen to Specific Topic:**
```bash
conda run -p /Users/yasiru/miniconda3 python3 mqtt_render_pubsub.py \
  --mode subscribe \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --topic "sensor/temperature"
```

**Listen to All Topics (Wildcard):**
```bash
conda run -p /Users/yasiru/miniconda3 python3 mqtt_render_pubsub.py \
  --mode subscribe \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --topic "#"
```

**Listen to Sensor Topics Only:**
```bash
conda run -p /Users/yasiru/miniconda3 python3 mqtt_render_pubsub.py \
  --mode subscribe \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --topic "sensors/+"
```

### 3. Sensor Simulation Mode

**Simulate 3 Sensors Publishing Every 2 Seconds:**
```bash
conda run -p /Users/yasiru/miniconda3 python3 mqtt_render_pubsub.py \
  --mode sensor \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --sensors 3 \
  --interval 2
```

**Run for 60 Seconds:**
```bash
conda run -p /Users/yasiru/miniconda3 python3 mqtt_render_pubsub.py \
  --mode sensor \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --sensors 3 \
  --interval 2 \
  --duration 60
```

### 4. Interactive Mode - Full Control

```bash
conda run -p /Users/yasiru/miniconda3 python3 mqtt_render_pubsub.py \
  --mode interactive \
  --host mqtt-xxxxx.render.com \
  --port 12345
```

Then use commands:
```
> pub sensor/temp 25.5
✓ Published to 'sensor/temp': 25.5

> sub sensor/#
Subscribed to 'sensor/#' (QoS: 1)

> sensor 2 5
Publishing from 2 sensors every 5s...

> exit
```

## Authentication

Change default credentials:
```bash
conda run -p /Users/yasiru/miniconda3 python3 mqtt_render_pubsub.py \
  --mode publish \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --username your_username \
  --password your_password \
  --topic "test" \
  --message "Hello"
```

## Sample Workflow - End-to-End Testing

**Terminal 1 - Subscribe (Listen for messages):**
```bash
conda run -p /Users/yasiru/miniconda3 python3 mqtt_render_pubsub.py \
  --mode subscribe \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --topic "test/#"
```

**Terminal 2 - Publish (Send messages):**
```bash
conda run -p /Users/yasiru/miniconda3 python3 mqtt_render_pubsub.py \
  --mode publish \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --topic "test/hello" \
  --message "Hello from Terminal 2!"
```

**Terminal 3 - Sensor Simulator:**
```bash
conda run -p /Users/yasiru/miniconda3 python3 mqtt_render_pubsub.py \
  --mode sensor \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --sensors 2 \
  --interval 3 \
  --duration 60
```

**Expected Output in Terminal 1:**
```
[12:34:56] Message #1 from 'test/hello':
Hello from Terminal 2!
------------------------------------------------------------
[12:34:59] Message #2 from 'sensors/sensor_001/data':
{
  "sensor_id": "sensor_001",
  "timestamp": "2025-10-22T12:34:59.123456",
  "sequence": 1,
  "temperature": 23.45,
  "humidity": 52.10,
  "pressure": 1013.89,
  "battery": 87.3
}
------------------------------------------------------------
```

## Topic Structure

### Standard Topics:
- `sensors/sensor_001/data` - Sensor data
- `devices/rollerdoor/status` - Device status
- `devices/rollerdoor/command` - Commands to device
- `system/health` - System health info

### Wildcards:
- `#` - All topics
- `sensors/+/data` - All sensor data
- `devices/#` - All device topics

## Troubleshooting

### Connection Timeout
```
✗ Connection timeout
```
**Solution:** Verify you're using a TCP Service on Render, not Web Service.

### Connection Refused
```
✗ Connection error: Connection refused
```
**Solution:** Check the hostname and port are correct from Render dashboard.

### Authentication Failed
```
✗ Connection failed with code 4
```
**Solution:** Check username/password are correct.

### No Messages Received
```
Subscribed to 'test/topic' (QoS: 1)
[waiting but no messages]
```
**Solution:** 
1. Verify publisher is connected and publishing
2. Check topic name matches exactly
3. Try subscribing to `#` to see all topics

## Features

✅ Publish single or multiple messages
✅ Subscribe with wildcard support
✅ Simulate realistic IoT sensor data
✅ JSON message formatting
✅ QoS (Quality of Service) support
✅ Message count tracking
✅ Interactive mode
✅ Automatic connection/disconnection
✅ Error handling and feedback
✅ Timestamp tracking

## Next Steps

1. **Deploy TCP Service** on Render
   - Follow `RENDER_TCP_SERVICE.md`
   - Get new connection URL

2. **Test Locally First**
   - Run subscriber: `python3 mqtt_render_pubsub.py --mode subscribe --host localhost --port 1883 --topic "#"`
   - Run publisher in another terminal
   - Verify messages flow

3. **Connect to Render**
   - Replace `localhost` with Render hostname
   - Replace `1883` with Render port

4. **Connect Your IoT Devices**
   - Use the same topic structure
   - Same authentication credentials
   - Same hostname:port

## Example IoT Device Integration

```python
import paho.mqtt.client as mqtt

# Configuration
MQTT_HOST = "mqtt-xxxxx.render.com"  # Your Render host
MQTT_PORT = 12345                     # Your Render port
MQTT_USER = "admin"
MQTT_PASS = "password"

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
client.publish("sensors/device_001/temperature", "23.5")
```

## Help
```bash
conda run -p /Users/yasiru/miniconda3 python3 mqtt_render_pubsub.py --help
```
