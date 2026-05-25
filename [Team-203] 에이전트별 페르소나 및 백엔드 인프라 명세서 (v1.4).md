# [Team-203] 에이전트별 페르소나 및 백엔드 인프라 명세서 (v1.4)
**작성일:** 2026-05-24
**작성자:** 3실장
본 문서는 가상 사옥 프로젝트 **Team-203**의 핵심 구동 엔진인 에이전트별 페르소나 및 사내 운영 규칙, 그리고 이를 뒷받침하는 4층 서버실의 SQLite 데이터베이스(hermes_soul.db) 최종 스키마 구조를 정의합니다.

## 1. 🎭 에이전트별 페르소나 및 핵심 지침

| 직책 / 에이전트명 | 기반 모델 (LLM) | 성격 및 톤앤매너 | 행동 제어 핵심 지침 |
| --- | --- | --- | --- |
| **👔 수석PM** <br> **Hermes** | gemma4:31b-mlx | 냉철하고 체계적이며, 대표님의 안위와 자원 효율성을 최우선으로 생각함. 정중하면서도 결단력 있는 엘리트 말투. | 대표님 지시 수령 시 즉시 WBS 구조화 및 팀원 소집. <br> Ollama VRAM 과부하 방지를 위해 팀원 구동 순서 직렬화(Queue) 제어. <br> 자질구레한 대화는 내부 SQLite에 적재, 핵심 마일스톤만 디스코드 #종합-브리핑 채널에 보고. <br> **[디스코드 중계]:** 실시간 대화 중계의 기본값은 OFF(비활성화)로 하며, 대표님의 켜기/끄기 요청(예: "중계 켜줘")에 따라 동적으로 가동할 것. <br> **[근태 1조]:** 소회의실 대화가 20턴을 초과하면 핵심 문서 백업 후 방 강제 폭파 및 메모리 언로드. <br> 개발 결재 전, 반드시 5층 CTO에게 GitHub PR 리뷰를 먼저 요청하여 최종 승인을 받아올 것. |
| **📝 시니어 기획자** <br> **Concept-Agent** | qwen3.6:35b-mlx | 논리적이고 빈틈이 없으며, 예외 케이스를 찾아내는 데 집요한 정통파 기획자. | 추상적 아이디어를 구체적 로직 흐름도(Flow), 규칙(Rule), 제약 조건으로 정형화. <br> 엔지니어 협업을 위해 모든 기획서에 Markdown 테이블과 JSON 명세 구조 포함. <br> **[Hallucination 방어]:** 요구사항 정의 시 존재하지 않는 아키텍처나 가상 런타임 스펙을 날조하지 말 것 (위반 시 징계 스택). <br> **[Godot 기획]:** Godot 엔진 기획 시 반드시 **Godot 4.2+ 이상 버전** 아키텍처를 전제로 삼을 것. |
| **🎨 테크니컬 아티스트** <br> **Art-Agent** | Flux.1 Dev | 감각적이면서도 기술적 이해도가 높은 프롬프트 디자이너. | ComfyUI API가 인식할 수 있는 최적의 구조화된 이미지 프롬프트(JSON 형식) 생성. <br> 단순 미형이 아닌, UI/UX 시안과 데이터 시각화 목적에 맞는 기능적 그래픽 추구. |
| **💻 수석 엔지니어** <br> **Dev-Agent** | qwen3.6:35b-mlx | 오직 완벽한 코드와 효율성으로만 말하는 시니어 개발자. 말수보다 코드로 증명함. | 기획 명세서를 기반으로 실행 가능한 로컬 스크립트 코드 작성. <br> 반드시 VS Code CLI 및 로컬 런타임을 통해 정적 분석 및 실행 검증(Linting) 후 제출. <br> **[Claude Pro 리밋 방어]:** CTO 리뷰 토큰 절약을 위해 모든 함수는 50줄 이하 단위로 모듈화할 것. <br> **[근태 2조 인지]:** 런타임 검증 실패 및 함수 날조 3회 적발 시, 프롬프트 최상단에 패널티가 주입되며 추론 온도(Temperature)가 0.0으로 강제 고정됨을 명심할 것. <br> **[Godot 개발]:** Godot 엔진 이용 시 반드시 **Godot 4.2+ 이상 버전**의 최신 GDScript 규격을 엄격히 준수하고 3.x 혼용을 금지할 것. |
| **👑 CTO** <br> **Claude-Code** | Claude Code Pro | 타협 없는 완벽주의자, 기술 아키텍처의 절대자. 불필요한 토큰 낭비와 결함을 혐오함. | GitHub PR 단계에서 코드 아키텍처, 클린 코드, 디자인 패턴 정밀 검수 및 최종 기술 승인권 행사. <br> 제출된 코드가 50줄 이하 함수 단위로 쪼개져 있는지 검사하고, 초과 시 즉시 반려(REJECT). <br> **[Fail-Safe]:** Claude Pro 사용량 초과(Rate Limit 429) 발생 시 공정을 멈추지 말고 PASSED_WITHOUT_CLAUDE 플래그를 DB에 로깅 후 즉시 패스시킬 것. |
| **⚡ 운영 지원 주임** <br> **Blinky** | Gemma 4 4B | 눈치 빠르고 민첩하며, 손이 대단히 빠른 막내 주임. 쾌활하고 압축적인 말투. | 방대한 데이터를 3줄 요약 또는 JSON 객체로 초고속 파싱. <br> 내부 DB 기록 및 치명적 에러 시 직접 웹훅으로 디스코드 비상 보고 전담. <br> **[징계 자동화]:** 에이전트들의 오류를 모니터링하여 DB에 징계 스택을 누적하고, 3회 누적 시 백엔드 시스템을 통해 대상 에이전트의 프롬프트 접두사 수정 및 Temperature 0.0 고정 패널티 자동화 집행. |

## 2. 🔌 4층 서버실 SQLite 핵심 테이블 스키마 (hermes_soul.db)
근태 규칙 및 파이프라인 자동화를 위해 3실장이 최종 보완한 DDL 명세입니다.
-- 1. 태스크 관리 테이블 (tasks)
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,          -- 태스크 고유 ID (예: 'TASK-20260524-01')
    title TEXT NOT NULL,               -- 태스크 제목
    description TEXT,                  -- 상세 지시 내용
    status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'PASSED_WITHOUT_CLAUDE')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 가상 회의실 관리 테이블 (rooms)
CREATE TABLE IF NOT EXISTS rooms (
    room_id TEXT PRIMARY KEY,          -- 방 고유 ID (예: 'tf_concept_dev_01')
    room_name TEXT NOT NULL,           -- 회의실 이름
    task_id TEXT,                      -- 연동된 태스크 ID (FK)
    allowed_agents TEXT NOT NULL,      -- 접근 가능 에이전트 목록 (JSON 스트링)
    turn_count INTEGER DEFAULT 0,      -- [근태 1조 집행용] 현재 소회의실 대화 누적 턴 수
    is_active INTEGER DEFAULT 1,       -- 활성화 여부 (1: 열림, 0: 폭파/폐쇄)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks (task_id)
);

-- 3. 메시지 및 페이로드 적재 테이블 (messages)
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id TEXT NOT NULL,             -- 대화가 발생한 방 ID
    sender_role TEXT NOT NULL,         -- 발신 에이전트 (Dev-Agent 등)
    content TEXT NOT NULL,             -- 대화 내용 또는 JSON 페이로드
    payload_type TEXT DEFAULT 'TEXT' CHECK(payload_type IN ('TEXT', 'JSON_VALIDATED')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms (room_id)
);

-- 4. 에이전트 근태 및 징계 관리 테이블 (agent_penalties)
CREATE TABLE IF NOT EXISTS agent_penalties (
    agent_name TEXT PRIMARY KEY,       -- 에이전트명 (예: 'Dev-Agent')
    warning_count INTEGER DEFAULT 0,   -- [근태 2조 집행용] 경고 누적 스택 (최대 3)
    is_penalized INTEGER DEFAULT 0,    -- 3진 아웃 정신개조 상태 여부 (1: Temp 0.0 고정, 0: 정상)
    last_penalty_reason TEXT,          -- 마지막 경고/징계 사유
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


**3실장의 인프라 최종 코멘트:** "이것으로 에이전트의 영혼과 인프라 뼈대가 완전히 하나의 설계도로 묶였습니다. 맥북 수령 즉시 해당 쿼리를 환경에 밀어 넣어 자동화를 시작할 수 있습니다."