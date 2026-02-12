from enum import Enum


class UserState(Enum):
    """User conversation state."""
    IDLE = "idle"                      # Waiting for user message
    WAITING = "waiting"                # User sent message, bot thinking
    BOT_RESPONDING = "bot_responding"  # Bot sending response


class Context:
    def __init__(self):
        self.last_seen_rowid = 0
        # Message counter for triggering summaries
        self.message_count = 0
        # Mid-term memory: conversation summary
        self.conversation_summary = ""
        # Key learning points
        self.key_points = []
        # Threshold for auto-summarization
        self.summary_threshold = 5  # Temporarily lowered for testing (was 30)
        # Track if we've loaded initial summary
        self._loaded_initial_summary = False
        # Language detection
        self.current_language = "en"  # "ko" or "en"
        self.last_user_message_time = None
        # User state tracking
        self.current_state = UserState.IDLE
        self.response_session_id = 0

    def update_last_seen(self, rowid):
        self.last_seen_rowid = rowid

    def increment_message_count(self):
        """Increment message counter and return current count."""
        self.message_count += 1
        return self.message_count

    def should_generate_summary(self):
        """Check if we should generate a summary."""
        return self.message_count > 0 and self.message_count % self.summary_threshold == 0

    def update_summary(self, summary, key_points=None):
        """Update conversation summary and key points."""
        self.conversation_summary = summary
        if key_points:
            self.key_points = key_points
        print(f"[Context Updated] Summary length: {len(summary)} chars, Key points: {len(self.key_points)}")

    def save_summary_to_db(self):
        """Save current summary to database."""
        from memory.storage import save_summary
        if self.conversation_summary:
            save_summary(self.conversation_summary, self.key_points, self.message_count)

    def load_latest_summary(self):
        """Load the most recent summary from database on startup."""
        if self._loaded_initial_summary:
            return  # Only load once
        
        from memory.storage import get_latest_summary
        latest = get_latest_summary()
        
        if latest:
            self.conversation_summary = latest['summary']
            self.key_points = latest['key_points']
            print(f"[Context] Loaded previous summary from {latest['session_date']}")
            print(f"  Summary: {self.conversation_summary[:100]}...")
            print(f"  Key points: {len(self.key_points)}")
        
        self._loaded_initial_summary = True

    def get_summary_context(self):
        """Get formatted summary for system prompt."""
        if not self.conversation_summary:
            return ""
        
        context_text = f"\n\n[Previous Conversation Summary]\n{self.conversation_summary}"
        
        if self.key_points:
            context_text += "\n\n[Key Learning Points]\n"
            context_text += "\n".join(f"- {point}" for point in self.key_points)
        
        return context_text

    def detect_and_set_language(self, text):
        """
        Detect language from text and update context.
        Uses simple heuristic: Korean character ratio.
        
        Args:
            text: User message text
        
        Returns:
            str: Detected language code ("ko" or "en")
        """
        from datetime import datetime
        
        # Count Korean characters (Hangul syllables)
        korean_chars = sum(1 for c in text if '\uAC00' <= c <= '\uD7A3')
        # Count all non-whitespace characters
        total_chars = len([c for c in text if c.strip()])
        
        if total_chars > 0:
            korean_ratio = korean_chars / total_chars
            # If more than 30% Korean characters, consider it Korean
            self.current_language = "ko" if korean_ratio > 0.3 else "en"
        else:
            # Default to English for empty/whitespace-only messages
            self.current_language = "en"
        
        self.last_user_message_time = datetime.now()
        
        return self.current_language
    
    def update_user_message(self, rowid, text):
        """
        Update context when user message is received.
        
        Args:
            rowid: Message row ID
            text: Message text
        """
        self.update_last_seen(rowid)
        detected_lang = self.detect_and_set_language(text)
        self.current_state = UserState.WAITING
        print(f"[Context] User message language: {detected_lang}, state: {self.current_state.value}")
    
    def start_response_session(self):
        """
        Start a new response session.
        Call this when bot starts generating a response.
        
        Returns:
            int: New session ID
        """
        self.response_session_id += 1
        self.current_state = UserState.BOT_RESPONDING
        print(f"[Context] Started response session {self.response_session_id}")
        return self.response_session_id
    
    def finish_response_session(self):
        """Mark response session as complete."""
        self.current_state = UserState.IDLE
        print(f"[Context] Response session {self.response_session_id} complete")
    
    def is_bot_busy(self):
        """Check if bot is currently responding."""
        return self.current_state == UserState.BOT_RESPONDING
    
    def reset(self):
        """Reset context (useful for testing or new sessions)."""
        self.message_count = 0
        self.conversation_summary = ""
        self.key_points = []
        print("[Context Reset]")

# Global context instance
context = Context()
