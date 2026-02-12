import asyncio
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI

from imessage.reader import get_db_connection, get_last_message_rowid, get_new_messages, get_conversation_history
from imessage.sender import send_message # Keep for direct use if needed, but mostly via manager
from imessage.manager import message_manager, MessagePriority
from ai.chat import generate_response
from ai.grammar import get_bot_system_prompt
from ai.utils import split_message_into_chunks
from state.user import user
from state.context import context
from memory.summary import generate_summary, extract_key_points
from memory.storage import init_database

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
                    print(f"New message ({service}): {text}")
                    
                    # Update context with language detection
                    context.update_user_message(rowid, text)
                    
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
                    
                    print(f"DEBUG: Formatted history ({len(formatted_history)} messages):")
                    for i, msg in enumerate(formatted_history[-5:]):  # Show last 5
                        print(f"  [{i}] {msg['role']}: {msg['content'][:50]}...")
                    
                    # Increment message counter
                    msg_count = context.increment_message_count()
                    print(f"DEBUG: Message count: {msg_count}")
                    
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
                    
                    # Split and add to queue with HIGH priority
                    chunks = split_message_into_chunks(response)
                    print(f"DEBUG: Split into {len(chunks)} chunks")
                    for i, chunk in enumerate(chunks, 1):
                        print(f"DEBUG: Adding chunk {i}/{len(chunks)} to queue: {chunk[:50]}...")
                        message_manager.add_message(
                            user.phone_number, 
                            chunk,
                            priority=MessagePriority.HIGH
                        )
                    
                    # Log queue status
                    status = message_manager.get_queue_status()
                    print(f"[Queue Status] Pending: {status['pending']}, Session: {status['latest_session']}")
                    
                    # Mark response as complete (state will change when messages finish sending)
                    # Note: We don't call finish_response_session() here because messages are still queued
                    
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

@app.get("/")
def read_root():
    return {"status": "running", "bot": "RingleBot", "target": user.phone_number}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
