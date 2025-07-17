import re
from transformers import pipeline

# Load transformers pipelines
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)
bert_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

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
    info["email"] = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.\w+", text)
    info["phone"] = re.findall(r"\+?\d[\d\s\-()]{8,15}", text)

    # NER for name
    name = "Not Found"
    for ent in ner_pipeline(text[:1000]):
        if ent["entity_group"] == "PER":
            name = ent["word"].replace("##", "")
            break
    info["name"] = name

    skills_list = [
        "python", "java", "c++", "html", "css", "javascript", "react",
        "node", "django", "flask", "sql", "mongodb", "nlp", "machine learning"
    ]
    info["skills"] = [s for s in skills_list if s in text.lower()]

    edu_keywords = ["b.tech", "m.tech", "bachelor", "master", "degree", "graduation", "university", "college"]
    info["education"] = "Yes" if any(k in text.lower() for k in edu_keywords) else "Not Found"
    return info

def generate_feedback(text, info):
    feedback = []
    if "github" not in text.lower() and "portfolio" not in text.lower():
        feedback.append("🔗 Consider adding a GitHub or personal portfolio link.")

    if len(text.split()) < 150:
        feedback.append(f"📄 Resume has only {len(text.split())} words. Aim for 250–500 words.")

    if info.get("education") == "Not Found":
        feedback.append("🎓 Education section is missing.")

    if len(info.get("skills", [])) < 3:
        feedback.append("🛠️ Too few technical skills listed.")

    if info.get("name") == "Not Found":
        feedback.append("🧾 Name not confidently detected.")

    # Role classification
    try:
        labels = ["Software Engineer", "Data Scientist", "Web Developer"]
        result = bert_classifier(text, labels)
        if result and result.get("labels"):
            best_fit = result["labels"][0]
            confidence = round(result["scores"][0] * 100, 1)
            feedback.append(f"✅ Resume aligns best with **{best_fit}** ({confidence}% confidence).")
    except Exception:
        feedback.append("⚠️ Role classification failed.")

    return feedback

def analyze_resume(text):
    info = extract_info(text)
    feedback = generate_feedback(text, info)

    score = 100
    deductions = 0
    issues = []

    if "🔗" in "".join(feedback):
        deductions += 15
        issues.append({
            "title": "Portfolio or GitHub Link Missing",
            "type": "critical",
            "description": "Add a GitHub or portfolio link to highlight your projects."
        })

    if "📄" in "".join(feedback):
        deductions += 10
        issues.append({
            "title": "Resume Too Short",
            "type": "moderate",
            "description": "Your resume should be between 250–500 words."
        })

    if "🎓" in "".join(feedback):
        deductions += 15
        issues.append({
            "title": "Education Section Missing",
            "type": "critical",
            "description": "List your degree, university, and graduation year."
        })

    if "🛠️" in "".join(feedback):
        deductions += 10
        issues.append({
            "title": "Lacks Technical Skills",
            "type": "moderate",
            "description": "Add more relevant tools, frameworks, or technologies."
        })

    if "🧾" in "".join(feedback):
        deductions += 5
        issues.append({
            "title": "Name Not Detected",
            "type": "low",
            "description": "Ensure your name is clearly placed at the top of the resume."
        })

    # Classification
    alignment = next((f for f in feedback if f.startswith("✅")), "No clear classification found.")

    score -= deductions
    score = max(0, score)

    return {
        "info": info,
        "feedback": feedback,
        "score": score,
        "alignment": alignment,
        "issues": issues
    }
