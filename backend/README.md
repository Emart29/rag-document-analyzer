# 🚀 RAG Document Analyzer - Backend API

Production-ready FastAPI backend for RAG-powered document question answering.

## 🌟 Features

- **PDF Document Processing**: Upload and process PDF documents with intelligent chunking
- **Semantic Search**: Vector-based similarity search using ChromaDB
- **Question Answering**: GPT-4 class performance with Groq's Llama 3.1 70B
- **Source Citations**: Every answer includes relevant document sources
- **Conversation History**: Maintains context across multiple questions
- **RESTful API**: Well-documented endpoints with Swagger UI
- **Production Ready**: Error handling, logging, validation

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   FastAPI REST API                  │
│   - Document Upload                 │
│   - Question Answering              │
│   - System Management               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   RAG Engine (Orchestrator)         │
│   - Coordinates all components      │
│   - Manages workflow                │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┬──────────┬──────────┐
        │             │          │          │
┌───────▼─────┐ ┌────▼────┐ ┌───▼────┐ ┌───▼────────┐
│ PDF         │ │Groq API │ │Sentence│ │  ChromaDB  │
│ Processor   │ │(LLM)    │ │Transformers│ │(Vector DB)│
└─────────────┘ └─────────┘ └────────┘ └────────────┘
```

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | FastAPI | REST API framework |
| **LLM** | Groq (Llama 3.1 70B) | Answer generation |
| **Embeddings** | Sentence Transformers | Text vectorization |
| **Vector DB** | ChromaDB | Semantic search |
| **PDF Processing** | PyPDF2, pdfplumber | Text extraction |
| **Validation** | Pydantic | Request/response models |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API key ([Get one free](https://console.groq.com/))
- 8GB RAM minimum
- 2GB free disk space

### Installation

1. **Clone and navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your Groq API key
GROQ_API_KEY=your_key_here
```

5. **Run the server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access API documentation:**
```
http://localhost:8000/docs
```

## 📡 API Endpoints

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/documents/upload` | Upload PDF document |
| `GET` | `/documents/list` | List all documents |
| `GET` | `/documents/{id}` | Get document details |
| `DELETE` | `/documents/{id}` | Delete document |

### Query

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/query/ask` | Ask question about documents |
| `GET` | `/query/conversation/{id}` | Get conversation history |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/system/health` | Health check |
| `GET` | `/system/stats` | System statistics |
| `GET` | `/system/info` | System information |

## 💡 Usage Examples

### Upload a Document

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"
```

### Ask a Question

```bash
curl -X POST "http://localhost:8000/query/ask" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main findings?",
    "document_ids": null,
    "conversation_id": null
  }'
```

### Get System Stats

```bash
curl -X GET "http://localhost:8000/system/stats"
```

## 🔧 Configuration

Edit `.env` file to customize:

```env
# Groq API
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-70b-versatile

# Chunking
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Retrieval
TOP_K_RESULTS=5

# File Upload
MAX_FILE_SIZE_MB=10
```

## 📊 Performance

**Tested on:** Dell Latitude 5400 (i5-8th gen, 8GB RAM)

- **Document Upload**: 10-30 seconds (depends on PDF size)
- **Question Answering**: 1-3 seconds
- **Memory Usage**: ~600MB
- **Concurrent Requests**: Supports multiple users

## 🧪 Testing

### Run Tests
```bash
# Test individual components
python app/services/groq_client.py
python app/services/embeddings.py
python app/database/chroma_db.py
python app/services/rag_engine.py

# Test via Swagger UI
# Navigate to http://localhost:8000/docs
```

### Create Test PDF
```bash
python create_test_pdf.py
```

## 🐳 Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t rag-backend .
docker run -p 8000:8000 --env-file .env rag-backend
```

## 🚀 Deployment

### Render.com (Recommended for Free Hosting)

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: rag-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
```

2. Connect GitHub repo to Render
3. Add environment variables
4. Deploy!

### Railway.app

```bash
railway login
railway init
railway up
```

## 🔒 Security Notes

- ⚠️ Never commit `.env` file
- ⚠️ Use environment variables for API keys
- ⚠️ Implement rate limiting in production
- ⚠️ Add authentication for sensitive deployments
- ⚠️ Validate and sanitize all inputs

## 🐛 Troubleshooting

### Issue: "GROQ_API_KEY not found"
**Solution:** Check `.env` file exists and contains valid API key

### Issue: ChromaDB connection errors
**Solution:** Ensure `chroma_db/` directory has write permissions

### Issue: PDF processing fails
**Solution:** Check PDF is not corrupted or password-protected

### Issue: Out of memory errors
**Solution:** Reduce `CHUNK_SIZE` or process smaller documents

## 📈 Monitoring

```python
# Check system health
GET /system/health

# Response
{
  "status": "healthy",
  "groq_api_status": "healthy",
  "chromadb_status": "healthy",
  "embedding_model_loaded": true
}
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file

## 👤 Author

**Your Name**
- GitHub: [Emart29](https://github.com/Emart29)
- LinkedIn: [Emmanuel Nwanguma](https://linkedin.com/in/nwangumaemmanuel)

## 🙏 Acknowledgments

- [Groq](https://groq.com/) - Ultra-fast LLM inference
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Modern API framework
- [Sentence Transformers](https://www.sbert.net/) - Text embeddings

---

⭐ **Star this repo if you find it helpful!**