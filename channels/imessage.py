import asyncio
from typing import AsyncGenerator, Tuple, Optional
from channels.base import BaseChannel
from imessage.reader import get_db_connection, get_last_message_rowid, get_new_messages
from imessage.manager import MessageManager
from imessage.typer import simulate_typing_activity

class IMessageChannel(BaseChannel):
    """
    Adapter for iMessage/SMS communication on macOS.
    """
    def __init__(self, target_phone: str):
        self.target_phone = target_phone
        self.manager = MessageManager()
        self.last_seen_rowid = 0
        self.conn = None
        self.running = False

    async def connect(self):
        """Connects to chat.db and starts the message manager."""
        print(f"Connecting to iMessage (Target: {self.target_phone})...")
        self.conn = get_db_connection()
        
        if self.conn:
            try:
                self.last_seen_rowid = get_last_message_rowid(self.conn, self.target_phone)
                print(f"IMessageChannel connected. Initial Last Row ID: {self.last_seen_rowid}")
            except Exception as e:
                print(f"Error fetching last row ID: {e}")
        
        # Start the background manager for sending
        asyncio.create_task(self.manager.start())
        self.running = True

    async def status(self) -> str:
        return "connected" if self.conn else "disconnected"

    async def listen(self) -> AsyncGenerator[Tuple[str, str, dict], None]:
        """
        Polls chat.db for new messages.
        Yields: (sender_id, text, metadata={service, is_from_me, rowid})
        """
        if not self.conn:
             print("Reconnecting to DB...")
             self.conn = get_db_connection()
             if not self.conn:
                 await asyncio.sleep(5)
                 return

        print(f"Started listening on iMessage for {self.target_phone}...")
        while self.running:
            try:
                # get_new_messages returns [(rowid, text, service), ...] 
                # Note: I verified in debug steps that is_from_me was NOT in the tuple in reader.py, 
                # but I did remove the WHERE clause filter.
                # Let's double check reader.py content. 
                # If I only removed the filter, the SELECT count is 3: ROWID, text, service.
                
                new_msgs = get_new_messages(self.conn, self.target_phone, self.last_seen_rowid)
                
                for rowid, text, service in new_msgs:
                    # Update local cursor immediately to avoid re-reading
                    self.last_seen_rowid = max(self.last_seen_rowid, rowid)
                    
                    # Yield message
                    # We might want to add is_from_me to the SELECT in reader.py if we need it here,
                    # but for now, rely on previous logic. 
                    # Wait, if I want to distinguish "from me", I should add it to reader.py officially.
                    # But if I stick to current reader.py:
                    yield (self.target_phone, text, {"service": service, "rowid": rowid})
                    
            except Exception as e:
                print(f"IMessage listen error: {e}")
                
            await asyncio.sleep(1)

    async def send(self, target: str, message: str, metadata: Optional[dict] = None):
        """
        Queues the message for sending via MessageManager.
        """
        service = "iMessage"
        if metadata and "service" in metadata:
            service = metadata["service"]
            
        self.manager.add_message(target, message, service)

    async def typing(self, target: str):
        """
        Triggers the typing indicator simulation.
        """
        # Note: MessageManager already does this based on delay, 
        # but this allows explicit control if needed.
        await asyncio.to_thread(simulate_typing_activity, target)
