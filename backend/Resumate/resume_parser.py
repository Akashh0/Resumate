import re
from transformers import pipeline

# ✅ HuggingFace Pipelines (faster model)
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)
bert_classifier = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")

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

# ✅ Extract key info
def extract_info(text):
    info = {}
    info["email"] = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.\w+", text)
    info["phone"] = re.findall(r"\+?\d[\d\s\-()]{8,15}", text)

    # Extract name using NER
    name = "Not Found"
    entities = ner_pipeline(text[:1000])  # Limit to beginning for performance
    for ent in entities:
        if ent["entity_group"] == "PER":
            name = ent["word"].replace("##", "")
            break
    info["name"] = name

    # Skills (Basic keyword match)
    skill_set = [
        "python", "java", "c++", "html", "css", "javascript", "react",
        "node", "django", "flask", "sql", "mongodb", "nlp", "machine learning"
    ]
    info["skills"] = [skill for skill in skill_set if skill in text.lower()]

    # Education detection
    edu_keywords = ["b.tech", "m.tech", "bachelor", "master", "degree", "graduation", "university", "college"]
    info["education"] = "Yes" if any(k in text.lower() for k in edu_keywords) else "Not Found"

    return info

# ✅ Feedback Generator
def generate_feedback(text, info):
    score = 100
    issues = []
    positives = []
    suggestions = []
    feedback = []
    alignment = "Alignment not available."

    # --- GitHub/Portfolio Link ---
    if "github" not in text.lower() and "portfolio" not in text.lower():
        score -= 15
        issues.append({
            "type": "critical",
            "title": "Missing GitHub/Portfolio",
            "description": "Include links to your GitHub or personal portfolio."
        })
        suggestions.append("Add GitHub or portfolio link to showcase your work.")
    else:
        positives.append("GitHub/Portfolio link included")

    # --- Word Count ---
    word_count = len(text.split())
    if word_count < 150:
        score -= 10
        issues.append({
            "type": "moderate",
            "title": "Resume too short",
            "description": f"Your resume has {word_count} words. Consider elaborating your experience."
        })
        suggestions.append("Expand your resume to at least 250–400 words for depth.")
    else:
        positives.append("Sufficient word count")

    # --- Education ---
    if info.get("education") == "Not Found":
        score -= 15
        issues.append({
            "type": "critical",
            "title": "Education section missing",
            "description": "Mention your degree, university, and graduation year."
        })
        suggestions.append("Add your education details to reflect qualifications.")
    else:
        positives.append("Education section present")

    # --- Skills ---
    if len(info.get("skills", [])) < 3:
        score -= 10
        issues.append({
            "type": "moderate",
            "title": "Too few skills",
            "description": "List relevant skills, tools, or frameworks."
        })
        suggestions.append("Add more relevant skills (languages, frameworks, tools).")
    else:
        positives.append("Skills listed adequately")

    # --- Name ---
    if info.get("name") == "Not Found":
        score -= 10
        issues.append({
            "type": "moderate",
            "title": "Name not detected",
            "description": "Ensure your name is clearly written at the top."
        })
        suggestions.append("Write your full name prominently at the top.")
    else:
        positives.append("Name clearly found")

    # --- Role Alignment (Optimized) ---
    try:
        labels = ["Software Engineer", "Data Scientist", "Web Developer", "AI Engineer"]
        short_text = ' '.join(text.split()[:500])  # Truncate for faster response
        result = bert_classifier(short_text, labels)

        if result and result.get("labels"):
            best_fit = result["labels"][0]
            confidence = round(result["scores"][0] * 100, 1)
            alignment = f"{best_fit} ({confidence}% match)"
    except Exception as e:
        print("Alignment check failed:", e)
        alignment = "Alignment check failed."

    # --- Final Review ---
    if score >= 85:
        feedback.append("🌟 Excellent resume! You're doing great. Just minor polish needed.")
    elif score >= 65:
        feedback.append("👍 Good effort! Address the listed issues to make it even better.")
    else:
        feedback.append("⚠️ Needs improvement. Consider reworking the sections mentioned.")

    return {
        "score": max(score, 0),
        "alignment": alignment,
        "feedback": feedback,
        "issues": issues,
        "positives": positives,
        "suggestions": suggestions
    }
