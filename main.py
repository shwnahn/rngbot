import asyncio
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional

from imessage.reader import get_db_connection, get_last_message_rowid, get_new_messages, get_conversation_history
from imessage.sender import send_message # Keep for direct use if needed, but mostly via manager
from imessage.manager import message_manager, MessagePriority
from ai.chat import generate_response
from ai.grammar import get_bot_system_prompt
from ai.utils import split_message_into_chunks
from state.user import user
from state.context import context, UserState
from memory.summary import generate_summary, extract_key_points
from memory.storage import init_database

# Setup Templates
templates = Jinja2Templates(directory="templates")

# Connection Manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
            
    async def send_json(self, websocket: WebSocket, data: dict):
        await websocket.send_json(data)

manager = ConnectionManager()

async def process_user_message(text: str, service: str, conn, reply_callback, rowid: Optional[int] = None):
    """
    Core message processing pipeline.
    
    Args:
        text: The message text
        service: Service name (e.g. iMessage, Web)
        conn: Database connection
        reply_callback: Async function to handle response chunks (arg: text)
        rowid: Optional rowid if from iMessage DB
    """
    print(f"Processing message ({service}): {text}")
    
    # Update context
    if rowid:
        context.update_user_message(rowid, text)
    else:
        # Check language but don't mess with last_seen_rowid
        detected_lang = context.detect_and_set_language(text)
        context.current_state = UserState.WAITING
        print(f"[Web] Language: {detected_lang}, State: {context.current_state}")
    
    # Start new response session
    session_id = context.start_response_session()
    message_manager.session_id = session_id
    
    # Get recent history (limit 20)
    history_rows = get_conversation_history(conn, user.phone_number, limit=20)
    print(f"DEBUG: Loaded {len(history_rows)} messages from history")
    
    # Convert to OpenAI format
    formatted_history = []
    for is_from_me, msg_text in history_rows:
        role = "assistant" if is_from_me else "user"
        formatted_history.append({"role": role, "content": msg_text})
    
    # If this is a Web message (not in DB), append it manually to history
    if rowid is None:
        formatted_history.append({"role": "user", "content": text})
    
    print(f"DEBUG: Formatted history ({len(formatted_history)} messages):")
    # for i, msg in enumerate(formatted_history[-5:]):  # Show last 5
    #     print(f"  [{i}] {msg['role']}: {msg['content'][:50]}...")
    
    # Increment message counter
    msg_count = context.increment_message_count()
    
    # Check if we should generate a summary
    if context.should_generate_summary():
        print(f"[Auto-Summary] Generating summary after {msg_count} messages...")
        summary = generate_summary(formatted_history)
        key_points = extract_key_points(formatted_history)
        context.update_summary(summary, key_points)
        # Save to database
        context.save_summary_to_db()
    
    # Generate AI response with summary context
    system_prompt = get_bot_system_prompt()
    summary_context = context.get_summary_context()
    print(f"DEBUG: Generating AI response...")
    
    response = generate_response(system_prompt, formatted_history, summary_context)
    print(f"DEBUG: AI response: {response[:100]}...")
    
    # Split and send chunks
    chunks = split_message_into_chunks(response)
    print(f"DEBUG: Split into {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks, 1):
        # Call the callback (adds to queue or sends via WS)
        await reply_callback(chunk)

    # Note: We don't call finish_response_session() here because messages might still be queued/sending

# Background task for polling messages
async def message_poller():
    print(f"Starting poller for {user.phone_number}...")
    
    # Initialize database and load previous summary
    init_database()
    context.load_latest_summary()
    
    conn = get_db_connection()
    if not conn:
        print("Database connection failed. Poller stopped.")
        return

    # Initial state
    try:
        last_rowid = get_last_message_rowid(conn, user.phone_number)
        context.update_last_seen(last_rowid)
        print(f"Initial Last Row ID: {context.last_seen_rowid}")
        
        # Proactive greeting (optional, good for testing)
        # send_message(user.phone_number, "RingleBot is back online!")

        while True:
            # Poll for new messages
            # print(f"Polling... Last seen: {context.last_seen_rowid}") # Very verbose
            new_msgs = get_new_messages(conn, user.phone_number, context.last_seen_rowid)
            
            if new_msgs:
                print(f"DEBUG: Found {len(new_msgs)} new messages. Last seen: {context.last_seen_rowid}")
                
                # New user message detected - interrupt pending responses
                if context.is_bot_busy():
                    cleared = message_manager.clear_pending_messages()
                    if cleared > 0:
                        print(f"[Interrupt] Cleared {cleared} pending messages due to new user input")

            for rowid, text, service in new_msgs:
                if text:
                    # Define callback for iMessage: add to queue
                    async def imessage_callback(chunk):
                         message_manager.add_message(
                            user.phone_number, 
                            chunk,
                            priority=MessagePriority.HIGH
                        )
                    
                    # Process the message
                    await process_user_message(text, service, conn, imessage_callback, rowid)
                    
                    # Log queue status
                    status = message_manager.get_queue_status()
                    print(f"[Queue Status] Pending: {status['pending']}, Session: {status['latest_session']}")
                    
                    # Update state with the rowid of the incoming message we just processed
                    context.update_last_seen(rowid)
            
            await asyncio.sleep(1) # Non-blocking sleep
            
    except Exception as e:
        print(f"Poller error: {e}")
    finally:
        conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the poller and the message manager
    user.validate()
    
    poller_task = asyncio.create_task(message_poller())
    manager_task = asyncio.create_task(message_manager.start())
    
    yield
    
    # Shutdown
    poller_task.cancel()
    await message_manager.stop()
    manager_task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial status
        await manager.send_json(websocket, {"role": "bot", "content": "Connected to RingleBot Brain."})
        
        while True:
            data = await websocket.receive_text()
            print(f"[WebSocket] Received: {data}")
            
            # 1. Echo user message back to UI (optional, UI can do it optimistically)
            # await manager.send_json(websocket, {"role": "user", "content": data})
            
            # 2. Process message
            conn = get_db_connection()
            if conn:
                try:
                    # Callback to send chunks back to WebSocket
                    async def ws_callback(chunk):
                        await manager.send_json(websocket, {"role": "bot", "content": chunk})
                    
                    await process_user_message(data, "Web", conn, ws_callback, rowid=None)
                finally:
                    conn.close()
            else:
                 await manager.send_json(websocket, {"role": "bot", "content": "Error: Database connection failed."})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("[WebSocket] Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
