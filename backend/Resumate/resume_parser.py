import os
import re
import requests
import pdfplumber
import docx2txt
from dotenv import load_dotenv

# Load environment variables from the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

HUGGINGFACE_API_KEY = os.getenv("HF_API_TOKEN")
if not HUGGINGFACE_API_KEY:
    raise ValueError("❌ Hugging Face API key (HF_API_TOKEN) not found in .env file")

headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}


def extract_resume_text(file_path):
    if file_path.lower().endswith(".pdf"):
        try:
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            print(f"Error reading PDF: {e}")
    elif file_path.lower().endswith(".docx"):
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            print(f"Error reading DOCX: {e}")
    return ""


def call_huggingface_model(model_id, inputs, parameters=None):
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    payload = {"inputs": inputs}
    if parameters:
        payload["parameters"] = parameters
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def extract_section(text, section_keywords):
    """
    Extracts a section's content using a robust regex-based approach.
    Returns the content if found, otherwise returns None.
    """
    all_section_starters = [
        "education", "experience", "skills", "projects", "achievements", "awards",
        "certifications", "publications", "summary", "objective", "contact",
        "honors", "professional experience", "work experience", "technical events"
    ]

    # Pattern to find the start of the target section (case-insensitive, whole word)
    start_pattern = r"(?i)\b(" + "|".join(section_keywords) + r")\b"
    match = re.search(start_pattern, text)
    
    if not match:
        return None

    # Find where the actual content starts (after the heading)
    start_index = match.end()
    
    # Find the start of the next possible section to set the boundary
    end_index = len(text)
    
    # Create a pattern for all other section headings
    next_section_keywords = [s for s in all_section_starters if s not in section_keywords]
    next_section_pattern = r"(?i)\b(" + "|".join(next_section_keywords) + r")\b"
    
    # Search for the next heading only in the text *after* our current section's heading
    next_match = re.search(next_section_pattern, text[start_index:])
    if next_match:
        end_index = start_index + next_match.start()

    # Extract and clean the content
    section_text = text[start_index:end_index].strip()
    
    # Remove any leading colons or newlines for cleaner text
    cleaned_text = re.sub(r"^\s*[:\-\s]*\n", "", section_text).strip()
    
    return cleaned_text if cleaned_text else None


def extract_info(text):
    if not text:
        return {}

    info = {}
    text_lower = text.lower()

    # Contact Info
    info["email"] = list(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)))
    info["phone"] = list(set(re.findall(r"(\+?\d[\d\s\-()]{8,15}\d)", text)))
    info["word_count"] = len(text.split())

    # Name Extraction
    name = "Not Found"
    try:
        ner_results = call_huggingface_model(
            "Jean-Baptiste/roberta-large-ner-english",
            text[:512],
            parameters={"aggregation_strategy": "simple"}
        )
        for ent in ner_results:
            if ent["entity_group"] == "PER":
                name = ent["word"].strip().title()
                break
        if name == "Not Found":
            for line in text.split("\n")[:5]:
                if line.strip().isupper() and 2 <= len(line.split()) <= 5:
                    name = line.strip().title()
                    break
    except Exception as e:
        print(f"⚠️ Name extraction failed: {e}")
    info["name"] = name

    # GitHub / LinkedIn
    github_match = re.search(r"github\.com/([\w\-]+)", text_lower)
    info["github"] = f"https://github.com/{github_match.group(1)}" if github_match else "Not Found"

    linkedin_match = re.search(r"linkedin\.com/in/([\w\-]+)", text_lower)
    info["linkedin"] = f"https://linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else "Not Found"

    # Languages (always list)
    langs = re.findall(r"\b(english|hindi|french|german|tamil|telugu|spanish|marathi)\b", text_lower)
    info["languages"] = list(set(langs)) if langs else []

    # Skills
    skill_set = [
        "python", "java", "c++", "c#", "html", "css", "javascript", "typescript", "react", "angular",
        "vue", "node.js", "django", "flask", "fastapi", "sql", "mysql", "postgresql", "mongodb", "nlp",
        "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
        "docker", "kubernetes", "aws", "azure", "gcp", "git"
    ]
    info["skills"] = list(set(skill for skill in skill_set if skill in text_lower))

    # Section Flags
    info["education"] = "Yes" if extract_section(text, ["education", "academic background", "qualifications"]) is not None else "No"
    info["achievements"] = "Yes" if extract_section(text, ["achievements", "awards", "honors"]) is not None else "No"
    info["certifications"] = "Yes" if extract_section(text, ["certifications", "licenses", "certification"]) is not None else "No"
    info["projects"] = "Yes" if extract_section(text, ["projects", "personal projects", "project"]) is not None else "No"

    return info


def generate_feedback(text, info):
    score = 100
    issues = []
    positives = []
    alignment = "Alignment check unavailable."

    # Role alignment
    try:
        result = call_huggingface_model(
            "facebook/bart-large-mnli",
            text[:1024],
            parameters={"candidate_labels": ["Software Engineer", "Data Scientist", "Web Developer", "AI Engineer"]}
        )
        if isinstance(result, dict) and "labels" in result and "scores" in result:
            best_fit = result["labels"][0]
            confidence = round(result["scores"][0] * 100, 1)
            alignment = f"{best_fit} ({confidence}% match)"
            positives.append("Resume shows a clear role alignment.")
        else:
            print(f"⚠️ Unexpected alignment model output: {result}")
    except Exception as e:
        print(f"⚠️ Alignment failed: {e}")

    # Name
    name_found = info.get("name", "Not Found") != "Not Found"
    if not name_found:
        score -= 10
        issues.append({
            "type": "critical",
            "title": "Name Not Detected",
            "description": "Make sure your full name is prominently visible at the top."
        })
    else:
        positives.append("Candidate name is clearly identified.")

    # GitHub
    github_url = info.get("github", "Not Found")
    has_github = "github.com" in github_url
    if not has_github:
        score -= 15
        issues.append({
            "type": "critical",
            "title": "Missing GitHub/Portfolio",
            "description": "Add a GitHub or portfolio link to showcase your work."
        })
    else:
        positives.append("Includes GitHub or portfolio link.")

    # LinkedIn
    linkedin_url = info.get("linkedin", "Not Found")
    has_linkedin = "linkedin.com/in/" in linkedin_url

    # Word count
    wc = info.get("word_count", 0)
    if wc < 250:
        score -= 10
        issues.append({
            "type": "moderate",
            "title": "Resume Too Short",
            "description": f"{wc} words detected. Ideal range is 300–500 words."
        })
    elif wc > 700:
        score -= 10
        issues.append({
            "type": "moderate",
            "title": "Resume Too Long",
            "description": f"{wc} words detected. Try keeping it under one page."
        })
    else:
        positives.append("Resume length is optimal.")

    # Education
    education_found = info.get("education", "No") == "Yes"
    if not education_found:
        score -= 15
        issues.append({
            "type": "critical",
            "title": "Missing Education Section",
            "description": "Include academic background, degree, or university."
        })
    else:
        positives.append("Education section is present.")

    # Skills
    skills = info.get("skills", [])
    if len(skills) < 5:
        score -= 10
        issues.append({
            "type": "moderate",
            "title": "Few Skills Listed",
            "description": "List at least 5–10 relevant technical skills."
        })
    else:
        positives.append("Skills section is well-filled.")

    # Projects
    projects_mentioned = info.get("projects", "No") == "Yes"
    if not projects_mentioned:
        score -= 10
        issues.append({
            "type": "moderate",
            "title": "Projects Not Mentioned",
            "description": "Include a 'Projects' section to demonstrate experience."
        })
    else:
        positives.append("Projects section is included.")

    return {
        "score": max(score, 0),
        "alignment": alignment,
        "issues": issues,
        "positives": positives,
        "feedback": positives,
        "name_found": name_found,
        "education_found": education_found,
        "has_github": has_github,
        "linkedin_found": has_linkedin,
        "email_count": len(info.get("email", [])),
        "phone_count": len(info.get("phone", [])),
        "word_count": wc,
        "skills_count": len(skills),
        "achievements": info.get("achievements", "No"),
        "languages": info.get("languages", []),
    }