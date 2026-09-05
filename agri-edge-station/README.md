# AgriSmart Tier 1 & 2: Local Edge Station & Physical Display Console

This service powers the **Tier 1 (On-Device Physical Display)** and **Tier 2 (Offline Local Hotspot Gateway)** in the AgriSmart 3-Tier IoT Agriculture Architecture:
- **Tier 1**: Physical On-Device Touchscreen Console (`display_gui.py` - Python Tkinter)
- **Tier 2**: Offline Local Hotspot Station (`server.py`, `sync_worker.py` - FastAPI + SQLite)
- **Tier 3**: Cloud Telemetry Central (`agri-cloud-dashboard` - Next.js 16 + MongoDB)

---

## 🖥️ Tier 1: Physical Touchscreen Console (`display_gui.py`)

- **Lightweight Native Tkinter GUI**: Built specifically for Raspberry Pi touchscreens (1024x600, 800x480, DSI/HDMI/TFT) with <30MB RAM footprint.
- **Keybindings**:
  - `F11`: Toggle Fullscreen
  - `Escape`: Exit Fullscreen
- **High-Contrast Dark Theme**: Outdoor-readable `#0d1117` palette with large typography.
- **Real-Time Synchronized Operation**: Reads and writes directly to `database.py` (`agri_edge.db`), remaining in 100% two-way sync with Tier 2 (Local AP) and Tier 3 (Cloud).
- **Dual Zone Panels**: Large Soil Moisture gauges (<40% amber, 40-75% green, >75% cyan), Soil Temp, Canopy Temp, Air Humidity, and large touch-friendly pump toggle buttons (>=50px).
- **Emergency Stop Rover Button**: Prominent red quick-action button setting rover status to `STOP`.

### Autostart Systemd Service (`agri-display.service`)
To enable automatic startup on Raspberry Pi boot:
```bash
sudo cp agri-display.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable agri-display.service
sudo systemctl start agri-display.service
```

---

## 🌾 Tier 2: Offline Local Hotspot Gateway (`server.py`)

1. **Zero-Internet Local Hotspot Operation**:
   - Runs locally at `http://10.42.0.1:8000` (or `http://localhost:8000`).
   - Serves a **100% self-contained offline dark-theme dashboard** (`static/index.html`).

2. **7-Day Offline Weather Cache Widget**:
   - Automatically caches Open-Meteo forecasts in SQLite when online.

3. **24-Hour Rolling Storage Pruning**:
   - Automatically cleans up synced records older than 24 hours to prevent SD card wear.

4. **Bidirectional Actuator & Telemetry Synchronization**:
   - Two-way pump relay control between local switches and cloud dashboard with `last-write-wins`.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Tier 1 Touchscreen Console
```bash
python display_gui.py
```

### 3. Run Tier 2 Local Gateway Station
```bash
python main.py
```
This boots:
- The FastAPI Local Dashboard on `http://localhost:8000/`
- The background Sensor Simulator thread (5s tick)
- The background Cloud Sync Worker thread (5s sync batch + 24h prune + weather cache + cloud command execution)
