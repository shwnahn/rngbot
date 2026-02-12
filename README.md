# RingleBot (링글봇) - 모듈형 아키텍처

맥(Mac)의 아이메시지(iMessage)를 연동하여 동작하는 AI 영어 튜터 봇입니다.
FastAPI를 기반으로 리팩토링되었으며, 대화 맥락을 기억하고 자연스러운 영어 교정을 제공합니다.

## ✨ 주요 기능

*   **실시간 대화**: 아이메시지와 **SMS(문자)**를 모두 지원하며, 받은 방식 그대로 답장합니다.
*   **문맥 인식 (Context Awareness)**: 최근 대화 내용(History)을 기억하여 자연스러운 티키타카 가능
*   **자연스러운 타이핑**:
    *   메시지 길이에 따라 입력 시간을 조절하여 사람처럼 보냅니다.
    *   긴 답변은 문장 단위로 끊어서 전송합니다.
*   **영어 교정**: 링글 튜터 페르소나(Emily)가 학생(Kwon)의 문법을 자연스럽게 교정
*   **자동 응답**: 받은 모든 메시지에 자동으로 응답합니다.

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
    ```

3.  **서버 실행**:
    ```bash
    python3 main.py
    ```

## 📝 최근 변경사항 (v0.2.0)

*   ✅ **자체 메시지 필터링**: 봇이 자신이 보낸 메시지를 읽지 않도록 수정
*   ✅ **타이핑 시뮬레이션 제거**: 접근성 권한 문제로 인해 비활성화 (자연스러운 딜레이는 유지)
*   ✅ **트리거 모드 제거**: 모든 메시지에 자동 응답 (prefix 체크 불필요)
*   ✅ **서비스 타입 지원 강화**: iMessage/SMS 구분 처리 개선

## ⚠️ 알려진 문제 (Known Issues)

*   **빈 메시지 처리**: 사진이나 이모티콘 등 텍스트가 없는 메시지는 자동으로 무시됩니다.
