import asyncio
import random
from imessage.sender import send_message
from ai.utils import calculate_chunk_delay

class MessageManager:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_running = False

    async def start(self):
        """Start the background worker."""
        self.is_running = True
        print("MessageManager started.")
        while self.is_running:
            # Wait for a chunk from the queue
            target_number, text = await self.queue.get()
            
            if text:
                # Calculate natural delay
                delay = calculate_chunk_delay(text)
                
                # Simulate typing/thinking time
                # Optional: Send "Typing..." check? (Not easily possible via AppleScript)
                await asyncio.sleep(delay)
                
                # Send the message
                send_message(target_number, text)
            
            # Mark task as done
            self.queue.task_done()

    def add_message(self, target_number, text):
        """Add a message to the queue."""
        self.queue.put_nowait((target_number, text))

    async def stop(self):
        """Stop the worker (gracefully ideally, but here just flag)."""
        self.is_running = False

# Global instance
message_manager = MessageManager()
