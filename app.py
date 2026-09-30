import os
import uuid
import json
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from dotenv import load_dotenv
load_dotenv()
from api_client import api_predict, get_common_plant_name
import requests
import hashlib
import time
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "plant_care_ai_super_secret" # For flash messages

# Directory specific config
BASE_DIR = os.path.dirname(os.path.abspath(__name__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ══════════════════════════════════════════════════════
#   DATABASE CONFIGURATION (SQLite + Flask-SQLAlchemy)
# ══════════════════════════════════════════════════════
from models import db, User, ScanHistory, migrate_from_json

DB_PATH = os.path.join(BASE_DIR, 'agrivision.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize database tables and run migration from JSON on startup
with app.app_context():
    db.create_all()
    migrate_from_json(BASE_DIR, UPLOAD_FOLDER)

def load_scan_history(user_id=None):
    try:
        if user_id:
            # Show the logged-in user's scans
            return ScanHistory.query.filter_by(user_id=user_id).order_by(ScanHistory.created_at.desc()).limit(50).all()
        else:
            # Show guest / unassigned scans
            return ScanHistory.query.filter(ScanHistory.user_id.is_(None)).order_by(ScanHistory.created_at.desc()).limit(50).all()
    except Exception as e:
        print(f"Error loading scan history from DB: {e}")
        return []

def save_scan_entry(entry, user_id=None):
    try:
        scan_id = entry.get('id') or str(uuid.uuid4())[:8]
        scan = ScanHistory(
            id=scan_id,
            user_id=user_id or entry.get('user_id'),
            filename=entry.get('filename', ''),
            plant_type=entry.get('plant_type', 'Unknown'),
            disease_name=entry.get('disease_name', 'Unknown'),
            confidence=float(entry.get('confidence', 0.0)),
            scan_type=entry.get('scan_type', 'plant'),
            cause=entry.get('cause', ''),
            prevention=entry.get('prevention', ''),
            treatment=entry.get('treatment', ''),
            timestamp=entry.get('timestamp') or datetime.now().strftime("%b %d, %Y - %I:%M %p")
        )
        db.session.add(scan)
        db.session.commit()
        return scan
    except Exception as e:
        db.session.rollback()
        print(f"Error saving scan to DB: {e}")
        return None

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

        plant_species = get_common_plant_name(response.get('plant', 'Unknown'))
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

# ══════════════════════════════════════════════════════
#   USER AUTHENTICATION SYSTEM
# ══════════════════════════════════════════════════════

def load_users():
    return User.query.all()

def save_user(user_obj):
    db.session.add(user_obj)
    db.session.commit()

def find_user_by_email(email):
    if not email:
        return None
    return User.query.filter_by(email=email.strip().lower()).first()

@app.context_processor
def inject_user():
    """Make current_user available in all templates."""
    user_id = session.get('user_id')
    if user_id:
        current_user = User.query.filter_by(id=user_id).first()
        return {'current_user': current_user}
    return {'current_user': None}


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('login'))

        user = find_user_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session.permanent = bool(request.form.get('remember'))
            flash(f"Welcome back, {user.first_name}! 🌿", 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('user_id'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not all([first_name, last_name, email, password, confirm_password]):
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('signup'))

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('signup'))

        if find_user_by_email(email):
            flash('An account with this email already exists.', 'error')
            return redirect(url_for('signup'))

        # Create user in database
        user = User(
            id=str(uuid.uuid4())[:12],
            first_name=first_name,
            last_name=last_name,
            email=email.lower(),
            password_hash=generate_password_hash(password),
            created_at=datetime.utcnow()
        )
        save_user(user)

        flash('Account created successfully! Please sign in. 🎉', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))


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

@app.route('/export-map')
def export_map_page():
    return render_template('export.html')

@app.route('/weather-map')
def weather_map_page():
    return render_template('weather.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    user_id = session.get('user_id')
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
            
            parsed_disease = disease_name.split(' - ')[-1] if ' - ' in disease_name else disease_name
            parsed_plant = disease_name.split(' - ')[0] if ' - ' in disease_name else "Unknown"
            scan_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now().strftime("%b %d, %Y - %I:%M %p")
            
            entry = {
                "id": scan_id,
                "user_id": user_id,
                "filename": filename,
                "plant_type": parsed_plant,
                "disease_name": parsed_disease,
                "confidence": round(confidence, 2),
                "cause": cause,
                "prevention": prevention,
                "treatment": treatment,
                "scan_type": scan_type,
                "timestamp": timestamp
            }
            save_scan_entry(entry, user_id=user_id)
            
            # Return result
            return render_template('result.html', 
                                   image_file=filename,
                                   disease_name=parsed_disease,
                                   plant_type=parsed_plant,
                                   confidence=round(confidence, 2),
                                   cause=cause,
                                   prevention=prevention,
                                   treatment=treatment,
                                   scan_type=scan_type,
                                   scan_id=scan_id)
            
    history = load_scan_history(user_id=user_id)
    return render_template('upload.html', history=history)

@app.route('/history/<scan_id>')
def view_history_item(scan_id):
    item = ScanHistory.query.filter_by(id=scan_id).first()
    if not item:
        flash("Scan history item not found", "error")
        return redirect(url_for('upload'))
    
    return render_template('result.html',
                           image_file=item.filename,
                           disease_name=item.disease_name,
                           plant_type=item.plant_type,
                           confidence=item.confidence,
                           cause=item.cause,
                           prevention=item.prevention,
                           treatment=item.treatment,
                           scan_type=item.scan_type,
                           scan_id=item.id,
                           from_history=True)

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    try:
        user_id = session.get('user_id')
        if user_id:
            ScanHistory.query.filter_by(user_id=user_id).delete()
        else:
            ScanHistory.query.filter((ScanHistory.user_id.is_(None)) | (ScanHistory.user_id == '')).delete()
        db.session.commit()

        # Also clear any legacy JSON files so old records are not resurrected on server reloads
        upload_folder = app.config.get('UPLOAD_FOLDER', '')
        if upload_folder:
            for fname in ['scan_history.json', 'scan_history.json.migrated']:
                fpath = os.path.join(upload_folder, fname)
                if os.path.exists(fpath):
                    try:
                        with open(fpath, 'w', encoding='utf-8') as f:
                            json.dump([], f)
                    except Exception:
                        pass

        return jsonify({"success": True, "message": "Scan history cleared successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# Base Crop Profiles for Indian states
BASE_CROP_PROFILES = {
    "Cotton": {
        "price": 7150,
        "msp": "₹6,620 / Quintal",
        "apmc": "APMC",
        "volume": "Bags",
        "sowing": "June - July (Kharif)",
        "harvest": "October - January",
        "water": "Medium (500 - 800 mm)",
        "districts_map": {
            "Gujarat": "Surendranagar, Rajkot, Jamnagar",
            "Maharashtra": "Yavatmal, Amravati, Jalgaon",
            "Punjab": "Bathinda, Sri Muktsar Sahib, Fazilka",
            "Andhra Pradesh": "Guntur, Kurnool, Adilabad",
            "default": "Primary State Cultivation Belts"
        }
    },
    "Groundnut": {
        "price": 6750,
        "msp": "₹6,375 / Quintal",
        "apmc": "APMC",
        "volume": "Bags",
        "sowing": "June - July (Kharif)",
        "harvest": "October - November",
        "water": "Low-Medium (500 - 600 mm)",
        "districts_map": {
            "Gujarat": "Junagadh, Rajkot, Amreli",
            "Andhra Pradesh": "Anantapur, Chittoor, Kurnool",
            "Tamil Nadu": "Tiruvannamalai, Villupuram, Vellore",
            "default": "Primary Oilseed Belts"
        }
    },
    "Wheat": {
        "price": 2650,
        "msp": "₹2,275 / Quintal",
        "apmc": "APMC",
        "volume": "Bags",
        "sowing": "October - November (Rabi)",
        "harvest": "March - April",
        "water": "Moderate (Irrigated)",
        "districts_map": {
            "Gujarat": "Ahmedabad, Anand, Mehsana",
            "Uttar Pradesh": "Gorakhpur, Bulandshahr, Aligarh",
            "Punjab": "Ludhiana, Patiala, Sangrur",
            "Haryana": "Karnal, Hisar, Sirsa",
            "default": "Indo-Gangetic Plains & Central Plateaus"
        }
    },
    "Rice": {
        "price": 3100,
        "msp": "₹2,183 / Quintal",
        "apmc": "APMC",
        "volume": "Bags",
        "sowing": "June - July (Kharif)",
        "harvest": "November - December",
        "water": "High (1200 - 1500 mm)",
        "districts_map": {
            "Gujarat": "Kheda, Anand, Ahmedabad, Surat",
            "West Bengal": "Bardhaman, Midnapore, Hooghly",
            "Uttar Pradesh": "Shahjahanpur, Lakhimpur Kheri",
            "Punjab": "Firozpur, Sangrur, Patiala",
            "default": "Lowland deltaic and irrigated canal zones"
        }
    },
    "Castor Seed": {
        "price": 5850,
        "msp": "No MSP (Market Driven)",
        "apmc": "APMC",
        "volume": "Bags",
        "sowing": "August - September",
        "harvest": "December - March",
        "water": "Low (Drought Hardy)",
        "districts_map": {
            "Gujarat": "Banaskantha, Patan, Mehsana",
            "Rajasthan": "Barmer, Jalore, Jodhpur",
            "default": "Arid and semi-arid oilseed zones"
        }
    },
    "Bajra (Pearl Millet)": {
        "price": 2400,
        "msp": "₹2,500 / Quintal",
        "apmc": "APMC",
        "volume": "Bags",
        "sowing": "June - July (Kharif)",
        "harvest": "September - October",
        "water": "Very Low (300 - 450 mm)",
        "districts_map": {
            "Gujarat": "Banaskantha, Kutch, Sabarkantha",
            "Rajasthan": "Alwar, Jaipur, Tonk",
            "default": "Sandy arid soils & rainfed plains"
        }
    },
    "Maize (Corn)": {
        "price": 2300,
        "msp": "₹2,090 / Quintal",
        "apmc": "APMC",
        "volume": "Bags",
        "sowing": "June - July (Kharif)",
        "harvest": "October - November",
        "water": "Medium (600 - 800 mm)",
        "districts_map": {
            "Gujarat": "Dahod, Panchmahal, Sabarkantha",
            "Karnataka": "Havery, Davangere, Belagavi",
            "Madhya Pradesh": "Chhindwara, Dhar, Khargone",
            "default": "Red-loamy sub-montane and central soils"
        }
    },
    "Mustard": {
        "price": 5600,
        "msp": "₹5,450 / Quintal",
        "apmc": "APMC",
        "volume": "Bags",
        "sowing": "October - November (Rabi)",
        "harvest": "February - March",
        "water": "Low (Cool & Dry)",
        "districts_map": {
            "Gujarat": "Banaskantha, Mehsana, Patan",
            "Rajasthan": "Bharatpur, Alwar, Ganganagar",
            "default": "Rabi oilseed belts"
        }
    },
    "Cumin (Jeera)": {
        "price": 28000,
        "msp": "No MSP (Spice Grade)",
        "apmc": "APMC",
        "volume": "Bags",
        "sowing": "November (Rabi)",
        "harvest": "February - March",
        "water": "Very Low (Dry Climate)",
        "districts_map": {
            "Gujarat": "Mehsana, Patan, Banaskantha, Saurashtra",
            "Rajasthan": "Jodhpur, Barmer, Jalore",
            "default": "Highly specialized arid spice tracts"
        }
    },
    "Sugarcane": {
        "price": 345,
        "msp": "₹315 / Quintal (FRP)",
        "apmc": "Sugar Coop",
        "volume": "Quintals",
        "sowing": "January - February / October",
        "harvest": "12 - 14 Months Cycle",
        "water": "Very High (1500+ mm)",
        "districts_map": {
            "Gujarat": "Surat, Valsad, Navsari, Gir Somnath",
            "Uttar Pradesh": "Muzaffarnagar, Lakhimpur Kheri",
            "Maharashtra": "Kolhapur, Pune, Ahmednagar",
            "default": "Sub-tropical canal and high water table zones"
        }
    }
}

STATE_APMC_MAP = {
    "Gujarat": {
        "Cotton": "Rajkot APMC",
        "Groundnut": "Gondal APMC",
        "Wheat": "Ahmedabad APMC",
        "Rice": "Kheda APMC",
        "Castor Seed": "Patan APMC",
        "Bajra (Pearl Millet)": "Deesa APMC",
        "Maize (Corn)": "Dahod APMC",
        "Mustard": "Mehsana APMC",
        "Cumin (Jeera)": "Unjha APMC",
        "Sugarcane": "Surat Sugar Coop"
    },
    "default": {
        "Cotton": "Guntur APMC",
        "Groundnut": "Anantapur APMC",
        "Wheat": "Khanna APMC",
        "Rice": "Burdwan APMC",
        "Castor Seed": "Jodhpur APMC",
        "Bajra (Pearl Millet)": "Alwar APMC",
        "Maize (Corn)": "Dharwad APMC",
        "Mustard": "Bharatpur APMC",
        "Cumin (Jeera)": "Jodhpur APMC",
        "Sugarcane": "Kolhapur Coop"
    }
}

def normalize_name(name):
    if not name:
        return ""
    name = name.lower().strip()
    if "cotton" in name:
        return "Cotton"
    if "groundnut" in name:
        return "Groundnut"
    if "wheat" in name:
        return "Wheat"
    if "rice" in name or "paddy" in name:
        return "Rice"
    if "castor" in name:
        return "Castor Seed"
    if "bajra" in name or "pearl millet" in name:
        return "Bajra (Pearl Millet)"
    if "maize" in name or "corn" in name:
        return "Maize (Corn)"
    if "mustard" in name:
        return "Mustard"
    if "cumin" in name or "jeera" in name:
        return "Cumin (Jeera)"
    if "sugarcane" in name:
        return "Sugarcane"
    return name

def get_base_profile(norm_crop, state):
    base_crop = None
    for k in BASE_CROP_PROFILES.keys():
        if k.lower() in norm_crop.lower() or norm_crop.lower() in k.lower():
            base_crop = BASE_CROP_PROFILES[k]
            break
            
    if not base_crop:
        return {
            "msp": "No MSP (Market Driven)",
            "sowing": "June - July (Kharif)",
            "harvest": "October - November",
            "water": "Medium (500-800 mm)",
            "districts": "Primary Cultivation Belts"
        }
        
    districts = base_crop["districts_map"].get(state, base_crop["districts_map"]["default"])
    return {
        "msp": base_crop["msp"],
        "sowing": base_crop["sowing"],
        "harvest": base_crop["harvest"],
        "water": base_crop["water"],
        "districts": districts
    }

def get_seeded_market_data(state, crop):
    state = state.strip()
    norm_crop = crop.strip()
    
    base_crop = None
    matched_key = None
    for k in BASE_CROP_PROFILES.keys():
        if k.lower() in norm_crop.lower() or norm_crop.lower() in k.lower():
            base_crop = BASE_CROP_PROFILES[k]
            matched_key = k
            break
            
    if not base_crop:
        base_crop = {
            "price": 3000,
            "msp": "No MSP (Market Driven)",
            "apmc": "Central APMC",
            "volume": "Bags",
            "sowing": "June - July (Kharif)",
            "harvest": "October - November",
            "water": "Medium (500-800 mm)",
            "districts_map": { "default": "Primary Cultivation Belts" }
        }
        matched_key = crop
        
    current_day_str = time.strftime("%Y-%m-%d")
    seed_str = f"{state}_{matched_key}_{current_day_str}"
    
    hasher = hashlib.md5(seed_str.encode('utf-8'))
    hash_int = int(hasher.hexdigest()[:8], 16)
    
    var_percent = (hash_int % 100 - 50) / 1000.0
    final_price = int(base_crop["price"] * (1.0 + var_percent))
    
    trend_pct = round(((hash_int % 60) - 25) / 10.0, 1)
    trend_icon = "▲" if trend_pct >= 0 else "▼"
    trend_class = "market-trend-up" if trend_pct >= 0 else "market-trend-down"
    trend_str = f"{'+' if trend_pct >= 0 else ''}{trend_pct}%"
    
    apmc = STATE_APMC_MAP.get(state, STATE_APMC_MAP["default"]).get(matched_key, STATE_APMC_MAP["default"].get(matched_key, "Central APMC"))
    
    volume_val = (hash_int % 21 + 5) * 1000
    volume = f"{volume_val:,} Bags"
    
    districts = base_crop["districts_map"].get(state, base_crop["districts_map"]["default"])
    
    return {
        "price": f"₹{final_price:,} / Quintal",
        "trendIcon": trend_icon,
        "trendPct": trend_str,
        "trendClass": trend_class,
        "msp": base_crop["msp"],
        "apmc": apmc,
        "volume": volume,
        "sowing": base_crop["sowing"],
        "harvest": base_crop["harvest"],
        "water": base_crop["water"],
        "districts": districts,
        "source": "Simulated"
    }

@app.route('/api/crop-prices')
def get_crop_prices():
    state = request.args.get('state', 'Gujarat')
    api_key = os.getenv("DATA_GOV_API_KEY")
    
    state_crops_map = {
        "Gujarat": ["Cotton", "Groundnut", "Wheat", "Rice", "Castor Seed", "Bajra (Pearl Millet)", "Maize (Corn)", "Mustard", "Cumin (Jeera)", "Sugarcane"],
        "Andhra Pradesh": ["Rice", "Cotton", "Chillies", "Tobacco", "Groundnut", "Sugarcane", "Mango", "Turmeric", "Maize", "Sweet Orange"],
        "Assam": ["Tea", "Rice", "Jute", "Mustard", "Citrus Fruits", "Sugarcane", "Potatoes", "Maize", "Coconut", "Arecanut"],
        "Bihar": ["Rice", "Wheat", "Sugarcane", "Maize", "Lentils", "Mango", "Potatoes", "Mustard", "Banana", "Jute"],
        "Chhattisgarh": ["Rice (Paddy)", "Maize", "Soybeans", "Groundnut", "Pulses", "Sugarcane", "Mustard", "Wheat", "Cotton", "Vegetables"],
        "Goa": ["Cashew", "Coconut", "Rice", "Arecanut", "Mangoes", "Bananas", "Kokum", "Ragi", "Black Pepper", "Jackfruit"],
        "Haryana": ["Wheat", "Rice", "Mustard", "Sugarcane", "Cotton", "Bajra", "Maize", "Barley", "Gram", "Sunflower"],
        "Himachal Pradesh": ["Apples", "Maize", "Wheat", "Barley", "Off-season Vegetables"],
        "Jammu and Kashmir": ["Saffron", "Apples", "Rice", "Maize", "Barley", "Walnuts"],
        "Jharkhand": ["Rice", "Maize", "Pulses", "Mustard", "Vegetables"],
        "Karnataka": ["Rice", "Ragi", "Sugarcane", "Coffee", "Coconut", "Cardamom"],
        "Kerala": ["Rubber", "Coconut", "Black Pepper", "Cardamom", "Rice", "Coffee"],
        "Madhya Pradesh": ["Soybean", "Wheat", "Gram", "Cotton", "Mustard", "Garlic"],
        "Maharashtra": ["Sugarcane", "Soybean", "Cotton", "Jowar", "Grapes", "Onions"],
        "Manipur": ["Rice", "Maize", "Pulses", "Potato", "Pineapple"],
        "Meghalaya": ["Rice", "Maize", "Potato", "Ginger", "Turmeric", "Pineapple"],
        "Mizoram": ["Rice", "Maize", "Mustard", "Sugarcane", "Ginger", "Anthurium"],
        "Nagaland": ["Rice", "Maize", "Millet", "Cardamom", "Tea", "Cabbage"],
        "Odisha": ["Rice", "Jute", "Sugarcane", "Coconut", "Turmeric", "Cashew"],
        "Punjab": ["Wheat", "Rice", "Cotton", "Sugarcane", "Maize", "Potatoes"],
        "Rajasthan": ["Bajra", "Mustard", "Barley", "Guar", "Wheat", "Coriander"],
        "Sikkim": ["Large Cardamom", "Ginger", "Rice", "Maize", "Mandarin Orange"],
        "Tamil Nadu": ["Rice", "Sugarcane", "Coconut", "Groundnut", "Cotton", "Bananas"],
        "Telangana": ["Rice", "Cotton", "Maize", "Chillies", "Turmeric"],
        "Tripura": ["Rice", "Jackfruit", "Pineapple", "Rubber", "Tea", "Bamboo"],
        "Uttar Pradesh": ["Sugarcane", "Wheat", "Rice", "Potatoes", "Mustard", "Mangoes"],
        "Uttarakhand": ["Rice", "Wheat", "Barley", "Soybeans", "Apples", "Amaranth"],
        "West Bengal": ["Rice", "Jute", "Tea", "Potatoes", "Sugarcane", "Mustard"]
    }
    
    crops = state_crops_map.get(state, ["Rice", "Wheat", "Cotton", "Sugarcane"])
    
    if api_key:
        try:
            resource_id = os.getenv("DATA_GOV_RESOURCE_ID", "35987303-07cb-4ec0-98a1-0cf82d85b597")
            url = f"https://api.data.gov.in/resource/{resource_id}?api-key={api_key}&format=json&limit=1000"
            url_filtered = f"{url}&filters[state_name]={state}"
            
            response = requests.get(url_filtered, timeout=5)
            data = response.json()
            records = data.get('records', [])
            
            if not records:
                url_filtered_alt = f"{url}&filters[state]={state}"
                response = requests.get(url_filtered_alt, timeout=5)
                data = response.json()
                records = data.get('records', [])
                
            if not records:
                response = requests.get(url, timeout=5)
                data = response.json()
                all_records = data.get('records', [])
                records = [r for r in all_records if (r.get('state_name') or r.get('state', '')).lower() == state.lower()]
                
            if records:
                from collections import defaultdict
                commodity_groups = defaultdict(list)
                for r in records:
                    comm = r.get('commodity') or r.get('commodity_name')
                    if comm:
                        commodity_groups[comm].append(r)
                        
                results = {}
                for api_comm, group in commodity_groups.items():
                    norm_crop = normalize_name(api_comm)
                    
                    prices = []
                    for r in group:
                        p_val = r.get('modal_price') or r.get('modal_price_value') or r.get('price')
                        if p_val:
                            try:
                                prices.append(float(p_val))
                            except ValueError:
                                pass
                                
                    if not prices:
                        continue
                        
                    avg_price = int(sum(prices) / len(prices))
                    first_record = group[0]
                    apmc = first_record.get('market') or first_record.get('market_name') or "APMC"
                    district = first_record.get('district') or first_record.get('district_name') or ""
                    if district and district.lower() not in apmc.lower():
                        apmc = f"{apmc} ({district})"
                        
                    base_profile = get_base_profile(norm_crop, state)
                    
                    current_day_str = time.strftime("%Y-%m-%d")
                    seed_str = f"{state}_{norm_crop}_{current_day_str}_{avg_price}"
                    hasher = hashlib.md5(seed_str.encode('utf-8'))
                    hash_int = int(hasher.hexdigest()[:8], 16)
                    trend_pct = round(((hash_int % 50) - 20) / 10.0, 1)
                    trend_icon = "▲" if trend_pct >= 0 else "▼"
                    trend_class = "market-trend-up" if trend_pct >= 0 else "market-trend-down"
                    trend_str = f"{'+' if trend_pct >= 0 else ''}{trend_pct}%"
                    
                    volume_val = (hash_int % 15 + 5) * 1000
                    
                    results[norm_crop] = {
                        "price": f"₹{avg_price:,} / Quintal",
                        "trendIcon": trend_icon,
                        "trendPct": trend_str,
                        "trendClass": trend_class,
                        "msp": base_profile["msp"],
                        "apmc": f"{apmc} APMC",
                        "volume": f"{volume_val:,} Bags",
                        "sowing": base_profile["sowing"],
                        "harvest": base_profile["harvest"],
                        "water": base_profile["water"],
                        "districts": base_profile["districts"],
                        "source": "Live API"
                    }
                    
                final_response = {}
                for c in crops:
                    matched_key = None
                    for r_key in results.keys():
                        if r_key.lower() in c.lower() or c.lower() in r_key.lower():
                            matched_key = r_key
                            break
                    if matched_key:
                        final_response[c] = results[matched_key]
                    else:
                        final_response[c] = get_seeded_market_data(state, c)
                        
                return jsonify(final_response)
        except Exception as ex:
            print(f"Error querying data.gov.in: {ex}")
            
    response_data = {}
    for c in crops:
        response_data[c] = get_seeded_market_data(state, c)
    return jsonify(response_data)

    return render_template('upload.html')

if __name__ == '__main__':
    print("Starting AgriVision AI Web Application...")
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False
    )