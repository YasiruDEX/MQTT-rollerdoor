#!/usr/bin/env python3
"""
MQTT Publisher Script
Publishes messages to the MQTT broker hosted locally or on Render.com
"""

import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime
import argparse

# Handle different versions of paho-mqtt
try:
    from paho.mqtt.client import CallbackAPIVersion
    MQTT_CALLBACK_API = CallbackAPIVersion.VERSION1
except ImportError:
    MQTT_CALLBACK_API = None


class MQTTPublisher:
    def __init__(self, broker_host, broker_port, username, password, client_id="python-publisher"):
        """
        Initialize MQTT Publisher
        
        Args:
            broker_host: MQTT broker host/IP
            broker_port: MQTT broker port (default 1883)
            username: MQTT username
            password: MQTT password
            client_id: Unique client identifier
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client = None
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback when client connects"""
        if rc == 0:
            print(f"✓ Connected to {self.broker_host}:{self.broker_port}")
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
        print(f"✓ Message published (mid: {mid})")
    
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
            
            print(f"Connecting to {self.broker_host}:{self.broker_port}...")
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
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
        Publish message to topic
        
        Args:
            topic: MQTT topic
            message: Message payload
            qos: Quality of Service (0, 1, or 2)
            retain: Retain message on broker
        """
        try:
            if not self.connected:
                print("✗ Not connected to broker")
                return False
            
            result = self.client.publish(topic, message, qos=qos, retain=retain)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Published to '{topic}': {message}")
                return True
            else:
                print(f"✗ Publish failed: {result.rc}")
                return False
                
        except Exception as e:
            print(f"✗ Publish error: {e}")
            return False
    
    def publish_json(self, topic, data, qos=1, retain=False):
        """
        Publish JSON message to topic
        
        Args:
            topic: MQTT topic
            data: Dictionary to serialize as JSON
            qos: Quality of Service (0, 1, or 2)
            retain: Retain message on broker
        """
        try:
            message = json.dumps(data)
            return self.publish(topic, message, qos=qos, retain=retain)
        except Exception as e:
            print(f"✗ JSON publish error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()


def main():
    parser = argparse.ArgumentParser(description='MQTT Publisher Script')
    parser.add_argument('--host', default='localhost', help='MQTT broker host (default: localhost)')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port (default: 1883)')
    parser.add_argument('--username', default='admin', help='MQTT username (default: admin)')
    parser.add_argument('--password', default='password', help='MQTT password (default: password)')
    parser.add_argument('--topic', default='test/topic', help='MQTT topic to publish to')
    parser.add_argument('--message', help='Message to publish')
    parser.add_argument('--sensor', action='store_true', help='Simulate sensor data publishing')
    parser.add_argument('--interval', type=int, default=5, help='Interval in seconds for sensor simulation')
    parser.add_argument('--count', type=int, default=10, help='Number of messages to publish in sensor mode')
    
    args = parser.parse_args()
    
    # Create publisher
    publisher = MQTTPublisher(args.host, args.port, args.username, args.password)
    
    # Connect to broker
    if not publisher.connect():
        print("Failed to connect to broker")
        return
    
    try:
        if args.sensor:
            # Simulate sensor data
            print(f"\nSimulating sensor data (publishing {args.count} messages)...")
            for i in range(args.count):
                sensor_data = {
                    "id": "sensor_001",
                    "temperature": 20.5 + (i * 0.5),
                    "humidity": 45.0 + (i * 1.2),
                    "timestamp": datetime.now().isoformat(),
                    "sequence": i + 1
                }
                publisher.publish_json(args.topic, sensor_data)
                time.sleep(args.interval)
        elif args.message:
            # Publish single message
            publisher.publish(args.topic, args.message)
        else:
            # Interactive mode
            print("\n=== MQTT Publisher (Interactive Mode) ===")
            print(f"Topic: {args.topic}")
            print("Type 'exit' to quit\n")
            
            while True:
                message = input("Enter message: ").strip()
                if message.lower() == 'exit':
                    break
                if message:
                    publisher.publish(args.topic, message)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        print("\nDisconnecting...")
        publisher.disconnect()
        print("Done!")


if __name__ == '__main__':
    main()
