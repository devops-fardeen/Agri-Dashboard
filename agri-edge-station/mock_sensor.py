import time
import random
import threading
import logging
from datetime import datetime, timezone
import database

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [MOCK_SENSOR] %(message)s")
logger = logging.getLogger("mock_sensor")

class FieldSensorSimulator:
    """
    Simulates field sensors for Zone A (Crops) and Zone B (Orchard).
    Reflects actuator dynamics: when a pump is ON, moisture rises;
    when OFF, natural evapotranspiration slowly depletes moisture.
    """
    def __init__(self):
        # Baseline state for Zone A
        self.state_a = {
            "soil_moisture": 62.5,
            "soil_temp": 23.8,
            "ambient_temp": 28.2,
            "ambient_humidity": 64.0,
            "light_lux": 1450.0,
            "pressure": 1013.2,
            "rain_detected": 0
        }
        # Baseline state for Zone B
        self.state_b = {
            "soil_moisture": 58.0,
            "soil_temp": 24.5,
            "ambient_temp": 28.6,
            "ambient_humidity": 61.5,
            "light_lux": 1520.0,
            "pressure": 1013.0,
            "rain_detected": 0
        }
        self.running = False
        self._thread = None
        self._cycle_count = 0

    def _tick_zone(self, zone_id: str, state: dict, pump_active: bool) -> dict:
        # Moisture dynamics
        if pump_active:
            # Active irrigation
            state["soil_moisture"] = min(88.0, state["soil_moisture"] + random.uniform(0.6, 1.2))
        else:
            # Natural depletion
            state["soil_moisture"] = max(28.0, state["soil_moisture"] - random.uniform(0.04, 0.12))
            
        # Temperature fluctuations (+- 0.15 deg)
        state["soil_temp"] = round(state["soil_temp"] + random.uniform(-0.08, 0.08), 2)
        state["ambient_temp"] = round(state["ambient_temp"] + random.uniform(-0.12, 0.12), 2)
        
        # Clamp temperatures within realistic ranges
        state["soil_temp"] = max(18.0, min(35.0, state["soil_temp"]))
        state["ambient_temp"] = max(20.0, min(42.0, state["ambient_temp"]))
        
        # Humidity fluctuations
        state["ambient_humidity"] = round(state["ambient_humidity"] + random.uniform(-0.25, 0.25), 2)
        state["ambient_humidity"] = max(30.0, min(95.0, state["ambient_humidity"]))
        
        # Light & pressure
        state["light_lux"] = round(max(0.0, state["light_lux"] + random.uniform(-20.0, 20.0)), 1)
        state["pressure"] = round(state["pressure"] + random.uniform(-0.05, 0.05), 2)
        
        return state

    def run_cycle(self):
        """Generates one telemetry sample for both zones and logs to SQLite."""
        # Read current actuator states
        actuators = database.get_all_actuators()
        pump_a = bool(actuators.get("PUMP_ZONE_A", 0))
        pump_b = bool(actuators.get("PUMP_ZONE_B", 0))
        
        now_iso = datetime.now(timezone.utc).isoformat()
        self._cycle_count += 1
        
        # Update and log Zone A
        self._tick_zone("ZONE_A", self.state_a, pump_a)
        row_a = database.log_telemetry(
            zone_id="ZONE_A",
            soil_moisture=self.state_a["soil_moisture"],
            soil_temp=self.state_a["soil_temp"],
            ambient_temp=self.state_a["ambient_temp"],
            ambient_humidity=self.state_a["ambient_humidity"],
            pump_active=1 if pump_a else 0,
            light_lux=self.state_a["light_lux"],
            barometric_pressure=self.state_a["pressure"],
            rain_detected=self.state_a["rain_detected"],
            recorded_at=now_iso
        )
        
        # Update and log Zone B
        self._tick_zone("ZONE_B", self.state_b, pump_b)
        row_b = database.log_telemetry(
            zone_id="ZONE_B",
            soil_moisture=self.state_b["soil_moisture"],
            soil_temp=self.state_b["soil_temp"],
            ambient_temp=self.state_b["ambient_temp"],
            ambient_humidity=self.state_b["ambient_humidity"],
            pump_active=1 if pump_b else 0,
            light_lux=self.state_b["light_lux"],
            barometric_pressure=self.state_b["pressure"],
            rain_detected=self.state_b["rain_detected"],
            recorded_at=now_iso
        )
        
        logger.info(
            f"Sample logged -> Zone A: {self.state_a['soil_moisture']:.1f}% (Pump: {'ON' if pump_a else 'OFF'}, Rain: {bool(self.state_a['rain_detected'])}) | "
            f"Zone B: {self.state_b['soil_moisture']:.1f}% (Pump: {'ON' if pump_b else 'OFF'}, Rain: {bool(self.state_b['rain_detected'])}) [IDs: {row_a}, {row_b}]"
        )

    def start_loop(self, interval_seconds: float = 5.0):
        """Continuous simulation loop."""
        self.running = True
        logger.info(f"Starting mock sensor telemetry generation (interval: {interval_seconds}s)...")
        database.init_db()
        while self.running:
            try:
                self.run_cycle()
            except Exception as e:
                logger.error(f"Error generating mock telemetry: {e}")
            time.sleep(interval_seconds)

    def start_background(self, interval_seconds: float = 5.0) -> threading.Thread:
        """Starts simulator as a daemon thread."""
        self._thread = threading.Thread(target=self.start_loop, args=(interval_seconds,), daemon=True)
        self._thread.start()
        return self._thread

    def stop(self):
        self.running = False

if __name__ == "__main__":
    simulator = FieldSensorSimulator()
    try:
        simulator.start_loop(5.0)
    except KeyboardInterrupt:
        logger.info("Mock sensor simulation stopped by user.")
