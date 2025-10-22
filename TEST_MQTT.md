# Testing MQTT Broker

This guide will help you test your MQTT broker using Python scripts.

## Installation

First, install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install paho-mqtt directly:

```bash
pip install paho-mqtt
```

## Scripts Overview

### 1. `mqtt_publisher.py` - Publish Messages

Publishes messages to the MQTT broker.

**Basic Usage:**

```bash
# Publish a single message
python mqtt_publisher.py --host localhost --port 1883 --username admin --password password --topic "test/topic" --message "Hello MQTT"

# Interactive mode (type messages in real-time)
python mqtt_publisher.py --host localhost --port 1883 --username admin --password password --topic "test/topic"

# Simulate sensor data (publishes 10 messages with 5-second interval)
python mqtt_publisher.py --sensor --interval 5 --count 10

# Publish to remote broker
python mqtt_publisher.py --host your-service-name.onrender.com --port 1883 --username admin --password password --topic "test/topic" --message "Hello Render"
```

**Arguments:**

- `--host`: MQTT broker host (default: localhost)
- `--port`: MQTT broker port (default: 1883)
- `--username`: MQTT username (default: admin)
- `--password`: MQTT password (default: password)
- `--topic`: Topic to publish to (default: test/topic)
- `--message`: Message to publish (if omitted, enters interactive mode)
- `--sensor`: Simulate sensor data
- `--interval`: Interval in seconds for sensor simulation (default: 5)
- `--count`: Number of messages to publish (default: 10)

### 2. `mqtt_subscriber.py` - Subscribe to Topics

Subscribes to and listens for messages from the MQTT broker.

**Basic Usage:**

```bash
# Subscribe to specific topic
python mqtt_subscriber.py --host localhost --port 1883 --username admin --password password --topic "test/topic"

# Subscribe to all topics (using # wildcard)
python mqtt_subscriber.py --host localhost --port 1883 --username admin --password password --all

# Subscribe with different QoS
python mqtt_subscriber.py --host localhost --topic "sensors/#" --qos 2

# Subscribe to remote broker
python mqtt_subscriber.py --host your-service-name.onrender.com --port 1883 --username admin --password password --topic "test/topic"
```

**Arguments:**

- `--host`: MQTT broker host (default: localhost)
- `--port`: MQTT broker port (default: 1883)
- `--username`: MQTT username (default: admin)
- `--password`: MQTT password (default: password)
- `--topic`: Topic to subscribe to (default: test/topic, supports # and + wildcards)
- `--qos`: Quality of Service 0-2 (default: 1)
- `--all`: Subscribe to all topics (#)

### 3. `mqtt_sensor_simulator.py` - Simulate IoT Sensors

Simulates multiple IoT sensors publishing data to the MQTT broker.

**Basic Usage:**

```bash
# Simulate 3 sensors with 2-second interval
python mqtt_sensor_simulator.py --host localhost --sensors 3 --interval 2

# Simulate 5 sensors for 60 seconds
python mqtt_sensor_simulator.py --sensors 5 --duration 60

# Simulate sensors on remote broker
python mqtt_sensor_simulator.py --host your-service-name.onrender.com --username admin --password password --sensors 3

# Use custom topic base
python mqtt_sensor_simulator.py --topic-base "iot/devices" --sensors 3 --interval 1
```

**Arguments:**

- `--host`: MQTT broker host (default: localhost)
- `--port`: MQTT broker port (default: 1883)
- `--username`: MQTT username (default: admin)
- `--password`: MQTT password (default: password)
- `--sensors`: Number of sensors to simulate (default: 3)
- `--interval`: Interval in seconds between messages (default: 2)
- `--duration`: Duration in seconds (0 for infinite)
- `--topic-base`: Base topic for sensors (default: sensors)

## Testing Scenarios

### Scenario 1: Local Testing (Terminal 1 & 2)

**Terminal 1 - Start Subscriber:**

```bash
python mqtt_subscriber.py --topic "test/#"
```

**Terminal 2 - Start Publisher:**

```bash
python mqtt_publisher.py --message "Test message"
```

Expected: Terminal 1 should receive the message.

### Scenario 2: Sensor Simulation

**Terminal 1 - Subscribe to sensor data:**

```bash
python mqtt_subscriber.py --topic "sensors/#"
```

**Terminal 2 - Simulate sensors:**

```bash
python mqtt_sensor_simulator.py --sensors 3 --interval 2
```

Expected: Terminal 1 should display sensor data every 2 seconds from 3 different sensors.

### Scenario 3: Multiple Topics

**Terminal 1 - Subscribe to all topics:**

```bash
python mqtt_subscriber.py --all
```

**Terminal 2 - Publish to different topics:**

```bash
python mqtt_publisher.py --topic "home/living-room/temperature" --message "22.5"
```

**Terminal 3 - Another publisher:**

```bash
python mqtt_publisher.py --topic "home/kitchen/humidity" --message "45.2"
```

Expected: Terminal 1 should see messages from both publishers.

### Scenario 4: Testing with Render.com

Once deployed to Render.com, test with:

**Terminal 1 - Subscribe:**

```bash
python mqtt_subscriber.py \
  --host your-service-name.onrender.com \
  --port 1883 \
  --username admin \
  --password your-password \
  --topic "test/topic"
```

**Terminal 2 - Publish:**

```bash
python mqtt_publisher.py \
  --host your-service-name.onrender.com \
  --port 1883 \
  --username admin \
  --password your-password \
  --topic "test/topic" \
  --message "Hello from Render!"
```

## Troubleshooting

### Connection Refused

- Check if broker is running
- Verify hostname and port
- Check firewall settings

### Authentication Failed

- Verify username and password are correct
- Make sure password file exists on broker

### Topics Not Received

- Check topic names match exactly (case-sensitive)
- Verify QoS levels are compatible
- Check broker logs

## MQTT Topic Wildcards

- `#` - Matches any number of levels (must be at end)
  - `sensors/#` matches `sensors/temp`, `sensors/humidity`, `sensors/room1/temp`, etc.
- `+` - Matches exactly one level
  - `sensors/+/temp` matches `sensors/room1/temp`, `sensors/room2/temp` but not `sensors/room1/level2/temp`

## JSON Message Format

The scripts support JSON messages. Example sensor data:

```json
{
  "sensor_id": "sensor_001",
  "timestamp": "2025-10-22T10:56:53.123456",
  "sequence": 1,
  "temperature": 22.45,
  "humidity": 48.23,
  "pressure": 1013.25,
  "battery": 85.5
}
```

## Tips

1. Use terminal multiplexing (tmux, screen) to run multiple scripts simultaneously
2. Combine with `mosquitto_sub` and `mosquitto_pub` CLI tools for testing
3. Monitor broker logs in Docker: `docker logs mqtt-broker`
4. Use high QoS (2) for critical messages but lower QoS (0) for high-frequency data to reduce overhead

## Next Steps

- Integrate these scripts with your IoT devices
- Create custom scripts for your specific use case
- Set up automated testing
- Deploy to Render.com and test end-to-end
