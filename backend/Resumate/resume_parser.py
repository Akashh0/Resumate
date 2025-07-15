# Resumate/resume_parser.py

import pdfplumber
import docx2txt
import re
import spacy
from transformers import pipeline

nlp = spacy.load("en_core_web_sm")
bert_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def extract_resume_text(path):
    if path.endswith('.pdf'):
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif path.endswith('.docx'):
        return docx2txt.process(path)
    return ""

def extract_info(text):
    info = {}

    info["email"] = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.\w+", text)
    info["phone"] = re.findall(r"\+?\d[\d\s\-()]{8,15}", text)

    # 🔍 Name Extraction - Improved
    lines = text.strip().split("\n")
    top_block = "\n".join(lines[:15])  # Focus on top of resume

    doc = nlp(top_block)
    person_names = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]

    # Check if any look like valid name (not location or numeric)
    filtered_names = [name for name in person_names if len(name.split()) >= 2 and not any(char.isdigit() for char in name)]

    # 🌟 Final fallback: All-uppercase line with 2+ words, from top few lines
    fallback_upper = next((line.strip() for line in lines[:10]
                          if line.strip().isupper() and len(line.split()) >= 2), None)

    info["name"] = filtered_names[0] if filtered_names else (fallback_upper or "Not Found")

    # 🛠 Skill Matching
    skills_list = ["python", "django", "react", "sql", "ml", "nlp", "html", "css", "javascript", "git"]
    info["skills"] = [skill for skill in skills_list if skill in text.lower()]

    # 🎓 Education Check
    edu_keywords = ["b.tech", "m.tech", "bachelor", "master", "degree", "graduation", "university", "10th", "12th"]
    info["education"] = "Yes" if any(word in text.lower() for word in edu_keywords) else "Not Found"

    return info



def generate_feedback(text, info):
    feedback = []

    try:
        if "github" not in text.lower() and "portfolio" not in text.lower():
            feedback.append("Consider adding a GitHub or Portfolio link.")

        if len(text.split()) < 150:
            feedback.append("Resume seems short. Try elaborating your experience or skills.")

        if info.get("education") == "Not Found":
            feedback.append("Education section is missing or unclear.")

        print("DEBUG: Running BERT classification...")
        labels = ["Software Engineer", "Data Scientist", "Web Developer"]
        bert_result = bert_classifier(text, labels)
        print("DEBUG: BERT Result", bert_result)

        if bert_result.get("labels"):
            feedback.append(f"Resume aligns best with: {bert_result['labels'][0]}")

    except Exception as e:
        print("❌ Feedback generation error:", str(e))
        feedback.append("Feedback generation failed.")

    return feedback

