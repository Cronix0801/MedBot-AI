"""
MedBot Disease Scraper
Scrapes comprehensive A-Z disease and medical condition listings from Medindia
and saves them to data/diseases_list.csv with offline fallback support.
"""

import csv
import string
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "diseases_list.csv"

BASE_URL = "https://www.medindia.net/drugs/medical-condition/index.htm"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Standard curated fallback diseases in case of network unavailability
FALLBACK_DISEASES = [
    "Allergic Rhinitis", "Alzheimer's Disease", "Amoebiasis", "Anemia", "Angina Pectoris",
    "Ankylosing Spondylitis", "Appendicitis", "Arrhythmia", "Arthritis", "Asthma",
    "Atherosclerosis", "Atopic Dermatitis", "Bacterial Meningitis", "Bell's Palsy",
    "Bipolar Disorder", "Bronchiectasis", "Bronchitis", "Candidiasis", "Cataract",
    "Celiac Disease", "Chickenpox", "Chikungunya", "Cholecystitis", "Chronic Kidney Disease",
    "Cirrhosis", "Common Cold", "Conjunctivitis", "COPD", "COVID-19",
    "Crohn's Disease", "Cushing's Syndrome", "Cystic Fibrosis", "Deep Vein Thrombosis",
    "Dengue Fever", "Depression", "Diabetes Mellitus Type 1", "Diabetes Mellitus Type 2",
    "Diverticulitis", "Dry Eye Syndrome", "Dysentery", "Eczema", "Endometriosis",
    "Epilepsy", "Fibromyalgia", "Food Poisoning", "Gallstones", "Gastritis",
    "Gastroenteritis", "GERD", "Glaucoma", "Gout", "Graves' Disease",
    "Guillain-Barre Syndrome", "Hashimoto's Thyroiditis", "Heart Failure", "Hepatitis A",
    "Hepatitis B", "Hepatitis C", "Herpes Simplex", "Herpes Zoster (Shingles)",
    "Hodgkin's Lymphoma", "Hypertension", "Hyperthyroidism", "Hypothyroidism",
    "Impetigo", "Influenza (Flu)", "Insomnia", "Iron Deficiency Anemia",
    "Irritable Bowel Syndrome", "Kidney Stones", "Laryngitis", "Leukemia",
    "Lyme Disease", "Malaria", "Measles", "Migraine", "Multiple Sclerosis",
    "Mumps", "Myasthenia Gravis", "Myocardial Infarction", "Narcolepsy",
    "Nephrotic Syndrome", "Non-Alcoholic Fatty Liver Disease", "Obesity", "Osteoarthritis",
    "Osteoporosis", "Otitis Media", "Pancreatitis", "Parkinson's Disease",
    "Peptic Ulcer Disease", "Pericarditis", "Pneumonia", "Polycystic Ovary Syndrome (PCOS)",
    "Psoriasis", "Pulmonary Embolism", "Rheumatoid Arthritis", "Rhinitis",
    "Ringworm", "Rosacea", "Rubella", "Salmonellosis", "Scabies",
    "Scarlet Fever", "Sciatica", "Scoliosis", "Seborrheic Dermatitis",
    "Sinusitis", "Sleep Apnea", "Strep Throat", "Stroke", "Systemic Lupus Erythematosus",
    "Tension Headache", "Tetanus", "Thrombosis", "Thyroiditis", "Tinnitus",
    "Tonsillitis", "Toxoplasmosis", "Tuberculosis", "Typhoid Fever",
    "Ulcerative Colitis", "Urinary Tract Infection (UTI)", "Urticaria (Hives)",
    "Varicose Veins", "Vertigo", "Vitiligo", "Whooping Cough (Pertussis)", "Yellow Fever"
]


def clean_disease_name(raw_name: str) -> str:
    """Clean and standardize medical disease names."""
    if not raw_name:
        return ""
    # Split by delimiters like |, (, /, -
    text = raw_name.split("|")[0].split("(")[0].strip()
    # Remove common filler phrases
    for prefix in ["All ", "View ", "List of "]:
        if text.startswith(prefix):
            return ""
    # Remove non-alpha prefixes or trailing noise
    text = text.strip(" -:,;\t\r\n")
    if len(text) < 3 or len(text) > 80:
        return ""
    return text


def fetch_diseases_from_web() -> list[str]:
    """Scrape disease names from Medindia A-Z directory."""
    print("Connecting to Medindia disease directories...")
    diseases = set()
    session = requests.Session()
    session.headers.update(HEADERS)

    # Scrape main page first
    try:
        resp = session.get(BASE_URL, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                if "/drugs/medical-condition/" in a["href"]:
                    cleaned = clean_disease_name(a.get_text(strip=True))
                    if cleaned:
                        diseases.add(cleaned)
    except Exception as e:
        print(f"Warning: Main page scrape error: {e}")

    # Scrape A-Z letters
    letters = list(string.ascii_lowercase)
    print(f"Scraping A-Z listings ({len(letters)} letters)...")
    for letter in letters:
        url = f"{BASE_URL}?alpha={letter}"
        try:
            r = session.get(url, timeout=6)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    if "/drugs/medical-condition/" in a["href"]:
                        cleaned = clean_disease_name(a.get_text(strip=True))
                        if cleaned:
                            diseases.add(cleaned)
            time.sleep(0.05)  # respectful scraping delay
        except Exception as e:
            print(f"Letter {letter} notice: {e}")
            continue

    print(f"Successfully scraped {len(diseases)} unique conditions from the web.")
    return sorted(diseases)


def save_csv(diseases: list[str]) -> Path:
    """Save sorted list of unique disease names to CSV."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["disease"])
        for name in diseases:
            writer.writerow([name])
    return OUTPUT


def main():
    try:
        diseases = fetch_diseases_from_web()
    except Exception as e:
        print(f"Web scraping encountered an issue: {e}")
        diseases = []

    # If web scraping returned very few results, supplement with curated medical list
    combined = set(diseases)
    combined.update(FALLBACK_DISEASES)
    final_list = sorted(combined)

    saved_path = save_csv(final_list)
    print(f"Done! Saved {len(final_list)} diseases to {saved_path}")


if __name__ == "__main__":
    main()