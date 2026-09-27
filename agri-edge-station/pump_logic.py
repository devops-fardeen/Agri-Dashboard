"""
Automated Weather & Soil Moisture Pump Irrigation Logic Controller

Implements the flowchart decision tree:
1. Check weather condition: Is Raining?
   - YES: Force Relay OFF if ON, do nothing else.
   - NO: Check Soil Moisture.
2. Check Soil Moisture:
   - HIGH (>= 60%): Do nothing with relay (Pumps OFF / Idle).
   - LOW (< 60%): Check Rain forecast / precipitation chance in upcoming hours.
3. Check Rain Forecast:
   - Next hour rain chance is HIGH (80% - 90% or above):
     -> Do nothing (hold irrigation since natural rainfall is imminent).
   - Rain chance is LOW to MODERATE (10% to 50%):
     -> Turn ON the pump for a 15-minute cycle, then turn OFF.
     -> After the rainy/forecast window, re-check soil moisture to dynamically resume normal control.
   - Very Low rain chance (< 10%):
     -> Normal irrigation cycle (Turn pump ON until optimal hydration target is reached).
"""

import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, Optional
import database

logger = logging.getLogger("pump_logic")

# In-memory tracking of timed irrigation cycles, hold timers, and manual force overrides
# Format: { "PUMP_ZONE_A": { "cycle_end_time": datetime, "started_at": datetime, "mode": "15_MIN_RAIN_WINDOW" } }
_pump_cycle_tracker: Dict[str, Dict[str, Any]] = {}
_manual_force_override: Dict[str, bool] = {"PUMP_ZONE_A": False, "PUMP_ZONE_B": False}

def set_force_override(target: str, force_on: bool):
    """Sets or clears manual force override to run pump regardless of all weather/moisture conditions."""
    target_clean = "PUMP_ZONE_A" if "A" in target.upper() else "PUMP_ZONE_B"
    _manual_force_override[target_clean] = force_on
    if force_on:
        database.set_actuator_state(target_clean, 1)
        logger.info(f"[{target_clean}] MANUAL FORCE OVERRIDE ENGAGED. Pump forced ON regardless of conditions.")
    else:
        logger.info(f"[{target_clean}] Manual force override cleared.")

def get_force_override(target: str) -> bool:
    target_clean = "PUMP_ZONE_A" if "A" in target.upper() else "PUMP_ZONE_B"
    return _manual_force_override.get(target_clean, False)

def get_rain_probability_next_hours(hours: int = 2) -> Tuple[int, int]:
    """
    Returns (next_1h_rain_prob, max_next_hours_rain_prob) from Open-Meteo cached forecast.
    """
    cached_wx = database.get_cached_weather()
    if not cached_wx or not cached_wx.get("forecast"):
        return 0, 0
    
    forecast = cached_wx["forecast"]
    hourly = forecast.get("hourly", [])
    if not hourly:
        # Check daily
        days = forecast.get("days", [])
        if days:
            return int(days[0].get("rain_prob", 0)), int(days[0].get("rain_prob", 0))
        return 0, 0

    # Get probabilities for upcoming slots
    probs = []
    for item in hourly[:max(hours, 1)]:
        p = item.get("rainProb") if "rainProb" in item else item.get("rain_prob", 0)
        probs.append(int(p or 0))

    next_1h = probs[0] if len(probs) > 0 else 0
    max_window = max(probs) if probs else 0
    return next_1h, max_window

def evaluate_and_apply_pump_logic(zone_id: str = "ZONE_A", moisture_threshold: float = 60.0) -> Dict[str, Any]:
    """
    Executes the decision tree for the specified zone's water pump.
    NOTE: As requested, if manual force override is ON, the pump runs forcefully regardless of all conditions!
    """
    target_pump = "PUMP_ZONE_A" if "A" in zone_id.upper() else "PUMP_ZONE_B"
    now_utc = datetime.now(timezone.utc)
    
    # 0. Check Manual Force Override First!
    if _manual_force_override.get(target_pump, False):
        database.set_actuator_state(target_pump, 1)
        return {
            "target": target_pump,
            "zone_id": zone_id,
            "is_raining": False,
            "soil_moisture": float((database.get_latest_telemetry(zone_id) or {}).get("soil_moisture") or 60.0),
            "pump_state": 1,
            "action": "FORCE_ON_MANUAL",
            "reason": "Force Override Active: Pump is running forcefully regardless of all weather & moisture conditions.",
            "mode": "MANUAL_FORCE_OVERRIDE",
            "force_override": True
        }

    # 1. Fetch current sensor telemetry for display and soil moisture
    telemetry = database.get_latest_telemetry(zone_id) or {}
    soil_moisture = float(telemetry.get("soil_moisture") or 60.0)
    current_pump_state = database.get_actuator_state(target_pump)

    # 2. Check live weather condition and precipitation strictly from Weather API
    cached_wx = database.get_cached_weather()
    weather_rain = False
    curr_condition = "Clear"
    if cached_wx and cached_wx.get("forecast"):
        curr = cached_wx["forecast"].get("current", {})
        precip = float(curr.get("precipitation", 0.0))
        curr_condition = str(curr.get("condition", ""))
        cond_lower = curr_condition.lower()
        age = float(cached_wx.get("age_minutes", 999))
        if age <= 30.0 and (precip > 0.0 or any(w in cond_lower for w in ["rain", "shower", "thunder", "drizzle"])):
            weather_rain = True

    # -------------------------------------------------------------
    # DECISION STEP 1: Check Weather API -> Is It Currently Raining?
    # -------------------------------------------------------------
    if weather_rain:
        # Force Relay OFF if ON
        if current_pump_state != 0:
            database.set_actuator_state(target_pump, 0)
            logger.info(f"[{target_pump}] Live Weather API indicates active rain ({curr_condition})! Pump relay shut OFF.")
        
        # Clear any active timer cycle
        if target_pump in _pump_cycle_tracker:
            del _pump_cycle_tracker[target_pump]

        return {
            "target": target_pump,
            "zone_id": zone_id,
            "is_raining": True,
            "soil_moisture": soil_moisture,
            "pump_state": 0,
            "action": "FORCE_OFF",
            "reason": f"Active weather precipitation detected from Weather API ({curr_condition}). Relay shut OFF to avoid waterlogging.",
            "mode": "RAIN_LOCKOUT"
        }

    # -------------------------------------------------------------
    # DECISION STEP 2: Check active 15-minute timer cycle
    # -------------------------------------------------------------
    if target_pump in _pump_cycle_tracker:
        tracker = _pump_cycle_tracker[target_pump]
        end_time = tracker.get("cycle_end_time")
        if end_time and now_utc < end_time:
            # 15-minute cycle still active
            rem_secs = int((end_time - now_utc).total_seconds())
            rem_mins = round(rem_secs / 60.0, 1)
            if current_pump_state == 0:
                database.set_actuator_state(target_pump, 1)
            return {
                "target": target_pump,
                "zone_id": zone_id,
                "is_raining": False,
                "soil_moisture": soil_moisture,
                "pump_state": 1,
                "action": "RUNNING_TIMER",
                "time_remaining_minutes": rem_mins,
                "reason": f"Active 15-minute irrigation cycle in progress ({rem_mins}m left for moderate rain chance).",
                "mode": "TIMED_CYCLE_15MIN"
            }
        else:
            # Cycle finished! Turn pump OFF and remove tracker
            database.set_actuator_state(target_pump, 0)
            del _pump_cycle_tracker[target_pump]
            logger.info(f"[{target_pump}] 15-Minute moderate-rain irrigation cycle completed. Pump turned OFF.")

    # -------------------------------------------------------------
    # DECISION STEP 3: Check Soil Moisture (Low vs High)
    # -------------------------------------------------------------
    if soil_moisture >= moisture_threshold:
        # Moisture is HIGH -> Do nothing with relay
        if current_pump_state == 1:
            database.set_actuator_state(target_pump, 0)
            logger.info(f"[{target_pump}] Soil moisture is optimal/high ({soil_moisture}% >= {moisture_threshold}%). Pump turned OFF.")
        
        return {
            "target": target_pump,
            "zone_id": zone_id,
            "is_raining": False,
            "soil_moisture": soil_moisture,
            "moisture_level": "HIGH",
            "pump_state": 0,
            "action": "NO_ACTION",
            "reason": f"Soil moisture is sufficient ({soil_moisture}% >= {moisture_threshold}%). Relay idle.",
            "mode": "MOISTURE_OPTIMAL"
        }

    # Soil moisture is LOW (< moisture_threshold) -> Check Rain Forecast
    next_1h_rain, next_3h_max_rain = get_rain_probability_next_hours(hours=3)
    effective_rain_chance = max(next_1h_rain, next_3h_max_rain)

    # -------------------------------------------------------------
    # DECISION STEP 4: Check Rain Forecast when Moisture is Low
    # -------------------------------------------------------------
    # Branch A: Rain prediction shows rain is happening in next hour and chances are 80% to 90%+
    if next_1h_rain >= 75 or effective_rain_chance >= 80:
        if current_pump_state == 1:
            database.set_actuator_state(target_pump, 0)
        return {
            "target": target_pump,
            "zone_id": zone_id,
            "is_raining": False,
            "soil_moisture": soil_moisture,
            "moisture_level": "LOW",
            "rain_chance": effective_rain_chance,
            "pump_state": 0,
            "action": "HOLD_FOR_RAIN",
            "reason": f"Soil moisture is low ({soil_moisture}%), but rain is imminent in next hour ({effective_rain_chance}% chance). Pump kept OFF to conserve water.",
            "mode": "RAIN_IMMINENT_HOLD"
        }

    # Branch B: If chance of rain is about 10% to 50%
    if 10 <= effective_rain_chance <= 74:
        # Turn ON pump for 15 minutes, then turn OFF
        end_time = now_utc + timedelta(minutes=15)
        _pump_cycle_tracker[target_pump] = {
            "started_at": now_utc,
            "cycle_end_time": end_time,
            "mode": "15_MIN_RAIN_WINDOW",
            "rain_chance": effective_rain_chance
        }
        database.set_actuator_state(target_pump, 1)
        logger.info(f"[{target_pump}] Rain chance is {effective_rain_chance}% (10-50% range). Starting 15-minute timed irrigation.")
        
        return {
            "target": target_pump,
            "zone_id": zone_id,
            "is_raining": False,
            "soil_moisture": soil_moisture,
            "moisture_level": "LOW",
            "rain_chance": effective_rain_chance,
            "pump_state": 1,
            "action": "START_15_MIN_CYCLE",
            "time_remaining_minutes": 15.0,
            "reason": f"Soil moisture is low ({soil_moisture}%) and rain chance is moderate ({effective_rain_chance}%). Pump turned ON for 15 minutes.",
            "mode": "TIMED_CYCLE_15MIN"
        }

    # Branch C: Chance of rain is very low (< 10%)
    # Normal standard irrigation cycle until moisture recovers
    database.set_actuator_state(target_pump, 1)
    return {
        "target": target_pump,
        "zone_id": zone_id,
        "is_raining": False,
        "soil_moisture": soil_moisture,
        "moisture_level": "LOW",
        "rain_chance": effective_rain_chance,
        "pump_state": 1,
        "action": "START_IRRIGATION",
        "reason": f"Soil moisture is low ({soil_moisture}% < {moisture_threshold}%) with clear sky (<10% rain). Standard irrigation pump active.",
        "mode": "ACTIVE_IRRIGATION"
    }

def run_automated_pump_check():
    """Runs the flowchart evaluation for both Zone A and Zone B."""
    res_a = evaluate_and_apply_pump_logic("ZONE_A", moisture_threshold=60.0)
    res_b = evaluate_and_apply_pump_logic("ZONE_B", moisture_threshold=55.0)
    return {
        "ZONE_A": res_a,
        "ZONE_B": res_b,
        "evaluated_at": datetime.now(timezone.utc).isoformat()
    }
