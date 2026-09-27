"""
MedBot Model Trainer
Loads symptom-disease dataset, trains a Random Forest Classifier with probability estimation,
evaluates metrics (accuracy, classification report), and persists model to models/medbot_model.pkl.
"""

from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

ROOT = Path(__file__).resolve().parent.parent
DATA_FP = ROOT / "data" / "training_data.csv"
MODEL_FP = ROOT / "models" / "medbot_model.pkl"

def train():
    print(f"Loading training data from: {DATA_FP}")
    if not DATA_FP.exists():
        raise FileNotFoundError(f"Training dataset not found at {DATA_FP}")

    df = pd.read_csv(DATA_FP)
    print(f"Dataset shape: {df.shape} ({df['disease'].nunique()} distinct diseases)")

    X = df.drop(columns=["disease"])
    y = df["disease"]

    # Stratified split to maintain balanced representation across all diseases
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set: {X_train.shape[0]} samples, Test set: {X_test.shape[0]} samples")

    # High-performance Random Forest with probability calibration
    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=16,
        min_samples_split=2,
        class_weight="balanced",
        random_state=42
    )

    print("Fitting Random Forest classifier...")
    clf.fit(X_train, y_train)

    # Evaluation
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Validation Accuracy: {acc * 100:.2f}%")
    print("\nClassification Report (Sample):")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Ensure target directory exists
    MODEL_FP.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, MODEL_FP)
    print(f"Model successfully saved to {MODEL_FP}")
    print(f"Total features learned: {len(clf.feature_names_in_)}")

if __name__ == "__main__":
    train()