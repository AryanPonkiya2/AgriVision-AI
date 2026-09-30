import os
import base64
import re
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API Key - read from .env, fallback to hardcoded
API_KEY = os.environ.get("PLANT_ID_API_KEY")

# Correct endpoint with disease details requested
API_URL = "https://api.plant.id/v3/identification"

# Extensive mapping of scientific names to common native English names
SCIENTIFIC_TO_COMMON = {
    "solanum lycopersicum": "Tomato",
    "lycopersicon esculentum": "Tomato",
    "malus domestica": "Apple",
    "malus sylvestris": "Apple",
    "malus": "Apple",
    "vitis vinifera": "Grape",
    "vitis": "Grape",
    "prunus persica": "Peach",
    "prunus domestica": "Plum",
    "prunus armeniaca": "Apricot",
    "prunus avium": "Sweet Cherry",
    "prunus cerasus": "Sour Cherry",
    "prunus dulcis": "Almond",
    "prunus": "Cherry / Peach / Plum",
    "capsicum annuum": "Pepper (Bell / Chili)",
    "capsicum frutescens": "Chili Pepper",
    "capsicum": "Pepper",
    "solanum tuberosum": "Potato",
    "solanum melongena": "Eggplant (Brinjal)",
    "solanum": "Potato / Tomato Family",
    "fragaria x ananassa": "Strawberry",
    "fragaria × ananassa": "Strawberry",
    "fragaria vesca": "Strawberry",
    "fragaria": "Strawberry",
    "citrus sinensis": "Orange",
    "citrus limon": "Lemon",
    "citrus aurantiifolia": "Lime",
    "citrus reticulata": "Mandarin / Tangerine",
    "citrus paradisi": "Grapefruit",
    "citrus": "Citrus",
    "mangifera indica": "Mango",
    "musa acuminata": "Banana",
    "musa balbisiana": "Banana",
    "musa x paradisiaca": "Banana",
    "musa": "Banana",
    "carica papaya": "Papaya",
    "pyrus communis": "Pear",
    "pyrus pyrifolia": "Asian Pear",
    "pyrus": "Pear",
    "cucumis sativus": "Cucumber",
    "cucumis melo": "Muskmelon / Cantaloupe",
    "citrullus lanatus": "Watermelon",
    "cucurbita pepo": "Squash / Zucchini",
    "cucurbita maxima": "Pumpkin",
    "zea mays": "Corn (Maize)",
    "oryza sativa": "Rice (Paddy)",
    "triticum aestivum": "Wheat",
    "triticum": "Wheat",
    "gossypium hirsutum": "Cotton",
    "gossypium": "Cotton",
    "arachis hypogaea": "Groundnut (Peanut)",
    "brassica juncea": "Mustard",
    "brassica oleracea": "Cabbage / Broccoli",
    "brassica napus": "Rapeseed / Canola",
    "brassica": "Mustard / Cabbage",
    "cuminum cyminum": "Cumin (Jeera)",
    "saccharum officinarum": "Sugarcane",
    "coffea arabica": "Coffee",
    "coffea canephora": "Coffee",
    "coffea": "Coffee",
    "camellia sinensis": "Tea",
    "theobroma cacao": "Cocoa",
    "phaseolus vulgaris": "Common Bean",
    "pisum sativum": "Pea",
    "cajanus cajan": "Pigeon Pea",
    "cicer arietinum": "Chickpea (Gram)",
    "glycine max": "Soybean",
    "allium cepa": "Onion",
    "allium sativum": "Garlic",
    "nicotiana tabacum": "Tobacco",
    "helianthus annuus": "Sunflower",
    "punica granatum": "Pomegranate",
    "psidium guajava": "Guava",
    "actinidia deliciosa": "Kiwi",
    "rubus idaeus": "Raspberry",
    "vaccinium": "Blueberry",
    "olea europaea": "Olive",
    "ficus carica": "Fig",
    "ananas comosus": "Pineapple",
    "spinacia oleracea": "Spinach",
    "lactuca sativa": "Lettuce",
    "daucus carota": "Carrot",
    "beta vulgaris": "Beetroot",
    "raphanus sativus": "Radish",
    "ipomoea batatas": "Sweet Potato",
    "manihot esculenta": "Cassava",
    "zingiber officinale": "Ginger",
    "curcuma longa": "Turmeric",
    "coriandrum sativum": "Coriander",
    "mentha": "Mint"
}

def get_common_plant_name(name: str) -> str:
    if not name:
        return "Unknown Plant"
    
    clean_name = name.lower().strip()
    
    # 1. Exact match
    if clean_name in SCIENTIFIC_TO_COMMON:
        return SCIENTIFIC_TO_COMMON[clean_name]
    
    # 2. Check substring matches
    for sci, common in SCIENTIFIC_TO_COMMON.items():
        if sci == clean_name or sci in clean_name:
            return common
            
    # 3. Check first word (Genus)
    words = clean_name.split()
    if words and words[0] in SCIENTIFIC_TO_COMMON:
        return SCIENTIFIC_TO_COMMON[words[0]]
        
    return name.title()

def clean_disease_name(disease_name: str, plant_name: str) -> str:
    if not disease_name:
        return "Unknown Disease"
    
    clean_dis = disease_name.strip()
    
    # Replace any embedded scientific names with common plant names
    for sci, common in SCIENTIFIC_TO_COMMON.items():
        if sci in clean_dis.lower():
            pattern = re.compile(re.escape(sci), re.IGNORECASE)
            clean_dis = pattern.sub(common, clean_dis)
            
    return clean_dis.title()


class APIError(Exception):
    pass


def api_predict(image_path: str) -> dict:
    """Send image to Plant.id API and return parsed result dict with native English plant and disease names."""
    if not API_KEY:
        raise APIError("Missing PLANT_ID_API_KEY")

    if not Path(image_path).is_file():
        raise APIError(f"File not found: {image_path}")

    try:
        # Encode image to base64
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("ascii")

        payload = {
            "images": [encoded_image],
            "health": "all",
            "symptoms": True         # request symptom details
        }

        headers = {
            "Api-Key": API_KEY,
            "Content-Type": "application/json"
        }

        # Request disease details via query params
        params = {
            "details": "cause,treatment,prevention,common_names,description"
        }

        response = requests.post(API_URL, json=payload, headers=headers, params=params, timeout=30)

        if response.status_code in [401, 403]:
            raise APIError("Authentication failed. Check your PLANT_ID_API_KEY.")

        if response.status_code not in [200, 201]:
            raise APIError(f"Status {response.status_code}: {response.text}")

        data = response.json()
        print("Plant.id API Response:", data)

        result = data.get("result")
        if not result:
            error_msg = data.get("error", {}).get("message", "Unknown response structure")
            raise APIError(f"API Error: {error_msg}")

        # --- Plant species identification (Native English) ---
        classification = result.get("classification")
        suggestions = classification.get("suggestions") if classification else None
        
        plant_species = "Unknown Plant"
        if suggestions:
            top_sug = suggestions[0]
            sug_details = top_sug.get("details") or {}
            common_names = sug_details.get("common_names") or top_sug.get("common_names") or []
            
            if common_names and isinstance(common_names, list) and len(common_names) > 0:
                plant_species = common_names[0].title()
            else:
                raw_name = top_sug.get("name", "")
                plant_species = get_common_plant_name(raw_name)

        # --- is_healthy signal from API ---
        is_healthy_data = result.get("is_healthy") or {}
        is_healthy_binary    = is_healthy_data.get("binary", True)
        is_healthy_prob      = is_healthy_data.get("probability", 1.0)  # 0-1 scale

        # --- Disease identification (null-safe) ---
        disease_result      = result.get("disease")
        disease_suggestions = disease_result.get("suggestions") if disease_result else None

        # Minimum probability threshold — below this treat as healthy
        DISEASE_THRESHOLD = 0.10  # 10%

        top_disease_prob = disease_suggestions[0].get("probability", 0.0) if disease_suggestions else 0.0

        if disease_suggestions and not is_healthy_binary and top_disease_prob >= DISEASE_THRESHOLD:
            top_disease  = disease_suggestions[0]
            details = top_disease.get("details") or {}
            
            dis_common_names = details.get("common_names") or top_disease.get("common_names") or []
            if dis_common_names and isinstance(dis_common_names, list) and len(dis_common_names) > 0:
                disease_name = dis_common_names[0].title()
            else:
                raw_dis_name = top_disease.get("name", "Unknown Disease")
                disease_name = clean_disease_name(raw_dis_name, plant_species)

            # Confidence = how sure the API is the plant IS DISEASED with this disease
            confidence   = top_disease_prob

            # Cause
            cause_data = details.get("cause")
            if isinstance(cause_data, dict):
                cause = cause_data.get("description") or cause_data.get("value") or ""
            elif isinstance(cause_data, str):
                cause = cause_data
            else:
                cause = ""

            # Treatment — API returns dict with keys: prevention, chemical, biological, organic
            treatment_data  = details.get("treatment") or {}
            treatment_parts = []
            for category in ["prevention", "organic", "biological", "chemical"]:
                actions = treatment_data.get(category)
                if actions and isinstance(actions, list):
                    treatment_parts.extend(actions)
                elif actions and isinstance(actions, str):
                    treatment_parts.append(actions)
            treatment = " ".join(treatment_parts) if treatment_parts else ""

            # Prevention — sometimes a separate field
            prevention_data = details.get("prevention")
            if isinstance(prevention_data, list):
                prevention = " ".join(prevention_data)
            elif isinstance(prevention_data, str):
                prevention = prevention_data
            else:
                prev_list  = treatment_data.get("prevention") or []
                prevention = " ".join(prev_list) if isinstance(prev_list, list) else str(prev_list)

            # Description
            description = details.get("description")
            if isinstance(description, dict):
                description = description.get("value", "")

        else:
            # Plant is healthy (or disease probability too low to be meaningful)
            disease_name = "Healthy"
            confidence   = is_healthy_prob if is_healthy_prob > 0 else 1.0
            cause        = ""
            prevention   = ""
            treatment    = ""
            description  = ""

        return {
            "plant":       plant_species,
            "disease":     disease_name,
            "confidence":  confidence,    # 0-1 scale; app.py multiplies by 100
            "cause":       cause,
            "prevention":  prevention,
            "treatment":   treatment,
            "description": description
        }

    except requests.RequestException as e:
        raise APIError(str(e))
