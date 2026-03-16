# Agentic Automation Studio

A production-grade AI workflow automation platform that runs locally using open-source models.

## Features

- 🤖 Autonomous AI Agents (Research, Analyst, Writer)
- 🔄 Visual Workflow Builder
- 🧠 Vector Memory with Semantic Search
- ⚡ Event-driven Automation
- 💰 100% Free (No API costs)
- 🔒 Complete Data Privacy

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Ollama with models: `deepseek-coder`, `nomic-embed-text`

### Installation

1. **Backend Setup**
```bash
cd backend
python -m venv venv
venv\Scripts\Activate
pip install -r requirements.txt
```

2. **Frontend Setup**
```bash
cd frontend
npm install
```

3. **Start Services**
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\Activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Access
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, ChromaDB, Ollama  
**Frontend:** Next.js, React, TailwindCSS  
**AI:** Local LLMs (DeepSeek, Mistral)  
**Database:** SQLite (PostgreSQL optional)

## License

MIT
