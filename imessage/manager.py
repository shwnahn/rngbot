import asyncio
import random
from imessage.sender import send_message
from imessage.typer import simulate_typing_activity
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
            # Item format: (target_number, text, service)
            print("DEBUG: Waiting for message from queue...")
            target_number, text, service = await self.queue.get()
            print(f"DEBUG: Got message from queue: {text}")
            
            if text:
                # Calculate natural delay
                delay = calculate_chunk_delay(text)
                print(f"DEBUG: Waiting {delay:.2f}s before sending...")
                
                # Simple delay without typing simulation
                # (Typing simulation requires Accessibility permissions)
                await asyncio.sleep(delay)
                
                # Send the message
                print(f"DEBUG: Sending message: {text}")
                send_message(target_number, text, service)
                print(f"DEBUG: Message sent!")
            
            # Mark task as done
            self.queue.task_done()

    def add_message(self, target_number, text, service="iMessage"):
        """Add a message to the queue."""
        self.queue.put_nowait((target_number, text, service))

    async def stop(self):
        """Stop the worker (gracefully ideally, but here just flag)."""
        self.is_running = False

# Global instance
message_manager = MessageManager()
