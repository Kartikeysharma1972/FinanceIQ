"""
Claw Assistant — Combined server: Static PWA + WebSocket + REST API
Serves the PWA and handles all backend communication with OpenClaw.
"""

import asyncio
import json
import uuid
import os
import structlog
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

logger = structlog.get_logger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

app = FastAPI(title="Claw Assistant")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# State
connections: Dict[str, WebSocket] = {}
chat_history: List[Dict] = []
reminders: List[Dict] = []


class SendRequest(BaseModel):
    message: str
    device_id: str = "iphone"


# ─── WebSocket ────────────────────────────────

@app.websocket("/ws/chat/{device_id}")
async def ws_chat(websocket: WebSocket, device_id: str):
    await websocket.accept()
    connections[device_id] = websocket
    logger.info("connected", device=device_id)

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            text = msg.get("text", "")

            # Store
            chat_history.append({
                "id": str(uuid.uuid4()),
                "message": text,
                "sender": "user",
                "timestamp": datetime.now(IST).isoformat()
            })

            # Get AI response
            ai_reply = await ask_openclaw(text)

            chat_history.append({
                "id": str(uuid.uuid4()),
                "message": ai_reply,
                "sender": "ai",
                "timestamp": datetime.now(IST).isoformat()
            })

            await websocket.send_text(json.dumps({
                "type": "chat",
                "data": {"message": ai_reply, "sender": "ai"}
            }))

    except WebSocketDisconnect:
        connections.pop(device_id, None)
        logger.info("disconnected", device=device_id)


# ─── REST API ─────────────────────────────────

@app.post("/api/send")
async def send_message(req: SendRequest):
    ai_reply = await ask_openclaw(req.message)
    return {"message": ai_reply, "sender": "ai", "timestamp": datetime.now(IST).isoformat()}


@app.get("/api/history")
async def history(limit: int = 50):
    return chat_history[-limit:]


@app.post("/api/reminder")
async def add_reminder(title: str, body: str, remind_at: str):
    r = {"id": str(uuid.uuid4()), "title": title, "body": body, "remind_at": remind_at, "status": "active"}
    reminders.append(r)
    return r


@app.get("/api/health")
async def health():
    return {"status": "ok", "connections": len(connections), "messages": len(chat_history)}


# ─── OpenClaw Bridge ─────────────────────────

async def ask_openclaw(message: str) -> str:
    """Forward message to OpenClaw gateway."""
    import aiohttp

    gateway_url = "http://127.0.0.1:18789"
    token = "4ec8bfae3ed00662eb8805c93420ab81293c6c81275d6a67"

    try:
        async with aiohttp.ClientSession() as session:
            # Try the sessions API
            async with session.post(
                f"{gateway_url}/api/v1/chat",
                json={"message": message, "session": "pwa-chat"},
                headers={"Authorization": f"Bearer {token}"},
                timeout=aiohttp.ClientTimeout(total=60),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("reply", data.get("message", "No response"))
                else:
                    body = await resp.text()
                    return f"Gateway returned {resp.status}: {body[:200]}"
    except Exception as e:
        logger.error("openclaw_error", error=str(e))
        return f"⚠️ Connection error: {str(e)}"


# ─── Static Files (PWA) ──────────────────────

# Serve PWA static files
app.mount("/", StaticFiles(directory="public", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
