import re
import random

def is_short_response(text, word_threshold=5):
    """
    Check if response is short enough to not split.
    
    Args:
        text: Message text
        word_threshold: Minimum word count for splitting (default: 5)
    
    Returns:
        bool: True if message is short
    """
    words = text.split()
    return len(words) < word_threshold


def split_by_semantic_units(text):
    """
    Split text by semantic units (paragraphs, topic transitions, lists).
    
    Args:
        text: Message text to split
    
    Returns:
        list: List of semantic chunks
    """
    # First, split by double newlines (paragraphs)
    paragraphs = re.split(r'\n\n+', text)
    
    chunks = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # Check if it's a list (multiple lines starting with -, *, or numbers)
        lines = para.split('\n')
        list_patterns = [r'^\s*[-*•]\s', r'^\s*\d+\.\s']
        is_list = sum(1 for line in lines if any(re.match(p, line) for p in list_patterns)) > 1
        
        if is_list:
            # Keep entire list together
            chunks.append(para)
        else:
            # Split by topic transition keywords
            # Korean: 그런데, 그리고, 한편, 그래서, 하지만
            # English: By the way, However, Meanwhile, Also
            topic_transitions = r'(?:그런데|그리고|한편|그래서|하지만|By the way|However|Meanwhile|Also),?\s+'
            
            segments = re.split(topic_transitions, para, flags=re.IGNORECASE)
            
            for i, segment in enumerate(segments):
                segment = segment.strip()
                if segment:
                    # If not the first segment, prepend the transition word
                    if i > 0:
                        # Find which transition was used (approximate)
                        transition_match = re.search(topic_transitions, para, flags=re.IGNORECASE)
                        if transition_match:
                            segment = transition_match.group(0) + segment
                    
                    # Further split long segments by sentence
                    if len(segment) > 200:  # Long paragraph
                        sentences = re.split(r'(?<=[.?!])\s+(?=[A-Z"\'\(])', segment)
                        chunks.extend([s.strip() for s in sentences if s.strip()])
                    else:
                        chunks.append(segment)
    
    return chunks


def merge_short_fragments(chunks, min_words=3):
    """
    Merge very short fragments with adjacent chunks.
    
    Args:
        chunks: List of text chunks
        min_words: Minimum word count per chunk (default: 3)
    
    Returns:
        list: Merged chunks
    """
    if not chunks:
        return chunks
    
    merged = []
    current = chunks[0]
    
    for i in range(1, len(chunks)):
        chunk = chunks[i]
        word_count = len(chunk.split())
        
        if word_count < min_words:
            # Merge with current chunk
            current += " " + chunk
        else:
            # Save current and start new
            merged.append(current)
            current = chunk
    
    # Add the last chunk
    if current:
        merged.append(current)
    
    return merged


def merge_symbols_and_numbers(chunks):
    """
    Merge standalone symbols and numbers with adjacent chunks.
    Prevents sending messages like ".", "2", "3" alone.
    
    Args:
        chunks: List of text chunks
    
    Returns:
        list: Merged chunks
    """
    if not chunks:
        return chunks
    
    merged = []
    i = 0
    
    while i < len(chunks):
        chunk = chunks[i].strip()
        
        # Check if chunk is just symbols/numbers (very short and no letters)
        is_symbol = len(chunk) <= 3 and not any(c.isalpha() for c in chunk)
        
        if is_symbol and merged:
            # Merge with previous chunk
            merged[-1] += " " + chunk
        elif is_symbol and i + 1 < len(chunks):
            # Merge with next chunk
            chunks[i + 1] = chunk + " " + chunks[i + 1]
        else:
            merged.append(chunk)
        
        i += 1
    
    return merged


def split_message_into_chunks(text):
    """
    Smart message splitting with semantic awareness.
    
    Splits when:
    - Paragraph boundaries (double newline)
    - Topic transitions (그런데, By the way, etc.)
    - Natural sentence breaks in long text
    
    Keeps together:
    - Short responses (< 5 words)
    - Lists and structured content
    - Related sentences
    - Code blocks or special formatting
    
    Args:
        text: Message text to split
    
    Returns:
        list: List of message chunks
    """
    text = text.strip()
    
    if not text:
        return []
    
    # Don't split very short responses
    if is_short_response(text):
        return [text]
    
    # Split by semantic units
    chunks = split_by_semantic_units(text)
    
    # Merge short fragments
    chunks = merge_short_fragments(chunks)
    
    # Merge standalone symbols and numbers
    chunks = merge_symbols_and_numbers(chunks)
    
    # Final validation: ensure all chunks are meaningful
    chunks = [c.strip() for c in chunks if c.strip() and len(c.strip()) >= 2]
    
    # If splitting produced nothing useful, return original
    if not chunks:
        return [text]
    
    return chunks


def calculate_chunk_delay(text):
    """
    Calculate a natural delay based on typing speed.
    Optimized for better user experience.
    """
    chars = len(text)
    
    # Much faster typing speed: 15-25 chars per second (realistic for chat)
    chars_per_sec = random.uniform(15.0, 25.0)
    base_delay = chars / chars_per_sec
    
    # Minimal "thinking" overhead (0.2-0.5s)
    overhead = random.uniform(0.2, 0.5)
    
    total_delay = base_delay + overhead
    
    # Cap delay to 3 seconds (vs previous 5s)
    final_delay = min(total_delay, 3.0)
    
    # Ensure minimum 0.3s delay (feels more natural)
    final_delay = max(final_delay, 0.3)
    
    # Average should be 0.5-2 seconds for typical messages
    return final_delay

