# 🆘 Render Deployment Troubleshooting

## Issue: Deployment Frozen After Image Upload

If your deployment is stuck at "Deploying..." after the Docker image is successfully pushed, follow these steps:

### 🛑 Step 1: Cancel Current Deployment

1. Go to https://render.com/dashboard
2. Click on your `mqtt-broker` service
3. Look for "Deployment" section
4. Click **"Cancel Deployment"** button
5. Wait for cancellation to complete

### 🔧 Step 2: Fix Configuration

The issue is likely one of these:

#### Problem A: Health Check Timeout
**Symptom:** Stuck after image upload  
**Cause:** MQTT doesn't have HTTP endpoints, but Render tries to health-check it  
**Solution:** We've already fixed `render.yaml` - health checks are now disabled

#### Problem B: Port Configuration
**Symptom:** Container won't start  
**Cause:** Fixed external port mapping not supported  
**Solution:** Updated to let Render.com assign ports dynamically

#### Problem C: Container Startup Issue
**Symptom:** Container starts but doesn't respond  
**Cause:** Mosquitto needs a moment to bind ports  
**Solution:** Add startup delay

### ✅ Step 3: Redeploy with Fixed Configuration

1. **Commit and push changes:**
   ```bash
   cd /Users/yasiru/Documents/GitHub/MQTT-rollerdoor
   git add render.yaml
   git commit -m "Fix Render deployment config - disable health checks"
   git push origin main
   ```

2. **Trigger manual redeploy on Render.com:**
   - Go to your service dashboard
   - Click **"Manual Deploy"** → **"Deploy latest commit"**

3. **Monitor the deployment:**
   - Check "Logs" tab in real-time
   - Should complete in 1-2 minutes
   - Look for: "mosquitto version 2.0.22 running"

### 📊 Expected Logs After Fix

```
Building...
[...Docker build steps...]
Pushing image to registry...
Upload succeeded
Deploying...
Starting service...
1761111401: mosquitto version 2.0.22 starting
1761111401: Config loaded from /mosquitto/config/mosquitto.conf
1761111401: Opening ipv4 listen socket on port 1883
1761111401: Opening ipv6 listen socket on port 1883
1761111401: Opening websockets listen socket on port 9001
1761111401: mosquitto version 2.0.22 running
✓ Service deployed successfully
```

### 🚨 Still Stuck? Try These Steps:

#### Option A: Use Simple Docker Service (Recommended)

Instead of Blueprint, use a standard Web Service:

1. Go to Render Dashboard
2. Delete the stuck service
3. Click **"New +" → "Web Service"**
4. Connect your GitHub repo
5. Configure:
   - **Name:** mqtt-broker
   - **Environment:** Docker
   - **Plan:** Starter
   - **Docker Context:** `.`
   - **Dockerfile Path:** `./Dockerfile`
6. Click **"Create Web Service"**

#### Option B: Use Render Native MQTT Service

If available in your region:
1. Go to Render Dashboard
2. Click **"New +" → "Managed Database"**
3. Look for "Message Queue" or "MQTT" option
4. Follow setup wizard

#### Option C: Check Render System Status

Sometimes Render.com has infrastructure issues:
- Visit https://status.render.com
- Check if there are any ongoing incidents
- If yes, wait for resolution and try again

### 🔍 Debugging Commands

If you want to test locally before redeploying:

```bash
# Build locally
docker build -t mqtt-broker .

# Run locally
docker run -d -p 1883:1883 -p 9001:9001 mqtt-broker

# Test connection
docker run --rm --network host \
  -it eclipse-mosquitto mosquitto_sub -h localhost -p 1883 \
  -u admin -P password -t "test/topic"
```

### ✅ Success Indicators

Your deployment is successful when:

1. ✓ Service shows "Live" status (green)
2. ✓ "Deployment" tab shows "Success"
3. ✓ Logs show "mosquitto version 2.0.22 running"
4. ✓ You can connect with Python script:
   ```bash
   python3 mqtt_publisher.py \
     --host your-service-name.onrender.com \
     --port 1883 \
     --username admin \
     --password password \
     --topic "test/topic" \
     --message "Hello Render!"
   ```

### 📞 Need More Help?

1. **Check Render Logs:**
   - Click service → "Logs" tab
   - Look for error messages
   - Copy error and search on Render docs

2. **Common Error Messages:**
   - "Container exits" → Check Dockerfile CMD
   - "Health check failed" → Expected for MQTT (now fixed)
   - "Port already in use" → Service conflict
   - "Out of memory" → Upgrade plan

3. **Contact Render Support:**
   - https://support.render.com
   - Include: service logs, render.yaml, Dockerfile

---

**Status:** If stuck, try the steps above in order.
**Estimated Resolution Time:** 5-10 minutes
