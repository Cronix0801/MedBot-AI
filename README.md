# MedBot AI — Clinical Symptom Checker & Health Assistant

MedBot is a machine-learning-driven clinical symptom analyzer and medical triage assistant. It predicts likely medical conditions from reported symptoms, estimates confidence probabilities across differentials, provides recommended home care precautions, flags emergency warning signs, and directs users to appropriate medical specialists.

---

## 📁 Project Architecture

```
Medic/
├── data/
│   ├── diseases_list.csv         # 1,430+ medical diseases scraped from clinical registries
│   └── training_data.csv         # 1,085 multi-symptom clinical training records
├── models/
│   └── medbot_model.pkl          # Trained Random Forest classifier (35 symptoms, 31 conditions)
├── scripts/
│   └── scrape_diseases.py        # Web scraper for comprehensive A-Z disease listings
├── src/
│   ├── static/
│   │   ├── favicon.svg           # MedBot vector favicon
│   │   ├── index.html            # Single-page diagnostic dashboard & chat interface
│   │   ├── script.js             # Client interactivity, API queries, and chat logic
│   │   └── style.css             # Healthcare UI design tokens & responsive styling
│   ├── app.py                    # Flask application entry point
│   ├── disease_info.py           # Domain clinical metadata, severity, precautions, NLP patterns
│   ├── predict.py                # Prediction service, probabilities, and REST endpoints
│   └── train.py                  # Model training, stratified split, evaluation & serialization
├── tests/
│   └── test_medbot.py            # Automated unit and integration test suite
├── requirements.txt              # Production Python package requirements
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Activate the Virtual Environment
```powershell
.\venv\Scripts\activate
```

### 2. (Optional) Retrain the Model
```powershell
python src\train.py
```
*Current benchmark: 86.2% validation accuracy across 31 distinct diseases.*

### 3. (Optional) Run the Disease Scraper
```powershell
python scripts\scrape_diseases.py
```
*Scrapes 1,430+ diseases across A-Z directories into `data\diseases_list.csv`.*

### 4. Run the Web Application
```powershell
python src\app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

### 5. Run the Automated Tests
```powershell
python -m unittest tests\test_medbot.py
```

---

## 🌐 API Reference

### `GET /health`
Returns system status.
```json
{
  "service": "MedBot AI Healthcare Assistant",
  "status": "healthy",
  "version": "2.0.0"
}
```

### `GET /api/symptoms`
Returns categorized symptom catalog across body systems (Respiratory, General, Neurological, Digestive, etc.).

### `POST /predict`
Run clinical prediction on an array of symptoms.
- **Request Body:**
  ```json
  {
    "symptoms": ["fever", "chills", "body_aches", "cough", "fatigue"]
  }
  ```
- **Response:**
  ```json
  {
    "diagnosis": "Influenza (Flu)",
    "confidence": 51.0,
    "severity": "Moderate",
    "specialist": "General Physician / Pulmonologist",
    "description": "An acute viral infection that attacks your respiratory system...",
    "differentials": [
      { "disease": "Influenza (Flu)", "confidence": 51.0 },
      { "disease": "Malaria", "confidence": 8.3 },
      { "disease": "Bronchitis", "confidence": 7.6 }
    ],
    "precautions": [
      "Isolate at home to prevent spreading the infection to others.",
      "Drink plenty of water, electrolyte drinks, and warm soups."
    ],
    "red_flags": "Difficulty breathing, persistent chest pressure, bluish lips."
  }
  ```

### `POST /api/chat`
Conversational endpoint with natural language symptom extraction.
- **Request Body:**
  ```json
  {
    "message": "I'm having a persistent dry cough, high fever and chest tightness"
  }
  ```
- **Response:**
  Returns friendly clinical triage response, detected symptoms, and diagnostic breakdown.

---

## 🛡️ Medical Disclaimer
MedBot is intended for educational screening and triage assistance. It is not a licensed medical practitioner and does not replace professional clinical evaluation or emergency care.
