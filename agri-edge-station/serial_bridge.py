import time
import threading
import logging
import glob
import re
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import database

try:
    import serial
    import serial.tools.list_ports
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [SERIAL_BRIDGE] %(message)s")
logger = logging.getLogger("serial_bridge")

_global_bridge_instance = None

def get_serial_bridge():
    global _global_bridge_instance
    return _global_bridge_instance

class MasterSerialBridge:
    """
    USB Serial Bridge for the Agri Master ESP32 Node.
    - Robustly parses LoRa packets: NODE=1/2,T=...,H=...,SM=...,SMRAW=...,ST=...
    - Parses Master Station sensors: Rain Raw, Water Level Raw, Light (BH1750), BMP Temperature & Pressure (BMP280)
    - Parses and syncs Irrigation Relay states: Pump 1 & Pump 2
    - Fallback compatibility for legacy DATA,... and RAIN_STATUS:... formats
    """
    def __init__(self, baud_rate: int = 115200):
        global _global_bridge_instance
        _global_bridge_instance = self

        self.baud_rate = baud_rate
        self.serial_conn = None
        self.running = False
        self.hardware_active = False
        self.last_hardware_time: float = 0.0
        self._thread = None
        self._last_pump_states = {"PUMP_ZONE_A": -1, "PUMP_ZONE_B": -1}

        # Parsing state machine context
        self._current_block: Optional[str] = None
        self._block_node_id: Optional[int] = None

        # Master & Slave Node In-Memory Cache
        self.master_data = {
            "rain_raw": 3000,
            "rain_detected": 0,
            "water_level_raw": 0,
            "water_level_pct": 0,
            "light_lux": 1200.0,
            "bmp_temperature": 27.5,
            "pressure": 1013.25,
            "pump1_on": False,
            "pump2_on": False,
            "last_updated": 0.0
        }

        self.slave_nodes: Dict[int, Dict[str, Any]] = {
            1: {
                "node_id": 1,
                "zone_id": "ZONE_A",
                "air_temp": 28.0,
                "air_humidity": 65.0,
                "soil_moisture": 62,
                "soil_moisture_raw": 2100,
                "soil_temp": 24.0,
                "rssi": -65,
                "last_received": 0.0
            },
            2: {
                "node_id": 2,
                "zone_id": "ZONE_B",
                "air_temp": 27.5,
                "air_humidity": 66.0,
                "soil_moisture": 58,
                "soil_moisture_raw": 2200,
                "soil_temp": 24.2,
                "rssi": -68,
                "last_received": 0.0
            }
        }

    def is_hardware_active(self, timeout_seconds: float = 15.0) -> bool:
        """Returns True if real hardware has received packets in the last `timeout_seconds`."""
        if not self.hardware_active:
            return False
        return (time.time() - self.last_hardware_time) < timeout_seconds

    def get_hardware_status(self) -> Dict[str, Any]:
        """Returns diagnostic status of the USB Serial Bridge and hardware nodes."""
        now = time.time()
        is_live = self.is_hardware_active(timeout_seconds=15.0)
        return {
            "serial_connected": bool(self.serial_conn and self.serial_conn.is_open),
            "hardware_streaming": is_live,
            "last_packet_seconds_ago": round(now - self.last_hardware_time, 1) if self.last_hardware_time > 0 else None,
            "master_sensors": self.master_data,
            "slave_1_online": (now - self.slave_nodes[1]["last_received"]) < 30.0 if self.slave_nodes[1]["last_received"] > 0 else False,
            "slave_2_online": (now - self.slave_nodes[2]["last_received"]) < 30.0 if self.slave_nodes[2]["last_received"] > 0 else False,
            "slave_nodes": self.slave_nodes
        }

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

                time.sleep(0.02)
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
        Parses all telemetry streams emitted by Master_Node.ino:
        1. Direct LoRa Packet: "NODE=1,T=...,H=...,SM=...,SMRAW=...,ST=..." (or with "Received: ")
        2. Master Sensors Block: "========== MASTER SENSORS =========="
        3. Slave Node Block: "========== SLAVE NODE 1 =========="
        4. Irrigation Block: "========== IRRIGATION =========="
        5. Legacy DATA,... or RAIN_STATUS:...
        """
        import mock_sensor

        now_ts = time.time()
        now_iso = datetime.now(timezone.utc).isoformat()
        line_clean = line.strip()

        # =====================================================================
        # 1. DIRECT LORA PACKET (e.g. Received: NODE=1,T=28.50,H=65.00,SM=42,SMRAW=2100,ST=24.00)
        # =====================================================================
        if "NODE=" in line_clean and ",T=" in line_clean:
            packet_str = line_clean
            if "Received:" in packet_str:
                packet_str = packet_str.split("Received:", 1)[1].strip()

            match = re.search(r"NODE=(\d+),T=([-\d\.]+),H=([-\d\.]+),SM=(\d+),SMRAW=(\d+),ST=([-\d\.]+)", packet_str)
            if match:
                node_id = int(match.group(1))
                air_t = float(match.group(2))
                air_h = float(match.group(3))
                soil_m = int(match.group(4))
                soil_raw = int(match.group(5))
                soil_t = float(match.group(6))

                self.last_hardware_time = now_ts
                self.hardware_active = True

                zone_id = "ZONE_A" if node_id == 1 else "ZONE_B"
                pump_key = "PUMP_ZONE_A" if node_id == 1 else "PUMP_ZONE_B"
                actuators = database.get_all_actuators()
                pump_on = bool(actuators.get(pump_key, 0))

                if node_id in self.slave_nodes:
                    self.slave_nodes[node_id].update({
                        "air_temp": air_t,
                        "air_humidity": air_h,
                        "soil_moisture": soil_m,
                        "soil_moisture_raw": soil_raw,
                        "soil_temp": soil_t,
                        "last_received": now_ts
                    })

                logger.info(
                    f"📥 [LORA PACKET INGEST] Node {node_id} ({zone_id}) -> "
                    f"Air: {air_t}°C, Hum: {air_h}%, Soil: {soil_m}% (Raw: {soil_raw}), Soil Temp: {soil_t}°C"
                )

                # Log to SQLite telemetry
                database.log_telemetry(
                    zone_id=zone_id,
                    node_id=f"SLAVE_NODE_{node_id}",
                    soil_moisture=float(soil_m),
                    soil_temp=soil_t,
                    ambient_temp=air_t,
                    ambient_humidity=air_h,
                    pump_active=1 if pump_on else 0,
                    light_lux=self.master_data["light_lux"],
                    barometric_pressure=self.master_data["pressure"],
                    rain_detected=1 if self.master_data["rain_detected"] else 0,
                    recorded_at=now_iso
                )
                return

        # =====================================================================
        # 2. BLOCK HEADERS & STATE MACHINE
        # =====================================================================
        if "========== MASTER SENSORS ==========" in line_clean:
            self._current_block = "MASTER_SENSORS"
            return
        elif "========== SLAVE NODE" in line_clean:
            self._current_block = "SLAVE_NODE"
            node_m = re.search(r"SLAVE NODE (\d+)", line_clean)
            self._block_node_id = int(node_m.group(1)) if node_m else 1
            return
        elif "========== IRRIGATION ==========" in line_clean:
            self._current_block = "IRRIGATION"
            return
        elif line_clean.startswith("=========="):
            self._current_block = None
            return

        # =====================================================================
        # 3. PARSE LINES WITHIN BLOCKS
        # =====================================================================
        if self._current_block == "MASTER_SENSORS":
            self.last_hardware_time = now_ts
            self.hardware_active = True

            if line_clean.startswith("Rain Raw:"):
                val = int(line_clean.split(":", 1)[1].strip())
                self.master_data["rain_raw"] = val
                is_rain = val < 1500
                self.master_data["rain_detected"] = 1 if is_rain else 0
                mock_sensor.set_rain_detected(is_rain)

            elif line_clean.startswith("Water Level Raw:"):
                val = int(line_clean.split(":", 1)[1].strip())
                self.master_data["water_level_raw"] = val
                # Water level raw 0..4095 approx mapped to 0..100%
                pct = max(0, min(100, int((val / 3000.0) * 100)))
                self.master_data["water_level_pct"] = pct

            elif line_clean.startswith("Light:"):
                val_str = line_clean.split(":", 1)[1].replace("lux", "").strip()
                try:
                    self.master_data["light_lux"] = float(val_str)
                except ValueError:
                    pass

            elif line_clean.startswith("BMP Temperature:"):
                val_str = line_clean.split(":", 1)[1].replace("°C", "").replace("C", "").strip()
                try:
                    self.master_data["bmp_temperature"] = float(val_str)
                except ValueError:
                    pass

            elif line_clean.startswith("Pressure:"):
                val_str = line_clean.split(":", 1)[1].replace("hPa", "").strip()
                try:
                    self.master_data["pressure"] = float(val_str)
                except ValueError:
                    pass

            self.master_data["last_updated"] = now_ts
            return

        elif self._current_block == "SLAVE_NODE":
            nid = self._block_node_id or 1
            self.last_hardware_time = now_ts
            self.hardware_active = True

            if nid in self.slave_nodes:
                node_dict = self.slave_nodes[nid]
                if line_clean.startswith("Air Temperature:"):
                    val_str = line_clean.split(":", 1)[1].replace("°C", "").replace("C", "").strip()
                    try:
                        node_dict["air_temp"] = float(val_str)
                    except ValueError:
                        pass
                elif line_clean.startswith("Air Humidity:"):
                    val_str = line_clean.split(":", 1)[1].replace("%", "").strip()
                    try:
                        node_dict["air_humidity"] = float(val_str)
                    except ValueError:
                        pass
                elif line_clean.startswith("Soil Moisture:"):
                    val_str = line_clean.split(":", 1)[1].replace("%", "").strip()
                    try:
                        node_dict["soil_moisture"] = int(float(val_str))
                    except ValueError:
                        pass
                elif line_clean.startswith("Soil Raw:"):
                    val_str = line_clean.split(":", 1)[1].strip()
                    try:
                        node_dict["soil_moisture_raw"] = int(val_str)
                    except ValueError:
                        pass
                elif line_clean.startswith("Soil Temperature:"):
                    val_str = line_clean.split(":", 1)[1].replace("°C", "").replace("C", "").strip()
                    try:
                        node_dict["soil_temp"] = float(val_str)
                    except ValueError:
                        pass
                elif line_clean.startswith("LoRa RSSI:"):
                    val_str = line_clean.split(":", 1)[1].replace("dBm", "").strip()
                    try:
                        node_dict["rssi"] = int(float(val_str))
                    except ValueError:
                        pass
                node_dict["last_received"] = now_ts
            return

        elif self._current_block == "IRRIGATION":
            self.last_hardware_time = now_ts
            self.hardware_active = True

            if line_clean.startswith("Rain Detected:"):
                is_rain = "YES" in line_clean.upper()
                self.master_data["rain_detected"] = 1 if is_rain else 0
                mock_sensor.set_rain_detected(is_rain)

            elif line_clean.startswith("Pump 1:"):
                pump1_on = "ON" in line_clean.upper()
                self.master_data["pump1_on"] = pump1_on
                database.set_actuator_state("PUMP_ZONE_A", 1 if pump1_on else 0)

            elif line_clean.startswith("Pump 2:"):
                pump2_on = "ON" in line_clean.upper()
                self.master_data["pump2_on"] = pump2_on
                database.set_actuator_state("PUMP_ZONE_B", 1 if pump2_on else 0)
            return

        # =====================================================================
        # 4. LEGACY / FALLBACK STRING FORMATS
        # =====================================================================
        if line_clean.startswith("DATA,"):
            parts = line_clean.split(",")
            if len(parts) >= 6:
                try:
                    temp = float(parts[1])
                    hum = float(parts[2])
                    soil_pct = float(parts[3])
                    soil_raw = int(parts[4])
                    is_rain = parts[5].strip() == "RAIN"

                    self.last_hardware_time = now_ts
                    self.hardware_active = True
                    mock_sensor.set_rain_detected(is_rain)

                    pumps = database.get_all_actuators()
                    pump_a_on = bool(pumps.get("PUMP_ZONE_A", 0))

                    database.log_telemetry(
                        zone_id="ZONE_A",
                        node_id="SLAVE_NODE_1",
                        soil_moisture=soil_pct,
                        soil_temp=24.0,
                        ambient_temp=temp,
                        ambient_humidity=hum,
                        pump_active=1 if pump_a_on else 0,
                        light_lux=self.master_data["light_lux"],
                        barometric_pressure=self.master_data["pressure"],
                        rain_detected=1 if is_rain else 0,
                        recorded_at=now_iso
                    )
                except Exception as ex:
                    logger.warning(f"Failed to parse legacy telemetry line '{line_clean}': {ex}")

        elif "RAIN_STATUS:" in line_clean or line_clean in ["RAIN", "NO_RAIN", "RAIN_DETECTED"]:
            is_rain = "RAIN" in line_clean and "NO_RAIN" not in line_clean
            self.last_hardware_time = now_ts
            self.master_data["rain_detected"] = 1 if is_rain else 0
            mock_sensor.set_rain_detected(is_rain)
            logger.info(f"🌧️ [MASTER ESP32 HARDWARE RAIN SENSOR] Rain Active: {is_rain}")

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
