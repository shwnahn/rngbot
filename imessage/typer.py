import subprocess
import time

def simulate_typing_activity(target_phone, duration=2.0):
    """
    Simulate typing by focusing the chat and typing a space.
    This triggers the native "Typing..." bubble on the recipient's end.
    
    WARNING: This brings the Messages app to the foreground!
    """
    # 1. Open the specific chat window
    # 'open location' helps focus the right buddy
    subprocess.run(['open', f'imessage://{target_phone}'])
    
    # 2. Wait for focus
    time.sleep(0.5)
    
    # 3. Type a space (triggers typing indicator) -> Wait -> Update/Clear
    # We use a space because it's invisible if we accidentally send it,
    # and it triggers the bubble.
    applescript = f'''
    tell application "System Events"
        tell process "Messages"
            -- Type a space
            keystroke " "
            
            -- Wait for the duration (simulating typing time)
            delay {duration}
            
            -- Clear the text (Cmd + A, Delete) to ensure we don't send garbage
            keystroke "a" using command down
            key code 51 -- Delete
        end tell
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', applescript], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Typing simulation failed: {e}")
