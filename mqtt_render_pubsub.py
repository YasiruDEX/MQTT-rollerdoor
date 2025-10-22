#!/usr/bin/env python3
"""
MQTT Render Broker - Complete Pub/Sub Script
Publishes and subscribes to the MQTT broker hosted on Render.com

IMPORTANT: This requires Render TCP Service (not Web Service)
See: RENDER_TCP_SERVICE.md for deployment instructions

Usage:
    # Publish a message
    python3 mqtt_render_pubsub.py --mode publish --host mqtt-xxxxx.render.com --port 12345 --topic "sensor/temp" --message "25.5"
    
    # Subscribe to topics
    python3 mqtt_render_pubsub.py --mode subscribe --host mqtt-xxxxx.render.com --port 12345 --topic "sensor/#"
    
    # Simulate sensor publishing
    python3 mqtt_render_pubsub.py --mode sensor --host mqtt-xxxxx.render.com --port 12345 --sensors 3 --interval 2
    
    # Interactive pub/sub
    python3 mqtt_render_pubsub.py --mode interactive --host mqtt-xxxxx.render.com --port 12345
"""

import paho.mqtt.client as mqtt
import time
import json
import argparse
import sys
from datetime import datetime
import random
import math

# Handle different versions of paho-mqtt
try:
    from paho.mqtt.client import CallbackAPIVersion
    MQTT_CALLBACK_API = CallbackAPIVersion.VERSION1
except ImportError:
    MQTT_CALLBACK_API = None


class MQTTRenderBroker:
    """Complete MQTT Pub/Sub client for Render.com broker"""
    
    def __init__(self, host, port, username="admin", password="password", client_id=None):
        """
        Initialize MQTT client
        
        Args:
            host: Render broker hostname (e.g., mqtt-xxxxx.render.com)
            port: Render broker port (e.g., 12345)
            username: MQTT username
            password: MQTT password
            client_id: Unique client identifier
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id or f"python-client-{int(time.time())}"
        self.client = None
        self.connected = False
        self.message_count = 0
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback when client connects"""
        if rc == 0:
            print(f"✓ Connected to {self.host}:{self.port}")
            self.connected = True
        else:
            print(f"✗ Connection failed with code {rc}")
            self.connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback when client disconnects"""
        if rc != 0:
            print(f"✗ Unexpected disconnection: {rc}")
        else:
            print("✓ Disconnected from broker")
        self.connected = False
    
    def on_publish(self, client, userdata, mid):
        """Callback after message is published"""
        # Silently acknowledge
        pass
    
    def on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback after subscription"""
        print(f"✓ Subscription confirmed (QoS: {granted_qos[0]})")
    
    def on_message(self, client, userdata, msg):
        """Callback when message is received"""
        self.message_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Try to parse as JSON
        try:
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)
            print(f"[{timestamp}] Message #{self.message_count} from '{msg.topic}':")
            print(json.dumps(data, indent=2))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Just print as string
            try:
                print(f"[{timestamp}] Message #{self.message_count} from '{msg.topic}':")
                print(msg.payload.decode('utf-8'))
            except:
                print(f"[{timestamp}] Message #{self.message_count} from '{msg.topic}':")
                print(f"[Binary data: {msg.payload.hex()}]")
        
        print("-" * 60)
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            if MQTT_CALLBACK_API is not None:
                self.client = mqtt.Client(MQTT_CALLBACK_API, self.client_id)
            else:
                self.client = mqtt.Client(self.client_id)
            
            self.client.username_pw_set(self.username, self.password)
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            self.client.on_subscribe = self.on_subscribe
            self.client.on_message = self.on_message
            
            print(f"Connecting to {self.host}:{self.port}...")
            self.client.connect(self.host, self.port, keepalive=60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 5
            start = time.time()
            while not self.connected and (time.time() - start) < timeout:
                time.sleep(0.1)
            
            if not self.connected:
                print("✗ Connection timeout")
                return False
            return True
            
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def publish(self, topic, message, qos=1, retain=False):
        """
        Publish message
        
        Args:
            topic: MQTT topic
            message: Message payload
            qos: Quality of Service (0, 1, or 2)
            retain: Retain message
        """
        try:
            if not self.connected:
                print("✗ Not connected to broker")
                return False
            
            result = self.client.publish(topic, message, qos=qos, retain=retain)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"✓ Published to '{topic}': {message}")
                return True
            else:
                print(f"✗ Publish failed: {result.rc}")
                return False
                
        except Exception as e:
            print(f"✗ Publish error: {e}")
            return False
    
    def publish_json(self, topic, data, qos=1, retain=False):
        """
        Publish JSON message
        
        Args:
            topic: MQTT topic
            data: Dictionary to serialize as JSON
            qos: Quality of Service
            retain: Retain message
        """
        try:
            message = json.dumps(data)
            return self.publish(topic, message, qos=qos, retain=retain)
        except Exception as e:
            print(f"✗ JSON publish error: {e}")
            return False
    
    def subscribe(self, topic, qos=1):
        """
        Subscribe to topic
        
        Args:
            topic: MQTT topic (supports # and + wildcards)
            qos: Quality of Service
        """
        try:
            if not self.connected:
                print("✗ Not connected to broker")
                return False
            
            result = self.client.subscribe(topic, qos=qos)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                print(f"Subscribed to '{topic}' (QoS: {qos})")
                return True
            else:
                print(f"✗ Subscribe failed: {result[0]}")
                return False
                
        except Exception as e:
            print(f"✗ Subscribe error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            print("Disconnected from broker")


def mode_publish(args):
    """Publish messages"""
    broker = MQTTRenderBroker(args.host, args.port, args.username, args.password)
    
    if not broker.connect():
        return False
    
    try:
        if args.message:
            broker.publish(args.topic, args.message)
        else:
            print("No message specified")
            return False
    finally:
        broker.disconnect()
    
    return True


def mode_subscribe(args):
    """Subscribe to messages"""
    broker = MQTTRenderBroker(args.host, args.port, args.username, args.password)
    
    if not broker.connect():
        return False
    
    try:
        broker.subscribe(args.topic, qos=args.qos)
        print(f"\n=== Listening for messages (Ctrl+C to exit) ===\n")
        
        # Keep listening
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        print(f"\nTotal messages received: {broker.message_count}")
        broker.disconnect()
    
    return True


def mode_sensor(args):
    """Simulate sensor publishing"""
    broker = MQTTRenderBroker(args.host, args.port, args.username, args.password)
    
    if not broker.connect():
        return False
    
    try:
        print(f"\n=== Simulating {args.sensors} sensors ===")
        print(f"Interval: {args.interval} seconds")
        if args.duration:
            print(f"Duration: {args.duration} seconds")
        print("Press Ctrl+C to stop\n")
        
        start_time = time.time()
        sequence = 0
        
        while True:
            # Publish from each sensor
            for i in range(1, args.sensors + 1):
                sequence += 1
                sensor_id = f"sensor_{i:03d}"
                
                # Generate realistic sensor data
                base_temp = 22.0
                base_humidity = 50.0
                
                temperature = base_temp + random.uniform(-2, 2) + 0.1 * math.sin(sequence / 10)
                humidity = base_humidity + random.uniform(-5, 5) + 0.1 * math.cos(sequence / 15)
                pressure = 1013.25 + random.uniform(-2, 2)
                
                sensor_data = {
                    "sensor_id": sensor_id,
                    "timestamp": datetime.now().isoformat(),
                    "sequence": sequence,
                    "temperature": round(temperature, 2),
                    "humidity": round(humidity, 2),
                    "pressure": round(pressure, 2),
                    "battery": round(random.uniform(60, 100), 1)
                }
                
                topic = f"sensors/{sensor_id}/data"
                broker.publish_json(topic, sensor_data)
            
            # Check duration
            if args.duration and (time.time() - start_time) >= args.duration:
                print("\nDuration reached, stopping...")
                break
            
            # Wait before next round
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        broker.disconnect()
    
    return True


def mode_interactive(args):
    """Interactive publish/subscribe mode"""
    broker = MQTTRenderBroker(args.host, args.port, args.username, args.password)
    
    if not broker.connect():
        return False
    
    try:
        print("\n=== MQTT Interactive Mode ===")
        print("Commands:")
        print("  pub <topic> <message> - Publish a message")
        print("  sub <topic>           - Subscribe to a topic")
        print("  sensor <n> <interval> - Simulate n sensors")
        print("  exit                  - Quit")
        print()
        
        while True:
            try:
                cmd = input("> ").strip().split()
                
                if not cmd:
                    continue
                
                if cmd[0].lower() == "exit":
                    break
                
                elif cmd[0].lower() == "pub":
                    if len(cmd) < 3:
                        print("Usage: pub <topic> <message>")
                        continue
                    topic = cmd[1]
                    message = " ".join(cmd[2:])
                    broker.publish(topic, message)
                
                elif cmd[0].lower() == "sub":
                    if len(cmd) < 2:
                        print("Usage: sub <topic>")
                        continue
                    topic = cmd[1]
                    broker.subscribe(topic)
                    print(f"Subscribed. Messages will appear below (type 'exit' to quit)")
                
                elif cmd[0].lower() == "sensor":
                    if len(cmd) < 3:
                        print("Usage: sensor <num_sensors> <interval_seconds>")
                        continue
                    num_sensors = int(cmd[1])
                    interval = int(cmd[2])
                    print(f"Publishing from {num_sensors} sensors every {interval}s...")
                    # Could implement this here
                
                else:
                    print(f"Unknown command: {cmd[0]}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
    finally:
        broker.disconnect()
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='MQTT Render Broker - Publish/Subscribe Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Publish a message
  python3 mqtt_render_pubsub.py --mode publish --host mqtt-xxxxx.render.com --port 12345 --topic "sensor/temp" --message "25.5"
  
  # Subscribe to all topics
  python3 mqtt_render_pubsub.py --mode subscribe --host mqtt-xxxxx.render.com --port 12345 --topic "#"
  
  # Simulate sensors
  python3 mqtt_render_pubsub.py --mode sensor --host mqtt-xxxxx.render.com --port 12345 --sensors 3 --interval 2
  
  # Interactive mode
  python3 mqtt_render_pubsub.py --mode interactive --host mqtt-xxxxx.render.com --port 12345

NOTE: Requires Render TCP Service (not Web Service)
        """
    )
    
    parser.add_argument('--mode', choices=['publish', 'subscribe', 'sensor', 'interactive'],
                        default='interactive',
                        help='Operating mode (default: interactive)')
    parser.add_argument('--host', required=True,
                        help='Render MQTT broker hostname (e.g., mqtt-xxxxx.render.com)')
    parser.add_argument('--port', type=int, required=True,
                        help='Render MQTT broker port (e.g., 12345)')
    parser.add_argument('--username', default='admin',
                        help='MQTT username (default: admin)')
    parser.add_argument('--password', default='password',
                        help='MQTT password (default: password)')
    
    # Publish mode arguments
    parser.add_argument('--topic', default='test/topic',
                        help='MQTT topic (default: test/topic)')
    parser.add_argument('--message',
                        help='Message to publish (publish mode)')
    
    # Subscribe mode arguments
    parser.add_argument('--qos', type=int, default=1,
                        help='Quality of Service 0-2 (default: 1)')
    
    # Sensor mode arguments
    parser.add_argument('--sensors', type=int, default=3,
                        help='Number of sensors to simulate (default: 3)')
    parser.add_argument('--interval', type=int, default=2,
                        help='Interval in seconds (default: 2)')
    parser.add_argument('--duration', type=int,
                        help='Duration in seconds (0 for infinite)')
    
    args = parser.parse_args()
    
    # Execute mode
    if args.mode == 'publish':
        success = mode_publish(args)
    elif args.mode == 'subscribe':
        success = mode_subscribe(args)
    elif args.mode == 'sensor':
        success = mode_sensor(args)
    else:  # interactive
        success = mode_interactive(args)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
