# 🧠 Team-203 프로젝트 작업 메모리 (MEMORY.md)

이전 세션의 작업 내용과 프로젝트 연속성을 유지하기 위한 핵심 컨텍스트 기록 파일입니다. 다음 작업 시작 시 이 파일을 먼저 읽고 브리핑을 진행합니다.

---

## 1. 📅 오늘 완료한 주요 작업 및 핵심 변경 사항

### ① 4번: Blinky 징계 집행기(Penalty Automator) 명세 공식화 완료
- `[Team-203] 에이전트별 페르소나 및 백엔드 인프라 명세서 (v1.4).md`에 'Blinky 징계 집행기' 장을 신설하고 경고 스택 누적, 3진 아웃 삼진 징계, 디스코드 빨간색 경보, 시스템 프롬프트 접두사 인젝션, **추론 온도 `0.0` 강제 고정** 및 API 규격 문서를 공식 기록으로 완벽 정리했습니다.

### ② 2번: CTO 에이전트(`Claude-Code`) CLI 래퍼 개발 완료
- **`run_cto_review.py` 신설:** 파이썬 구문 트리(AST) 분석을 통해 함수의 물리 코드 라인수(주석/docstring 제외)가 50줄을 넘는지 정밀하게 로컬 사전 검사하는 CLI 래퍼 개발을 완료했습니다.
- **징계 연동 & Fail-Safe:** 50줄 초과 시 `Dev-Agent`에게 자동으로 징계 경고를 누적시키고 반려시키며, Claude Pro CLI 부재나 레이트 리밋(429) 감지 시 DB를 `PASSED_WITHOUT_CLAUDE` 상태로 전환해 빌드를 통과시키는 무중단 예외 처리를 탑재 완료했습니다.

### ③ 3번: Ollama 메모리 능동 비우기 API 연동 완료
- `app/main.py`에 `POST /api/vram/unload` 엔드포인트를 탑재하여, Ollama API에 `keep_alive: 0`을 전송하고 GPU VRAM 캐시를 OS 레벨로 강제 반환하게 하여 메모리 한계를 지능적으로 방어하도록 구현했습니다.

### ④ 5번: Git 자동 백업 스냅샷 프로토콜 탑재 완료
- **자동 롤백 스냅샷:** 소회의실이 폐쇄(`close`)되거나 Blinky가 20턴 압축 요약을 완료해 세션이 리셋되는 시점에 백그라운드에서 `git add . && git commit`을 안전하게 자동 트리거하여 에이전트들의 코드 실수 유실을 차단하도록 완비했습니다.
- **바이너리 DB 격리 (옵션 A):** 대표님 결정에 의거하여 `hermes_soul.db` 파일은 Git 충돌 및 대용량 오버플로우 방지를 위해 `.gitignore` 예외 처리를 그대로 유지(Git 추적 대상에서 제외)하고, 오직 소스코드 및 문서 텍스트 산출물만 안전하게 Git 스냅샷에 동화시켰습니다.

### ⑤ 100% 통합 검증 성공 및 GitHub 최종 배포 완료
- `tests/test_cto_review.py`, `tests/test_vram_unload.py`, `tests/test_penalties.py`를 신설 완료했습니다.
- `python3 -m unittest discover tests` 가동 결과 **전체 7개 테스트 케이스가 단 0.142초 만에 100% 성공(OK)**을 달성했습니다.
- 검증된 모든 최신 명세 문서와 파이썬 코드를 [GitHub 원격 저장소](https://github.com/ChungRyong/Team-203)의 `main` 브랜치에 깨끗하게 푸시 배포 동기화 완료했습니다.

### 📄 변경 및 추가된 핵심 파일 목록
* **[NEW]** `run_cto_review.py` (AST 기반 CTO Pro 50줄 정밀 분석 CLI 래퍼)
* **[NEW]** `tests/test_cto_review.py` (CTO 래퍼 및 Fail-Safe 통합 테스트)
* **[NEW]** `tests/test_vram_unload.py` (VRAM Unload Mock/Fail-Safe 통합 테스트)
* **[MODIFY]** `app/database.py` (run_git_snapshot 백그라운드 Git 자동화 헬퍼 추가)
* **[MODIFY]** `app/main.py` (VRAM Unload API 및 Git Snapshot 연동 추가)
* **[MODIFY]** `app/blinky_middleware.py` (20턴 압축 시점의 Git Snapshot 연동 추가)
* **[MODIFY]** `[Team-203] 에이전트별 페르소나 및 백엔드 인프라 명세서 (v1.4).md` (Blinky 징계 집행 명세 추가)

---

## 2. ⚠️ 현재 마주한 에러 및 미해결 이슈
- **특이사항 없음:** 전 구간 통합 테스트가 100% PASS 하였으며, 어떠한 오류나 리소그 랙 현상 없이 매끄럽게 컴파일 및 구동됩니다.

---

## 3. 🎯 다음 세션에 이어서 해야 할 구체적인 목표와 할 일 (To-Do)
- [ ] **에이전트별 독립 샌드박스 오케스트레이션 실행:** `Concept-Agent`와 `Dev-Agent` 프로세스가 신설된 징계 및 AST 래퍼 통제를 받으며 소회의실 API를 종단 교환하는 라이브 기획-개발 구동 시나리오 검증.
- [ ] **Art-Agent ComfyUI 이미지 생성 연동:** UI/UX 시안 에셋 보관 공간과 Flux.1 API 통신 바인딩 프로토콜 기획 및 설계.
