 # Student Feedback Analyzer
> Turning Student Voices into Actionable Institutional Insights

## What is this?

Student Feedback Analyzer is an AI-powered platform that automatically
processes large volumes of student feedback. It discovers recurring
themes, analyzes sentiment, filters low-quality submissions, and
generates actionable recommendations — all through an interactive
dashboard.

Built for educational institutions that receive thousands of feedback
responses every semester but lack the tools to act on them effectively.

---

## Why does this exist?

| Problem | Our Solution |
|---|---|
| Manual review is too slow | Automated multi-agent pipeline |
| Recurring issues go unnoticed | BERTopic theme discovery |
| Human bias in interpretation | RoBERTa sentiment + bias filtering |
| No actionable output | Groq LLaMA recommendation engine |
| Data stuck in spreadsheets | Interactive Streamlit dashboard |

---

## Demo

Upload a CSV of student feedback → get themes, sentiment, and
recommendations in minutes.

Pages available:
- Upload Feedback — CSV input
- Agent Dashboard — live pipeline monitoring
- Theme Discovery — interactive topic explorer
- Sentiment Analysis — charts and breakdowns
- Bias Report — outlier detection results
- Recommendations — prioritized action items

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| Embeddings | Sentence-Transformers (all-MiniLM-L6-v2) |
| Topic Modeling | BERTopic (UMAP + HDBSCAN + c-TF-IDF) |
| Sentiment | RoBERTa |
| Recommendations | Groq API (LLaMA 3.1) |
| Memory | Redis + PostgreSQL |
| Monitoring | OpenTelemetry |
| Deployment | Docker + Docker Compose |

---

## How to Install

### Prerequisites
- Python 3.10+
- Docker and Docker Compose
- Groq API key (free at console.groq.com)

### Steps

1. Clone the repository

```text
git clone https://github.com/youmindlattice/student-feedback-analyzer
cd student-feedback-analyzer
```

2. Set up environment variables

```text
cp .env.example .env
# Open .env and add your GROQ_API_KEY
```

3. Install dependencies

```text
pip install -r requirements.txt
```

---

## How to Run

### Frontend

Open a terminal, navigate to the frontend folder and run:

```text
cd E:\Student_feedback_analyser\frontend
python -m streamlit run app.py --server.port 8501
```

Frontend will be available at:

```text
http://localhost:8501
```

### Backend

Open a separate terminal at the project root and run:

```text
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend API will be available at:

```text
http://localhost:8000
```

## How to Use

1. Open http://localhost:8501 in your browser
2. Go to Upload Feedback page
3. Upload a CSV file with a column containing student feedback text
4. Watch the Agent Dashboard as each agent processes the data
5. View results across Theme Discovery, Sentiment, and Bias Report pages
6. Download recommendations from the Recommendations page

---

## Project Structure

```text
student-feedback-analyzer/
├── README.md                  # Project overview and setup guide
├── docker-compose.yml         # Container orchestration
├── requirements.txt           # Python dependencies
├── config.py                  # Global configuration
├── main.py                    # Application entry point
├── .env                       # Environment variables (API keys)
│
├── docs/
│   ├── ARCHITECTURE.md        # System design and data flow
│   ├── AGENTS.md              # Each agent explained in detail
│   ├── DATASET.md             # Dataset details and preprocessing
│   ├── API.md                 # FastAPI endpoints reference
│   ├── PROJECT_STRUCTURE.md   # Folder and file structure explained
│   ├── SETUP.md               # Local setup instructions
│   └── DOCUMENTATION.md       # Full hackathon submission document
│
├── frontend/                  # Streamlit dashboard and pages
├── agents/                    # All AI agents and orchestrator
├── memory/                    # Redis and PostgreSQL memory modules
├── communication/             # Message bus and task queue
├── api/                       # FastAPI routes and schemas
├── monitoring/                # Observability and decision tracer
└── database/                  # SQL initialization scripts
```

---

## Agent Pipeline

```text
┌─────────────────────────────────────────────┐
│              CSV Upload                      │
└───────────────────┬─────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          Preprocessing Agent                 │
│     clean · normalize · deduplicate          │
└───────────────────┬─────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│            Embedding Agent                   │
│     text → 384-dimensional vector            │
│     (Sentence-Transformers · GPU)            │
└──────────┬────────────────────┬─────────────┘
           ↓                    ↓
┌──────────────────┐  ┌──────────────────────┐
│   Theme Agent    │  │   Sentiment Agent     │
│   BERTopic       │  │   RoBERTa             │
│   UMAP → HDBSCAN │  │   pos / neg / neutral │
│   → c-TF-IDF     │  │   confidence score    │
└──────────┬───────┘  └────────────┬──────────┘
           └────────────┬──────────┘
                        ↓
┌─────────────────────────────────────────────┐
│              Bias Agent                      │
│  frequency threshold · confidence filter     │
│  anomaly detection                           │
└───────────────────┬─────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Recommendation Agent                 │
│         Groq LLaMA 3.1                       │
│   topic + sentiment → actionable insight     │
└───────────────────┬─────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           FastAPI Backend                    │
│   /topics · /sentiment · /recommendations    │
└───────────────────┬─────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Streamlit Dashboard                  │
├─────────────┬─────────────┬─────────────────┤
│ Admin View  │Faculty View │  Student View    │
└─────────────┴─────────────┴─────────────────┘
```

---

## Future Scope

- Multilingual feedback support
- Real-time streaming ingestion
- Predictive satisfaction models
- Mobile dashboard
- Institutional export reports

---

## License

MIT License — open for academic and institutional use.
