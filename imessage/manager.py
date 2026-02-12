import asyncio
import random
from enum import IntEnum
from imessage.sender import send_message
from ai.utils import calculate_chunk_delay


class MessagePriority(IntEnum):
    """Priority levels for message queue."""
    HIGH = 1      # New responses (user just sent a message)
    NORMAL = 2    # Regular responses
    LOW = 3       # System messages


class MessageManager:
    def __init__(self):
        self.queue = asyncio.PriorityQueue()
        self.is_running = False
        self.current_task = None  # Track currently sending message
        self.task_counter = 0     # Maintain order for same priority
        self.session_id = 0       # Track response sessions

    async def start(self):
        """Start the background worker."""
        self.is_running = True
        print("MessageManager started.")
        while self.is_running:
            # Wait for a chunk from the queue
            # Item format: (priority, counter, session_id, target_number, text, service)
            print("DEBUG: Waiting for message from queue...")
            priority, counter, msg_session_id, target_number, text, service = await self.queue.get()
            
            # Check if this message is from an old session (interrupted)
            if msg_session_id < self.session_id:
                print(f"DEBUG: Skipping message from old session {msg_session_id} (current: {self.session_id})")
                self.queue.task_done()
                continue
            
            # Set current task
            self.current_task = {
                "priority": priority,
                "session_id": msg_session_id,
                "text": text[:50] + "..." if len(text) > 50 else text
            }
            
            print(f"DEBUG: Got message from queue (priority={priority}, session={msg_session_id}): {text[:50]}...")
            
            if text:
                # Calculate natural delay
                delay = calculate_chunk_delay(text)
                print(f"DEBUG: Waiting {delay:.2f}s before sending...")
                
                # Simple delay without typing simulation
                await asyncio.sleep(delay)
                
                # Send the message
                print(f"DEBUG: Sending message: {text}")
                send_message(target_number, text, service)
                print(f"DEBUG: Message sent!")
            
            # Clear current task
            self.current_task = None
            
            # Mark task as done
            self.queue.task_done()

    def add_message(self, target_number, text, service="iMessage", priority=MessagePriority.NORMAL):
        """
        Add a message to the priority queue.
        
        Args:
            target_number: Phone number to send to
            text: Message text
            service: iMessage or SMS
            priority: MessagePriority level (default: NORMAL)
        """
        self.task_counter += 1
        # Use current session_id from context (will be set in main.py)
        self.queue.put_nowait((priority, self.task_counter, self.session_id, target_number, text, service))
        print(f"DEBUG: Added message to queue (priority={priority}, session={self.session_id})")

    def start_new_session(self):
        """
        Start a new response session.
        Used when user sends a new message.
        
        Returns:
            int: New session ID
        """
        self.session_id += 1
        print(f"[MessageManager] Started new session: {self.session_id}")
        return self.session_id

    def clear_pending_messages(self):
        """
        Mark current session as interrupted.
        Manager will skip messages from old sessions.
        
        Returns:
            int: Number of messages that will be skipped
        """
        # Don't actually clear the queue (causes manager to block)
        # Instead, just increment session_id so old messages get skipped
        pending = self.queue.qsize()
        
        if pending > 0:
            print(f"[MessageManager] {pending} messages will be skipped (old session)")
        
        return pending

    def get_queue_status(self):
        """
        Get current queue status for debugging.
        
        Returns:
            dict: Status information
        """
        return {
            "pending": self.queue.qsize(),
            "current_sending": self.current_task is not None,
            "current_text": self.current_task.get("text") if self.current_task else None,
            "current_session": self.current_task.get("session_id") if self.current_task else None,
            "latest_session": self.session_id
        }

    async def stop(self):
        """Stop the worker gracefully."""
        self.is_running = False

# Global instance
message_manager = MessageManager()
