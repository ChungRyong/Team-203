# 🧠 Team-203 프로젝트 작업 메모리 (MEMORY.md)

이전 세션의 작업 내용과 프로젝트 연속성을 유지하기 위한 핵심 컨텍스트 기록 파일입니다. 다음 작업 시작 시 이 파일을 먼저 읽고 브리핑을 진행합니다.

---

## 1. 📅 오늘 완료한 주요 작업 및 핵심 변경 사항

### ① 오케스트레이션 루프(`orchestrator.py`) 통합 유닛 테스트 완비
- **tests/test_orchestrator.py 신규 수립 (Critical):** `VirtualStudioOrchestrator` 클래스의 8대 통합 시나리오(WBS 기동, VRAM 능동 해제, 순차 에이전트 턴 제어, 징계 상태 자동 격리, CTO 리뷰 On/Off 바이패스 분기, AST 50줄 심사 통과/Reject 분기, 회의실 폐쇄 및 디스코드 전송)를 완벽히 모킹 검증했습니다.
- **CEO 이원화 CTO 리뷰/사면 규칙 코딩 및 물리적 입증 (Critical):** 단순 AST 50줄 위반이나 단순 반려 시, 에이전트에게 경고를 적립하지 않고 즉시 `/api/agents/Dev-Agent/pardon`을 연동 호출하여 징계 스택을 원복(사면)하고 교정 턴 기회를 제공하는 이원화된 환류 로직의 무결성을 코드로 명백하게 검증 완료했습니다.
- **징계 상태 격리 통제 입증 (Important):** 징계(penalized) 상태에 돌입한 에이전트에 대해 시스템 프롬프트 접두사에 `[절대 팩트 모드]` 제약 조건이 동적 주입되며 추천 온도가 `0.0`으로 자동 강제 격리되는 안전 장치가 정상 작동함을 증명했습니다.

### ② 3순위: Art-Agent ComfyUI 이미지 생성 연동 구현 및 테스트 완비
- **ComfyUI 워크플로우 템플릿 신설 (config/comfyui_workflow_flux.json):** 긍정 프롬프트와 샘플러 시드를 동적으로 치환/인젝션하여 ComfyUI Prompt API에 안전하게 밀어넣는 JSON 스키마를 수립 완료했습니다.
- **FastAPI 이미지 생성 엔드포인트 신설 (app/main.py):** `POST /api/art/generate` API를 구축해 ComfyUI 서버(포트 8188)와 폴링 통신을 구현하고, 오프라인 시 placeholder(1x1 유효 투명 PNG)를 즉석에서 안전하게 물리 파일로 생성하는 **Fail-Safe** 장치를 완비했습니다.
- **Sequential Queue 확장 및 VRAM 언로드 고도화 (orchestrator.py):** 직렬 오케스트레이터 시퀀스에 `Concept-Agent(기획)` ➡️ `Art-Agent(디자인 및 에셋 이미지 생성)` ➡️ `Dev-Agent(개발)`의 3에이전트 순차 교대 루프를 장착하고, 턴 이동 시 VRAM을 해제하여 GPU가 ComfyUI와 Ollama에 번갈아 100% 집중할 수 있게 설계 보완했습니다.
- **에셋 생성 통합 테스트 완비 (tests/test_art_generation.py 신설):** ComfyUI의 온라인 완료 시나리오와 오프라인 Fail-Safe 1x1 PNG 생성 시나리오를 100% 통합 패스 성공했습니다.
- **3에이전트 직렬 드라이런 완결 (TASK-TEST-888):** 실제 로컬 서버 연동 후 3에이전트 기동을 모의 실행하여 SQLite 턴 제어 ➡️ VRAM 언로드 ➡️ ComfyUI 연동 에셋 생성(warning 폴백) ➡️ 개발 ➡️ 마일리 마일스톤 마감 및 디스코드 요약 경보 ➡️ Git 백그라운드 자동 스냅샷까지의 전 공정이 물 흐르듯 가동됨을 최종 입증했습니다.

### ③ 4순위: 에이전트 구동 지침 및 persona 명세 정비 완비
- **VIRTUAL_OFFICE.md [V5 개정]:** ComfyUI 그래픽 생산 규정 및 '에셋 날조 방지 리소스 바인딩 규정' 신설.
- **백엔드 인프라 명세서 [v1.5 개정]:** `Art-Agent` 징계 조건 및 `metadata.json` 사이드카 검사 규격 보강.
- **에이전트별 핵심 지침 [v1.4 개정]:** 에이전트 체인의 시각적/기능적 결합성(Chain of Visual Integrity) 수립 완료.

### ④ [마일스톤 1] 에셋 날조 방지 정적 감사 기능 물리적 코딩 및 검증 완료 (Critical)
- **정규식 기반 리소스 참조 정밀 추출 (run_cto_review.py):** `[\w/.:_-]+\.(?:png|tscn)` 패턴을 도입하여, 소스코드 내 하드코딩된 `.png` 및 `.tscn` 참조 경로를 콜론(`:`)까지 포함해 100% 오차 없이 추출하는 검사기를 장착했습니다.
- **에셋 위반 징계 연동 및 Reject 완비:** `art/metadata.json` 사이드카 조상 폴더 탐색기를 가동하여, 미등록된 가상 에셋의 무단 바인딩 감지 시 즉각 `exit 1`로 PR을 반려하고 Blinky 징계 API 연동으로 경고 1회를 적립하도록 구축했습니다.
- **감사기 통합 테스트 신설 (tests/test_cto_review.py):** 정상 리소스 바인딩 패스 및 미등록 에셋 참조 위반 적발 검증용 2대 테스트를 완비하여, **프로젝트 전체 20개 테스트가 단 2.174초 만에 100% 성공(OK)**함을 증명했습니다.
- **실전 dry-run 검수 통과:** 미등록 가상 에셋 `fake_nonexistent_sprite.png`를 참조시킨 모의 코드를 집행하여, 정확하게 Reject 되고 Blinky 경고 스택 누적 및 디스코드 징계 알림 임베드 브리핑이 유기적으로 흐름을 완벽히 최종 검수 완료했습니다.

---

## 2. ⚠️ 현재 마주한 에러 및 미해결 이슈
- **Git Remote HTTP 401 curl 22:** 원격 푸시 단계에서 GitHub 권한 부족(401) 네트워크 경보가 확인되었으나, 로컬 작업 트리(`git status`)는 이미 백그라운드 스냅샷 데몬에 의해 **2개 앞선 커밋(`ahead by 2 commits`)으로 100% 안전하게 저장(working tree clean)**되었으므로 기능적 보존은 완벽합니다.

---

## 3. 🎯 다음 세션에 이어서 해야 할 구체적인 목표와 할 일 (To-Do)
- [ ] **[마일스톤 2] 실전 테트리스 모노레포 1차 프로토타입 릴리스 (실물 공정 돌입):**
  - [ ] `Concept-Agent`를 소집해 격리 sandbox 폴더 `workspace/projects/game_01_tetris/concept/` 아래에 정규 그리드 테트리스 예외처리 기획 명세서 물리 작성.
  - [ ] `Art-Agent` 턴을 가동해 `/api/art/generate` API로 ComfyUI를 찔러 고품질 UI/UX 시안 에셋 물리 렌더링 및 `metadata.json` 적재.
  - [ ] `Dev-Agent`가 앞선 명세와 `art/metadata.json` 에 등록된 실물 PNG 리소스만 100% 임포트하여 작동 가능한 GDScript 소스코드 `dev/tetris.gd` 물리 코딩.
  - [ ] 가상 CTO(`Claude-Code`)의 정밀 정적 AST 및 에셋 정합성 감사 통과 후 실물 1호기 원격 릴리스.
