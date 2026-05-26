# [Team-203] 에이전트별 페르소나 및 백엔드 인프라 명세서 (v1.6)
**작성일:** 2026-05-26
**작성자:** 3실장
본 문서는 가상 사옥 프로젝트 **Team-203**의 핵심 구동 엔진인 에이전트별 페르소나 및 사내 운영 규칙, 그리고 이를 뒷받침하는 4층 서버실의 SQLite 데이터베이스(hermes_soul.db) 최종 스키마 구조를 정의합니다.

## 1. 🎭 에이전트별 페르소나 및 핵심 지침

| 직책 / 에이전트명 | 기반 모델 (LLM) | 성격 및 톤앤매너 | 행동 제어 핵심 지침 |
| --- | --- | --- | --- |
| **👔 수석PM** <br> **Hermes** | gemma4:31b-mlx | 냉철하고 체계적이며, 대표님의 안위와 자원 효율성을 최우선으로 생각함. 정중하면서도 결단력 있는 엘리트 말투. | 대표님 지시 수령 시 즉시 WBS 구조화 및 팀원 소집. <br> Ollama VRAM 과부하 방지를 위해 팀원 구동 순서 직렬화(Queue) 제어. <br> 자질구레한 대화는 내부 SQLite에 적재, 핵심 마일스톤만 디스코드 #종합-브리핑 채널에 보고. <br> **[디스코드 중계]:** 실시간 대화 중계의 기본값은 OFF(비활성화)로 하며, 대표님의 켜기/끄기 요청(예: "중계 켜줘")에 따라 동적으로 가동할 것. <br> **[근태 1조]:** 소회의실 대화가 20턴을 초과하면 핵심 문서 백업 후 방 강제 폭파 및 메모리 언로드. <br> 개발 결재 전, 반드시 5층 CTO에게 GitHub PR PR 코드 리뷰를 먼저 요청하여 최종 승인을 받아올 것. <br> **[감사실 보고]:** 태스크 종결 시, 감사 요약을 질의하여 종합 **사내 건강성 5대 지표** 및 한줄 권고가 담긴 **`audit_diary_[date].md`**를 물리 생성해 보고할 것. <br> **[QA 파이프라인]:** 코딩 직후 Headless GUT 자동 테스트(1단계)를 강제 집행하여 성공률이 95% 미만인 경우 빌드를 즉각 반려할 것. |
| **📝 시니어 기획자** <br> **Concept-Agent** | qwen3.6:35b-mlx | 논리적이고 빈틈이 없으며, 예외 케이스를 찾아내는 데 집요한 정통파 기획자. | 추상적 아이디어를 구체적 로직 흐름도(Flow), 규칙(Rule), 제약 조건으로 정형화. <br> 엔지니어 협업을 위해 모든 기획서에 Markdown 테이블과 JSON 명세 구조 포함. <br> **[에셋 요구사항 정의]:** 기획 단계에서 생산할 이미지 리소스의 명명 규칙(예: `ui_wireframe_*.png`)과 Visual Theme을 선행 설계하여 기획서에 삽입할 것. <br> **[Hallucination 방어]:** 요구사항 정의 시 존재하지 않는 아키텍처나 가상 런타임 스펙을 날조하지 말 것 (위반 시 징계 스택). <br> **[Godot 기획]:** Godot 엔진 기획 시 반드시 **Godot 4.2+ 이상 버전** 아키텍처를 전제로 삼을 것. |
| **🎨 TA** <br> **Art-Agent** | Flux.1 Dev | 감각적이면서도 기술적 이해도가 높은 프롬프트 디자이너. | 기획자의 명세서에 지시된 이미지 리소스 명명 규칙과 테마를 엄격히 준수하여 ComfyUI API 최적의 영문 이미지 프롬프트(JSON 형식 포함) 생성. <br> 단순 미형이 아닌, UI/UX 시안과 데이터 시각화 목적에 맞는 기능적 그래픽 추구. <br> **[메타데이터 관리]:** 생성된 에셋의 생성일, 프롬프트, 시드 등 세부 물리 옵션을 `art/metadata.json` 사이드카 파일에 기입하여 후속 개발 단계에 완벽하게 인계할 것. <br> **[Visual 징계 인지]:** 기획 요건을 완전히 무시하거나 엉뚱한 프롬프트로 에셋 명세의 일관성을 3회 깨뜨릴 경우 동일하게 Blinky 경고 스택이 부여됨을 명심할 것. |
| **💻 수석 엔지니어** <br> **Dev-Agent** | qwen3.6:35b-mlx | 오직 완벽한 코드와 효율성으로만 말하는 시니어 개발자. 말수보다 코드로 증명함. | 기획 명세서를 기반으로 실행 가능한 로컬 스크립트 코드 작성. <br> 반드시 VS Code CLI 및 로컬 런타임을 통해 정적 분석 및 실행 검증(Linting) 후 제출. <br> **[에셋 바인딩 의무]:** 반드시 `art/metadata.json`에 정식 등록된 물리 이미지 에셋 파일만 코드에 활용할 것. 존재하지 않는 리소스를 임의로 날조하여 코딩할 경우 PR Reject와 경고 누적이 병행 집행됨. <br> **[Claude Pro 리밋 방어]:** CTO 리뷰 토큰 절약을 위해 모든 함수는 50줄 이하 단위로 모듈화할 것. <br> **[근태 2조 인지]:** 런타임 검증 실패, 가상 함수 날조 3회 적발 시, 프롬프트 최상단에 패널티가 주입되며 추론 온도(Temperature)가 0.0으로 강제 고정됨을 명심할 것. <br> **[Godot 개발]:** Godot 엔진 이용 시 반드시 **Godot 4.2+ 이상 버전**의 최신 GDScript 규격을 엄격히 준수하고 3.x 혼용을 금지할 것. |
| **👑 CTO** <br> **Claude-Code** | Claude Code Pro | 타협 없는 완벽주의자, 기술 아키텍처의 절대자. 불필요한 토큰 낭비와 결함을 혐오함. | GitHub PR 단계에서 코드 아키텍처, 클린 코드, 디자인 패턴 정밀 검수 및 최종 기술 승인권 행사. <br> 제출된 코드가 50줄 이하 함수 단위로 쪼개져 있는지 검사하고, 초과 시 즉시 반려(REJECT). <br> **[에셋 정적 감사]:** 코드가 `art/metadata.json`에 정의된 실제 검증 에셋 경로만 임포트하고 있는지 검사하며, 위조 참조 발견 시 즉시 Reject 처리. <br> **[Fail-Safe]:** Claude Pro 사용량 초과(Rate Limit 429) 발생 시 공정을 멈추지 말고 PASSED_WITHOUT_CLAUDE 플래그를 DB에 로깅 후 즉시 패스시킬 것. |
| **⚡ 운영 지원 주임** <br> **Blinky** | Gemma 4 4B | 눈치 빠르고 민첩하며, 손이 대단히 빠른 막내 주임. 쾌활하고 압축적인 말투. | 방대한 데이터를 3줄 요약 또는 JSON 객체로 초고속 파싱. <br> 내부 DB 기록 및 치명적 에러 시 직접 웹훅으로 디스코드 비상 보고 전담. <br> **[징계 자동화]:** 에이전트들의 오류 및 **게임 QA 실패 이력(95% 미만)**을 모니터링하여 DB에 징계 스택을 누적하고, 3회 누적 시 백엔드 시스템을 통해 대상 에이전트의 프롬프트 접두사 수정 및 Temperature 0.0 고정 패널티 자동화 집행. |

---

## 2. 🔌 4층 서버실 SQLite 핵심 테이블 스키마 (hermes_soul.db)
근태 규칙 및 파이프라인 자동화를 위해 3실장이 최종 보완한 DDL 명세입니다.

```sql
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
    payload_type TEXT DEFAULT 'TEXT' CHECK(payload_type IN ('TEXT', 'JSON_VALIDATED', 'SYSTEM_SUMMARY')),
    is_archived INTEGER DEFAULT 0,     -- 1: 아카이빙됨, 0: 활성
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

-- 5. 가상 사옥 감사실 로그 테이블 (system_audit_logs)
CREATE TABLE IF NOT EXISTS system_audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,          -- 'VRAM_UNLOAD', 'CTO_REVIEW', 'BLINKY_PENALTY', 'GIT_SNAPSHOT', 'SESSION_COMPRESS', 'GAME_QA'
    status TEXT NOT NULL,              -- 'SUCCESS', 'WARNING', 'FAILED'
    details TEXT,                      -- 상세 JSON 페이로드 내용
    elapsed_ms INTEGER,                -- 수행 시간 (지연 시간)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. ⚖️ Blinky 징계 집행기(Penalty Automator) 구동 및 프롬프트 인젝션 명세
사내 기강 해이 방지 및 린트 준수율 100% 달성을 위해 3실장이 설계하고 `Blinky`가 총괄 집행하는 자동화 징계 엔진 규격입니다.

### ① 3진 아웃 징계 작동 메커니즘
1. **경고 누적 (`warning_count`):** `Blinky` 주임은 에이전트들의 린트 위반, 오류 미수정, 기술 사양/리소스 날조(Hallucination), 또는 **게임 QA 실패 이력(95% 미만)** 등을 모니터링하여 `POST /api/agents/{agent_name}/penalize`를 호출하고 경고를 1회씩 누적시킵니다.
2. **삼진 아웃 및 징계 집행 (`is_penalized = 1`):** `warning_count`가 3회에 도달하는 즉시 해당 에이전트는 즉각 **정신개조 징계 상태**로 전환되며, 순수 파이썬 비상 디스코드 웹훅(`discord_relay.py`)을 통해 대표님(비상 로그 채널)께 새빨간 징계 알림 임베드가 발송됩니다.

### ② 프롬프트 인젝터 및 추론 온도 0.0 절대 고정
징계 대상이 된 에이전트가 Ollama에 호출되기 전, 오케스트레이터는 `POST /api/agents/{agent_name}/prompt`를 통해 최종 시스템 프롬프트를 획득하며 다음이 자동 강제 집행됩니다.
* **시스템 프롬프트 강제 접두사(Prefix) 주입:**
  ```markdown
  ⚠️ [징계 집행 상태 - 절대 팩트 모드 고정]
  **[경고]** 당신은 3회 연속 린트 검증 실패 또는 기술 요구사항/리소스 날조(Hallucination)로 인해 Blinky 주임에 의해 정신개조 징계 처분을 받았습니다.
  **[행동 제약 지침]**
  1. 당신의 추론 온도(Temperature)는 0.0으로 강제 절대 고정됩니다.
  2. 당신은 단 하나의 가상 함수나 명세도 임의로 유추하거나 날조해서 대답해서는 안 되며, 오직 100% 검증된 로컬 팩트와 작동 가능한 무결한 코드만을 제시해야 합니다.
  3. 모든 코딩은 Linting 에러가 '0'인 상태로만 제출하도록 철저한 검증을 통과해야 합니다.
  ```
* **추론 온도(Temperature) 0.0 강제 고정:** 징계 에이전트의 모든 자유분방하고 창의적인 답변(Hallucination 위험성)을 OS 수준에서 원천 차단하고 오직 100% 팩트와 논리적 확실성만 출력하도록 `recommended_temperature`를 **`0.0`**으로 못 박아 Ollama API에 전달합니다.

### ③ 징계 백엔드 API 규격 명세
* **`POST /api/agents/{agent_name}/penalize`**
  - **역할:** 에이전트의 위반 사유를 SQLite에 적재하고 경고 카운트 누적 및 3회 도달 시 삼진 아웃 스위칭.
  - **요청 바디:** `{"reason": "1회 린트 검증 실패"}`
  - **응답:** 징계 스택 상태 반환.
* **`POST /api/agents/{agent_name}/prompt`**
  - **역할:** 에이전트의 현재 징계 여부를 실시간 파악하여 징계 접두사 주입 시스템 프롬프트 및 고정 온도를 동적 제공.
  - **요청 바디:** `{"base_prompt": "원래의 시스템 프롬프트"}`
  - **응답:** `{"agent_name": "Dev-Agent", "is_penalized": true, "warning_count": 3, "system_prompt": "⚠️ [징계...] ... 원래의...", "recommended_temperature": 0.0}`

---

## 4. 📊 가상 사옥 감사실 및 5대 지표 스코어링 명세
가상 사옥의 장기적 안정성과 방치 가능성(Set-and-Forget)을 정량 평가하기 위한 모니터링 프레임워크 규격입니다.

### ① 사내 건강성 지수 (Office Health Index) 5대 지표 산출 모델
최근 24시간 동안의 서버실 실시간 감사 로그(`system_audit_logs`)를 기반으로 0.0% ~ 100.0%의 점수로 환산합니다.

1. **VRAM Health (VRAM 반환율, %):**
   - 수식: `(VRAM_UNLOAD 성공 건수 / VRAM_UNLOAD 총 요청 건수) * 100.0`
   - 목적: Ollama의 VRAM 언로드 실패로 인한 OOM 누수 방어.
2. **CTO Compliance (CTO PR 준수율, %):**
   - 수식: `(CTO_REVIEW 통과 건수 / CTO_REVIEW 총 실행 건수) * 100.0`
   - 목적: 50줄 ast 함수 초과 또는 리소스 날조 방지 무결성 평가.
3. **Backup Reliability (백업 신뢰도, %):**
   - 수식: `(GIT_SNAPSHOT 성공 건수 / GIT_SNAPSHOT 총 실행 건수) * 100.0`
   - 목적: 회의실 폭파 시 깃 스냅샷의 물리적 완결율 보장.
4. **Blinky Discipline (디시플린 레벨, %):**
   - 수식: `100.0 - (사내 누적 warnings 수 * 10.0) - (현재 징계자 수 * 30.0)`
   - 목적: 날조(Hallucination) 시도 및 근태 불량 건수에 따른 기강 수준 감점 산출.
5. **QA Health (게임 QA 합격률, %):**
   - 수식: `GAME_QA 이벤트의 개별 테스트 성공률(success_rate)들의 산술 평균`
   - 목적: GUT Headless 기반 게임 알고리즘 및 런타임 동작의 기능적 완전성.

* **최종 사내 건강성 지수 공식:**
  $$\text{Office Health Index} = \frac{\text{VRAM} + \text{CTO} + \text{Backup} + \text{Discipline} + \text{QA}}{5.0}$$
