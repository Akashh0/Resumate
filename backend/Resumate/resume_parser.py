# resume_parser.py

import re
from transformers import pipeline

# ✅ Required Pipelines
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)
bert_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# ✅ Extract text from resume
def extract_resume_text(path):
    import pdfplumber
    import docx2txt

    if path.endswith(".pdf"):
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif path.endswith(".docx"):
        return docx2txt.process(path)
    return ""

# ✅ Extract info

def extract_info(text):
    info = {}
    info["email"] = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.\w+", text)
    info["phone"] = re.findall(r"\+?\d[\d\s\-()]{8,15}", text)

    # Extract name
    name = "Not Found"
    entities = ner_pipeline(text[:1000])
    for ent in entities:
        if ent["entity_group"] == "PER":
            name = ent["word"].replace("##", "")
            break
    info["name"] = name

    # Skill Extraction
    skill_set = [
        "python", "java", "c++", "html", "css", "javascript", "react",
        "node", "django", "flask", "sql", "mongodb", "nlp", "machine learning"
    ]
    info["skills"] = [skill for skill in skill_set if skill in text.lower()]

    # Education
    edu_keywords = ["b.tech", "m.tech", "bachelor", "master", "degree", "graduation", "university", "college"]
    info["education"] = "Yes" if any(k in text.lower() for k in edu_keywords) else "Not Found"

    return info

# ✅ Generate score, feedback, and review

def generate_feedback(text, info):
    score = 100
    issues = []
    positives = []
    feedback = []

    # 1. GitHub/Portfolio
    if "github" not in text.lower() and "portfolio" not in text.lower():
        score -= 15
        issues.append({
            "type": "critical",
            "title": "Missing GitHub/Portfolio",
            "description": "Include links to your GitHub or personal portfolio. They validate your skills."
        })
    else:
        positives.append("GitHub/Portfolio link included")

    # 2. Word count
    word_count = len(text.split())
    if word_count < 150:
        score -= 10
        issues.append({
            "type": "moderate",
            "title": "Resume too short",
            "description": f"Your resume has {word_count} words. Consider elaborating your experience."
        })
    else:
        positives.append("Sufficient word count")

    # 3. Education
    if info.get("education") == "Not Found":
        score -= 15
        issues.append({
            "type": "critical",
            "title": "Education section missing",
            "description": "Mention your degree, university, and graduation year."
        })
    else:
        positives.append("Education section present")

    # 4. Skills
    if len(info.get("skills", [])) < 3:
        score -= 10
        issues.append({
            "type": "moderate",
            "title": "Too few skills",
            "description": "List relevant skills, tools, or frameworks."
        })
    else:
        positives.append("Skills listed adequately")

    # 5. Name
    if info.get("name") == "Not Found":
        score -= 10
        issues.append({
            "type": "moderate",
            "title": "Name not detected",
            "description": "Ensure your name is clearly written at the top."
        })
    else:
        positives.append("Name clearly found")

    # 6. Role Alignment
    labels = ["Software Engineer", "Data Scientist", "Web Developer"]
    alignment = ""
    try:
        labels = ["Software Engineer", "Data Scientist", "Web Developer"]
        result = bert_classifier(text, labels)
        
        if result and result.get("labels"):
            best_fit = result["labels"][0]
            confidence = round(result["scores"][0] * 100, 1)
            alignment = f"{best_fit} ({confidence}% match)"
        else:
            alignment = "Could not determine a best-fit role."
    except Exception as e:
            alignment = "Alignment check failed."


    # Review Summary
    if score >= 85:
        review = "🌟 Excellent resume! You're doing great. Just minor polish needed."
    elif score >= 65:
        review = "👍 Good effort! Address the listed issues to make it even better."
    else:
        review = "⚠️ Needs improvement. Consider reworking the sections mentioned."

    feedback.append(review)

    return {
        "score": max(score, 0),
        "alignment": alignment,
        "feedback": feedback,
        "issues": issues,
        "positives": positives,
    }
