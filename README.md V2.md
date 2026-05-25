# 🚀 Team-203 멀티 에이전트 가상 스튜디오
M5 Max 128GB 단일 머신 기반, 보안 유출 및 토큰 비용이 없는 **100% 폐쇄형 고성능 로컬 멀티 에이전트 시스템**의 임시 마스터 플랜 및 작업 기록 저장소입니다. 맥북 도착 전까지 본 문서를 기반으로 아키텍처를 견고히 다집니다.
## 📅 프로젝트 정보
**최종 업데이트:** 2026년 5월 21일 (야간 고도화 작업)
**총괄 승인권자:** Team-203 대표 박청룡
**운영 책임자:** 운영전략실장 3실장

## 1. 핵심 아키텍처 개요 (Infrastructure)
**외부 채널 (대표님 ↔ 시스템):** **디스코드(Discord)** — 대표님의 명령 하달 및 최종 마일스톤 보고서 브리핑 전용 채널.
**내부 채널 (Agent ↔ Agent):** **초경량 로컬 채팅 서버 (FastAPI + SQLite)** — 에이전트 간 수천 줄의 소스코드, 기획서, 이미지 파일 경로를 밀리초(ms) 단위로 교환하는 보안 격리 공간.
**추론 및 그래픽 엔진:** Ollama (로컬 LLM 인프라) + ComfyUI API (Flux.1 Dev FP8 로컬 이미지 생성).
**코드 검증 런타임:** VS Code Headless (CLI) 기반의 에이전트별 샌드박스 파일 시스템 바인딩.

## 2. Team-203 가상 오피스 조직도 (5인 체제)

| 부서 / 직책 | 이름 | 백엔드 모델 | 자원 운용 및 핵심 권한 |
| --- | --- | --- | --- |
| **운영전략본부 수석PM** | Hermes | Gemma 4 31B (Q4_K_M) | **상시 상주.** 대표님 명령 수신 및 WBS 자원 통제, 동적 VRAM 제어(Keep-alive 스위칭) 전권 행사. |
| **서비스기획팀 시니어 기획자** | Concept-Agent | qwen3.6:35b-mlx | **동적 로딩.** 서비스 논리 구조, 제약 조건 설계 및 개발팀 구동 시 메모리 언로드(Unload). |
| **크리에이티브팀 테크니컬 아티스트** | Art-Agent | Flux.1 Dev (FP8 정밀도) | **동적 호출.** UI/UX 시안 및 이미지 프롬프트 최적화. 생성 시 GPU 풀 로드 후 즉시 자원 반환. |
| **기술개발팀 수석 엔지니어** | Dev-Agent | qwen3.6:35b-mlx | **상시 상주.** 기획서 기반 소스 코드 구현 및 VS Code CLI 연동 격리 환경 검증(Linting) 전담. |
| **경영지원/IO 운영 지원 주임** | Blinky | Gemma 4 E4B (경량화) | **상시 상주.** 대용량 로그/데이터 초고속 3줄 요약, JSON 파싱 및 내부 DB/비상 직접 웹훅 통신 전담. |

## 3. [공정 1] 로컬 채팅 서버 DB 스키마 명세
**tasks:** task_id (PK), description (대표님 지시), status (PENDING/IN_PROGRESS/COMPLETED)
**rooms:** room_id (PK), task_id (FK), room_name, is_active (컨텍스트 세션 제어 플래그)
**messages:** message_id (AI), room_id (FK), sender_role, content, payload_type (TEXT/CODE/JSON_SPEC/IMAGE_PATH), payload (소스코드 및 그래픽 원본 데이터 적재)

## 4. [공정 2] 로컬 작업 디렉터리 트리 (Tree) 구조 설계
에이전트별 독립된 파일 시스템 샌드박스를 배정하여 파일 락(File Lock) 및 무한 수정 루프를 방지합니다.
~/Workspace/Team-203/
├── .git/                      # GitHub 원격 저장소 연결 로컬 폴더
├── README.md                  # 마스터플랜 메인 문서
├── config/                    # 공통 환경 변수 (.env)
├── database/                  # 수석PM 영속성 및 로컬 채팅 DB (hermes_soul.db)
└── workspace/                 # ★ 에이전트 격리 작업 공간
    ├── shared/                # 읽기 전용 공통 명세 가이드라인
    ├── concept_sandbox/       # [시니어 기획자] Markdown 기획서 작성 구역
    ├── art_sandbox/           # [테크니컬 아티스트] Flux.1 생성 에셋 보관 구역
    └── dev_sandbox/           # [수석 엔지니어] VS Code CLI 연동 소스코드(src) 및 테스트(tests) 구역


## 5. [공정 2] 에이전트 Git 브랜치 운용 및 형상 관리 규칙
**브랜치 강제 격리:** 각 부서는 지정된 브랜치(feature/concept, feature/dev)에만 작업 내역을 push할 수 있으며, 타 부서 영역 직접 수정은 원천 차단됨.
**VS Code 린팅 패스 조건:** Dev-Agent가 코드를 push하기 전, tests/ 내의 검증 스크립트를 headless 모드로 자동 실행하여 "Errors: 0"을 달성해야 수석PM에게 Pull Request(PR) 발송 가능.
**수석PM 통합 승인 권한:** 메인 코드 저장소(main 또는 release)로의 최종 병합(Merge) 권한은 [수석PM] Hermes가 독점 제어하며, 완료 후 Blinky가 커밋 로그를 파싱하여 대표님께 보고함.