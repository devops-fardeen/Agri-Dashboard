import time
import os
import requests
import threading
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
import database

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [SYNC_WORKER] %(message)s")
logger = logging.getLogger("sync_worker")

CLOUD_BASE_URL = os.getenv("CLOUD_BASE_URL", "http://localhost:3000")
CLOUD_SYNC_URL = os.getenv("CLOUD_SYNC_URL", f"{CLOUD_BASE_URL}/api/telemetry/sync")
CLOUD_AI_SYNC_URL = os.getenv("CLOUD_AI_SYNC_URL", f"{CLOUD_BASE_URL}/api/ai/sync")
CLOUD_COMMANDS_URL = os.getenv("CLOUD_COMMANDS_URL", f"{CLOUD_BASE_URL}/api/commands")
EDGE_SYNC_KEY = os.getenv("EDGE_SYNC_KEY", "dashboard@agri1")
BATCH_SIZE = int(os.getenv("SYNC_BATCH_SIZE", "20"))
SYNC_INTERVAL = float(os.getenv("SYNC_INTERVAL_SEC", "5.0"))
WEATHER_LATITUDE = float(os.getenv("FARM_LATITUDE", "26.8467"))
WEATHER_LONGITUDE = float(os.getenv("FARM_LONGITUDE", "80.9462"))

class CloudSyncWorker:
    """
    Bidirectional synchronization worker:
    1. Edge Push: Batches and pushes local SQLite telemetry, AI detections, and physical actuator states to Tier 3 Cloud.
    2. Cloud Pull: Drains pending commands from Tier 3 Cloud, executes them locally in SQLite, and acknowledges back.
    3. Storage Management: Performs 24-hour rolling local storage pruning on synced records.
    4. Offline Weather Cache: Fetches and caches 7-day Open-Meteo weather forecasts.
    """
    def __init__(
        self,
        cloud_url: str = CLOUD_SYNC_URL,
        ai_sync_url: str = CLOUD_AI_SYNC_URL,
        commands_url: str = CLOUD_COMMANDS_URL,
        sync_key: str = EDGE_SYNC_KEY
    ):
        self.cloud_url = cloud_url
        self.ai_sync_url = ai_sync_url
        self.commands_url = commands_url
        self.sync_key = sync_key
        self.running = False
        self._thread = None
        self.last_sync_status = "INITIALIZING"
        self.last_sync_time = None
        self.consecutive_failures = 0

    def format_payload(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Converts SQLite rows into the MongoDB document schema expected by Tier 3."""
        payload = []
        for r in records:
            payload.append({
                "zoneId": r["zone_id"],
                "nodeId": r.get("node_id", "EDGE_STATION_PI"),
                "recordedAt": r["recorded_at"],
                "telemetry": {
                    "soilMoisture": r["soil_moisture"],
                    "soilTemperature": r["soil_temp"],
                    "ambientTemp": r["ambient_temp"],
                    "ambientHumidity": r["ambient_humidity"],
                    "lightLux": r.get("light_lux", 0.0),
                    "barometricPressure": r.get("barometric_pressure", 1013.25),
                    "rainDetected": bool(r.get("rain_detected", 0)),
                    "rainStatus": "HEAVY_RAIN" if bool(r.get("rain_detected", 0)) else "NO_RAIN"
                },
                "actuatorState": {
                    "pumpActive": bool(r.get("pump_active", 0)),
                    "lastIrrigationDurationSec": 0,
                    "triggerSource": "MANUAL"
                },
                "alerts": []
            })
        return payload

    def poll_and_execute_cloud_commands(self) -> int:
        """
        Cloud Pull (Cloud -> Local):
        Fetches pending commands from Tier 3 Next.js Cloud, applies them to SQLite actuators/rover,
        and acknowledges execution via PATCH /api/commands.
        """
        headers = {
            "x-edge-sync-key": self.sync_key
        }
        try:
            res = requests.get(self.commands_url, headers=headers, timeout=4.0)
            if res.status_code == 200:
                data = res.json()
                commands = data.get("commands", [])
                executed_count = 0

                for cmd in commands:
                    cmd_id = cmd.get("_id")
                    target = cmd.get("target", "").upper().strip()
                    action = cmd.get("action", "").upper().strip()

                    logger.info(f"Received Cloud Command: {target} -> {action} (ID: {cmd_id})")

                    # Execute Pump Commands
                    if target in ["PUMP_ZONE_A", "PUMP_ZONE_B", "ZONE_A", "ZONE_B"]:
                        normalized_target = "PUMP_ZONE_A" if "A" in target else "PUMP_ZONE_B"
                        new_state = 1 if action in ["ON", "1", "START", "RUNNING"] else 0
                        
                        database.set_actuator_state(normalized_target, new_state)
                        logger.info(f"Local Actuator Updated: {normalized_target} = {'ON' if new_state else 'OFF'}")

                    # Execute Rover Commands
                    elif target == "ROVER":
                        database.update_rover_command(action)
                        logger.info(f"Local Rover Command Updated: {action}")

                    # Acknowledge execution back to Cloud
                    ack_res = requests.patch(
                        self.commands_url,
                        json={"id": cmd_id, "status": "EXECUTED"},
                        headers={"Content-Type": "application/json", "x-edge-sync-key": self.sync_key},
                        timeout=4.0
                    )
                    if ack_res.status_code == 200:
                        executed_count += 1
                        logger.info(f"Cloud Command Acknowledged: ID {cmd_id} marked EXECUTED.")

                return executed_count
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass
        except Exception as e:
            logger.error(f"Error polling cloud commands: {e}")
        return 0

    def sync_batch(self) -> int:
        """
        Edge Push (Local -> Cloud):
        Pulls one batch of unsynced records from SQLite and transmits to Tier 3 Cloud.
        On HTTP 200, marks records as synced and runs 24h storage pruning.
        """
        unsynced = database.get_unsynced_telemetry(limit=BATCH_SIZE)
        if not unsynced:
            return 0
            
        ids = [r["id"] for r in unsynced]
        payload = self.format_payload(unsynced)
        
        headers = {
            "Content-Type": "application/json",
            "x-edge-sync-key": self.sync_key
        }
        
        try:
            response = requests.post(
                self.cloud_url,
                json=payload,
                headers=headers,
                timeout=6.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    marked = database.mark_telemetry_synced(ids)
                    self.last_sync_status = "ONLINE_SYNCED"
                    self.last_sync_time = time.time()
                    self.consecutive_failures = 0
                    logger.info(f"Synced batch of {marked} telemetry records to Tier 3 Cloud.")
                    
                    # 24-Hour Rolling Storage Prune
                    pruned_count = database.prune_synced_telemetry(retention_hours=24)
                    if pruned_count > 0:
                        logger.info(f"24-Hour Prune: Purged {pruned_count} synced records older than 24h.")
                        
                    return marked
                else:
                    logger.warning(f"Cloud rejected batch: {data.get('error')}")
                    self.last_sync_status = f"ERROR: {data.get('error')}"
            else:
                logger.warning(f"Cloud responded with HTTP {response.status_code}: {response.text}")
                self.last_sync_status = f"HTTP_{response.status_code}"
                
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            self.consecutive_failures += 1
            self.last_sync_status = "OFFLINE_BUFFERING"
            stats = database.get_edge_stats()
            if self.consecutive_failures % 4 == 1:
                logger.info(
                    f"Tier 3 Cloud unreachable ({self.cloud_url}). "
                    f"Local buffer holding {stats['unsynced_records']} un-synced records safely in SQLite."
                )
        except Exception as e:
            self.last_sync_status = f"EXCEPTION: {str(e)}"
            logger.error(f"Unexpected sync worker exception: {e}")
            
        return 0

    def sync_ai_batch(self) -> int:
        """
        Edge Push for AI Vision Detections (Local SQLite -> Cloud MongoDB Atlas):
        Pulls batch of unsynced AI detections from SQLite and posts to Tier 3 /api/ai/sync.
        """
        unsynced = database.get_unsynced_ai_detections(limit=BATCH_SIZE)
        if not unsynced:
            return 0
            
        ids = [r["id"] for r in unsynced]
        payload = []
        for r in unsynced:
            meta = {}
            if r.get("metadata_json"):
                try:
                    meta = json.loads(r["metadata_json"])
                except Exception:
                    meta = {}
            payload.append({
                "nodeId": r["node_id"],
                "modelName": r["model_name"],
                "detectionLabel": r["detection_label"],
                "confidence": r["confidence"],
                "imagePath": r.get("image_path"),
                "metadata": meta,
                "recordedAt": r["created_at"]
            })
            
        headers = {
            "Content-Type": "application/json",
            "x-edge-sync-key": self.sync_key
        }
        
        try:
            response = requests.post(
                self.ai_sync_url,
                json=payload,
                headers=headers,
                timeout=6.0
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    marked = database.mark_ai_detections_synced(ids)
                    logger.info(f"Synced batch of {marked} AI detection events to Tier 3 Cloud.")
                    database.prune_synced_ai_detections(retention_hours=24)
                    return marked
        except Exception as e:
            logger.debug(f"AI sync offline/buffering: {e}")
        return 0

    def check_and_update_weather_cache(self):
        """7-Day Offline Weather Cache updater."""
        if not database.is_weather_stale(max_age_hours=24):
            return

        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={WEATHER_LATITUDE}&longitude={WEATHER_LONGITUDE}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code"
            f"&timezone=auto"
        )
        try:
            res = requests.get(url, timeout=5.0)
            if res.status_code == 200:
                data = res.json()
                daily = data.get("daily", {})
                dates = daily.get("time", [])
                max_temps = daily.get("temperature_2m_max", [])
                min_temps = daily.get("temperature_2m_min", [])
                precip_probs = daily.get("precipitation_probability_max", [])
                weather_codes = daily.get("weather_code", [])

                formatted_days = []
                for i in range(min(len(dates), 7)):
                    wcode = weather_codes[i] if i < len(weather_codes) else 0
                    condition = self._interpret_wmo_code(wcode)
                    
                    formatted_days.append({
                        "date": dates[i],
                        "day_name": datetime.fromisoformat(dates[i]).strftime("%a"),
                        "temp_max": max_temps[i] if i < len(max_temps) else 30.0,
                        "temp_min": min_temps[i] if i < len(min_temps) else 20.0,
                        "rain_prob": precip_probs[i] if i < len(precip_probs) else 0,
                        "weather_code": wcode,
                        "condition": condition
                    })

                forecast_payload = {
                    "latitude": WEATHER_LATITUDE,
                    "longitude": WEATHER_LONGITUDE,
                    "cached_at": datetime.now(timezone.utc).isoformat(),
                    "days": formatted_days
                }
                database.save_cached_weather(forecast_payload)
                logger.info(f"Updated 7-day offline weather cache ({len(formatted_days)} days stored in SQLite).")
        except Exception as e:
            logger.debug(f"Weather cache refresh skipped: {e}")

    def _interpret_wmo_code(self, code: int) -> str:
        if code == 0:
            return "Clear Sky"
        elif code in [1, 2, 3]:
            return "Partly Cloudy"
        elif code in [45, 48]:
            return "Foggy"
        elif code in [51, 53, 55]:
            return "Drizzle"
        elif code in [61, 63, 65]:
            return "Rain"
        elif code in [80, 81, 82]:
            return "Showers"
        elif code in [95, 96, 99]:
            return "Thunderstorm"
        return "Fair"

    def start_loop(self, interval_seconds: float = SYNC_INTERVAL):
        """Continuous bidirectional sync & command execution daemon loop."""
        self.running = True
        logger.info(f"Starting Bidirectional Cloud Sync Worker -> Target: {self.cloud_url} (Interval: {interval_seconds}s)")
        database.init_db()
        self.check_and_update_weather_cache()
        
        while self.running:
            try:
                # 1. Cloud Pull: Drain & execute pending commands from cloud
                self.poll_and_execute_cloud_commands()

                # 2. Edge Push: Drain unsynced telemetry batches to cloud
                while self.running:
                    count = self.sync_batch()
                    if count <= 0:
                        break
                        
                # 3. Edge Push: Drain unsynced AI detections to cloud
                while self.running:
                    ai_count = self.sync_ai_batch()
                    if ai_count <= 0:
                        break

                # 4. Weather Cache freshness check
                self.check_and_update_weather_cache()
                
            except Exception as e:
                logger.error(f"Sync loop error: {e}")
                
            time.sleep(interval_seconds)

    def start_background(self, interval_seconds: float = SYNC_INTERVAL) -> threading.Thread:
        self._thread = threading.Thread(target=self.start_loop, args=(interval_seconds,), daemon=True)
        self._thread.start()
        return self._thread

    def stop(self):
        self.running = False

if __name__ == "__main__":
    worker = CloudSyncWorker()
    try:
        worker.start_loop(SYNC_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Cloud sync worker stopped by user.")
