"""
AI Personal Finance Analyst Agent
FastAPI Backend with LangGraph Agent Architecture
"""

import os
import csv
import json
import uuid
import time
import asyncio
import tempfile
import hashlib
import traceback
from pathlib import Path
from typing import Optional, TypedDict, Annotated
from datetime import datetime

import pandas as pd
import pdfplumber
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, Response
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import StateGraph, END
import operator

load_dotenv()

app = FastAPI(title="AI Finance Analyst Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage
sessions: dict = {}

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Model strategy: Use Scout as primary (30k TPM), compound-beta as fallback (70k TPM)
# Avoid 70b-versatile — only 12k TPM + 100k daily token limit (exhausts fast)
MODEL_PRIMARY = "meta-llama/llama-4-scout-17b-16e-instruct"   # 30k TPM
MODEL_FALLBACK = "compound-beta"                               # 70k TPM
MODEL = MODEL_PRIMARY


def groq_call_with_retry(client, messages, temperature=0.2, max_tokens=2000, max_retries=5, prefer_model=None):
    """Make a Groq API call with retry + exponential backoff for rate limits.
    
    Model escalation: preferred -> primary -> fallback (compound-beta)
    """
    last_error = None
    base_model = prefer_model or MODEL_PRIMARY
    model_sequence = [
        base_model,
        base_model,
        MODEL_FALLBACK,
        MODEL_FALLBACK,
        MODEL_PRIMARY,
    ]
    
    for attempt in range(max_retries):
        try:
            model = model_sequence[attempt]
            print(f"  [API] Attempt {attempt+1}/{max_retries} using {model}...")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            tokens_used = response.usage.total_tokens if response.usage else "?"
            print(f"  [OK] Used {tokens_used} tokens with {model}")
            return response
        except Exception as e:
            last_error = e
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                wait = (2 ** attempt) * 4 + 3  # 7s, 11s, 19s, 35s, 67s
                print(f"  [RATE LIMITED] on {model_sequence[attempt]} (attempt {attempt+1}/{max_retries}), waiting {wait}s...")
                time.sleep(wait)
            elif "decommissioned" in error_str or "not found" in error_str.lower() or "not_found" in error_str.lower():
                print(f"  [UNAVAILABLE] Model {model_sequence[attempt]} not available, trying next...")
                continue
            else:
                raise e
    raise last_error

# ─────────────────────────────────────────────
# Auth: CSV-based user storage
# ─────────────────────────────────────────────

USERS_CSV = Path(__file__).parent / "users.csv"


def _ensure_users_csv():
    """Create users.csv with headers if it doesn't exist."""
    if not USERS_CSV.exists():
        with open(USERS_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "email", "password_hash", "created_at"])


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _read_users() -> list[dict]:
    _ensure_users_csv()
    users = []
    with open(USERS_CSV, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row)
    return users


def _write_user(user: dict):
    _ensure_users_csv()
    with open(USERS_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([user["id"], user["name"], user["email"], user["password_hash"], user["created_at"]])


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/signup")
async def signup(req: SignupRequest):
    """Register a new user, store in CSV."""
    name = req.name.strip()
    email = req.email.strip().lower()
    password = req.password

    if not name or not email or not password:
        raise HTTPException(status_code=400, detail="All fields are required")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    users = _read_users()
    if any(u["email"] == email for u in users):
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    user = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "password_hash": _hash_password(password),
        "created_at": datetime.now().isoformat(),
    }
    _write_user(user)

    return {"user": {"id": user["id"], "name": user["name"], "email": user["email"]}}


@app.post("/auth/login")
async def login(req: LoginRequest):
    """Authenticate a user from CSV storage."""
    email = req.email.strip().lower()
    password = req.password

    users = _read_users()
    pw_hash = _hash_password(password)

    user = next((u for u in users if u["email"] == email and u["password_hash"] == pw_hash), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"user": {"id": user["id"], "name": user["name"], "email": user["email"]}}


def get_groq_client():
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
    return Groq(api_key=GROQ_API_KEY)


# ─────────────────────────────────────────────
# LangGraph State
# ─────────────────────────────────────────────

class FinanceState(TypedDict):
    session_id: str
    file_path: str
    file_type: str
    raw_text: str
    transactions: list
    categorized_transactions: list
    analysis_data: dict
    insights_data: list
    action_items: list
    suggested_budget: dict
    reflection_data: str
    final_report: dict
    progress: list
    errors: list


# ─────────────────────────────────────────────
# Node 1: Extraction
# ─────────────────────────────────────────────

def extraction_node(state: FinanceState) -> FinanceState:
    """Extract transactions from PDF or CSV."""
    session_id = state["session_id"]
    file_path = state["file_path"]
    file_type = state["file_type"]
    
    _update_progress(session_id, "extraction", "running", "Extracting transactions from your file...")
    
    transactions = []
    
    try:
        if file_type == "csv":
            df = pd.read_csv(file_path)
            # Limit to 500 transactions for memory efficiency
            if len(df) > 500:
                df = df.head(500)
                _update_progress(session_id, "extraction", "warning", f"Large file detected. Processing first 500 transactions...")
            
            # Normalize column names
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            
            # Try to find date, description, amount columns
            date_col = next((c for c in df.columns if "date" in c), None)
            desc_col = next((c for c in df.columns if any(x in c for x in ["desc", "narr", "detail", "merchant", "payee"])), None)
            amount_col = next((c for c in df.columns if "amount" in c or "amt" in c), None)
            type_col = next((c for c in df.columns if "type" in c or "cr/dr" in c or "debit/credit" in c), None)
            
            if not date_col:
                date_col = df.columns[0]
            if not desc_col:
                desc_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            if not amount_col:
                amount_col = df.columns[2] if len(df.columns) > 2 else df.columns[-1]
            
            for _, row in df.iterrows():
                amount = float(str(row[amount_col]).replace(",", "").replace("$", "").strip())
                tx_type = "credit" if amount > 0 else "debit"
                
                if type_col and pd.notna(row.get(type_col)):
                    raw_type = str(row[type_col]).lower()
                    if "credit" in raw_type or "cr" == raw_type:
                        tx_type = "credit"
                    elif "debit" in raw_type or "dr" == raw_type:
                        tx_type = "debit"
                
                transactions.append({
                    "date": str(row[date_col]),
                    "description": str(row[desc_col]),
                    "amount": abs(amount),
                    "type": tx_type,
                    "category": ""
                })
        
        elif file_type == "pdf":
            raw_lines = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        raw_lines.append(text)
            
            raw_text = "\n".join(raw_lines)
            state["raw_text"] = raw_text
            
            # Use LLM to parse transactions from PDF text
            client = get_groq_client()
            prompt = f"""Extract all financial transactions from this bank statement text.
Return ONLY a JSON array with this exact format, no other text:
[{{"date": "YYYY-MM-DD", "description": "merchant name", "amount": 0.00, "type": "debit or credit"}}]

Rules:
- amount is always positive
- type is "credit" for money coming in (salary, deposits), "debit" for money going out
- date in YYYY-MM-DD format if possible
- description should be clean merchant/payee name

Bank statement text:
{raw_text[:8000]}"""
            
            response = groq_call_with_retry(
                client,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content.strip()
            # Extract JSON array
            start = content.find("[")
            end = content.rfind("]") + 1
            if start >= 0 and end > start:
                parsed = json.loads(content[start:end])
                transactions = [{**t, "category": ""} for t in parsed]
        
        state["transactions"] = transactions
        _update_progress(session_id, "extraction", "done", f"Extracted {len(transactions)} transactions")
        
    except Exception as e:
        state["errors"] = state.get("errors", []) + [f"Extraction error: {str(e)}"]
        _update_progress(session_id, "extraction", "error", f"Extraction failed: {str(e)}")
    
    return state


# ─────────────────────────────────────────────
# Node 2: Categorization
# ─────────────────────────────────────────────

def categorization_node(state: FinanceState) -> FinanceState:
    """Categorize transactions using LLM."""
    session_id = state["session_id"]
    transactions = state["transactions"]
    
    _update_progress(session_id, "categorization", "running", "Categorizing your transactions with AI...")
    
    if not transactions:
        state["categorized_transactions"] = []
        _update_progress(session_id, "categorization", "done", "No transactions to categorize")
        return state
    
    try:
        client = get_groq_client()
        
        categories = [
            "Food & Dining", "Transport", "Shopping", "Entertainment",
            "Utilities", "Healthcare", "Rent/Housing", "Salary/Income",
            "Freelance Income", "Subscriptions", "Personal Care", "Miscellaneous"
        ]
        
        # Batch transactions in chunks of 25 to avoid token limits + rate limits
        BATCH_SIZE = 25
        categorized = [dict(t) for t in transactions]
        
        for batch_start in range(0, len(transactions), BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, len(transactions))
            batch = transactions[batch_start:batch_end]
            
            tx_list = "\n".join([
                f"{j+1}. {t['date']} | {t['description']} | ${t['amount']} | {t['type']}"
                for j, t in enumerate(batch)
            ])
            
            prompt = f"""Categorize each transaction into exactly one category from this list:
{', '.join(categories)}

Transactions:
{tx_list}

Return ONLY a JSON array of objects with "index" (1-based) and "category" fields. No other text.
Example: [{{"index": 1, "category": "Food & Dining"}}, ...]"""
            
            if batch_start > 0:
                time.sleep(3)  # Rate limit buffer between batches
            
            response = groq_call_with_retry(
                client,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content.strip()
            start = content.find("[")
            end = content.rfind("]") + 1
            
            if start >= 0 and end > start:
                cat_data = json.loads(content[start:end])
                cat_map = {item["index"]: item["category"] for item in cat_data}
                for j in range(len(batch)):
                    categorized[batch_start + j]["category"] = cat_map.get(j + 1, "Miscellaneous")
            
            _update_progress(session_id, "categorization", "running", 
                f"Categorized {batch_end}/{len(transactions)} transactions...")
        
        state["categorized_transactions"] = categorized
        _update_progress(session_id, "categorization", "done", "All transactions categorized")
        
    except Exception as e:
        # If partial categorization happened, use what we have
        if categorized:
            state["categorized_transactions"] = categorized
        else:
            state["categorized_transactions"] = [dict(t) for t in transactions]
        state["errors"] = state.get("errors", []) + [f"Categorization error: {str(e)}"]
        _update_progress(session_id, "categorization", "error", f"Categorization issue: {str(e)}")
    
    return state


# ─────────────────────────────────────────────
# Node 3: Analysis
# ─────────────────────────────────────────────

def analysis_node(state: FinanceState) -> FinanceState:
    """Perform pandas-based financial analysis."""
    session_id = state["session_id"]
    transactions = state["categorized_transactions"]
    
    _update_progress(session_id, "analysis", "running", "Running deep financial analysis with pandas...")
    
    if not transactions:
        state["analysis_data"] = {}
        _update_progress(session_id, "analysis", "done", "No data to analyze")
        return state
    
    try:
        df = pd.DataFrame(transactions)
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        
        # Parse dates flexibly
        try:
            df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=False, errors="coerce")
        except Exception:
            try:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            except Exception:
                df["date"] = pd.NaT
        
        income_df = df[df["type"] == "credit"]
        expense_df = df[df["type"] == "debit"]
        
        total_income = round(float(income_df["amount"].sum()), 2)
        total_expenses = round(float(expense_df["amount"].sum()), 2)
        net_savings = round(total_income - total_expenses, 2)
        savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0
        
        # Category breakdown (expenses only)
        cat_breakdown = (
            expense_df.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        if total_expenses > 0:
            cat_breakdown["percentage"] = round(cat_breakdown["amount"] / total_expenses * 100, 1)
        else:
            cat_breakdown["percentage"] = 0
        categories_list = cat_breakdown.to_dict("records")
        
        # Top 5 biggest single expenses
        top_expenses = (
            expense_df.nlargest(5, "amount")[["date", "description", "amount", "category"]]
            .copy()
        )
        top_expenses["date"] = top_expenses["date"].astype(str)
        top_expenses_list = top_expenses.to_dict("records")
        
        # Monthly breakdown - robust approach
        monthly = {}
        valid_dates = df["date"].dropna()
        if len(valid_dates) > 0:
            # Add month column to main df
            df["month"] = df["date"].dt.strftime("%Y-%m")
            
            # Expenses by month
            expense_with_month = expense_df.copy()
            expense_with_month["month"] = expense_with_month["date"].dt.strftime("%Y-%m")
            monthly_expenses = (
                expense_with_month.dropna(subset=["month"])
                .groupby("month")["amount"]
                .sum()
                .round(2)
                .to_dict()
            )
            
            # Income by month
            income_with_month = income_df.copy()
            income_with_month["month"] = income_with_month["date"].dt.strftime("%Y-%m")
            monthly_income = (
                income_with_month.dropna(subset=["month"])
                .groupby("month")["amount"]
                .sum()
                .round(2)
                .to_dict()
            )
            
            monthly = {"expenses": monthly_expenses, "income": monthly_income}
        
        # Subscription total
        sub_total = round(
            expense_df[expense_df["category"] == "Subscriptions"]["amount"].sum(), 2
        )
        
        # Daily average
        if not df["date"].isna().all():
            date_range = (df["date"].max() - df["date"].min()).days + 1
            daily_avg = round(total_expenses / max(date_range, 1), 2)
        else:
            daily_avg = round(total_expenses / 30, 2)
        
        analysis = {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_savings": net_savings,
            "savings_rate": f"{savings_rate}%",
            "savings_rate_num": savings_rate,
            "categories": categories_list,
            "top_expenses": top_expenses_list,
            "monthly": monthly,
            "subscription_total": sub_total,
            "daily_avg_spending": daily_avg,
            "transaction_count": len(transactions),
            "expense_count": len(expense_df),
            "income_count": len(income_df),
        }
        
        state["analysis_data"] = analysis
        _update_progress(session_id, "analysis", "done", "Financial analysis complete")
        
    except Exception as e:
        state["analysis_data"] = {}
        state["errors"] = state.get("errors", []) + [f"Analysis error: {str(e)}"]
        _update_progress(session_id, "analysis", "error", f"Analysis failed: {str(e)}")
        traceback.print_exc()
    
    return state


# ─────────────────────────────────────────────
# Node 4: Insights
# ─────────────────────────────────────────────

def insight_node(state: FinanceState) -> FinanceState:
    """Generate LLM-powered financial insights."""
    session_id = state["session_id"]
    analysis = state["analysis_data"]
    
    _update_progress(session_id, "insights", "running", "Generating personalized financial insights...")
    
    if not analysis:
        state["insights_data"] = ["Insufficient data for insights."]
        _update_progress(session_id, "insights", "done", "Insights generated")
        return state
    
    try:
        client = get_groq_client()
        
        analysis_summary = f"""
Financial Summary:
- Total Income: ${analysis.get('total_income', 0):,.2f}
- Total Expenses: ${analysis.get('total_expenses', 0):,.2f}
- Net Savings: ${analysis.get('net_savings', 0):,.2f}
- Savings Rate: {analysis.get('savings_rate', '0%')}
- Subscription Total: ${analysis.get('subscription_total', 0):,.2f}/month
- Daily Average Spending: ${analysis.get('daily_avg_spending', 0):,.2f}

Spending by Category:
{json.dumps(analysis.get('categories', []), indent=2)}

Top 5 Biggest Expenses:
{json.dumps(analysis.get('top_expenses', []), indent=2)}
"""
        
        prompt = f"""You are an expert financial analyst. Analyze this person's spending data and provide sharp, specific insights.

{analysis_summary}

Generate exactly 6 insights in this JSON format. Be specific with numbers, not generic:
[
  {{"type": "warning", "title": "Short title", "detail": "Specific observation with exact numbers and why it's concerning"}},
  {{"type": "warning", "title": "Short title", "detail": "..."}},
  {{"type": "warning", "title": "Short title", "detail": "..."}},
  {{"type": "positive", "title": "Short title", "detail": "Positive financial behavior observed"}},
  {{"type": "positive", "title": "Short title", "detail": "..."}},
  {{"type": "neutral", "title": "Key Metric", "detail": "Important financial metric to be aware of"}}
]

Return ONLY the JSON array, no other text."""
        
        time.sleep(2)  # Rate limit buffer
        response = groq_call_with_retry(
            client,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1500,
            prefer_model=MODEL_PRIMARY
        )
        
        content = response.choices[0].message.content.strip()
        start = content.find("[")
        end = content.rfind("]") + 1
        
        if start >= 0 and end > start:
            insights = json.loads(content[start:end])
        else:
            insights = [{"type": "neutral", "title": "Analysis Complete", "detail": content}]
        
        state["insights_data"] = insights
        _update_progress(session_id, "insights", "done", "Insights generated")
        
    except Exception as e:
        state["insights_data"] = []
        state["errors"] = state.get("errors", []) + [f"Insight error: {str(e)}"]
        _update_progress(session_id, "insights", "error", f"Insight generation failed: {str(e)}")
    
    return state


# ─────────────────────────────────────────────
# Node 5: Advice
# ─────────────────────────────────────────────

def advice_node(state: FinanceState) -> FinanceState:
    """Generate personalized, actionable financial advice."""
    session_id = state["session_id"]
    analysis = state["analysis_data"]
    insights = state["insights_data"]
    
    _update_progress(session_id, "advice", "running", "Crafting your personalized action plan...")
    
    try:
        client = get_groq_client()
        
        prompt = f"""You are a certified financial planner. Based on this financial data, create a highly specific, actionable advice report.

Financial Data:
- Monthly Income: ${analysis.get('total_income', 0):,.2f}
- Monthly Expenses: ${analysis.get('total_expenses', 0):,.2f}
- Savings Rate: {analysis.get('savings_rate', '0%')}
- Categories: {json.dumps(analysis.get('categories', []))}
- Subscriptions: ${analysis.get('subscription_total', 0):,.2f}/month

Return a JSON object with exactly this structure (no other text):
{{
  "action_items": [
    {{"rank": 1, "impact": "High", "action": "Specific action with exact dollar amounts", "monthly_savings": 150}},
    {{"rank": 2, "impact": "High", "action": "...", "monthly_savings": 80}},
    {{"rank": 3, "impact": "Medium", "action": "...", "monthly_savings": 50}},
    {{"rank": 4, "impact": "Medium", "action": "...", "monthly_savings": 30}},
    {{"rank": 5, "impact": "Low", "action": "...", "monthly_savings": 20}}
  ],
  "suggested_budget": {{
    "Rent/Housing": 30,
    "Food & Dining": 15,
    "Transport": 10,
    "Utilities": 8,
    "Entertainment": 5,
    "Subscriptions": 3,
    "Shopping": 8,
    "Healthcare": 5,
    "Savings/Investments": 16
  }},
  "emergency_fund": {{
    "recommended_amount": 15000,
    "current_monthly_savings": 1300,
    "months_to_goal": 11,
    "advice": "Specific emergency fund advice"
  }},
  "motivational_insight": "One powerful, personalized closing message referencing their specific numbers"
}}"""
        
        time.sleep(2)  # Rate limit buffer
        response = groq_call_with_retry(
            client,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=2000,
            prefer_model=MODEL_PRIMARY
        )
        
        content = response.choices[0].message.content.strip()
        start = content.find("{")
        end = content.rfind("}") + 1
        
        if start >= 0 and end > start:
            advice_data = json.loads(content[start:end])
            state["action_items"] = advice_data.get("action_items", [])
            state["suggested_budget"] = {
                "percentages": advice_data.get("suggested_budget", {}),
                "emergency_fund": advice_data.get("emergency_fund", {}),
                "motivational_insight": advice_data.get("motivational_insight", ""),
            }
        
        _update_progress(session_id, "advice", "done", "Personalized advice ready")
        
    except Exception as e:
        state["action_items"] = []
        state["suggested_budget"] = {}
        state["errors"] = state.get("errors", []) + [f"Advice error: {str(e)}"]
        _update_progress(session_id, "advice", "error", f"Advice generation failed: {str(e)}")
    
    return state


# ─────────────────────────────────────────────
# Node 6: Reflection
# ─────────────────────────────────────────────

def reflection_node(state: FinanceState) -> FinanceState:
    """Self-reflection: review and refine the advice for quality."""
    session_id = state["session_id"]
    action_items = state.get("action_items", [])
    analysis = state.get("analysis_data", {})
    
    _update_progress(session_id, "reflection", "running", "Self-reviewing advice for quality and specificity...")
    
    try:
        client = get_groq_client()
        
        prompt = f"""You are a senior financial advisor reviewing advice generated for a client.

Client data: Income ${analysis.get('total_income',0):,.0f}, Expenses ${analysis.get('total_expenses',0):,.0f}, Savings rate {analysis.get('savings_rate','?')}

Generated action items:
{json.dumps(action_items, indent=2)}

Review these action items critically. Are they:
1. Specific (mentioning actual dollar amounts)?
2. Realistic (achievable given the income level)?
3. Prioritized correctly?
4. Not generic or boilerplate?

Return a JSON object:
{{
  "quality_score": 8,
  "is_specific": true,
  "is_realistic": true,
  "reflection_notes": "Brief assessment of advice quality",
  "refined_items": [] // Only include if items need refinement, otherwise empty array
}}

Return ONLY JSON, no other text."""
        
        time.sleep(2)  # Rate limit buffer
        response = groq_call_with_retry(
            client,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000,
            prefer_model=MODEL_PRIMARY
        )
        
        content = response.choices[0].message.content.strip()
        start = content.find("{")
        end = content.rfind("}") + 1
        
        reflection_text = "Advice reviewed and validated"
        if start >= 0 and end > start:
            reflection_data = json.loads(content[start:end])
            reflection_text = reflection_data.get("reflection_notes", "Quality check passed")
            
            # If there are refined items, use them
            refined = reflection_data.get("refined_items", [])
            if refined and len(refined) > 0:
                state["action_items"] = refined
        
        state["reflection_data"] = reflection_text
        _update_progress(session_id, "reflection", "done", f"Quality check: {reflection_text}")
        
    except Exception as e:
        state["reflection_data"] = "Reflection completed"
        state["errors"] = state.get("errors", []) + [f"Reflection error: {str(e)}"]
        _update_progress(session_id, "reflection", "done", "Reflection complete")
    
    return state


# ─────────────────────────────────────────────
# Final Report Assembly
# ─────────────────────────────────────────────

def _sanitize_for_json(obj):
    """Convert numpy/pandas types to JSON-serializable types."""
    import numpy as np
    import math
    
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_for_json(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        if np.isnan(obj) or np.isinf(obj):
            return 0.0  # Replace NaN/Inf with 0
        return float(obj)
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0  # Replace NaN/Inf with 0
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif hasattr(obj, 'item'):  # Handle pandas objects
        try:
            val = obj.item()
            if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                return 0.0
            return val
        except:
            return str(obj)
    else:
        return str(obj) if obj is not None else None


def finalize_node(state: FinanceState) -> FinanceState:
    """Assemble the final report."""
    session_id = state["session_id"]
    analysis = state.get("analysis_data", {})
    
    _update_progress(session_id, "finalize", "running", "Assembling your complete financial report...")
    
    # Sanitize analysis data to prevent JSON serialization errors
    clean_analysis = _sanitize_for_json(analysis)
    
    final_report = {
        "summary": {
            "total_income": float(clean_analysis.get("total_income", 0)),
            "total_expenses": float(clean_analysis.get("total_expenses", 0)),
            "net_savings": float(clean_analysis.get("net_savings", 0)),
            "savings_rate": str(clean_analysis.get("savings_rate", "0%")),
            "transaction_count": int(clean_analysis.get("transaction_count", 0)),
            "subscription_total": float(clean_analysis.get("subscription_total", 0)),
            "daily_avg_spending": float(clean_analysis.get("daily_avg_spending", 0)),
        },
        "categories": clean_analysis.get("categories", []),
        "monthly": clean_analysis.get("monthly", {}),
        "top_expenses": clean_analysis.get("top_expenses", []),
        "insights": state.get("insights_data", []),
        "action_items": state.get("action_items", []),
        "suggested_budget": state.get("suggested_budget", {}),
        "reflection": state.get("reflection_data", ""),
        "transactions": state.get("categorized_transactions", [])[:100],  # limit for JSON
        "generated_at": datetime.now().isoformat(),
        "errors": state.get("errors", []),
    }
    
    state["final_report"] = final_report
    
    # Store in session
    if session_id in sessions:
        sessions[session_id]["report"] = final_report
        sessions[session_id]["status"] = "complete"
    
    _update_progress(session_id, "finalize", "done", "Your financial report is ready! 🎉")
    
    return state


# ─────────────────────────────────────────────
# Progress Tracking
# ─────────────────────────────────────────────

def _update_progress(session_id: str, node: str, status: str, message: str):
    """Update session progress for SSE streaming."""
    if session_id not in sessions:
        sessions[session_id] = {"progress": [], "report": None, "status": "running"}
    
    progress_entry = {
        "node": node,
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    sessions[session_id]["progress"].append(progress_entry)


# ─────────────────────────────────────────────
# Build LangGraph
# ─────────────────────────────────────────────

def build_graph():
    graph = StateGraph(FinanceState)
    
    graph.add_node("extraction", extraction_node)
    graph.add_node("categorization", categorization_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("insights", insight_node)
    graph.add_node("advice", advice_node)
    graph.add_node("reflection", reflection_node)
    graph.add_node("finalize", finalize_node)
    
    graph.set_entry_point("extraction")
    graph.add_edge("extraction", "categorization")
    graph.add_edge("categorization", "analysis")
    graph.add_edge("analysis", "insights")
    graph.add_edge("insights", "advice")
    graph.add_edge("advice", "reflection")
    graph.add_edge("reflection", "finalize")
    graph.add_edge("finalize", END)
    
    return graph.compile()


finance_graph = build_graph()


# ─────────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────────

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Accept PDF or CSV file upload, start agent processing."""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file size (max 5MB for free tier)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="File too large. Please upload a file smaller than 5MB.")
    
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".csv"]:
        raise HTTPException(status_code=400, detail="Only PDF and CSV files are supported")
    
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "progress": [],
        "report": None,
        "status": "processing",
        "file_name": file.filename
    }
    
    # Save file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    # Run agent in background
    asyncio.create_task(run_agent(session_id, tmp_path, ext.lstrip(".")))
    
    return {"session_id": session_id, "file_name": file.filename, "file_type": ext.lstrip(".")}


async def run_agent(session_id: str, file_path: str, file_type: str):
    """Run the LangGraph agent asynchronously."""
    try:
        initial_state: FinanceState = {
            "session_id": session_id,
            "file_path": file_path,
            "file_type": file_type,
            "raw_text": "",
            "transactions": [],
            "categorized_transactions": [],
            "analysis_data": {},
            "insights_data": [],
            "action_items": [],
            "suggested_budget": {},
            "reflection_data": "",
            "final_report": {},
            "progress": [],
            "errors": [],
        }
        
        await asyncio.get_event_loop().run_in_executor(
            None, finance_graph.invoke, initial_state
        )
        
    except Exception as e:
        if session_id in sessions:
            sessions[session_id]["status"] = "error"
            sessions[session_id]["progress"].append({
                "node": "error",
                "status": "error",
                "message": f"Agent error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    finally:
        try:
            os.unlink(file_path)
        except:
            pass


@app.get("/stream/{session_id}")
async def stream_progress(session_id: str):
    """SSE endpoint for streaming agent progress."""
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    async def event_generator():
        last_idx = 0
        max_wait = 120  # 2 minutes timeout
        waited = 0
        
        while waited < max_wait:
            if session_id not in sessions:
                break
            
            session = sessions[session_id]
            progress = session.get("progress", [])
            
            # Send new events
            while last_idx < len(progress):
                event = progress[last_idx]
                yield f"data: {json.dumps(event)}\n\n"
                last_idx += 1
            
            # Check if done
            if session.get("status") in ["complete", "error"]:
                if last_idx >= len(progress):
                    yield f"data: {json.dumps({'node': 'done', 'status': 'done', 'message': 'Complete'})}\n\n"
                    break
            
            await asyncio.sleep(0.5)
            waited += 0.5
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/report/{session_id}")
async def get_report(session_id: str):
    """Return the full structured report."""
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if session.get("status") == "processing":
        return JSONResponse({"status": "processing", "message": "Analysis still in progress"})
    
    if not session.get("report"):
        return JSONResponse({"status": "error", "message": "Report not available"})
    
    try:
        return JSONResponse({"status": "complete", "report": session["report"]})
    except Exception as e:
        print(f"Error serializing report: {e}")
        return JSONResponse({"status": "error", "message": f"Report serialization error: {str(e)}"})


@app.get("/debug/session/{session_id}")
async def debug_session(session_id: str):
    """Debug endpoint to check session data."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "status": session.get("status"),
        "has_report": "report" in session,
        "report_keys": list(session.get("report", {}).keys()) if session.get("report") else [],
        "progress_count": len(session.get("progress", [])),
        "last_progress": session.get("progress", [])[-1] if session.get("progress") else None
    }


# ─────────────────────────────────────────────
# Chat with Financial Data
# ─────────────────────────────────────────────

# Per-session chat history (in-memory)
chat_histories: dict = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.post("/chat")
async def chat_with_report(req: ChatRequest):
    """Chat about financial data. Supports Hindi, English, Hinglish."""
    session_id = req.session_id
    user_message = req.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    report = session.get("report")
    if not report:
        raise HTTPException(status_code=400, detail="Report not ready yet")

    # Initialize chat history for session
    if session_id not in chat_histories:
        chat_histories[session_id] = []

    try:
        client = get_groq_client()

        # Build financial context from report
        summary = report.get("summary", {})
        categories = report.get("categories", [])
        transactions = report.get("transactions", [])
        insights = report.get("insights", [])
        action_items = report.get("action_items", [])
        top_expenses = report.get("top_expenses", [])
        monthly = report.get("monthly", {})

        # Compact transaction list for context
        tx_summary = "\n".join([
            f"  {t.get('date','')} | {t.get('description','')} | ${t.get('amount',0)} | {t.get('type','')} | {t.get('category','')}"
            for t in transactions[:80]
        ])

        cat_summary = "\n".join([
            f"  {c.get('category','')}: ${c.get('amount',0):.2f} ({c.get('percentage',0)}%)"
            for c in categories
        ])

        monthly_summary = ""
        if monthly:
            for month in sorted(set(list(monthly.get("expenses", {}).keys()) + list(monthly.get("income", {}).keys()))):
                inc = monthly.get("income", {}).get(month, 0)
                exp = monthly.get("expenses", {}).get(month, 0)
                monthly_summary += f"  {month}: Income=${inc:.2f}, Expenses=${exp:.2f}\n"

        insights_text = "\n".join([f"  [{i.get('type','')}] {i.get('title','')}: {i.get('detail','')}" for i in insights])

        financial_context = f"""FINANCIAL DATA CONTEXT:

Summary:
  Total Income: ${summary.get('total_income', 0):,.2f}
  Total Expenses: ${summary.get('total_expenses', 0):,.2f}
  Net Savings: ${summary.get('net_savings', 0):,.2f}
  Savings Rate: {summary.get('savings_rate', '0%')}
  Daily Avg Spending: ${summary.get('daily_avg_spending', 0):,.2f}
  Subscription Total: ${summary.get('subscription_total', 0):,.2f}/mo
  Total Transactions: {summary.get('transaction_count', 0)}

Category Breakdown (Expenses):
{cat_summary}

Monthly Breakdown:
{monthly_summary}

Top 5 Biggest Expenses:
{json.dumps(top_expenses, indent=2)}

AI Insights:
{insights_text}

All Transactions (up to 80):
{tx_summary}
"""

        system_prompt = f"""You are FinanceIQ Assistant — a helpful, friendly financial advisor chatbot.

{financial_context}

INSTRUCTIONS:
- The user can ask in Hindi, English, Hinglish, or any mix. ALWAYS reply in the SAME language/style the user uses.
- If user writes in Hindi/Hinglish, reply in Hindi/Hinglish. If English, reply in English.
- Be specific — use exact numbers, dates, merchant names from the data above.
- If asked about a specific transaction, date, or category, look it up from the transaction list.
- If asked about savings tips or where to cut, give specific actionable advice referencing their actual data.
- Keep responses concise but helpful. Use bullet points when listing things.
- If you don't have enough data to answer something, say so honestly.
- Be warm, supportive, and encouraging about their financial journey.
- Format currency as $X,XXX.XX"""

        # Build messages with history
        messages = [{"role": "system", "content": system_prompt}]

        # Add last 10 messages of history for context
        for h in chat_histories[session_id][-10:]:
            messages.append(h)

        messages.append({"role": "user", "content": user_message})

        response = groq_call_with_retry(
            client,
            messages=messages,
            temperature=0.4,
            max_tokens=1000
        )

        reply = response.choices[0].message.content.strip()

        # Save to history
        chat_histories[session_id].append({"role": "user", "content": user_message})
        chat_histories[session_id].append({"role": "assistant", "content": reply})

        # Keep history manageable
        if len(chat_histories[session_id]) > 30:
            chat_histories[session_id] = chat_histories[session_id][-20:]

        return {"reply": reply}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.get("/health")
async def health():
    return {"status": "ok", "groq_configured": bool(GROQ_API_KEY)}


@app.options("/health")
async def health_options():
    return Response(status_code=200)


@app.get("/")
async def root():
    return {"message": "AI Finance Analyst Agent API", "docs": "/docs"}
