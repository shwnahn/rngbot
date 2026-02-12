# RingleBot Context (v0.4.1)

## Project Overview
RingleBot is an AI-powered English tutoring chatbot that integrates with iMessage on macOS. It uses OpenAI's GPT-4o-mini to provide conversational practice and feedback.

## Tech Stack
- **Language**: Python 3.13
- **Web Framework**: FastAPI, Uvicorn, **WebSockets**
- **Database**: SQLite (`chat.db`, `ringle_memory.db`)
- **Integration**: AppleScript (sending), SQLite Polling (reading)
- **Frontend**: HTML5, Vanilla JS, WebSockets (for local debug interface)

## Current Status
- **Core Logic**:
  - Polling `chat.db` for new iMessages.
  - Sending messages via `imessage/typer.py` (AppleScript).
  - Context management with simple short-term memory and summary-based mid-term memory.
- **Web Interface**:
  - URL: `http://localhost:8000`
  - Real-time chat via WebSockets (`/ws`).
  - Mirrors core bot logic (`process_user_message`).

## Recent Changes
- **[Fix] WebSocket Dependency**: Installed `websockets` library to fix 404 errors on `/ws`.
- **[Feature] Web Interface**: Added a local web interface for testing and debugging without needing to send real iMessages.
  - Refactored `main.py` to support multiple channels (iMessage & WebSocket).
  - Added `templates/chat.html`.
  - Added `jinja2` dependency.

## Known Issues
- `imessage/reader.py` polling might be slightly delayed compared to real-time.
- `Permissions`: Requires Full Disk Access for Terminal/IDE to read `chat.db`.
