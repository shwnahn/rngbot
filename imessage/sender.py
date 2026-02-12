import subprocess

def send_message(phone_number, message):
    """Send an iMessage using AppleScript."""
    if not message:
        return

    # Escape double quotes to prevent AppleScript errors
    safe_message = message.replace('"', '\\"')
    
    applescript = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{phone_number}" of targetService
        send "{safe_message}" to targetBuddy
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', applescript], check=True)
        print(f"Sent to {phone_number}: {message}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to send message: {e}")
