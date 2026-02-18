# RAG Document Analyzer

> A production-ready Retrieval-Augmented Generation (RAG) system for intelligent document question-answering, with integrated LLM observability and monitoring — powered by Groq's ultra-fast inference engine.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-rag--document--analyzer.vercel.app-blue)](https://rag-document-analyzer.vercel.app)
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger%20UI-green)](https://rag-document-analyzer.onrender.com/docs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## Overview

RAG Document Analyzer lets users upload PDF documents and ask natural-language questions, receiving accurate, source-cited answers grounded in the document content. It combines semantic vector search with LLM reasoning for fast, reliable document intelligence.

In its latest update, the system now includes a full **LLM observability and monitoring layer** — providing real-time visibility into token usage, query cost, latency, and prompt governance directly from a built-in dashboard.

**Built with:**
- React + Vite (Frontend)
- FastAPI (Backend)
- Groq (Llama 3.1 70B) for LLM inference
- ChromaDB for vector similarity search
- SQLAlchemy + SQLite/PostgreSQL for observability persistence

---

## Features

### Core RAG Capabilities
- **PDF Document Processing** — Upload and process PDFs with intelligent text chunking
- **AI-Powered Q&A** — Ask natural-language questions and receive grounded, accurate answers
- **Semantic Search** — Vector-based similarity search via ChromaDB
- **Source Citations** — Every answer includes relevant document excerpts with page references
- **Conversation History** — Context is maintained across multiple questions in a session
- **Lightning-Fast Inference** — Powered by Groq (500+ tokens/sec)

### LLM Observability (update)
- **Request Logging** — Every LLM call is logged with prompt, response, model, status, and timestamps
- **Token Usage Monitoring** — Tracks prompt tokens, completion tokens, and total tokens per request
- **Cost per Query** — Configurable per-1K token pricing for transparent cost accounting
- **Latency Tracking** — Per-request LLM latency measured and persisted in milliseconds
- **Prompt Versioning** — Prompt templates are versioned with active/inactive states for auditability
- **Observability Dashboard** — React tab visualizing metrics, trends, logs, and active prompt templates

### UI/UX
- Modern React interface built with TailwindCSS and shadcn/ui
- Responsive design across desktop and mobile
- Real-time upload progress and query processing indicators
- Drag-and-drop document upload
- Dedicated Observability tab with live metrics and request logs

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                     │
│   Document Upload │ Chat Interface │ Observability Dashboard │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (Axios)
┌────────────────────────▼────────────────────────────────────┐
│                      FastAPI Backend                         │
│              RAG Engine (Orchestrator)                       │
│   PDF Processor │ Groq API │ Sentence Transformers │ ChromaDB│
│                                                              │
│              Observability Layer                             │
│   groq_client.py (wrapped) │ observability_service.py       │
│   observability_db.py (SQLAlchemy) │ /observability router   │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- [Groq API Key](https://console.groq.com) (free tier available)
- 8 GB RAM minimum
- 2 GB free disk space

### 1. Clone the Repository

```bash
git clone https://github.com/Emart29/rag-document-analyzer.git
cd rag-document-analyzer
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Add your GROQ_API_KEY and observability config
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend: http://localhost:8000  
API Docs: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

---

## Environment Variables

Add the following to `backend/.env`:

```env
# Required
GROQ_API_KEY=gsk_...

# Observability database (SQLite default)
OBSERVABILITY_DB_URL=sqlite:///./observability.db

# Optional: PostgreSQL
# OBSERVABILITY_DB_URL=postgresql+psycopg2://user:password@localhost:5432/rag_obs

# Cost model (USD per 1,000 tokens)
GROQ_INPUT_TOKEN_COST_PER_1K=0.00059
GROQ_OUTPUT_TOKEN_COST_PER_1K=0.00079
```

---

## Usage

### Upload a Document
1. Open the **Upload** tab in the sidebar
2. Drag and drop a PDF, or click Browse
3. Wait for processing (typically 10–30 seconds)
4. The document appears in the Documents list

### Ask Questions
1. Optionally select specific documents (defaults to searching all)
2. Type your question in the chat input
3. Receive an AI-generated answer with source citations in 2–3 seconds

### Monitor with the Observability Dashboard
1. Open the **Observability** tab
2. View total queries, tokens consumed, estimated cost, and average latency
3. Inspect daily usage trends and per-request logs
4. Manage and review versioned prompt templates

---

## API Reference

### RAG Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/documents/upload` | Upload and process a PDF |
| GET | `/documents` | List all uploaded documents |
| POST | `/query` | Submit a question and receive an answer |

### Observability Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/observability/metrics?window_hours=24` | Aggregated metrics for the given window |
| GET | `/observability/logs?limit=50` | Recent LLM request logs |
| GET | `/observability/prompts` | List all prompt template versions |
| POST | `/observability/prompts` | Create a new prompt template version |

---

## Technology Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| Vite | Build tool & dev server |
| TailwindCSS | Styling |
| shadcn/ui | UI components |
| Tanstack Query | Server state management |
| Axios | HTTP client |
| React Markdown | Answer rendering |
| Lucide React | Icons |

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | REST API framework |
| Groq API | LLM inference (Llama 3.1 70B) |
| ChromaDB | Vector database |
| Sentence Transformers | Text embeddings |
| PyPDF2 / pdfplumber | PDF text extraction |
| SQLAlchemy | Observability persistence (SQLite/PostgreSQL) |
| Pydantic | Data validation |
| Uvicorn | ASGI server |

---

## Project Structure

```
rag-document-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routers/
│   │   │   ├── documents.py
│   │   │   ├── query.py
│   │   │   ├── system.py
│   │   │   └── observability.py          # ← update
│   │   ├── services/
│   │   │   ├── rag_engine.py
│   │   │   ├── groq_client.py            # ← Wrapped with observability
│   │   │   ├── embeddings.py
│   │   │   ├── pdf_processor.py
│   │   │   └── observability_service.py  # ← update
│   │   └── database/
│   │       ├── chroma_db.py
│   │       └── observability_db.py       # ← update
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── DocumentList.jsx
│   │   │   ├── ObservabilityDashboard.jsx  # ← update
│   │   │   └── ui/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
└── README.md
```

---

## Performance

Tested on (Intel i5 8th Gen, 8 GB RAM):

| Operation | Duration | Notes |
|-----------|----------|-------|
| Document Upload | 10–30s | 5-page PDF |
| Question Answering | 1–3s | Retrieval + generation |
| Semantic Search | < 100ms | ChromaDB query |
| Backend Memory | ~600 MB | Runtime |
| LLM Inference | 500+ tokens/sec | Via Groq |

---

## Deployment

### Frontend — Vercel (Free)

```bash
npm i -g vercel
cd frontend
vercel
# Set VITE_API_URL=https://your-backend.onrender.com
```

### Backend — Render.com (Free)

Create `render.yaml` in the project root:

```yaml
services:
  - type: web
    name: rag-backend
    env: python
    region: oregon
    plan: free
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: OBSERVABILITY_DB_URL
        value: sqlite:///./observability.db
```

Push to GitHub → connect repo to Render → add `GROQ_API_KEY` → deploy.

---

## Security

- Environment variables for all sensitive credentials
- Input validation via Pydantic models
- CORS configured for frontend origin
- File size and type validation on upload
- Error handling and structured logging throughout
- **Recommended for production:** Add JWT authentication and per-user document isolation

---

## Troubleshooting

**`GROQ_API_KEY not found`**
```bash
cat backend/.env  # Verify GROQ_API_KEY=gsk_... is present
```

**ChromaDB errors**
```bash
rm -rf backend/chroma_db/
# Restart the backend
```

**PDF processing fails**
```bash
pip install python-magic       # macOS/Linux
pip install python-magic-bin   # Windows
```

**Frontend API connection refused**
```bash
# Verify VITE_API_URL in frontend/.env points to the running backend
```

**Build errors**
```bash
rm -rf node_modules package-lock.json
npm install
```

---

## Roadmap

- [ ] Multi-format support (.docx, .txt, .md)
- [ ] JWT-based user authentication
- [ ] Per-user document isolation (multi-tenancy)
- [ ] Streaming LLM responses (real-time tokens)
- [ ] Export conversation history
- [ ] Voice input (speech-to-text)
- [ ] Auto-generated document summaries
- [ ] Collaborative document sharing
- [ ] Advanced analytics (per-user usage, cost breakdowns)

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

This project is licensed under the [MIT License](./LICENSE).

---

## Author

**Emmanuel Nwanguma**  
[GitHub: Emart29](https://github.com/Emart29) · [LinkedIn](https://linkedin.com/in/emmanuel-nwanguma)

---

## Acknowledgments

- [Groq](https://groq.com) — Ultra-fast LLM inference
- [ChromaDB](https://www.trychroma.com) — Open-source embedding database
- [FastAPI](https://fastapi.tiangolo.com) — Modern Python web framework
- [Sentence Transformers](https://www.sbert.net) — State-of-the-art text embeddings
- [shadcn/ui](https://ui.shadcn.com) — Beautiful React component library
- [Vercel](https://vercel.com) & [Render](https://render.com) — Hosting platforms

---

*If this project was useful to you, consider giving it a ⭐ on GitHub.*
