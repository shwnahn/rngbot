# RingleBot Context (v0.5.0)

## Project Overview
RingleBot is an AI-powered English tutoring chatbot that integrates with **iMessage** and **Telegram**. It uses OpenAI's GPT-4o-mini to provide conversational practice and feedback.

## Tech Stack
- **Language**: Python 3.13
- **Web Framework**: FastAPI, Uvicorn, **WebSockets**
- **Bot Framework**: `python-telegram-bot` (v22.6)
- **Database**: SQLite (`chat.db` for iMessage, `ringle_memory.db` for Telegram & Memory)
- **Integration**: AppleScript (iMessage sending), SQLite Polling (iMessage reading), Telegram Long Polling

## Current Status
- **Core Logic**:
  - Unified message processing pipeline (`main.process_user_message`) supporting multiple channels.
  - State management with `context` (Language detection, session handling).
- **Channels**:
  - **iMessage**: Polling `chat.db` (Readable), AppleScript (Writable).
  - **Web Interface**: `http://localhost:8000/chat` (WebSocket).
  - **Telegram**: `@Ringle_test_bot` (Long Polling).
- **Memory**:
  - Conversation history:
    - iMessage: Stored in Apple's `chat.db`.
    - Telegram: Stored in local `telegram_messages` table in `memory.db`.
  - Content summary and key points stored in `memory.db`.

## Recent Changes
- **[Feature] Telegram Integration**:
  - Added `channels/telegram.py` for bot logic.
  - Implemented history storage for Telegram in `memory/storage.py`.
  - Refactored `main.py` to initialize bot and start polling.
- **[Fix] Dependency Conflicts**:
  - Upgraded `python-telegram-bot` to v22.6 to fix `AttributeError` in startup.
  - Unpinned `httpx` version to resolve conflicts with `openai` library.
- **[Fix] Configuration**:
  - Fixed malformed `.env` file where tokens were concatenated.

## Known Issues
- `imessage/reader.py` polling might be slightly delayed compared to real-time.
- `Permissions`: Requires Full Disk Access for Terminal/IDE to read `chat.db`.
