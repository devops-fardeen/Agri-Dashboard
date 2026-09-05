import os
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, HTTPException, Path, Body
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import database

# Initialize SQLite database schema
database.init_db()

app = FastAPI(
    title="AgriSmart Local Edge Station",
    description="Tier 2: Offline Local Gateway & Direct Hotspot Controller",
    version="2.0.0"
)

# Allow local intranet and cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
INDEX_FILE = os.path.join(STATIC_DIR, "index.html")

# ----------------------------------------------------------------------
# PYDANTIC MODELS
# ----------------------------------------------------------------------

class RoverCommandRequest(BaseModel):
    action: str

# ----------------------------------------------------------------------
# API ENDPOINTS
# ----------------------------------------------------------------------

@app.get("/api/edge/status")
def get_edge_status():
    """Returns the comprehensive status: telemetry, actuators, stats, rover, and cached weather."""
    telemetry = database.get_latest_telemetry()
    actuators = database.get_all_actuators()
    stats = database.get_edge_stats()
    rover = database.get_rover_state()
    weather = database.get_cached_weather()
    
    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "edge_node": "EDGE_STATION_PI (Local AP: 10.42.0.1:8000)",
        "actuators": {
            "PUMP_ZONE_A": actuators.get("PUMP_ZONE_A", 0),
            "PUMP_ZONE_B": actuators.get("PUMP_ZONE_B", 0),
        },
        "telemetry": telemetry,
        "rover": rover,
        "weather": weather,
        "stats": stats
    }

@app.get("/api/edge/weather")
def get_weather():
    """Returns the 7-day offline cached Open-Meteo weather forecast."""
    cached = database.get_cached_weather()
    if not cached:
        return {
            "success": False,
            "message": "Weather cache is empty. Will populate automatically when online."
        }
    return {
        "success": True,
        "data": cached
    }

@app.get("/api/edge/rover")
def get_rover():
    """Returns the field scout rover telemetry state."""
    state = database.get_rover_state()
    return {
        "success": True,
        "rover": state
    }

@app.post("/api/edge/rover/command")
def send_rover_command(payload: RoverCommandRequest):
    """Processes a navigation/emergency command for the rover."""
    action = payload.action.upper().strip()
    valid_actions = ["MOVE_FORWARD", "MOVE_BACKWARD", "MOVE_LEFT", "MOVE_RIGHT", "STOP"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid rover command. Must be one of {valid_actions}")
        
    updated = database.update_rover_command(action)
    return {
        "success": True,
        "action": action,
        "rover": updated
    }

@app.post("/api/edge/pump/{target}/{action}")
def control_pump(
    target: str = Path(..., description="Target pump: PUMP_ZONE_A or PUMP_ZONE_B"),
    action: str = Path(..., description="Action: ON, OFF, or TOGGLE")
):
    """Toggles or sets the hardware pump relay state in SQLite."""
    target_clean = target.upper().strip()
    if target_clean in ["ZONE_A", "PUMP_A", "A"]:
        target_clean = "PUMP_ZONE_A"
    elif target_clean in ["ZONE_B", "PUMP_B", "B"]:
        target_clean = "PUMP_ZONE_B"
        
    if target_clean not in ["PUMP_ZONE_A", "PUMP_ZONE_B"]:
        raise HTTPException(status_code=400, detail="Invalid target. Must be PUMP_ZONE_A or PUMP_ZONE_B")
        
    action_clean = action.upper().strip()
    if action_clean in ["ON", "1", "TRUE", "START"]:
        new_state = 1
        database.set_actuator_state(target_clean, new_state)
    elif action_clean in ["OFF", "0", "FALSE", "STOP"]:
        new_state = 0
        database.set_actuator_state(target_clean, new_state)
    elif action_clean in ["TOGGLE", "SWITCH"]:
        new_state = database.toggle_actuator_state(target_clean)
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use ON, OFF, or TOGGLE")
        
    return {
        "success": True,
        "target": target_clean,
        "state": new_state,
        "state_name": "RUNNING" if new_state else "IDLE",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/edge/history")
def get_history(zoneId: Optional[str] = None, zone_id: Optional[str] = None, limit: int = 50):
    """Fetches 24-hour historical records for time-series charts."""
    target_zone = zoneId or zone_id or "ZONE_A"
    limit = min(max(limit, 5), 100)
    records = database.get_24h_history(zone_id=target_zone, limit=limit)
    return {
        "success": True,
        "count": len(records),
        "zone_id": target_zone,
        "data": records
    }

# ----------------------------------------------------------------------
# SERVE LOCAL OFFLINE DASHBOARD
# ----------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Serves the self-contained offline HTML dashboard."""
    if os.path.exists(INDEX_FILE):
        return FileResponse(INDEX_FILE)
    return HTMLResponse("<h1>AgriSmart Edge Gateway</h1><p>static/index.html not found</p>", status_code=200)
