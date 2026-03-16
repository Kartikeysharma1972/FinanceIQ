# FinanceIQ — AI Personal Finance Analyst Agent

![Tech Stack](https://img.shields.io/badge/LangGraph-Agent-blue?style=flat-square)
![LLM](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-orange?style=flat-square)
![Backend](https://img.shields.io/badge/FastAPI-Python-green?style=flat-square)
![Frontend](https://img.shields.io/badge/React-Tailwind-61DAFB?style=flat-square)
![Charts](https://img.shields.io/badge/Recharts-Visualization-red?style=flat-square)
![Streaming](https://img.shields.io/badge/SSE-Streaming-purple?style=flat-square)
![Free APIs](https://img.shields.io/badge/100%25-Free_APIs-success?style=flat-square)

> Upload your bank statement. Watch AI analyze every transaction in real-time. Get a personalized financial roadmap.

## 🎯 Problem Statement

Managing personal finances is challenging:
- **Manual Analysis is Time-Consuming**: Reviewing hundreds of transactions manually takes hours
- **Hidden Spending Patterns**: Hard to identify where money actually goes
- **Lack of Actionable Insights**: Bank statements show data but not recommendations
- **Budget Planning Requires Expertise**: Creating realistic budgets needs financial knowledge
- **No Personalization**: Generic financial advice doesn't fit individual situations

## 💡 Solution

**FinanceIQ** is an intelligent AI agent that automatically analyzes your bank statements using a 6-node LangGraph pipeline to provide:
- ✅ **Automatic Transaction Categorization** - AI classifies every transaction into 12 categories
- ✅ **Deep Financial Analysis** - Pandas-powered analytics on income, expenses, trends
- ✅ **Personalized Insights** - AI identifies your specific spending patterns and behaviors
- ✅ **Actionable Recommendations** - 5 ranked action items with estimated monthly savings
- ✅ **Budget Planning** - Suggested budget percentages + emergency fund calculator
- ✅ **Beautiful Dashboard** - Interactive charts, tables, and exportable PDF reports

**Key Differentiator**: Uses agentic AI architecture (LangGraph) with self-reflection for quality control, not just simple LLM prompting.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     LangGraph Agent Pipeline                │
│                                                             │
│  [Extraction] → [Categorization] → [Analysis] →            │
│  [Insights]  → [Advice]         → [Reflection] → [Report]  │
└─────────────────────────────────────────────────────────────┘
         │                                        │
   FastAPI Backend                         React Frontend
   (SSE Streaming)                    (Live Pipeline View)
         │                                        │
    Groq API                              Recharts Dashboard
  LLaMA 3.3-70B                     (Pie + Bar + Tables)
```

### 6-Node Agent Pipeline

| Node | Tool Used | What It Does |
|------|-----------|--------------|
| **Extraction** | pdfplumber + pandas | Parse PDF/CSV, extract transactions |
| **Categorization** | LLaMA 3.3-70B | Classify each transaction into 12 categories |
| **Analysis** | pandas | Compute income, expenses, trends, averages |
| **Insights** | LLaMA 3.3-70B | Identify wasteful habits, positive behaviors |
| **Advice** | LLaMA 3.3-70B | Generate 5 action items + budget plan |
| **Reflection** | LLaMA 3.3-70B | Self-review advice for realism & specificity |

---

## 🌟 Key Features

### 1. **Smart File Processing**
- Supports PDF and CSV bank statements
- Automatic column detection for CSV files
- AI-powered PDF text extraction and parsing
- Handles various bank statement formats

### 2. **AI-Powered Categorization**
- 12 intelligent categories: Food & Dining, Transport, Shopping, Entertainment, Utilities, Healthcare, Rent/Housing, Salary/Income, Freelance Income, Subscriptions, Personal Care, Miscellaneous
- Context-aware classification using LLaMA 3.3-70B
- Batch processing for efficiency

### 3. **Comprehensive Analytics**
- Total income, expenses, and net savings
- Savings rate calculation
- Category-wise spending breakdown with percentages
- Top 5 biggest expenses
- Monthly trends (income vs expenses)
- Daily average spending
- Subscription cost tracking

### 4. **AI-Generated Insights**
- 6 personalized insights with warning/positive/neutral types
- Specific observations with exact numbers
- Pattern recognition for wasteful habits
- Positive financial behavior identification

### 5. **Actionable Advice**
- 5 ranked action items (High/Medium/Low impact)
- Estimated monthly savings for each recommendation
- Suggested budget percentages by category
- Emergency fund calculator with timeline
- Motivational closing message

### 6. **Self-Reflection Quality Control**
- AI reviews its own advice for specificity and realism
- Quality scoring system
- Automatic refinement if needed
- Ensures non-generic, personalized recommendations

### 7. **Real-Time Streaming**
- Live progress updates via Server-Sent Events (SSE)
- Watch each agent node process in real-time
- Transparent pipeline visualization
- Error handling and status tracking

### 8. **Interactive Dashboard**
- Responsive design with dark/light mode
- Recharts visualizations (pie charts, bar charts)
- Paginated transaction tables
- Export to PDF functionality
- Print-optimized CSS

---

## 🔑 API Keys - 100% FREE

This project uses **ONLY FREE APIs**:

| API | Cost | Limits | Purpose |
|-----|------|--------|---------|
| **Groq API** | **FREE** | 30 req/min, 14.4K req/day | LLaMA 3.3-70B for AI analysis |

**No credit card required. No paid services. No hidden costs.**

Get your free Groq API key at: [console.groq.com](https://console.groq.com)

---

## ⚡ Quick Setup (5 Steps)

### Prerequisites
- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Free Groq API key** - [Get it here](https://console.groq.com) (no credit card needed)

### Step 1: Get Your Free API Key
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for free (no credit card required)
3. Navigate to "API Keys" section
4. Click "Create API Key"
5. Copy the key (starts with `gsk_...`)

### Step 2: Backend Setup
```powershell
# Navigate to backend folder
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file from template
copy .env.example .env

# Edit .env and add your Groq API key
notepad .env
```

**Your `.env` file should contain:**
```env
GROQ_API_KEY=gsk_your_actual_key_here
```

### Step 3: Start Backend Server
```powershell
# From backend folder
uvicorn main:app --reload --port 8000
```
✅ **Expected output:** `Uvicorn running on http://127.0.0.1:8000`

### Step 4: Frontend Setup (New Terminal)
```powershell
# Navigate to frontend folder
cd frontend

# Install Node.js dependencies
npm install
```

### Step 5: Start Frontend
```powershell
# From frontend folder
npm run dev
```
✅ **Expected output:** `Local: http://localhost:5173/`

### Step 6: Test the Application
1. Open browser at `http://localhost:5173`
2. Upload `sample_data/sample_statement.csv`
3. Click "Analyze Statement"
4. Watch the 6-node AI pipeline process in real-time!
5. View your comprehensive financial dashboard

**Total setup time: ~10 minutes**

---

## 📁 Project Structure

```
finance-agent/
├── backend/
│   ├── main.py              # FastAPI + LangGraph agent
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # API key template
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app with routing
│   │   ├── pages/
│   │   │   ├── UploadPage.jsx    # Drag & drop upload
│   │   │   ├── PipelinePage.jsx  # Live SSE progress
│   │   │   └── DashboardPage.jsx # Full analytics dashboard
│   │   └── index.css        # Global styles + print
│   ├── package.json
│   └── vite.config.js
└── sample_data/
    └── sample_statement.csv  # 50 realistic test transactions
```

---

## 🧠 Key AI/Engineering Concepts

| Concept | Implementation |
|---------|----------------|
| **Agentic AI Systems** | LangGraph StateGraph with 6 sequential nodes, each with specific responsibilities |
| **Tool-Using Agents** | pandas as a programmatic analysis tool called by the agent |
| **Structured Output Generation** | LLM prompted to return strict JSON schemas for transactions, insights, advice |
| **Function Calling** | LLM extracts transactions from unstructured PDF text into structured objects |
| **Document Intelligence** | pdfplumber extracts text from PDFs; LLM interprets and structures it |
| **Self-Reflection Loop** | Reflection node reviews LLM-generated advice for quality before final output |
| **LangGraph StateGraph** | Shared state flows through all nodes; each node reads/writes state fields |
| **SSE Streaming** | FastAPI streams real-time node progress to React via Server-Sent Events |

---

## 📊 Dashboard Features

- **4 Summary Cards** — Income, Expenses, Net Savings, Savings Rate
- **Spending Pie Chart** — Category breakdown with color coding
- **Monthly Bar Chart** — Income vs Expenses trend
- **AI Insights Panel** — 6 insights with warning/positive/neutral types
- **5-Point Action Plan** — Ranked by impact with savings estimates
- **Suggested Budget** — Visual % breakdown with progress bars
- **Emergency Fund Calculator** — Target amount + timeline
- **Top 5 Expenses** — Biggest single transactions
- **Transactions Table** — Paginated with category badges
- **Export PDF** — Print-optimized CSS via `window.print()`

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload PDF/CSV, returns `session_id` |
| `GET` | `/stream/{session_id}` | SSE stream of agent progress |
| `GET` | `/report/{session_id}` | Full JSON report |
| `GET` | `/health` | Backend health check |

### Report Schema
```json
{
  "summary": {
    "total_income": 11000.00,
    "total_expenses": 5033.18,
    "net_savings": 5966.82,
    "savings_rate": "54.2%",
    "subscription_total": 127.93,
    "daily_avg_spending": 89.88
  },
  "categories": [
    {"name": "Rent/Housing", "amount": 2800.00, "percentage": 55.6}
  ],
  "insights": [{"type": "warning", "title": "...", "detail": "..."}],
  "action_items": [{"rank": 1, "impact": "High", "action": "...", "monthly_savings": 150}],
  "suggested_budget": {"percentages": {...}, "emergency_fund": {...}},
  "transactions": [...]
}
```

---

## 🧪 Testing the Project

### Test 1: Sample Data (Recommended First Test)
```powershell
# 1. Ensure both servers are running
# 2. Open http://localhost:5173
# 3. Upload: sample_data/sample_statement.csv
# 4. Watch real-time processing
```

**Expected Results:**
- ✅ 50 transactions extracted
- ✅ All transactions categorized
- ✅ Total Income: ~$11,000
- ✅ Total Expenses: ~$5,033
- ✅ Net Savings: ~$5,967
- ✅ Savings Rate: ~54%
- ✅ 6 AI insights generated
- ✅ 5 action items with savings estimates
- ✅ Interactive dashboard with charts

### Test 2: Your Own CSV Bank Statement
**CSV Format Requirements:**
- Columns: `Date`, `Description`, `Amount`, `Type` (optional)
- Date: Any format (YYYY-MM-DD, MM/DD/YYYY, etc.)
- Amount: Positive numbers (use Type column for credit/debit)
- Type: "credit" or "debit" (optional, can be inferred from amount)

**Example CSV:**
```csv
Date,Description,Amount,Type
2024-01-15,Salary Deposit,5000.00,credit
2024-01-16,Grocery Store,125.50,debit
2024-01-17,Netflix,15.99,debit
```

### Test 3: PDF Bank Statement
- Upload any PDF bank statement
- AI will extract transactions using pdfplumber + LLM
- Works with most standard bank formats
- Processing time: 45-90 seconds

### Test 4: API Health Check
```powershell
# Check backend status
curl http://localhost:8000/health
```
**Expected response:**
```json
{"status":"ok","groq_configured":true}
```

### Test 5: API Endpoints
```powershell
# View API documentation
# Open: http://localhost:8000/docs
```

---

## 🔧 Troubleshooting

### Backend Issues

**Problem:** `GROQ_API_KEY not configured`
```powershell
# Solution: Check .env file exists and contains valid key
cd backend
type .env
# Should show: GROQ_API_KEY=gsk_...
```

**Problem:** `Module not found` errors
```powershell
# Solution: Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Problem:** Port 8000 already in use
```powershell
# Solution: Use different port
uvicorn main:app --reload --port 8001
# Update frontend API URL in src/pages/UploadPage.jsx
```

### Frontend Issues

**Problem:** `npm install` fails
```powershell
# Solution: Clear cache and retry
npm cache clean --force
rm -r node_modules
npm install
```

**Problem:** Port 5173 already in use
```powershell
# Solution: Vite will automatically use next available port
# Check terminal output for actual port number
```

**Problem:** "Network Error" when uploading
- ✅ Ensure backend is running on port 8000
- ✅ Check `http://localhost:8000/health` returns OK
- ✅ Verify CORS is enabled (already configured in main.py)

### Analysis Issues

**Problem:** No transactions extracted from PDF
- PDF might have complex formatting
- Try converting to CSV manually first
- Check backend terminal for extraction errors

**Problem:** Generic/vague insights
- Upload more transactions (50+ recommended)
- Include multiple months of data
- Ensure diverse transaction types

**Problem:** Slow processing
- Normal for large files (500+ transactions)
- Groq free tier: 30 requests/min
- PDF processing takes longer than CSV

---

## 🔒 Privacy & Security

Your financial data is **never stored**. Files are:
1. Saved to a temporary OS temp file
2. Processed by the agent
3. Deleted immediately after analysis

Session data lives in memory and is lost when the server restarts.

---

## 📝 Environment Variables

```env
GROQ_API_KEY=your_key_here   # Get free at console.groq.com
```

That's it. One API key, no database, no Redis, no Docker.

---

## � Performance & Limits

### Processing Time
| File Type | Transactions | Time |
|-----------|--------------|------|
| CSV | 50 | ~15-30 seconds |
| CSV | 500 | ~30-60 seconds |
| PDF | 50 | ~45-90 seconds |
| PDF | 500 | ~90-180 seconds |

### Groq API Free Tier Limits
- **Rate Limit:** 30 requests per minute
- **Daily Limit:** 14,400 requests per day
- **Model:** LLaMA 3.3-70B-Versatile
- **Sufficient for:** Personal use, ~100 analyses per day

### Optimization Tips
- Use CSV instead of PDF when possible (faster)
- Batch multiple months into one file
- Limit to 500-1000 transactions per upload for best performance

---

## 💼 Use Cases

### Personal Finance Management
- Monthly spending review
- Budget creation and tracking
- Identifying cost-cutting opportunities
- Emergency fund planning

### Financial Goal Setting
- Savings rate optimization
- Subscription audit
- Category-wise spending limits
- Investment planning preparation

### Financial Literacy
- Understanding spending patterns
- Learning budget allocation best practices
- Developing financial awareness
- Building healthy money habits

---

## �🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Groq API — LLaMA 3.3-70B-Versatile (free tier) |
| Agent Framework | LangGraph 0.1 StateGraph |
| Backend | FastAPI + uvicorn |
| PDF Parsing | pdfplumber |
| Data Analysis | pandas |
| Streaming | Server-Sent Events (SSE) |
| Frontend | React 18 + Vite |
| Styling | Tailwind CSS |
| Charts | Recharts |
| HTTP Client | axios |
