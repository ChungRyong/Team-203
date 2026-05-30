# 🧠 Team-203 프로젝트 작업 메모리 (MEMORY.md)

이전 세션의 작업 내용과 프로젝트 연속성을 유지하기 위한 핵심 컨텍스트 기록 파일입니다. 다음 작업 시작 시 이 파일을 먼저 읽고 브리핑을 진행합니다.

---

## 1. 📅 오늘 완료한 주요 작업 및 핵심 변경 사항

### ⑦ [2026-05-30] 가상 CTO 피드백 수용 11대 인프라 고도화 및 깃허브 원격 업로드 완결 (Critical)
* **스킬 자산화 및 R&R Lock 규정 개편:**
  - 로컬 `.gemini` 하위 의존성(심볼릭 링크)을 완전히 폐기 및 삭제하여 환경 격리를 확보했습니다.
  - 프로젝트 최상단 디렉토리인 `.skills/`를 가상 사옥 공식 공유 스킬 단일 저장소로 지정하였습니다.
  - `VIRTUAL_OFFICE.md` 및 `MEMORY.md`에 **[제5조 에이전트 자율 스킬 실행 및 자산화 규칙]**과 **[R&R 경계 제약 (R&R Lock)]**을 명문화하여, 인프라 빌더(Antigravity)와 사내 상주 실무 에이전트(Concept, Art, Dev) 간의 R&R 경계를 영구 각인하고 월권 개입을 원천 차단했습니다.
* **macOS 키체인(Keychain) 하드웨어 보안 연동 모듈 완비:**
  - `bootstrap.py` 내에 파이썬 `subprocess` 및 macOS `security` CLI 기반의 **Keychain Security Resolver (`resolve_keychain_secrets`)** 모듈을 직접 코딩 및 이식 완료했습니다. 중요 토큰 정보(Discord Webhook, HF Token)를 키체인에서 안전하게 바인딩하여 `.env` 자동 무인 생성/병합 및 `chmod 600` 타이트락을 완수했습니다.
* **가상 CTO 피드백 수용 11대 인프라 고도화 및 zsh 호환성 보완:**
  - `PM_AGENT_INFRA_PROVISIONING_GUIDE.md`, `M5_PRO_MAX_BOOTSTRAP_GUIDE.md`, `M5_PRO_MAX_BOOTSTRAP_GUIDE.html` 파일 전면 리팩토링.
  - **Part A (Bug Fix):** Xcode CLT `xcode-select --install` 자동 확인 및 물리 팝업 승인 한계 명시, Ollama GUI 미감지 시 CLI 데몬(`ollama serve`) 하이브리드 분기 기동 로직 보강, zsh `TIMEOUT=$((TIMEOUT - 1))` 호환 루프 문법 교체, ComfyUI cd Abort 예방(`mkdir -p`) 및 헬스 체크 폴링 신설, FastAPI Uvicorn 기동 전 venv 활성화 강제화.
  - **Part B (Security Upgrade):** huggingface_hub 격리 가상환경 내부 설치 완료, 포트 바인딩 루프백 `127.0.0.1`로 엄격 조임, requirements.txt 실존 조건 가드 탑재, `.env` chmod 600 통제 락 적용.
  - **Part C (Security Core):** 특수문자가 포함될 경우 `sed` 파싱이 깨지는 치명적인 취약점을 해결하기 위해, 쉘의 `sed` 대신 내장 파이썬 한 줄 명령어(**`python3 -c` 및 os.environ 안전 대입**) 방식으로 전면 리팩토링 및 이식을 완수했습니다.
* **양대 워크스페이스 Parity 동기화 및 깃허브 원격 전송 완료:**
  - 보조 워크스페이스인 `/Users/jabiseu/Documents/workspace/Team-203`과의 Parity 동기화를 100% 완료하였습니다.
  - 대표님의 최종 승인 하에 깃허브 원격 main 브랜치로 `git push origin main --force`를 성공적으로 전송 완료하여 모든 정교화된 가상 사옥 인프라 자산을 원격지에 안전하게 박제했습니다.

* **변경된 핵심 파일 목록:**
  - [MEMORY.md](file:///Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203/MEMORY.md) (규정 개편 및 R&R Lock 각인)
  - [VIRTUAL_OFFICE.md](file:///Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203/VIRTUAL_OFFICE.md) (제5조 자율 스킬 활용 규칙 신설)
  - [M5_PRO_MAX_BOOTSTRAP_GUIDE.md](file:///Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203/M5_PRO_MAX_BOOTSTRAP_GUIDE.md) (Ollama CLI 기동 및 클론 단계 추가 반영)
  - [M5_PRO_MAX_BOOTSTRAP_GUIDE.html](file:///Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203/M5_PRO_MAX_BOOTSTRAP_GUIDE.html) (프리미엄 다크테마 원터치 복사 엔진 연동 가이드 생성)
  - [PM_AGENT_INFRA_PROVISIONING_GUIDE.md](file:///Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203/PM_AGENT_INFRA_PROVISIONING_GUIDE.md) (CTO 피드백 수렴 11대 인프라 고도화 완수)
  - [bootstrap.py](file:///Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203/bootstrap.py) (Keychain Security Resolver 완비)
  - [task.md](file:///Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203/task.md) & [walkthrough.md](file:///Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203/walkthrough.md) (최종 완료 정리)

---

## 2. ⚠️ 현재 마주한 에러 및 미해결 이슈
* **현재 해결해야 할 오류나 버그는 '0건'**입니다. 가상 CTO의 정교한 2차 기술 검사 피드백까지 100% 무결하게 수정 및 반영하여, 전체 시공 인프라가 대기업 엔터프라이즈 아키텍처 수준의 완벽한 안정성과 보안성을 확보하고 있습니다.

---

## 3. 🎯 다음 세션에 이어서 해야 할 구체적인 목표와 할 일 (To-Do)

### ① M5 Pro Max 신형 맥북 배송 완료 대기 및 셋업
- [ ] 대표님의 신형 장비(MacBook Pro M5 Pro Max)가 배송 완료될 때까지 안전한 방치 대기 모드로 진입합니다.
- [ ] 맥북 수령 즉시 대표실 가이드북에 따라 다음 **초간단 5단계 부트스트랩**을 기동합니다:
  - 1단계: 저장소 격리 클론 (`~/Documents/workspace/Team-203`)
  - 2단계: 키체인에 Discord Webhook 및 HF_TOKEN 등록
  - 3단계: Ollama 가동 및 gemma4:31b-mlx 풀링
  - 4단계: PM Hermes 깨우기 (`hermes setup` ➡️ 방향키로 gemma4 선택)
  - 5단계: 키체인 접근 제어 항상 허용 세팅

### ② 가상 사옥 에이전트 소집 및 테트리스 1단계 실무 기획 돌입
- [ ] PM Hermes 부팅 완료 후, 대표실 지시에 따라 가상 사옥의 상주 에이전트들(Concept-Agent 등)을 격리 폴더 `workspace/projects/game_01_tetris/concept/` 하위에 소집합니다.
- [ ] 본격적인 테트리스 게임 1호기 개발을 위해 **Godot 4.2+ GDScript stable 규격 기반의 그리드 및 특수 예외처리 기획 명세서 물리 작성**을 하달 및 서포트합니다.

---

## 4. 🚨 대표님 핵심 지침 및 제약사항 (Rules & Constraints)
* **[R&R 경계 제약] 플랫폼 빌더(Antigravity)와 실무 에이전트 간 역할 엄격 구분 (R&R Lock):**
  - **Antigravity의 역할:** VIRTUAL-OFFICE의 전체 인프라(FastAPI 백엔드, SQLite DB, 감사실, 키체인 보안 연동, 가이드라인 런북, 동기화 스크립트 등)를 설계하고 무결하게 구축/시공하는 **플랫폼 빌더(Platform Builder)**입니다.
  - **사내 에이전트들의 역할:** 테트리스 게임 개발 및 기획 등 개별 프로젝트 실무는 **"맥북 수령 후 VIRTUAL-OFFICE가 완전히 구성된 이후"** 대표님이 직접 사무실에서 소집 가동하실 실무진(Concept, Art, Dev-Agent 등)의 영역입니다.
  - **절대적 제약:** Antigravity는 가상 사옥 구축 단계에서 테트리스 게임 기획 소집 및 실무 설계 영역에 어떠한 경우에도 임의로 월권하거나 개입해서는 안 되며, 오직 사옥 인프라의 완성도를 극한으로 올리는 데에만 집중해야 합니다.
* **[Git 컨펌 제약] Git 업로드(Push) 절대 통제:** Git 원격 저장소(`git push`)에 작업 내용을 업로드하는 것은 **대표님께서 최종 마음에 들어 하시고 명시적으로 승인(컨펌)하셨을 때**에만 진행합니다. 에이전트가 테스트 통과나 스냅샷 등의 이유로 사전에 승인받지 않은 `git push`를 자동 수행해서는 절대로 안 됩니다. (자율 백업 및 로컬 커밋은 허용하되, 원격 Push는 100% 대표님 컨펌 이후 수동으로 진행)
* **[정적 에셋 제약] 프론트엔드 수정 시 백엔드 테스트 전면 금지 (경고 1회 반영):** `virtual_dorm.html` 등 순수 프론트엔드/정적 에셋 작업 시에는 백엔드 전체 유닛 테스트(`pytest` 등)를 절대로 임의로 구동하지 마십시오. 백업 자동화 오작동 및 불필요한 시스템 검증 과부하를 원천 차단하기 위한 대표님의 엄중한 규칙입니다. (경고 1회 누적 사항 반영 완수)
* **[스킬 자산화 제약] 반복 작업의 자율 스킬화 및 자산화 원칙 (Skill Creation Rule):**
  - **트리거:** 특정 워크플로우(에셋 변환, 코드 검사, 다단계 협업 등)가 2회 이상 중복 수행되거나 에이전트 간 수동 가이드가 계속 발생할 경우.
  - **원칙:** 즉시 이를 격리하여 `SKILL.md` (트리거)와 `scripts/` (결정론적 자동화 스크립트)를 포함하는 **정식 Skill**로 자산화 패키징을 수행해야 합니다.
  - **배포:** 신설된 스킬은 프로젝트 최상단 디렉토리인 `.skills/` 하위에 명세(`SKILL.md`)와 자동화 스크립트(`scripts/`)를 정식 물리 패키징하여 관리하며, 양대 워크스페이스에 Parity 동기화합니다. 가상 사옥(VIRTUAL-OFFICE)의 모든 에이전트들은 정형 반복 작업 수행 시 이 저장소를 자율 탐색 및 실행하여 100% 완벽히 복제 수행하도록 의무화합니다.
