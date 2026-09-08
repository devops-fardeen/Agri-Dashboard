import time
import threading
import logging
import glob
import sys
import database

try:
    import serial
    import serial.tools.list_ports
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [SERIAL_BRIDGE] %(message)s")
logger = logging.getLogger("serial_bridge")

class MasterSerialBridge:
    """
    USB Serial Bridge for the Agri Master ESP32 Node.
    - Reads real-time telemetry packets: DATA,<temp>,<humidity>,<soilPercent>,<soilRaw>,<RAIN/NO_RAIN>
    - Controls hardware relays by sending: PUMP1_ON, PUMP1_OFF, PUMP2_ON, PUMP2_OFF
    """
    def __init__(self, baud_rate: int = 115200):
        self.baud_rate = baud_rate
        self.serial_conn = None
        self.running = False
        self.hardware_active = False
        self._thread = None
        self._last_pump_states = {"PUMP_ZONE_A": -1, "PUMP_ZONE_B": -1}

    def _find_esp32_port(self):
        """Auto-detects ESP32 CP210x, CH340, or FTDI serial ports."""
        if not PYSERIAL_AVAILABLE:
            return None
            
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            desc = (p.description or "").lower()
            hwid = (p.hwid or "").lower()
            if any(k in desc or k in hwid for k in ["cp210", "ch340", "ch341", "usb serial", "uart", "esp32", "ftdi"]):
                return p.device

        # Fallback for Linux / Raspberry Pi devices
        linux_ports = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
        if linux_ports:
            return linux_ports[0]

        return None

    def start_background(self):
        """Starts the serial reader & actuator sync worker thread."""
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        return self._thread

    def stop(self):
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except Exception:
                pass

    def _run_loop(self):
        logger.info("Starting Master Node USB Serial Bridge watcher...")
        while self.running:
            if not self.serial_conn or not self.serial_conn.is_open:
                port = self._find_esp32_port()
                if port:
                    try:
                        logger.info(f"Connecting to Master ESP32 on port {port} at {self.baud_rate} baud...")
                        self.serial_conn = serial.Serial(port, self.baud_rate, timeout=1.0)
                        self.hardware_active = True
                        logger.info(f"✓ Master ESP32 connected successfully on {port}!")
                    except Exception as e:
                        logger.warning(f"Failed to connect to {port}: {e}")
                        self.serial_conn = None
                        self.hardware_active = False
                        time.sleep(3.0)
                else:
                    self.hardware_active = False
                    time.sleep(3.0)
                    continue

            try:
                # 1. Read incoming line from Master ESP32
                if self.serial_conn.in_waiting > 0:
                    raw_line = self.serial_conn.readline().decode("utf-8", errors="ignore").strip()
                    if raw_line:
                        self._parse_line(raw_line)

                # 2. Sync Actuator Relay states to Master ESP32
                self._sync_actuators()

                time.sleep(0.05)
            except Exception as e:
                logger.error(f"Serial connection error: {e}. Reconnecting...")
                if self.serial_conn:
                    try:
                        self.serial_conn.close()
                    except Exception:
                        pass
                self.serial_conn = None
                self.hardware_active = False
                time.sleep(2.0)

    def _parse_line(self, line: str):
        """
        Parses structured format:
        1. Full Telemetry: DATA,<temp>,<humidity>,<soilPercent>,<soilRaw>,<RAIN/NO_RAIN>
        2. Periodic Rain Status: RAIN_STATUS:RAIN or RAIN_STATUS:NO_RAIN
        """
        import mock_sensor

        if line.startswith("DATA,"):
            parts = line.split(",")
            if len(parts) >= 6:
                try:
                    temp = float(parts[1])
                    hum = float(parts[2])
                    soil_pct = float(parts[3])
                    soil_raw = int(parts[4])
                    is_rain = parts[5].strip() == "RAIN"

                    mock_sensor.set_rain_detected(is_rain)
                    logger.info(f"📥 [MASTER ESP32 INGEST] Temp: {temp}°C | Humidity: {hum}% | Soil: {soil_pct}% (Raw: {soil_raw}) | Rain: {is_rain}")
                    
                    # Log into SQLite telemetry database
                    pumps = database.get_all_actuators()
                    pump_a_on = bool(pumps.get("PUMP_ZONE_A", 0))

                    database.log_telemetry(
                        zone_id="ZONE_A",
                        node_id="SLAVE_ESP32_NOW",
                        soil_moisture=soil_pct,
                        soil_temp=24.0,
                        ambient_temp=temp,
                        ambient_humidity=hum,
                        pump_active=1 if pump_a_on else 0,
                        light_lux=0.0,
                        barometric_pressure=1013.25,
                        rain_detected=1 if is_rain else 0
                    )
                except Exception as ex:
                    logger.warning(f"Failed to parse telemetry line '{line}': {ex}")

        elif "RAIN_STATUS:" in line or line in ["RAIN", "NO_RAIN", "RAIN_DETECTED"]:
            is_rain = "RAIN" in line and "NO_RAIN" not in line
            mock_sensor.set_rain_detected(is_rain)
            logger.info(f"🌧️ [MASTER ESP32 HARDWARE RAIN SENSOR] Rain Active: {is_rain}")
            
            # Immediately update latest telemetry record with live rain status
            latest_a = database.get_latest_telemetry("ZONE_A") or {}
            database.log_telemetry(
                zone_id="ZONE_A",
                node_id="MASTER_ESP32_RAIN",
                soil_moisture=latest_a.get("soil_moisture", 62.0),
                soil_temp=latest_a.get("soil_temp", 24.0),
                ambient_temp=latest_a.get("ambient_temp", 28.0),
                ambient_humidity=latest_a.get("ambient_humidity", 65.0),
                pump_active=latest_a.get("pump_active", 0),
                light_lux=latest_a.get("light_lux", 0.0),
                barometric_pressure=latest_a.get("barometric_pressure", 1013.25),
                rain_detected=1 if is_rain else 0
            )

        elif "PUMP" in line or "SLAVE" in line or "MASTER" in line:
            logger.info(f"📟 [ESP32 LOG] {line}")


    def _sync_actuators(self):
        """Sends PUMP1_ON / PUMP1_OFF / PUMP2_ON / PUMP2_OFF when states change."""
        if not self.serial_conn or not self.serial_conn.is_open:
            return

        actuators = database.get_all_actuators()
        pA = actuators.get("PUMP_ZONE_A", 0)
        pB = actuators.get("PUMP_ZONE_B", 0)

        # Sync Pump A (Relay 1)
        if pA != self._last_pump_states["PUMP_ZONE_A"]:
            cmd = "PUMP1_ON\n" if pA else "PUMP1_OFF\n"
            self.serial_conn.write(cmd.encode("utf-8"))
            self.serial_conn.flush()
            self._last_pump_states["PUMP_ZONE_A"] = pA
            logger.info(f"📤 Sent command to Master ESP32: {cmd.strip()}")

        # Sync Pump B (Relay 2)
        if pB != self._last_pump_states["PUMP_ZONE_B"]:
            cmd = "PUMP2_ON\n" if pB else "PUMP2_OFF\n"
            self.serial_conn.write(cmd.encode("utf-8"))
            self.serial_conn.flush()
            self._last_pump_states["PUMP_ZONE_B"] = pB
            logger.info(f"📤 Sent command to Master ESP32: {cmd.strip()}")
