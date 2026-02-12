import re
import random

def split_message_into_chunks(text):
    """
    Split a long message into smaller chunks (sentences) for natural texting flow.
    """
    # Split by sentence endings (. ? !), keeping the punctuation.
    # This regex looks for punctuation followed by space or end of string.
    # It creates a list like ['Hello.', ' ', 'How are you?', '']
    parts = re.split(r'([.?!]+(?:\s+|$))', text)
    
    chunks = []
    current_chunk = ""
    
    for part in parts:
        current_chunk += part
        # If the part contains punctuation, it's likely the end of a sentence/chunk.
        # But we also want to avoid sending tiny chunks like just "." if something goes wrong.
        if re.search(r'[.?!]', part):
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = ""
            
    # Add any remaining text
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
        
    return chunks

def calculate_chunk_delay(text):
    """
    Calculate a natural delay based on typing speed.
    Avg typing speed: ~300 chars/min = 5 chars/sec.
    """
    chars = len(text)
    
    # Base speed: 4-6 chars per second (randomized)
    chars_per_sec = random.uniform(4.0, 6.0)
    base_delay = chars / chars_per_sec
    
    # Add "thinking" or "sentence pause" overhead
    overhead = random.uniform(0.5, 1.5)
    
    total_delay = base_delay + overhead
    
    # Cap delay to avoid waiting too long for huge chunks (max 10s)
    return min(total_delay, 10.0)

