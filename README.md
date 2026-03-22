# 📜 DocDigitizer — दस्तावेज़ डिजिटाइज़र

A full-stack web application for **digitizing, processing, and searching old government documents** in Devanagari (Hindi/Marathi) using OCR.

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────────────┐     ┌──────────┐
│   React +   │────▶│   FastAPI Backend    │────▶│PostgreSQL│
│ Tailwind UI │     │                     │     └──────────┘
└─────────────┘     │  ┌───────────────┐  │     ┌──────────┐
                    │  │ OCR Pipeline  │  │────▶│  Elastic  │
                    │  │ OpenCV + Tess │  │     │  Search   │
                    │  └───────────────┘  │     └──────────┘
                    │  ┌───────────────┐  │     ┌──────────┐
                    │  │ JWT Auth +    │  │────▶│  File     │
                    │  │ Role-based    │  │     │ Storage   │
                    │  └───────────────┘  │     └──────────┘
                    └─────────────────────┘
```

## ⚡ Quick Start

### Docker (Recommended)

```bash
# Clone and start all services
docker-compose up --build

# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # Edit configuration
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Prerequisites:**
- PostgreSQL 16+
- Elasticsearch 8.x
- Tesseract OCR with Hindi language pack (`tesseract-ocr-hin`)
- Python 3.11+
- Node.js 20+

## 📋 Features

| Feature | Description |
|---------|-------------|
| 🔐 **Authentication** | JWT-based auth with admin/reviewer/user roles |
| 📤 **Document Upload** | PDF, JPG, PNG, TIFF with metadata |
| 🔍 **OCR Processing** | OpenCV preprocessing → Tesseract (Hindi+English) |
| ✏️ **Text Correction** | Side-by-side editor with version history |
| 🔎 **Full-text Search** | Elasticsearch with fuzzy search & filters |
| 📊 **Admin Dashboard** | Stats, accuracy tracking, user management |
| 🤖 **Feedback Learning** | Export OCR→corrected pairs for model training |
| 🐳 **Dockerized** | Full-stack Docker Compose setup |

## 🗄️ Database Schema

| Table | Purpose |
|-------|---------|
| `users` | Authentication & role management |
| `documents` | Document metadata & file references |
| `ocr_results` | Per-page OCR text & confidence scores |
| `corrections` | Versioned text corrections |
| `keywords` | Auto/manual document tagging |

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login, get JWT |
| POST | `/api/documents/upload` | Upload document |
| GET | `/api/documents/` | List documents |
| POST | `/api/ocr/process/{id}` | Trigger OCR |
| GET | `/api/ocr/results/{id}` | Get OCR results |
| POST | `/api/corrections/{id}` | Submit correction |
| POST | `/api/search/` | Full-text search |
| GET | `/api/admin/stats` | System statistics |
| GET | `/api/admin/feedback-dataset` | Export training data |

Full interactive docs at: `http://localhost:8000/docs`

## 🚀 Deployment

| Component | Option |
|-----------|--------|
| Backend | Docker → AWS ECS / Google Cloud Run |
| Frontend | Vercel / Netlify |
| Database | AWS RDS / Supabase |
| Storage | AWS S3 (configurable in `.env`) |
| Search | Elastic Cloud / AWS OpenSearch |

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── config.py        # Settings
│   │   ├── database.py      # Async SQLAlchemy
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # API routes
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Helpers (security, storage, OCR)
│   │   └── middleware/      # Auth middleware
│   ├── alembic/             # DB migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI
│   │   ├── pages/           # 8 page components
│   │   ├── services/        # API client
│   │   ├── context/         # Auth context
│   │   └── App.jsx          # Router
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 📄 License

MIT
