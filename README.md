# RingleBot (링글봇) - 모듈형 아키텍처

맥(Mac)의 아이메시지(iMessage)를 연동하여 동작하는 AI 영어 튜터 봇입니다.
FastAPI를 기반으로 리팩토링되었으며, 대화 맥락을 기억하고 자연스러운 영어 교정을 제공합니다.

## ✨ 주요 기능

*   **실시간 대화**: 아이메시지와 **SMS(문자)**를 모두 지원하며, 받은 방식 그대로 답장합니다.
*   **문맥 인식 (Context Awareness)**: 최근 대화 내용(History)을 기억하여 자연스러운 티키타카 가능
*   **자연스러운 타이핑**:
    *   메시지 길이에 따라 입력 시간을 조절하여 사람처럼 보냅니다.
    *   긴 답변은 문장 단위로 끊어서 전송합니다.
    *   **입력중(...) 효과**: 메시지 창에 빈 공간을 입력하여 상대방에게 '입력중' 말풍선을 띄웁니다.
*   **영어 교정**: 링글 튜터 페르소나(Emily)가 학생(Kwon)의 문법을 자연스럽게 교정
*   **명령어 모드**: `/`로 시작하는 메시지에만 반응하도록 설정 가능 (혼잣말 방지)

## 📂 프로젝트 구조

*   `main.py`: 메인 서버 & 메시지 감지 루프
*   `core/`: **(New)**
    *   `bot.py`: 봇의 핵심 로직 (채널 독립적)
*   `channels/`: **(New)**
    *   `base.py`: 채널 인터페이스 정의
    *   `imessage.py`: iMessage 연동 어댑터
*   `imessage/`: (Legacy - `channels/imessage.py`로 통합 중)
    *   `reader.py`: `chat.db` 읽기 (SMS/iMessage 구분)
    *   `sender.py`: AppleScript 발송
    *   `manager.py`: 메시지 대기열(Queue) 및 타이밍 관리
    *   `typer.py`: UI 자동화를 통한 입력중 효과 구현
*   `ai/`:
    *   `chat.py`: OpenAI API 연동
    *   `utils.py`: 메시지 분할 및 딜레이 계산 로직
*   `state/`: 사용자 및 컨텍스트 상태 관리

## 🛠️ 필수 조건

*   **macOS** (아이메시지 사용 가능 환경)
*   **Python 3.x**
*   **Full Disk Access**: 터미널/에디터에 `~/Library/Messages/chat.db` 접근 권한 필요
*   **Accessibility (손쉬운 사용)**: '입력중 효과'를 위해 터미널/에디터에 컴퓨터 제어 권한 필요

## 🚀 설치 및 실행

1.  **패키지 설치**:
    ```bash
    pip install openai python-dotenv fastapi uvicorn
    ```

2.  **환경 설정 (`.env`)**:
    프로젝트 루트에 `.env` 파일을 생성하세요.
    ```env
    OPENAI_API_KEY=sk-proj-....
    TARGET_PHONE_NUMBER=+821012345678
    
    # 봇 트리거 설정 (True일 경우 /로 시작하는 말에만 대답)
    USE_TRIGGER=True
    TRIGGER_PREFIX=/
    ```

3.  **서버 실행**:
    ```bash
    python3 main.py
    ```

## ⚠️ 알려진 문제 (Known Issues)

*   **빈 메시지 무한 루프**: 사진이나 이모티콘 등 **내용이 없는(Empty Text)** 메시지를 받으면, 봇이 이를 무시하는 과정에서 '읽음 처리'가 누락되어 무한 루프에 빠질 수 있습니다. (현재 수정 중)
*   **화면 가로채기**: '입력중 효과' 기능이 활성화되면, 봇이 답장할 때마다 메시지 앱이 화면 맨 앞으로 튀어나옵니다. 불편하면 `imessage/manager.py`에서 끄면 됩니다.
