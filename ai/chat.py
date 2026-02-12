import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(system_prompt, message_history, summary_context=""):
    """
    Generate a response using OpenAI.
    
    Args:
        system_prompt: Base system prompt
        message_history: List of dictionaries [{'role': 'user'|'assistant', 'content': '...'}, ...]
        summary_context: Optional conversation summary to include in system prompt
    
    Returns:
        str: Generated response
    """
    try:
        # Append summary context to system prompt if available
        enhanced_prompt = system_prompt
        if summary_context:
            enhanced_prompt += summary_context
        
        messages = [{"role": "system", "content": enhanced_prompt}] + message_history
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "Sorry, I'm having trouble thinking right now. Let's try again in a bit."
