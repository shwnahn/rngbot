# RingleBot (링글봇) - 모듈형 아키텍처

맥(Mac)의 아이메시지(iMessage)를 연동하여 동작하는 AI 영어 튜터 봇입니다.
FastAPI를 기반으로 리팩토링되었으며, 대화 맥락을 기억하고 자연스러운 영어 교정을 제공합니다.

## ✨ 주요 기능

*   **실시간 대화**: 아이메시지를 통해 봇과 실시간으로 영어 대화 가능
*   **문맥 인식 (Context Awareness)**: 최근 대화 내용(History)을 기억하여 자연스러운 티키타카 가능
*   **영어 교정**: 링글 튜터 페르소나(Emily)가 학생(Kwon)의 문법을 자연스럽게 교정
*   **모듈형 구조**: 유지보수가 쉬운 FastAPI 백엔드 구조

## 📂 프로젝트 구조

*   `main.py`: 메인 서버 & 메시지 감지 루프 (FastAPI)
*   `imessage/`:
    *   `reader.py`: `chat.db`에서 메시지 읽기 & 대화 기록 조회
    *   `sender.py`: AppleScript를 이용한 메시지 발송
*   `ai/`:
    *   `chat.py`: OpenAI API 연동
    *   `grammar.py`: 시스템 프롬프트 관리
*   `state/`:
    *   `user.py`: 사용자 설정 관리 (이름, 전화번호)
    *   `context.py`: 마지막 메시지 위치 추적
*   `ringle/`:
    *   `mock_data.py`: 가상 수업 데이터 & 학생/튜터 정보

## 🛠️ 필수 조건

*   **macOS** (아이메시지 사용 가능 환경)
*   **Python 3.x**
*   **Full Disk Access (전체 디스크 접근 권한)**:
    *   터미널(Terminal) 또는 VSCode가 `~/Library/Messages/chat.db`를 읽을 수 있어야 합니다.
    *   *설정 > 개인정보 보호 및 보안 > 전체 디스크 접근 권한*에서 사용하는 터미널/에디터를 체크해주세요.

## 🚀 설치 및 실행

1.  **패키지 설치**:
    ```bash
    pip install openai python-dotenv fastapi uvicorn
    ```

2.  **환경 설정 (`.env`)**:
    프로젝트 루트에 `.env` 파일을 생성하고 아래 내용을 입력하세요.
    ```env
    OPENAI_API_KEY=sk-proj-.... (본인의 OpenAI 키)
    TARGET_PHONE_NUMBER=+821012345678 (봇과 대화할 상대방의 번호)
    ```
    *   주의: `TARGET_PHONE_NUMBER`는 **상대방(학생)의 핸드폰 번호**입니다.

3.  **학생 이름 변경** (옵션):
    `ringle/mock_data.py` 파일의 `STUDENT_NAME` 변수를 수정하여 본인의 이름으로 설정하세요.

4.  **서버 실행**:
    ```bash
    python3 main.py
    ```
    또는
    ```bash
    uvicorn main:app --reload
    ```

## ❓ 문제 해결

*   **DB Locked 오류**: `chat.db`는 시스템이 수시로 쓰기 작업을 합니다. 봇은 읽기 전용(`ro`) 모드로 접근하지만, 간혹 충돌이 날 수 있습니다. 잠시 후 다시 시도하면 됩니다.
*   **메시지 인식 안됨**:
    *   `.env`의 전화번호 형식이 맞는지 확인하세요. (한국 번호 예: `+8210...`)
    *   "나와의 채팅"(내 폰 -> 내 맥)인 경우 `imessage/reader.py` 로직상 무시될 수 있습니다. 가능하면 다른 번호로 테스트하세요.
