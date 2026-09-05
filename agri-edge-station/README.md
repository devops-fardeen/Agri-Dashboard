# AgriSmart Tier 2: Offline Local Edge Station

This service powers **Tier 2 (Offline Local Hotspot & Direct Edge Gateway)** in the AgriSmart 3-Tier IoT Agriculture Architecture:
- **Tier 1**: Field Hardware & OLED Display (ESP32 / LoRa Nodes & Sensors)
- **Tier 2**: Offline Local Edge Station (`agri-edge-station` - FastAPI + SQLite)
- **Tier 3**: Cloud Telemetry Central (`agri-cloud-dashboard` - Next.js 16 + MongoDB)

---

## 🌾 Key Capabilities

1. **Zero-Internet Local Hotspot Operation**:
   - Runs locally on the Raspberry Pi / Edge Gateway at `http://10.42.0.1:8000` (or `http://localhost:8000`).
   - Serves a **100% self-contained offline dark-theme dashboard** (zero external CDN or internet dependencies).
   - Allows farmers to connect phone/tablet directly to the Pi's Wi-Fi hotspot in remote fields to monitor soil moisture, temperature, and manually toggle irrigation pumps.

2. **7-Day Offline Weather Cache Widget**:
   - Fetches 7-day forecast from Open-Meteo when network connectivity is present and caches it in SQLite (`weather_cache` table).
   - Automatically refreshes once every 24 hours.
   - Displayed seamlessly on the offline dashboard even when operating in disconnected fields.

3. **24-Hour Rolling Local Storage Pruning**:
   - Automatically deletes records where `synced_to_cloud == 1` AND `recorded_at < (now - 24 hours)`.
   - Prevents the Raspberry Pi's SD card from running out of disk space while keeping 24 hours of local data for offline trend charting.

4. **Field Scout Rover Telemetry & Manual D-Pad**:
   - Manages rover state (`heading`, `speed`, `battery`, `last_action`).
   - Interactive local D-pad controller (Forward, Backward, Turn Left, Turn Right, Emergency Stop).

5. **24-Hour Previous Data Graph**:
   - Zero-dependency inline HTML5 Canvas time-series chart.
   - Real-time dual-axis display for Soil Moisture (%) and Temperature (°C) with Zone A / Zone B switching.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Edge Station
```bash
python main.py
```
This boots:
- The FastAPI Local Dashboard on `http://localhost:8000/`
- The background Sensor Simulator thread (5s tick)
- The background Cloud Sync Worker thread (10s sync batch + 24h prune + weather cache)

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Self-contained Offline HTML/JS/CSS Local Dashboard |
| `/api/edge/status` | `GET` | Status overview (telemetry, pumps, rover, cached weather, buffer stats) |
| `/api/edge/weather` | `GET` | Cached 7-day Open-Meteo weather forecast |
| `/api/edge/rover` | `GET` | Field scout rover telemetry state |
| `/api/edge/rover/command` | `POST` | Transmits rover command (`MOVE_FORWARD`, `MOVE_BACKWARD`, `MOVE_LEFT`, `MOVE_RIGHT`, `STOP`) |
| `/api/edge/pump/{target}/{action}` | `POST` | Hardware pump relay control (`PUMP_ZONE_A` / `PUMP_ZONE_B`, action: `ON`, `OFF`, `TOGGLE`) |
| `/api/edge/history` | `GET` | 24-hour historical buffer for time-series charts (`zoneId=ZONE_A` or `ZONE_B`) |
