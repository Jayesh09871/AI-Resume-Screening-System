# Project Explanation Guide: AI-Resume-Screening-System

> **Purpose of this document:**  
> This guide explains the entire project in **very simple, clear English**. If your mentor or interviewer asks about any file, any folder, or any line of code, you will find the exact explanation here.

---

## 1. What is this project in simple words?

Imagine you are applying for a software job.
- You have a resume (PDF or Word document).
- The company has a **Job Description (JD)** listing what they want (like Python, React, Docker).
- Most companies use automated software called an **Applicant Tracking System (ATS)** to filter resumes before a human ever looks at them.

Most existing resume tools make two big mistakes:
1. **They are black boxes:** They give you a random score (like "72%") without explaining where that number came from.
2. **They make things up (Hallucination):** Many AI tools invent fake numbers, fake metrics, or fake companies that the candidate never actually worked for.

### Our Solution:
Our **AI-Resume-Screening-System** is a full-stack web application that:
1. Reads your resume and extracts every detail cleanly.
2. Compares your resume against any Job Description.
3. Calculates an **explainable match score from 0 to 100** based on clear rules.
4. Uses **smart AI matching (Semantic Embeddings)** so that words with the same meaning match even if the wording is different.
5. Gives you **evidence-based suggestions** without ever inventing fake information.
6. Lets you edit your resume on a live dashboard and download a clean, machine-readable PDF.

---

## 2. The 10-Step Pipeline (How the Project Works Step-by-Step)

```
[Your Resume File: PDF or DOCX]
       ↓
Step 1: Document Parsing (PyMuPDF / python-docx reads text page-by-page)
       ↓
Step 2: Rule-Based Contact Extraction (Regex finds email, phone, links)
       ↓
Step 3: AI Structuring & Safety Check (Converts text to JSON, validated by Pydantic)
       ↓
Step 4: Job Description Analysis (Separates required skills from optional skills)
       ↓
Step 5: Skill Normalization (Maps aliases like "Postgres" to "PostgreSQL")
       ↓
Step 6: Semantic Matching (Sentence embeddings match similar concepts)
       ↓
Step 7: Explainable ATS Scoring (Calculates 0-100 score using 4 weighted parts)
       ↓
Step 8: Evidence-Based Suggestions (Pairs resume quotes with job requirements)
       ↓
Step 9: Interactive Editing (Candidate reviews and edits bullet points)
       ↓
Step 10: ATS PDF Generation (ReportLab creates a clean, readable PDF)
```

---

## 3. Complete File-by-File & Folder-by-Folder Guide

Your mentor can point to any file in the project. Here is what every single folder and file does:

### Root Directory
- **`README.md`**: The main project overview document. It contains feature lists, architecture diagrams, setup commands, and Docker instructions.
- **`docker-compose.yml`**: A configuration file that lets you start the entire project (PostgreSQL database + FastAPI backend + React frontend) with a single command (`docker-compose up`).
- **`.gitignore`**: Tells Git which files to ignore (like passwords in `.env`, virtual environment folders, and cache files).

---

### Backend Directory (`backend/`)

- **`backend/requirements.txt`**: A list of all Python libraries required by the backend (FastAPI, PyMuPDF, python-docx, sentence-transformers, SQLAlchemy, ReportLab, etc.).
- **`backend/.env.example`**: A template showing what environment variables are needed (like port numbers, database URLs, and Groq API keys) without exposing private keys.
- **`backend/.env`**: The actual configuration file used when running the backend locally.
- **`backend/Dockerfile`**: Instructions for building a Docker container for the Python backend.

#### Backend Application (`backend/app/`)
- **`backend/app/__init__.py`**: Marks `app` as a Python package.
- **`backend/app/main.py`**: The entrypoint of the backend. It starts FastAPI, configures CORS (so frontend can talk to backend), sets up structured request-time logging, connects to the database, and registers all API routes.
- **`backend/app/config.py`**: Reads settings from `.env` using Pydantic Settings. Ensures folders for file uploads and generated PDFs exist automatically.

#### Backend API Routes (`backend/app/api/`)
- **`backend/app/api/__init__.py`**: Package marker for routes.
- **`backend/app/api/resume_routes.py`**: Handles all resume file operations:
  - `POST /api/resumes/upload`: Uploads a PDF or DOCX file, extracts text, converts it to structured JSON, and saves it.
  - `GET /api/resumes/{id}`: Fetches a saved resume by its ID.
  - `PUT /api/resumes/{id}`: Saves edits made by the user and records a new version number.
  - `DELETE /api/resumes/{id}`: Deletes a resume.
  - `POST /api/resumes/{id}/pdf`: Builds and downloads a professional ATS PDF.
- **`backend/app/api/analysis_routes.py`**: Handles matching and scoring:
  - `POST /api/analyze`: Takes a resume and a Job Description, runs skill matching and semantic analysis, calculates the ATS score, generates recommendations, and saves the report.
  - `POST /api/improve`: Takes a single weak bullet point and rewrites it using the Google XYZ formula.
  - `GET /api/analyses/{id}`: Retrieves a previously saved analysis report.
- **`backend/app/api/history_routes.py`**:
  - `GET /api/history`: Returns a list of all past resume screenings.
  - `DELETE /api/history/{id}`: Deletes a report from history.

#### Backend Data Models (`backend/app/models/`)
- **`backend/app/models/__init__.py`**: Package marker for models.
- **`backend/app/models/schemas.py`**: Contains **Pydantic schemas**. Pydantic acts like a strict security guard that checks data shapes. If an LLM returns unexpected data, Pydantic catches it immediately. Defines schemas for `ResumeSchema`, `JobDescriptionSchema`, `ATSScoreBreakdown`, `MatchResultSchema`, and `EvidenceBasedSuggestion`.
- **`backend/app/models/database_models.py`**: Contains **SQLAlchemy database models**. These define the tables in the database:
  - `User`: Candidate user records.
  - `Resume`: Stores resume title, raw text, structured JSON data, and version number.
  - `JobDescription`: Stores job text and extracted requirements.
  - `Analysis`: Stores the final ATS score breakdown and suggestions.
  - `ResumeVersion`: Keeps a history of every edit made to a resume.

#### Backend Services (`backend/app/services/`)
- **`backend/app/services/__init__.py`**: Package marker for services.
- **`backend/app/services/resume_parser.py`**: Reads raw files. Uses `fitz` (PyMuPDF) to read PDF files page-by-page, and `python-docx` to read Word files. Detects sections like Summary, Skills, Experience, and Education.
- **`backend/app/services/resume_extractor.py`**: The hybrid extraction engine. Combines regex rules (for emails and phones) with LLM parsing, followed by automatic data repair and Pydantic validation.
- **`backend/app/services/jd_extractor.py`**: Reads the Job Description and separates required (mandatory) skills from preferred (nice-to-have) skills and responsibilities.
- **`backend/app/services/skill_matcher.py`**: Matches resume skills against job requirements deterministically using exact names and aliases.
- **`backend/app/services/semantic_matcher.py`**: Uses the AI model `all-MiniLM-L6-v2` to create sentence embeddings and calculates cosine similarity. Finds the closest sentence in your resume for each requirement in the job description.
- **`backend/app/services/ats_scorer.py`**: Calculates the 0-100 ATS compatibility score using our explainable formula (40% required skills, 25% experience, 20% semantic alignment, 15% preferred skills).
- **`backend/app/services/recommendation_engine.py`**: Generates honest advice. Follows the **Anti-Hallucination rule**: every suggestion must cite actual evidence from your resume and link it to an actual requirement in the job description.
- **`backend/app/services/pdf_generator.py`**: Uses the `ReportLab` library to draw a clean, single-column, machine-readable PDF resume that ATS scanners can easily read. Supports 3 styles: `classic_ats` (standard corporate), `modern_tech` (indigo/slate), and `executive` (navy serif).
- **`backend/app/services/linguistic_analyzer.py`**: Evaluates resume language against industry recruiter standards. Checks for strong action verbs, detects weak passive phrasing (e.g., "worked on"), calculates the ratio of quantified bullet points (with numbers/metrics), and assigns an ATS Linguistic Quality Score (0-100).
- **`backend/app/services/llm_provider.py`**: An abstraction layer. Supports Groq's high-speed LLaMA 3.3 model, and includes a built-in rule-based fallback so the app works even offline without an API key.

#### Backend Utilities & Database (`backend/app/utils/` and `backend/app/database/`)
- **`backend/app/utils/text_cleaner.py`**: Cleans up messy whitespace and uses regular expressions (regex) to reliably detect emails, phone numbers, and URLs.
- **`backend/app/utils/skill_normalizer.py`**: Contains a dictionary of skill aliases (for example: converts "Postgres" to "PostgreSQL", "React.js" to "React", "K8s" to "Kubernetes").
- **`backend/app/utils/logger.py`**: Structured JSON logger. Automatically hides private keys and masks candidate personal info so sensitive data is never leaked into logs.
- **`backend/app/database/database.py`**: Creates the database connection. Uses PostgreSQL in production, with an automatic fallback to local SQLite for easy development.

#### Backend Automated Tests (`backend/tests/`)
- **`backend/tests/conftest.py`**: Provides fake sample data (fake candidate resume, fake job description, in-memory test PDF, in-memory test DOCX) and a test client.
- **`backend/tests/test_parser.py`**: Tests PDF extraction, DOCX extraction, section detection, and corrupted file handling.
- **`backend/tests/test_extraction.py`**: Tests regex parsing, skill normalization, and Pydantic validation.
- **`backend/tests/test_matching.py`**: Tests deterministic skill matching, semantic embeddings, and score calculation.
- **`backend/tests/test_analysis.py`**: Tests the recommendation engine, bullet point improvement, linguistic action verb analysis, and API endpoints.
- **`backend/tests/test_pdf.py`**: Tests that ReportLab generates a valid PDF file containing real text across templates.

---

### Frontend Directory (`frontend/`)

- **`frontend/package.json`**: Lists frontend packages (React 19, Vite, Tailwind CSS, Axios, React Router, Lucide icons).
- **`frontend/vite.config.js`**: Vite build configuration. Connects Tailwind CSS and sets up an API proxy to `http://127.0.0.1:8000`.
- **`frontend/index.html`**: The HTML entry page containing page title and Google Inter font.
- **`frontend/Dockerfile`**: Multi-stage Docker build that builds the React app and serves it with Nginx.

#### Frontend Components (`frontend/src/components/`)
- **`frontend/src/components/Navbar.jsx`**: Top navigation bar with links and a live status badge showing whether the backend API and Groq LLM are active.
- **`frontend/src/components/Footer.jsx`**: Bottom footer with technology stack details.
- **`frontend/src/components/FileUpload.jsx`**: Interactive drag-and-drop file uploader with animated progress bar, file size validation, and format indicators.
- **`frontend/src/components/ScoreGauge.jsx`**: An animated circular progress gauge displaying the 0-100 ATS score and sub-metric breakdown bars.
- **`frontend/src/components/SkillBadge.jsx`**: Color-coded badges for skills (green for matched, red for missing required, yellow for preferred).
- **`frontend/src/components/RecommendationCard.jsx`**: Expandable card showing a suggestion, why it matters, the resume quote, and the job requirement.
- **`frontend/src/components/Toast.jsx`**: Floating alert messages (success/error/info) that appear at the bottom-right of the screen.

#### Frontend Pages (`frontend/src/pages/`)
- **`frontend/src/pages/LandingPage.jsx`**: Welcome page explaining the architecture pipeline and key innovations.
- **`frontend/src/pages/Dashboard.jsx`**: Main dashboard showing KPI numbers (ATS score, matched skills, missing skills) and recent screening history.
- **`frontend/src/pages/UploadPage.jsx`**: Page where users drop their resume file and view extracted contact info and detected sections.
- **`frontend/src/pages/AnalysisPage.jsx`**: The core analysis screen. Allows users to paste a Job Description (or click a sample JD button), run ATS screening, and view scores, semantic alignment, and recommendations.
- **`frontend/src/pages/EditorPage.jsx`**: Full resume builder and editor. Allows users to modify sections, use the AI Google XYZ Bullet Enhancer, and download an ATS-compliant PDF.
- **`frontend/src/pages/HistoryPage.jsx`**: Shows all past screening reports with options to reload or delete them.

#### Frontend State & Utilities (`frontend/src/`)
- **`frontend/src/services/api.js`**: Axios HTTP client that talks to all FastAPI endpoints.
- **`frontend/src/hooks/useResume.jsx`**: Global React Context that shares the active resume, active job description, and active analysis across all pages.
- **`frontend/src/utils/formatters.js`**: Helper functions to format dates and assign colors to scores.
- **`frontend/src/App.jsx`**: Main React component with all page routes.
- **`frontend/src/main.jsx`**: Mounts the React app into the DOM.
- **`frontend/src/index.css`**: Tailwind CSS v4 design system with dark mode glassmorphism effects.

---

## 4. Key Technical Concepts Explained Simply

### What is Skill Normalization?
Different people write the same skill in different ways:
- One person writes: `Postgres`
- Another writes: `postgresql`
- The job description asks for: `PostgreSQL`
If you do a simple word check, they won't match!
**Our solution:** In `skill_normalizer.py`, we created an alias dictionary. It maps all variations to a single official name (`PostgreSQL`). This happens *before* any AI matching.

### What is Semantic Matching and Cosine Similarity?
- **Exact match:** Only matches identical words.
- **Semantic match:** Matches meaning. For example:
  - Job Description says: *"Experience with REST API development"*
  - Resume says: *"Architected backend services using FastAPI"*
These mean the same thing, but have completely different words.
**How it works:** We use `sentence-transformers/all-MiniLM-L6-v2`. This model turns each sentence into a list of 384 numbers (called an **embedding** or vector). Think of these numbers like latitude and longitude coordinates on a map. If two sentences have similar meanings, their coordinates are very close together. We measure the angle between them using **cosine similarity** (a number between 0 and 1).

### How is the ATS Score calculated?
We do not randomly pick numbers. We use a transparent mathematical formula:
- **Required Skills (40%):** How many mandatory skills did you have?
- **Experience Relevance (25%):** Are your job titles and work history relevant to the target role?
- **Semantic Alignment (20%):** Do your bullet points conceptually align with the day-to-day responsibilities?
- **Preferred Skills (15%):** Do you have bonus or nice-to-have skills?

### What is the Google XYZ Formula for bullet points?
Recruiters love bullets that follow this formula:
> **Accomplished [X] as measured by [Y], by doing [Z]**  
*Example:* "Reduced API response times by 35% [Y] by implementing Redis caching [Z]."  
Our AI Bullet Optimizer in the editor rewrites weak statements into this structure without making up fake statistics.

---

## 5. Frequently Asked Mentor & Interview Questions

**Q1: Why did you not just send the resume and JD directly to an LLM like ChatGPT and ask for a score?**  
*Answer:* Sending everything to an LLM is a "black-box" approach. LLMs suffer from three big problems:
1. They hallucinate (make up facts and numbers).
2. The score is not reproducible (asking twice gives two different scores).
3. It is expensive and slow.  
Our system uses a **hybrid approach**: exact regex for contacts, alias normalization for skills, sentence embeddings for semantic similarity, a mathematical formula for scoring, and the LLM only for structured interpretation and advice.

**Q2: What happens if Groq API is down or the user does not have an API key?**  
*Answer:* We implemented an **LLM Provider Abstraction** (`BaseLLMProvider`). If Groq is unavailable, the application automatically switches to `RuleBasedNLPProvider`, our local rule-based engine. The system never crashes.

**Q3: How do you prevent sensitive candidate data from leaking into logs?**  
*Answer:* In `backend/app/utils/logger.py`, our custom `StructuredFormatter` intercepts log messages. Any field containing passwords, API tokens, or secrets is replaced with `[REDACTED]`, and full resumes are logged only by their character length, never raw text.
