"""
Conversation summarization for mid-term memory.
Generates and manages conversation summaries to maintain context efficiently.
"""

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_summary(message_history):
    """
    Generate a concise summary of the conversation history.
    
    Args:
        message_history: List of dicts with 'role' and 'content'
    
    Returns:
        str: Concise summary of the conversation
    """
    if not message_history:
        return ""
    
    # Format messages for summary
    conversation_text = "\n".join([
        f"{'Student' if msg['role'] == 'user' else 'Tutor'}: {msg['content']}"
        for msg in message_history
    ])
    
    prompt = f"""다음은 영어 튜터(Emily)와 학생(Kwon)의 대화입니다.
이 대화의 핵심 내용을 200자 이내로 요약해주세요. 다음을 포함하세요:
- 주요 학습 주제
- 학생이 한 질문이나 실수
- 튜터가 제공한 피드백
- 현재 대화의 맥락

대화:
{conversation_text}

요약:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        summary = response.choices[0].message.content.strip()
        print(f"[Summary Generated] {summary}")
        return summary
    except Exception as e:
        print(f"Error generating summary: {e}")
        return ""


def extract_key_points(message_history):
    """
    Extract key learning points from conversation.
    
    Args:
        message_history: List of dicts with 'role' and 'content'
    
    Returns:
        list: List of key points
    """
    if not message_history:
        return []
    
    conversation_text = "\n".join([
        f"{'Student' if msg['role'] == 'user' else 'Tutor'}: {msg['content']}"
        for msg in message_history
    ])
    
    prompt = f"""다음 영어 학습 대화에서 핵심 학습 포인트를 3-5개 추출해주세요.
각 포인트는 한 줄로 간결하게 작성하세요.

대화:
{conversation_text}

학습 포인트 (각 줄에 하나씩):"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3
        )
        points_text = response.choices[0].message.content.strip()
        # Split by newlines and clean
        key_points = [p.strip() for p in points_text.split('\n') if p.strip()]
        print(f"[Key Points Extracted] {len(key_points)} points")
        return key_points
    except Exception as e:
        print(f"Error extracting key points: {e}")
        return []
