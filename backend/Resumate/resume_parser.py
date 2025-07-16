# resume_parser.py

import re
from transformers import pipeline

# Named Entity Recognition (NER) pipeline for extracting name
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)

# Zero-shot classification for predicting resume type
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def extract_resume_text(path):
    import pdfplumber
    import docx2txt

    if path.endswith('.pdf'):
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif path.endswith('.docx'):
        return docx2txt.process(path)
    return ""

def extract_info(text):
    info = {}

    # Extract email
    info["email"] = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.\w+", text)

    # Extract phone numbers
    info["phone"] = re.findall(r"\+?\d[\d\s\-()]{8,15}", text)

    # Extract name using BERT NER
    name = "Not Found"
    entities = ner_pipeline(text[:1000])  # limit input for speed
    for ent in entities:
        if ent["entity_group"] == "PER":
            name = ent["word"].replace("##", "")
            break
    info["name"] = name

    # Extract skills from known list
    skills_list = [
        "python", "java", "c++", "html", "css", "javascript", "react",
        "node", "django", "flask", "sql", "mongodb", "nlp", "machine learning"
    ]
    info["skills"] = [skill for skill in skills_list if skill in text.lower()]

    # Check if education keywords exist
    edu_keywords = ["b.tech", "m.tech", "bachelor", "master", "degree", "graduation", "university", "college"]
    info["education"] = "Yes" if any(word in text.lower() for word in edu_keywords) else "Not Found"

    return info

def generate_feedback(text, info):
    feedback = []

    if not any(x in text.lower() for x in ["github", "portfolio", "linkedin"]):
        feedback.append("Consider adding a GitHub, Portfolio or LinkedIn link.")

    if len(text.split()) < 150:
        feedback.append("Your resume is quite short — add more content.")

    if info.get("education") == "Not Found":
        feedback.append("Education section is missing or unclear.")

    # Predict job alignment using BERT
    labels = ["Software Engineer", "Data Scientist", "Web Developer", "UI/UX Designer"]
    result = classifier(text[:1024], labels)

    if result.get("labels"):
        feedback.append(f"Resume aligns best with: {result['labels'][0]}")

    return feedback
