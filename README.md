# HireSense AI – Intelligent Resume Screening & Recruitment System

## Abstract
HireSense AI is an AI-assisted recruitment screening application for an MSc IT/BSc CS college project. It extracts resume text, compares it with job requirements and produces transparent advisory scores.

## Architecture
One Flask application using Jinja2 + Bootstrap for the UI, SQLAlchemy with SQLite for persistence, and Python services for resume parsing and NLP.

## AI methodology
**TF-IDF:** converts job and resume text into weighted word vectors.  
**Cosine similarity:** measures textual similarity between the two vectors.  
**Skill matching:** compares normalized required skills with detected resume skills.  
**Experience matching:** detects simple year/years expressions and compares them with the job requirement.

Final Score = 60% text similarity + 30% skill match + 10% experience match.

Recommendations: 80+ Strong Match, 65–79 Good Match, 50–64 Potential Match, below 50 Low Match.

## Modules
Authentication, job management, resume processing, skill extraction, screening, ranking, analytics, reports and profile management.

## Gemini
Set `GEMINI_API_KEY` to enable optional Gemini enhancement. The local screening algorithm does not depend on Gemini; without a key or if the API fails, a deterministic local fallback is used.

## Installation
Python 3.10+ is recommended.

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Environment variables
Copy `.env.example` to `.env` and set:
- `SECRET_KEY`
- `GEMINI_API_KEY` (optional)
- `DATABASE_URL` (optional; SQLite is the default)

## Demo login
Email: `admin@hiresense.ai`  
Password: `Admin@123`

Demo jobs are created automatically on first run.

## Screening workflow
1. Login.
2. Upload a PDF or DOCX resume (max 5 MB).
3. Open Screening.
4. Select a job and candidate.
5. Run screening.
6. Review score breakdown, skills, recommendation and optional AI insights.
7. View candidates, analytics and printable report.

## Security
Passwords are hashed. Uploaded filenames are secured. API keys are read only from environment variables and are never sent to browser code. `.env` and database files are excluded from the distributable source archive.

## Limitations
Resume parsing is heuristic and depends on document formatting. Experience detection is intentionally simple. TF-IDF is lexical rather than a deep semantic model. Gemini output can vary and should be reviewed.

## Future scope
Semantic embeddings, richer OCR, multilingual parsing, recruiter collaboration, audit trails and configurable scoring models.

## College-project disclaimer
HireSense AI is an AI-assisted recruitment screening and ranking system. It does not make final hiring decisions. Recruiters remain responsible for evaluating candidates.
