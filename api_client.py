import os
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API Key - read from .env, fallback to hardcoded
API_KEY = os.getenv("PLANT_ID_API_KEY")

# Correct endpoint with disease details requested
API_URL = "https://api.plant.id/v3/identification"


class APIError(Exception):
    pass


def api_predict(image_path: str) -> dict:
    """Send image to Plant.id API and return parsed result dict.
    Returns:
        {
            "plant":      "Apple",
            "disease":    "Apple scab",
            "confidence": 0.94,      # 0-1 scale
            "cause":      "...",
            "prevention": "...",
            "treatment":  "..."
        }
    Raises APIError on failure.
    """
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

        # --- Plant species identification (null-safe) ---
        classification = result.get("classification")
        suggestions = classification.get("suggestions") if classification else None
        plant_species = suggestions[0]["name"] if suggestions else "Unknown Plant"

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
            disease_name = top_disease.get("name", "Unknown Disease")
            # Confidence = how sure the API is the plant IS DISEASED with this disease
            confidence   = top_disease_prob

            # --- Extract detailed info directly from API response ---
            details = top_disease.get("details") or {}

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
                # Fall back: use the prevention section from treatment dict
                prev_list  = treatment_data.get("prevention") or []
                prevention = " ".join(prev_list) if isinstance(prev_list, list) else str(prev_list)

            # Description
            description = details.get("description")
            if isinstance(description, dict):
                description = description.get("value", "")

        else:
            # Plant is healthy (or disease probability too low to be meaningful)
            disease_name = "Healthy"
            # Use is_healthy probability as the confidence score
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
