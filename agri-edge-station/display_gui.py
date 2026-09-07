"""
Tier 1: Raspberry Pi Physical Touchscreen Console GUI (1024x600 / 800x480).
AgriSmart Edge Station — Palette-Graded Tomato Crop Monitor, AI Diagnostics & Actuator Hub.

Palette:
#10232A - Deep Slate Marine
#3D4D55 - Slate Grey
#A79E9C - Muted Grey
#D3C3B9 - Warm Oat Sand
#B58863 - Caramel Amber
#161616 - Obsidian
"""

import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime, timezone
import os
import sys
import json
import math
from typing import Dict, Any, Optional

# Ensure local module directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database

# ==============================================================================
# TRILINGUAL LOCALIZATION DICTIONARY (EN / HI / PA)
# ==============================================================================
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "app_title": "🌱 AGRISMART CONSOLE — TOMATO MONITOR",
        "station_sub": "Local Edge Station • 10.42.0.1:8000 • Tier 1 Touchscreen",
        "cloud_linked": "● CLOUD LINKED",
        "cloud_buffering": "○ BUFFERING ({count} queued)",
        "weather_loading": "Loading weather...",
        "weather_offline": "Weather Cached (Offline)",
        "weather_rain": "Rain: {prob}%",
        "field_a_title": "🍅 TOMATO FIELD A (ZONE A)",
        "field_b_title": "🍅 TOMATO FIELD B (ZONE B)",
        "node_a_sub": "Node: EDGE_01 • LoRa Ch 1",
        "node_b_sub": "Node: EDGE_02 • LoRa Ch 2",
        "root_moisture": "ROOT SOIL MOISTURE",
        "moist_optimal_a": "Target: 60% – 75% • OPTIMAL HYDRATION",
        "moist_optimal_b": "Target: 50% – 65% • OPTIMAL HYDRATION",
        "moist_low": "Target: 60% – 75% • LOW MOISTURE / DRY",
        "moist_high": "Target: 60% – 75% • HIGH MOISTURE / SATURATED",
        "soil_temp": "SOIL TEMP",
        "air_temp": "AIR TEMP",
        "canopy_temp": "CANOPY TEMP",
        "air_humidity": "AIR HUMIDITY",
        "pump_a_on": "● PUMP A RUNNING — TAP TO STOP",
        "pump_a_off": "○ PUMP A IDLE / OFF — TAP TO START",
        "pump_b_on": "● PUMP B RUNNING — TAP TO STOP",
        "pump_b_off": "○ PUMP B IDLE / OFF — TAP TO START",
        "alert_normal": "✓ All Systems Normal — No Action Required",
        "alert_low_moist_a": "⚠️ Action Needed: Low moisture in Field A — Irrigation Recommended",
        "alert_low_moist_b": "⚠️ Action Needed: Low moisture in Field B — Irrigation Recommended",
        "alert_high_heat": "⚠️ High heat risk for tomato blossoms (>38°C)",
        "alert_low_battery": "⚠️ Low Rover Battery — Docking needed (<20%)",
        "rover_title": "🚜 FIELD SCOUT ROVER TELEMETRY",
        "rover_status_lbl": "Rover Status",
        "rover_parked": "Parked / Charging Dock",
        "rover_active_a": "Active in Field A",
        "rover_active_b": "Active in Field B",
        "rover_moving": "Moving ({speed} m/s)",
        "rover_battery_lbl": "Battery",
        "rover_heading_lbl": "Heading",
        "rover_stop_btn": "🛑 EMERGENCY STOP ROVER",
        "rover_stopped_alert": "🛑 ROVER EMERGENCY STOP TRIGGERED",
        "btn_fullscreen": "FULLSCREEN",
        "btn_exit": "EXIT CONSOLE",
        # AI Crop Diagnostics
        "ai_diagnostics_title": "🔬 AI CROP VISION DIAGNOSTICS (4 MODELS)",
        "ai_disease_lbl": "Disease",
        "ai_pest_lbl": "Pest Scout",
        "ai_nutrition_lbl": "Nutrition",
        "ai_stage_lbl": "Stage",
        "ai_healthy": "Healthy / Clear",
        "ai_no_pests": "No Pests",
        "ai_optimal_nutrients": "Balanced",
        "ai_stage_1": "Stage 1: Seedling",
        "ai_stage_2": "Stage 2: Blossom",
        "ai_stage_3": "Stage 3: Fruiting",
        "alert_disease_detected": "⚠️ AI ALERT: {label} in {node} ({conf}%) — Fungicide Recommended",
        "alert_pest_detected": "⚠️ AI ALERT: {label} in {node} ({conf}%) — Pest Control Required",
        "alert_nutrient_deficiency": "⚠️ AI ALERT: {label} in {node} — Fertilizer Recommended",
    },
    "hi": {
        "app_title": "🌱 एग्रीस्मार्ट कंसोल — टमाटर फसल निगरानी",
        "station_sub": "स्थानीय एज स्टेशन • 10.42.0.1:8000 • टियर 1 टचस्क्रीन",
        "cloud_linked": "● क्लाउड कनेक्टेड",
        "cloud_buffering": "○ बफरिंग ({count} कतारबद्ध)",
        "weather_loading": "मौसम लोड हो रहा है...",
        "weather_offline": "मौसम कैश (ऑफ़लाइन)",
        "weather_rain": "बारिश: {prob}%",
        "field_a_title": "🍅 टमाटर खेत A (जोन A)",
        "field_b_title": "🍅 टमाटर खेत B (जोन B)",
        "node_a_sub": "नोड: EDGE_01 • लोरा चैनल 1",
        "node_b_sub": "नोड: EDGE_02 • लोरा चैनल 2",
        "root_moisture": "जड़ मिट्टी की नमी",
        "moist_optimal_a": "लक्ष्य: 60% – 75% • अनुकूल नमी",
        "moist_optimal_b": "लक्ष्य: 50% – 65% • अनुकूल नमी",
        "moist_low": "लक्ष्य: 60% – 75% • कम नमी / सूखा",
        "moist_high": "लक्ष्य: 60% – 75% • अधिक नमी / संतृप्त",
        "soil_temp": "मिट्टी का तापमान",
        "air_temp": "हवा का तापमान",
        "canopy_temp": "छतरी तापमान",
        "air_humidity": "हवा की नमी",
        "pump_a_on": "● पंप A चालू — बंद करने के लिए दबाएं",
        "pump_a_off": "○ पंप A बंद — चालू करने के लिए दबाएं",
        "pump_b_on": "● पंप B चालू — बंद करने के लिए दबाएं",
        "pump_b_off": "○ पंप B बंद — चालू करने के लिए दबाएं",
        "alert_normal": "✓ सब ठीक है — कोई कार्रवाई आवश्यक नहीं",
        "alert_low_moist_a": "⚠️ कार्रवाई आवश्यक: खेत A में कम नमी — सिंचाई की सिफारिश",
        "alert_low_moist_b": "⚠️ कार्रवाई आवश्यक: खेत B में कम नमी — सिंचाई की सिफारिश",
        "alert_high_heat": "⚠️ टमाटर के फूलों के लिए अत्यधिक गर्मी का जोखिम (>38°C)",
        "alert_low_battery": "⚠️ रोवर बैटरी कम — डॉकिंग आवश्यक (<20%)",
        "rover_title": "🚜 फील्ड स्काउट रोवर टेलीमेट्री",
        "rover_status_lbl": "रोवर स्थिति",
        "rover_parked": "पार्क किया हुआ / चार्जिंग डॉक",
        "rover_active_a": "खेत A में सक्रिय",
        "rover_active_b": "खेत B में सक्रिय",
        "rover_moving": "गतिशील ({speed} m/s)",
        "rover_battery_lbl": "बैटरी",
        "rover_heading_lbl": "दिशा",
        "rover_stop_btn": "🛑 आपातकालीन रोवर रोकें",
        "rover_stopped_alert": "🛑 रोवर आपातकालीन रोक सक्रिय",
        "btn_fullscreen": "पूर्ण स्क्रीन",
        "btn_exit": "कंसोल बंद करें",
        # AI Crop Diagnostics
        "ai_diagnostics_title": "🔬 एआई फसल दृष्टि निदान (4 मॉडल)",
        "ai_disease_lbl": "रोग",
        "ai_pest_lbl": "कीट",
        "ai_nutrition_lbl": "पोषण",
        "ai_stage_lbl": "चरण",
        "ai_healthy": "स्वस्थ / सामान्य",
        "ai_no_pests": "कीट रहित",
        "ai_optimal_nutrients": "संतुलित",
        "ai_stage_1": "चरण 1: अंकुर",
        "ai_stage_2": "चरण 2: फूल",
        "ai_stage_3": "चरण 3: फल",
        "alert_disease_detected": "⚠️ एआई चेतावनी: {node} में {label} ({conf}%) — कवकनाशी उपचार की सिफारिश",
        "alert_pest_detected": "⚠️ एआई चेतावनी: {node} में {label} ({conf}%) — कीट नियंत्रण आवश्यक",
        "alert_nutrient_deficiency": "⚠️ एआई चेतावनी: {node} में {label} — उर्वरक समायोजन की सिफारिश",
    },
    "pa": {
        "app_title": "🌱 ਐਗਰੀਸਮਾਰਟ ਕੰਸੋਲ — ਟਮਾਟਰ ਫਸਲ ਨਿਗਰਾਨੀ",
        "station_sub": "ਸਥਾਨਕ ਐਜ ਸਟੇਸ਼ਨ • 10.42.0.1:8000 • ਟੀਅਰ 1 ਟੱਚਸਕ੍ਰੀਨ",
        "cloud_linked": "● ਕਲਾਊਡ ਕਨੈਕਟਡ",
        "cloud_buffering": "○ ਬਫਰਿੰਗ ({count} ਕਤਾਰ ਵਿੱਚ)",
        "weather_loading": "ਮੌਸਮ ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...",
        "weather_offline": "ਮੌਸਮ ਕੈਸ਼ (ਆਫਲਾਈਨ)",
        "weather_rain": "ਮੀਂਹ: {prob}%",
        "field_a_title": "🍅 ਟਮਾਟਰ ਖੇਤ A (ਜ਼ੋਨ A)",
        "field_b_title": "🍅 ਟਮਾਟਰ ਖੇਤ B (ਜ਼ੋਨ B)",
        "node_a_sub": "ਨੋਡ: EDGE_01 • ਲੋਰਾ ਚੈਨਲ 1",
        "node_b_sub": "ਨੋਡ: EDGE_02 • ਲੋਰਾ ਚੈਨਲ 2",
        "root_moisture": "ਜੜ੍ਹ ਮਿੱਟੀ ਦੀ ਨਮੀ",
        "moist_optimal_a": "ਨਿਸ਼ਾਨਾ: 60% – 75% • ਸਹੀ ਨਮੀ",
        "moist_optimal_b": "ਨਿਸ਼ਾਨਾ: 50% – 65% • ਸਹੀ ਨਮੀ",
        "moist_low": "ਨਿਸ਼ਾਨਾ: 60% – 75% • ਘੱਟ ਨਮੀ / ਸੁੱਕਾ",
        "moist_high": "ਨਿਸ਼ਾਨਾ: 60% – 75% • ਵੱਧ ਨਮੀ / ਗਿੱਲਾ",
        "soil_temp": "ਮਿੱਟੀ ਦਾ ਤਾਪਮਾਨ",
        "air_temp": "ਹਵਾ ਦਾ ਤਾਪਮਾਨ",
        "canopy_temp": "ਛਤਰੀ ਤਾਪਮਾਨ",
        "air_humidity": "ਹਵਾ ਦੀ ਨਮੀ",
        "pump_a_on": "● ਪੰਪ A ਚਾਲੂ — ਬੰਦ ਕਰਨ ਲਈ ਦਬਾਓ",
        "pump_a_off": "○ ਪੰਪ A ਬੰਦ — ਚਾਲੂ ਕਰਨ ਲਈ ਦਬਾਓ",
        "pump_b_on": "● ਪੰਪ B ਚਾਲੂ — ਬੰਦ ਕਰਨ ਲਈ ਦਬਾਓ",
        "pump_b_off": "○ ਪੰਪ B ਬੰਦ — ਚਾਲੂ ਕਰਨ ਲਈ ਦਬਾਓ",
        "alert_normal": "✓ ਸਭ ਠੀਕ ਹੈ — ਕੋਈ ਕਾਰਵਾਈ ਦੀ ਲੋੜ ਨਹੀਂ",
        "alert_low_moist_a": "⚠️ ਕਾਰਵਾਈ ਦੀ ਲੋੜ: ਖੇਤ A ਵਿੱਚ ਘੱਟ ਨਮੀ — ਸਿੰਚਾਈ ਦੀ ਸਿਫਾਰਸ਼",
        "alert_low_moist_b": "⚠️ ਕਾਰਵਾਈ ਦੀ ਲੋੜ: ਖੇਤ B ਵਿੱਚ ਘੱਟ ਨਮੀ — ਸਿੰਚਾਈ ਦੀ ਸਿਫਾਰਸ਼",
        "alert_high_heat": "⚠️ ਟਮਾਟਰ ਦੇ ਫੁੱਲਾਂ ਲਈ ਵੱਧ ਗਰਮੀ ਦਾ ਖਤਰਾ (>38°C)",
        "alert_low_battery": "⚠️ ਰੋਵਰ ਬੈਟਰੀ ਘੱਟ — ਡੌਕਿੰਗ ਦੀ ਲੋੜ (<20%)",
        "rover_title": "🚜 ਫੀਲਡ ਸਕਾਊਟ ਰੋਵਰ ਟੈਲੀਮੈਟਰੀ",
        "rover_status_lbl": "ਰੋਵਰ ਸਥਿਤੀ",
        "rover_parked": "ਪਾਰਕ ਕੀਤਾ / ਚਾਰਜਿੰਗ ਡੌਕ",
        "rover_active_a": "ਖੇਤ A ਵਿੱਚ ਕੰਮ ਜਾਰੀ",
        "rover_active_b": "ਖੇਤ B ਵਿੱਚ ਕੰਮ ਜਾਰੀ",
        "rover_moving": "ਗਤੀਸ਼ੀਲ ({speed} m/s)",
        "rover_battery_lbl": "ਬੈਟਰੀ",
        "rover_heading_lbl": "ਦਿਸ਼ਾ",
        "rover_stop_btn": "🛑 ਐਮਰਜੈਂਸੀ ਰੋਵਰ ਰੋਕੋ",
        "rover_stopped_alert": "🛑 ਰੋਵਰ ਐਮਰਜੈਂਸੀ ਰੋਕ ਲਾਗੂ",
        "btn_fullscreen": "ਪੂਰੀ ਸਕ੍ਰੀਨ",
        "btn_exit": "ਕੰਸੋਲ ਬੰਦ ਕਰੋ",
        # AI Crop Diagnostics
        "ai_diagnostics_title": "🔬 ਏਆਈ ਫਸਲ ਨਿਰੀਖਣ ਤੇ ਨਿਦਾਨ (4 ਮਾਡਲ)",
        "ai_disease_lbl": "ਬਿਮਾਰੀ",
        "ai_pest_lbl": "ਕੀੜੇ",
        "ai_nutrition_lbl": "ਪੋਸ਼ਣ",
        "ai_stage_lbl": "ਪੜਾਅ",
        "ai_healthy": "ਸਿਹਤਮੰਦ / ਸਹੀ",
        "ai_no_pests": "ਕੋਈ ਕੀੜਾ ਨਹੀਂ",
        "ai_optimal_nutrients": "ਸੰਤੁਲਿਤ",
        "ai_stage_1": "ਪੜਾਅ 1: ਪੌਦਾ",
        "ai_stage_2": "ਪੜਾਅ 2: ਫੁੱਲ",
        "ai_stage_3": "ਪੜਾਅ 3: ਫਲ",
        "alert_disease_detected": "⚠️ ਏਆਈ ਚੇਤਾਵਨੀ: {node} ਵਿੱਚ {label} ({conf}%) — ਸਪਰੇਅ ਦੀ ਸਿਫਾਰਸ਼",
        "alert_pest_detected": "⚠️ ਏਆਈ ਚੇਤਾਵਨੀ: {node} ਵਿੱਚ {label} ({conf}%) — ਕੀਟ ਰੋਕਥਾਮ ਦੀ ਲੋੜ",
        "alert_nutrient_deficiency": "⚠️ ਏਆਈ ਚੇਤਾਵਨੀ: {node} ਵਿੱਚ {label} — ਖਾਦ ਦੀ ਸਿਫਾਰਸ਼",
    }
}


class AgriSmartDisplayGUI:
    """
    Tier 1: Physical On-Device Display GUI for Raspberry Pi Touchscreen (1024x600 / 800x480).
    Color Palette Graded: #051F20, #0B2B26, #163832, #235347, #8EB69B, #DAF1DE.
    """

    BG_DARK = "#f0f7f2"        # Luminous Soft Mint Canvas
    CARD_BG = "#ffffff"        # Elevated White Panel
    INNER_BG = "#daf1de"       # Soft Pale Mint Metric Box
    BORDER_COLOR = "#8eb69b"   # Soft Sage Border
    BORDER_GLOW = "#235347"    # Forest Sage Glow
    TEXT_MAIN = "#051f20"      # Forest Noir (Darkest Pine)
    TEXT_MUTED = "#163832"     # Dark Spruce
    TEXT_ACCENT = "#235347"    # Forest Sage
    
    # Semantic Accents
    AMBER_PRIMARY = "#235347"  # Forest Sage Primary
    SLATE_PRIMARY = "#163832"  # Dark Spruce
    DEEP_SLATE = "#051f20"     # Forest Noir
    GREEN_ON = "#235347"       # Active Forest Sage
    GREEN_TEXT = "#051f20"     # Forest Readout
    GREEN_ALERT_BG = "#daf1de" # Pale Mint Alert Banner
    GREEN_ALERT_BORDER = "#8eb69b"
    
    AMBER_WARN = "#8eb69b"     # Soft Sage Warning
    AMBER_ALERT_BG = "#daf1de" # Pale Mint Alert Banner
    AMBER_ALERT_BORDER = "#8eb69b"
    
    RED_STOP = "#be123c"       # Emergency Rose
    RED_ACTIVE = "#e11d48"
    RED_ALERT_BG = "#fef2f2"   # Light Red Alert Banner
    RED_ALERT_BORDER = "#fecaca"
    
    BLUE_ACCENT = "#163832"    # Dark Spruce
    ORANGE_TEMP = "#235347"    # Forest Sage Temp
    CYAN_HUMID = "#235347"     # Humidity
    PURPLE_ACCENT = "#051f20"  # Stage
    
    BTN_IDLE = "#daf1de"       # Idle Actuator Button
    BTN_IDLE_HOVER = "#8eb69b"
    BTN_ACTIVE_LANG = "#051f20"# Highlighted Language Pill

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AgriSmart Field Console — Tier 1")
        self.root.configure(bg=self.BG_DARK)
        
        # Default active language: English ('en')
        self.current_lang = "en"

        # Center 1024x600 window by default (fits Raspberry Pi Official 7" touch)
        win_w, win_h = 1024, 600
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h) // 2)
        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.root.minsize(800, 480)

        # Fullscreen handling (F11 = Toggle, Escape = Exit Fullscreen)
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        # Initialize SQLite database
        database.init_db()

        # Build UI Components
        self._setup_styles()
        self._build_header()
        self._build_alert_banner()
        self._build_ai_diagnostics_strip()
        self._build_zone_cards()
        self._build_rover_bottom_panel()

        # Update initial text translations
        self._apply_translations()

        # Start non-blocking polling loop (every 1000ms)
        self.poll_data()

    def t(self, key: str, **kwargs) -> str:
        """Retrieves translated text for the current active language with variable formatting."""
        lang_dict = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        template = lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
        if kwargs:
            try:
                return template.format(**kwargs)
            except Exception:
                return template
        return template

    def _setup_styles(self):
        """Prepares standard system font families with fallback for Unicode Hindi and Punjabi."""
        if sys.platform == "win32":
            family = "Segoe UI"
            family_bold = "Segoe UI"
        else:
            family = "DejaVu Sans"
            family_bold = "DejaVu Sans"

        self.font_brand = (family_bold, 12, "bold")
        self.font_clock = (family_bold, 13, "bold")
        self.font_weather = (family, 10, "bold")
        self.font_small = (family, 9)
        self.font_small_bold = (family_bold, 9, "bold")
        self.font_badge = (family_bold, 9, "bold")
        self.font_zone_title = (family_bold, 12, "bold")
        self.font_big_num = (family_bold, 24, "bold")
        self.font_metric_lbl = (family_bold, 8, "bold")
        self.font_metric_val = (family_bold, 12, "bold")
        self.font_btn = (family_bold, 10, "bold")
        self.font_alert = (family_bold, 10, "bold")
        self.font_lang_btn = (family_bold, 9, "bold")
        self.font_ai_badge = (family_bold, 9, "bold")

    # ==========================================================================
    # UI BUILDERS
    # ==========================================================================
    def _build_header(self):
        """Builds top status bar: Brand, Weather Snapshot, Digital Clock, Trilingual Selector, Cloud Sync."""
        self.header_frame = tk.Frame(
            self.root,
            bg=self.CARD_BG,
            height=56,
            padx=14,
            pady=6,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        self.header_frame.pack_propagate(False)

        # 1. Left: Station Brand Title & IP
        self.box_brand = tk.Frame(self.header_frame, bg=self.CARD_BG)
        self.box_brand.pack(side=tk.LEFT, fill=tk.Y)
        
        self.lbl_brand = tk.Label(
            self.box_brand,
            text="",
            font=self.font_brand,
            fg=self.TEXT_MAIN,
            bg=self.CARD_BG
        )
        self.lbl_brand.pack(anchor="w")
        
        self.lbl_sub = tk.Label(
            self.box_brand,
            text="",
            font=self.font_small,
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG
        )
        self.lbl_sub.pack(anchor="w")

        # 2. Center-Left: Weather Snapshot Widget
        self.box_weather = tk.Frame(
            self.header_frame,
            bg=self.INNER_BG,
            padx=10,
            pady=3,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        self.box_weather.pack(side=tk.LEFT, padx=(14, 0))

        self.lbl_weather = tk.Label(
            self.box_weather,
            text="⛅ Weather Loading...",
            font=self.font_weather,
            fg=self.AMBER_PRIMARY,
            bg=self.INNER_BG
        )
        self.lbl_weather.pack(anchor="w")
        
        self.lbl_weather_detail = tk.Label(
            self.box_weather,
            text="Rain: 0% • Forecast 7-Day",
            font=self.font_small,
            fg=self.TEXT_MUTED,
            bg=self.INNER_BG
        )
        self.lbl_weather_detail.pack(anchor="w")

        # 3. Center-Right: Live Digital Clock & Date
        self.box_clock = tk.Frame(self.header_frame, bg=self.CARD_BG)
        self.box_clock.pack(side=tk.LEFT, expand=True)

        self.lbl_clock = tk.Label(
            self.box_clock,
            text="--:--:--",
            font=self.font_clock,
            fg=self.TEXT_MAIN,
            bg=self.CARD_BG
        )
        self.lbl_clock.pack()
        self.lbl_date = tk.Label(
            self.box_clock,
            text="Loading date...",
            font=self.font_small,
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG
        )
        self.lbl_date.pack()

        # 4. Right: Trilingual Switcher Buttons [ EN | HI | PA ]
        self.box_lang = tk.Frame(self.header_frame, bg=self.CARD_BG)
        self.box_lang.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))

        self.btn_lang_en = tk.Button(
            self.box_lang,
            text="EN",
            font=self.font_lang_btn,
            bg=self.BTN_ACTIVE_LANG,
            fg="#ffffff",
            activebackground=self.AMBER_PRIMARY,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=8,
            pady=3,
            cursor="hand2",
            command=lambda: self.set_language("en")
        )
        self.btn_lang_en.pack(side=tk.LEFT, padx=1)

        self.btn_lang_hi = tk.Button(
            self.box_lang,
            text="हिन्दी",
            font=self.font_lang_btn,
            bg=self.BTN_IDLE,
            fg=self.TEXT_MUTED,
            activebackground=self.BTN_IDLE_HOVER,
            activeforeground=self.TEXT_MAIN,
            relief=tk.FLAT,
            padx=8,
            pady=3,
            cursor="hand2",
            command=lambda: self.set_language("hi")
        )
        self.btn_lang_hi.pack(side=tk.LEFT, padx=1)

        self.btn_lang_pa = tk.Button(
            self.box_lang,
            text="ਪੰਜਾਬੀ",
            font=self.font_lang_btn,
            bg=self.BTN_IDLE,
            fg=self.TEXT_MUTED,
            activebackground=self.BTN_IDLE_HOVER,
            activeforeground=self.TEXT_MAIN,
            relief=tk.FLAT,
            padx=8,
            pady=3,
            cursor="hand2",
            command=lambda: self.set_language("pa")
        )
        self.btn_lang_pa.pack(side=tk.LEFT, padx=1)

        # 5. Far Right: Cloud Sync Health Badge
        self.box_sync = tk.Frame(self.header_frame, bg=self.CARD_BG)
        self.box_sync.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 8))

        self.lbl_sync_badge = tk.Label(
            self.box_sync,
            text="● CLOUD LINKED",
            font=self.font_badge,
            fg=self.GREEN_TEXT,
            bg=self.INNER_BG,
            padx=8,
            pady=4,
            relief=tk.FLAT,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        self.lbl_sync_badge.pack(pady=4)

    def _build_alert_banner(self):
        """Dedicated dynamic 'Action Needed' alert bar sitting beneath the header."""
        self.alert_frame = tk.Frame(
            self.root,
            bg=self.GREEN_ALERT_BG,
            padx=16,
            pady=6,
            highlightbackground=self.GREEN_ALERT_BORDER,
            highlightthickness=1
        )
        self.alert_frame.pack(side=tk.TOP, fill=tk.X, padx=12, pady=(6, 0))

        self.lbl_alert_msg = tk.Label(
            self.alert_frame,
            text="✓ All Systems Normal — No Action Required",
            font=self.font_alert,
            fg=self.GREEN_TEXT,
            bg=self.GREEN_ALERT_BG,
            anchor="w"
        )
        self.lbl_alert_msg.pack(fill=tk.X)

    def _build_ai_diagnostics_strip(self):
        """Builds a responsive 4-model AI vision diagnostics status strip across the top."""
        self.ai_strip = tk.Frame(
            self.root,
            bg=self.CARD_BG,
            padx=8,
            pady=4,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        self.ai_strip.pack(side=tk.TOP, fill=tk.X, padx=12, pady=(6, 0))
        self.ai_strip.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="ai_col")

        # 1. Disease Model Badge Box
        self.box_ai_disease = tk.Frame(self.ai_strip, bg=self.INNER_BG, padx=8, pady=4, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        self.box_ai_disease.grid(row=0, column=0, sticky="nsew", padx=2)
        self.lbl_ai_disease_title = tk.Label(self.box_ai_disease, text="🦠 DISEASE", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG)
        self.lbl_ai_disease_title.pack(anchor="w")
        self.lbl_ai_disease_val = tk.Label(self.box_ai_disease, text="Healthy / Clear", font=self.font_ai_badge, fg=self.GREEN_TEXT, bg=self.INNER_BG)
        self.lbl_ai_disease_val.pack(anchor="w")

        # 2. Pest Model Badge Box
        self.box_ai_pest = tk.Frame(self.ai_strip, bg=self.INNER_BG, padx=8, pady=4, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        self.box_ai_pest.grid(row=0, column=1, sticky="nsew", padx=2)
        self.lbl_ai_pest_title = tk.Label(self.box_ai_pest, text="🐛 PEST SCOUT", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG)
        self.lbl_ai_pest_title.pack(anchor="w")
        self.lbl_ai_pest_val = tk.Label(self.box_ai_pest, text="No Pests", font=self.font_ai_badge, fg=self.GREEN_TEXT, bg=self.INNER_BG)
        self.lbl_ai_pest_val.pack(anchor="w")

        # 3. Nutrition Model Badge Box
        self.box_ai_nutr = tk.Frame(self.ai_strip, bg=self.INNER_BG, padx=8, pady=4, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        self.box_ai_nutr.grid(row=0, column=2, sticky="nsew", padx=2)
        self.lbl_ai_nutr_title = tk.Label(self.box_ai_nutr, text="🧪 NUTRITION", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG)
        self.lbl_ai_nutr_title.pack(anchor="w")
        self.lbl_ai_nutr_val = tk.Label(self.box_ai_nutr, text="Balanced", font=self.font_ai_badge, fg=self.AMBER_PRIMARY, bg=self.INNER_BG)
        self.lbl_ai_nutr_val.pack(anchor="w")

        # 4. Growth Stage Model Badge Box
        self.box_ai_stage = tk.Frame(self.ai_strip, bg=self.INNER_BG, padx=8, pady=4, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        self.box_ai_stage.grid(row=0, column=3, sticky="nsew", padx=2)
        self.lbl_ai_stage_title = tk.Label(self.box_ai_stage, text="🍅 STAGE", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG)
        self.lbl_ai_stage_title.pack(anchor="w")
        self.lbl_ai_stage_val = tk.Label(self.box_ai_stage, text="Stage 2: Blossom", font=self.font_ai_badge, fg=self.PURPLE_ACCENT, bg=self.INNER_BG)
        self.lbl_ai_stage_val.pack(anchor="w")

    def _build_zone_cards(self):
        """Builds side-by-side telemetry cards for Tomato Field A and Tomato Field B."""
        self.cards_container = tk.Frame(self.root, bg=self.BG_DARK, padx=12, pady=6)
        self.cards_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.cards_container.grid_columnconfigure(0, weight=1, uniform="group1")
        self.cards_container.grid_columnconfigure(1, weight=1, uniform="group1")
        self.cards_container.grid_rowconfigure(0, weight=1)

        # =============================================================
        # TOMATO FIELD A CARD (ZONE A)
        # =============================================================
        self.card_a = tk.Frame(
            self.cards_container,
            bg=self.CARD_BG,
            padx=12,
            pady=6,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        self.card_a.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        # Zone A Header Row
        hdr_a = tk.Frame(self.card_a, bg=self.CARD_BG)
        hdr_a.pack(fill=tk.X, pady=(0, 2))
        self.lbl_hdr_a = tk.Label(hdr_a, text="", font=self.font_zone_title, fg=self.TEXT_MAIN, bg=self.CARD_BG)
        self.lbl_hdr_a.pack(side=tk.LEFT)
        self.lbl_node_a = tk.Label(hdr_a, text="", font=self.font_small, fg=self.TEXT_MUTED, bg=self.CARD_BG)
        self.lbl_node_a.pack(side=tk.RIGHT)

        # Zone A Moisture Hero Box with Custom Arc Canvas
        moist_box_a = tk.Frame(
            self.card_a,
            bg=self.INNER_BG,
            padx=8,
            pady=4,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        moist_box_a.pack(fill=tk.X, pady=(0, 4))
        
        self.lbl_moist_title_a = tk.Label(
            moist_box_a,
            text="",
            font=self.font_metric_lbl,
            fg=self.TEXT_MUTED,
            bg=self.INNER_BG
        )
        self.lbl_moist_title_a.pack(anchor="w")

        # Inner container with Canvas Arc + Big Number
        arc_box_a = tk.Frame(moist_box_a, bg=self.INNER_BG)
        arc_box_a.pack(fill=tk.X)

        self.canvas_arc_a = tk.Canvas(
            arc_box_a,
            width=90,
            height=46,
            bg=self.INNER_BG,
            highlightthickness=0
        )
        self.canvas_arc_a.pack(side=tk.LEFT, padx=(4, 10))

        self.lbl_za_moist = tk.Label(
            arc_box_a,
            text="--.-%",
            font=self.font_big_num,
            fg=self.AMBER_PRIMARY,
            bg=self.INNER_BG
        )
        self.lbl_za_moist.pack(side=tk.LEFT)
        
        self.lbl_za_moist_status = tk.Label(
            moist_box_a,
            text="",
            font=self.font_small_bold,
            fg=self.GREEN_TEXT,
            bg=self.INNER_BG
        )
        self.lbl_za_moist_status.pack(anchor="w")

        # Zone A Secondary Metrics (Soil Temp, Canopy Temp, Air Humidity)
        grid_a = tk.Frame(self.card_a, bg=self.CARD_BG)
        grid_a.pack(fill=tk.X, pady=(0, 4))
        grid_a.grid_columnconfigure((0, 1, 2), weight=1, uniform="submetric_a")

        # Metric 1: Soil Temp
        m1_a = tk.Frame(grid_a, bg=self.INNER_BG, padx=6, pady=3, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        m1_a.grid(row=0, column=0, sticky="nsew", padx=2)
        self.lbl_soil_temp_lbl_a = tk.Label(m1_a, text="", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG)
        self.lbl_soil_temp_lbl_a.pack(anchor="w")
        self.lbl_za_soil_temp = tk.Label(m1_a, text="--°C", font=self.font_metric_val, fg=self.BLUE_ACCENT, bg=self.INNER_BG)
        self.lbl_za_soil_temp.pack(anchor="w")

        # Metric 2: Canopy / Air Temp
        m2_a = tk.Frame(grid_a, bg=self.INNER_BG, padx=6, pady=3, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        m2_a.grid(row=0, column=1, sticky="nsew", padx=2)
        self.lbl_air_temp_lbl_a = tk.Label(m2_a, text="", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG)
        self.lbl_air_temp_lbl_a.pack(anchor="w")
        self.lbl_za_amb_temp = tk.Label(m2_a, text="--°C", font=self.font_metric_val, fg=self.ORANGE_TEMP, bg=self.INNER_BG)
        self.lbl_za_amb_temp.pack(anchor="w")

        # Metric 3: Air Humidity
        m3_a = tk.Frame(grid_a, bg=self.INNER_BG, padx=6, pady=3, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        m3_a.grid(row=0, column=2, sticky="nsew", padx=2)
        self.lbl_humid_lbl_a = tk.Label(m3_a, text="", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG)
        self.lbl_humid_lbl_a.pack(anchor="w")
        self.lbl_za_humid = tk.Label(m3_a, text="--%", font=self.font_metric_val, fg=self.CYAN_HUMID, bg=self.INNER_BG)
        self.lbl_za_humid.pack(anchor="w")

        # Zone A Touch-Friendly Pump Relay Button
        self.btn_pump_a = tk.Button(
            self.card_a,
            text="",
            font=self.font_btn,
            bg=self.BTN_IDLE,
            fg=self.TEXT_MAIN,
            activebackground=self.BTN_IDLE_HOVER,
            activeforeground=self.TEXT_MAIN,
            relief=tk.FLAT,
            height=2,
            cursor="hand2",
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1,
            command=lambda: self.toggle_pump("PUMP_ZONE_A")
        )
        self.btn_pump_a.pack(fill=tk.X, side=tk.BOTTOM, pady=(4, 0))

        # =============================================================
        # TOMATO FIELD B CARD (ZONE B)
        # =============================================================
        self.card_b = tk.Frame(
            self.cards_container,
            bg=self.CARD_BG,
            padx=12,
            pady=6,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        self.card_b.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # Zone B Header Row
        hdr_b = tk.Frame(self.card_b, bg=self.CARD_BG)
        hdr_b.pack(fill=tk.X, pady=(0, 2))
        self.lbl_hdr_b = tk.Label(hdr_b, text="", font=self.font_zone_title, fg=self.TEXT_MAIN, bg=self.CARD_BG)
        self.lbl_hdr_b.pack(side=tk.LEFT)
        self.lbl_node_b = tk.Label(hdr_b, text="", font=self.font_small, fg=self.TEXT_MUTED, bg=self.CARD_BG)
        self.lbl_node_b.pack(side=tk.RIGHT)

        # Zone B Moisture Hero Box with Custom Arc Canvas
        moist_box_b = tk.Frame(
            self.card_b,
            bg=self.INNER_BG,
            padx=8,
            pady=4,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        moist_box_b.pack(fill=tk.X, pady=(0, 4))
        
        self.lbl_moist_title_b = tk.Label(
            moist_box_b,
            text="",
            font=self.font_metric_lbl,
            fg=self.TEXT_MUTED,
            bg=self.INNER_BG
        )
        self.lbl_moist_title_b.pack(anchor="w")

        # Inner container with Canvas Arc + Big Number
        arc_box_b = tk.Frame(moist_box_b, bg=self.INNER_BG)
        arc_box_b.pack(fill=tk.X)

        self.canvas_arc_b = tk.Canvas(
            arc_box_b,
            width=90,
            height=46,
            bg=self.INNER_BG,
            highlightthickness=0
        )
        self.canvas_arc_b.pack(side=tk.LEFT, padx=(4, 10))

        self.lbl_zb_moist = tk.Label(
            arc_box_b,
            text="--.-%",
            font=self.font_big_num,
            fg=self.AMBER_PRIMARY,
            bg=self.INNER_BG
        )
        self.lbl_zb_moist.pack(side=tk.LEFT)
        
        self.lbl_zb_moist_status = tk.Label(
            moist_box_b,
            text="",
            font=self.font_small_bold,
            fg=self.GREEN_TEXT,
            bg=self.INNER_BG
        )
        self.lbl_zb_moist_status.pack(anchor="w")

        # Zone B Secondary Metrics (Soil Temp, Canopy Temp, Air Humidity)
        grid_b = tk.Frame(self.card_b, bg=self.CARD_BG)
        grid_b.pack(fill=tk.X, pady=(0, 4))
        grid_b.grid_columnconfigure((0, 1, 2), weight=1, uniform="submetric_b")

        # Metric 1: Soil Temp
        m1_b = tk.Frame(grid_b, bg=self.INNER_BG, padx=6, pady=3, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        m1_b.grid(row=0, column=0, sticky="nsew", padx=2)
        self.lbl_soil_temp_lbl_b = tk.Label(m1_b, text="", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG)
        self.lbl_soil_temp_lbl_b.pack(anchor="w")
        self.lbl_zb_soil_temp = tk.Label(m1_b, text="--°C", font=self.font_metric_val, fg=self.BLUE_ACCENT, bg=self.INNER_BG)
        self.lbl_zb_soil_temp.pack(anchor="w")

        # Metric 2: Canopy / Air Temp
        m2_b = tk.Frame(grid_b, bg=self.INNER_BG, padx=6, pady=3, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        m2_b.grid(row=0, column=1, sticky="nsew", padx=2)
        self.lbl_air_temp_lbl_b = tk.Label(m2_b, text="", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG)
        self.lbl_air_temp_lbl_b.pack(anchor="w")
        self.lbl_zb_amb_temp = tk.Label(m2_b, text="--°C", font=self.font_metric_val, fg=self.ORANGE_TEMP, bg=self.INNER_BG)
        self.lbl_zb_amb_temp.pack(anchor="w")

        # Metric 3: Air Humidity
        m3_b = tk.Frame(grid_b, bg=self.INNER_BG, padx=6, pady=3, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        m3_b.grid(row=0, column=2, sticky="nsew", padx=2)
        self.lbl_humid_lbl_b = tk.Label(m3_b, text="", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG)
        self.lbl_humid_lbl_b.pack(anchor="w")
        self.lbl_zb_humid = tk.Label(m3_b, text="--%", font=self.font_metric_val, fg=self.CYAN_HUMID, bg=self.INNER_BG)
        self.lbl_zb_humid.pack(anchor="w")

        # Zone B Touch-Friendly Pump Relay Button
        self.btn_pump_b = tk.Button(
            self.card_b,
            text="",
            font=self.font_btn,
            bg=self.BTN_IDLE,
            fg=self.TEXT_MAIN,
            activebackground=self.BTN_IDLE_HOVER,
            activeforeground=self.TEXT_MAIN,
            relief=tk.FLAT,
            height=2,
            cursor="hand2",
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1,
            command=lambda: self.toggle_pump("PUMP_ZONE_B")
        )
        self.btn_pump_b.pack(fill=tk.X, side=tk.BOTTOM, pady=(4, 0))

    def _render_moisture_arc(self, canvas: tk.Canvas, pct: float):
        """Draws a smooth glowing semicircular gauge on the Tkinter canvas."""
        canvas.delete("all")
        cx, cy, r = 45, 42, 36
        
        # Background arc
        canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=0, extent=180,
            style=tk.ARC,
            outline=self.BORDER_COLOR,
            width=6
        )

        # Active progress arc
        extent = min(180, max(0, (pct / 100.0) * 180.0))
        arc_color = self.AMBER_PRIMARY if pct < 75 else self.GREEN_ON
        if pct < 40:
            arc_color = self.RED_STOP
        
        canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=180, extent=-extent,
            style=tk.ARC,
            outline=arc_color,
            width=6
        )

    def _build_rover_bottom_panel(self):
        """Builds bottom bar with Rover Scout Telemetry, Dynamic Battery Meter, Emergency Stop & Exit."""
        self.bottom_frame = tk.Frame(
            self.root,
            bg=self.CARD_BG,
            height=52,
            padx=12,
            pady=5,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=(0, 6))
        self.bottom_frame.pack_propagate(False)

        # Left: Rover Status Badge
        self.box_rover_left = tk.Frame(self.bottom_frame, bg=self.CARD_BG)
        self.box_rover_left.pack(side=tk.LEFT, fill=tk.Y)

        self.lbl_rover_badge = tk.Label(
            self.box_rover_left,
            text="🚜 ROVER:",
            font=self.font_badge,
            fg=self.TEXT_MAIN,
            bg=self.CARD_BG
        )
        self.lbl_rover_badge.pack(side=tk.LEFT, padx=(0, 6))

        self.lbl_rover_status = tk.Label(
            self.box_rover_left,
            text="Parked / Charging Dock",
            font=self.font_small_bold,
            fg=self.GREEN_TEXT,
            bg=self.INNER_BG,
            padx=8,
            pady=2,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        self.lbl_rover_status.pack(side=tk.LEFT, padx=(0, 10))

        # Battery Status & Visual Progress Bar
        self.lbl_battery_title = tk.Label(
            self.box_rover_left,
            text="🔋 84%",
            font=self.font_small_bold,
            fg=self.GREEN_TEXT,
            bg=self.CARD_BG
        )
        self.lbl_battery_title.pack(side=tk.LEFT, padx=(0, 4))

        self.canvas_battery = tk.Canvas(
            self.box_rover_left,
            width=50,
            height=14,
            bg=self.INNER_BG,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        self.canvas_battery.pack(side=tk.LEFT, padx=(0, 10))
        self._render_battery_bar(84)

        # Rover Heading & Speed
        self.lbl_rover_telemetry = tk.Label(
            self.box_rover_left,
            text="NW (312°) • 0.0 m/s",
            font=self.font_small,
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG
        )
        self.lbl_rover_telemetry.pack(side=tk.LEFT)

        # Right: Emergency Stop & Exit / Fullscreen Buttons
        self.box_rover_right = tk.Frame(self.bottom_frame, bg=self.CARD_BG)
        self.box_rover_right.pack(side=tk.RIGHT, fill=tk.Y)

        self.btn_exit = tk.Button(
            self.box_rover_right,
            text="",
            font=self.font_small,
            bg=self.BTN_IDLE,
            fg=self.TEXT_MUTED,
            activebackground=self.BTN_IDLE_HOVER,
            activeforeground=self.TEXT_MAIN,
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.root.destroy
        )
        self.btn_exit.pack(side=tk.RIGHT, padx=(4, 0))

        self.btn_fullscreen = tk.Button(
            self.box_rover_right,
            text="",
            font=self.font_small,
            bg=self.BTN_IDLE,
            fg=self.TEXT_MUTED,
            activebackground=self.BTN_IDLE_HOVER,
            activeforeground=self.TEXT_MAIN,
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.toggle_fullscreen
        )
        self.btn_fullscreen.pack(side=tk.RIGHT, padx=(4, 0))

        self.btn_stop_rover = tk.Button(
            self.box_rover_right,
            text="",
            font=self.font_btn,
            bg=self.RED_STOP,
            fg="#ffffff",
            activebackground=self.RED_ACTIVE,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=12,
            pady=3,
            cursor="hand2",
            command=self.emergency_stop_rover
        )
        self.btn_stop_rover.pack(side=tk.RIGHT, padx=(0, 6))

    # ==========================================================================
    # LOCALIZATION & ACTIONS
    # ==========================================================================
    def set_language(self, lang_code: str):
        """Switches GUI language on the fly and updates button styles."""
        if lang_code not in TRANSLATIONS:
            return
        self.current_lang = lang_code

        for code, btn in [("en", self.btn_lang_en), ("hi", self.btn_lang_hi), ("pa", self.btn_lang_pa)]:
            if code == lang_code:
                btn.configure(bg=self.BTN_ACTIVE_LANG, fg="#ffffff")
            else:
                btn.configure(bg=self.BTN_IDLE, fg=self.TEXT_MUTED)

        self._apply_translations()
        self._update_ui_state()

    def _apply_translations(self):
        """Updates static string references across all Tkinter labels."""
        self.lbl_brand.configure(text=self.t("app_title"))
        self.lbl_sub.configure(text=self.t("station_sub"))
        self.lbl_hdr_a.configure(text=self.t("field_a_title"))
        self.lbl_hdr_b.configure(text=self.t("field_b_title"))
        self.lbl_node_a.configure(text=self.t("node_a_sub"))
        self.lbl_node_b.configure(text=self.t("node_b_sub"))
        self.lbl_moist_title_a.configure(text=self.t("root_moisture"))
        self.lbl_moist_title_b.configure(text=self.t("root_moisture"))
        self.lbl_soil_temp_lbl_a.configure(text=self.t("soil_temp"))
        self.lbl_soil_temp_lbl_b.configure(text=self.t("soil_temp"))
        self.lbl_air_temp_lbl_a.configure(text=self.t("canopy_temp"))
        self.lbl_air_temp_lbl_b.configure(text=self.t("canopy_temp"))
        self.lbl_humid_lbl_a.configure(text=self.t("air_humidity"))
        self.lbl_humid_lbl_b.configure(text=self.t("air_humidity"))
        self.btn_stop_rover.configure(text=self.t("rover_stop_btn"))
        self.btn_fullscreen.configure(text=self.t("btn_fullscreen"))
        self.btn_exit.configure(text=self.t("btn_exit"))
        
        # AI Labels
        self.lbl_ai_disease_title.configure(text=f"🦠 {self.t('ai_disease_lbl').upper()}")
        self.lbl_ai_pest_title.configure(text=f"🐛 {self.t('ai_pest_lbl').upper()}")
        self.lbl_ai_nutr_title.configure(text=f"🧪 {self.t('ai_nutrition_lbl').upper()}")
        self.lbl_ai_stage_title.configure(text=f"🍅 {self.t('ai_stage_lbl').upper()}")

    def toggle_pump(self, target: str):
        """Toggles actuator state in SQLite database and refreshes GUI."""
        database.toggle_actuator_state(target)
        self._update_ui_state()

    def emergency_stop_rover(self):
        """Sends immediate STOP action to rover in SQLite."""
        database.update_rover_command("STOP")
        self._update_ui_state()

    def toggle_fullscreen(self, event=None):
        """Toggles fullscreen mode."""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        """Exits fullscreen mode."""
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)

    # ==========================================================================
    # DATA REFRESH & POLLING LOOP
    # ==========================================================================
    def poll_data(self):
        """1-second timer loop for continuous database synchronization."""
        self._update_ui_state()
        self.root.after(1000, self.poll_data)

    def _update_ui_state(self):
        """Reads latest values from SQLite and updates all graphical widgets."""
        now = datetime.now()
        self.lbl_clock.configure(text=now.strftime("%H:%M:%S"))
        self.lbl_date.configure(text=now.strftime("%A, %d %b %Y"))

        # Fetch telemetry
        t_za = database.get_latest_telemetry("ZONE_A")
        t_zb = database.get_latest_telemetry("ZONE_B")
        actuators = database.get_all_actuators()
        rover = database.get_rover_state()
        stats = database.get_edge_stats()
        weather = database.get_cached_weather()
        ai_summary = database.get_latest_ai_summary()

        # 1. Update Zone A Telemetry
        if t_za:
            moist_a = float(t_za.get("soil_moisture", 0.0))
            self.lbl_za_moist.configure(text=f"{moist_a:.1f}%")
            self._render_moisture_arc(self.canvas_arc_a, moist_a)
            if 60.0 <= moist_a <= 75.0:
                self.lbl_za_moist.configure(fg=self.AMBER_PRIMARY)
                self.lbl_za_moist_status.configure(text=self.t("moist_optimal_a"), fg=self.GREEN_TEXT)
            elif moist_a < 60.0:
                self.lbl_za_moist.configure(fg=self.AMBER_WARN)
                self.lbl_za_moist_status.configure(text=self.t("moist_low"), fg=self.AMBER_WARN)
            else:
                self.lbl_za_moist.configure(fg=self.BLUE_ACCENT)
                self.lbl_za_moist_status.configure(text=self.t("moist_high"), fg=self.BLUE_ACCENT)

            self.lbl_za_soil_temp.configure(text=f"{t_za.get('soil_temp', 0):.1f}°C")
            self.lbl_za_amb_temp.configure(text=f"{t_za.get('canopy_temp', t_za.get('ambient_temp', 0)):.1f}°C")
            self.lbl_za_humid.configure(text=f"{t_za.get('ambient_humidity', 0):.1f}%")

        # 2. Update Zone B Telemetry
        if t_zb:
            moist_b = float(t_zb.get("soil_moisture", 0.0))
            self.lbl_zb_moist.configure(text=f"{moist_b:.1f}%")
            self._render_moisture_arc(self.canvas_arc_b, moist_b)
            if 50.0 <= moist_b <= 65.0:
                self.lbl_zb_moist.configure(fg=self.AMBER_PRIMARY)
                self.lbl_zb_moist_status.configure(text=self.t("moist_optimal_b"), fg=self.GREEN_TEXT)
            elif moist_b < 50.0:
                self.lbl_zb_moist.configure(fg=self.AMBER_WARN)
                self.lbl_zb_moist_status.configure(text=self.t("moist_low"), fg=self.AMBER_WARN)
            else:
                self.lbl_zb_moist.configure(fg=self.BLUE_ACCENT)
                self.lbl_zb_moist_status.configure(text=self.t("moist_high"), fg=self.BLUE_ACCENT)

            self.lbl_zb_soil_temp.configure(text=f"{t_zb.get('soil_temp', 0):.1f}°C")
            self.lbl_zb_amb_temp.configure(text=f"{t_zb.get('canopy_temp', t_zb.get('ambient_temp', 0)):.1f}°C")
            self.lbl_zb_humid.configure(text=f"{t_zb.get('ambient_humidity', 0):.1f}%")

        # 3. Update Actuator Buttons
        pump_a_on = bool(actuators.get("PUMP_ZONE_A", 0))
        if pump_a_on:
            self.btn_pump_a.configure(text=self.t("pump_a_on"), bg=self.GREEN_ON, fg="#ffffff")
        else:
            self.btn_pump_a.configure(text=self.t("pump_a_off"), bg=self.BTN_IDLE, fg=self.TEXT_MAIN)

        pump_b_on = bool(actuators.get("PUMP_ZONE_B", 0))
        if pump_b_on:
            self.btn_pump_b.configure(text=self.t("pump_b_on"), bg=self.GREEN_ON, fg="#ffffff")
        else:
            self.btn_pump_b.configure(text=self.t("pump_b_off"), bg=self.BTN_IDLE, fg=self.TEXT_MAIN)

        # 4. Update Rover Telemetry
        if rover:
            act = rover.get("last_action", "STOP")
            if act == "STOP":
                self.lbl_rover_status.configure(text=self.t("rover_parked"), fg=self.GREEN_TEXT)
            else:
                speed = rover.get("speed", 0.6)
                self.lbl_rover_status.configure(text=self.t("rover_moving", speed=f"{speed:.1f}"), fg=self.AMBER_WARN)

            batt = int(rover.get("battery", 80))
            self.lbl_battery_title.configure(text=f"🔋 {batt}%")
            self._render_battery_bar(batt)
            
            heading = rover.get("heading", 312)
            speed_val = rover.get("speed", 0.0)
            self.lbl_rover_telemetry.configure(text=f"NW ({heading}°) • {speed_val:.1f} m/s")

        # 5. Update Cloud Sync Badge
        unsynced = stats.get("unsynced_records", 0) if stats else 0
        if unsynced == 0:
            self.lbl_sync_badge.configure(text=self.t("cloud_linked"), fg=self.GREEN_TEXT)
        else:
            self.lbl_sync_badge.configure(text=self.t("cloud_buffering", count=unsynced), fg=self.AMBER_WARN)

        # 6. Update Weather Snapshot
        if weather and "days" in weather and len(weather["days"]) > 0:
            today_w = weather["days"][0]
            cond = today_w.get("condition", "Optimal")
            t_max = today_w.get("temp_max", 30.0)
            rain_p = today_w.get("rain_prob", 0)
            self.lbl_weather.configure(text=f"⛅ {cond} ({t_max:.1f}°C)")
            self.lbl_weather_detail.configure(text=f"{self.t('weather_rain', prob=rain_p)} • 7-Day Cached")

        # 7. Update AI Diagnostics Badges
        if ai_summary:
            if ai_summary.get("disease"):
                d = ai_summary["disease"]
                lbl = d.get("detection_label", "Healthy")
                conf = int((d.get("confidence", 0.95)) * 100)
                self.lbl_ai_disease_val.configure(
                    text=f"{lbl} ({conf}%)",
                    fg=self.RED_ACTIVE if "blight" in lbl.lower() or "spot" in lbl.lower() else self.GREEN_TEXT
                )
            if ai_summary.get("pest"):
                p = ai_summary["pest"]
                lbl = p.get("detection_label", "No Pests")
                conf = int((p.get("confidence", 0.94)) * 100)
                self.lbl_ai_pest_val.configure(
                    text=f"{lbl} ({conf}%)",
                    fg=self.RED_ACTIVE if "pest" in lbl.lower() or "fly" in lbl.lower() else self.GREEN_TEXT
                )
            if ai_summary.get("nutrition"):
                n = ai_summary["nutrition"]
                lbl = n.get("detection_label", "Balanced")
                self.lbl_ai_nutr_val.configure(
                    text=lbl,
                    fg=self.AMBER_WARN if "deficiency" in lbl.lower() else self.GREEN_TEXT
                )
            if ai_summary.get("stage"):
                s = ai_summary["stage"]
                lbl = s.get("detection_label", "Stage 2")
                self.lbl_ai_stage_val.configure(text=lbl)

        # 8. Evaluate Alert Engine
        alert_text, alert_bg, alert_fg, alert_border = self._evaluate_alerts(t_za, t_zb, rover, ai_summary)
        self.alert_frame.configure(bg=alert_bg, highlightbackground=alert_border)
        self.lbl_alert_msg.configure(text=alert_text, bg=alert_bg, fg=alert_fg)

    def _render_battery_bar(self, level: int):
        """Draws visual battery progress bar."""
        self.canvas_battery.delete("all")
        pct = max(0, min(100, level))
        fill_w = int((pct / 100.0) * 46)
        color = self.GREEN_ON if pct > 30 else self.AMBER_WARN if pct > 15 else self.RED_STOP
        self.canvas_battery.create_rectangle(2, 2, 2 + fill_w, 12, fill=color, outline="")
        self.canvas_battery.create_rectangle(48, 4, 50, 10, fill=self.BORDER_COLOR, outline="")

    def _evaluate_alerts(self, za: Optional[Dict], zb: Optional[Dict], rover: Optional[Dict], ai: Optional[Dict]):
        """
        Prioritized Alert Engine:
        1. AI Disease / Pest Detections
        2. Soil moisture critical (<35%)
        3. High ambient heat (>38°C)
        4. Low Rover Battery (<20%)
        5. Normal Status
        """
        # 1. AI Alerts
        if ai:
            if ai.get("alerts") and len(ai["alerts"]) > 0:
                top_alert = ai["alerts"][0]
                alert_type = top_alert.get("type", "")
                lbl = top_alert.get("label", "")
                conf = int((top_alert.get("confidence", 0.9)) * 100)
                node = top_alert.get("node_id", "NODE_01")
                if alert_type == "DISEASE":
                    return self.t("alert_disease_detected", label=lbl, node=node, conf=conf), self.RED_ALERT_BG, self.RED_ACTIVE, self.RED_ALERT_BORDER
                elif alert_type == "PEST":
                    return self.t("alert_pest_detected", label=lbl, node=node, conf=conf), self.RED_ALERT_BG, self.RED_ACTIVE, self.RED_ALERT_BORDER
                elif alert_type == "NUTRITION":
                    return self.t("alert_nutrient_deficiency", label=lbl, node=node), self.AMBER_ALERT_BG, self.AMBER_WARN, self.AMBER_ALERT_BORDER

        # 2. Moisture Alerts
        if za and za.get("soil_moisture", 100) < 35.0:
            return self.t("alert_low_moist_a"), self.AMBER_ALERT_BG, self.AMBER_WARN, self.AMBER_ALERT_BORDER
        if zb and zb.get("soil_moisture", 100) < 35.0:
            return self.t("alert_low_moist_b"), self.AMBER_ALERT_BG, self.AMBER_WARN, self.AMBER_ALERT_BORDER

        # 3. High Heat
        if (za and za.get("ambient_temp", 0) > 38.0) or (zb and zb.get("ambient_temp", 0) > 38.0):
            return self.t("alert_high_heat"), self.RED_ALERT_BG, self.RED_ACTIVE, self.RED_ALERT_BORDER

        # 4. Low Battery
        if rover and rover.get("battery", 100) < 20:
            return self.t("alert_low_battery"), self.RED_ALERT_BG, self.RED_ACTIVE, self.RED_ALERT_BORDER

        # 5. Normal
        return self.t("alert_normal"), self.GREEN_ALERT_BG, self.GREEN_TEXT, self.GREEN_ALERT_BORDER


if __name__ == "__main__":
    root = tk.Tk()
    app = AgriSmartDisplayGUI(root)
    root.mainloop()
