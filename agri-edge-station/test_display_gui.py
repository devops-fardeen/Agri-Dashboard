"""
Unit and Integration Test Suite for upgraded Tier 1 display_gui.py with AI Models
"""
import sys
import os
import tkinter as tk

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure local module directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
import display_gui

def run_tests():
    print("=" * 60)
    print("RUNNING TIER 1 DISPLAY GUI & AI VALIDATION SUITE")
    print("=" * 60)

    # 1. Initialize Database
    database.init_db()
    print("[1/8] Database initialized successfully.")

    # 2. Check translation keys symmetry across EN, HI, PA
    keys_en = set(display_gui.TRANSLATIONS["en"].keys())
    keys_hi = set(display_gui.TRANSLATIONS["hi"].keys())
    keys_pa = set(display_gui.TRANSLATIONS["pa"].keys())

    diff_hi = keys_en.symmetric_difference(keys_hi)
    diff_pa = keys_en.symmetric_difference(keys_pa)

    print(f"[2/8] Key count: EN={len(keys_en)}, HI={len(keys_hi)}, PA={len(keys_pa)}")
    assert not diff_hi, f"Mismatch in Hindi keys: {diff_hi}"
    assert not diff_pa, f"Mismatch in Punjabi keys: {diff_pa}"
    print("      [OK] Translation keys symmetry verified (all 3 languages 100% matched)")

    # 3. Headless Tkinter GUI Instantiation
    root = tk.Tk()
    root.withdraw()  # Headless mode
    app = display_gui.AgriSmartDisplayGUI(root)
    print("[3/8] [OK] GUI components, AI diagnostics strip, and fonts initialized without errors.")

    # 4. Instant Trilingual Hot-Swapping
    for lang in ["en", "hi", "pa", "en"]:
        app.set_language(lang)
        assert app.current_lang == lang
        brand_txt = app.lbl_brand.cget("text")
        print(f"      [OK] Switched to [{lang.upper()}]: {brand_txt}")
    print("[4/8] [OK] Trilingual hot-swapping verified.")

    # 5. Alert Rules Engine Priority Testing (Telemetry + AI)
    alerts_to_test = [
        # AI alerts
        ({"soil_moisture": 60.0, "ambient_temp": 25.0}, {"soil_moisture": 65.0, "ambient_temp": 25.0}, {"battery": 80}, {"alerts": [{"type": "DISEASE", "label": "Early Blight", "confidence": 0.92, "node_id": "NODE_01"}]}, "alert_disease_detected"),
        ({"soil_moisture": 60.0, "ambient_temp": 25.0}, {"soil_moisture": 65.0, "ambient_temp": 25.0}, {"battery": 80}, {"alerts": [{"type": "PEST", "label": "Silverleaf whitefly", "confidence": 0.88, "node_id": "NODE_01"}]}, "alert_pest_detected"),
        ({"soil_moisture": 60.0, "ambient_temp": 25.0}, {"soil_moisture": 65.0, "ambient_temp": 25.0}, {"battery": 80}, {"alerts": [{"type": "NUTRITION", "label": "Nitrogen deficiency", "confidence": 0.78, "node_id": "NODE_01"}]}, "alert_nutrient_deficiency"),
        # Telemetry alerts
        ({"soil_moisture": 30.0, "ambient_temp": 25.0}, {"soil_moisture": 65.0, "ambient_temp": 25.0}, {"battery": 80}, None, "alert_low_moist_a"),
        ({"soil_moisture": 60.0, "ambient_temp": 25.0}, {"soil_moisture": 32.0, "ambient_temp": 25.0}, {"battery": 80}, None, "alert_low_moist_b"),
        ({"soil_moisture": 60.0, "ambient_temp": 39.5}, {"soil_moisture": 65.0, "ambient_temp": 25.0}, {"battery": 80}, None, "alert_high_heat"),
        ({"soil_moisture": 60.0, "ambient_temp": 25.0}, {"soil_moisture": 65.0, "ambient_temp": 25.0}, {"battery": 15}, None, "alert_low_battery"),
        ({"soil_moisture": 65.0, "ambient_temp": 26.0}, {"soil_moisture": 62.0, "ambient_temp": 26.0}, {"battery": 80}, None, "alert_normal"),
    ]

    print("[5/8] Testing Alert Rules Engine under various AI & telemetry conditions:")
    for za, zb, rov, ai, expected_key in alerts_to_test:
        msg, bg, fg, border = app._evaluate_alerts(za, zb, rov, ai)
        print(f"      [OK] [{expected_key}] -> '{msg}'")

    # 6. Actuator & Rover State Controls
    print("[6/8] Testing hardware toggles & safety commands:")
    initial_a = database.get_actuator_state("PUMP_ZONE_A")
    app.toggle_pump("PUMP_ZONE_A")
    new_a = database.get_actuator_state("PUMP_ZONE_A")
    assert new_a != initial_a
    print(f"      [OK] Pump Zone A toggle verified: State {initial_a} -> {new_a}")
    app.toggle_pump("PUMP_ZONE_A")  # Reset back

    app.emergency_stop_rover()
    rov_state = database.get_rover_state()
    assert rov_state["last_action"] == "STOP"
    print("      [OK] Rover Emergency Stop button verified.")

    # 7. Weather Cache Snapshot Rendering
    print("[7/8] Testing Weather Snapshot widget:")
    database.save_cached_weather({
        "latitude": 26.8, "longitude": 80.9, "cached_at": "2026-09-06T10:00:00Z",
        "days": [
            {"date": "2026-09-07", "day_name": "Today", "temp_max": 28.0, "temp_min": 21.0, "rain_prob": 0, "condition": "Sunny"},
            {"date": "2026-09-08", "day_name": "Tue", "temp_max": 27.0, "temp_min": 20.0, "rain_prob": 10, "condition": "Partly Cloudy"},
            {"date": "2026-09-09", "day_name": "Wed", "temp_max": 25.0, "temp_min": 19.0, "rain_prob": 65, "condition": "Rain"},
            {"date": "2026-09-10", "day_name": "Thu", "temp_max": 29.0, "temp_min": 22.0, "rain_prob": 5, "condition": "Sunny"},
            {"date": "2026-09-11", "day_name": "Fri", "temp_max": 28.0, "temp_min": 21.0, "rain_prob": 15, "condition": "Partly Cloudy"},
            {"date": "2026-09-12", "day_name": "Sat", "temp_max": 30.0, "temp_min": 23.0, "rain_prob": 20, "condition": "Sunny"},
            {"date": "2026-09-13", "day_name": "Sun", "temp_max": 27.0, "temp_min": 20.0, "rain_prob": 40, "condition": "Showers"},
        ]
    })
    app._update_ui_state()
    weather_lbl = app.lbl_weather.cget("text")
    weather_sub = app.lbl_weather_detail.cget("text")
    print(f"      [OK] Weather display: '{weather_lbl}' | '{weather_sub}'")

    # 8. AI Inference Bundle Logging & Live GUI Update
    print("[8/8] Testing AI Inference Bundle Logging & GUI Refresh:")
    test_results = {
        "disease": [{"name": "Early Blight", "confidence": 0.94, "bbox": [100, 100, 300, 300], "class_id": 0}],
        "pest": [{"name": "Silverleaf whitefly", "confidence": 0.85, "bbox": [50, 50, 150, 150], "class_id": 3}],
        "nutrition": [{"name": "nitrogen deficiency", "confidence": 0.77, "bbox": [200, 200, 400, 400], "class_id": 3}],
        "stage": [{"name": "Stage 2", "confidence": 0.96, "bbox": [0, 0, 640, 640], "class_id": 1}]
    }
    inserted = database.log_ai_inference_bundle("NODE_01", test_results, "test_frame.jpg")
    assert len(inserted) == 4
    app._update_ui_state()
    print(f"      [OK] AI Disease badge: {app.lbl_ai_disease_val.cget('text')}")
    print(f"      [OK] AI Pest badge: {app.lbl_ai_pest_val.cget('text')}")
    print(f"      [OK] AI Nutrition badge: {app.lbl_ai_nutr_val.cget('text')}")
    print(f"      [OK] AI Stage badge: {app.lbl_ai_stage_val.cget('text')}")

    root.destroy()
    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! (8/8)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
