import os
from dotenv import load_dotenv

load_dotenv()

class User:
    def __init__(self):
        self.phone_number = os.getenv("TARGET_PHONE_NUMBER")
        self.name = "Kwon"  # Could be dynamic later
        
        # Trigger configuration
        self.trigger_prefix = os.getenv("TRIGGER_PREFIX", "/")
        # Default to True as requested
        self.use_trigger = os.getenv("USE_TRIGGER", "True").lower() == "true"

    def validate(self):
        if not self.phone_number:
            raise ValueError("TARGET_PHONE_NUMBER not set in .env")

# Global user instance
user = User()
