# 🔧 Render.com Deployment Issue & Solutions

## ⚠️ Issue Identified

**Problem:** Render.com Web Services only expose HTTP/HTTPS (ports 80/443), but MQTT requires raw TCP port 1883.

**Error:**
```
Connecting to mqtt-rollerdoor.onrender.com:1883...
✗ Connection error: timed out
```

## ✅ Solution: Switch to Render TCP Service

Render.com has a different service type for non-HTTP protocols:

### Option 1: Deploy as TCP Service (RECOMMENDED) ✨

**Steps:**

1. **Go to Render Dashboard:** https://render.com/dashboard

2. **Delete Current Web Service:**
   - Click on `mqtt-broker` service
   - Click **"Settings"** → **"Delete Service"** → Confirm

3. **Create New TCP Service:**
   - Click **"New +"** → **"TCP Service"** (or look for "Custom TCP/UDP Service")
   - Connect your GitHub repository
   - Configure:
     - **Name:** mqtt-broker-tcp
     - **Environment:** Docker
     - **Plan:** Starter ($12/month for TCP)
     - **Docker Context:** `.`
     - **Dockerfile Path:** `./Dockerfile`

4. **Configure Port Mapping:**
   - **Container Port:** 1883
   - **Protocol:** TCP

5. **Click "Create TCP Service"**

6. **After Deployment:**
   - Render assigns you a unique hostname: `mqtt-xxxxx.render.com:XXXXX`
   - Use that for connections

### Option 2: Use Render Private Service + Proxy

More complex but allows HTTP front-end + TCP backend.

### Option 3: Docker Compose Your Own Server

Host on your own infrastructure if you need full control.

## 🧪 Test After Switching to TCP Service

Once you have the new TCP service URL from Render (e.g., `mqtt-xxxxx.render.com:12345`):

```bash
# Update the hostname and port in the command
conda run -p /Users/yasiru/miniconda3 python3 mqtt_publisher.py \
  --host mqtt-xxxxx.render.com \
  --port 12345 \
  --username admin \
  --password password \
  --topic "test/render" \
  --message "Connected to Render TCP Service!"
```

## 📊 Current Working Status

### ✅ Local Testing (Docker Compose)
```bash
# All tests PASSING ✅
✓ HTTP Health Check on port 8080
✓ MQTT on port 1883
✓ WebSocket on port 9001
✓ Authentication working
✓ Publisher script working
✓ Sensor simulator working
```

### ⚠️ Render.com HTTP/HTTPS Limitation
- ❌ MQTT (port 1883) - Not accessible via Web Service
- ❌ WebSocket (port 9001) - Not accessible via Web Service
- ✅ HTTP (port 8080) - Health checks work fine

### ✅ Solution: TCP Service on Render
- ✓ Will expose port 1883 on unique hostname:port
- ✓ Full MQTT support
- ✓ Same Docker image
- ✓ Slightly higher cost ($12 vs $7)

## 💡 Alternative: Use Azure Container Instances

If you prefer, you can also deploy to:
- **Azure Container Instances** - Full TCP support
- **AWS EC2** - Full TCP support
- **DigitalOcean App Platform** - Full TCP support

But Render TCP Service is the quickest option.

## 📋 Quick Summary

| Service Type | HTTP | MQTT (1883) | Cost | Setup |
|---|---|---|---|---|
| Web Service (Current) | ✅ | ❌ | $7/mo | Easy |
| TCP Service (Recommended) | ❌ | ✅ | $12/mo | Medium |
| VPS (Self-hosted) | ✅ | ✅ | $5-20/mo | Hard |

## 🚀 Next Steps

1. **Delete** current Web Service on Render
2. **Create** new TCP Service
3. **Test** with Python script once URL is provided
4. **Update** documentation with new connection details

Would you like me to create a simpler setup guide for the TCP service option?
