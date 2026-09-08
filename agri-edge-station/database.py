import sqlite3
import os
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agri_edge.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=15.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for high concurrency between reader threads & background writer
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db():
    """Initializes the SQLite database with all tables, indices, and default seed records."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Telemetry storage table (Offline buffer)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_id TEXT NOT NULL,
                node_id TEXT NOT NULL DEFAULT 'EDGE_STATION_PI',
                recorded_at TEXT NOT NULL,
                soil_moisture REAL NOT NULL,
                soil_temp REAL NOT NULL,
                ambient_temp REAL NOT NULL,
                ambient_humidity REAL NOT NULL,
                light_lux REAL DEFAULT 0.0,
                barometric_pressure REAL DEFAULT 1013.25,
                pump_active INTEGER DEFAULT 0,
                rain_detected INTEGER DEFAULT 0,
                synced_to_cloud INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Safe automatic migration for existing database instances
        try:
            cursor.execute("ALTER TABLE telemetry ADD COLUMN rain_detected INTEGER DEFAULT 0;")
        except Exception:
            pass # Already exists
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_synced ON telemetry(synced_to_cloud, id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_zone_rec ON telemetry(zone_id, recorded_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_rec ON telemetry(recorded_at DESC);")
        
        # 2. Actuators state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actuators (
                target TEXT PRIMARY KEY,
                state INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            );
        """)
        
        # 3. Weather Cache Table (7-Day offline forecast cache)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_cache (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                fetched_at TEXT NOT NULL,
                forecast_json TEXT NOT NULL
            );
        """)
        
        # 4. Rover State Table (Heading, speed, battery, last command)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rover_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                heading TEXT NOT NULL DEFAULT 'NW (312°)',
                speed REAL NOT NULL DEFAULT 0.0,
                battery INTEGER NOT NULL DEFAULT 84,
                last_action TEXT NOT NULL DEFAULT 'STOP',
                updated_at TEXT NOT NULL
            );
        """)
        
        # 5. AI Detections Storage Table (Vision Models inference events)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT NOT NULL DEFAULT 'NODE_01',
                model_name TEXT NOT NULL,
                detection_label TEXT NOT NULL,
                confidence REAL NOT NULL,
                image_path TEXT,
                metadata_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                synced_to_cloud INTEGER DEFAULT 0
            );
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_synced ON ai_detections(synced_to_cloud, id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_node_rec ON ai_detections(node_id, created_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_model ON ai_detections(model_name, created_at DESC);")
        
        # 6. Farm Location / Settings Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farm_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)
        
        # Seed default farm settings if missing
        now_iso = datetime.now(timezone.utc).isoformat()
        cursor.execute("INSERT OR IGNORE INTO farm_settings (key, value, updated_at) VALUES ('location_name', 'Lucknow Farm Zone', ?)", (now_iso,))
        cursor.execute("INSERT OR IGNORE INTO farm_settings (key, value, updated_at) VALUES ('latitude', '26.8467', ?)", (now_iso,))
        cursor.execute("INSERT OR IGNORE INTO farm_settings (key, value, updated_at) VALUES ('longitude', '80.9462', ?)", (now_iso,))
        
        # Seed default actuator relays if missing
        cursor.execute("""
            INSERT OR IGNORE INTO actuators (target, state, updated_at)
            VALUES ('PUMP_ZONE_A', 0, ?)
        """, (now_iso,))
        cursor.execute("""
            INSERT OR IGNORE INTO actuators (target, state, updated_at)
            VALUES ('PUMP_ZONE_B', 0, ?)
        """, (now_iso,))
        
        # Seed default rover state if missing
        cursor.execute("""
            INSERT OR IGNORE INTO rover_state (id, heading, speed, battery, last_action, updated_at)
            VALUES (1, 'NW (312°)', 0.0, 84, 'STOP', ?)
        """, (now_iso,))
        
        # Seed 7-day weather forecast cache if missing
        cursor.execute("SELECT forecast_json FROM weather_cache WHERE id = 1")
        w_row = cursor.fetchone()
        seed_needed = True
        if w_row and w_row["forecast_json"]:
            try:
                parsed_w = json.loads(w_row["forecast_json"])
                if isinstance(parsed_w.get("days"), list) and len(parsed_w["days"]) >= 7:
                    seed_needed = False
            except Exception:
                pass
        
        if seed_needed:
            today_dt = datetime.now(timezone.utc)
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            default_days = [
                {"date": (today_dt + timedelta(days=0)).strftime("%Y-%m-%d"), "day_name": "Today", "temp_max": 28.5, "temp_min": 21.0, "rain_prob": 0, "condition": "Sunny", "weather_code": 0, "precip_sum": 0.0},
                {"date": (today_dt + timedelta(days=1)).strftime("%Y-%m-%d"), "day_name": day_names[(today_dt + timedelta(days=1)).weekday()], "temp_max": 27.0, "temp_min": 20.0, "rain_prob": 10, "condition": "Partly Cloudy", "weather_code": 2, "precip_sum": 0.0},
                {"date": (today_dt + timedelta(days=2)).strftime("%Y-%m-%d"), "day_name": day_names[(today_dt + timedelta(days=2)).weekday()], "temp_max": 25.0, "temp_min": 19.5, "rain_prob": 65, "condition": "Rain", "weather_code": 61, "precip_sum": 2.5},
                {"date": (today_dt + timedelta(days=3)).strftime("%Y-%m-%d"), "day_name": day_names[(today_dt + timedelta(days=3)).weekday()], "temp_max": 29.0, "temp_min": 22.0, "rain_prob": 5, "condition": "Sunny", "weather_code": 0, "precip_sum": 0.0},
                {"date": (today_dt + timedelta(days=4)).strftime("%Y-%m-%d"), "day_name": day_names[(today_dt + timedelta(days=4)).weekday()], "temp_max": 28.0, "temp_min": 21.0, "rain_prob": 15, "condition": "Partly Cloudy", "weather_code": 1, "precip_sum": 0.1},
                {"date": (today_dt + timedelta(days=5)).strftime("%Y-%m-%d"), "day_name": day_names[(today_dt + timedelta(days=5)).weekday()], "temp_max": 30.5, "temp_min": 23.0, "rain_prob": 20, "condition": "Sunny", "weather_code": 0, "precip_sum": 0.0},
                {"date": (today_dt + timedelta(days=6)).strftime("%Y-%m-%d"), "day_name": day_names[(today_dt + timedelta(days=6)).weekday()], "temp_max": 27.5, "temp_min": 20.5, "rain_prob": 40, "condition": "Showers", "weather_code": 80, "precip_sum": 1.2},
            ]
            default_payload = json.dumps({
                "location_name": "Lucknow Farm Zone",
                "latitude": 26.8467,
                "longitude": 80.9462,
                "is_live": False,
                "cached_at": now_iso,
                "days": default_days
            })
            cursor.execute("""
                INSERT INTO weather_cache (id, fetched_at, forecast_json)
                VALUES (1, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    fetched_at = excluded.fetched_at,
                    forecast_json = excluded.forecast_json
            """, (now_iso, default_payload))
        
        conn.commit()

# ----------------------------------------------------------------------
# TELEMETRY METHODS
# ----------------------------------------------------------------------

def log_telemetry(
    zone_id: str,
    soil_moisture: float,
    soil_temp: float,
    ambient_temp: float,
    ambient_humidity: float,
    pump_active: int = 0,
    light_lux: float = 0.0,
    barometric_pressure: float = 1013.25,
    node_id: str = "EDGE_STATION_PI",
    recorded_at: Optional[str] = None,
    rain_detected: int = 0
) -> int:
    """Logs a new sensor reading into the local offline SQLite buffer."""
    if not recorded_at:
        recorded_at = datetime.now(timezone.utc).isoformat()
        
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO telemetry (
                zone_id, node_id, recorded_at, soil_moisture, soil_temp,
                ambient_temp, ambient_humidity, light_lux, barometric_pressure,
                pump_active, rain_detected, synced_to_cloud
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            zone_id, node_id, recorded_at,
            round(soil_moisture, 2), round(soil_temp, 2),
            round(ambient_temp, 2), round(ambient_humidity, 2),
            round(light_lux, 2), round(barometric_pressure, 2),
            1 if pump_active else 0,
            1 if rain_detected else 0
        ))
        conn.commit()
        return cursor.lastrowid

def get_latest_telemetry(zone_id: Optional[str] = None) -> Dict[str, Any]:
    """Returns the latest reading for a specific zone or dictionary for all known zones."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if zone_id:
            cursor.execute("""
                SELECT * FROM telemetry 
                WHERE zone_id = ? 
                ORDER BY id DESC LIMIT 1
            """, (zone_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        else:
            result = {}
            for z in ["ZONE_A", "ZONE_B"]:
                cursor.execute("""
                    SELECT * FROM telemetry 
                    WHERE zone_id = ? 
                    ORDER BY id DESC LIMIT 1
                """, (z,))
                row = cursor.fetchone()
                result[z] = dict(row) if row else None
            return result

def get_24h_history(zone_id: Optional[str] = "ZONE_A", limit: int = 60) -> List[Dict[str, Any]]:
    """
    Returns historical records from the last 24 hours (or recent records up to limit)
    ordered chronologically (ascending) for time-series charts.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        if zone_id and zone_id in ["ZONE_A", "ZONE_B"]:
            cursor.execute("""
                SELECT * FROM telemetry 
                WHERE zone_id = ? AND recorded_at >= ?
                ORDER BY id DESC LIMIT ?
            """, (zone_id, cutoff, limit))
        else:
            cursor.execute("""
                SELECT * FROM telemetry 
                WHERE recorded_at >= ?
                ORDER BY id DESC LIMIT ?
            """, (cutoff, limit))
        rows = cursor.fetchall()
        
        # Fallback if brand new database with fewer records in window
        if not rows:
            if zone_id and zone_id in ["ZONE_A", "ZONE_B"]:
                cursor.execute("""
                    SELECT * FROM telemetry 
                    WHERE zone_id = ? 
                    ORDER BY id DESC LIMIT ?
                """, (zone_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM telemetry 
                    ORDER BY id DESC LIMIT ?
                """, (limit,))
            rows = cursor.fetchall()
            
        return [dict(r) for r in reversed(rows)]

def get_unsynced_telemetry(limit: int = 20) -> List[Dict[str, Any]]:
    """Fetches a batch of un-synced telemetry records (synced_to_cloud = 0)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM telemetry 
            WHERE synced_to_cloud = 0 
            ORDER BY id ASC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def mark_telemetry_synced(ids: List[int]) -> int:
    """Marks a list of record IDs as synced_to_cloud = 1."""
    if not ids:
        return 0
    with get_connection() as conn:
        cursor = conn.cursor()
        placeholders = ",".join("?" for _ in ids)
        cursor.execute(f"""
            UPDATE telemetry 
            SET synced_to_cloud = 1 
            WHERE id IN ({placeholders})
        """, ids)
        conn.commit()
        return cursor.rowcount

def prune_synced_telemetry(retention_hours: int = 24) -> int:
    """
    24-Hour Rolling Local Storage Pruning:
    Deletes all records where synced_to_cloud == 1 AND recorded_at < (now - retention_hours).
    Preserves offline data locally for 24 hours while preventing SD card overflow.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=retention_hours)).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM telemetry 
            WHERE synced_to_cloud = 1 AND recorded_at < ?
        """, (cutoff,))
        conn.commit()
        return cursor.rowcount

# ----------------------------------------------------------------------
# ACTUATOR METHODS
# ----------------------------------------------------------------------

def get_actuator_state(target: str) -> int:
    """Returns the state of an actuator (0 for OFF, 1 for ON)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT state FROM actuators WHERE target = ?", (target,))
        row = cursor.fetchone()
        return row["state"] if row else 0

def get_all_actuators() -> Dict[str, int]:
    """Returns a dictionary of all actuator targets and their current states."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT target, state, updated_at FROM actuators")
        rows = cursor.fetchall()
        return {r["target"]: r["state"] for r in rows}

def set_actuator_state(target: str, state: int) -> bool:
    """Updates an actuator's state in SQLite with timestamp."""
    normalized_state = 1 if state else 0
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO actuators (target, state, updated_at) 
            VALUES (?, ?, ?)
            ON CONFLICT(target) DO UPDATE SET 
                state = excluded.state,
                updated_at = excluded.updated_at
        """, (target, normalized_state, now_iso))
        conn.commit()
        return True

# Aliases for Tier 1 display GUI
get_latest_zone_data = get_latest_telemetry
update_actuator_state = set_actuator_state

def toggle_actuator_state(target: str) -> int:
    """Toggles the state of an actuator and returns the new state."""
    current = get_actuator_state(target)
    new_state = 0 if current else 1
    set_actuator_state(target, new_state)
    return new_state

# ----------------------------------------------------------------------
# ROVER METHODS
# ----------------------------------------------------------------------

def get_rover_state() -> Dict[str, Any]:
    """Returns the current field scout rover telemetry."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rover_state WHERE id = 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {
            "id": 1,
            "heading": "NW (312°)",
            "speed": 0.0,
            "battery": 84,
            "last_action": "STOP",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

def update_rover_battery(battery_percent: int) -> bool:
    """Updates the rover battery percentage in SQLite."""
    now_iso = datetime.now(timezone.utc).isoformat()
    pct = max(0, min(100, int(battery_percent)))
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rover_state (id, heading, speed, battery, last_action, updated_at)
            VALUES (1, 'NW (312°)', 0.0, ?, 'STOP', ?)
            ON CONFLICT(id) DO UPDATE SET
                battery = excluded.battery,
                updated_at = excluded.updated_at
        """, (pct, now_iso))
        conn.commit()
    return True

def update_rover_command(action: str) -> Dict[str, Any]:
    """Updates rover movement command and simulates speed/heading changes."""
    action_clean = action.upper().strip()
    now_iso = datetime.now(timezone.utc).isoformat()
    
    speed_map = {
        "MOVE_FORWARD": 0.6,
        "MOVE_BACKWARD": 0.4,
        "MOVE_LEFT": 0.3,
        "MOVE_RIGHT": 0.3,
        "AUTO_ON": 0.6,
        "AUTO_OFF": 0.0,
        "STOP": 0.0
    }
    heading_map = {
        "MOVE_FORWARD": "N (000°)",
        "MOVE_BACKWARD": "S (180°)",
        "MOVE_LEFT": "W (270°)",
        "MOVE_RIGHT": "E (090°)",
        "AUTO_ON": "N (000°)",
        "AUTO_OFF": "NW (312°)",
        "STOP": "NW (312°)"
    }
    
    speed = speed_map.get(action_clean, 0.0)
    heading = heading_map.get(action_clean, "NW (312°)")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rover_state (id, heading, speed, battery, last_action, updated_at)
            VALUES (1, ?, ?, 84, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                heading = excluded.heading,
                speed = excluded.speed,
                last_action = excluded.last_action,
                updated_at = excluded.updated_at
        """, (heading, speed, action_clean, now_iso))
        conn.commit()
        
    return get_rover_state()

# ----------------------------------------------------------------------
# WEATHER CACHE & FARM LOCATION METHODS
# ----------------------------------------------------------------------

def get_farm_location() -> Dict[str, Any]:
    """Returns the current farm location metadata (name, lat, lon)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM farm_settings")
        rows = cursor.fetchall()
        settings = {r["key"]: r["value"] for r in rows}
        return {
            "location_name": settings.get("location_name", "Lucknow Farm Zone"),
            "latitude": float(settings.get("latitude", "26.8467")),
            "longitude": float(settings.get("longitude", "80.9462")),
        }

def update_farm_location(location_name: str, latitude: float, longitude: float) -> Dict[str, Any]:
    """Updates farm location in SQLite and returns new settings."""
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        for k, v in [("location_name", location_name.strip()), ("latitude", str(latitude)), ("longitude", str(longitude))]:
            cursor.execute("""
                INSERT INTO farm_settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
            """, (k, v, now_iso))
        conn.commit()
    return get_farm_location()

def get_cached_weather() -> Optional[Dict[str, Any]]:
    """Returns the cached 7-day weather forecast dictionary with age & location metadata."""
    loc = get_farm_location()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fetched_at, forecast_json FROM weather_cache WHERE id = 1")
        row = cursor.fetchone()
        if row and row["forecast_json"]:
            try:
                data = json.loads(row["forecast_json"])
                fetched_time = datetime.fromisoformat(row["fetched_at"])
                if fetched_time.tzinfo is None:
                    fetched_time = fetched_time.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                age_minutes = round(max(0.0, (now - fetched_time).total_seconds() / 60.0), 1)
                is_stale = age_minutes > 60.0

                return {
                    "fetched_at": row["fetched_at"],
                    "age_minutes": age_minutes,
                    "is_stale": is_stale,
                    "is_live": bool(data.get("is_live", False)),
                    "location": {
                        "location_name": data.get("location_name", loc["location_name"]),
                        "latitude": data.get("latitude", loc["latitude"]),
                        "longitude": data.get("longitude", loc["longitude"])
                    },
                    "forecast": data
                }
            except Exception:
                return None
        return None

def save_cached_weather(forecast_data: Dict[str, Any], is_live: bool = True) -> bool:
    """Saves a 7-day weather forecast JSON to SQLite."""
    now_iso = datetime.now(timezone.utc).isoformat()
    loc = get_farm_location()
    if "location_name" not in forecast_data:
        forecast_data["location_name"] = loc["location_name"]
    if "latitude" not in forecast_data:
        forecast_data["latitude"] = loc["latitude"]
    if "longitude" not in forecast_data:
        forecast_data["longitude"] = loc["longitude"]
    forecast_data["is_live"] = is_live
    forecast_data["cached_at"] = now_iso

    json_str = json.dumps(forecast_data)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO weather_cache (id, fetched_at, forecast_json)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                fetched_at = excluded.fetched_at,
                forecast_json = excluded.forecast_json
        """, (now_iso, json_str))
        conn.commit()
        return True

def is_weather_stale(max_age_minutes: int = 30) -> bool:
    """Checks if the weather cache is missing or older than max_age_minutes."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fetched_at FROM weather_cache WHERE id = 1")
        row = cursor.fetchone()
        if not row or not row["fetched_at"]:
            return True
        try:
            fetched_time = datetime.fromisoformat(row["fetched_at"])
            # Handle tz-aware vs naive
            if fetched_time.tzinfo is None:
                fetched_time = fetched_time.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            age_min = (now - fetched_time).total_seconds() / 60.0
            return age_min >= max_age_minutes
        except Exception:
            return True

# ----------------------------------------------------------------------
# STATS
# ----------------------------------------------------------------------

def get_edge_stats() -> Dict[str, Any]:
    """Returns high-level statistics about the local SQLite edge buffer (telemetry + AI)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM telemetry")
        total_records = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) as unsynced FROM telemetry WHERE synced_to_cloud = 0")
        unsynced_records = cursor.fetchone()["unsynced"]
        
        cursor.execute("SELECT recorded_at FROM telemetry WHERE synced_to_cloud = 1 ORDER BY id DESC LIMIT 1")
        last_synced_row = cursor.fetchone()
        last_synced_at = last_synced_row["recorded_at"] if last_synced_row else None
        
        cursor.execute("SELECT COUNT(*) as total_ai FROM ai_detections")
        total_ai = cursor.fetchone()["total_ai"]
        
        cursor.execute("SELECT COUNT(*) as unsynced_ai FROM ai_detections WHERE synced_to_cloud = 0")
        unsynced_ai = cursor.fetchone()["unsynced_ai"]
        
        return {
            "total_records": total_records,
            "unsynced_records": unsynced_records,
            "synced_records": total_records - unsynced_records,
            "last_synced_at": last_synced_at,
            "total_ai_detections": total_ai,
            "unsynced_ai_detections": unsynced_ai
        }

# ----------------------------------------------------------------------
# AI DETECTIONS METHODS (4 ONNX Vision Models)
# ----------------------------------------------------------------------

def log_ai_detection(
    node_id: str,
    model_name: str,
    detection_label: str,
    confidence: float,
    image_path: Optional[str] = None,
    metadata_json: Optional[str] = None,
    created_at: Optional[str] = None
) -> int:
    """Logs a single AI inference detection into SQLite."""
    if not created_at:
        created_at = datetime.now(timezone.utc).isoformat()
        
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ai_detections (
                node_id, model_name, detection_label, confidence,
                image_path, metadata_json, created_at, synced_to_cloud
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            node_id,
            model_name.lower().strip(),
            detection_label.strip(),
            round(confidence, 3),
            image_path,
            metadata_json,
            created_at
        ))
        conn.commit()
        return cursor.lastrowid

def log_ai_inference_bundle(
    node_id: str,
    results: Dict[str, Any],
    image_filename: Optional[str] = None,
    created_at: Optional[str] = None
) -> List[int]:
    """
    Ingests and logs a complete 4-model inference dictionary from dashboard-ai-modals:
    results = { 'disease': [...], 'pest': [...], 'nutrition': [...], 'stage': [...] }
    """
    if not created_at:
        created_at = datetime.now(timezone.utc).isoformat()
        
    inserted_ids = []
    
    # Process each model category
    for model_name in ["disease", "pest", "nutrition", "stage"]:
        detections = results.get(model_name, [])
        if detections:
            for det in detections:
                label = det.get("name", "Unknown")
                conf = det.get("confidence", 0.0)
                meta = json.dumps({
                    "bbox": det.get("bbox", []),
                    "class_id": det.get("class_id", -1)
                })
                row_id = log_ai_detection(
                    node_id=node_id,
                    model_name=model_name,
                    detection_label=label,
                    confidence=conf,
                    image_path=image_filename,
                    metadata_json=meta,
                    created_at=created_at
                )
                inserted_ids.append(row_id)
        else:
            # If healthy / no disease or pest detected, record baseline status
            if model_name in ["disease", "pest"]:
                default_label = "Healthy / No Disease" if model_name == "disease" else "No Pests Detected"
                row_id = log_ai_detection(
                    node_id=node_id,
                    model_name=model_name,
                    detection_label=default_label,
                    confidence=0.99,
                    image_path=image_filename,
                    metadata_json=json.dumps({"status": "CLEAR"}),
                    created_at=created_at
                )
                inserted_ids.append(row_id)
                
    return inserted_ids

def get_latest_ai_detections(node_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Returns the most recent AI detection events ordered newest first."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if node_id:
            cursor.execute("""
                SELECT * FROM ai_detections 
                WHERE node_id = ? 
                ORDER BY id DESC LIMIT ?
            """, (node_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM ai_detections 
                ORDER BY id DESC LIMIT ?
            """, (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def get_agronomic_treatment(category: str, label: str) -> Dict[str, Any]:
    """Provides professional AI Agronomist diagnostic treatments and action triggers."""
    l = label.lower()
    
    if category == "disease":
        if "healthy" in l or "no disease" in l or "none" in l:
            return {
                "treatment": "Healthy plant foliage. No fungal or bacterial pathogen observed.",
                "action": None,
                "action_label": None,
                "severity": "nominal"
            }
        elif "septoria" in l:
            return {
                "treatment": "Foliar bio-fungicide (Bacillus subtilis) spray recommended. Prune lower infected leaves to prevent soil-splash spore spread.",
                "action": "PUMP_ZONE_B",
                "action_label": "Start Misting Spray",
                "severity": "warning"
            }
        elif "early blight" in l or "alternaria" in l:
            return {
                "treatment": "Apply copper hydroxide / chlorothalonil fungicide spray immediately. Sanitize tools and maintain drip irrigation to keep canopy dry.",
                "action": "PUMP_ZONE_B",
                "action_label": "Start Misting Spray",
                "severity": "critical"
            }
        elif "late blight" in l or "phytophthora" in l:
            return {
                "treatment": "High-risk pathogen! Apply systemic fungicide (Metalaxyl + Mancozeb). Suspend overhead misting and remove heavily infected vines.",
                "action": "PUMP_ZONE_B",
                "action_label": "Start Fungicide Spray",
                "severity": "critical"
            }
        elif "bacterial spot" in l or "xanthomonas" in l:
            return {
                "treatment": "Apply fixed copper + Mancozeb bactericide spray. Avoid handling wet foliage to limit bacterial dissemination.",
                "action": "PUMP_ZONE_B",
                "action_label": "Start Bactericide Spray",
                "severity": "critical"
            }
        elif "powdery mildew" in l:
            return {
                "treatment": "Apply potassium bicarbonate or wettable sulfur spray. Increase ventilation schedule (06:00 - 19:00).",
                "action": "PUMP_ZONE_B",
                "action_label": "Start Sulfur Spray",
                "severity": "warning"
            }
        elif "leaf mold" in l:
            return {
                "treatment": "Reduce relative humidity below 80%. Apply copper-based fungicide and increase exhaust fan ventilation.",
                "action": "PUMP_ZONE_B",
                "action_label": "Start Foliar Treatment",
                "severity": "warning"
            }
        elif "virus" in l or "curl" in l:
            return {
                "treatment": "Viral infection detected. Target insect vectors (whiteflies/aphids) immediately and rogue infected plants.",
                "action": "PUMP_ZONE_B",
                "action_label": "Target Vectors",
                "severity": "critical"
            }
        else:
            return {
                "treatment": f"Foliar pathogen observed ({label}). Spray broad-spectrum organic bio-fungicide and inspect plant cluster.",
                "action": "PUMP_ZONE_B",
                "action_label": "Start Misting Spray",
                "severity": "warning"
            }

    elif category == "pest":
        if "no pest" in l or "none" in l or "healthy" in l:
            return {
                "treatment": "No active insect pests detected on crop foliage.",
                "action": None,
                "action_label": None,
                "severity": "nominal"
            }
        elif "aphid" in l:
            return {
                "treatment": "Scouted colony on leaf undersides. Apply 0.5% cold-pressed neem oil foliar spray or release predatory ladybird beetles.",
                "action": "PUMP_ZONE_B",
                "action_label": "Apply Neem Spray",
                "severity": "warning"
            }
        elif "mite" in l:
            return {
                "treatment": "Spider mites detected in dry canopy. Initiate canopy misting (Pump B) to raise humidity and apply wettable sulfur.",
                "action": "PUMP_ZONE_B",
                "action_label": "Start Canopy Misting",
                "severity": "warning"
            }
        elif "whitefly" in l:
            return {
                "treatment": "Whitefly swarm detected. Deploy yellow sticky cards along row and apply Beauveria bassiana bio-insecticide.",
                "action": "PUMP_ZONE_B",
                "action_label": "Apply Bio-Pesticide",
                "severity": "warning"
            }
        elif "caterpillar" in l or "worm" in l or "borer" in l or "armyworm" in l:
            return {
                "treatment": "Foliar chewers detected. Apply Bacillus thuringiensis (Bt) kurstaki spray during evening hours.",
                "action": "PUMP_ZONE_B",
                "action_label": "Apply Bt Spray",
                "severity": "critical"
            }
        else:
            return {
                "treatment": f"Pest activity identified ({label}). Apply biological neem oil spray and install insect monitoring cards.",
                "action": "PUMP_ZONE_B",
                "action_label": "Apply Pest Control",
                "severity": "warning"
            }

    elif category == "nutrition":
        if "balanced" in l or "optimal" in l or "healthy" in l:
            return {
                "treatment": "Foliar nutrient profile balanced (N-P-K nominal).",
                "action": None,
                "action_label": None,
                "severity": "nominal"
            }
        elif "nitrogen" in l or "n deficiency" in l:
            return {
                "treatment": "Lower foliage chlorosis (yellowing) detected. Inject Calcium Nitrate (19:19:19) solution via Drip Line A.",
                "action": "PUMP_ZONE_A",
                "action_label": "Start Drip Fertigation",
                "severity": "advisory"
            }
        elif "potassium" in l or "k deficiency" in l:
            return {
                "treatment": "Leaf margin scorch detected. Apply 1% Potassium Nitrate (KNO3) foliar spray and balance soil pH.",
                "action": "PUMP_ZONE_A",
                "action_label": "Inject Potassium",
                "severity": "advisory"
            }
        elif "iron" in l or "chlorosis" in l:
            return {
                "treatment": "Interveinal chlorosis observed. Drench soil with Chelated Iron (Fe-EDDHA) and check root zone alkalinity.",
                "action": "PUMP_ZONE_A",
                "action_label": "Drench Iron Chelate",
                "severity": "advisory"
            }
        elif "phosphorus" in l:
            return {
                "treatment": "Purpling of stems/undersides. Inject Monoammonium Phosphate (MAP) fertigation.",
                "action": "PUMP_ZONE_A",
                "action_label": "Adjust Phosphate",
                "severity": "advisory"
            }
        else:
            return {
                "treatment": f"Nutrient imbalance detected ({label}). Adjust N-P-K injector dosage in fertigation header.",
                "action": "PUMP_ZONE_A",
                "action_label": "Adjust Fertigation",
                "severity": "advisory"
            }
            
    return {
        "treatment": f"Plant health observation: {label}.",
        "action": None,
        "action_label": None,
        "severity": "nominal"
    }


def get_latest_ai_summary(node_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns the latest diagnosed state for each of the 4 models:
    { 'disease': {...}, 'pest': {...}, 'nutrition': {...}, 'stage': {...}, 'alerts': [...] }
    """
    summary = {
        "disease": None,
        "pest": None,
        "nutrition": None,
        "stage": None,
        "alerts": []
    }
    
    with get_connection() as conn:
        cursor = conn.cursor()
        for model in ["disease", "pest", "nutrition", "stage"]:
            row = None
            if node_id:
                n_up = node_id.upper()
                if n_up in ["NODE_01", "ZONE_A", "FIELD_A"]:
                    node_list = ("NODE_01", "ZONE_A", "PHONE_ZONE_A", "ROVER_PHONE_01", "ROVER_MANUAL_CAM", "ROVER_FIELD_SCOUT", "EDGE_STATION_PI")
                    placeholders = ",".join("?" for _ in node_list)
                    cursor.execute(f"""
                        SELECT * FROM ai_detections 
                        WHERE model_name = ? AND node_id IN ({placeholders})
                        ORDER BY id DESC LIMIT 1
                    """, (model, *node_list))
                    row = cursor.fetchone()
                elif n_up in ["NODE_02", "ZONE_B", "FIELD_B"]:
                    node_list = ("NODE_02", "ZONE_B", "PHONE_ZONE_B", "SLAVE_01")
                    placeholders = ",".join("?" for _ in node_list)
                    cursor.execute(f"""
                        SELECT * FROM ai_detections 
                        WHERE model_name = ? AND node_id IN ({placeholders})
                        ORDER BY id DESC LIMIT 1
                    """, (model, *node_list))
                    row = cursor.fetchone()
                else:
                    cursor.execute("""
                        SELECT * FROM ai_detections 
                        WHERE model_name = ? AND node_id = ?
                        ORDER BY id DESC LIMIT 1
                    """, (model, node_id))
                    row = cursor.fetchone()

            # Fallback to latest farm overall detection if node-specific is missing
            if not row:
                cursor.execute("""
                    SELECT * FROM ai_detections 
                    WHERE model_name = ?
                    ORDER BY id DESC LIMIT 1
                """, (model,))
                row = cursor.fetchone()

            if row:
                d = dict(row)
                label = d.get("detection_label", "Unknown")
                conf = d.get("confidence", 0.0)
                n_id = d.get("node_id", "ROVER_SCOUT")
                label_lower = label.lower()
                
                # Attach agronomist treatment plan
                rx = get_agronomic_treatment(model, label)
                d["treatment"] = rx["treatment"]
                d["action"] = rx["action"]
                d["action_label"] = rx["action_label"]
                d["severity"] = rx["severity"]
                
                summary[model] = d
                
                # Check for actionable alerts
                if model == "disease" and "healthy" not in label_lower and "no disease" not in label_lower and conf >= 0.35:
                    summary["alerts"].append({
                        "type": "DISEASE",
                        "severity": rx["severity"],
                        "icon": "🦠",
                        "title": f"Plant Infection: {label}",
                        "label": label,
                        "confidence": conf,
                        "treatment": rx["treatment"],
                        "action": rx["action"],
                        "action_label": rx["action_label"],
                        "node_id": n_id,
                        "created_at": d.get("created_at")
                    })
                elif model == "pest" and "no pest" not in label_lower and "none" not in label_lower and "healthy" not in label_lower and conf >= 0.30:
                    summary["alerts"].append({
                        "type": "PEST",
                        "severity": rx["severity"],
                        "icon": "🐛",
                        "title": f"Pest Infestation: {label}",
                        "label": label,
                        "confidence": conf,
                        "treatment": rx["treatment"],
                        "action": rx["action"],
                        "action_label": rx["action_label"],
                        "node_id": n_id,
                        "created_at": d.get("created_at")
                    })
                elif model == "nutrition" and "healthy" not in label_lower and "optimal" not in label_lower and "balanced" not in label_lower and conf >= 0.40:
                    summary["alerts"].append({
                        "type": "NUTRITION",
                        "severity": rx["severity"],
                        "icon": "🧪",
                        "title": f"Nutrient Stress: {label}",
                        "label": label,
                        "confidence": conf,
                        "treatment": rx["treatment"],
                        "action": rx["action"],
                        "action_label": rx["action_label"],
                        "node_id": n_id,
                        "created_at": d.get("created_at")
                    })

    return summary


def get_unsynced_ai_detections(limit: int = 20) -> List[Dict[str, Any]]:
    """Fetches batch of unsynced AI detections (synced_to_cloud = 0)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM ai_detections 
            WHERE synced_to_cloud = 0 
            ORDER BY id ASC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def mark_ai_detections_synced(ids: List[int]) -> int:
    """Marks AI detection record IDs as synced_to_cloud = 1."""
    if not ids:
        return 0
    with get_connection() as conn:
        cursor = conn.cursor()
        placeholders = ",".join("?" for _ in ids)
        cursor.execute(f"""
            UPDATE ai_detections 
            SET synced_to_cloud = 1 
            WHERE id IN ({placeholders})
        """, ids)
        conn.commit()
        return cursor.rowcount

def prune_synced_ai_detections(retention_hours: int = 24) -> int:
    """Deletes synced AI records older than retention_hours to preserve disk storage."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=retention_hours)).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM ai_detections 
            WHERE synced_to_cloud = 1 AND created_at < ?
        """, (cutoff,))
        conn.commit()
        return cursor.rowcount

