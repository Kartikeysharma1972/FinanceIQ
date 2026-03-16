"""
Claw Assistant Backend — Bridge between Android app and OpenClaw AI agent.
Handles WebSocket chat, FCM push notifications, reminders, and alarms.
"""

import asyncio
import json
import uuid
import structlog
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from api.auth import create_token, verify_token
from websocket.manager import ConnectionManager
from fcm.push import FCMService

logger = structlog.get_logger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

# In-memory stores (replace with DB in production)
reminders_store: List[Dict] = []
alarms_store: List[Dict] = []
chat_history: List[Dict] = []
fcm_tokens: Dict[str, str] = {}  # device_id -> fcm_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    logger.info("Starting Claw Assistant Backend")
    # Start reminder checker
    asyncio.create_task(reminder_loop())
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Claw Assistant API",
    description="Backend for the Claw Assistant Android app",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ws_manager = ConnectionManager()
fcm_service = FCMService()


# ─── Models ───────────────────────────────────────────────

class MessageRequest(BaseModel):
    message: str
    device_id: str


class MessageResponse(BaseModel):
    id: str
    message: str
    sender: str  # "user" or "ai"
    timestamp: str


class ReminderRequest(BaseModel):
    title: str
    body: str
    remind_at: str  # ISO format
    priority: str = "normal"  # normal, high, urgent


class AlarmRequest(BaseModel):
    title: str
    time: str  # HH:MM format (IST)
    repeat: Optional[str] = None  # daily, weekdays, once
    sound: str = "default"


class FCMRegisterRequest(BaseModel):
    device_id: str
    fcm_token: str


class DashboardResponse(BaseModel):
    active_reminders: int
    active_alarms: int
    messages_today: int
    last_ai_message: Optional[str] = None


# ─── WebSocket Chat ──────────────────────────────────────

@app.websocket("/ws/chat/{device_id}")
async def websocket_chat(websocket: WebSocket, device_id: str):
    """Real-time bidirectional chat with AI agent."""
    await ws_manager.connect(device_id, websocket)
    logger.info("device_connected", device_id=device_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Store user message
            user_msg = {
                "id": str(uuid.uuid4()),
                "message": message.get("text", ""),
                "sender": "user",
                "device_id": device_id,
                "timestamp": datetime.now(IST).isoformat(),
            }
            chat_history.append(user_msg)

            # Forward to OpenClaw agent and get response
            ai_response = await forward_to_openclaw(message.get("text", ""))

            # Store AI response
            ai_msg = {
                "id": str(uuid.uuid4()),
                "message": ai_response,
                "sender": "ai",
                "device_id": device_id,
                "timestamp": datetime.now(IST).isoformat(),
            }
            chat_history.append(ai_msg)

            # Send back to device
            await ws_manager.send_message(
                device_id,
                json.dumps({
                    "type": "chat",
                    "data": ai_msg,
                }),
            )

    except WebSocketDisconnect:
        ws_manager.disconnect(device_id)
        logger.info("device_disconnected", device_id=device_id)


# ─── REST Endpoints ──────────────────────────────────────

@app.post("/api/send", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    """Send a message to AI (REST fallback when WebSocket unavailable)."""
    ai_response = await forward_to_openclaw(request.message)

    msg = MessageResponse(
        id=str(uuid.uuid4()),
        message=ai_response,
        sender="ai",
        timestamp=datetime.now(IST).isoformat(),
    )

    # Also push via FCM if device has token
    if request.device_id in fcm_tokens:
        await fcm_service.send_notification(
            token=fcm_tokens[request.device_id],
            title="AI Response",
            body=ai_response[:100],
            data={"type": "chat", "message_id": msg.id},
        )

    return msg


@app.post("/api/reminder")
async def set_reminder(request: ReminderRequest):
    """Set a timed reminder with push notification."""
    reminder = {
        "id": str(uuid.uuid4()),
        "title": request.title,
        "body": request.body,
        "remind_at": request.remind_at,
        "priority": request.priority,
        "status": "active",
        "created_at": datetime.now(IST).isoformat(),
    }
    reminders_store.append(reminder)
    logger.info("reminder_set", reminder_id=reminder["id"], at=request.remind_at)
    return {"status": "set", "reminder": reminder}


@app.post("/api/alarm")
async def set_alarm(request: AlarmRequest):
    """Set an alarm (triggers on-device alarm via FCM)."""
    alarm = {
        "id": str(uuid.uuid4()),
        "title": request.title,
        "time": request.time,
        "repeat": request.repeat,
        "sound": request.sound,
        "status": "active",
        "created_at": datetime.now(IST).isoformat(),
    }
    alarms_store.append(alarm)

    # Push alarm config to device
    for device_id, token in fcm_tokens.items():
        await fcm_service.send_data_message(
            token=token,
            data={
                "type": "alarm",
                "alarm_id": alarm["id"],
                "title": request.title,
                "time": request.time,
                "repeat": request.repeat or "once",
                "sound": request.sound,
            },
        )

    return {"status": "set", "alarm": alarm}


@app.post("/api/fcm/register")
async def register_fcm_token(request: FCMRegisterRequest):
    """Register device FCM token for push notifications."""
    fcm_tokens[request.device_id] = request.fcm_token
    logger.info("fcm_registered", device_id=request.device_id)
    return {"status": "registered"}


@app.get("/api/history")
async def get_history(limit: int = 50, device_id: Optional[str] = None):
    """Get chat history."""
    history = chat_history
    if device_id:
        history = [m for m in history if m.get("device_id") == device_id]
    return history[-limit:]


@app.get("/api/reminders")
async def list_reminders():
    """List all active reminders."""
    return [r for r in reminders_store if r["status"] == "active"]


@app.get("/api/alarms")
async def list_alarms():
    """List all active alarms."""
    return [a for a in alarms_store if a["status"] == "active"]


@app.get("/api/dashboard", response_model=DashboardResponse)
async def get_dashboard():
    """Dashboard summary data."""
    today = datetime.now(IST).date().isoformat()
    msgs_today = len([m for m in chat_history if m["timestamp"].startswith(today)])
    last_ai = next(
        (m["message"] for m in reversed(chat_history) if m["sender"] == "ai"),
        None,
    )

    return DashboardResponse(
        active_reminders=len([r for r in reminders_store if r["status"] == "active"]),
        active_alarms=len([a for a in alarms_store if a["status"] == "active"]),
        messages_today=msgs_today,
        last_ai_message=last_ai,
    )


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "connected_devices": len(ws_manager.active_connections),
        "timestamp": datetime.now(IST).isoformat(),
    }


# ─── Background Tasks ────────────────────────────────────

async def reminder_loop():
    """Check and fire reminders every 30 seconds."""
    while True:
        now = datetime.now(IST)
        for reminder in reminders_store:
            if reminder["status"] != "active":
                continue
            remind_at = datetime.fromisoformat(reminder["remind_at"])
            if now >= remind_at:
                reminder["status"] = "fired"
                # Push to all devices
                for device_id, token in fcm_tokens.items():
                    await fcm_service.send_notification(
                        token=token,
                        title=f"⏰ {reminder['title']}",
                        body=reminder["body"],
                        data={"type": "reminder", "reminder_id": reminder["id"]},
                        priority=reminder.get("priority", "normal"),
                    )
                    # Also send via WebSocket if connected
                    await ws_manager.send_message(
                        device_id,
                        json.dumps({
                            "type": "reminder",
                            "data": reminder,
                        }),
                    )
                logger.info("reminder_fired", reminder_id=reminder["id"])
        await asyncio.sleep(30)


async def forward_to_openclaw(message: str) -> str:
    """Forward message to OpenClaw gateway and get AI response."""
    import aiohttp

    gateway_url = "http://127.0.0.1:18789"
    gateway_token = "4ec8bfae3ed00662eb8805c93420ab81293c6c81275d6a67"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{gateway_url}/api/chat",
                json={"message": message},
                headers={"Authorization": f"Bearer {gateway_token}"},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("reply", "No response from AI")
                else:
                    return f"Gateway error: {resp.status}"
    except Exception as e:
        logger.error("openclaw_forward_failed", error=str(e))
        return f"Connection error: {str(e)}"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
