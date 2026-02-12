from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, Tuple

class BaseChannel(ABC):
    """
    Abstract base class for all communication channels (iMessage, Terminal, etc.).
    """

    @abstractmethod
    async def connect(self):
        """
        Initialize any necessary connections (DB, WebSocket, API, etc.).
        """
        pass

    @abstractmethod
    async def status(self) -> str:
        """
        Return the current status of the channel.
        """
        pass

    @abstractmethod
    async def listen(self) -> AsyncGenerator[Tuple[str, str, dict], None]:
        """
        Async generator that yields new messages.
        
        Yields:
            Tuple[str, str, dict]: (sender_id, text, metadata)
            
            - sender_id: Unique identifier for the sender (e.g., phone number)
            - text: The message content
            - metadata: Additional context (e.g., service type, message ID, raw object)
        """
        pass

    @abstractmethod
    async def send(self, target: str, message: str, metadata: Optional[dict] = None):
        """
        Send a message to the target.
        
        Args:
            target: The recipient identifier (matches sender_id from listen)
            message: The text to send
            metadata: Optional verification or service info (e.g. {'service': 'SMS'})
        """
        pass

    @abstractmethod
    async def typing(self, target: str):
        """
        Simulate typing activity for the target.
        """
        pass
