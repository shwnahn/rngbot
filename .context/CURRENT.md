# RingleBot Context (v0.4.0)
**Last Updated**: 2026-02-12  
**Status**: 🟢 Production Ready

---

## 📌 프로젝트 개요

**목적**: macOS iMessage 기반 AI 영어 튜터 봇  
**기술 스택**: Python 3.x, FastAPI, OpenAI GPT-4o-mini, SQLite, AppleScript  
**대상 사용자**: 링글 학생 (Kwon)  
**튜터 페르소나**: Emily (Business Email Writing 수업)

---

## ✅ 최근 완료 작업 (2026-02-12)

### Phase 1: 기반 개선
- ✅ 타이핑 속도 최적화 (5초 → 3초 최대, 평균 0.5-2초)
- ✅ 언어 자동 감지 (한글 비율 30% 기준 ko/en 구분)

### Phase 2: 스마트 메시지 분할
- ✅ 짧은 응답(5단어 미만) 분할 안함
- ✅ 문단, 목록, 화제 전환 감지하여 의미 단위 분할
- ✅ 단일 기호/숫자 자동 병합
- ✅ 구조화된 내용(목록) 유지

### Phase 3: 응답 큐 관리
- ✅ PriorityQueue 구현 (HIGH/NORMAL/LOW)
- ✅ 새 메시지 도착 시 이전 응답 자동 중단
- ✅ 세션 ID 기반 메시지 필터링
- ✅ 큐 상태 모니터링

### 버그 수정
- ✅ 대화 히스토리 복원 (봇 응답이 히스토리에 누락되던 문제 수정)
- ✅ 큐 블로킹 해결 (세션 ID 필터링으로 안전한 중단)

**커밋 히스토리**:
```
2e5b333 docs: README 업데이트 (v0.4.0 변경사항 반영)
cfec189 fix: 대화 히스토리 쿼리 개선으로 봇 응답 맥락 복원
83ae0de feat: 우선순위 큐 기반 응답 중단 기능 구현
1849f70 feat: 언어 감지 및 대화 상태 관리 기능 추가
9091adc feat: 타이핑 속도 최적화 및 스마트 메시지 분할 구현
```

---

## 🏗️ 현재 시스템 상태

### 설정 값
- **메모리 임계값**: 5 (테스트용, 원래 30)
- **타이핑 속도**: 15-25 chars/sec
- **최대 지연**: 3초
- **대화 히스토리**: 최근 20개 메시지

### 데이터베이스 상태
- **위치**: `~/Documents/rngbot/data/memory.db`
- **크기**: 20KB
- **요약 개수**: 1개 (테스트 데이터)
- **실제 대화 요약**: 아직 없음 (메시지 카운트 < 5)

### 실행 환경
- **Python**: 3.x (venv)
- **서버**: FastAPI + Uvicorn (localhost:8000)
- **메시지 폴링**: 1초 간격
- **로깅**: DEBUG 레벨 (상세)

---

## 📂 핵심 파일 구조

```
rngbot/
├── main.py                 # 메인 서버, 메시지 폴링
├── imessage/
│   ├── manager.py         # PriorityQueue, 응답 중단
│   ├── reader.py          # iMessage DB 읽기 (히스토리 로드)
│   └── sender.py          # AppleScript 메시지 전송
├── ai/
│   ├── chat.py            # OpenAI API 호출
│   ├── utils.py           # 스마트 분할, 타이핑 딜레이
│   └── grammar.py         # 튜터 페르소나 정의
├── memory/
│   ├── summary.py         # 대화 요약 생성
│   └── storage.py         # SQLite 저장/로드
├── state/
│   ├── context.py         # 대화 맥락, 상태 관리
│   └── user.py            # 사용자 설정
└── data/
    └── memory.db          # 요약, 프로필 DB
```

---

## 🎯 활성 기능

### 메시지 흐름
1. **Polling** (main.py): iMessage DB 1초마다 체크
2. **새 메시지 감지**: 
   - 큐 초기화 (이전 응답 중단)
   - 세션 ID 증가
   - 언어 감지 (ko/en)
3. **AI 응답 생성**:
   - 히스토리 로드 (최근 20개)
   - 요약 컨텍스트 포함
   - GPT-4o-mini 호출
4. **스마트 분할**: 의미 단위로 분할
5. **큐 처리**: 
   - 자연스러운 딜레이 (0.5-2초)
   - 순차 전송
   - 오래된 세션 메시지 스킵

### 메모리 시스템
- **단기**: 최근 20개 메시지 (iMessage DB)
- **중기**: 5개마다 자동 요약 (GPT-4o-mini)
- **장기**: SQLite에 영구 저장

---

## ⚠️ 알려진 이슈

**현재 이슈**: 없음

**테스트 필요**:
- [ ] 메모리 임계값 5 → 30 복원 후 장기 테스트
- [ ] 긴 대화에서 요약 품질 확인
- [ ] 여러 메시지 연속 전송 시 중단 로직 검증

---

## 🔜 다음 작업 후보

### 우선순위 높음
- [ ] 메모리 임계값을 30으로 되돌리기
- [ ] 실제 대화 테스트 (30개 메시지)
- [ ] 요약 DB 확인 및 로드 테스트

### 우선순위 중간
- [ ] 사용자 프로필 자동 추출 (학습 목표, 약점)
- [ ] Graceful shutdown 구현
- [ ] 에러 핸들링 강화

### 우선순위 낮음
- [ ] 웹 대시보드 (대화 히스토리 조회)
- [ ] 다중 사용자 지원
- [ ] 성능 모니터링 (Prometheus/Grafana)

---

## 💡 Agent 작업 시 참고사항

### 코드 수정 시
1. **테스트**: 서버 재시작 후 실제 메시지로 검증
2. **로깅**: DEBUG 레벨로 상세 로그 확인
3. **커밋**: 의미 단위로 분리하여 커밋
4. **문서**: 이 파일(CURRENT.md) 업데이트

### 디버깅 팁
- 로그 위치: 터미널 출력 (파일 저장 안함)
- DB 확인: `sqlite3 ~/Documents/rngbot/data/memory.db`
- 히스토리 확인: main.py의 DEBUG 로그
- 큐 상태: `[Queue Status]` 로그

### 중요 제약사항
- macOS 전용 (iMessage, AppleScript)
- Full Disk Access 필요 (chat.db 접근)
- OpenAI API 키 필요 (.env)
- Python 3.x 필수

---

## 📞 컨텍스트 사용 예시

```markdown
Agent야, 다음 작업을 해줘:
[작업 내용]

참고: .context/CURRENT.md 확인
```

**이 문서는 작업 전후로 업데이트하세요!**
