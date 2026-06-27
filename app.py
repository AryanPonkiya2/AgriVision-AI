import os
import uuid
from flask import Flask, request, render_template, redirect, url_for, flash
from dotenv import load_dotenv
load_dotenv()
from api_client import api_predict

app = Flask(__name__)
app.secret_key = "plant_care_ai_super_secret" # For flash messages

# Directory specific config
BASE_DIR = os.path.dirname(os.path.abspath(__name__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Disease causes knowledge base
DISEASE_CAUSES = {
    "rot": "Rot is typically caused by fungal or bacterial pathogens that thrive in overly moist conditions. Poor drainage, overwatering, and high humidity create the perfect environment for rot-causing organisms to infect the plant through wounds or natural openings.",
    "blight": "Blight is caused by pathogenic fungi or bacteria (such as Phytophthora or Alternaria) that spread through water splashes, wind, or contaminated soil. It often starts in cool, wet weather and can survive in plant debris between seasons.",
    "spot": "Leaf spots are caused by fungal or bacterial pathogens that spread through water splashes, wind-blown rain, or contaminated gardening tools. They typically enter through stomata or small wounds and thrive in humid conditions with poor air circulation.",
    "mildew": "Powdery mildew is caused by fungal spores (Erysiphales family) that thrive in moderate temperatures with high humidity but dry leaf surfaces. Spores spread through wind and typically attack when there's poor air circulation and low light.",
    "rust": "Rust is caused by fungal pathogens (Pucciniales order) that require living plant tissue to survive. Spores spread through wind, water, or direct contact, and thrive in moderate temperatures with extended leaf wetness periods.",
    "wilt": "Wilting is often caused by soil-borne fungi (Fusarium or Verticillium) that invade the plant's vascular system, blocking water transport. It can persist in soil for years and enters through root wounds.",
    "mosaic": "Mosaic patterns are caused by plant viruses that are typically transmitted by sap-sucking insects like aphids, whiteflies, or through contaminated tools. Once infected, the plant remains a carrier.",
    "canker": "Cankers are caused by fungal or bacterial pathogens that enter through wounds in bark or stems. Stress factors like drought, frost damage, or poor nutrition make plants more susceptible.",
    "scorch": "Leaf scorch is caused by fungal pathogens or environmental stress (excessive sun, wind, or salt buildup). Fungal scorch spreads through water splash and infected plant debris, while physiological scorch results from root damage or underwatering.",
    "scab": "Scab is caused by fungal pathogens (such as Venturia inaequalis for apples) that infect young leaves and fruit during wet spring weather. Spores spread through rain splash and wind.",
    "mold": "Leaf mold is caused by fungal pathogens (such as Passalora fulva for tomatoes) that thrive in high humidity and poor air circulation. Spores enter through leaf stomata and spread rapidly in damp, shaded conditions.",
    "mite": "Spider mites are not a disease but tiny arachnid pests that feed on plant sap. They thrive in hot, dry conditions and multiply rapidly, causing stippling, yellowing, and fine webbing on leaves.",
    "virus": "Plant viruses are microscopic pathogens that hijack plant cells to replicate. They are typically transmitted by sap-sucking insects (aphids, whiteflies, leafhoppers), through contaminated tools, or via infected seeds.",
    "curl": "Leaf curl is caused by viral infections (such as Tomato Yellow Leaf Curl Virus) transmitted by whiteflies, or by fungal pathogens (Taphrina deformans) that infect buds during cool, wet weather.",
    "default": "This disease is caused by pathogenic microorganisms (fungi, bacteria, or viruses) that infect the plant under favorable environmental conditions. Factors like high humidity, poor air circulation, overwatering, and contaminated soil or tools contribute to disease development."
}

DISEASE_PREVENTION = {
    "rot": "Prevent rot by ensuring well-draining soil and avoiding overwatering. Space plants properly for airflow, water at the base rather than overhead, and remove any decaying plant matter promptly. Use raised beds if drainage is poor.",
    "blight": "Prevent blight by using disease-resistant varieties, practicing crop rotation (avoid planting same family for 3-4 years), watering at soil level, and providing adequate plant spacing. Remove and destroy infected plant debris at season end.",
    "spot": "Prevent leaf spots by watering at the base to keep foliage dry, providing good air circulation through proper spacing, and mulching to prevent soil splash. Use clean, disease-free seeds and practice crop rotation.",
    "mildew": "Prevent powdery mildew by choosing resistant varieties, planting in full sun with good airflow, avoiding overhead watering, and applying preventive sulfur or neem oil sprays during high-risk periods.",
    "rust": "Prevent rust by planting resistant varieties, ensuring good air circulation, watering at soil level, and removing alternate host plants nearby. Clean up all plant debris in fall to reduce overwintering spores.",
    "wilt": "Prevent wilting diseases by using disease-resistant varieties, practicing long crop rotations (5-7 years), solarizing soil in hot seasons, and avoiding overwatering. Sterilize pruning tools between uses.",
    "mosaic": "Prevent mosaic viruses by controlling aphid and whitefly populations with reflective mulches or insecticidal soaps, using virus-free seeds, and regularly disinfecting gardening tools.",
    "canker": "Prevent cankers by avoiding wounding the bark, pruning during dry weather, providing proper nutrition and irrigation to reduce stress, and applying protective wound dressings on large cuts.",
    "scorch": "Prevent leaf scorch by providing consistent soil moisture through mulching and regular watering, avoiding direct afternoon sun for sensitive plants, and ensuring good air circulation. Remove and dispose of infected leaves in fall.",
    "scab": "Prevent scab by planting resistant varieties, applying preventive fungicides at green tip through petal fall, and raking up all fallen leaves and fruit in autumn to reduce overwintering spores.",
    "mold": "Prevent leaf mold by spacing plants for maximum airflow, watering at soil level, and avoiding overhead irrigation. Prune lower branches to improve air circulation around the soil line.",
    "mite": "Prevent spider mites by keeping plants well-watered to reduce stress, misting leaves regularly to increase humidity, and encouraging natural predators like ladybugs and predatory mites.",
    "virus": "Prevent viral diseases by controlling insect vectors with reflective mulches or insecticidal soaps, using virus-free certified seeds, disinfecting pruning tools between plants, and removing weeds that act as virus reservoirs.",
    "curl": "Prevent leaf curl by controlling whitefly populations with yellow sticky traps or insecticidal soaps, using reflective mulch to deter vectors, and removing infected plants promptly.",
    "default": "Prevent diseases by maintaining good garden hygiene: use disease-free seeds, practice crop rotation, ensure proper spacing for air circulation, water at soil level, and disinfect tools regularly."
}


def get_disease_info(disease_name, scan_type='plant'):
    disease_lower = disease_name.lower()

    if "healthy" in disease_lower:
        if scan_type == 'fruit':
            return ("No disease detected",
                    "Maintain stable soil moisture and feed with balanced nutrients to keep your fruit healthy.",
                    "Great job! Your fruit is perfectly healthy and ready for optimal development.")
        else:
            return ("No disease detected",
                    "Ensure proper watering, sunlight, and good air circulation to keep your plant healthy.",
                    "Great job! Your plant is perfectly healthy. Ensure proper watering and sunlight to keep it this way.")

    cause = DISEASE_CAUSES.get("default")
    prevention = DISEASE_PREVENTION.get("default")
    treatment = ""

    for key in ["rot", "blight", "spot", "mildew", "rust", "wilt", "mosaic", "canker", "scorch", "scab", "mold", "mite", "virus", "curl"]:
        if key in disease_lower:
            cause = DISEASE_CAUSES.get(key, cause)
            prevention = DISEASE_PREVENTION.get(key, prevention)
            break

    if "rot" in disease_lower:
        if scan_type == 'fruit':
            treatment = "Harvest unaffected ripe fruit immediately. Remove and destroy infected fruit to prevent spread. Apply calcium sprays if blossom end rot, or appropriate copper fungicides for fungal rots."
        else:
            treatment = "Remove infected leaves immediately, improve air circulation, and apply a suitable fungicide. Avoid overhead watering."
    elif "blight" in disease_lower:
        if scan_type == 'fruit':
            treatment = "Prune nearby infected foliage to stop the spores from reaching fruit. Keep the fruit off wet ground, and treat crops with copper fungicides."
        else:
            treatment = "Blight spreads quickly in wet conditions! Prune infected areas, avoid overhead watering, and treat with a copper-based fungicide."
    elif "spot" in disease_lower:
        if scan_type == 'fruit':
            treatment = "Avoid overhead irrigation as water splashes spread the pathogens. Apply protective fungicide and harvest early if needed."
        else:
            treatment = "Remove severely damaged leaves. Avoid splashing water onto leaves. Apply a suitable fungicide if the infection is severe."
    elif "mildew" in disease_lower:
        treatment = "Ensure good airflow around the plant. Treat with neem oil or a sulfur fungicide. Remove heavily infected plant parts."
    elif "rust" in disease_lower:
        treatment = "Remove and destroy infected leaves immediately. Apply sulfur-based or copper fungicides. Avoid working with wet plants to prevent spore spread."
    elif "wilt" in disease_lower:
        treatment = "Remove and destroy infected plants immediately. Do not compost them. Solarize the soil before replanting. There is no chemical cure for vascular wilts."
    elif "mosaic" in disease_lower:
        treatment = "There is no cure for viral infections. Remove and destroy infected plants. Control insect vectors with insecticidal soaps or neem oil."
    elif "canker" in disease_lower:
        treatment = "Prune infected branches 10-12 inches below the canker during dry weather. Sterilize pruning tools between cuts. Apply a protective fungicide paste."
    elif "scorch" in disease_lower:
        treatment = "Remove severely scorched leaves. For fungal leaf scorch, apply a copper-based fungicide. For physiological scorch, increase watering frequency, add mulch to retain moisture, and provide shade during peak heat."
    elif "scab" in disease_lower:
        treatment = "Apply protective fungicides (captan, sulfur, or copper) starting at green tip and continuing through petal fall. Remove and destroy infected fruit and leaves. Rake fallen leaves in autumn to reduce next year's inoculum."
    elif "mold" in disease_lower:
        treatment = "Remove affected leaves immediately. Improve air circulation by pruning and spacing. Apply a sulfur-based or copper fungicide. Avoid overhead watering entirely."
    elif "mite" in disease_lower:
        treatment = "Spray undersides of leaves with water to dislodge mites. Apply insecticidal soap, neem oil, or miticides. For severe infestations, prune heavily infested leaves. Increase humidity around plants."
    elif "virus" in disease_lower:
        treatment = "There is no cure for viral infections. Remove and destroy infected plants immediately. Control insect vectors with insecticidal soaps, neem oil, or reflective mulches. Disinfect tools thoroughly."
    elif "curl" in disease_lower:
        treatment = "Remove and destroy infected leaves and fruit. Control whitefly populations with sticky traps and insecticidal soaps. For fungal curl (peach/almond), apply copper fungicide before bud swell in late winter."
    else:
        if scan_type == 'fruit':
            treatment = "Isolate affected fruits, avoid overhead watering, ensure proper crop rotation next season, and consult local agriculture advisors for broad-spectrum crop-safe treatments."
        else:
            treatment = "Isolate the plant, remove affected parts, and consider applying broad-spectrum treatments. Consult local agriculture experts for specific advice."

    return cause, prevention, treatment

def predict_disease(image_path, scan_type='plant'):
    try:
        # Call Plant.id API via our client
        response = api_predict(image_path)

        plant_species = response.get('plant', 'Unknown')
        disease_label = response.get('disease', 'Unknown')
        confidence    = response.get('confidence', 0.0)

        # API-provided details (accurate, disease-specific)
        api_cause      = response.get('cause', '').strip()
        api_prevention = response.get('prevention', '').strip()
        api_treatment  = response.get('treatment', '').strip()

        if disease_label.lower() == "healthy":
            disease_name = "Healthy"
            cause, prevention, treatment = get_disease_info("Healthy", scan_type)
        else:
            disease_name = disease_label.replace("_", " ").strip()
            # Use API details when available; fall back to keyword-based info only if empty
            if api_cause or api_prevention or api_treatment:
                cause      = api_cause      or DISEASE_CAUSES.get("default")
                prevention = api_prevention or DISEASE_PREVENTION.get("default")
                treatment  = api_treatment  or "Consult a local agriculture expert for treatment advice."
            else:
                cause, prevention, treatment = get_disease_info(disease_name, scan_type)

        confidence_pct = round(confidence * 100, 2)
        full_disease_name = f"{plant_species} - {disease_name}"
        return full_disease_name, confidence_pct, cause, prevention, treatment

    except Exception as e:
        print(f"API Error: {e}")
        return "API Error", 0.0, "", "", str(e)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return redirect(url_for('team'))

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/map')
def map_page():
    return render_template('map.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part provided", "error")
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash("No selected file", "error")
            return redirect(request.url)
            
        scan_type = request.form.get('scan_type', 'plant')
        if file:
            filename = str(uuid.uuid4()) + "_" + getattr(file, "filename", "uploaded_image.jpg")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Predict
            disease_name, confidence, cause, prevention, treatment = predict_disease(filepath, scan_type=scan_type)
            
            # Return result
            return render_template('result.html', 
                                   image_file=filename,
                                   disease_name=disease_name.split(' - ')[-1] if ' - ' in disease_name else disease_name,
                                   plant_type=disease_name.split(' - ')[0] if ' - ' in disease_name else "Unknown",
                                   confidence=round(confidence, 2),
                                   cause=cause,
                                   prevention=prevention,
                                   treatment=treatment,
                                   scan_type=scan_type)
            
    return render_template('upload.html')

if __name__ == '__main__':
    print("Starting AgriVison AI Web Application...")
    app.run(debug=True, host='0.0.0.0', port=5000)
