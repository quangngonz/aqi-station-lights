# Remote Control Setup Guide

## Overview

This guide will help you deploy a cloud backend and enable remote control of your Raspberry Pi Pico W AQI monitoring device from anywhere on the internet.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  You (anywhere) │ ◄─────► │  Cloud Backend   │ ◄─────► │   Pico W Device │
│   curl/browser  │  HTTPS  │  (Flask API)     │  HTTPS  │  (MicroPython)  │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                    │
                                    ├─ GET  /command  (Pico polls)
                                    ├─ POST /command  (You send)
                                    ├─ GET  /status   (You query)
                                    └─ POST /status   (Pico reports)
```

---

## Part 1: Deploy the Backend

### Option A: PythonAnywhere (Recommended - Free & Easy)

#### 1. Create Account

- Go to https://www.pythonanywhere.com
- Sign up for a free "Beginner" account
- Confirm your email

#### 2. Upload Backend Code

- Go to **Files** tab
- Click **Upload a file**
- Upload `backend.py` and `requirements.txt`

#### 3. Install Dependencies

- Go to **Consoles** tab
- Start a **Bash console**
- Run:

```bash
pip3 install --user -r requirements.txt
```

#### 4. Configure Web App

- Go to **Web** tab
- Click **Add a new web app**
- Choose **Flask** and Python 3.10
- Set path to: `/home/yourusername/backend.py`
- In **WSGI configuration file**, ensure it points to your `backend.py`

#### 5. Set Environment Variable (Security)

- In **Web** tab, scroll to **Environment variables**
- Add variable:
  - **Name**: `PICO_API_TOKEN`
  - **Value**: `MySecureToken123!` (change this!)

#### 6. Reload Web App

- Click **Reload** button
- Your API is now live at: `https://yourusername.pythonanywhere.com`

#### 7. Test Backend

Open terminal and test:

```bash
curl "https://yourusername.pythonanywhere.com/?token=MySecureToken123!"
```

Expected response:

```json
{
  "service": "Pico W Remote Control API",
  "status": "running"
}
```

---

### Option B: Render.com (Alternative - Free Tier)

#### 1. Create Account

- Go to https://render.com
- Sign up with GitHub

#### 2. Create Web Service

- Click **New +** → **Web Service**
- Connect your GitHub repo or upload files
- Configure:
  - **Name**: pico-remote-control
  - **Environment**: Python 3
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `gunicorn backend:app`

#### 3. Set Environment Variable

- Go to **Environment** tab
- Add:
  - **Key**: `PICO_API_TOKEN`
  - **Value**: `MySecureToken123!`

#### 4. Deploy

- Click **Create Web Service**
- Wait for deployment (2-3 minutes)
- Your URL: `https://pico-remote-control.onrender.com`

---

### Option C: Local Testing (Development Only)

```bash
# In your project directory
python3 backend.py
```

Access at: `http://localhost:5000`

⚠️ **Note**: This only works on your local network and requires your computer to be running.

---

## Part 2: Configure Your Pico W

### 1. Update Configuration File

Edit `config.py` (or copy from `config_example.py`):

```python
# Enable remote control
ENABLE_REMOTE_CONTROL = True

# Your deployed backend URL (without trailing slash)
BACKEND_URL = "https://yourusername.pythonanywhere.com"

# Must match the PICO_API_TOKEN from backend
BACKEND_TOKEN = "MySecureToken123!"

# How often to check for commands (seconds)
BACKEND_POLL_INTERVAL = 30
```

### 2. Upload Files to Pico

Upload these files to your Pico W:

- `main.py` (updated with remote control)
- `remote_control.py` (new file)
- `config.py` (with your settings)
- `wifi.py` (existing)

### 3. Restart Pico

Unplug and replug the Pico, or press the reset button.

### 4. Verify Connection

Check the serial output for:

```
Wi-Fi connected.
Starting AQI monitoring (update interval: 300s)
Remote control enabled (poll interval: 30s)
```

---

## Part 3: Control Your Device Remotely

### From Your Computer (Terminal)

#### Trigger AQI Refresh

```bash
curl -X POST "https://yourusername.pythonanywhere.com/command?token=MySecureToken123!" \
  -H "Content-Type: application/json" \
  -d '{"action": "refresh"}'
```

#### Restart Device

```bash
curl -X POST "https://yourusername.pythonanywhere.com/command?token=MySecureToken123!" \
  -H "Content-Type: application/json" \
  -d '{"action": "restart"}'
```

#### Check Device Status

```bash
curl "https://yourusername.pythonanywhere.com/status?token=MySecureToken123!"
```

#### Clear Command

```bash
curl -X POST "https://yourusername.pythonanywhere.com/command?token=MySecureToken123!" \
  -H "Content-Type: application/json" \
  -d '{"action": "none"}'
```

---

### From Your Phone (Browser)

Create bookmarks with these URLs:

**Refresh AQI:**

```
https://yourusername.pythonanywhere.com/command?token=MySecureToken123!&action=refresh
```

**Check Status:**

```
https://yourusername.pythonanywhere.com/status?token=MySecureToken123!
```

⚠️ **Note**: For POST requests, you'll need a REST client app or use the curl commands above.

---

### Python Script (Automation)

Create `control_pico.py`:

```python
import requests

BACKEND_URL = "https://yourusername.pythonanywhere.com"
TOKEN = "MySecureToken123!"

def send_command(action):
    """Send command to Pico device."""
    url = f"{BACKEND_URL}/command?token={TOKEN}"
    response = requests.post(url, json={"action": action})
    print(response.json())

def get_status():
    """Get device status."""
    url = f"{BACKEND_URL}/status?token={TOKEN}"
    response = requests.get(url)
    print(response.json())

# Usage
send_command("refresh")  # Trigger AQI refresh
get_status()             # Check current status
```

Run it:

```bash
python3 control_pico.py
```

---

## How It Works

### 1. Polling Loop (Pico → Backend)

Every 30 seconds (or your configured interval), the Pico asks:

```
GET /command?token=SECRET
```

Backend responds:

```json
{ "action": "none" } // or "refresh" or "restart"
```

### 2. Command Execution (Pico)

If `action == "refresh"`:

- Fetch new AQI data
- Update traffic lights
- Report status back to backend

If `action == "restart"`:

- Clear command
- Call `machine.reset()`

### 3. Status Reporting (Pico → Backend)

After each AQI update:

```
POST /status?token=SECRET
{"aqi": 45, "timestamp": 1702123456}
```

### 4. Command Issuing (You → Backend)

From anywhere:

```
POST /command?token=SECRET
{"action": "refresh"}
```

Next time Pico polls (within 30s), it will execute the command.

---

## Security Notes

### ✅ Good Practices

- Use HTTPS (automatic with PythonAnywhere/Render)
- Change default token immediately
- Use a long, random token (20+ characters)
- Don't commit tokens to git (use `.gitignore`)

### ⚠️ Limitations

- Token in URL is visible in logs (acceptable for free tier)
- No user authentication (single shared token)
- No rate limiting (backend could be spammed)

### 🔒 Production Improvements

For sensitive deployments:

- Move token to headers: `Authorization: Bearer TOKEN`
- Add rate limiting (Flask-Limiter)
- Use database for command queue
- Implement user authentication
- Add HTTPS certificate pinning on Pico

---

## Troubleshooting

### Pico Can't Connect to Backend

**Check:**

1. Is `ENABLE_REMOTE_CONTROL = True` in config.py?
2. Is backend URL correct (no trailing slash)?
3. Is token matching backend exactly?
4. Can you access backend from browser?

**Test:**

```python
# On Pico, in REPL:
import requests
response = requests.get("https://yourusername.pythonanywhere.com/command?token=MySecureToken123!")
print(response.json())
```

### Backend Returns 401 Unauthorized

**Problem**: Token mismatch

**Solution**: Verify tokens match exactly in:

- Backend environment variable: `PICO_API_TOKEN`
- Pico config.py: `BACKEND_TOKEN`

### Commands Not Executing

**Check:**

1. Is command still pending? Clear it first.
2. Check Pico serial output for errors.
3. Verify polling interval isn't too long.

**Debug:**

```bash
# Check current command
curl "https://yourusername.pythonanywhere.com/command?token=TOKEN"

# Clear command
curl -X POST "https://yourusername.pythonanywhere.com/command?token=TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "none"}'
```

### Backend Not Responding

**PythonAnywhere:**

- Check **Web** tab for errors
- View error logs in **Files** tab: `/var/log/`
- Ensure web app is reloaded

**Render:**

- Check **Logs** tab for errors
- Ensure service is running (not paused)

### Memory Issues on Pico

If Pico runs out of memory:

1. Increase `BACKEND_POLL_INTERVAL` to reduce requests
2. Remove debug print statements
3. Consider disabling local web server if not needed

---

## Example Usage Scenarios

### Scenario 1: Manual Refresh

You're about to go outside and want fresh AQI data:

```bash
curl -X POST "https://yourusername.pythonanywhere.com/command?token=TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "refresh"}'
```

Within 30 seconds, lights will update with latest data.

### Scenario 2: Scheduled Automation

Create a cron job to refresh AQI every hour:

```bash
# crontab -e
0 * * * * curl -X POST "https://yourusername.pythonanywhere.com/command?token=TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "refresh"}'
```

### Scenario 3: Monitoring Dashboard

Build a simple web page that shows status:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>AQI Monitor</title>
  </head>
  <body>
    <h1>Current AQI</h1>
    <div id="status">Loading...</div>
    <button onclick="refresh()">Refresh Now</button>

    <script>
      const API = 'https://yourusername.pythonanywhere.com';
      const TOKEN = 'MySecureToken123!';

      async function getStatus() {
        const res = await fetch(`${API}/status?token=${TOKEN}`);
        const data = await res.json();
        document.getElementById(
          'status'
        ).innerHTML = `AQI: ${data.aqi}<br>Age: ${data.age_seconds}s`;
      }

      async function refresh() {
        await fetch(`${API}/command?token=${TOKEN}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'refresh' }),
        });
        alert('Refresh command sent!');
      }

      // Update every 10 seconds
      setInterval(getStatus, 10000);
      getStatus();
    </script>
  </body>
</html>
```

---

## Cost Analysis

### Free Tier Limits

**PythonAnywhere (Beginner):**

- ✅ Always free
- ✅ HTTPS included
- ⚠️ Daily CPU quota (100 seconds)
- ⚠️ One web app only
- ✅ More than enough for polling every 30s

**Render (Free):**

- ✅ Free for 750 hours/month
- ✅ HTTPS included
- ⚠️ Spins down after 15 min inactivity
- ⚠️ Cold start delay (~30s)
- ✅ Good for occasional use

**Pico W Data Usage:**

- Poll every 30s: ~2 requests/min
- ~2,880 requests/day
- ~0.5 MB/day (negligible)

---

## Next Steps

### Enhancements You Can Add

1. **Mobile App**: Build with React Native or Flutter
2. **Notifications**: Email/SMS when AQI is unhealthy
3. **Multiple Devices**: Support multiple Picos with device IDs
4. **Historical Data**: Store AQI history in database
5. **Weather Integration**: Add temperature, humidity sensors
6. **Voice Control**: Integrate with Alexa or Google Home

### Learning Resources

- Flask Documentation: https://flask.palletsprojects.com
- MicroPython Requests: https://docs.micropython.org/en/latest/library/urequests.html
- REST API Design: https://restfulapi.net
- Raspberry Pi Pico W: https://www.raspberrypi.com/documentation/microcontrollers/

---

## Support

If you encounter issues:

1. Check serial output from Pico
2. Check backend logs
3. Verify network connectivity
4. Test each component separately

For more help, refer to:

- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/
- Raspberry Pi Forums: https://forums.raspberrypi.com/
- MicroPython Forum: https://forum.micropython.org/

---

## Summary

You now have:

- ✅ Cloud backend with REST API
- ✅ Secure token-based authentication
- ✅ Remote refresh and restart commands
- ✅ Status monitoring
- ✅ Free hosting on PythonAnywhere or Render

Your Pico W can now be controlled from anywhere in the world! 🌍
