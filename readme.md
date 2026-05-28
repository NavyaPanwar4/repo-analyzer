# 🚀 Repo Analyzer

> Understand any codebase instantly.

An AI-powered developer tool that lets you explore, analyze, and query any GitHub repository using natural language — without reading a single file manually.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6B35?style=flat-square)](https://trychroma.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3-F55036?style=flat-square)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## 📌 Overview

Repo Analyzer is a full-stack AI system designed to eliminate the friction of onboarding into unfamiliar codebases.

Instead of manually reading dozens of files, you can:

- Ask questions in plain English
- Visualize file architecture and dependencies
- Detect bugs and code smells automatically

It combines **AST parsing**, **dependency graphs**, **vector search**, and **LLM reasoning** to give accurate, context-aware answers grounded in real source code.

---

## ✨ Key Features

### 🔍 Intelligent Code Understanding
- AST-based parsing using **tree-sitter**
- Extracts functions, classes, and imports with line-level precision
- Supports Python, JavaScript, TypeScript, Java, Rust, C/C++
- Fallback to raw text parsing for HTML, CSS, Markdown, JSON, YAML

### 🧠 AI-Powered Q&A (RAG Pipeline)
- Semantic search using **ChromaDB** vector store
- Context-aware answers using **LLaMA 3** via Groq
- Source-backed responses — every answer shows the exact code chunks used
- Intent detection tailors prompts for architecture, bug, security, and function queries

### 🕸️ Dependency Graph Visualization
- Built with **NetworkX** + **React Flow**
- Interactive graph of file import relationships
- Identifies:
  - Hub files (most depended on)
  - Isolated modules
  - Cross-module dependencies
- Click any node to ask the AI about that specific file

### 🐛 Built-in Bug Detection
- Static analysis with 11 custom rules — no external linter needed
- Detects:
  - Hardcoded secrets and credentials
  - Poor practices (bare except, mutable defaults, loose equality)
  - Debug leftovers (print statements, console.log)
  - Unresolved TODO/FIXME comments
- AI-generated explanations and fix suggestions per finding

### 📦 Flexible Input
- Analyze via:
  - **GitHub URL** — paste any public repo link
  - **ZIP upload** — upload a local project archive

---

## 🏗️ Tech Stack

### Frontend
| Library | Purpose |
|---|---|
| React + Vite | UI framework and build tool |
| React Flow | Interactive dependency graph |
| React Router | Client-side routing |
| Axios | HTTP client |
| react-syntax-highlighter | Code chunk display |

### Backend
| Library | Purpose |
|---|---|
| FastAPI | REST API framework |
| tree-sitter | AST parsing (multi-language) |
| NetworkX | Dependency graph construction |
| GitPython | Remote repo cloning |

### AI / Data
| Library | Purpose |
|---|---|
| ChromaDB | Local vector store |
| sentence-transformers | Local embeddings (no API key needed) |
| Groq API | LLM inference (LLaMA 3) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- A free Groq API key → [console.groq.com](https://console.groq.com)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/repo-analyzer.git
cd repo-analyzer
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Linux / macOS
# venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

Create `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Run the server:

```bash
uvicorn app.main:app --reload --port 8000
```

Verify:

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

---

## 🧠 How It Works

### 1. Ingestion Pipeline

```
GitHub URL / ZIP
      ↓
  Clone or extract repo
      ↓
  Walk files (filter by extension, skip noise)
      ↓
  tree-sitter AST parsing
  → Functions, classes, imports extracted per file
      ↓
  NetworkX dependency graph
  → Import relationships resolved between files
      ↓
  Smart chunking
  → One chunk per function / class / import block
      ↓
  sentence-transformers embeddings (local)
      ↓
  ChromaDB vector store
      ↓
  Static bug detection
```

### 2. Query Pipeline

```
User question
      ↓
  Embed question (same local model)
      ↓
  ChromaDB similarity search → top-8 chunks
      ↓
  Intent detection (architecture / bug / security / function)
      ↓
  LLM prompt built with context + repo summary
      ↓
  Groq LLaMA 3 generates answer
      ↓
  Answer + source chunks returned to frontend
```

---

## 🗂️ Project Structure

```
repo-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── routes/
│   │   │   ├── ingest.py            # /ingest/url  /ingest/zip  /ingest/debug
│   │   │   └── ask.py               # /ask  /bugs/explain
│   │   └── services/
│   │       ├── ingestion.py         # Clone, extract, file walker
│   │       ├── parser.py            # tree-sitter AST parsing
│   │       ├── graph.py             # NetworkX graph builder
│   │       ├── chunker.py           # Chunking strategy
│   │       ├── embedder.py          # Local sentence-transformers
│   │       ├── vector_store.py      # ChromaDB storage + retrieval
│   │       ├── llm.py               # Groq LLM + prompt builder
│   │       └── bug_detector.py      # Static analysis heuristics
│   ├── requirements.txt
│   └── .env
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Home.jsx             # Repo input (URL or ZIP)
    │   │   └── Chat.jsx             # Chat / Graph / Bugs tabs
    │   ├── components/
    │   │   ├── ChatMessage.jsx      # Message bubbles + source chunks
    │   │   ├── GraphView.jsx        # React Flow graph
    │   │   └── BugPanel.jsx         # Bug findings + AI explain
    │   └── api/
    │       └── client.js            # Axios → localhost:8000
    └── package.json
```

---

## 📊 Example Use Cases

| Use Case | How |
|---|---|
| 🔎 Understand a new codebase in minutes | Ask "What does this project do?" and "Where is the main entry point?" |
| 🐛 Detect bugs without running code | Open the Bugs tab after ingestion for instant static analysis |
| 📚 Learn how a feature is implemented | Ask "How is authentication handled?" or "Where is X called?" |
| 🏗️ Visualize architecture instantly | Switch to the Graph tab and explore the dependency map |
| 🔐 Audit for security issues | Ask "Are there any hardcoded secrets or security vulnerabilities?" |

---

## 🛠️ API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/ingest/url` | Clone and index a GitHub repo by URL |
| `POST` | `/api/ingest/zip` | Upload and index a local ZIP file |
| `POST` | `/api/ingest/debug` | List files that would be parsed (dry run) |
| `POST` | `/api/ask` | Ask a question about an indexed repo |
| `POST` | `/api/bugs/explain` | Get AI summary of bug findings |
| `GET` | `/health` | Health check |

### Example: ingest a repo

```bash
curl -X POST http://localhost:8000/api/ingest/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/realpython/flask-boilerplate"}'
```

### Example: ask a question

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "repo_id": "a3f9c12b4e01",
    "question": "Where is routing handled?"
  }'
```

---

## 🐛 Bug Detection Rules

| Rule | Language | Severity |
|---|---|---|
| `hardcoded-secret` | Python, JS | 🔴 Error |
| `mutable-default-arg` | Python | 🔴 Error |
| `bare-except` | Python | 🟡 Warning |
| `none-comparison` | Python | 🟡 Warning |
| `long-function` | Python | 🟡 Warning |
| `loose-equality` | JavaScript | 🟡 Warning |
| `no-var` | JavaScript | 🟡 Warning |
| `print-statement` | Python | 🔵 Info |
| `console-log` | JavaScript | 🔵 Info |
| `todo-comment` | All | 🔵 Info |
| `long-line` | All | 🔵 Info |

---

## ⚙️ Configuration

```env
# backend/.env
GROQ_API_KEY=your_key_here
```

- **Embeddings** run fully locally using `all-MiniLM-L6-v2` — no API key needed, ~90MB download on first run
- **Vector DB** stored locally in `backend/chroma_db/` — one collection per repo
- **LLM model** can be changed in `backend/app/services/llm.py`:

```python
MODEL = "llama3-8b-8192"        # Default: fast and free
# MODEL = "llama3-70b-8192"     # Higher quality
# MODEL = "mixtral-8x7b-32768"  # Larger context window
```

---

## 🔧 Troubleshooting

**Only one file found when ingesting**
Use the debug endpoint to check which files are being picked up:
```bash
curl -X POST http://localhost:8000/api/ingest/debug \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/your/repo"}'
```

**tree-sitter import errors**
Install language grammars manually:
```bash
pip install tree-sitter-python tree-sitter-javascript \
            tree-sitter-typescript tree-sitter-java \
            tree-sitter-rust tree-sitter-cpp
```

**CORS errors in browser**
Make sure backend runs on port `8000` and frontend on `3000`. If you change either port, update `allow_origins` in `backend/app/main.py` and `baseURL` in `frontend/src/api/client.js`.

**Groq rate limit errors**
Reduce context size by changing `n_results=8` to `n_results=4` in `backend/app/services/vector_store.py`.

---

## 📄 License

MIT License © 2025
