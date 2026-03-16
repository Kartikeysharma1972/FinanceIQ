# Claw Assistant - Personal AI Assistant

A full-stack AI assistant application with real-time chat, reminders, alarms, and push notifications.

## Features

- 💬 Real-time chat with AI agent via WebSocket
- ⏰ Reminders and alarms with push notifications
- 📱 Progressive Web App (PWA) with mobile optimization
- 🔔 Firebase Cloud Messaging support
- 📊 Dashboard with activity statistics
- ⚡ Quick actions for common tasks

## Tech Stack

- **Backend**: FastAPI, WebSocket, Python
- **Frontend**: HTML5, CSS3, JavaScript (PWA)
- **Database**: In-memory storage (production: SQLite)
- **Push Notifications**: Firebase Cloud Messaging
- **AI Integration**: OpenClaw Gateway

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python server.py
   ```

3. Open browser: `http://localhost:8080`

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/send` - Send message to AI
- `GET /api/history` - Get chat history
- `POST /api/reminder` - Set reminder
- `POST /api/alarm` - Set alarm
- `WebSocket /ws/chat/{device_id}` - Real-time chat

## Configuration

- OpenClaw Gateway: `127.0.0.1:18789`
- Server Port: `8080`
- Firebase: Service account key required for push notifications

## Author

Made by kartikey • kartikey.site
