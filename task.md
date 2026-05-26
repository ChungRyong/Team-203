# 🎯 Team-203 인프라, 백엔드, CTO dynamic AST, central settings, requirements minimalization 및 M5 Pro Max 자율 프로비저닝 완비 태스크 보드 (task.md)

---

## ⚖️ 1. 징계 코어 및 프롬프트 인젝터 구현 & 문서화 (4번 완료)
- [x] `app/penalties.py` 신설 구현
  - [x] `get_agent_system_prompt(agent_name, base_prompt)` 함수 구현 (징계 상태에 따른 템플릿 인젝션)
  - [x] `enforce_penalty_check(agent_name, reason)` 함수 구현 (3회 경고 누적 시 삼진 아웃 집행 및 디스코드 경보 릴레이)
- [x] 사내 공식 명세서 최신화 및 징계 가이드라인 수록
  - [x] `[Team-203] 에이전트별 페르소나 및 백엔드 인프라 명세서 (v1.4).md`에 'Blinky 징계 집행기' 공식 명세 및 징계 접두사, `temperature=0.0` 규칙 수록

## 👑 2. CTO 에이전트(`Claude-Code`) CLI 래퍼 개발 & 동적 ON/OFF 제어 (2번 완료)
- [x] `run_cto_review.py` CLI 래퍼 개발
  - [x] 파이썬 `ast` 모듈 기반 주석/docstring 제외 순수 50줄 엄격 제한 알고리즘 탑재 (ast.Constant 단일화로 3.14 미래 대비 완료)
  - [x] 50줄 초과 위반 시 `/api/agents/Dev-Agent/penalize` API 연동 및 경고 적립
  - [x] 로컬 Claude CLI 부재 또는 429 에러 대응 `PASSED_WITHOUT_CLAUDE` Fail-Safe 구현 (PATCH API 기반 부분 수정으로 400 에러 완벽 해결)
- [x] 수석PM(Hermes) On/Off 통제 제어권 설계
  - [x] SQLite `system_settings` 테이블 신설 및 영속성 구성
  - [x] API `GET /api/config/cto-review` 및 `POST /api/config/cto-review` 구현
  - [x] `run_cto_review.py` 에 On/Off 우회 로직 주입 완료 (비활성화 시 정적 AST 필터 및 Claude 검수 완전 Bypass 및 자동 성공 처리)
  - [x] `bootstrap.py` 씨딩 조치로 스튜디오 초기 구동 시 **기본값 OFF('0')** 처리로 안정 우선 가동 보장
- [x] `tests/test_cto_review.py` 에 On/Off 우회 검증 테스트 `test_cto_review_disabled_bypasses_all` 완비

## 🔌 3. Ollama 메모리 능동 비우기 API 구현 (3번 완료)
- [x] `app/main.py`에 `POST /api/vram/unload` 엔드포인트 구현
  - [x] Ollama API에 `keep_alive: 0` 전송 및 OS VRAM 캐시 해제 유도
  - [x] Ollama 오프라인 시 warning과 함께 우회하는 Fail-Safe 구현
- [x] `tests/test_vram_unload.py` 통합 테스트 세트 완비

## 🔄 4. Git 자동 스냅샷 백업 및 아카이빙 연동 (5번 완료)
- [x] `app/database.py`에 `run_git_snapshot` 헬퍼 함수 구현
  - [x] `git add . && git commit`을 백그라운드로 안전하게 처리하고 에러 시 우아하게 우회
- [x] 회의실 폐쇄 및 Blinky 20턴 압축 트랜잭션 시 자동 Git 커밋 연동
  - [x] `app/main.py` 의 `close_meeting_room` 내부 연동 및 **대화 메시지 아카이빙 동기화(`is_archived = 1`) 보완 완료**
  - [x] `app/blinky_middleware.py` 의 20턴 압축 트랜잭션 내부 연동 완료

## ⚙️ 5. 환경 변수 및 중앙 집중식 설정 완비 (CTO 피드백 피드백)
- [x] 루트 `.env.example` 및 `config/settings.py` 중앙 로더 구축
- [x] `app/discord_relay.py` 설정 중앙 결합 완료 (DISCORD_WEBHOOK_URL 임포트)
- [x] `app/blinky_middleware.py` 설정 중앙 결합 완료 (OLLAMA_GENERATE_URL 임포트)
- [x] `app/main.py` 설정 중앙 결합 완료 (OLLAMA_CHAT_URL 임포트)
- [x] **requirements.txt 의존성 극단적 미니멀리즘 완비 (httpx 줄 마저 삭제 완료)**

## 🧪 6. 전 구간 통합 검증 및 원격 배포 완료
- [x] `python3 -m unittest discover tests` 가동 결과 전체 8개 테스트 **100% OK** 패스 및 DeprecationWarning 박멸 성공
- [x] GitHub `ChungRyong/Team-203` 원격 저장소 `main` 브랜치에 최종 푸시 및 동기화 완료

## 👑 7. 오케스트레이션 루프 검증 및 이원화 사면 로직 증명 (100% 완료)
- [x] `tests/test_orchestrator.py` 신규 유닛 테스트 작성
  - [x] `test_initialize_studio` (태스크 등록 및 회의실 개설 검증)
  - [x] `test_unload_agent_vram` (VRAM 해제 API 호출 검증)
  - [x] `test_run_agent_turn_normal` (일반 에이전트 동적 프롬프트 & 대화 연동 검증)
  - [x] `test_run_agent_turn_penalized` (징계 에이전트 강제 온도 0.0 & 프롬프트 인젝션 검증)
  - [x] `test_execute_cto_review_flow_bypassed` (CTO 리뷰 비활성화 시 Bypass 검증)
  - [x] `test_execute_cto_review_flow_passed` (CTO 리뷰 활성화 시 통과 검증)
  - [x] `test_execute_cto_review_flow_rejected_and_pardoned` (AST 50줄 초과 탈락 시 즉시 사면 연동 검증)
  - [x] `test_finalize_studio` (회의실 닫기, 태스크 COMPLETED, 디스코드 청색 마일스톤 보고 검증)
- [x] `python -m unittest tests/test_orchestrator.py` 성공 확인 (8/8 Pass 완료)
- [x] `python -m unittest discover tests` 전체 16개 테스트 통과 성공 확인 (16/16 Pass 완료)
- [x] `python orchestrator.py TASK-TEST-999` 모의 실구동 주행(live dry-run) 진행 및 SQLite/디스코드 로그 최종 검수 (100% 완결 통과 완료)

## 🎨 8. 3순위: Art-Agent ComfyUI 이미지 생성 연동 구현 및 검증 (100% 완료)
- [x] `bootstrap.py` 파일의 물리 에셋 art/ 폴더 생성 규칙 보완 및 DB 마이그레이션 확인
- [x] `config/comfyui_workflow_flux.json` 워크플로우 API 템플릿 신설
- [x] `app/main.py`에 `POST /api/art/generate` 이미지 자동 생성 및 비동기 폴링 ➡️ Fail-Safe 연동 엔드포인트 구현
- [x] `orchestrator.py` 의 Sequential Queue에 `Art-Agent` 턴 단계(VRAM 해제 ↔ 이미지 생성 교대) 정식 편입
- [x] `tests/test_art_generation.py` 신규 생성 및 ComfyUI 모킹 폴링, 오프라인 시 placeholder 연동 100% 검증
- [x] `tests/test_orchestrator.py` 에 `Art-Agent` 순차 실행 단계 모킹 및 검증 보완 추가
- [x] `python3 -m unittest discover tests` 전체 18개 테스트 (기존 16개 + 신규 2개) 100% OK 패스 증명
- [x] `python orchestrator.py TASK-TEST-888` 3에이전트 직렬 모의 구동 테스트 최종 검수

## 📄 9. 4순위: 에이전트 구동 지침 및 persona 명세 정비 (100% 완료)
- [x] `VIRTUAL_OFFICE.md`에 ComfyUI 그래픽 생산 및 리소스 바인딩 규칙 개정 반영 (V5 리뉴얼 완료)
- [x] `[Team-203] 에이전트별 페르소나 및 백엔드 인프라 명세서 (v1.5).md` 신설 및 징계, 메타데이터 사이드카 검사 규격 보강 (완료)
- [x] `[Team-203] 에이전트별 페르소나 및 핵심 지침 (v1.4).md` 신설 및 연쇄 시각적/기능적 결합 준수 행동지침 반영 (완료)
- [x] 개정된 마크다운 문서 최종 검수 및 GitHub Push 배포 (완료)

## 🛡️ 10. 마일스톤 1: 에셋 날조 감사 기능 물리적 코딩 (100% 완료)
- [x] `run_cto_review.py` 에 조상 폴더 `art/metadata.json` 파싱 헬퍼 및 정규식 에셋 감사 기능 신설 (완료)
- [x] 에셋 위반 검출 시 징계 연동 및 PR Reject (`exit 1`) 적용 (완료)
- [x] `tests/test_cto_review.py` 에 정상 등록/미등록 에셋 모킹 검증 테스트 케이스 2종 추가 보완 (완료)
- [x] `python3 -m unittest discover tests` 전체 20개 테스트 100% 패스 확인 (완료)
- [x] 임시 샌드박스 파일 생성을 통한 에셋 감사기 수동 dry-run 최종 검수 (200% 오작동 없는Reject 검수 완료)

## 📊 11. 마일스톤 1.5: 가상 사옥 감사실(Audit Bureau) 및 모니터링 시스템 구축 (100% 완료)
- [x] SQLite `system_audit_logs` 테이블 스키마 DDL 작성 및 `add_audit_log`, `get_audit_summary` 구현 (완료)
- [x] FastAPI `/api/audit/log` 및 `/api/audit/summary` 건강성 지수 산출 API 엔드포인트 완비 (완료)
- [x] `orchestrator.py` 순차 오케스트레이션 단계별 감사 로그 자동 적재 적용 (완료)
- [x] `workspace/audit/` 경로 하위 `audit_diary_[date].md` 마크다운 일지 생성 로직 완비 (완료)
- [x] 80% 미만 점수 도달 시 Discord 적색 비상 Embed 알림 및 이상 없을 시 청색 보고 연동 완비 (완료)
- [x] `tests/test_system_audits.py` 신설 및 23개 전구간 유닛 테스트 100% 성공 검증 (완료)

## 🎮 12. 마일스톤 2: 가상 사옥 게임 QA 1단계 자동화 파이프라인 연동 (100% 완료)
- [x] `app/database.py` 감사실 5대 지표 (QA Health 추가) 계산 확장 구현 (완료)
- [x] `app/main.py` 신규 `/api/qa/verify` API 엔드포인트 구현 (완료)
- [x] `orchestrator.py` 순차 공정 내부 `execute_qa_audit_stage` 편입 및 감사 일지 마크다운 연동 (완료)
- [x] `tests/test_qa_pipeline.py` 신설 및 통합 유닛 테스트 검증 완완 (완료)
- [x] 전체 28개 유닛 테스트 100% 완결 통과 확인 및 원격 Push 배포 (완료)

## 💻 13. 마일스톤 2.6: M5 Pro Max AI-Driven PM Autonomous Provisioning 및 PM 가이드 작성 (100% 완료)
- [x] `M5_PRO_MAX_BOOTSTRAP_GUIDE.md` 파일의 극단적 미니멀리즘 1단계 셋업 및 MLX 모델 튜닝 반영 (완료)
- [x] `PM_AGENT_INFRA_PROVISIONING_GUIDE.md` PM 전용 자율 프로비저닝 표준 쉘 커맨드 런북 신설 (완료)
- [x] `app/blinky_middleware.py` 및 `tests/test_orchestrator.py` 내 Blinky 구동 모델 `gemma4:4b` ➡️ `gemma4:4b-mlx` MLX 지원 판올림 (완료)
- [x] 전체 28개 백엔드 및 오케스트레이터 유닛 테스트 재구동 100% 패스 확인 (완료)
- [x] 브레인 아티팩트 디렉토리 및 로컬 프로젝트 디렉토리 간 마크다운 가이드 파일 최종 동기화 완료 (완료)
