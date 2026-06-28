# 🌿 AgriVision - Your Farmer Assistant

### Smart Plant Disease Detection and Farmer Assistance Platform

---

## 📖 Overview

AgriVision is a farmer-focused application designed to help users identify plant diseases quickly using image analysis and provide useful information to support crop management decisions.

Developed as an academic project at **Ganpat University**, the platform aims to make plant disease identification simple, accessible, and practical.

---

## 🚨 Problem Statement

Many farmers struggle to identify plant diseases during the early stages of infection. Delayed diagnosis often leads to reduced crop quality, lower yields, and increased treatment costs.

A simple and accessible digital solution can help farmers detect issues earlier and make informed decisions.

---

## 💡 Solution

AgriVision allows users to upload plant images and receive disease information through an easy-to-use web interface.

The system focuses on:

* Early disease identification
* Faster decision making
* Improved accessibility to agricultural information
* Supporting farmers with technology-driven solutions

---

## ✨ Key Features

* 🌿 Plant disease identification
* 📷 Image upload support
* ⚡ Fast analysis and results
* 🌐 Web-based interface
* 👨‍🌾 Farmer-friendly design

---

## 🛠 Tech Stack

| Category   | Technology                 |
| ---------- | -------------------------- |
| Frontend   | HTML, CSS, JavaScript      |
| Backend    | Flask                      |
| API        | Kindwise Plant Disease API |
| Deployment | Render                     |
| Tools      | Git, GitHub, VS Code       |

---

## 🏗 System Architecture

```mermaid
flowchart TD
A[Upload Plant Image]
--> B[Flask Backend]
--> C[Image Processing]
--> D[Kindwise API]
--> E[Disease Information]
--> F[Display Results]
```

---

## 📂 Folder Structure

```text
AgriVision/
│
├── static/
│   ├── images/
│   ├── uploads/
│   ├── Main_Logo.png
│   └── style.css
│
├── templates/
│   ├── home.html
│   ├── upload.html
│   ├── result.html
│   ├── map.html
│   └── team.html
│
├── uploads/
├── test/
│
├── app.py
├── requirements.txt
├── runtime.txt
├── .env
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/YOUR_USERNAME/AgriVision.git
cd AgriVision

pip install -r requirements.txt
```

---

## 📋 Prerequisites

* Python 3.x
* pip
* Git

---

## 🔐 Environment Variables

Create a `.env` file in the project root directory:

```env
API_KEY=your_kindwise_api_key
```

---

## ▶️ Running the Project

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

## 📚 Usage Guide

1. Open the application.
2. Upload a plant image.
3. Wait for the analysis to complete.
4. View the disease information and recommendations.

---

## 🔌 API Integration

* **Kindwise Plant Disease API— Used for plant disease identification and disease information retrieval.

---

## 📦 Requirements

```text
Flask==3.1.1
gunicorn==26.0.0
tensorflow==2.18.0
numpy
Pillow
opencv-python-headless
python-dotenv
```

---

## 🚀 Deployment

The application is deployed using **Render**.

> ⚠️ The service may take a minute to start if it has been inactive for some time. This is due to free hosting limitations and only affects the first request.

---

## 🎥 Demo

🌐 **Live Demo:TODO: Add your Render URL here

---

## 🚀 Future Improvements

* 🇮🇳 Support for Indian regional languages.
* 🌐 Automatic language translation.
* 🗄️ Database integration for prediction history and analytics.
* 🌾 Support for additional crops and diseases.
* 📱 Mobile application support.
* 📍 Nearby agriculture center recommendations.
* ☁️ Improved cloud scalability and deployment.
* 🔔 Disease alerts and notifications.
* 📊 Historical crop analysis and reporting.
* 🤖 Personalized farming recommendations.

---

## 👥 Team Members

* **Aryan Ponkiya
* **Kausar Rami**

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

---

## 🙏 Acknowledgements

* Ganpat University
* Kindwise Plant Disease API
* Open Source Community
* Farmers and Agricultural Researchers

---

<div align="center">

### 🌱 Building smarter agriculture with technology

Made with ❤️ by Team AgriVision

</div>
