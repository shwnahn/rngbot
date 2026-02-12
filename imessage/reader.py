import sqlite3
import os

DB_PATH = os.path.expanduser("~/Library/Messages/chat.db")

def get_db_connection():
    """Connect to the iMessage database in read-only mode."""
    try:
        # uri=file:...&mode=ro opens in read-only mode, safer for access
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        return conn
    except sqlite3.OperationalError as e:
        print(f"Error connecting to database: {e}")
        print("Ensure you have granted Full Disk Access to your Terminal/IDE.")
        return None

def get_last_message_rowid(conn, handle_id):
    """Get the ROWID of the last message from the target handle."""
    cursor = conn.cursor()
    # handle.id might be formatted differently, but we assume exact match for now
    # based on what we found in check_handles.py
    query = """
    SELECT message.ROWID
    FROM message
    JOIN handle ON message.handle_id = handle.ROWID
    WHERE handle.id = ? AND message.is_from_me = 0
    ORDER BY message.date DESC
    LIMIT 1
    """
    cursor.execute(query, (handle_id,))
    result = cursor.fetchone()
    return result[0] if result else 0

def get_new_messages(conn, handle_id, last_seen_rowid):
    """Fetch new messages since the last seen ROWID."""
    cursor = conn.cursor()
    query = """
    SELECT message.ROWID, message.text, handle.service
    FROM message
    JOIN handle ON message.handle_id = handle.ROWID
    WHERE handle.id = ? AND message.ROWID > ?
    ORDER BY message.date ASC
    """
    cursor.execute(query, (handle_id, last_seen_rowid))
    return cursor.fetchall()

def get_conversation_history(conn, handle_id, limit=10):
    """Fetch recent conversation history for context."""
    cursor = conn.cursor()
    # Fetch last N messages (both from me and from handle)
    query = """
    SELECT message.is_from_me, message.text
    FROM message
    JOIN handle ON message.handle_id = handle.ROWID
    WHERE handle.id = ? AND message.text IS NOT NULL
    ORDER BY message.date DESC
    LIMIT ?
    """
    cursor.execute(query, (handle_id, limit))
    rows = cursor.fetchall()
    
    # Return in chronological order (oldest first)
    return rows[::-1]

