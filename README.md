# 🌿 PlantCare AI — Advanced Plant Disease Detection System

PlantCare AI is an intelligent, real-time plant disease detection web application developed for the AI & Machine Learning department at **Ganpat University**. By combining a futuristic, glassmorphic UI, a dynamic canvas simulation background, and the power of cloud-based Transfer Learning, the system allows users to instantly identify plant species and diagnose crop diseases using leaf images or live device cameras.

---

## 🚀 How to Run the Project

Follow these steps to set up and run PlantCare AI on your local system:

### 1. Install Dependencies
Open your terminal/command prompt, navigate to the project directory, and install the required Python libraries:
```bash
pip install -r requirements.txt
# Make sure the requests library is installed:
pip install requests
```

### 2. Configure the API Key
Get your free API Key from the [Kindwise / Plant.id Dashboard](https://admin.kindwise.com/). 
Create a file named `.env` in the project root directory and add your key:
```env
PLANT_ID_API_KEY=your_actual_api_key_here
```
*(Alternatively, you can modify line 13 of `app.py` to paste your key directly as a default fallback).*

### 3. Run the Application
Launch the Flask development server:
```bash
python app.py
```
Wait for the terminal to display `* Debugger is active!` and `* Running on http://127.0.0.1:5000`.

### 4. Open the Web Browser
Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

*(To stop the server, press `Ctrl + C` in your terminal).*

---

## 🌟 Key Features

### 1. Cloud-Based AI Diagnostics Core
*   **Plant.id v3 Integration**: Replaces heavy local models with a high-performance REST API, enabling instant startup and lightweight hosting.
*   **Dual Classification**: Concurrently identifies the **plant species** (e.g., Tomato) and **specific diseases** (e.g., Early Blight).
*   **Actionable Care Guidelines**: Returns organic, chemical, and preventative treatment advice parsed directly from the API response or fell back onto custom localized expert recommendations.
*   **Null-Safe Safety Layer**: Fully protected against empty identification outputs or invalid images, preventing server crashes.

### 2. Live Web Camera Capture Interface
*   **Native Camera Stream**: Enables real-time video capture using the device's webcam or mobile rear camera (`facingMode: "environment"`).
*   **In-Memory Frame Capture**: Captures snapshots onto an offscreen canvas, serializes them as binary blobs, and injects them dynamically into the form using standard HTML `DataTransfer` file structures.

### 3. Glassmorphic Cyber-Agri UI Theme
*   **Futuristic Visual Design**: Built using HSL-tailored dark modes, smooth gradients, and glassmorphic translucent panels (using vanilla CSS backdrop-filters).
*   **Dynamic Animations**: Smooth scroll-triggered fading actions, pulse glows, and a matrix-style scanning line during image classification.

### 4. Physics-Based Interactive Background Canvas
*   **Deterministic Foliage Generation**: Uses custom coordinate-keyed seeded random functions to draw complex fractal trees and grass blades, avoiding frame-to-frame rendering flicker.
*   **Waving Grass Waves**: Renders grass as tapered 2D polygon paths filled with vertical green gradients that bend in response to continuous rolling sine waves.
*   **Hierarchical Branch Swaying**: Uses recursive coordinate translations to sway tree limbs in response to wind gusts. Trunks sway slowly, while outer twigs wiggle at higher frequencies.
*   **Parallax Depth Sorting**: Composites elements back-to-front (Far Hill -> Far Grass/Trees -> Near Hill -> Near Grass/Trees -> Floating Leaves) to create deep perspective layers.

---

## 📂 Project Directory Structure

```text
plant-disease-detection/
│
├── app.py                      # Flask backend (API integration, routing, parsing)
├── .env                        # Local configuration file storing the Plant.id API key
├── mobilenetv2_best.keras      # (Deprecated) Original local training weights file
├── requirements.txt            # Python library dependencies
├── README.md                   # Complete system documentation
│
├── static/                     # Static assets & scripts
│   ├── style.css               # Futuristic glassmorphic dark theme stylesheet
│   ├── leaves.js               # Canvas foliage simulation & wind sway animation loop
│   ├── logo1.png               # Brand icon
│   └── uploads/                # Temporary directory storing uploaded leaf photos
│
└── templates/                  # Flask HTML view templates
    ├── home.html               # Main welcome dashboard
    ├── about.html              # Architecture & dataset specifications page
    ├── team.html               # "About Us" project credits page
    ├── upload.html             # Upload/Live Camera scanner interface
    └── result.html             # Diagnostic dashboard (species, disease, confidence, recommendations)
```

---

## 🧠 Technologies Used

*   **Backend**: Python, Flask (web framework)
*   **APIs & Networking**: requests (HTTP library), base64 (encoding), Plant.id v3 API (Kindwise)
*   **Frontend Logic**: Vanilla JavaScript (HTML5 Canvas 2D API, MediaDevices Camera API)
*   **Styling**: HTML5, CSS3 Grid/Flexbox (incorporating custom linear-gradients & backdrop-blur filters)

---

## 👨‍💻 Project Team & Credits

This project was built as an academic AI & Machine Learning application under the supervision of **Ganpat University (Mehsana, Gujarat)**.

### Team Leaders:
*   👑 **Aryan Ponkiya** — [aryanpatel09395@gmail.com](mailto:aryanpatel09395@gmail.com)
*   👑 **Kausar rami** — [ramikausar@gmail.com](mailto:ramikausar@gmail.com)

**Department**: AI & Machine Learning Department  
**Institution**: Ganpat University (2025–2026 Academic Year)

---

## 📜 License
This project is developed for educational, academic demonstration, and research purposes.
