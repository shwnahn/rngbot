import asyncio
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI

from imessage.reader import get_db_connection, get_last_message_rowid, get_new_messages, get_conversation_history
from imessage.sender import send_message
from ai.chat import generate_response
from ai.grammar import get_bot_system_prompt
from state.user import user
from state.context import context

# Background task for polling messages
async def message_poller():
    print(f"Starting poller for {user.phone_number}...")
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
            new_msgs = get_new_messages(conn, user.phone_number, context.last_seen_rowid)
            
            for rowid, text in new_msgs:
                if text:
                    print(f"New message: {text}")
                    
                    # 1. Get recent history (limit 10)
                    # Note: This will include the message we just read (since it's in DB), 
                    # but we might need to handle it carefully to avoid duplication if the logic implies it.
                    # Actually, get_new_messages gets us the 'delta'. 
                    # get_conversation_history gets us the 'state'.
                    # Let's clean up:
                    
                    history_rows = get_conversation_history(conn, user.phone_number, limit=10)
                    
                    # Convert to OpenAI format
                    formatted_history = []
                    for is_from_me, msg_text in history_rows:
                        role = "assistant" if is_from_me else "user"
                        formatted_history.append({"role": role, "content": msg_text})
                    
                    # Generate AI response
                    system_prompt = get_bot_system_prompt()
                    response = generate_response(system_prompt, formatted_history)
                    
                    # Send response
                    send_message(user.phone_number, response)
                    
                    # Update state
                    context.update_last_seen(rowid)
            
            await asyncio.sleep(1) # Non-blocking sleep
            
    except Exception as e:
        print(f"Poller error: {e}")
    finally:
        conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the poller
    user.validate()
    task = asyncio.create_task(message_poller())
    yield
    # Shutdown: Cancel task if needed (asyncio handles this mostly)
    task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"status": "running", "bot": "RingleBot", "target": user.phone_number}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
