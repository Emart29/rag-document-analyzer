# 🚀 RAG Document Analyzer

A **production-ready Retrieval-Augmented Generation (RAG) system** for intelligent document question-answering, powered by **Groq’s ultra-fast LLM inference**.

🎥 **Live Demo**: https://rag-document-analyzer.vercel.app  
📖 **API Docs (Swagger)**: https://rag-document-analyzer.onrender.com/docs  
🐛 **Report Bug**: https://github.com/Emart29/rag-document-analyzer/issues  

[![Live Demo](https://img.shields.io/badge/Live-Demo-green)](https://rag-document-analyzer.vercel.app)
[![API Docs](https://img.shields.io/badge/API-Docs-blue)](https://rag-document-analyzer.onrender.com/docs)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Overview

**RAG Document Analyzer** allows users to upload PDF documents and ask natural-language questions while receiving **accurate, source-cited answers**.  
It combines **semantic search + LLM reasoning** for fast, reliable document intelligence.

Built with:
- **React + Vite** (Frontend)
- **FastAPI** (Backend)
- **Groq (Llama 3.1 70B)** for lightning-fast inference
- **ChromaDB** for vector similarity search

---

## ✨ Features

### 🎯 Core Capabilities
- **📄 PDF Document Processing**: Upload and process PDFs with intelligent text chunking
- **🧠 AI-Powered Q&A**: Ask natural language questions and get accurate answers
- **🔍 Semantic Search**: Vector-based similarity search using ChromaDB
- **📚 Source Citations**: Every answer includes relevant document excerpts with page numbers
- **💬 Conversation History**: Maintains context across multiple questions
- **⚡ Lightning Fast**: Powered by Groq's ultra-fast LLM inference (500+ tokens/sec)

### 🎨 Modern UI/UX
- **Beautiful React Interface**: Built with Vite, TailwindCSS, and shadcn/ui
- **Responsive Design**: Works seamlessly across devices
- **Real-time Updates**: Live upload progress and query processing
- **Dark Mode Support**: Eye-friendly interface (if implemented)
- **Drag & Drop**: Intuitive document upload experience

### 🛠️ Technical Excellence
- **Production-Ready**: Comprehensive error handling and validation
- **Scalable Architecture**: Modular, maintainable codebase
- **API Documentation**: Auto-generated Swagger/OpenAPI docs
- **Type Safety**: Pydantic models for request/response validation
- **Performance Optimized**: Efficient chunking, batching, and caching

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Document    │  │     Chat     │  │   Source     │      │
│  │   Upload     │  │  Interface   │  │  Citations   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (Axios)
┌────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              RAG Engine (Orchestrator)                │   │
│  └──┬────────────┬────────────┬────────────┬───────────┘   │
│     │            │            │            │                │
│  ┌──▼───┐   ┌───▼───┐   ┌───▼────┐   ┌───▼─────┐         │
│  │ PDF  │   │ Groq  │   │Sentence│   │ Chroma  │         │
│  │Proces│   │ API   │   │Transform│   │   DB    │         │
│  │sor   │   │(LLM)  │   │ (Embed)│   │(Vector) │         │
│  └──────┘   └───────┘   └────────┘   └─────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **Groq API Key** ([Get free key](https://console.groq.com/))
- **8GB RAM minimum**
- **2GB free disk space**

### Installation

#### 1️⃣ Clone Repository
```bash
git clone https://github.com/Emart29/rag-document-analyzer.git
cd rag-document-analyzer
```

#### 2️⃣ Setup Backend
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will start on: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

#### 3️⃣ Setup Frontend
```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will start on: **http://localhost:5173**

---

## 📖 Usage

### Upload Documents
1. Click the **Upload** tab in the sidebar
2. Drag & drop a PDF or click **Browse**
3. Wait for processing (10-30 seconds)
4. Document appears in the **Documents** list

### Ask Questions
1. Select documents (optional - searches all if none selected)
2. Type your question in the chat input
3. Press **Enter** or click **Send**
4. Get AI-generated answer with source citations in 2-3 seconds

### Example Questions
```
"What are the main findings of this research?"
"Summarize the key points from page 5"
"Compare the methodologies discussed in the documents"
"What does the author say about machine learning?"
```

---

## 🛠️ Technology Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **Vite** | Build tool & dev server |
| **TailwindCSS** | Styling |
| **shadcn/ui** | UI components |
| **Tanstack Query** | Server state management |
| **Axios** | HTTP client |
| **React Markdown** | Answer rendering |
| **Lucide React** | Icons |

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework |
| **Groq API** | LLM inference (Llama 3.1 70B) |
| **ChromaDB** | Vector database |
| **Sentence Transformers** | Text embeddings |
| **PyPDF2 & pdfplumber** | PDF text extraction |
| **Pydantic** | Data validation |
| **Uvicorn** | ASGI server |

---

## 📊 Performance Metrics

**Tested on:** Dell Latitude 5400 (i5-8th gen, 8GB RAM)

| Operation | Time | Notes |
|-----------|------|-------|
| **Document Upload** | 10-30s | 5-page PDF |
| **Question Answering** | 1-3s | Including retrieval & generation |
| **Semantic Search** | <100ms | ChromaDB query |
| **Memory Usage** | ~600MB | Backend runtime |
| **LLM Inference** | 500+ tokens/sec | Via Groq |

---

## 🚢 Deployment

### Frontend Deployment (Vercel) - FREE ✅

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend folder
cd frontend

# Deploy
vercel

# Follow prompts, set environment variable:
# VITE_API_URL=https://your-backend-url.onrender.com
```

### Backend Deployment (Render.com) - FREE ✅

1. Create `render.yaml` in project root:
```yaml
services:
  - type: web
    name: rag-backend
    env: python
    region: oregon
    plan: free
    buildCommand: |
      cd backend
      pip install -r requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
```

2. Push to GitHub
3. Connect repo to Render.com
4. Add `GROQ_API_KEY` environment variable
5. Deploy!

**Your app will be live at:**
- Frontend: `https://your-app.vercel.app`
- Backend API: `https://your-api.onrender.com`

---

## 📁 Project Structure

```
rag-document-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Pydantic models
│   │   ├── routers/             # API endpoints
│   │   │   ├── documents.py     # Document operations
│   │   │   ├── query.py         # Q&A endpoints
│   │   │   └── system.py        # Health & stats
│   │   ├── services/            # Business logic
│   │   │   ├── rag_engine.py    # RAG orchestration
│   │   │   ├── groq_client.py   # LLM interface
│   │   │   ├── embeddings.py    # Vector generation
│   │   │   └── pdf_processor.py # Document processing
│   │   └── database/
│   │       └── chroma_db.py     # Vector database
│   ├── requirements.txt
│   ├── .env
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── DocumentList.jsx
│   │   │   └── ui/              # shadcn components
│   │   ├── services/
│   │   │   └── api.js           # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── README.md
├── README.md                    # This file
└── LICENSE
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Test individual components
python app/services/groq_client.py
python app/services/embeddings.py
python app/database/chroma_db.py
python app/services/rag_engine.py

# API documentation
# Visit: http://localhost:8000/docs
```

### Frontend Tests
```bash
cd frontend

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 🔒 Security & Best Practices

- ✅ Environment variables for sensitive data
- ✅ Input validation with Pydantic
- ✅ CORS configuration for frontend
- ✅ File size and type validation
- ✅ Error handling and logging
- ✅ API rate limiting (recommended for production)
- ⚠️ Add authentication for production use
- ⚠️ Implement user management for multi-tenant

---

## 🐛 Troubleshooting

### Backend Issues

**Issue:** "GROQ_API_KEY not found"
```bash
# Solution: Check .env file
cat backend/.env  # Should show GROQ_API_KEY=gsk_...
```

**Issue:** ChromaDB errors
```bash
# Solution: Clear database and restart
rm -rf backend/chroma_db/
# Restart backend
```

**Issue:** PDF processing fails
```bash
# Solution: Install additional dependencies
pip install python-magic-bin  # Windows
pip install python-magic       # Mac/Linux
```

### Frontend Issues

**Issue:** API connection refused
```bash
# Solution: Check VITE_API_URL in .env
# Verify backend is running on correct port
```

**Issue:** Build errors
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 🎯 Future Enhancements

- [ ] **Multi-format Support**: Add .docx, .txt, .md support
- [ ] **User Authentication**: JWT-based auth system
- [ ] **Multi-tenancy**: Per-user document isolation
- [ ] **Advanced Filters**: Filter by date, size, type
- [ ] **Export Conversations**: Download chat history
- [ ] **Streaming Responses**: Real-time token streaming
- [ ] **Voice Input**: Speech-to-text for questions
- [ ] **Document Summarization**: Auto-generate summaries
- [ ] **Collaborative Sharing**: Share documents between users
- [ ] **Analytics Dashboard**: Usage statistics and insights

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**

- LinkedIn: [Emmanuel Nwanguma](https://linkedin.com/in/nwangumaemmanuel)
- GitHub: [Emart29](https://github.com/Emart29)

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) - Ultra-fast LLM inference platform
- [ChromaDB](https://www.trychroma.com/) - Open-source embedding database
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Sentence Transformers](https://www.sbert.net/) - State-of-the-art text embeddings
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful React components
- [Vercel](https://vercel.com/) - Frontend hosting platform
- [Render](https://render.com/) - Backend hosting platform

---

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/Emart29/rag-document-analyzer?style=social)
![GitHub forks](https://img.shields.io/github/forks/Emart29/rag-document-analyzer?style=social)
![GitHub issues](https://img.shields.io/github/issues/Emart29/rag-document-analyzer)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Emart29/rag-document-analyzer)

---

<div align="center">

**⭐ If this project helped you, please give it a star! ⭐**

Made with ❤️ by [Emmanuel Nwanguma](https://github.com/Emart29)

[⬆ Back to Top](#-rag-document-analyzer)

</div>
---

## 📈 Project 3: LLM Observability & Monitoring

This project now includes a fully integrated observability layer across the FastAPI backend and React frontend dashboard.

### ✅ Implemented Features

- **Custom Logging for All LLM Calls**
  - Every Groq request is wrapped and logged with prompt input, answer output, timestamps, model, metadata, status, and errors.
- **Prompt & Response Tracking (Persistent DB)**
  - Stored in `llm_request_logs` using SQLAlchemy with SQLite by default (`observability.db`) or PostgreSQL via `OBSERVABILITY_DB_URL`.
- **Token Usage Monitoring**
  - Captures prompt tokens, completion tokens, and total tokens for each LLM call.
- **Cost per Query Calculation**
  - Uses configurable per-1K token rates:
    - `GROQ_INPUT_TOKEN_COST_PER_1K`
    - `GROQ_OUTPUT_TOKEN_COST_PER_1K`
- **Latency Tracking**
  - Measures and stores per-request LLM latency in milliseconds.
- **Prompt Versioning**
  - Prompt templates are versioned in `prompt_templates` with active/inactive states for auditability and experimentation.
- **Dashboard Visualization (React)**
  - New Observability tab visualizes:
    - total queries
    - total tokens
    - total cost
    - average latency
    - daily trends
    - active prompt templates
    - recent LLM request logs

### 🗂️ Observability API Endpoints

- `GET /observability/metrics?window_hours=24`
- `GET /observability/logs?limit=50`
- `GET /observability/prompts`
- `POST /observability/prompts`

### ⚙️ Environment Variables

Add these to `backend/.env`:

```bash
# Observability database (SQLite default)
OBSERVABILITY_DB_URL=sqlite:///./observability.db

# Optional: PostgreSQL example
# OBSERVABILITY_DB_URL=postgresql+psycopg2://user:password@localhost:5432/rag_observability

# Cost model (USD per 1000 tokens)
GROQ_INPUT_TOKEN_COST_PER_1K=0.00059
GROQ_OUTPUT_TOKEN_COST_PER_1K=0.00079
```

### 🧩 Code Structure Added for Project 3

```text
backend/app/
├── database/
│   └── observability_db.py          # SQLAlchemy engine + tables
├── services/
│   └── observability_service.py     # logging, metrics, prompt versions
├── routers/
│   └── observability.py             # observability REST endpoints
├── services/groq_client.py          # wrapped LLM calls + observability capture
└── models.py                        # observability response models

frontend/src/
├── components/
│   └── ObservabilityDashboard.jsx   # metrics dashboard UI
├── services/
│   └── api.js                       # observability API methods
└── App.jsx                          # Chat + Observability tabs
```

### ▶️ How to Run Project 3 End-to-End

1. Start backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Start frontend:
```bash
cd frontend
npm install
npm run dev
```

3. Use the app:
- Upload a PDF
- Ask questions in Chat
- Open the **Observability** tab to see metrics and request logs in real time

### 🎯 Benefits

- Better production debugging and reliability
- Cost and token transparency per query
- Prompt governance and audit history
- Easier performance optimization through latency and usage trends

### 📣 Suggested Social Media Lines

- "Just shipped full LLM observability in my RAG Document Analyzer: token tracking, query cost, latency metrics, prompt versioning, and a live dashboard. #LLMOps #RAG #FastAPI #React"
- "Project 3 complete ✅ Added production-grade monitoring to a RAG app with Groq + ChromaDB: logs, usage analytics, prompt audits, and metrics dashboard. #GenAI #MLOps"
- "From prototype to production: integrated end-to-end LLM monitoring (prompts, responses, tokens, cost, latency) into our document Q&A platform. #LLMObservability"
