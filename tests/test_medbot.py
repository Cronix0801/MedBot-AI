"""
Automated Integration and Unit Tests for MedBot AI Healthcare System
"""

import sys
from pathlib import Path

# Add src to path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import unittest
from app import app
from predict import predict_symptoms, predict_detailed
from disease_info import extract_symptoms_from_text


class TestMedBot(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_health_endpoint(self):
        """Test system health check."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")

    def test_ui_served(self):
        """Test root route serves HTML."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"MedBot", response.data)
        self.assertIn(b"Clinical Symptom Analyzer", response.data)

    def test_symptoms_api(self):
        """Test symptoms categorization API."""
        response = self.client.get("/api/symptoms")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("categories", data)
        self.assertIn("Respiratory", data["categories"])
        self.assertGreater(data["total_count"], 30)

    def test_diseases_api(self):
        """Test diseases directory API."""
        response = self.client.get("/api/diseases")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("diseases", data)
        self.assertGreater(data["total"], 100)

    def test_predict_symptoms_legacy(self):
        """Test backward compatible predict_symptoms signature."""
        diagnosis = predict_symptoms(["fever", "cough", "chills"])
        self.assertIsInstance(diagnosis, str)
        self.assertGreater(len(diagnosis), 0)

    def test_predict_detailed_flu(self):
        """Test detailed prediction for flu symptoms."""
        result = predict_detailed(["fever", "chills", "body_aches", "fatigue", "cough"])
        self.assertTrue(result["recognized"])
        self.assertEqual(result["diagnosis"], "Influenza (Flu)")
        self.assertGreater(result["confidence"], 30)
        self.assertIn("precautions", result)
        self.assertIn("specialist", result)

    def test_predict_endpoint_post(self):
        """Test POST /predict endpoint."""
        payload = {"symptoms": ["runny_nose", "sneezing", "nasal_congestion"]}
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("diagnosis", data)
        self.assertIn("confidence", data)

    def test_nlp_extraction(self):
        """Test NLP symptom extraction from natural language."""
        text = "I have a high fever, severe dry cough, and lost my smell since yesterday."
        extracted = extract_symptoms_from_text(text)
        self.assertIn("fever", extracted)
        self.assertIn("dry_cough", extracted)
        self.assertIn("loss_of_smell", extracted)

    def test_chat_endpoint(self):
        """Test POST /api/chat endpoint."""
        payload = {"message": "I'm experiencing vomiting, severe diarrhea, and stomach cramps."}
        response = self.client.post("/api/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["diagnosis_available"])
        self.assertIn("reply", data)
        self.assertIn("diarrhea", data["detected_symptom_ids"])


if __name__ == "__main__":
    unittest.main()
