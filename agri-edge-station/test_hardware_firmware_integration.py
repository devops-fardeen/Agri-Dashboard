import os
import sys
import time

# Ensure current dir is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
import serial_bridge
from mock_sensor import FieldSensorSimulator
from server import app
from fastapi.testclient import TestClient

def test_hardware_integration():
    print("==================================================")
    print("Testing Hardware Firmware & Dashboard Integration")
    print("==================================================")

    # 1. Initialize DB
    database.init_db()
    print("[PASS] Database initialized")

    # 2. Instantiate MasterSerialBridge
    bridge = serial_bridge.MasterSerialBridge()
    print("[PASS] MasterSerialBridge instantiated")

    # 3. Simulate Master Node Sensors Serial Stream
    master_sensor_lines = [
        "========== MASTER SENSORS ==========",
        "Rain Raw: 2650",
        "Water Level Raw: 1800",
        "Light: 1520.50 lux",
        "BMP Temperature: 26.80 C",
        "Pressure: 1014.20 hPa",
        "===================================="
    ]
    for line in master_sensor_lines:
        bridge._parse_line(line)

    assert bridge.master_data["rain_raw"] == 2650
    assert bridge.master_data["rain_detected"] == 0
    assert bridge.master_data["light_lux"] == 1520.50
    assert bridge.master_data["bmp_temperature"] == 26.80
    assert bridge.master_data["pressure"] == 1014.20
    print("[PASS] Master sensors parsed correctly from block format")

    # 4. Simulate LoRa Packet from Slave Node 1 (Zone A)
    lora_pkt_1 = "Received: NODE=1,T=29.20,H=63.50,SM=45,SMRAW=2050,ST=23.40"
    bridge._parse_line(lora_pkt_1)

    latest_a = database.get_latest_telemetry("ZONE_A")
    assert latest_a is not None
    assert latest_a["soil_moisture"] == 45.0
    assert latest_a["soil_temp"] == 23.40
    assert latest_a["ambient_temp"] == 29.20
    assert latest_a["ambient_humidity"] == 63.50
    assert latest_a["light_lux"] == 1520.50
    assert latest_a["barometric_pressure"] == 1014.20
    print("[PASS] Slave Node 1 (Zone A) LoRa packet ingested & verified in SQLite")

    # 5. Simulate LoRa Packet from Slave Node 2 (Zone B)
    lora_pkt_2 = "Received: NODE=2,T=28.10,H=67.00,SM=38,SMRAW=2280,ST=24.10"
    bridge._parse_line(lora_pkt_2)

    latest_b = database.get_latest_telemetry("ZONE_B")
    assert latest_b is not None
    assert latest_b["soil_moisture"] == 38.0
    assert latest_b["soil_temp"] == 24.10
    assert latest_b["ambient_temp"] == 28.10
    assert latest_b["ambient_humidity"] == 67.00
    print("[PASS] Slave Node 2 (Zone B) LoRa packet ingested & verified in SQLite")

    # 6. Simulate Irrigation Relay Status Stream
    irrigation_lines = [
        "========== IRRIGATION ==========",
        "Rain Detected: NO",
        "Pump 1: ON",
        "Pump 2: OFF",
        "================================"
    ]
    for line in irrigation_lines:
        bridge._parse_line(line)

    actuators = database.get_all_actuators()
    assert actuators.get("PUMP_ZONE_A") == 1
    assert actuators.get("PUMP_ZONE_B") == 0
    print("[PASS] Hardware Irrigation Relays synchronized with Actuator states (Pump 1=ON, Pump 2=OFF)")

    # 7. Verify Hardware Yielding in Mock Sensor Simulator
    assert bridge.is_hardware_active() == True
    simulator = FieldSensorSimulator()
    # Running cycle while hardware is active should NOT log fake data
    init_count = len(database.get_24h_history("ZONE_A", limit=100))
    simulator.run_cycle()
    post_count = len(database.get_24h_history("ZONE_A", limit=100))
    assert init_count == post_count
    print("[PASS] Mock sensor simulator correctly yielded while hardware stream is active")

    # 8. Test API Endpoints with TestClient
    client = TestClient(app)
    
    # /api/edge/status
    res_status = client.get("/api/edge/status")
    assert res_status.status_code == 200
    data_status = res_status.json()
    assert data_status["success"] == True
    assert "hardware" in data_status
    assert data_status["actuators"]["PUMP_ZONE_A"] == 1
    assert data_status["actuators"]["PUMP_ZONE_B"] == 0
    print("[PASS] GET /api/edge/status returned valid hardware & telemetry payload")

    # /api/edge/hardware
    res_hw = client.get("/api/edge/hardware")
    assert res_hw.status_code == 200
    data_hw = res_hw.json()
    assert data_hw["success"] == True
    assert data_hw["status"]["master_sensors"]["rain_raw"] == 2650
    assert data_hw["status"]["slave_nodes"]["1"]["soil_moisture"] == 45
    assert data_hw["status"]["slave_nodes"]["2"]["soil_moisture"] == 38
    print("[PASS] GET /api/edge/hardware returned complete diagnostic structure")

    # /api/edge/rover/command
    res_rover = client.post("/api/edge/rover/command", json={"action": "MOVE_FORWARD"})
    assert res_rover.status_code == 200
    data_rover = res_rover.json()
    assert data_rover["success"] == True
    assert data_rover["action"] == "MOVE_FORWARD"
    print("[PASS] POST /api/edge/rover/command processed navigation command")

    print("==================================================")
    print(" ALL TESTS PASSED! Dashboard fully synced with HW ")
    print("==================================================")

if __name__ == "__main__":
    test_hardware_integration()
