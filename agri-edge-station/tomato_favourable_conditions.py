"""
Tomato — Favourable Conditions Reference Dataset & Agronomic Risk Engine
Reference dataset for tomato crop health, foliar diseases, insect pests, and nutrient deficiencies.
Values represent scientific general favourable ranges for outbreak, infection, and proliferation.
"""

from typing import Dict, Any, List, Optional

TOMATO_FAVOURABLE_CONDITIONS: List[Dict[str, Any]] = [
    {
        "class_id": "healthy",
        "name": "Healthy",
        "category": "healthy",
        "temp_min": 18.0,
        "temp_max": 30.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Moderate",
        "soil_moisture_min": 50.0,
        "soil_moisture_max": 75.0,
        "soil_temp_min": 18.0,
        "soil_temp_max": 24.0,
        "leaf_condition": "Low leaf wetness",
        "risk_level": "none",
        "requires_rain_leaf_wetness": False,
        "treatment": "All environmental parameters within ideal physiological bounds for vigorous tomato vegetative and reproductive growth. Maintain balanced fertigation and regular scouting.",
        "icon": "🌱"
    },
    {
        "class_id": "early_blight",
        "name": "Early Blight",
        "category": "disease",
        "temp_min": 22.0,
        "temp_max": 29.0,
        "humidity_min": 65.0,
        "humidity_max": 90.0,
        "soil_moisture": "Moderate–High",
        "soil_moisture_min": 60.0,
        "soil_moisture_max": 85.0,
        "soil_temp_min": 18.0,
        "soil_temp_max": 25.0,
        "leaf_condition": "Long leaf wetness / rain",
        "risk_level": "critical",
        "requires_rain_leaf_wetness": True,
        "treatment": "Target Alternaria solani with Mancozeb 75% WP (2.5g/L) or Copper Oxychloride spray within 24-48 hours. Prune infected lower foliage and avoid overhead sprinkling.",
        "icon": "🦠"
    },
    {
        "class_id": "late_blight",
        "name": "Late Blight",
        "category": "disease",
        "temp_min": 10.0,
        "temp_max": 25.0,
        "humidity_min": 80.0,
        "humidity_max": 95.0,
        "soil_moisture": "High",
        "soil_moisture_min": 75.0,
        "soil_moisture_max": 95.0,
        "soil_temp_min": 12.0,
        "soil_temp_max": 20.0,
        "leaf_condition": "Long leaf wetness / rain",
        "risk_level": "critical",
        "requires_rain_leaf_wetness": True,
        "treatment": "High-risk water mold (Phytophthora infestans). Apply systemic fungicide (Cymoxanil + Mancozeb / Metalaxyl-M). Halt irrigation immediately to prevent canopy saturation.",
        "icon": "⚠️"
    },
    {
        "class_id": "leaf_miner",
        "name": "Leaf Miner",
        "category": "pest",
        "temp_min": 20.0,
        "temp_max": 30.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Moderate",
        "soil_moisture_min": 50.0,
        "soil_moisture_max": 75.0,
        "soil_temp_min": 18.0,
        "soil_temp_max": 25.0,
        "leaf_condition": "Not dependent on leaf wetness",
        "risk_level": "warning",
        "requires_rain_leaf_wetness": False,
        "treatment": "Apply Abamectin 1.9% EC (0.5ml/L) or Spinosad 45% SC. Pick off heavily serpentine-mined leaves and deploy yellow sticky cards.",
        "icon": "🪰"
    },
    {
        "class_id": "leaf_mold",
        "name": "Leaf Mold",
        "category": "disease",
        "temp_min": 20.0,
        "temp_max": 25.0,
        "humidity_min": 85.0,
        "humidity_max": 95.0,
        "soil_moisture": "Moderate–High",
        "soil_moisture_min": 60.0,
        "soil_moisture_max": 85.0,
        "soil_temp_min": 18.0,
        "soil_temp_max": 24.0,
        "leaf_condition": "High humidity / wet foliage",
        "risk_level": "warning",
        "requires_rain_leaf_wetness": True,
        "treatment": "Passalora fulva thrives in stagnant humid air. Increase ventilation, drop RH below 85%, and spray Chlorothalonil or copper bio-fungicide.",
        "icon": "🍂"
    },
    {
        "class_id": "mosaic_virus",
        "name": "Mosaic Virus",
        "category": "disease",
        "temp_min": 20.0,
        "temp_max": 30.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Moderate",
        "soil_moisture_min": 50.0,
        "soil_moisture_max": 75.0,
        "soil_temp_min": 18.0,
        "soil_temp_max": 25.0,
        "leaf_condition": "Not leaf-wetness dependent",
        "risk_level": "warning",
        "requires_rain_leaf_wetness": False,
        "treatment": "Tobamovirus / TMV transmission. Disinfect pruning shears with 10% trisodium phosphate. Remove stunted plants and control vector sap-feeders.",
        "icon": "🧬"
    },
    {
        "class_id": "septoria",
        "name": "Septoria Leaf Spot",
        "category": "disease",
        "temp_min": 20.0,
        "temp_max": 25.0,
        "humidity_min": 80.0,
        "humidity_max": 95.0,
        "soil_moisture": "Moderate–High",
        "soil_moisture_min": 60.0,
        "soil_moisture_max": 85.0,
        "soil_temp_min": 18.0,
        "soil_temp_max": 25.0,
        "leaf_condition": "Rain / long leaf wetness",
        "risk_level": "critical",
        "requires_rain_leaf_wetness": True,
        "treatment": "Septoria lycopersici circular spotting. Apply copper fungicide or Azoxystrobin spray. Keep ground mulched to prevent water splash transmission.",
        "icon": "🟤"
    },
    {
        "class_id": "spider_mites",
        "name": "Spider Mites",
        "category": "pest",
        "temp_min": 25.0,
        "temp_max": 32.0,
        "humidity_min": 30.0,
        "humidity_max": 60.0,
        "soil_moisture": "Low–Moderate",
        "soil_moisture_min": 35.0,
        "soil_moisture_max": 55.0,
        "soil_temp_min": 20.0,
        "soil_temp_max": 28.0,
        "leaf_condition": "Dry conditions favor activity",
        "risk_level": "warning",
        "requires_rain_leaf_wetness": False,
        "treatment": "Tetranychus urticae explosive breeding in hot/dry microclimates. Spray Propargite 57% EC or cold-pressed Neem Oil (5ml/L). Mist canopy to raise RH.",
        "icon": "🕷️"
    },
    {
        "class_id": "yellow_leaf_curl_virus",
        "name": "Yellow Leaf Curl Virus",
        "category": "disease",
        "temp_min": 25.0,
        "temp_max": 30.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Moderate",
        "soil_moisture_min": 50.0,
        "soil_moisture_max": 75.0,
        "soil_temp_min": 20.0,
        "soil_temp_max": 28.0,
        "leaf_condition": "Whitefly activity important",
        "risk_level": "critical",
        "requires_rain_leaf_wetness": False,
        "treatment": "TYLCV spread by Bemisia tabaci whiteflies. Deploy yellow sticky traps (15/acre) and spray systemic insecticide (Thiamethoxam 25% WG / Neem).",
        "icon": "🟡"
    },
    {
        "class_id": "beet_armyworm",
        "name": "Beet Armyworm",
        "category": "pest",
        "temp_min": 22.0,
        "temp_max": 30.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Moderate",
        "soil_moisture_min": 50.0,
        "soil_moisture_max": 75.0,
        "soil_temp_min": 20.0,
        "soil_temp_max": 28.0,
        "leaf_condition": "Warm conditions",
        "risk_level": "warning",
        "requires_rain_leaf_wetness": False,
        "treatment": "Spodoptera exigua foliar skeletonization. Spray Bacillus thuringiensis (Bt @ 2g/L) or Emamectin benzoate 5% SG (0.5g/L).",
        "icon": "🐛"
    },
    {
        "class_id": "cotton_bollworm",
        "name": "Cotton Bollworm",
        "category": "pest",
        "temp_min": 24.0,
        "temp_max": 30.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Moderate",
        "soil_moisture_min": 50.0,
        "soil_moisture_max": 75.0,
        "soil_temp_min": 20.0,
        "soil_temp_max": 28.0,
        "leaf_condition": "Warm conditions",
        "risk_level": "critical",
        "requires_rain_leaf_wetness": False,
        "treatment": "Helicoverpa armigera tomato fruit borer. Install Helilure pheromone traps and spray Chlorantraniliprole 18.5% SC (0.3ml/L) during flowering.",
        "icon": "🐛"
    },
    {
        "class_id": "green_peach_aphid",
        "name": "Green Peach Aphid",
        "category": "pest",
        "temp_min": 18.0,
        "temp_max": 25.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Moderate",
        "soil_moisture_min": 50.0,
        "soil_moisture_max": 75.0,
        "soil_temp_min": 15.0,
        "soil_temp_max": 24.0,
        "leaf_condition": "Mild conditions",
        "risk_level": "warning",
        "requires_rain_leaf_wetness": False,
        "treatment": "Myzus persicae vectoring viral infections. Spray 0.5% cold-pressed neem oil or soap emulsion; introduce Ladybird beetle predators.",
        "icon": "🐜"
    },
    {
        "class_id": "melon_fly",
        "name": "Melon Fly",
        "category": "pest",
        "temp_min": 24.0,
        "temp_max": 30.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Moderate",
        "soil_moisture_min": 50.0,
        "soil_moisture_max": 75.0,
        "soil_temp_min": 20.0,
        "soil_temp_max": 28.0,
        "leaf_condition": "Warm conditions",
        "risk_level": "warning",
        "requires_rain_leaf_wetness": False,
        "treatment": "Zeugodacus cucurbitae ovipositing in fruit. Deploy Cue-lure fruit fly traps; collect and destroy punctured/infested tomatoes.",
        "icon": "🪰"
    },
    {
        "class_id": "melon_thrips",
        "name": "Melon Thrips",
        "category": "pest",
        "temp_min": 25.0,
        "temp_max": 32.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Low–Moderate",
        "soil_moisture_min": 35.0,
        "soil_moisture_max": 60.0,
        "soil_temp_min": 20.0,
        "soil_temp_max": 28.0,
        "leaf_condition": "Warm, relatively dry conditions",
        "risk_level": "warning",
        "requires_rain_leaf_wetness": False,
        "treatment": "Thrips palmi causing silvery foliar rasping. Install blue sticky traps; apply Spinosad 45% SC or Fipronil 5% SC.",
        "icon": "🦗"
    },
    {
        "class_id": "silverleaf_whitefly",
        "name": "Silverleaf Whitefly",
        "category": "pest",
        "temp_min": 25.0,
        "temp_max": 30.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Moderate",
        "soil_moisture_min": 50.0,
        "soil_moisture_max": 75.0,
        "soil_temp_min": 20.0,
        "soil_temp_max": 28.0,
        "leaf_condition": "Warm conditions",
        "risk_level": "critical",
        "requires_rain_leaf_wetness": False,
        "treatment": "Bemisia tabaci sap extraction and sooty mold. Deploy yellow sticky cards; apply Diafenthiuron 50% WP or Acetamiprid 20% SP.",
        "icon": "🪰"
    },
    {
        "class_id": "tobacco_cutworm",
        "name": "Tobacco Cutworm",
        "category": "pest",
        "temp_min": 22.0,
        "temp_max": 30.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Moderate",
        "soil_moisture_min": 50.0,
        "soil_moisture_max": 75.0,
        "soil_temp_min": 20.0,
        "soil_temp_max": 28.0,
        "leaf_condition": "Warm conditions",
        "risk_level": "warning",
        "requires_rain_leaf_wetness": False,
        "treatment": "Spodoptera litura nocturnal seedling cutting. Lay poison bait (rice bran + molasses/jaggery + Chlorpyrifos) around stem base.",
        "icon": "🐛"
    },
    {
        "class_id": "gray_leaf_spot",
        "name": "Gray Leaf Spot",
        "category": "disease",
        "temp_min": 20.0,
        "temp_max": 30.0,
        "humidity_min": 80.0,
        "humidity_max": 95.0,
        "soil_moisture": "Moderate–High",
        "soil_moisture_min": 60.0,
        "soil_moisture_max": 85.0,
        "soil_temp_min": 18.0,
        "soil_temp_max": 25.0,
        "leaf_condition": "Long leaf wetness / rain",
        "risk_level": "critical",
        "requires_rain_leaf_wetness": True,
        "treatment": "Stemphylium solani leaf lesions. Spray Difenoconazole 25% EC (1ml/L) or Azoxystrobin. Prune crowded branches for airflow.",
        "icon": "🔘"
    },
    {
        "class_id": "magnesium_deficiency",
        "name": "Magnesium Deficiency",
        "category": "deficiency",
        "temp_min": 20.0,
        "temp_max": 30.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Moderate",
        "soil_moisture_min": 50.0,
        "soil_moisture_max": 75.0,
        "soil_temp_min": 18.0,
        "soil_temp_max": 24.0,
        "leaf_condition": "Not disease-related",
        "risk_level": "advisory",
        "requires_rain_leaf_wetness": False,
        "treatment": "Interveinal chlorosis on older leaves. Foliar spray 1% Magnesium Sulfate (Epsom salt, 10g/L) and balance potassium/calcium ratio in soil.",
        "icon": "🧪"
    },
    {
        "class_id": "nitrogen_deficiency",
        "name": "Nitrogen Deficiency",
        "category": "deficiency",
        "temp_min": 20.0,
        "temp_max": 30.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Low–Moderate",
        "soil_moisture_min": 35.0,
        "soil_moisture_max": 60.0,
        "soil_temp_min": 18.0,
        "soil_temp_max": 24.0,
        "leaf_condition": "Not disease-related",
        "risk_level": "advisory",
        "requires_rain_leaf_wetness": False,
        "treatment": "Pale yellowing starting from lower foliage and stunted stem girth. Inject Calcium Nitrate or Urea (2g/L) via drip fertigation header.",
        "icon": "🧪"
    },
    {
        "class_id": "potassium_deficiency",
        "name": "Potassium Deficiency",
        "category": "deficiency",
        "temp_min": 20.0,
        "temp_max": 30.0,
        "humidity_min": 50.0,
        "humidity_max": 80.0,
        "soil_moisture": "Moderate",
        "soil_moisture_min": 50.0,
        "soil_moisture_max": 75.0,
        "soil_temp_min": 18.0,
        "soil_temp_max": 24.0,
        "leaf_condition": "Not disease-related",
        "risk_level": "advisory",
        "requires_rain_leaf_wetness": False,
        "treatment": "Marginal leaf scorch and uneven fruit ripening (yellow shoulder). Apply Potassium Nitrate (13-0-45) or SOP (0-0-50) at 3-5g/L via drip.",
        "icon": "🧪"
    },
    {
        "class_id": "powdery_mildew_ii",
        "name": "Powdery Mildew",
        "category": "disease",
        "temp_min": 15.0,
        "temp_max": 27.0,
        "humidity_min": 60.0,
        "humidity_max": 90.0,
        "soil_moisture": "Moderate",
        "soil_moisture_min": 50.0,
        "soil_moisture_max": 75.0,
        "soil_temp_min": 18.0,
        "soil_temp_max": 25.0,
        "leaf_condition": "Leaf wetness not required",
        "risk_level": "warning",
        "requires_rain_leaf_wetness": False,
        "treatment": "Leveillula taurica powdery white mycelium. Spray Wettable Sulfur (2g/L) or Hexaconazole 5% EC. Maintain good canopy air circulation.",
        "icon": "⚪"
    },
    {
        "class_id": "tomato_bacterial_spot",
        "name": "Tomato Bacterial Spot",
        "category": "disease",
        "temp_min": 24.0,
        "temp_max": 30.0,
        "humidity_min": 80.0,
        "humidity_max": 95.0,
        "soil_moisture": "Moderate–High",
        "soil_moisture_min": 60.0,
        "soil_moisture_max": 85.0,
        "soil_temp_min": 20.0,
        "soil_temp_max": 28.0,
        "leaf_condition": "Rain / wet foliage",
        "risk_level": "critical",
        "requires_rain_leaf_wetness": True,
        "treatment": "Xanthomonas perforans water-soaked lesions. Spray Streptocycline (0.5g/10L) tank-mixed with Copper Oxychloride (2.5g/L). Avoid handling wet crops.",
        "icon": "🛑"
    }
]

def evaluate_tomato_environmental_risk(
    air_temp: float,
    humidity: float,
    soil_moisture: float,
    soil_temp: float = 24.0,
    rain_detected: bool = False
) -> Dict[str, Any]:
    """
    Computes real-time environmental risk scores for tomato crop pathogens, insect pests, and nutrient stress
    by evaluating live ambient temperature (DHT11), humidity (DHT11), soil moisture, soil temperature, and rain sensor state.
    """
    active_threats: List[Dict[str, Any]] = []
    
    for item in TOMATO_FAVOURABLE_CONDITIONS:
        if item["category"] == "healthy":
            continue
            
        # 1. Temperature match score
        temp_in_range = (item["temp_min"] <= air_temp <= item["temp_max"])
        temp_diff = 0.0
        if air_temp < item["temp_min"]:
            temp_diff = item["temp_min"] - air_temp
        elif air_temp > item["temp_max"]:
            temp_diff = air_temp - item["temp_max"]
        temp_score = max(0.0, 1.0 - (temp_diff / 8.0))
        
        # 2. Humidity match score
        hum_in_range = (item["humidity_min"] <= humidity <= item["humidity_max"])
        hum_diff = 0.0
        if humidity < item["humidity_min"]:
            hum_diff = item["humidity_min"] - humidity
        elif humidity > item["humidity_max"]:
            hum_diff = humidity - item["humidity_max"]
        hum_score = max(0.0, 1.0 - (hum_diff / 20.0))
        
        # 3. Soil moisture match score
        sm_min = item.get("soil_moisture_min", 40.0)
        sm_max = item.get("soil_moisture_max", 85.0)
        sm_in_range = (sm_min <= soil_moisture <= sm_max)
        sm_diff = 0.0
        if soil_moisture < sm_min:
            sm_diff = sm_min - soil_moisture
        elif soil_moisture > sm_max:
            sm_diff = soil_moisture - sm_max
        sm_score = max(0.0, 1.0 - (sm_diff / 25.0))
        
        # 4. Rain & Leaf wetness requirement
        wetness_multiplier = 1.0
        if item.get("requires_rain_leaf_wetness", False):
            if rain_detected or humidity >= 85.0:
                wetness_multiplier = 1.35
            else:
                wetness_multiplier = 0.65
        else:
            if "dry" in item.get("leaf_condition", "").lower() and (rain_detected or humidity >= 75.0):
                wetness_multiplier = 0.70
            elif "dry" in item.get("leaf_condition", "").lower() and humidity <= 55.0:
                wetness_multiplier = 1.25

        # Weighted risk calculation
        if item["category"] == "disease":
            # For leaf diseases, humidity & leaf wetness are more important than soil temperature
            base_risk = (hum_score * 0.45) + (temp_score * 0.35) + (sm_score * 0.20)
        elif item["category"] == "deficiency":
            # For nutrient deficiencies, soil moisture & nutrient availability are most useful
            base_risk = (sm_score * 0.55) + (temp_score * 0.30) + (hum_score * 0.15)
        else: # pest
            base_risk = (temp_score * 0.45) + (hum_score * 0.35) + (sm_score * 0.20)
            
        calculated_prob = min(0.99, max(0.05, base_risk * wetness_multiplier))
        
        # Only include threats with significant environmental alignment
        if calculated_prob >= 0.60:
            severity = "critical" if calculated_prob >= 0.80 and item["risk_level"] == "critical" else ("warning" if calculated_prob >= 0.70 else "advisory")
            active_threats.append({
                "class_id": item["class_id"],
                "name": item["name"],
                "category": item["category"],
                "probability": round(calculated_prob, 2),
                "severity": severity,
                "favourable_temp": f"{item['temp_min']}–{item['temp_max']} °C",
                "favourable_humidity": f"{item['humidity_min']}–{item['humidity_max']}%",
                "favourable_moisture": item["soil_moisture"],
                "leaf_condition": item["leaf_condition"],
                "treatment": item["treatment"],
                "icon": item["icon"],
                "env_match": "High Alignment" if calculated_prob >= 0.80 else "Moderate Alignment"
            })
            
    # Sort threats by risk probability descending
    active_threats.sort(key=lambda x: x["probability"], reverse=True)
    
    # Healthy status check
    is_healthy_env = (18.0 <= air_temp <= 30.0) and (50.0 <= humidity <= 80.0) and (50.0 <= soil_moisture <= 75.0) and not rain_detected
    
    overall_status = "OPTIMAL_GROWTH"
    if any(t["severity"] == "critical" for t in active_threats):
        overall_status = "CRITICAL_PATHOGEN_WINDOW"
    elif any(t["severity"] == "warning" for t in active_threats):
        overall_status = "ELEVATED_PEST_DISEASE_RISK"
    elif active_threats:
        overall_status = "ADVISORY_MONITORING"
        
    return {
        "overall_status": overall_status,
        "is_healthy_environment": is_healthy_env,
        "current_telemetry": {
            "air_temp": air_temp,
            "ambient_humidity": humidity,
            "soil_moisture": soil_moisture,
            "soil_temp": soil_temp,
            "rain_detected": rain_detected
        },
        "active_threat_count": len(active_threats),
        "threats": active_threats[:6],
        "all_classes_count": len(TOMATO_FAVOURABLE_CONDITIONS),
        "scientific_note": "For most leaf diseases, humidity and leaf wetness are more decisive than soil temperature. For nutrient deficiencies, soil moisture is paramount."
    }
