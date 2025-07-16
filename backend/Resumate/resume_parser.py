# resume_parser.py

import re
from transformers import pipeline

from transformers import pipeline

bert_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


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

    try:
        # GitHub / Portfolio Check
        if "github" not in text.lower() and "portfolio" not in text.lower():
            feedback.append(
                "🔗 Consider adding a GitHub or personal portfolio link to showcase your projects and technical skills. Recruiters value real-world proof of your work."
            )

        # Word Count Check
        word_count = len(text.split())
        if word_count < 150:
            feedback.append(
                f"📄 Your resume has only {word_count} words. It feels too brief. Aim for 250–500 words to describe your roles, achievements, skills, and projects more thoroughly."
            )

        # Education Check
        if info.get("education") == "Not Found":
            feedback.append(
                "🎓 Your resume lacks a clear education section. Include your degrees, institutions, and graduation years. Education often forms a baseline filter for recruiters."
            )

        # Skill Depth Check
        if len(info.get("skills", [])) < 3:
            feedback.append(
                "🛠️ You’ve listed very few technical skills. Consider adding tools, languages, frameworks, or certifications that match your target job role."
            )

        # Name Check
        if info.get("name") == "Not Found":
            feedback.append(
                "🧾 Your name couldn't be confidently detected. Ensure it's prominently placed at the top, ideally in bold or large font. It's the first thing recruiters look for."
            )

        # Classification using BERT
        labels = ["Software Engineer", "Data Scientist", "Web Developer"]
        bert_result = bert_classifier(text, labels)

        if bert_result.get("labels"):
            best_fit = bert_result["labels"][0]
            confidence = round(bert_result["scores"][0] * 100, 1)
            feedback.append(
                f"✅ Based on your content, your resume aligns best with a **{best_fit}** role ({confidence}% confidence). Tailor your resume toward this path if applicable."
            )

    except Exception as e:
        print("❌ Feedback generation error:", str(e))
        feedback.append("⚠️ Feedback generation failed. Try again or check the input.")

    return feedback

