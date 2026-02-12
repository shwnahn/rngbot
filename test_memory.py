"""
Test script for memory system.
Run this to verify the memory components work correctly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.storage import init_database, save_summary, load_recent_summaries, save_user_profile, get_all_profile_data
from memory.summary import generate_summary, extract_key_points

def test_storage():
    """Test database operations."""
    print("=== Testing Storage ===")
    
    # Initialize DB
    init_database()
    print("✓ Database initialized")
    
    # Test saving summary
    test_summary = "Student practiced business email writing. Made progress on formal tone."
    test_points = ["Use 'Dear' for formal emails", "Avoid contractions in business context"]
    summary_id = save_summary(test_summary, test_points, 30)
    print(f"✓ Saved test summary (ID: {summary_id})")
    
    # Test loading summaries
    summaries = load_recent_summaries(limit=3)
    print(f"✓ Loaded {len(summaries)} recent summaries")
    for s in summaries:
        print(f"  - {s['session_date']}: {s['summary'][:50]}...")
    
    # Test user profile
    save_user_profile("learning_goal", "Improve business English")
    save_user_profile("level", "intermediate")
    save_user_profile("preferences", {"topics": ["business", "email"], "style": "formal"})
    print("✓ Saved user profile data")
    
    profile = get_all_profile_data()
    print(f"✓ Loaded profile: {profile}")
    
    print("\n✅ All storage tests passed!\n")


def test_summary_generation():
    """Test summary generation (requires OpenAI API key)."""
    print("=== Testing Summary Generation ===")
    
    # Mock conversation history
    mock_history = [
        {"role": "user", "content": "Hi Emily! I need help writing a business email."},
        {"role": "assistant", "content": "Hello Kwon! I'd be happy to help. What kind of business email are you writing?"},
        {"role": "user", "content": "I'm writing to a potential client. Should I say 'Hey' or something else?"},
        {"role": "assistant", "content": "Great question! For business emails, especially to clients, use 'Dear [Name]' instead of 'Hey'. It's more professional."},
        {"role": "user", "content": "Got it! What about ending the email?"},
        {"role": "assistant", "content": "For professional emails, use 'Best regards' or 'Sincerely' followed by your name."}
    ]
    
    try:
        # Generate summary
        summary = generate_summary(mock_history)
        print(f"✓ Generated summary:\n  {summary}\n")
        
        # Extract key points
        key_points = extract_key_points(mock_history)
        print(f"✓ Extracted {len(key_points)} key points:")
        for point in key_points:
            print(f"  - {point}")
        
        print("\n✅ Summary generation tests passed!\n")
    except Exception as e:
        print(f"❌ Summary generation failed: {e}")
        print("   Make sure OPENAI_API_KEY is set in .env\n")


def main():
    print("\n" + "="*60)
    print("Memory System Test Suite")
    print("="*60 + "\n")
    
    test_storage()
    
    # Ask before testing OpenAI (costs money)
    response = input("Test summary generation? This will call OpenAI API (y/n): ")
    if response.lower() == 'y':
        test_summary_generation()
    
    print("="*60)
    print("Testing complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
