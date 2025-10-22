#!/usr/bin/env python3
"""
MQTT Sensor Simulator
Simulates IoT sensor data publishing to MQTT broker
Useful for testing and development
"""

import paho.mqtt.client as mqtt
import json
import time
import random
import argparse
from datetime import datetime
import math

# Handle different versions of paho-mqtt
try:
    from paho.mqtt.client import CallbackAPIVersion
    MQTT_CALLBACK_API = CallbackAPIVersion.VERSION1
except ImportError:
    MQTT_CALLBACK_API = None


class SensorSimulator:
    def __init__(self, broker_host, broker_port, username, password, client_id="sensor-simulator"):
        """
        Initialize Sensor Simulator
        
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
        self.sequence = 0
        
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
        self.connected = False
    
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
    
    def publish_sensor_data(self, sensor_id, topic_base="sensors"):
        """
        Publish sensor data
        
        Args:
            sensor_id: Unique sensor identifier
            topic_base: Base topic for sensors
        """
        self.sequence += 1
        
        # Simulate realistic sensor readings with slight variation
        base_temp = 22.0
        base_humidity = 50.0
        
        temperature = base_temp + random.uniform(-2, 2) + 0.1 * math.sin(self.sequence / 10)
        humidity = base_humidity + random.uniform(-5, 5) + 0.1 * math.cos(self.sequence / 15)
        pressure = 1013.25 + random.uniform(-2, 2)
        
        sensor_data = {
            "sensor_id": sensor_id,
            "timestamp": datetime.now().isoformat(),
            "sequence": self.sequence,
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "pressure": round(pressure, 2),
            "battery": round(random.uniform(60, 100), 1)
        }
        
        topic = f"{topic_base}/{sensor_id}/data"
        message = json.dumps(sensor_data)
        
        try:
            result = self.client.publish(topic, message, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {sensor_id}: "
                      f"Temp={sensor_data['temperature']}°C, "
                      f"Humidity={sensor_data['humidity']}%, "
                      f"Battery={sensor_data['battery']}%")
                return True
            else:
                print(f"✗ Publish failed: {result.rc}")
                return False
        except Exception as e:
            print(f"✗ Publish error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()


def main():
    parser = argparse.ArgumentParser(description='MQTT Sensor Simulator')
    parser.add_argument('--host', default='localhost', help='MQTT broker host (default: localhost)')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port (default: 1883)')
    parser.add_argument('--username', default='admin', help='MQTT username (default: admin)')
    parser.add_argument('--password', default='password', help='MQTT password (default: password)')
    parser.add_argument('--sensors', type=int, default=3, help='Number of sensors to simulate (default: 3)')
    parser.add_argument('--interval', type=int, default=2, help='Interval in seconds between messages (default: 2)')
    parser.add_argument('--duration', type=int, help='Duration in seconds (0 for infinite)')
    parser.add_argument('--topic-base', default='sensors', help='Base topic for sensors (default: sensors)')
    
    args = parser.parse_args()
    
    # Create simulator
    simulator = SensorSimulator(args.host, args.port, args.username, args.password)
    
    # Connect to broker
    if not simulator.connect():
        print("Failed to connect to broker")
        return
    
    print(f"\n=== Simulating {args.sensors} sensors ===")
    print(f"Interval: {args.interval} seconds")
    if args.duration:
        print(f"Duration: {args.duration} seconds")
    print("Press Ctrl+C to stop\n")
    
    start_time = time.time()
    
    try:
        while True:
            # Publish data from all sensors
            for i in range(1, args.sensors + 1):
                sensor_id = f"sensor_{i:03d}"
                simulator.publish_sensor_data(sensor_id, args.topic_base)
            
            # Check duration
            if args.duration and (time.time() - start_time) >= args.duration:
                print("\nDuration reached, stopping...")
                break
            
            # Wait before next round
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        print("\nDisconnecting...")
        simulator.disconnect()
        print("Done!")


if __name__ == '__main__':
    main()
