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
            target_number, text, service = await self.queue.get()
            
            if text:
                # Calculate natural delay
                delay = calculate_chunk_delay(text)
                
                # Trigger native typing indicator via UI script
                # This steals focus but gives the "..." bubble!
                # Run in executor to avoid blocking the loop heavily? 
                # Actually, it's short lived.
                if delay > 1.0: # Only for meaningful delays
                   try:
                       # Running sync blocking call in async loop is bad practice generally,
                       # but for simplicity here we do it (or use run_in_executor)
                       await asyncio.to_thread(simulate_typing_activity, target_number, delay)
                   except Exception as e:
                       print(f"Typing sim error: {e}")
                       # Fallback to sleep if UI fails
                       await asyncio.sleep(delay)
                else:
                    await asyncio.sleep(delay)
                
                # Send the message
                send_message(target_number, text, service)
            
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
