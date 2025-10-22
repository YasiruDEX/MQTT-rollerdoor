#!/usr/bin/env python3
"""
MQTT Subscriber Script
Subscribes to topics on the MQTT broker hosted locally or on Render.com
"""

import paho.mqtt.client as mqtt
import json
import argparse
from datetime import datetime
import time

# Handle different versions of paho-mqtt
try:
    from paho.mqtt.client import CallbackAPIVersion
    MQTT_CALLBACK_API = CallbackAPIVersion.VERSION1
except ImportError:
    MQTT_CALLBACK_API = None


class MQTTSubscriber:
    def __init__(self, broker_host, broker_port, username, password, client_id="python-subscriber"):
        """
        Initialize MQTT Subscriber
        
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
        self.message_count = 0
        
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
    
    def on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback after subscription"""
        print(f"✓ Subscription confirmed (QoS: {granted_qos[0]})")
    
    def on_message(self, client, userdata, msg):
        """Callback when message is received"""
        self.message_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n[{timestamp}] Message #{self.message_count}")
        print(f"Topic: {msg.topic}")
        print(f"QoS: {msg.qos}")
        print(f"Payload ({len(msg.payload)} bytes):")
        
        # Try to decode as JSON
        try:
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)
            print(json.dumps(data, indent=2))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Just print as string
            try:
                print(msg.payload.decode('utf-8'))
            except UnicodeDecodeError:
                print(f"[Binary data: {msg.payload.hex()}]")
        
        print("-" * 50)
    
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
            self.client.on_subscribe = self.on_subscribe
            self.client.on_message = self.on_message
            
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
    
    def subscribe(self, topic, qos=1):
        """
        Subscribe to topic
        
        Args:
            topic: MQTT topic (supports wildcards # and +)
            qos: Quality of Service (0, 1, or 2)
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
    
    def keep_listening(self):
        """Keep the client listening (blocking)"""
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            pass


def main():
    parser = argparse.ArgumentParser(description='MQTT Subscriber Script')
    parser.add_argument('--host', default='localhost', help='MQTT broker host (default: localhost)')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port (default: 1883)')
    parser.add_argument('--username', default='admin', help='MQTT username (default: admin)')
    parser.add_argument('--password', default='password', help='MQTT password (default: password)')
    parser.add_argument('--topic', default='test/topic', help='MQTT topic to subscribe to (supports # and + wildcards)')
    parser.add_argument('--qos', type=int, default=1, help='Quality of Service (0, 1, or 2)')
    parser.add_argument('--all', action='store_true', help='Subscribe to all topics (#)')
    
    args = parser.parse_args()
    
    # Create subscriber
    subscriber = MQTTSubscriber(args.host, args.port, args.username, args.password)
    
    # Connect to broker
    if not subscriber.connect():
        print("Failed to connect to broker")
        return
    
    # Subscribe to topic
    topic = '#' if args.all else args.topic
    if not subscriber.subscribe(topic, qos=args.qos):
        print("Failed to subscribe to topic")
        subscriber.disconnect()
        return
    
    print("\n=== Listening for messages (Ctrl+C to exit) ===\n")
    
    try:
        subscriber.keep_listening()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        print("\nDisconnecting...")
        subscriber.disconnect()
        print(f"Total messages received: {subscriber.message_count}")
        print("Done!")


if __name__ == '__main__':
    main()
