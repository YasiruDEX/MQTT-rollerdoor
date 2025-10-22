# 🧪 MQTT Broker Testing Results

## 📊 Test Summary

### ✅ Local Testing - ALL PASSING

**Date:** 2025-10-22  
**Environment:** Docker Compose + macOS

```
Test 1: Local Publisher Connection    ✅ PASS
Test 2: Message Publishing            ✅ PASS
Test 3: HTTP Health Check (Port 8080) ✅ PASS
Test 4: MQTT Protocol (Port 1883)     ✅ PASS
Test 5: Sensor Simulator              ✅ PASS
Test 6: Authentication (admin)        ✅ PASS
```

#### Detailed Results

```python
Connecting to localhost:1883...
✓ Connected to localhost:1883
Published to 'test/local': Local test successful!
✓ Message published (mid: 1)
✓ Disconnected from broker
✓ Test passed
```

### ⚠️ Render.com Testing - Configuration Issue

**Issue:** Render Web Services only support HTTP/HTTPS  
**Error:** Connection timeout on port 1883

**Root Cause:**
- Render Web Services expose only ports 80 (HTTP) and 443 (HTTPS)
- MQTT requires raw TCP port 1883
- Current deployment is as a Web Service

**Status:** ✅ Service deployed, ❌ Wrong service type for MQTT

---

## 🔧 How to Fix Render Deployment

### Method 1: Switch to Render TCP Service (RECOMMENDED) ⭐

Render.com offers "Private Services" (TCP/UDP) specifically for non-HTTP protocols.

**Steps:**

1. **Access Render Dashboard:**
   - Go to https://render.com/dashboard
   - Find your `mqtt-broker` service

2. **Delete Current Web Service:**
   - Click on the service
   - Go to **Settings**
   - Click **"Delete Service"**
   - Confirm deletion

3. **Create New TCP Service:**
   - Click **"+ New"**
   - Select **"Private Service"** (or TCP Service if available)
   - Select **"Docker"** as environment
   - Connect your GitHub repo: `https://github.com/YasiruDEX/MQTT-rollerdoor`

4. **Configure Service:**
   - **Name:** mqtt-broker-tcp
   - **Plan:** Starter ($12/month)
   - **Auto-deploy:** Enable
   - **Dockerfile path:** `./Dockerfile`
   - **Docker context:** `.`

5. **Configure Ports:**
   - **Expose TCP Port:** 1883
   - (Optional) Also expose 9001 for WebSocket
   - Don't worry about HTTP ports

6. **Deploy:**
   - Click **"Create Private Service"**
   - Wait 2-3 minutes for deployment
   - You'll get a URL like: `mqtt-xxxxx.render.com:12345`

### Method 2: Use Current Web Service + WebSocket Bridge

If you want to stay on Web Service, use WebSocket:

```bash
# Connect via WebSocket instead of raw MQTT
conda run -p /Users/yasiru/miniconda3 python3 -c "
import paho.mqtt.client as mqtt

# Note: Would require WebSocket bridge setup
# More complex, not recommended for this use case
"
```

### Method 3: Deploy to Different Provider

Other cloud providers with better TCP support:
- **Azure Container Instances** - Full TCP/UDP
- **DigitalOcean App Platform** - Full TCP/UDP  
- **AWS ECS/EKS** - Full TCP/UDP
- **Heroku** - Has native TCP support

---

## ✅ How to Test After Fixing

Once you have the new TCP service URL from Render (e.g., `mqtt-xxxxx.render.com:12345`):

### Test 1: Publisher Test

```bash
cd /Users/yasiru/Documents/GitHub/MQTT-rollerdoor

# Replace mqtt-xxxxx.render.com:12345 with your actual URL
conda run -p /Users/yasiru/miniconda3 python3 mqtt_publisher.py \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --username admin \
  --password password \
  --topic "test/render" \
  --message "Connected to Render TCP Service!"
```

**Expected Output:**
```
Connecting to mqtt-xxxxx.render.com:12345...
✓ Connected to mqtt-xxxxx.render.com:12345
Published to 'test/render': Connected to Render TCP Service!
✓ Message published (mid: 1)
✓ Disconnected from broker
Done!
```

### Test 2: Subscriber Test

```bash
# Terminal 1 - Subscribe to all topics
conda run -p /Users/yasiru/miniconda3 python3 mqtt_subscriber.py \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --username admin \
  --password password \
  --all
```

**Expected Output:**
```
Connecting to mqtt-xxxxx.render.com:12345...
✓ Connected to mqtt-xxxxx.render.com:12345
✓ Subscription confirmed (QoS: 1)

=== Listening for messages (Ctrl+C to exit) ===
```

### Test 3: Sensor Simulator

```bash
# Publish sensor data for 30 seconds
conda run -p /Users/yasiru/miniconda3 python3 mqtt_sensor_simulator.py \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --username admin \
  --password password \
  --sensors 2 \
  --interval 2 \
  --duration 30
```

**Expected Output:**
```
Connecting to mqtt-xxxxx.render.com:12345...
✓ Connected to mqtt-xxxxx.render.com:12345

=== Simulating 2 sensors ===
Interval: 2 seconds
Duration: 30 seconds
Press Ctrl+C to stop

[HH:MM:SS] sensor_001: Temp=22.5°C, Humidity=48.3%, Battery=85.2%
[HH:MM:SS] sensor_002: Temp=21.2°C, Humidity=50.1%, Battery=92.1%
[HH:MM:SS] sensor_001: Temp=22.8°C, Humidity=49.1%, Battery=84.8%
...
Duration reached, stopping...
```

---

## 📝 Connection Details After Setup

Once deployed to Render TCP Service:

| Parameter | Value | Example |
|-----------|-------|---------|
| Host | `mqtt-XXXXX.render.com` | `mqtt-xyzabc.render.com` |
| Port | Assigned by Render | `12345` |
| Username | `admin` | `admin` |
| Password | `password` | `password` |
| Protocol | `MQTT` | `mqtt://` |
| Full URL | `mqtt://host:port` | `mqtt://mqtt-xyzabc.render.com:12345` |

---

## 🎯 Complete End-to-End Testing

Once TCP service is running, here's the complete test sequence:

```bash
#!/bin/bash

# Configuration
RENDER_HOST="mqtt-xxxxx.render.com"  # Replace with your host
RENDER_PORT="12345"                  # Replace with your port
USERNAME="admin"
PASSWORD="password"

echo "=== MQTT Broker Test Suite ==="
echo "Target: mqtt://$RENDER_HOST:$RENDER_PORT"
echo ""

# Test 1: Simple publisher
echo "Test 1: Publishing single message..."
conda run -p /Users/yasiru/miniconda3 python3 mqtt_publisher.py \
  --host $RENDER_HOST \
  --port $RENDER_PORT \
  --username $USERNAME \
  --password $PASSWORD \
  --topic "test/connectivity" \
  --message "Connectivity test from local machine"

sleep 2

# Test 2: Sensor data
echo ""
echo "Test 2: Publishing sensor data..."
conda run -p /Users/yasiru/miniconda3 python3 mqtt_sensor_simulator.py \
  --host $RENDER_HOST \
  --port $RENDER_PORT \
  --username $USERNAME \
  --password $PASSWORD \
  --sensors 1 \
  --interval 1 \
  --duration 5

echo ""
echo "✅ All tests completed!"
```

---

## 🚨 Troubleshooting

### Issue: Still Getting Timeout

**Check:**
1. Verify TCP service is actually deployed (status shows "Live")
2. Confirm the port number from Render dashboard
3. Try connecting with netcat:
   ```bash
   nc -zv mqtt-xxxxx.render.com 12345
   ```

### Issue: Authentication Failed

**Check:**
1. Verify credentials are correct (default: admin/password)
2. Check password hash in `passwd` file
3. Regenerate if needed:
   ```bash
   ./generate_password.sh
   git push origin main
   # Redeploy service
   ```

### Issue: Message Not Received

**Check:**
1. Verify topic names are correct (case-sensitive)
2. Use subscriber to listen to all topics:
   ```bash
   python3 mqtt_subscriber.py --all
   ```
3. Check Render logs for errors

---

## 📈 Performance Metrics (After Deployment)

Expected performance on Render Starter ($12/month):

- **Max concurrent connections:** 100+
- **Message throughput:** 1,000+ msg/sec
- **Latency:** 50-100ms (depending on device location)
- **Memory usage:** ~100MB
- **CPU usage:** <5% for typical IoT workload

---

## ✅ Success Criteria

Your deployment is successful when:

1. ✓ TCP Service shows "Live" status (green)
2. ✓ Publisher script connects without timeout
3. ✓ Messages are published and received
4. ✓ Sensor data flows continuously
5. ✓ No authentication errors
6. ✓ Render logs show normal operation

---

## 🎉 Next Steps

1. **Create TCP Service** on Render (5 minutes)
2. **Get your connection URL** from Render
3. **Run test scripts** with the new URL
4. **Connect your IoT devices** to the remote broker
5. **Monitor in production** with subscriber script

---

**Documentation Version:** 2.0 - TCP Service Ready  
**Last Updated:** 2025-10-22  
**Status:** Ready for TCP Service Deployment  

For more help, see:
- [RENDER_TCP_SERVICE.md](./RENDER_TCP_SERVICE.md)
- [TEST_MQTT.md](./TEST_MQTT.md)
- [README.md](./README.md)
