import asyncio
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI

from imessage.reader import get_db_connection, get_last_message_rowid, get_new_messages, get_conversation_history
from imessage.sender import send_message # Keep for direct use if needed, but mostly via manager
from imessage.manager import message_manager
from ai.chat import generate_response
from ai.grammar import get_bot_system_prompt
from ai.utils import split_message_into_chunks
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
            # print(f"Polling... Last seen: {context.last_seen_rowid}") # Very verbose
            new_msgs = get_new_messages(conn, user.phone_number, context.last_seen_rowid)
            
            if new_msgs:
                print(f"DEBUG: Found {len(new_msgs)} new messages. Last seen: {context.last_seen_rowid}")

            for rowid, text, service in new_msgs:
                if text:
                    print(f"New message ({service}): {text}")
                    
                    # Get recent history (limit 10)
                    history_rows = get_conversation_history(conn, user.phone_number, limit=10)
                    
                    # Convert to OpenAI format
                    formatted_history = []
                    for is_from_me, msg_text in history_rows:
                        role = "assistant" if is_from_me else "user"
                        formatted_history.append({"role": role, "content": msg_text})
                    
                    # Generate AI response
                    system_prompt = get_bot_system_prompt()
                    print(f"DEBUG: Generating AI response...")
                    response = generate_response(system_prompt, formatted_history)
                    print(f"DEBUG: AI response: {response[:100]}...")
                    
                    # Split and add to queue
                    chunks = split_message_into_chunks(response)
                    print(f"DEBUG: Split into {len(chunks)} chunks")
                    for chunk in chunks:
                        # The manager handles the delay logic now
                        print(f"DEBUG: Adding chunk to queue: {chunk}")
                        message_manager.add_message(user.phone_number, chunk)
                    
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
