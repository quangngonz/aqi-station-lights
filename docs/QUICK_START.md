# Quick Deployment Checklist

## ☁️ Backend Deployment (5 minutes)

### PythonAnywhere Setup

```bash
# 1. Sign up at pythonanywhere.com (free)
# 2. Upload backend.py and requirements.txt
# 3. In Bash console:
pip3 install --user -r requirements.txt

# 4. Create Flask web app pointing to backend.py
# 5. Set environment variable:
#    Name: PICO_API_TOKEN
#    Value: (generate a random 20+ char string)
# 6. Reload web app
```

### Test Backend

```bash
curl "https://yourusername.pythonanywhere.com/?token=YOUR_TOKEN"
# Should return: {"service": "Pico W Remote Control API", "status": "running"}
```

---

## 🤖 Pico Configuration

### Update config.py

```python
# Remote control settings
ENABLE_REMOTE_CONTROL = True
BACKEND_URL = "https://yourusername.pythonanywhere.com"  # No trailing slash!
BACKEND_TOKEN = "YOUR_TOKEN"  # Must match backend
BACKEND_POLL_INTERVAL = 30  # Check every 30 seconds
```

### Upload to Pico

Upload these files:

- ✅ main.py (updated with remote control)
- ✅ remote_control.py (new)
- ✅ config.py (with your settings)
- ✅ wifi.py

### Verify Connection

Monitor serial output for:

```
Wi-Fi connected.
Starting AQI monitoring (update interval: 300s)
Remote control enabled (poll interval: 30s)
```

---

## 🎮 Control Your Device

### From Terminal (Mac/Linux/Windows)

```bash
# Refresh AQI immediately
curl -X POST "https://yourusername.pythonanywhere.com/command?token=TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "refresh"}'

# Check device status
curl "https://yourusername.pythonanywhere.com/status?token=TOKEN"

# Restart device
curl -X POST "https://yourusername.pythonanywhere.com/command?token=TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "restart"}'
```

### Using Python Script

```bash
# Setup (once)
# Edit control_pico.py with your URL and token

# Use
python control_pico.py refresh   # Refresh AQI
python control_pico.py status    # Check status
python control_pico.py restart   # Restart device
python control_pico.py clear     # Clear pending command
```

### From Your Phone

Create browser bookmarks:

**Check Status:**

```
https://yourusername.pythonanywhere.com/status?token=TOKEN
```

**For POST requests, use a REST client app** (e.g., HTTP Request Shortcuts for Android)

---

## 🔍 Troubleshooting

### ❌ 401 Unauthorized

- **Problem**: Token mismatch
- **Fix**: Verify tokens match exactly in backend and Pico config

### ❌ Commands not executing

- **Check**: Current pending command
  ```bash
  curl "https://yourusername.pythonanywhere.com/command?token=TOKEN"
  ```
- **Fix**: Clear command if stuck
  ```bash
  curl -X POST "https://yourusername.pythonanywhere.com/command?token=TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"action": "none"}'
  ```

### ❌ Pico can't reach backend

- **Check**: Backend URL has no trailing slash
- **Check**: Token is correct (no spaces)
- **Test**: Can you access the URL from a browser?

---

## 📊 Architecture

```
You (Phone/Computer)
      ↓ HTTPS
[Cloud Backend - Flask]
      ↓ HTTPS (polling every 30s)
[Pico W Device]
      ↓
[Traffic Lights]
```

**How it works:**

1. Pico polls backend every 30s: "Any commands?"
2. You POST command to backend: "refresh"
3. Next poll: Pico receives "refresh" and executes
4. Pico clears command and reports status back

---

## 🔒 Security Checklist

- ✅ Change default token immediately
- ✅ Use HTTPS (automatic with PythonAnywhere)
- ✅ Don't commit token to git
- ✅ Use long random token (20+ characters)
- ⚠️ Token is visible in URL logs (acceptable for free tier)

---

## 💰 Cost

**FREE forever** with:

- PythonAnywhere Beginner account
- Pico W with WiFi
- Total: $0/month 💸

---

## 🚀 Next Steps

After basic setup works:

1. ✅ Test from different networks
2. ✅ Set up automation (cron jobs, scripts)
3. ✅ Build a monitoring dashboard
4. ✅ Add more devices with device IDs
5. ✅ Integrate with home automation

---

## 📚 Full Documentation

For detailed instructions, see:

- **REMOTE_CONTROL_GUIDE.md** - Complete setup guide
- **README.md** - Project overview

---

## 🆘 Quick Help

**Backend not responding?**

```bash
# Check backend health
curl "https://yourusername.pythonanywhere.com/health"
```

**Pico not polling?**

```python
# In Pico REPL, test manually:
import remote_control
from config import BACKEND_URL, BACKEND_TOKEN
action = remote_control.poll_backend_command(BACKEND_URL, BACKEND_TOKEN)
print(action)
```

**Need to debug?**

- Backend logs: PythonAnywhere Web tab → Error log
- Pico logs: Serial monitor (Thonny, screen, minicom)

---

**You're all set! 🎉**

Control your AQI monitor from anywhere in the world!
