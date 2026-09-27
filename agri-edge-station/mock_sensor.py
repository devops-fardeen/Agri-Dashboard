import time
import random
import threading
import logging
from datetime import datetime, timezone
import database

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [MOCK_SENSOR] %(message)s")
logger = logging.getLogger("mock_sensor")

_current_rain_detected: int = 0

def set_rain_detected(detected: bool):
    """Sets the simulated/manual rain state."""
    global _current_rain_detected
    _current_rain_detected = 1 if detected else 0

def get_rain_detected() -> int:
    """Returns the current simulated/manual rain state."""
    global _current_rain_detected
    return _current_rain_detected

class FieldSensorSimulator:
    """
    Simulates field sensors for Zone A (Crops) and Zone B (Orchard).
    Automatically yields when real ESP32 Master/Slave hardware is actively streaming data.
    """
    def __init__(self):
        # Baseline state for Zone A (Field A)
        self.state_a = {
            "soil_moisture": 62.5,
            "soil_temp": 23.8,
            "ambient_temp": 28.2,
            "ambient_humidity": 64.0,
            "light_lux": 1450.0,
            "pressure": 1013.2,
            "rain_detected": 0,
            "battery_level": 96.0
        }
        # Baseline state for Zone B (Field B)
        self.state_b = {
            "soil_moisture": 58.0,
            "soil_temp": 24.5,
            "ambient_temp": 28.6,
            "ambient_humidity": 61.5,
            "light_lux": 1520.0,
            "pressure": 1013.0,
            "rain_detected": 0,
            "battery_level": 92.5
        }
        self.running = False
        self._thread = None
        self._cycle_count = 0

    def _tick_zone(self, zone_id: str, state: dict, pump_active: bool, is_raining: bool) -> dict:
        # Moisture dynamics
        if pump_active:
            state["soil_moisture"] = min(88.0, state["soil_moisture"] + random.uniform(0.6, 1.2))
        elif is_raining:
            state["soil_moisture"] = min(92.0, state["soil_moisture"] + random.uniform(0.3, 0.7))
        else:
            state["soil_moisture"] = max(28.0, state["soil_moisture"] - random.uniform(0.04, 0.12))
            
        state["soil_temp"] = round(state["soil_temp"] + random.uniform(-0.08, 0.08), 2)
        state["ambient_temp"] = round(state["ambient_temp"] + random.uniform(-0.12, 0.12), 2)
        if is_raining:
            state["ambient_temp"] = max(19.0, min(27.0, state["ambient_temp"]))
        
        state["soil_temp"] = max(18.0, min(35.0, state["soil_temp"]))
        state["ambient_temp"] = max(20.0, min(42.0, state["ambient_temp"]))
        
        if is_raining:
            state["ambient_humidity"] = min(98.0, round(state["ambient_humidity"] + random.uniform(0.2, 0.8), 2))
        else:
            state["ambient_humidity"] = round(state["ambient_humidity"] + random.uniform(-0.25, 0.25), 2)
            state["ambient_humidity"] = max(30.0, min(95.0, state["ambient_humidity"]))
        
        state["light_lux"] = round(max(0.0, (200.0 if is_raining else 1450.0) + random.uniform(-20.0, 20.0)), 1)
        state["pressure"] = round(state["pressure"] + random.uniform(-0.05, 0.05), 2)
        state["rain_detected"] = 1 if is_raining else 0

        # Subnode battery dynamics (solar charging during day, slow drain)
        drain = random.uniform(0.005, 0.015)
        solar_boost = 0.01 if state["light_lux"] > 1000.0 else 0.0
        state["battery_level"] = round(max(15.0, min(100.0, state["battery_level"] - drain + solar_boost)), 1)
        
        return state

    def run_cycle(self):
        """Generates one telemetry sample for both zones only if real hardware is not active."""
        try:
            import serial_bridge
            bridge = serial_bridge.get_serial_bridge()
            if bridge and bridge.is_hardware_active(timeout_seconds=15.0):
                # Real hardware is actively streaming! Sync internal baseline and yield
                latest_a = database.get_latest_telemetry("ZONE_A")
                if latest_a:
                    self.state_a["soil_moisture"] = latest_a.get("soil_moisture", self.state_a["soil_moisture"])
                    self.state_a["soil_temp"] = latest_a.get("soil_temp", self.state_a["soil_temp"])
                    self.state_a["ambient_temp"] = latest_a.get("ambient_temp", self.state_a["ambient_temp"])
                    self.state_a["ambient_humidity"] = latest_a.get("ambient_humidity", self.state_a["ambient_humidity"])
                    self.state_a["battery_level"] = latest_a.get("battery_level", self.state_a["battery_level"])

                latest_b = database.get_latest_telemetry("ZONE_B")
                if latest_b:
                    self.state_b["soil_moisture"] = latest_b.get("soil_moisture", self.state_b["soil_moisture"])
                    self.state_b["soil_temp"] = latest_b.get("soil_temp", self.state_b["soil_temp"])
                    self.state_b["ambient_temp"] = latest_b.get("ambient_temp", self.state_b["ambient_temp"])
                    self.state_b["ambient_humidity"] = latest_b.get("ambient_humidity", self.state_b["ambient_humidity"])
                    self.state_b["battery_level"] = latest_b.get("battery_level", self.state_b["battery_level"])

                # Yield this cycle so fake data doesn't clobber live hardware telemetry
                return
        except Exception:
            pass

        # If no active hardware stream, execute standard simulation
        actuators = database.get_all_actuators()
        sensor_rain = bool(get_rain_detected())
        
        # Dual Rain Detection: Check rain sensor pin AND recent Weather API fetch data (last 15 min)
        weather_rain = False
        try:
            cached_wx = database.get_cached_weather()
            if cached_wx and cached_wx.get("forecast"):
                curr = cached_wx["forecast"].get("current", {})
                precip = float(curr.get("precipitation", 0.0))
                cond = str(curr.get("condition", "")).lower()
                age = float(cached_wx.get("age_minutes", 999))
                if age <= 15.0 and (precip > 0.0 or "rain" in cond or "shower" in cond or "thunder" in cond or "drizzle" in cond):
                    weather_rain = True
        except Exception:
            pass

        # Run Flowchart Pump Irrigation Evaluation Logic
        try:
            import pump_logic
            pump_logic.run_automated_pump_check()
            actuators = database.get_all_actuators()
        except Exception as e:
            logger.warning(f"Pump logic check error: {e}")

        pump_a = bool(actuators.get("PUMP_ZONE_A", 0))
        pump_b = bool(actuators.get("PUMP_ZONE_B", 0))
        now_iso = datetime.now(timezone.utc).isoformat()
        self._cycle_count += 1
        
        # Update and log Zone A
        self._tick_zone("ZONE_A", self.state_a, pump_a, is_raining)
        database.log_telemetry(
            zone_id="ZONE_A",
            node_id="SIMULATED_PROBE_A",
            soil_moisture=self.state_a["soil_moisture"],
            soil_temp=self.state_a["soil_temp"],
            ambient_temp=self.state_a["ambient_temp"],
            ambient_humidity=self.state_a["ambient_humidity"],
            pump_active=1 if pump_a else 0,
            light_lux=self.state_a["light_lux"],
            barometric_pressure=self.state_a["pressure"],
            rain_detected=1 if is_raining else 0,
            battery_level=self.state_a["battery_level"],
            recorded_at=now_iso
        )
        
        # Update and log Zone B
        self._tick_zone("ZONE_B", self.state_b, pump_b, is_raining)
        database.log_telemetry(
            zone_id="ZONE_B",
            node_id="SIMULATED_PROBE_B",
            soil_moisture=self.state_b["soil_moisture"],
            soil_temp=self.state_b["soil_temp"],
            ambient_temp=self.state_b["ambient_temp"],
            ambient_humidity=self.state_b["ambient_humidity"],
            pump_active=1 if pump_b else 0,
            light_lux=self.state_b["light_lux"],
            barometric_pressure=self.state_b["pressure"],
            rain_detected=1 if is_raining else 0,
            battery_level=self.state_b["battery_level"],
            recorded_at=now_iso
        )

    def start_loop(self, interval_seconds: float = 5.0):
        """Continuous simulation loop."""
        self.running = True
        logger.info(f"Starting mock sensor fallback service (interval: {interval_seconds}s)...")
        database.init_db()
        while self.running:
            try:
                self.run_cycle()
            except Exception as e:
                logger.error(f"Error in sensor fallback cycle: {e}")
            time.sleep(interval_seconds)

    def start_background(self, interval_seconds: float = 5.0) -> threading.Thread:
        """Starts simulator as a daemon thread."""
        self._thread = threading.Thread(target=self.start_loop, args=(interval_seconds,), daemon=True)
        self._thread.start()
        return self._thread

    def stop(self):
        self.running = False
