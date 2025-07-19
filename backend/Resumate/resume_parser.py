import os
import re
import requests
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))
HUGGINGFACE_API_KEY = os.getenv("HF_API_TOKEN")

if not HUGGINGFACE_API_KEY:
    raise ValueError("❌ Hugging Face API key not found in .env file")

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
}

def extract_resume_text(path):
    import pdfplumber
    import docx2txt

    if path.endswith(".pdf"):
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif path.endswith(".docx"):
        return docx2txt.process(path)
    return ""

def call_huggingface_model(model, inputs, parameters=None):
    url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {"inputs": inputs}
    if parameters:
        payload["parameters"] = parameters
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def extract_info(text):
    info = {}

    # Contact info
    info["email"] = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.\w+", text)
    info["phone"] = re.findall(r"\+?\d[\d\s\-()]{8,15}", text)
    info["word_count"] = len(text.split())

    # ---------------------- NAME EXTRACTION ----------------------
    name = "Not Found"
    try:
        ner_results = call_huggingface_model("dslim/bert-base-NER", text[:512])
        name_tokens = []
        for ent in ner_results:
            if ent["entity_group"] == "PER":
                word = ent["word"]
                if word.startswith("##") and name_tokens:
                    name_tokens[-1] += word[2:]
                else:
                    name_tokens.append(word)
        if name_tokens:
            name = " ".join(name_tokens).strip()
        else:
            # Fallback: Look at first 5 lines for ALL-CAPS name
            for line in text.split("\n")[:5]:
                if line.strip().isupper() and 2 <= len(line.split()) <= 5:
                    name = line.strip().title()
                    break
    except Exception:
        name = "Not Found"
    info["name"] = name
    

    # ---------------------- SKILLS EXTRACTION ----------------------
    skill_set = ["python", "java", "c++", "html", "css", "javascript", "react", "node", "django", "flask", "sql", "mongodb", "nlp", "machine learning"]
    text_lower = text.lower()
    info["skills"] = [skill for skill in skill_set if skill in text_lower]

    # ---------------------- OTHER SECTIONS ----------------------
    edu_keywords = ["b.tech", "m.tech", "bachelor", "master", "degree", "graduation", "university", "college"]
    info["education"] = "Yes" if any(k in text_lower for k in edu_keywords) else "Not Found"

    info["github"] = any(k in text_lower for k in ["github.com", "portfolio"])
    info["has_projects"] = any(k in text_lower for k in ["project", "built", "developed"])

    info["languages"] = re.findall(r"\b(?:english|hindi|french|german|spanish)\b", text_lower)
    info["certifications"] = "Yes" if any("certificat" in line.lower() for line in text.split("\n")) else "No"
    info["achievements"] = "Yes" if any("award" in line.lower() or "achievement" in line.lower() for line in text.split("\n")) else "No"
    info["experience"] = next((line for line in text_lower.split("\n") if "experience" in line), "Not Found")
    info["linkedin"] = any("linkedin.com" in line.lower() for line in text.split("\n"))

    return info

def generate_feedback(text, info):
    score = 100
    issues, positives, suggestions = [], [], []
    feedback = []
    alignment = "Alignment not available."

    # Role Alignment using NLI
    try:
        result = call_huggingface_model("facebook/bart-large-mnli", text[:512], parameters={
            "candidate_labels": ["Software Engineer", "Data Scientist", "Web Developer", "AI Engineer"]
        })
        best_fit = result["labels"][0]
        confidence = round(result["scores"][0] * 100, 1)
        alignment = f"{best_fit} ({confidence}% match)"
    except Exception:
        alignment = "Alignment check failed."

    # Checks
    if not info.get("github"):
        score -= 15
        issues.append({"type": "critical", "title": "Missing GitHub/Portfolio", "description": "Include links to your GitHub or personal portfolio."})
        suggestions.append("Add GitHub or portfolio link.")
    else:
        positives.append("GitHub/Portfolio link included")

    if info["word_count"] < 150:
        score -= 10
        issues.append({"type": "moderate", "title": "Resume too short", "description": f"Only {info['word_count']} words."})
        suggestions.append("Expand to 250–400 words.")
    else:
        positives.append("Sufficient word count")

    if info["education"] == "Not Found":
        score -= 15
        issues.append({"type": "critical", "title": "Education section missing", "description": "Mention your degree and university."})
        suggestions.append("Add education section.")
    else:
        positives.append("Education section present")

    if len(info.get("skills", [])) < 3:
        score -= 10
        issues.append({"type": "moderate", "title": "Too few skills", "description": "Add more technical skills."})
        suggestions.append("List at least 5–10 skills.")
    else:
        positives.append("Skills listed adequately")

    if info["name"] == "Not Found":
        score -= 10
        issues.append({"type": "moderate", "title": "Name not detected", "description": "Ensure your name is visible at the top."})
        suggestions.append("Put your full name prominently.")
    else:
        positives.append("Name clearly found")

    # Final feedback
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
