# AI-Resume-Screening-System

An explainable, enterprise-grade AI-powered **Resume Screening, ATS Alignment, and Resume Builder** web application. Designed to eliminate the black-box nature of commercial ATS scanners by combining **deterministic alias matching**, **deep semantic similarity embeddings**, **anti-hallucination recommendation generation**, and **ATS-optimized ReportLab PDF generation**.

---

## 📌 Executive Architecture & Processing Pipeline

The core philosophy of this project is that an ATS system must never be a simple `Resume -> LLM -> Answer` wrapper. Instead, it follows a multi-stage, schema-validated engineering pipeline:

```
[Resume PDF / DOCX]
       ↓
(1) Parse Page-by-Page (PyMuPDF / python-docx)
       ↓
(2) Deterministic Regex (Email, Phone, Links)
       ↓
(3) LLM Structuring & Controlled Repair (Pydantic Validation)
       ↓
(4) Job Description Requirement Analysis
       ↓
(5) Canonical Skill Normalization & Alias Matching
       ↓
(6) Semantic Cosine Similarity (sentence-transformers / all-MiniLM-L6-v2)
       ↓
(7) Explainable ATS Scoring (0 - 100 Multi-Factor Formula)
       ↓
(8) Evidence-Backed Recommendations (Dual Evidence Grounding)
       ↓
(9) Interactive Candidate Review & Editor (Google XYZ Formula)
       ↓
(10) ATS-Friendly Machine-Readable PDF (ReportLab)
```

---

## 🚀 Key Features

1. **Multi-Format Document Ingestion**
   - Drag-and-drop parsing for **PDF** (`PyMuPDF`) and **DOCX** (`python-docx`).
   - Page-by-page text extraction, page counting, section segmentation, file size validation, and corruption protection.
2. **Hybrid Pydantic Structuring Pipeline**
   - High-precision regex for contact fields (emails, phones, portfolio/LinkedIn URLs).
   - Strict Pydantic schema validation with automatic self-repair on unexpected LLM formats.
3. **Canonical Skill Normalization & Alias Matching**
   - Built-in canonical alias dictionary (`Postgres` → `PostgreSQL`, `ReactJS` → `React`, `NodeJS` → `Node.js`, `K8s` → `Kubernetes`).
   - Exact and alias matching runs *before* semantic matching to prevent false positives.
4. **Semantic Matching with Vector Embeddings**
   - Leverages `sentence-transformers/all-MiniLM-L6-v2` and cosine similarity.
   - Accurately links conceptual statements like *"Architected microservices using FastAPI"* to *"REST API development"*.
5. **Explainable ATS Compatibility Score (0 - 100)**
   - No opaque, randomized scores. Calculated transparently via:
     - **Required Skills Coverage**: 40%
     - **Experience Relevance**: 25%
     - **Semantic Alignment**: 20%
     - **Preferred Skills Coverage**: 15%
   - Prominently displays an honest candidate disclaimer.
6. **Strict Anti-Hallucination Recommendation Engine**
   - Strictly grounded in candidate-supplied facts.
   - **Guaranteed never to invent** candidate employment, projects, metrics, certifications, or schools.
   - Formulates improvement advice using dual evidence: **[Resume Evidence]** paired with **[Target JD Requirement]**.
7. **Google XYZ Bullet Point Enhancer**
   - Restructures weak bullet points into *"Accomplished [X] as measured by [Y], by doing [Z]"*.
   - Prompts the user to plug in their own actual metrics rather than fabricating statistics.
8. **Interactive Resume Editor & ReportLab PDF Builder**
   - Candidate maintains full control: AI suggestions do not alter the resume without explicit user review.
   - Exports clean, machine-readable ATS PDFs with native vector text and clickable links.
9. **Screening History & Version Tracking**
   - Stores resumes, job descriptions, and past analysis reports in PostgreSQL (with zero-configuration SQLite local fallback).

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, Vite, Tailwind CSS v4, Axios, React Router v7, Lucide React |
| **Backend** | Python 3.12, FastAPI, Uvicorn, Pydantic v2 |
| **AI / NLP** | Groq API (`llama-3.3-70b-versatile`), `sentence-transformers` (`all-MiniLM-L6-v2`), PyTorch, NumPy |
| **Document Processing** | PyMuPDF (`fitz`), `python-docx` |
| **PDF Generation** | ReportLab |
| **Database** | PostgreSQL 16 (production), SQLite 3 (local dev fallback), SQLAlchemy 2.0 |
| **DevOps** | Docker, Docker Compose |

---

## 📂 Project Structure

```
AI-Resume-Screening-System/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint, middleware, lifespan
│   │   ├── config.py                   # Pydantic Settings & environment config
│   │   ├── api/
│   │   │   ├── resume_routes.py        # Upload, update, delete, PDF download
│   │   │   ├── analysis_routes.py      # JD analysis, ATS scoring, bullet optimizer
│   │   │   └── history_routes.py       # Past analysis reports & logs
│   │   ├── models/
│   │   │   ├── database_models.py      # SQLAlchemy models (User, Resume, Analysis, etc.)
│   │   │   └── schemas.py              # Pydantic schemas (ResumeSchema, ATSBreakdown, etc.)
│   │   ├── services/
│   │   │   ├── resume_parser.py        # PDF & DOCX text extraction
│   │   │   ├── resume_extractor.py     # Hybrid extraction & schema validation
│   │   │   ├── jd_extractor.py         # Job description requirement parser
│   │   │   ├── skill_matcher.py        # Deterministic & alias skill matcher
│   │   │   ├── semantic_matcher.py     # SentenceTransformers cosine similarity
│   │   │   ├── ats_scorer.py           # Multi-factor explainable scoring engine
│   │   │   ├── recommendation_engine.py# Evidence-grounded suggestions
│   │   │   ├── pdf_generator.py        # ReportLab ATS resume generator
│   │   │   └── llm_provider.py         # LLM abstraction (Groq + Rule-based fallback)
│   │   ├── utils/
│   │   │   ├── text_cleaner.py         # Regex parsing, email/phone/url extraction
│   │   │   ├── skill_normalizer.py     # Canonical skill alias dictionary
│   │   │   └── logger.py               # Structured JSON logger with PII masking
│   │   └── database/
│   │       └── database.py             # Database engine & session management
│   ├── tests/
│   │   ├── conftest.py                 # Fixtures & TestClient setup
│   │   ├── test_parser.py              # Document extraction & validation tests
│   │   ├── test_extraction.py          # Normalization & schema tests
│   │   ├── test_matching.py            # Skill & semantic matching tests
│   │   ├── test_analysis.py            # ATS score & API endpoint tests
│   │   └── test_pdf.py                 # ReportLab PDF generation tests
│   ├── requirements.txt                # Python dependencies
│   ├── .env.example                    # Backend environment template
│   └── Dockerfile                      # Backend container configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx              # Navigation header with live health indicator
│   │   │   ├── Footer.jsx              # Application footer
│   │   │   ├── FileUpload.jsx          # Drag-and-drop resume uploader
│   │   │   ├── ScoreGauge.jsx          # Circular ATS score gauge & breakdown
│   │   │   ├── SkillBadge.jsx          # Matched / missing status pills
│   │   │   ├── RecommendationCard.jsx  # Evidence-paired recommendation card
│   │   │   └── Toast.jsx               # Floating notification alerts
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx         # Hero & pipeline walkthrough
│   │   │   ├── Dashboard.jsx           # KPI metrics & quick screening view
│   │   │   ├── UploadPage.jsx          # Resume upload & parsing summary
│   │   │   ├── AnalysisPage.jsx        # JD match analysis & suggestions
│   │   │   ├── EditorPage.jsx          # Interactive resume editor & XYZ enhancer
│   │   │   └── HistoryPage.jsx         # Past screening reports
│   │   ├── services/
│   │   │   └── api.js                  # Axios client for backend endpoints
│   │   ├── hooks/
│   │   │   └── useResume.jsx           # Global resume & analysis context
│   │   ├── utils/
│   │   │   └── formatters.js           # Date and score formatting helpers
│   │   ├── App.jsx                     # Route definitions & layout wrappers
│   │   ├── main.jsx                    # React DOM entrypoint
│   │   └── index.css                   # Tailwind CSS v4 styling & dark theme
│   ├── package.json                    # Frontend dependencies & scripts
│   ├── vite.config.js                  # Vite configuration & backend proxy
│   ├── .env.example                    # Frontend environment template
│   └── Dockerfile                      # Frontend container configuration
├── docs/
│   ├── PROJECT_EXPLANATION.md          # Comprehensive explanation in simple English
│   └── QUICK_SCRIPT.md                 # 2-minute interview presentation script
├── docker-compose.yml                  # Full stack compose (DB + Backend + Frontend)
├── .gitignore                          # Git ignore rules
└── README.md                           # Documentation root
```

---

## ⚡ Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional) Docker & Docker Compose
- (Optional) Groq API Key (If omitted, the system seamlessly uses its built-in rule-based NLP engine)

---

### Local Development Setup

#### 1. Backend Setup
```bash
cd backend

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY if available

# Run the FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```
Backend API will be available at: **http://127.0.0.1:8000**
Interactive Swagger Documentation: **http://127.0.0.1:8000/docs**

#### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start Vite development server
npm run dev
```
Frontend will be available at: **http://localhost:5173**

---

## 🐳 Docker Deployment

To spin up the entire application stack (PostgreSQL, FastAPI Backend, and Nginx Frontend) with a single command:

```bash
# Set your Groq API key (optional)
export GROQ_API_KEY="your-groq-key-here"

# Build and start all services
docker-compose up --build
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432

---

## 🧪 Automated Testing Suite

The project includes an end-to-end suite of 19 automated unit and integration tests covering parser safety, Pydantic repair, embedding similarity, ATS score boundaries, and API workflows:

```bash
# Run tests from project root
python3 -m pytest backend/tests/ -v
```

Test coverage includes:
- `test_parser.py`: PDF & DOCX extraction, corrupted file rejection, file size limits, section detection.
- `test_extraction.py`: Regex extraction (emails, phones, URLs), skill canonicalization, schema repair.
- `test_matching.py`: Exact/alias skill matching, `SentenceTransformer` cosine similarity, ATS score constraints.
- `test_analysis.py`: Evidence-based recommendations, Google XYZ enhancer, full API endpoint lifecycles.
- `test_pdf.py`: ReportLab PDF byte streaming and text extractability verification.

---

## 📊 How ATS Scoring Works

The compatibility score is calculated using an explainable weighted formula:

$$\text{Overall Score} = (0.40 \times \text{Req}) + (0.25 \times \text{Exp}) + (0.20 \times \text{Sem}) + (0.15 \times \text{Pref})$$

Where:
- **$\text{Req}$ (Required Skill Score, 40%)**: Ratio of mandatory skills detected in resume via exact and alias matching.
- **$\text{Exp}$ (Experience Relevance, 25%)**: Proximity of job titles, density of domain responsibilities, and work history duration.
- **$\text{Sem}$ (Semantic Similarity, 20%)**: Average cosine similarity computed by `all-MiniLM-L6-v2` between JD responsibilities and resume highlight statements.
- **$\text{Pref}$ (Preferred Skill Score, 15%)**: Bonus coverage of nice-to-have tools and cloud technologies.

---

## 🛡️ Security & Privacy Principles

- **No Complete Raw Resumes in Logs**: Structured logger masks sensitive PII and limits logs to character lengths and metadata.
- **Strict File Type & Size Validation**: Enforces MIME validation and 10MB file caps.
- **No Secret Leakage**: Secrets and API tokens are never written to disk or logged.
- **Controlled Exception Handling**: Prevents internal stack traces from leaking to client responses.

---

## 🔮 Future Improvements

1. Multi-resume batch candidate screening for enterprise recruiters.
2. Custom multi-language resume parsing (Spanish, German, French).
3. Integration with GitHub & LinkedIn OAuth for direct profile import.
4. Support for LaTeX source resume generation.
