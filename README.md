# CareerCompass AI — Resume & Job Match Analyzer

CareerCompass AI is a local, API-key-free resume analysis and job matching dashboard. Upload a PDF/DOCX/TXT resume, paste a job description, and get:
- A resume text preview and basic profile statistics
- Skill coverage analysis against the job description
- A transparent TF-IDF/cosine-similarity match score
- Important job-description keywords missing from the resume
- Actionable suggestions and a downloadable analysis report

> This is a portfolio/learning tool, not an official ATS score or a hiring decision system. It does not guarantee interview selection. Review suggestions for accuracy before changing a resume.

## Requirements
- Python 3.10–3.12 recommended
- VS Code
- Internet only for installing packages; analysis runs locally

## Windows setup (PowerShell)
Open the project folder in VS Code, then:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks activation, skip activation and use:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If `python` is not found, install Python 3.12 and select it in VS Code. Do not use a Python version that your installed packages do not support.

Streamlit normally opens `http://localhost:8501`.

## Usage
1. Upload a resume as PDF, DOCX, or TXT.
2. Paste the target job description.
3. Click **Analyze my match**.
4. Review the score, matched skills, missing keywords and suggestions.
5. Download the report as a Markdown file.

## Project structure
```text
CareerCompass-AI/
├── app.py
├── analyzer.py
├── requirements.txt
├── README.md
├── .gitignore
└── sample_data/
    ├── sample_resume.txt
    └── sample_job_description.txt
```

## How the matching works
The app extracts text from the uploaded file, normalizes it, and compares resume and job-description text with TF-IDF vectors and cosine similarity. It also checks a curated skills vocabulary and extracts frequent job-description terms not present in the resume. These are heuristic signals, not a measure of a candidate's actual ability.

## Privacy
Files are processed in the local Streamlit session. Do not upload confidential documents to a shared/public deployment. The app does not intentionally save uploaded resumes to disk.

## Troubleshooting
- **PDF text is empty:** the PDF may be scanned. This version does not include OCR; try a text-based PDF or DOCX/TXT.
- **DOCX error:** make sure the file is a valid Word document.
- **Port is busy:** run `python -m streamlit run app.py --server.port 8502`.
- **Package installation fails:** use Python 3.12 in a fresh virtual environment and retry.
