"""
Persistent storage for conversation summaries and user profiles.
Uses SQLite for local storage.
"""

import sqlite3
import json
from datetime import datetime
import os

DB_PATH = os.path.expanduser("~/Documents/rngbot/data/memory.db")

def ensure_db_directory():
    """Ensure the database directory exists."""
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"[Storage] Created directory: {db_dir}")


def init_database():
    """Initialize the database with required tables."""
    ensure_db_directory()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Conversation summaries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversation_summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_date TEXT NOT NULL,
        message_count INTEGER NOT NULL,
        summary TEXT NOT NULL,
        key_points TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # User profile table (for long-term memory)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
    print(f"[Storage] Database initialized at {DB_PATH}")


def save_summary(summary, key_points, message_count):
    """
    Save a conversation summary to the database.
    
    Args:
        summary: Text summary of conversation
        key_points: List of key learning points
        message_count: Current message count
    """
    ensure_db_directory()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    session_date = datetime.now().strftime("%Y-%m-%d")
    key_points_json = json.dumps(key_points, ensure_ascii=False)
    
    cursor.execute("""
    INSERT INTO conversation_summaries (session_date, message_count, summary, key_points)
    VALUES (?, ?, ?, ?)
    """, (session_date, message_count, summary, key_points_json))
    
    conn.commit()
    summary_id = cursor.lastrowid
    conn.close()
    
    print(f"[Storage] Saved summary #{summary_id} ({message_count} messages)")
    return summary_id


def load_recent_summaries(limit=5):
    """
    Load recent conversation summaries.
    
    Args:
        limit: Number of recent summaries to load
    
    Returns:
        List of dicts with summary data
    """
    if not os.path.exists(DB_PATH):
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, session_date, message_count, summary, key_points, created_at
    FROM conversation_summaries
    ORDER BY created_at DESC
    LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    summaries = []
    for row in rows:
        summaries.append({
            "id": row[0],
            "session_date": row[1],
            "message_count": row[2],
            "summary": row[3],
            "key_points": json.loads(row[4]) if row[4] else [],
            "created_at": row[5]
        })
    
    print(f"[Storage] Loaded {len(summaries)} recent summaries")
    return summaries


def get_latest_summary():
    """Get the most recent summary."""
    summaries = load_recent_summaries(limit=1)
    return summaries[0] if summaries else None


def save_user_profile(key, value):
    """
    Save or update a user profile entry.
    
    Args:
        key: Profile key (e.g., 'learning_goal', 'level')
        value: Profile value (will be JSON encoded if dict/list)
    """
    ensure_db_directory()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Serialize value if needed
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    
    cursor.execute("""
    INSERT INTO user_profile (key, value, updated_at)
    VALUES (?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(key) DO UPDATE SET
        value = excluded.value,
        updated_at = CURRENT_TIMESTAMP
    """, (key, value))
    
    conn.commit()
    conn.close()
    print(f"[Storage] Updated profile: {key}")


def load_user_profile(key):
    """
    Load a user profile entry.
    
    Args:
        key: Profile key
    
    Returns:
        Value (parsed from JSON if applicable) or None
    """
    if not os.path.exists(DB_PATH):
        return None
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    value = row[0]
    # Try to parse as JSON
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def get_all_profile_data():
    """Get all user profile data."""
    if not os.path.exists(DB_PATH):
        return {}
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT key, value FROM user_profile")
    rows = cursor.fetchall()
    conn.close()
    
    profile = {}
    for key, value in rows:
        try:
            profile[key] = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            profile[key] = value
    
    return profile
