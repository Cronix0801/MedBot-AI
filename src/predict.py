"""
MedBot Prediction Service & API Blueprint
Provides machine learning prediction, confidence ranking, disease insights,
symptom catalog endpoints, and conversational chatbot processing.
"""

from pathlib import Path
import csv
import joblib
import pandas as pd
from flask import Blueprint, request, jsonify

# Import domain knowledge and NLP helpers
from disease_info import (
    SYMPTOM_CATEGORIES,
    SYMPTOM_LABELS,
    get_disease_details,
    extract_symptoms_from_text
)

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "medbot_model.pkl"
DISEASES_CSV = Path(__file__).resolve().parent.parent / "data" / "diseases_list.csv"

# Load trained Random Forest model
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Trained model not found at {MODEL_PATH}. Run src/train.py first.")

model = joblib.load(MODEL_PATH)
feature_names = list(model.feature_names_in_)
classes = list(model.classes_)

def predict_symptoms(symptoms: list[str]) -> str:
    """
    Standard prediction returning top predicted disease name.
    Maintains 100% backwards compatibility with original API signature.
    """
    row = {feat: (1 if feat in symptoms else 0) for feat in feature_names}
    df = pd.DataFrame([row])
    return str(model.predict(df)[0])

def predict_detailed(symptoms: list[str]) -> dict:
    """
    Advanced prediction computing class probabilities, confidence scores,
    and associated clinical metadata and precautions.
    """
    # Clean input symptoms to match model features
    matched_features = [s for s in symptoms if s in feature_names]
    readable_symptoms = [SYMPTOM_LABELS.get(s, s.replace("_", " ").title()) for s in matched_features]

    if not matched_features:
        return {
            "error": "No recognized symptoms provided. Please select at least one valid symptom.",
            "recognized": False
        }

    row = {feat: (1 if feat in matched_features else 0) for feat in feature_names}
    df = pd.DataFrame([row])

    # Predict probabilities across all classes
    probs = model.predict_proba(df)[0]
    ranked_indices = probs.argsort()[::-1]

    top_idx = ranked_indices[0]
    top_disease = classes[top_idx]
    top_confidence = round(float(probs[top_idx]) * 100, 1)

    # Top differential diagnoses (up to 4)
    differentials = []
    for idx in ranked_indices[:4]:
        prob_pct = round(float(probs[idx]) * 100, 1)
        if prob_pct > 0.5:
            differentials.append({
                "disease": classes[idx],
                "confidence": prob_pct
            })

    # Retrieve clinical metadata
    details = get_disease_details(top_disease)

    return {
        "diagnosis": top_disease,
        "confidence": top_confidence,
        "matched_symptoms": readable_symptoms,
        "matched_symptom_ids": matched_features,
        "differentials": differentials,
        "severity": details["severity"],
        "specialist": details["specialist"],
        "description": details["description"],
        "precautions": details["precautions"],
        "red_flags": details["red_flags"],
        "recognized": True
    }

bp = Blueprint("predict", __name__, url_prefix="")

@bp.route("/predict", methods=["GET", "POST"])
def predict_endpoint():
    """
    Prediction endpoint.
    GET: Instructions
    POST: Expects JSON {"symptoms": ["fever", "cough"]}
    """
    if request.method == "GET":
        return jsonify({
            "message": "Send a POST request with JSON {'symptoms': ['fever', 'cough']} to obtain a diagnosis.",
            "available_features_count": len(feature_names)
        }), 200

    data = request.get_json(force=True, silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request body. Expected JSON object."}), 400

    symptoms = data.get("symptoms", [])
    if not isinstance(symptoms, list):
        return jsonify({"error": "'symptoms' must be an array of strings."}), 400

    if len(symptoms) == 0:
        return jsonify({
            "error": "Please select or mention at least one symptom for diagnosis."
        }), 400

    try:
        result = predict_detailed(symptoms)
        if not result.get("recognized", True):
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@bp.route("/api/symptoms", methods=["GET"])
def get_symptoms():
    """Return categorized symptoms for dynamic frontend rendering."""
    return jsonify({
        "categories": SYMPTOM_CATEGORIES,
        "all_features": feature_names,
        "total_count": len(feature_names)
    }), 200

@bp.route("/api/diseases", methods=["GET"])
def get_diseases():
    """Return scraped diseases list from CSV."""
    diseases = []
    if DISEASES_CSV.exists():
        with open(DISEASES_CSV, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if row:
                    diseases.append(row[0].strip())
    else:
        diseases = sorted(classes)

    return jsonify({
        "total": len(diseases),
        "diseases": diseases[:500]  # return top 500 for fast UI display
    }), 200

@bp.route("/api/chat", methods=["POST"])
def chat_endpoint():
    """
    Conversational MedBot endpoint.
    Expects {"message": "I'm having a persistent dry cough, high fever and chest tightness"}.
    Extracts symptoms using NLP regex matching, runs prediction, and returns conversational response.
    """
    data = request.get_json(force=True, silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field in JSON request body."}), 400

    user_message = str(data["message"]).strip()
    if not user_message:
        return jsonify({"reply": "Please describe your symptoms, and I'll help analyze them for you."}), 200

    detected_symptoms = extract_symptoms_from_text(user_message)

    if not detected_symptoms:
        return jsonify({
            "reply": (
                "I couldn't detect specific medical symptoms from your message. "
                "Could you tell me more about what you are experiencing? "
                "For example: 'I have a high fever, dry cough, and shortness of breath since yesterday.'"
            ),
            "detected_symptoms": [],
            "diagnosis_available": False
        }), 200

    # Run prediction with detected symptoms
    result = predict_detailed(detected_symptoms)
    readable = result["matched_symptoms"]

    reply_text = (
        f"Based on the symptoms you reported ({', '.join(readable)}), "
        f"the most likely primary condition is **{result['diagnosis']}** "
        f"with approximately **{result['confidence']}%** model confidence."
    )

    return jsonify({
        "reply": reply_text,
        "detected_symptoms": readable,
        "detected_symptom_ids": detected_symptoms,
        "diagnosis_available": True,
        "details": result
    }), 200