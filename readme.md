Repo Analyzer

Understand any codebase instantly.
An AI-powered developer tool that lets you explore, analyze, and query any repository using natural language.

📌 Overview

Repo Analyzer is a full-stack AI system designed to eliminate the friction of onboarding into unfamiliar codebases.

Instead of manually reading dozens of files, you can:

Ask questions in plain English
Visualize architecture
Detect bugs automatically

It combines AST parsing, dependency graphs, vector search, and LLM reasoning to give accurate, context-aware answers grounded in real code.

✨ Key Features
🔍 Intelligent Code Understanding
AST-based parsing using tree-sitter
Extracts functions, classes, and imports with precision
Supports multiple languages + fallback to raw text parsing
🧠 AI-Powered Q&A (RAG)
Semantic search using ChromaDB
Context-aware answers using LLaMA 3 via Groq
Source-backed responses (no hallucination guessing)
🕸️ Dependency Graph Visualization
Built with NetworkX + React Flow
Interactive graph of file relationships
Identify:
Hub files
Isolated modules
Cross-dependencies
🐛 Built-in Bug Detection
Static analysis with custom rules
Detects:
Hardcoded secrets
Poor practices
Debug leftovers
AI-generated explanations & fixes
📦 Flexible Input
Analyze via:
GitHub URL
ZIP upload
🏗️ Tech Stack

Frontend

React (Vite)
React Flow

Backend

FastAPI
Tree-sitter
NetworkX

AI / Data

ChromaDB (Vector DB)
Sentence Transformers (Embeddings)
Groq API (LLaMA 3)
🚀 Getting Started
1. Clone the repository
git clone https://github.com/YOUR_USERNAME/repo-analyzer.git
cd repo-analyzer
2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt

Create .env:

GROQ_API_KEY=your_api_key

Run server:

uvicorn app.main:app --reload
3. Frontend setup
cd frontend
npm install
npm run dev

Open 👉 http://localhost:3000

🧠 How It Works
Ingestion
Clone repo / extract ZIP
Parse files using AST
Build dependency graph
Generate embeddings
Query Pipeline
Convert question → embedding
Retrieve relevant code chunks
Send context to LLM
Return structured answer
📊 Example Use Cases
🔎 Understand a new codebase in minutes
🐛 Detect bugs without running code
📚 Learn how a feature is implemented
🏗️ Visualize architecture instantly
🛠️ API Endpoints
Endpoint	Description
/api/ingest/url	Analyze GitHub repo
/api/ingest/zip	Upload local project
/api/ask	Ask questions
/api/bugs/explain	AI bug explanations
⚙️ Configuration
GROQ_API_KEY=your_key
Embeddings run locally (no external API)
Vector DB stored in chroma_db/
🗺️ Roadmap

Multi-language expansion (Go, Ruby, PHP)

Offline mode (Ollama)

GitHub PR integration

Docker deployment

Persistent repo history

🤝 Contributing

Contributions are welcome!

git checkout -b feature/your-feature
git commit -m "feat: add feature"
git push origin feature/your-feature
📄 License

MIT License