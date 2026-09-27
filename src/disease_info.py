"""
Medical Knowledge Base, Disease Profiles, and Natural Language Symptom Extraction
Provides rich clinical context, precautions, specialists, and NLP helpers for MedBot.
"""

import re

# Comprehensive categorization of all 35 model features
SYMPTOM_CATEGORIES = {
    "Respiratory": [
        {"id": "cough", "label": "Cough", "desc": "Persistent dry or wet cough"},
        {"id": "dry_cough", "label": "Dry Cough", "desc": "Tickly cough without phlegm"},
        {"id": "productive_cough", "label": "Productive / Wet Cough", "desc": "Cough bringing up mucus or phlegm"},
        {"id": "difficulty_breathing", "label": "Difficulty Breathing", "desc": "Labored breathing or shortness of breath"},
        {"id": "shortness_of_breath", "label": "Shortness of Breath", "desc": "Feeling breathless during exertion or rest"},
        {"id": "chest_pain", "label": "Chest Pain / Tightness", "desc": "Ache, pressure, or sharpness in chest"},
        {"id": "sore_throat", "label": "Sore Throat", "desc": "Pain, scratchiness, or irritation in throat"},
        {"id": "runny_nose", "label": "Runny Nose (Rhinorrhea)", "desc": "Excess nasal drainage"},
        {"id": "nasal_congestion", "label": "Nasal Congestion / Blocked Nose", "desc": "Stuffy nose or sinus fullness"},
        {"id": "sneezing", "label": "Frequent Sneezing", "desc": "Repetitive involuntary expulsions"}
    ],
    "General & Systemic": [
        {"id": "fever", "label": "Fever", "desc": "Elevated body temperature above 38°C (100.4°F)"},
        {"id": "high_fever", "label": "High Fever (> 102°F)", "desc": "Very high spiking fever"},
        {"id": "chills", "label": "Chills & Shivering", "desc": "Feeling cold with involuntary shaking"},
        {"id": "fatigue", "label": "Fatigue & Malaise", "desc": "Severe tiredness, exhaustion, or weakness"},
        {"id": "body_aches", "label": "Generalized Body Aches", "desc": "Diffuse aching across muscles and body"},
        {"id": "muscle_pain", "label": "Muscle Pain (Myalgia)", "desc": "Soreness or tenderness in specific muscles"}
    ],
    "Neurological & Head": [
        {"id": "headache", "label": "Headache", "desc": "Throbbing, dull, or sharp pain in head"},
        {"id": "dizziness", "label": "Dizziness / Lightheadedness", "desc": "Feeling faint, woozy, or unsteady"},
        {"id": "stiff_neck", "label": "Stiff Neck", "desc": "Difficulty or pain when flexing neck forward"},
        {"id": "light_sensitivity", "label": "Sensitivity to Light (Photophobia)", "desc": "Discomfort or pain from bright lights"}
    ],
    "Digestive & Abdominal": [
        {"id": "nausea", "label": "Nausea", "desc": "Feeling of sickness with an inclination to vomit"},
        {"id": "vomiting", "label": "Vomiting", "desc": "Involuntary regurgitation of stomach contents"},
        {"id": "diarrhea", "label": "Diarrhea", "desc": "Frequent loose or watery stools"},
        {"id": "abdominal_pain", "label": "Abdominal / Stomach Pain", "desc": "Cramping, aching, or sharp belly pain"},
        {"id": "stomach_cramps", "label": "Stomach Cramps", "desc": "Intermittent painful spasms in abdomen"},
        {"id": "loss_of_appetite", "label": "Loss of Appetite", "desc": "Reduced desire to eat"},
        {"id": "acidity_heartburn", "label": "Acidity / Heartburn / GERD", "desc": "Burning sensation behind breastbone"}
    ],
    "Sensory, Skin & Joints": [
        {"id": "joint_pain", "label": "Joint Pain (Arthralgia)", "desc": "Aching or stiffness in knees, fingers, hips"},
        {"id": "skin_rash", "label": "Skin Rash", "desc": "Red patches, spots, or erupted areas on skin"},
        {"id": "itching", "label": "Itching (Pruritus)", "desc": "Irritating sensation prompting scratching"},
        {"id": "watery_eyes", "label": "Watery / Red Eyes", "desc": "Excessive tearing or conjunctival redness"},
        {"id": "loss_of_smell", "label": "Loss of Smell (Anosmia)", "desc": "Inability to detect odors"},
        {"id": "loss_of_taste", "label": "Loss of Taste (Ageusia)", "desc": "Inability to perceive sweet, sour, salty"}
    ],
    "Urinary": [
        {"id": "burning_urination", "label": "Burning Sensation During Urination", "desc": "Dysuria or stinging sensation"},
        {"id": "frequent_urination", "label": "Frequent Urination", "desc": "Need to urinate more often than usual"}
    ]
}

# Fast lookup for symptom labels
SYMPTOM_LABELS = {
    item["id"]: item["label"]
    for category in SYMPTOM_CATEGORIES.values()
    for item in category
}

# Clinical metadata, precautions, and specialist routing for diseases
DISEASE_METADATA = {
    "Common Cold": {
        "severity": "Mild",
        "specialist": "General Physician / Family Doctor",
        "description": "A viral infectious disease of the upper respiratory tract that primarily affects the nose, throat, and sinuses.",
        "precautions": [
            "Get plenty of bed rest to allow your immune system to recover.",
            "Stay well hydrated with warm fluids like broths, herbal teas, and water.",
            "Use saline nasal drops or steam inhalation to relieve congestion.",
            "Over-the-counter decongestants and throat lozenges can help manage discomfort."
        ],
        "red_flags": "High fever lasting more than 3 days, difficulty breathing, or severe ear pain."
    },
    "Influenza (Flu)": {
        "severity": "Moderate",
        "specialist": "General Physician / Pulmonologist",
        "description": "An acute viral infection that attacks your respiratory system, commonly marked by sudden high fever, chills, and severe muscle aches.",
        "precautions": [
            "Isolate at home to prevent spreading the infection to others.",
            "Drink plenty of water, electrolyte drinks, and warm soups.",
            "Take antipyretics (e.g. Paracetamol) as advised by your healthcare provider for fever and body aches.",
            "Consult a physician promptly if you fall into high-risk categories (elderly, asthma, pregnancy)."
        ],
        "red_flags": "Difficulty breathing, persistent chest pressure, bluish lips, or confusion."
    },
    "COVID-19": {
        "severity": "Moderate to High",
        "specialist": "Infectious Disease Specialist / Pulmonologist",
        "description": "A contagious disease caused by the SARS-CoV-2 coronavirus, characterized by respiratory symptoms, fatigue, and potential loss of taste/smell.",
        "precautions": [
            "Self-isolate immediately in a well-ventilated room.",
            "Monitor oxygen saturation with a pulse oximeter twice daily (keep above 94%).",
            "Stay hydrated and take prescribed fever-reducing medications.",
            "Wear a medical mask if you need to be near others."
        ],
        "red_flags": "Oxygen levels below 93%, severe shortness of breath, continuous chest tightness, or confusion."
    },
    "Pneumonia": {
        "severity": "High / Urgent",
        "specialist": "Pulmonologist / Critical Care Physician",
        "description": "An inflammatory condition of the lung affecting primarily the small air sacs known as alveoli, causing fluid buildup and impaired oxygen transfer.",
        "precautions": [
            "Seek urgent medical evaluation for diagnostic chest X-ray and sputum tests.",
            "Complete full course of antibiotics or antivirals exactly as prescribed.",
            "Rest completely and avoid all tobacco or second-hand smoke exposure.",
            "Use deep breathing exercises once recommended by your clinician."
        ],
        "red_flags": "Persistent high fever, severe breathlessness, rapid breathing, or coughing up blood."
    },
    "Bronchitis": {
        "severity": "Moderate",
        "specialist": "Pulmonologist / General Physician",
        "description": "Inflammation of the lining of the bronchial tubes, which carry air to and from your lungs, leading to deep cough and chest soreness.",
        "precautions": [
            "Use a cool-mist humidifier or breathe in moist steam to loosen mucus.",
            "Avoid irritants like cigarette smoke, dust, and fumes.",
            "Drink at least 8 to 10 glasses of water daily to thin respiratory secretions.",
            "Get adequate rest and do not suppress productive mucus coughs unnecessarily."
        ],
        "red_flags": "Cough lasting over 3 weeks, fever over 101°F, or wheezing."
    },
    "Asthma": {
        "severity": "Moderate to Emergency",
        "specialist": "Allergist / Pulmonologist",
        "description": "A chronic condition in which your airways narrow and swell and may produce extra mucus, making breathing difficult.",
        "precautions": [
            "Keep quick-relief inhaler (e.g., Albuterol/Salbutamol) on hand at all times.",
            "Identify and avoid known asthma triggers (pollen, cold air, smoke, pet dander).",
            "Follow your written Asthma Action Plan provided by your specialist.",
            "Monitor peak flow readings regularly."
        ],
        "red_flags": "Severe shortness of breath where talking is difficult, inhaler does not help, or blue discoloration around lips/nails."
    },
    "Allergic Rhinitis": {
        "severity": "Mild",
        "specialist": "Allergist / ENT Specialist",
        "description": "An allergic response to airborne allergens such as pollen, dust mites, or animal fur, causing sneezing and runny nose.",
        "precautions": [
            "Minimize exposure to known allergens (keep windows closed during high pollen seasons).",
            "Use nasal saline rinses daily to wash away allergens.",
            "Non-drowsy oral antihistamines or steroid nasal sprays can provide rapid relief.",
            "Wash bedding weekly in hot water."
        ],
        "red_flags": "Sinus pain accompanied by high fever or vision changes."
    },
    "Strep Throat": {
        "severity": "Moderate",
        "specialist": "ENT Specialist / General Physician",
        "description": "A bacterial infection caused by Streptococcus pyogenes, causing severe sudden throat pain, inflamed tonsils, and high fever.",
        "precautions": [
            "Consult a physician for a rapid strep throat swab test.",
            "If prescribed antibiotics, finish the full course even if you feel better quickly.",
            "Gargle with warm salt water several times a day.",
            "Replace your toothbrush 24-48 hours after starting antibiotics."
        ],
        "red_flags": "Difficulty swallowing saliva, inability to open mouth, or labored breathing."
    },
    "Sinusitis": {
        "severity": "Mild to Moderate",
        "specialist": "ENT Specialist",
        "description": "Inflammation or swelling of the tissue lining the sinuses, causing facial pressure, congestion, and throbbing headaches.",
        "precautions": [
            "Apply warm, moist compresses to face around nose and eyes.",
            "Perform regular nasal irrigation with sterile saline.",
            "Stay well hydrated to encourage drainage of mucus.",
            "Sleep with head slightly elevated to relieve congestion."
        ],
        "red_flags": "Swelling or redness around the eyes, stiff neck, or severe frontal headache."
    },
    "Migraine": {
        "severity": "Moderate",
        "specialist": "Neurologist",
        "description": "A neurological condition characterized by intense, throbbing headaches, often accompanied by extreme light/sound sensitivity and nausea.",
        "precautions": [
            "Rest in a quiet, dark room at the earliest onset of symptoms.",
            "Apply a cold compress or ice pack to forehead or back of neck.",
            "Stay hydrated and avoid skipping meals.",
            "Identify personal triggers (certain foods, stress, lack of sleep, sensory overload)."
        ],
        "red_flags": "Sudden thunderclap headache (worst headache of your life), numbness, or difficulty speaking."
    },
    "Tension Headache": {
        "severity": "Mild",
        "specialist": "General Physician / Neurologist",
        "description": "The most common type of headache, feeling like a tight band wrapped around the forehead, caused by muscular stress or fatigue.",
        "precautions": [
            "Practice gentle neck and shoulder stretching exercises.",
            "Take short screen breaks throughout the day (follow 20-20-20 rule).",
            "Ensure regular 7-8 hours of quality sleep.",
            "Stay hydrated and reduce excessive caffeine intake."
        ],
        "red_flags": "Headache following head trauma or accompanied by confusion."
    },
    "Gastroenteritis (Stomach Flu)": {
        "severity": "Moderate",
        "specialist": "Gastroenterologist / General Physician",
        "description": "Inflammation of the gastrointestinal tract involving stomach and small intestine, causing acute diarrhea, vomiting, and cramps.",
        "precautions": [
            "Sip Oral Rehydration Salts (ORS) or electrolyte solutions continuously.",
            "Eat bland, easy-to-digest foods (bananas, rice, applesauce, toast - BRAT diet).",
            "Avoid dairy, greasy foods, caffeine, and alcohol until fully recovered.",
            "Wash hands thoroughly with soap and water after using the restroom."
        ],
        "red_flags": "Signs of dehydration (no urine for 8+ hours, dry mouth, dizziness), blood in stool, or inability to keep fluids down for 24h."
    },
    "Food Poisoning": {
        "severity": "Moderate",
        "specialist": "General Physician / Gastroenterologist",
        "description": "Illness caused by consuming food or water contaminated with pathogenic bacteria, viruses, or toxins.",
        "precautions": [
            "Hydrate aggressively with small, frequent sips of electrolyte solutions.",
            "Rest your stomach by avoiding solid food for a few hours until vomiting subsides.",
            "Avoid anti-diarrheal medication unless instructed by a physician, as toxins must clear.",
            "Gradually introduce plain crackers, clear broths, and boiled rice."
        ],
        "red_flags": "High fever over 102°F, bloody vomit or stool, or severe dehydration."
    },
    "GERD (Acid Reflux)": {
        "severity": "Mild to Moderate",
        "specialist": "Gastroenterologist",
        "description": "Gastroesophageal reflux disease occurs when stomach acid frequently flows back into the tube connecting your mouth and stomach.",
        "precautions": [
            "Avoid lying down for at least 2 to 3 hours after eating.",
            "Avoid trigger foods (citrus, tomatoes, spicy meals, caffeine, chocolate, fatty meals).",
            "Eat smaller, more frequent meals rather than large heavy dinners.",
            "Elevate the head of your bed by 6 inches."
        ],
        "red_flags": "Difficulty swallowing food, vomiting blood, or unexplained weight loss."
    },
    "Peptic Ulcer Disease": {
        "severity": "Moderate to High",
        "specialist": "Gastroenterologist",
        "description": "Open sores that develop on the inside lining of your stomach and the upper portion of your small intestine.",
        "precautions": [
            "Consult a doctor for H. pylori testing and endoscopy evaluation.",
            "Avoid NSAID pain relievers (like ibuprofen or aspirin) which worsen ulcers.",
            "Refrain from smoking and alcohol consumption.",
            "Take prescribed acid-suppressing medication (PPIs) consistently."
        ],
        "red_flags": "Black or tarry stools, coffee-ground vomiting, or sudden excruciating abdominal pain."
    },
    "Appendicitis": {
        "severity": "Medical Emergency",
        "specialist": "General Surgeon / Emergency Medicine",
        "description": "An acute inflammation of the appendix that can rapidly lead to rupture and life-threatening peritonitis without prompt surgery.",
        "precautions": [
            "SEEK IMMEDIATE EMERGENCY MEDICAL CARE.",
            "Do NOT eat, drink, or take laxatives/painkillers before being evaluated by a surgeon.",
            "Do NOT apply heat pads to the abdomen as it may accelerate rupture.",
            "Go straight to the nearest emergency department."
        ],
        "red_flags": "Severe localized lower right quadrant abdominal pain, vomiting, fever."
    },
    "Urinary Tract Infection (UTI)": {
        "severity": "Moderate",
        "specialist": "Urologist / General Physician",
        "description": "An infection in any part of your urinary system—kidneys, ureters, bladder, or urethra—most commonly causing painful, frequent urination.",
        "precautions": [
            "See a healthcare provider for urine culture and appropriate antibiotics.",
            "Drink plenty of water to help flush out bacteria from the urinary tract.",
            "Urinate as soon as the urge arises without holding it in.",
            "Wipe from front to back after using the toilet."
        ],
        "red_flags": "High fever, chills, nausea, and sharp pain in the side or lower back (indicating kidney involvement)."
    },
    "Kidney Stones": {
        "severity": "Moderate to Urgent",
        "specialist": "Nephrologist / Urologist",
        "description": "Hard deposits made of minerals and salts that form inside your kidneys and cause intense, sharp flank pain as they pass through.",
        "precautions": [
            "Drink 2 to 3 liters of water per day to assist stone passage.",
            "Take prescribed pain medication as directed by your doctor.",
            "Strain urine if requested by your doctor to catch and analyze the stone.",
            "Consult a urologist for ultrasound or CT imaging."
        ],
        "red_flags": "Inability to pass urine, unbearable flank pain, fever, or persistent vomiting."
    },
    "Dengue Fever": {
        "severity": "High / Hospital Care",
        "specialist": "Infectious Disease / Internal Medicine",
        "description": "A mosquito-borne viral infection causing sudden high fever, severe headache, retro-orbital eye pain, and excruciating joint/bone aches.",
        "precautions": [
            "Monitor platelet counts daily under medical supervision.",
            "Strictly avoid Aspirin or Ibuprofen as they heighten internal bleeding risks (use Paracetamol only).",
            "Maintain vigorous hydration with fluids, coconut water, and electrolytes.",
            "Use mosquito nets and repellents to prevent transmission."
        ],
        "red_flags": "Severe belly pain, bleeding from gums/nose, persistent vomiting, or rapid drop in platelets."
    },
    "Malaria": {
        "severity": "High / Urgent",
        "specialist": "Infectious Disease Specialist",
        "description": "A life-threatening disease caused by Plasmodium parasites transmitted to people through the bites of infected female Anopheles mosquitoes.",
        "precautions": [
            "Seek emergency blood smear / rapid antigen test for malaria confirmation.",
            "Begin anti-malarial medication immediately under doctor's guidance.",
            "Keep hydrated and take fever medication as recommended.",
            "Sleep under insecticide-treated bed nets."
        ],
        "red_flags": "Extreme lethargy, confusion, seizures, jaundice, or dark tea-colored urine."
    },
    "Typhoid Fever": {
        "severity": "High",
        "specialist": "Infectious Disease / General Physician",
        "description": "A bacterial infection caused by Salmonella typhi, presenting with step-ladder fever, extreme weakness, stomach pain, and headache.",
        "precautions": [
            "Consult a physician for blood culture and Widal testing.",
            "Complete the entire course of prescribed antibiotics.",
            "Drink only boiled or bottled water and eat freshly cooked, piping hot food.",
            "Wash hands rigorously before eating."
        ],
        "red_flags": "Severe abdominal swelling, confusion, delirium, or bloody stools."
    },
    "Chickenpox": {
        "severity": "Moderate",
        "specialist": "Dermatologist / Pediatrician",
        "description": "A highly contagious viral infection caused by the varicella-zoster virus, causing an itchy rash with fluid-filled blisters.",
        "precautions": [
            "Isolate at home until all blisters have completely scabbed over.",
            "Apply calamine lotion to soothe itching without scratching.",
            "Keep fingernails short and clean to prevent secondary bacterial infection.",
            "Take cool or lukewarm baths with baking soda or oatmeal."
        ],
        "red_flags": "Skin blisters become infected (warm, red, pus), or breathing issues occur."
    },
    "Measles": {
        "severity": "High",
        "specialist": "Pediatrician / Infectious Disease",
        "description": "A highly contagious viral illness characterized by high fever, cough, runny nose, inflamed red eyes, and a widespread maculopapular rash.",
        "precautions": [
            "Isolate completely and notify local public health / clinic before visiting.",
            "Rest in a dimly lit room to protect eyes from light sensitivity.",
            "Maintain strong hydration with cool fluids.",
            "Administer Vitamin A supplements if prescribed by a doctor."
        ],
        "red_flags": "Shortness of breath, ear pain, extreme drowsiness, or convulsions."
    },
    "Viral Hepatitis": {
        "severity": "Moderate to High",
        "specialist": "Hepatologist / Gastroenterologist",
        "description": "An infection causing liver inflammation and damage, manifesting with jaundice, fatigue, nausea, and right upper quadrant discomfort.",
        "precautions": [
            "Consult a liver specialist for hepatic panel and viral serology.",
            "Abstain completely from all alcohol and non-essential hepatotoxic drugs.",
            "Eat a nutritious, low-fat, high-carbohydrate diet in small portions.",
            "Rest adequately and avoid strenuous physical exertion."
        ],
        "red_flags": "Yellowing of skin/eyes (jaundice), severe confusion (encephalopathy), or dark brown urine."
    },
    "Hypertension": {
        "severity": "Moderate Chronic",
        "specialist": "Cardiologist / General Physician",
        "description": "High blood pressure, where long-term force of blood against your artery walls can eventually cause health problems like heart disease.",
        "precautions": [
            "Monitor blood pressure readings daily at the same time.",
            "Reduce dietary sodium intake (< 2g/day) and follow the DASH diet.",
            "Engage in 30 minutes of moderate aerobic exercise most days.",
            "Never stop prescribed antihypertensive medications abruptly without doctor advice."
        ],
        "red_flags": "Blood pressure exceeding 180/120 mmHg, sudden chest pain, numbness, or vision loss."
    },
    "Type 2 Diabetes": {
        "severity": "Moderate Chronic",
        "specialist": "Endocrinologist / Diabetologist",
        "description": "A chronic metabolic condition characterized by high levels of glucose in the blood due to insulin resistance.",
        "precautions": [
            "Monitor fasting and post-prandial blood sugar levels routinely.",
            "Follow a balanced meal plan low in refined sugars and high in dietary fiber.",
            "Take prescribed oral hypoglycemics or insulin on schedule.",
            "Inspect feet daily for cuts, blisters, or signs of poor circulation."
        ],
        "red_flags": "Extreme confusion, fruity-smelling breath, vomiting, or blood sugar > 300 mg/dL."
    },
    "Iron Deficiency Anemia": {
        "severity": "Mild to Moderate",
        "specialist": "Hematologist / General Physician",
        "description": "A condition in which blood lacks adequate healthy red blood cells, causing pale skin, dizziness, fatigue, and breathlessness.",
        "precautions": [
            "Undergo a complete blood count (CBC) and serum ferritin test.",
            "Eat iron-rich foods: leafy greens, beans, lentils, lean meats, fortified cereals.",
            "Pair iron sources with Vitamin C (oranges, lemons) to boost absorption.",
            "Take iron supplements with meals if prescribed by your doctor."
        ],
        "red_flags": "Fainting episodes, rapid irregular heartbeat, or severe shortness of breath at rest."
    },
    "Tonsillitis": {
        "severity": "Mild to Moderate",
        "specialist": "ENT Specialist",
        "description": "Inflammation of the tonsils, two oval-shaped pads of tissue at the back of the throat, causing painful swallowing and fever.",
        "precautions": [
            "Gargle frequently with warm salt water (1/2 tsp salt in 1 cup warm water).",
            "Drink plenty of soothing warm liquids or suck on ice chips.",
            "Rest your voice and avoid throat-irritating environments.",
            "Consult an ENT specialist to determine whether the cause is viral or bacterial."
        ],
        "red_flags": "Difficulty opening mouth (trismus), drooling, or labored breathing."
    },
    "Conjunctivitis": {
        "severity": "Mild",
        "specialist": "Ophthalmologist",
        "description": "Pink eye: an inflammation or infection of the transparent membrane that lines your eyelid and covers the white part of your eyeball.",
        "precautions": [
            "Do not rub or touch your eyes.",
            "Wash hands frequently and avoid sharing towels or pillowcases.",
            "Discontinue contact lens use until infection is completely cleared.",
            "Apply cool or warm moist compresses to eyes for symptom relief."
        ],
        "red_flags": "Severe eye pain, intense light sensitivity, or sudden changes in vision."
    },
    "Eczema (Dermatitis)": {
        "severity": "Mild Chronic",
        "specialist": "Dermatologist",
        "description": "A condition that makes your skin red and itchy, common in children but can occur at any age; chronic and prone to periodic flares.",
        "precautions": [
            "Moisturize skin at least twice a day using thick fragrance-free creams or ointments.",
            "Take short lukewarm baths/showers and gently pat dry without vigorous rubbing.",
            "Wear soft, breathable cotton clothing and avoid scratchy wool materials.",
            "Use mild, soap-free cleansers and avoid harsh detergents."
        ],
        "red_flags": "Skin oozes yellow pus or is surrounded by red, hot, spreading streaks."
    },
    "Rheumatoid Arthritis": {
        "severity": "Moderate Chronic",
        "specialist": "Rheumatologist",
        "description": "A chronic autoimmune inflammatory disorder that can affect joints in hands and feet, causing painful swelling and bone erosion.",
        "precautions": [
            "Consult a rheumatologist early for disease-modifying antirheumatic drugs (DMARDs).",
            "Perform gentle low-impact exercises like swimming or walking to maintain mobility.",
            "Apply warm compresses before movement to ease morning joint stiffness.",
            "Balance physical activity with regular rest periods."
        ],
        "red_flags": "Sudden inability to bear weight, red hot swollen joint with high fever."
    }
}

# Default fallback metadata for any condition
DEFAULT_METADATA = {
    "severity": "Moderate",
    "specialist": "General Physician",
    "description": "A health condition requiring clinical assessment.",
    "precautions": [
        "Consult a qualified healthcare provider for proper clinical diagnosis.",
        "Get adequate rest and stay well hydrated.",
        "Monitor your vital signs and record symptom duration."
    ],
    "red_flags": "High fever, difficulty breathing, or severe pain."
}

def get_disease_details(disease_name: str) -> dict:
    """Retrieve metadata, severity, and precautions for a given disease name."""
    return DISEASE_METADATA.get(disease_name, DEFAULT_METADATA)

# NLP Natural Language Symptom Detection dictionary
NLP_SYMPTOM_PATTERNS = {
    "fever": [r"\bfever\b", r"\btemperature\b", r"\bpyrexia\b", r"\bhot body\b", r"\brunning hot\b", r"\bfeverish\b"],
    "high_fever": [r"\bhigh fever\b", r"\bspiking fever\b", r"\bvery hot\b", r"\b10[2-5](\.[0-9])?\s*(f|deg)?\b"],
    "chills": [r"\bchill[s]?\b", r"\bshivering\b", r"\bshiver[s]?\b", r"\bteeth chattering\b", r"\bfeeling cold\b"],
    "fatigue": [r"\bfatigue[d]?\b", r"\btired(ness)?\b", r"\bexhaust(ed|ion)\b", r"\bweak(ness)?\b", r"\bletharg(y|ic)\b", r"\bno energy\b"],
    "cough": [r"\bcough(ing)?\b", r"\bhacking\b"],
    "dry_cough": [r"\bdry cough\b", r"\btickly cough\b", r"\bnon[- ]productive cough\b"],
    "productive_cough": [r"\bproductive cough\b", r"\bwet cough\b", r"\bcoughing up phlegm\b", r"\bmucus cough\b"],
    "difficulty_breathing": [r"\bdifficult(y)? (in )?breath(ing)?\b", r"\bhard to breathe\b", r"\bbreathless(ness)?\b", r"\bstruggling to breathe\b"],
    "shortness_of_breath": [r"\bshort(ness)? of breath\b", r"\bsob\b", r"\bout of breath\b", r"\bpanting\b", r"\bwinded\b"],
    "chest_pain": [r"\bchest pain\b", r"\bchest tightness\b", r"\bpain in (the )?chest\b", r"\bchest discomfort\b"],
    "sore_throat": [r"\bsore throat\b", r"\bthroat pain\b", r"\bscratchy throat\b", r"\bpain(ful)? swallow(ing)?\b", r"\bpharyngitis\b"],
    "runny_nose": [r"\brunny nose\b", r"\brhinorrhea\b", r"\bdripping nose\b", r"\bwatery nose\b"],
    "nasal_congestion": [r"\bcongest(ed|ion)\b", r"\bblocked nose\b", r"\bstuffy nose\b", r"\bsinus clog\b"],
    "sneezing": [r"\bsneez(e|ing|es)\b"],
    "headache": [r"\bheadache[s]?\b", r"\bhead ache[s]?\b", r"\bhead hurting\b", r"\bpain in head\b", r"\bhead pain\b"],
    "dizziness": [r"\bdizz(y|iness)\b", r"\blightheaded(ness)?\b", r"\bwoozy\b", r"\bunsteady\b", r"\bspinning\b", r"\bvertigo\b"],
    "stiff_neck": [r"\bstiff neck\b", r"\bneck stiffness\b", r"\bcan(')?t bend neck\b", r"\bpainful neck\b"],
    "light_sensitivity": [r"\blight sensitiv(e|ity)\b", r"\bphotophobia\b", r"\bhurt(s)? to look at light\b"],
    "nausea": [r"\bnausea\b", r"\bfeeling sick\b", r"\bqueasy\b", r"\bnauseous\b", r"\bupset stomach\b"],
    "vomiting": [r"\bvomit(ing)?\b", r"\bthrowing up\b", r"\bpuk(e|ing)\b", r"\bbarf(ing)?\b"],
    "diarrhea": [r"\bdiarrhea\b", r"\bloose motion[s]?\b", r"\bruns\b", r"\bwatery stool[s]?\b"],
    "abdominal_pain": [r"\babdominal pain\b", r"\bstomach ache\b", r"\bbelly pain\b", r"\bgut pain\b", r"\bpain in stomach\b"],
    "stomach_cramps": [r"\bstomach cramp[s]?\b", r"\babdominal cramp[s]?\b", r"\bcramping\b"],
    "loss_of_appetite": [r"\bloss of appetite\b", r"\bnot hungry\b", r"\bdon(')?t feel like eating\b", r"\bpoor appetite\b"],
    "acidity_heartburn": [r"\bacidity\b", r"\bheartburn\b", r"\bacid reflux\b", r"\bgerd\b", r"\bburning chest\b", r"\bsour burps\b"],
    "body_aches": [r"\bbody ache[s]?\b", r"\baching all over\b", r"\bgeneral body pain\b"],
    "muscle_pain": [r"\bmuscle pain\b", r"\bmyalgia\b", r"\bsore muscle[s]?\b", r"\bmuscle ache[s]?\b"],
    "joint_pain": [r"\bjoint pain\b", r"\barthralgia\b", r"\bachy joint[s]?\b", r"\bswollen joint[s]?\b", r"\bknee pain\b"],
    "skin_rash": [r"\brash\b", r"\bskin rash\b", r"\bred spots\b", r"\bhives\b", r"\beruption\b", r"\bwelts\b"],
    "itching": [r"\bitch(y|ing)?\b", r"\bpruritus\b", r"\bscratch(ing)?\b"],
    "watery_eyes": [r"\bwatery eye[s]?\b", r"\btearing eye[s]?\b", r"\bred eye[s]?\b", r"\bitchy eye[s]?\b"],
    "loss_of_smell": [
        r"\bloss of smell\b",
        r"\blost (my |the )?(sense of )?smell\b",
        r"\bcan(')?t smell\b",
        r"\bcannot smell\b",
        r"\banosmia\b",
        r"\bno smell\b"
    ],
    "loss_of_taste": [
        r"\bloss of taste\b",
        r"\blost (my |the )?(sense of )?taste\b",
        r"\bcan(')?t taste\b",
        r"\bcannot taste\b",
        r"\bageusia\b",
        r"\bno taste\b"
    ],
    "burning_urination": [r"\bburning (when |during )?urinat(e|ion|ing)\b", r"\bdysuria\b", r"\bpain (when |during )?peeing\b", r"\bstinging pee\b"],
    "frequent_urination": [r"\bfrequent urinat(ion|ing)\b", r"\bpeeing a lot\b", r"\burinating often\b", r"\bconstant urge to pee\b"]
}

def extract_symptoms_from_text(text: str) -> list[str]:
    """Parse a free-form patient prompt and detect standard symptom keys."""
    if not text:
        return []
    clean_text = text.lower()
    found = []
    for symptom_key, patterns in NLP_SYMPTOM_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, clean_text):
                found.append(symptom_key)
                break
    return found
