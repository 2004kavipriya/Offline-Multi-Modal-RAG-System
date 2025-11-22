# Multimodal RAG System - Backend

Backend for the Multimodal RAG system using **FAISS + PostgreSQL + MinIO** architecture.

## Architecture

- **FAISS**: Fast vector similarity search for embeddings
- **PostgreSQL**: Metadata and document information storage
- **MinIO**: Object storage for uploaded files
- **FastAPI**: REST API framework

## Features

- **Document Processing**: PDF, DOCX, images (OCR), and audio (speech-to-text)
- **Semantic Search**: Cross-modal search using FAISS
- **RAG Queries**: Natural language queries with LLM-generated answers
- **Citations**: Automatic citation tracking with source references

## Prerequisites

- Python 3.10+
- Docker & Docker Compose (for PostgreSQL and MinIO)
- Tesseract OCR
- Ollama (for LLM)

## Setup

### 1. Start PostgreSQL and MinIO

```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- MinIO on port 9000 (API) and 9001 (Console)

Access MinIO Console: http://localhost:9001 (minioadmin/minioadmin)

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR

Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

### 5. Install Ollama and Download LLM

```bash
# Install Ollama from https://ollama.ai

# Pull a model
ollama pull llama2
```

### 6. Configure Environment

Edit `.env` file if needed (default values should work with docker-compose).

## Running the Server

```bash
# Activate virtual environment
venv\Scripts\activate

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## API Endpoints

### Upload
- `POST /api/upload/` - Upload a single file
- `POST /api/upload/batch` - Upload multiple files

### Search
- `POST /api/search/` - Semantic search
- `POST /api/search/cross-modal` - Cross-modal search (text-to-image)

### Query
- `POST /api/query/` - RAG query with LLM response
- `GET /api/query/health` - Check LLM availability

### Health
- `GET /health` - System health check
- `GET /` - Root endpoint

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── models/              # Data models & database
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── database.py      # SQLAlchemy models
│   │   └── db_session.py    # Database session
│   ├── processors/          # Document processors
│   ├── embeddings/          # Embedding generators
│   ├── vectorstore/         # FAISS + MinIO
│   │   ├── faiss_store.py   # FAISS vector store
│   │   └── minio_storage.py # MinIO client
│   ├── llm/                 # LLM integration
│   ├── api/                 # API endpoints
│   └── utils/               # Utilities
├── data/
│   └── faiss_indexes/       # FAISS index files
├── docker-compose.yml       # PostgreSQL + MinIO
├── requirements.txt
└── .env
```

## Database Schema

### Documents Table
- Stores document metadata
- Links to MinIO file paths

### DocumentChunks Table
- Text chunks with embeddings
- References to FAISS indices
- Page numbers and timestamps

### ImageEmbeddings Table
- Image-specific embeddings
- OCR text and confidence scores

## Models Used

- **Text Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (384 dim)
- **Image Embeddings**: openai/clip-vit-base-patch32 (512 dim)
- **Speech-to-Text**: OpenAI Whisper (base)
- **LLM**: llama2 (via Ollama)

## Development

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Stopping Services

```bash
docker-compose down
```

### Viewing Logs

```bash
docker-compose logs -f postgres
docker-compose logs -f minio
```

## Notes

- All models run locally (offline mode)
- First run will download models automatically
- GPU is recommended but not required
- FAISS indices are saved to disk for persistence
