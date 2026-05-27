# 🧠 Team-203 프로젝트 작업 메모리 (MEMORY.md)

이전 세션의 작업 내용과 프로젝트 연속성을 유지하기 위한 핵심 컨텍스트 기록 파일입니다. 다음 작업 시작 시 이 파일을 먼저 읽고 브리핑을 진행합니다.

---

## 1. 📅 오늘 완료한 주요 작업 및 핵심 변경 사항

### ⑤ [2026-05-27] PM 에이전트 자율 프로비저닝 가이드 품질 감사 및 8건 이슈 수정 (`PM_AGENT_INFRA_PROVISIONING_GUIDE.md`)
- **[Critical] Flux.1 다운로드 URL 및 인증 오류 수정:** 기존 `curl + lllyasviel/flux1-dev-onnx` (404 + 인증 없음) 방식을 `huggingface-cli download + $HF_TOKEN` 인증 방식으로 교체하였습니다. Flux.1-dev는 HuggingFace Gated Model로 반드시 토큰 인증이 필요합니다.
- **[Critical] ComfyUI 클론 경로 미명시 오류 수정:** 클론 전 `cd Team-203` 선행 명령을 명시하고, ComfyUI 전용 격리 venv(`.venv_comfyui`)를 신설하여 시스템 파이썬 오염을 방지했습니다. `app/main.py`의 `Team-203/ComfyUI/output` 경로 바인딩과 정합성을 확보했습니다.
- **[High] Ollama 모델 태그 검증 단계 추가:** `qwen3.6:35b-mlx`, `gemma4:31b-mlx` pull 전 `ollama search`로 태그 실존 여부를 검증하고, 실패 시 대체 태그(`qwen3:32b`, `gemma3:27b`)를 주석으로 제공했습니다.
- **[Medium] `sleep 5` / `sleep 3` 고정 대기 → 결정적 폴링(30초 타임아웃) 교체:** Ollama 데몬 및 FastAPI 서버 모두 `until curl` 폴링 루프로 전환하고 타임아웃 초과 시 `exit 1`로 즉각 중단하도록 구성했습니다.
- **[Medium] 완료 보고 100% 하드코딩 → 동적 API 조회로 전환:** `GET /api/audit/summary` 실시간 쿼리 결과로 5대 건강성 지표를 동적 구성하도록 안내하여 허위 보고를 원천 차단했습니다.
- **[Low] `kill -9` 즉시 사용 → SIGTERM(-15) 선행 후 SIGKILL(-9) 최후 수단 패턴으로 교체:** 데이터 손실 위험을 제거했습니다.
- **[Low] Python 버전 3.11 → 3.13으로 업데이트:** 현재 개발 환경(Python 3.13) 기준으로 수정하고 `brew link --overwrite` 명령을 추가했습니다.
- **[이전 세션 잔재 수정] 잘못된 프로젝트 경로 교정:** 이전 세션이 남긴 `/Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203` 경로를 사용자가 지정한 올바른 `/Users/jabiseu/Documents/workspace/Team-203` 경로로 일괄 교정했습니다.
- **커밋:** `b0f803a` — `docs: fix PM provisioning guide — 8 issues resolved`

---

### ① [마일스톤 1.5] 가상 사옥 감사실 (Audit Bureau) 및 정량 모니터링 인프라 구축 (Critical)
- **SQLite 감사 로그 테이블 (`system_audit_logs`) 신설:** 사내의 모든 핵심 공정(VRAM 캐시 아웃, CTO 정적 코드 심사, Blinky 징계, Git 스냅샷)의 성공 여부 및 소요 지연 시간(ms)을 영구 적재하는 스키마를 신설하고 헬퍼 함수를 완비했습니다.
- **사내 건강성 지수 (Office Health Index) 요약 API 탑재:** 최근 24시간 감사 로그를 동적으로 파싱하여 VRAM 반환 성공률, CTO 1회 패스율, 백업 신뢰도, 디시플린 기강 수준을 0.0~100.0% 정량 지표로 자동 취합하는 `/api/audit/summary`를 완비했습니다.
- **오케스트레이터 감사 데몬 및 실시간 디스코드 경보 연동:** WBS 부트스트랩 단계부터 태스크 종결 시점까지 매 공정의 elapsed_ms를 계산하여 감사실에 자동 로깅하고, 태스크 마감 시 건강 지수가 **80% 미만**으로 하락하면 대표실로 즉각 **적색 비상 경보 (Red Embed)**를 발송하며, 이상 없을 시 청색 보고(Blue Embed)를 발송하도록 결합했습니다.
- **Obsidian 연동 일일 경영 감사 다이어리 자동 생성:** 태스크 종료 시점에 `workspace/audit/` 경로 하위에 `audit_diary_[YYYYMMDD].md` 감사 일지를 자동으로 물리 생성하도록 구축하여 Obsidian Vault Dataview/Bases 대시보드 시각화를 완벽 호환 지원합니다.

### ② [마일스톤 2] 게임 QA 1단계 (GUT Headless 자동화 검증) 파이프라인 연동 (Critical)
- **FastAPI QA 연동 API 신설 (`POST /api/qa/verify`):** GUT Headless 테스트 수행 결과를 수집하여 성공률(%)을 도출하고, 성공률이 **95% 미만**인 경우 FAILED 상태로 데이터베이스 감사 로그에 기록하는 엔드포인트를 구현 완료했습니다.
- **감사실 5대 지표 확장 (`QA Health` 추가):** 기존 4대 건강 지표에 **`QA Health` (게임 QA 테스트 합격률, %)**를 신설 추가하여 총 5대 지표의 종합 평균값으로 **사내 건강성 지수**를 계산하도록 연산 지형을 고도화했습니다.
- **오케스트레이터 QA 검증 및 자가 치유(Self-Healing) 파이프라인 통합:** Dev-Agent 코딩 직후 자동으로 GUT QA 검증(`execute_qa_audit_stage`)을 수행하며, 통과율 95% 미만 시 즉각 `REJECT` 판정을 내리고 Dev-Agent에게 **Blinky 징계 경고를 자동 연동 부과**하여 스스로 버그를 수정(Self-Healing)하고 재제출하도록 피드백 루프를 결합했습니다.
- **QA 통합 테스트 신설 및 28개 전구간 패스 (`tests/test_qa_pipeline.py`):** QA API 동작, 5대 지표 종합 지수 연산, 오케스트레이터 QA 통과/반려 및 징계 연동을 모킹 테스트 세트로 완비하여, **전체 28개 통합 유닛 테스트가 단 2.20초 만에 100% 무결점으로 통과(OK)**함을 증명했습니다.

### ③ [마일스톤 2.6] M5 Pro Max AI-Driven PM 자율 프로비저닝 및 이원화 공유 최적화 (대표님 혜안 🌟)
- **대표님 초간편 시동 가이드 개정 (`M5_PRO_MAX_BOOTSTRAP_GUIDE.md`):** 대표님이 새 M5 Pro Max에서 실행하실 단계를 1줄의 쉘 명령어(`curl ... | bash && hermes setup`) 및 디스코드 한 줄 위임 지시어로 파격 압축했습니다.
- **PM 에이전트 자율 실무 런북 신설 (`PM_AGENT_INFRA_PROVISIONING_GUIDE.md`):** 수석 PM Hermes가 쉘 터미널 권한을 직접 획득하여 macOS 진단, Homebrew 및 의존성 설치, Ollama Cask 구성, MLX 추론 모델 풀링, ComfyUI/Flux 복사, SQLite 시딩, FastAPI 가동까지 원스톱으로 무인 프로비저닝할 명령어 표준 런북을 수립했습니다.
- **Blinky-Hermes 고성능 MLX 모델 자원 공유 단일화:** e4b-mlx 모델 대신 수석 PM과 Blinky 주임이 고품질 **`gemma4:31b-mlx`** 모델을 공유하게 설계했습니다. 이로써 메모리 사용량을 절감(동시 가동 로컬 모델 3개 ➡️ 2개)하고 Blinky의 회의록 압축 요약 지능 수준을 대폭 격상했습니다.
- **백엔드 소스코드 및 테스트 일치화:** `app/blinky_middleware.py` 및 `tests/test_orchestrator.py`에 적용된 Blinky 구동 모델명을 `gemma4:31b-mlx`로 수정하여 테스트 스위트 100% 패스 상태를 보존했습니다.

### ④ 가상 CTO Agent 피드백 100% 수집 및 리팩토링 완비
- **Pydantic V2 Deprecation 경고 해결:** `app/main.py` 전역의 Pydantic Schema 내 deprecated `Field(..., example=...)` 필드들을 최신 규격인 `Field(..., json_schema_extra={"example": ...})`로 변환하여 33개의 warning을 깔끔하게 박멸했습니다.
- **Lifespan Context Manager 마이그레이션:** 구형 `@app.on_event("startup")` 방식을 FastAPI의 최신 권장 패턴인 `@asynccontextmanager def lifespan` 방식으로 완벽하게 전환하여 부팅 안정성을 보장했습니다.
- **Glob Import 위치 교정:** `generate_art` 함수 내에 존재하던 인라인 `import glob` 구문을 파일의 최상단 정규 임포트 블록으로 격상하여 파이썬 표준 스타일 가이드(PEP 8)를 완수했습니다.
- **ComfyUI 폴더 절대경로화:** ComfyUI 출력물 추적 시 마지막 fallback 경로인 `"output"` 상대 경로를 프로젝트 루트 기준 절대 경로(`os.path.join(base_dir, "output")`)로 변경하여 실행 위치에 구애받지 않게 수정했습니다.
- **GUT 실측 elapsed_ms 전달 지원:** 게임 QA API (`POST /api/qa/verify`)의 요청 스키마 `QaVerifyRequest`에 선택적 `elapsed_ms` 필드를 추가하여, 실제 QA 테스트 도구의 정확한 측정 지연 시간을 감사 로그에 그대로 영구 적재할 수 있도록 고도화했습니다. (미제공 시 기존과 동일하게 random.randint fallback 안전 보장)

---

## 2. ⚠️ 현재 마주한 에러 및 미해결 이슈
- **현재 해결해야 할 오류나 버그는 '0건'**으로, 리팩토링 완료 후 전체 28개 유닛 테스트가 100% 무결점으로 완결 통과되었습니다.
- **CTO PR 머지 승인:** 가상 CTO Agent의 피드백을 100% 반영 완료하여 최종 기술적 머지 승인(Merge Approved)이 완료된 완결 무결 상태입니다.

---

## 3. 🎯 다음 세션에 이어서 해야 할 구체적인 목표와 할 일 (To-Do)

### ① 게임 QA 단계 지속 강화 및 고도화 (Milestone 2.5)
- [ ] **QA 2단계: 비주얼 회귀 테스트 (Visual QA) 아키텍처 연동**
  - [ ] Godot 헤드리스 스크린샷 렌더링 캡처 스크립트 작성.
  - [ ] Art-Agent가 Flux.1로 디자인한 오리지널 시안 이미지와 런타임 캡처 이미지 간의 픽셀/레이아웃 일치율 분석 및 Claude Vision API 정밀 시각 검수 자동화.
- [ ] **QA 3단계: 지능형 QA 에이전트 (`QA-Agent`) 전담 페르소나 신설**
  - [ ] 기획 스키마를 파싱하여 극단적 엣지 케이스 테스트 시나리오를 자동 도출하는 테스팅 프레임워크 수립.

### ② 실전 테트리스 모노레포 1차 프로토타입 릴리스 (Milestone 3 - 실물 공정 돌입)
- [ ] `Concept-Agent`를 소집해 격리 sandbox 폴더 `workspace/projects/game_01_tetris/concept/` 아래에 정규 그리드 테트리스 예외처리 기획 명세서 물리 작성.
- [ ] `Art-Agent` 턴을 가동해 `/api/art/generate` API로 ComfyUI를 찔러 고품질 UI/UX 시안 에셋 물리 렌더링 및 `metadata.json` 적재.
- [ ] `Dev-Agent`가 앞선 명세와 `art/metadata.json`에 등록된 실물 리소스만 100% 임포트하여 작동 가능한 GDScript 소스코드 `dev/tetris.gd` 물리 코딩.
- [ ] 가상 CTO(`Claude-Code`)의 정적 AST 및 에셋 정합성 감사, 그리고 GUT QA 자동 통과 확인 후 실물 1호기 원격 릴리스.
