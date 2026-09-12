<div align="center">

# OmniDoc: Grounded Enterprise Document Intelligence Platform

**High-precision, auditable, and production-ready Retrieval-Augmented Generation (RAG) platform over private enterprise documents.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.112-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Angular](https://img.shields.io/badge/Angular-18.2-DD0031.svg?logo=angular&logoColor=white)](https://angular.dev)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-FF6F00.svg)](https://www.trychroma.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## Table of Contents
- [About OmniDoc](#about-omnidoc)
- [Key Features & Use Cases](#key-features--use-cases)
- [Architecture & Technology Stack](#architecture--technology-stack)
- [Prerequisites](#prerequisites)
- [Quick Start via Docker (Recommended)](#quick-start-via-docker-recommended)
- [Local Bare-Metal Setup (Without Docker)](#local-bare-metal-setup-without-docker)
  - [1. PostgreSQL Setup & Database Integration](#1-postgresql-setup--database-integration)
  - [2. Database Migrations (Alembic)](#2-database-migrations-alembic)
  - [3. Running the Backend (FastAPI)](#3-running-the-backend-fastapi)
  - [4. Running the Frontend (Angular 18)](#4-running-the-frontend-angular-18)
- [How to Add a User via Swagger UI (/docs)](#how-to-add-a-user-via-swagger-ui-docs)
- [Using OmniDoc (Upload, Indexing & Chat)](#using-omnidoc-upload-indexing--chat)
- [Project Directory Structure](#project-directory-structure)
- [Troubleshooting & FAQs](#troubleshooting--faqs)

---

## About OmniDoc

Standard Generative AI models hallucinate, lack private organizational knowledge, and cannot provide verifiable citations. Traditional vector-only RAG systems frequently fail on proper nouns, alphanumeric codes, and similarly structured files (e.g., confusing different employee resumes or project proposals).

**OmniDoc** solves enterprise document discovery through an auditable, multi-stage hybrid intelligence pipeline:
- **Dual Ingestion**: Simultaneously indexes documents into dense vector embeddings (**ChromaDB**) for conceptual semantics and an inverted frequency index (**BM25**) for exact lexical matches.
- **Neural Cross-Encoder Reranking**: Re-evaluates candidate passages through deep token-to-token cross-attention (`ms-marco-MiniLM-L-6-v2`), separating authentic answers from vocabulary overlap and achieving **100% Precision@3**.
- **Synchronized 5-Step Atomic Purge**: Deleting a document purges database records, local storage, vector collections, and BM25 memory simultaneously—eliminating "ghost citations" and ensuring GDPR compliance.
- **Modern Angular 18 Signal UI**: Delivers real-time Server-Sent Events (SSE) token streaming, multi-stage animated AI thinking status, and collapsible bottom-aligned source citation cards with verified percentage match scores.

---

## Key Features & Use Cases

### Core Capabilities
- **Multi-Format Ingestion**: Upload PDF, DOCX, TXT, or Markdown documents with automatic background indexing.
- **Streaming SSE Chat**: Real-time generative chat with animated pre-stream shimmer indicators (`"Searching knowledge base..."` $\to$ `"Analyzing relevant passages..."` $\to$ `"Synthesizing answer..."`).
- **Verifiable Inline Citations**: Grounding source pills display filename, aggregated page lists (e.g., `p. 1, 2`), and peak match scores (`96% Match`), expanding to display the original chunk excerpts.
- **Strict Query Scoping**: Prevents multi-turn conversational context from polluting retrieval queries while preserving memory in the LLM generation prompt.
- **Full LLMOps Telemetry**: Native integration with **Langfuse v4** for distributed tracing, token accounting, latency analysis, and audit logging.

### Enterprise Use Cases
1. **Internal SOP & Corporate Policy Assistant**: Rapidly query onboarding handbooks, HR regulations, and compliance guidelines with page-level verification.
2. **Technical Architecture & Runbook Exploration**: Search system designs, error logs, and infrastructure runbooks without vocabulary mismatch.
3. **Talent & Profile Disambiguation**: Search candidate profiles and resumes where cross-attention eliminates false positives between candidates sharing identical skillsets.
4. **Legal & Contract Clause Auditing**: Pinpoint indemnity terms, non-disclosure expiration dates, and SLA commitments with exact citations.

---

## Architecture & Technology Stack

```
                                  OMNIDOC ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  Angular 18 Frontend  ◄─── Server-Sent Events ────►  FastAPI Backend Core              │
│  (Signals, Tailwind,                              (Clean Architecture: Domain,        │
│   Collapsible Citations)                           Application, Infrastructure,        │
│                                                    Delivery)                           │
│                                                              │                         │
│                                          ┌───────────────────┴───────────────────┐     │
│                                          ▼                                       ▼     │
│                                 [ Ingestion Pipeline ]                 [ Retrieval Pipeline ] │
│                                 • PDF / DOCX Extractor                 • ChromaDB (Dense)    │
│                                 • 512-Token Chunking                   • BM25 (Lexical)      │
│                                 • 64-Token Overlap                     • Reciprocal Rank     │
│                                          │                               Fusion (RRF)        │
│                                          ▼                               • Cross-Encoder     │
│                                 PostgreSQL 16 Storage                    Reranker (MiniLM)   │
│                                 ChromaDB Vector Store                            │           │
│                                 BM25 Inverted Index                              ▼           │
│                                                                        Streaming LLM +       │
│                                                                        Langfuse Telemetry    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

| Layer | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | Angular 18 (Standalone, Signals) + Tailwind CSS | Reactive client, SSE stream reader, collapsible grounding cards. |
| **Backend** | FastAPI + Python 3.12 | Asynchronous REST & SSE streaming API enforcing Clean Architecture. |
| **Relational DB** | PostgreSQL 16 | Stores users, conversations, messages, and document audit records. |
| **ORM & Migrations** | SQLAlchemy 2.0 Async + Alembic | Asynchronous database operations and versioned schema migrations. |
| **Vector Store** | ChromaDB (Persistent) | Dense vector storage with metadata filtering. |
| **Lexical Engine** | Rank-BM25 | In-memory tokenized frequency index for exact keyword matching. |
| **Neural Reranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Deep cross-attention reranking producing calibrated percentage confidence. |
| **LLM Provider** | OpenAI (`gpt-4o-mini`) / Google Gemini | Generative answer synthesis over retrieved context passages. |
| **Observability** | Langfuse v4 | Full-lifecycle distributed tracing, latency profiling, and token cost tracking. |

---

## Prerequisites

Before running OmniDoc, ensure you have the following installed on your machine:
- **Git**: Version 2.30+
- **Docker & Docker Compose** (for containerized mode): Docker Engine 24.0+ / Docker Desktop
- **Python 3.10+** (recommended **Python 3.12**; for bare-metal mode) with `uv` or `pip`
- **Node.js 18+** and **npm** (for bare-metal frontend mode)
- **OpenAI API Key**: Required for conversational answer synthesis (`sk-...`)

---

## Quick Start via Docker (Recommended)

The easiest and fastest way to launch the entire OmniDoc ecosystem (PostgreSQL, Backend, Frontend, and optional Cloudflare tunnel) is via Docker Compose.

### Step 1: Clone the Repository
```bash
git clone https://github.com/vivekks1293/enterprise-ai-platform.git
cd enterprise-ai-platform
```

### Step 2: Configure Environment Variables
Copy the example environment configuration:
```bash
cp apps/backend/.env.example apps/backend/.env
```
Open `apps/backend/.env` in your editor and add your OpenAI API key:
```ini
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key
```

### Step 3: Start All Services
Run Docker Compose from the root directory:
```bash
docker compose up -d --build
```

This will automatically provision:
- `enterprise-ai-postgres`: PostgreSQL 16 on port `5432` with automatic health checks.
- `enterprise-ai-backend`: FastAPI application on port `8000` with volume persistence for ChromaDB, BM25, and uploaded files.
- `enterprise-ai-frontend`: Angular 18 Nginx production container on port `80`.

### Step 4: Access the Application
- **OmniDoc Web Application**: [http://localhost](http://localhost)
- **FastAPI Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Endpoint**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

*(Next, proceed to [How to Add a User via Swagger UI](#how-to-add-a-user-via-swagger-ui-docs) to create your initial login credentials).*

---

## Local Bare-Metal Setup (Without Docker)

If you prefer to run the backend and frontend locally for development, follow the step-by-step instructions below.

### 1. PostgreSQL Setup & Database Integration
OmniDoc requires a running PostgreSQL 16 instance with an active database named `enterprise_ai`.

You can spin up just the database using Docker:
```bash
docker run --name enterprise-ai-postgres \
  -e POSTGRES_DB=enterprise_ai \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:16-alpine
```

Or configure your existing local PostgreSQL instance:
```sql
CREATE DATABASE enterprise_ai;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE enterprise_ai TO postgres;
```

### 2. Database Migrations (Alembic)
OmniDoc manages its relational schema using Alembic. Run migrations to initialize all tables:

```bash
cd apps/backend

# Using uv (recommended for ultra-fast dependency management)
uv run alembic upgrade head

# OR using standard python virtual environment
alembic upgrade head
```

This creates the required tables:
- `users`: User identity and role definitions.
- `conversations`: Chat sessions.
- `messages`: Individual user and assistant dialogue turns.
- `documents`: Document metadata, storage coordinates, and indexing status.

### 3. Running the Backend (FastAPI)

1. **Install Dependencies**:
   ```bash
   cd apps/backend
   
   # Using uv
   uv sync
   
   # OR using standard pip
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

2. **Verify Configuration (`apps/backend/.env`)**:
   Ensure `apps/backend/.env` points to your local database:
   ```ini
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/enterprise_ai
   ALEMBIC_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/enterprise_ai
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_CHAT_MODEL=gpt-4o-mini
   JWT_SECRET_KEY=local-dev-secret-key-change-in-production
   ```

3. **Start the FastAPI Server**:
   ```bash
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   The backend will start at `http://localhost:8000`. You can inspect the Swagger API documentation at `http://localhost:8000/docs`.

### 4. Running the Frontend (Angular 18)

1. **Navigate to UI Directory**:
   ```bash
   cd apps/ui
   ```

2. **Install Node Dependencies**:
   ```bash
   npm install
   ```

3. **Start the Development Server**:
   ```bash
   npm start
   # or: npx ng serve --port 4200
   ```

4. **Access the Frontend**:
   Open your browser to [http://localhost:4200](http://localhost:4200). The frontend is pre-configured to communicate with the backend at `http://localhost:8000/api/v1`.

---

## How to Add a User via Swagger UI (/docs)

Before logging into OmniDoc for the first time, you must create a user account. OmniDoc exposes an Identity API in its interactive Swagger documentation.

### Step-by-Step Instructions:

1. Open your browser and navigate to the Swagger UI:
   👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

2. Scroll down to the **Identity** section.

3. Click on the endpoint:  
   **`POST /api/v1/identity/users`** *(Create an application user)*.

4. Click the **"Try it out"** button on the right side.

5. Replace the default request body with one of the following JSON payloads:

#### To Create an Admin User:
```json
{
  "username": "admin@example.com",
  "password": "Password123!",
  "roleType": 0,
  "roleTypeName": "admin"
}
```

#### To Create a Standard User:
```json
{
  "username": "user@example.com",
  "password": "Password123!",
  "roleType": 1,
  "roleTypeName": "user"
}
```

> **Important Field Notes**:
> - `username`: Must be a valid email format (e.g., `name@domain.com`).
> - `password`: Minimum 8 characters, maximum 128 characters.
> - `roleType`: Use integer `0` for Admin, or integer `1` for Standard User.
> - `roleTypeName`: Must match the role type (`"admin"` for 0, `"user"` for 1).

6. Click the large blue **"Execute"** button.

7. **Verify Response**:
   You should receive an **HTTP 201 Created** response code with the user details:
   ```json
   {
     "id": "e4b2d1c9-7a3f-42a1-bf8e-90c12e345678",
     "username": "admin@example.com",
     "name": "",
     "roleType": 0,
     "roleTypeName": "admin"
   }
   ```

8. **Log In to the App**:
   Navigate to the OmniDoc web application at **[http://localhost](http://localhost)** (if using Docker) or **[http://localhost:4200](http://localhost:4200)** (if running bare-metal) and enter the email and password you just created!

---

## Using OmniDoc (Upload, Indexing & Chat)

### 1. Document Management & Automatic Indexing
- Click on the **Documents** link in the navigation bar.
- Drag and drop any **PDF**, **DOCX**, or **TXT** file into the upload dropzone (or click Browse).
- **Zero Redundant Buttons**: OmniDoc automatically parses, chunks (512 tokens with 64-token overlap), embeds into **ChromaDB**, and registers lexical terms into **BM25**.
- Once processed, the document immediately displays a green **`✓ Indexed`** badge.
- You can download the original file or delete it at any time. *(Deleting triggers an atomic 5-step purge that removes vector embeddings and lexical chunks immediately)*.

### 2. Grounded Conversational AI
- Click on the **Chat** link in the navigation bar.
- Type any question regarding your uploaded enterprise documents.
- **Thinking Shimmer**: While OmniDoc performs parallel dual retrieval, reciprocal rank fusion, and neural cross-encoder reranking, a sleek animated thinking indicator displays real-time progress.
- **Token-by-Token Streaming**: The answer streams smoothly with a live cursor.
- **Collapsible Grounding Cards**: At the bottom of the answer, click on any document source chip to expand and review the exact page numbers, neural confidence scores (e.g., `96% Match`), and original text excerpts used to answer the question.
- **Query History**: The left sidebar automatically saves your conversations. You can switch between chats or click the Refresh button to sync with the server.

---

## Project Directory Structure

```
enterprise-ai-platform/
├── apps/
│   ├── backend/                     # FastAPI Python 3.12 Backend Core
│   │   ├── app/
│   │   │   ├── domain/              # Clean Architecture: Pure business entities (User, Document, Chunk)
│   │   │   ├── application/         # Use cases, ports, orchestrator, retrieval query builder
│   │   │   ├── infrastructure/      # ChromaDB, BM25, PostgreSQL SQLAlchemy, MinIO, Langfuse
│   │   │   ├── delivery/            # FastAPI REST & SSE routers, Pydantic schemas, dependency injection
│   │   │   └── main.py              # Application entrypoint & middleware configuration
│   │   ├── migrations/              # Alembic versioned database migrations
│   │   ├── pyproject.toml           # Project dependencies & tool configurations
│   │   └── Dockerfile               # Backend container specification
│   │
│   └── ui/                          # Angular 18 Standalone Reactive Frontend
│       ├── src/
│       │   ├── app/
│       │   │   ├── features/        # Chat & Documents domain modules
│       │   │   ├── data/            # Repositories & DTO models
│       │   │   └── core/            # Auth guards, HTTP interceptors, streaming client
│       │   └── index.html           # Single-page shell with custom gradient favicon
│       ├── package.json             # NPM dependencies & scripts
│       └── Dockerfile               # Multi-stage Angular build + Nginx production server
│
├── docs/                            # Architectural specifications & Capstone documentation
│   ├── CAPSTONE_PROJECT_REPORT.md   # Comprehensive 16-18 page master report
│   └── OMNIDOC_CAPSTONE_PROJECT_REPORT.docx # Formatted Microsoft Word submission report
│
├── scripts/                         # Maintenance & document conversion utilities
│   └── convert_report.py            # Automated Markdown-to-DOCX styling compiler
│
├── docker-compose.yml               # Multi-container orchestration topology
└── README.md                        # Master project documentation
```

---

## Troubleshooting & FAQs

### Q1: I get `Connection refused` when connecting to PostgreSQL.
- **Fix**: Ensure PostgreSQL is running on port `5432`. If using Docker, check `docker ps` to verify `enterprise-ai-postgres` is healthy. When running bare-metal, ensure `DATABASE_URL` in `apps/backend/.env` uses `localhost:5432`, whereas inside Docker Compose it uses `postgres:5432`.

### Q2: Why does the Cross-Encoder take ~100ms on the first query?
- **Fix**: The `ms-marco-MiniLM-L-6-v2` model loads into memory upon the initial request. Subsequent queries execute with warm weights in under 30ms.

### Q3: When I delete a document, will the AI still answer questions about it?
- **Answer**: **No**. OmniDoc's atomic deletion pipeline removes the vector chunks from ChromaDB and the lexical tokens from BM25 simultaneously, guaranteeing zero "ghost citations".

### Q4: How do I rebuild or wipe the ChromaDB vector store?
- **Fix**: ChromaDB stores its persistent collections in `apps/backend/data/chroma`. To perform a clean reset, stop the backend and remove the directory:
  ```bash
  rm -rf apps/backend/data/chroma apps/backend/data/bm25
  ```

---

<div align="center">
  <sub>Built with ❤️ for enterprise-grade, auditable document intelligence.</sub>
</div>

