import io
import re
from collections import Counter
from typing import Dict, List, Tuple

import pandas as pd
from docx import Document
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity

SKILLS = [
    "python", "java", "javascript", "typescript", "c", "c++", "sql", "html", "css",
    "react", "node.js", "fastapi", "flask", "django", "streamlit", "rest api",
    "machine learning", "deep learning", "natural language processing", "nlp",
    "computer vision", "data analysis", "data science", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch", "power bi", "tableau", "excel",
    "git", "github", "docker", "kubernetes", "aws", "azure", "gcp",
    "mysql", "postgresql", "mongodb", "firebase", "linux", "agile",
    "communication", "problem solving", "leadership", "teamwork",
    "project management", "testing", "debugging", "cybersecurity",
    "cloud computing", "data structures", "algorithms"
]

def extract_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    raw = uploaded_file.getvalue()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith(".docx"):
        doc = Document(io.BytesIO(raw))
        return "\n".join(p.text for p in doc.paragraphs)
    if name.endswith(".txt"):
        return raw.decode("utf-8-sig", errors="replace")
    raise ValueError("Please upload a PDF, DOCX, or TXT file.")

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def find_skills(text: str) -> List[str]:
    normalized = clean_text(text)
    found = []
    for skill in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, normalized):
            found.append(skill)
    return sorted(found)

def keyword_gaps(job_text: str, resume_text: str, limit: int = 15) -> List[str]:
    job = clean_text(job_text)
    resume = clean_text(resume_text)
    tokens = re.findall(r"[a-z][a-z0-9+#.-]{2,}", job)
    counts = Counter(t for t in tokens if t not in ENGLISH_STOP_WORDS)
    resume_tokens = set(re.findall(r"[a-z][a-z0-9+#.-]{2,}", resume))
    return [word for word, _ in counts.most_common(60) if word not in resume_tokens][:limit]

def compare(resume_text: str, job_text: str) -> Tuple[float, str]:
    if not resume_text.strip() or not job_text.strip():
        return 0.0, "Not enough text to compare."
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=8000)
    try:
        matrix = vectorizer.fit_transform([resume_text, job_text])
        score = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100)
        return round(score, 1), "TF-IDF cosine similarity"
    except ValueError:
        return 0.0, "Not enough distinct text to compare."

def analyze(resume_text: str, job_text: str) -> Dict:
    resume_skills = find_skills(resume_text)
    job_skills = find_skills(job_text)
    matched = sorted(set(resume_skills) & set(job_skills))
    missing = sorted(set(job_skills) - set(resume_skills))
    score, method = compare(resume_text, job_text)
    gaps = keyword_gaps(job_text, resume_text)
    suggestions = []
    if missing:
        suggestions.append("Review the missing skills list. Add a skill only if you genuinely have that experience.")
    if score < 25:
        suggestions.append("Tailor the summary and experience bullets to the responsibilities in the target role.")
    if not re.search(r"\b(project|projects)\b", resume_text, re.I):
        suggestions.append("Consider adding a Projects section with your role, tools, and measurable outcome.")
    if not re.search(r"\b(intern|internship|experience|employment)\b", resume_text, re.I):
        suggestions.append("Make relevant internships, work experience, volunteering, or practical work easy to find.")
    if not suggestions:
        suggestions.append("Your text has reasonable overlap. Improve clarity with specific evidence and measurable outcomes.")
    return {
        "score": score, "method": method, "resume_skills": resume_skills,
        "job_skills": job_skills, "matched_skills": matched,
        "missing_skills": missing, "keyword_gaps": gaps,
        "word_count": len(re.findall(r"\b\w+\b", resume_text)),
        "suggestions": suggestions
    }
