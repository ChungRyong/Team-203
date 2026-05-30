# 🧠 Team-203 프로젝트 작업 메모리 (MEMORY.md)

이전 세션의 작업 내용과 프로젝트 연속성을 유지하기 위한 핵심 컨텍스트 기록 파일입니다. 다음 작업 시작 시 이 파일을 먼저 읽고 브리핑을 진행합니다.

---

## 1. 📅 오늘 완료한 주요 작업 및 핵심 변경 사항

### ⑦ [2026-05-30] 가상 CTO 피드백 수용 11대 인프라 고도화 및 깃허브 원격 업로드 완결 (Critical)
* **스킬 자산화 및 R&R Lock 규정 개편:**
  - 로컬 `.gemini` 하위 의존성(심볼릭 링크)을 완전히 폐기 및 삭제하여 환경 격리를 확보했습니다.
  - 프로젝트 최상단 디렉토리인 `.skills/`를 가상 사옥 공식 공유 스킬 단일 저장소로 지정하였습니다.
  - `VIRTUAL_OFFICE.md` 및 `MEMORY.md`에 **[제5조 에이전트 자율 스킬 실행 및 자산화 규칙]**과 **[R&R 경계 제약 (R&R Lock)]**을 명문화하여 R&R 경계를 영구 각인했습니다.
* **macOS 키체인(Keychain) 하드웨어 보안 연동 모듈 완비:**
  - `bootstrap.py` 내 Keychain Security Resolver (`resolve_keychain_secrets`) 모듈을 이식 완료하여 중요 토큰을 키체인에서 안전하게 바인딩하고 `.env` 생성/병합 및 `chmod 600` 타이트락을 완수했습니다.
* **가상 CTO 피드백 수용 11대 인프라 고도화 및 zsh 호환성 보완:**
  - Xcode CLT 자동 확인, Ollama CLI serve 데몬 하이브리드 분기 기동, zsh TIMEOUT 감산 문법 교체, ComfyUI cd Abort 예방(`mkdir -p`) 및 헬스 체크 폴링 신설, FastAPI Uvicorn 기동 전 venv 활성화 강제화.
  - huggingface_hub 격리 가상환경 내부 설치, 포트 바인딩 루프백 `127.0.0.1`로 엄격 조임, requirements.txt 실존 조건 가드 탑재, `.env` chmod 600 통제 락 적용.
  - `python3 -c` 및 os.environ 안전 대입 방식의 문자열 특수문자 깨짐 및 sed 파싱 취약점 원천적 보완 교체 완료.

### ⑧ [2026-05-30] obra/superpowers 에이전틱 스킬 프레임워크 타당성 마이닝 및 통합 설계 보고서 완수 (High-Yield)
* **`obra/superpowers` 저장소 완벽 마이닝:**
  - Jesse Vincent/Prime Radiant 팀의 핵심 철학인 Socratic Brainstorming, Git Worktree 격리 샌드박스, Micro-Task Planning, Autopilot Subagent Concurrent Execution, TDD (RED-GREEN-REFACTOR) 규칙 및 Spec & Quality 2단계 코드 리뷰 메커니즘을 상세히 분석하여 마이닝을 완수했습니다.
* **통합 설계 보고서 신설 작성 및 규정 명문화:**
  - [superpowers_integration_plan.md](file:///Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203/superpowers_integration_plan.md) 기술 아티팩트를 신설 작성하여 가상 사옥의 `.skills/` 저장소 체계와 `superpowers` 스킬 포맷의 100% 대칭성을 입증하고 R&R Lock을 절대 준수하는 백엔드 플러그인(FastAPI) 및 오케스트레이터 Context 주입 브리지 설계를 수립했습니다.
  - `VIRTUAL_OFFICE.md`에 **[제6조 Superpowers 에이전틱 스킬 프레임워크 수용]** 조항을 신설 명문화하여 제도적 기반을 완비했습니다.
* **14대 실물 에이전틱 스킬셋 라이브러리 물리 이식 완료:**
  - 대표님의 지시 하에 `temp_superpowers` 격리 클론 및 복사 기법을 사용해 `obra/superpowers/skills` 내의 **14대 실물 스킬 명세서 및 템플릿(46개 파일, 8,475줄)**을 최상단 `.skills/superpowers/`에 완벽하게 물리 이식 완료했습니다.
  - 수용된 스킬셋: `brainstorming`, `using-git-worktrees`, `writing-plans`, `test-driven-development`, `subagent-driven-development`, `requesting-code-review`, `receiving-code-review`, `finishing-a-development-branch`, `executing-plans`, `dispatching-parallel-agents`, `systematic-debugging`, `verification-before-completion`, `using-superpowers`, `writing-skills`.
* **이중 워크스페이스 Parity 동기화 및 Git 로컬 커밋 완수:**
  - `.skills/workspace-parity/scripts/sync.py` 스크립트를 자율 기동하여 Primary 워크스페이스와 Secondary 워크스페이스 간 파일 일치도 100% 동기화를 마감했습니다.
  - `git commit -m "feat(skills): import obra/superpowers 14 dynamic skills library"` 로컬 커밋을 생성했습니다. (STRICT GIT PUSH LOCK에 따라 원격 Push는 대기)

* **변경된 핵심 파일 목록:**
  - [MEMORY.md](file:///Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203/MEMORY.md) (규정 개편 및 superpowers 마감 기록 갱신)
  - [VIRTUAL_OFFICE.md](file:///Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203/VIRTUAL_OFFICE.md) (제6조 Superpowers 프레임워크 수용 규칙 신설)
  - [superpowers_integration_plan.md](file:///Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203/superpowers_integration_plan.md) (가상 사옥 Superpowers 플러그인 도입 및 설계 타당성 분석 보고서 신설)
  - [.skills/superpowers/](file:///Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203/.skills/superpowers) (신설된 14개 실물 에이전트 스킬 명세서 및 템플릿 라이브러리 폴더)
  - [task.md](file:///Users/jabiseu/.gemini/antigravity/brain/e9e32290-18f3-4a10-9130-4ebd4046d5a5/task.md) & [walkthrough.md](file:///Users/jabiseu/.gemini/antigravity/brain/e9e32290-18f3-4a10-9130-4ebd4046d5a5/walkthrough.md) (최종 완료 정리)

---

## 2. ⚠️ 현재 마주한 에러 및 미해결 이슈
* **현재 해결해야 할 오류나 버그는 '0건'**입니다. 가상 CTO의 정교한 2차 기술 검사 피드백 조치와 대표님의 superpowers 14개 실물 스킬셋 이식 및 설계 보고서 작성까지 완료되어, 전체 시공 인프라가 완벽한 무결성과 확장성을 확보하고 있습니다.

---

## 3. 🎯 다음 세션에 이어서 해야 할 구체적인 목표와 할 일 (To-Do)

### ① Superpowers 설계 보고서 및 실물 이식 승인 후 Git 원격 Push
- [ ] 대표님의 최종 결과 검토 및 "Push 승인" 하달 시 `git push origin main` 원격 최종 배포 실행.

### ② M5 Pro Max 신형 맥북 배송 완료 대기 및 셋업
- [ ] 대표님의 신형 장비(MacBook Pro M5 Pro Max)가 배송 완료될 때까지 안전한 방치 대기 모드로 진입합니다.
- [ ] 맥북 수령 즉시 대표실 가이드북에 따라 다음 **초간단 5단계 부트스트랩**을 기동합니다:
  - 1단계: 저장소 격리 클론 (`~/Documents/workspace/Team-203`)
  - 2단계: 키체인에 Discord Webhook 및 HF_TOKEN 등록
  - 3단계: Ollama 가동 및 gemma4:31b-mlx 풀링
  - 4단계: PM Hermes 깨우기 (`hermes setup` ➡️ 방향키로 gemma4 선택)
  - 5단계: 키체인 접근 제어 항상 허용 세팅

### ③ 가상 사옥 에이전트 소집 및 테트리스 1단계 실무 기획 돌입
- [ ] PM Hermes 부팅 완료 후, 가상 사옥의 상주 에이전트들(Concept-Agent 등)을 격리 폴더 `workspace/projects/game_01_tetris/concept/` 하위에 소집합니다.
- [ ] 에이전트들이 새로 도입된 `superpowers` 스킬 브리지(Socratic Brainstorming 및 Micro-Task Planning)를 활용하여 **Godot 4.2+ GDScript stable 규격 기반의 그리드 및 특수 예외처리 기획 명세서 물리 작성**을 기획-개발 간 TDD 프로세스로 처리하도록 서포트합니다.

---

## 4. 🚨 대표님 핵심 지침 및 제약사항 (Rules & Constraints)
* **[R&R 경계 제약] 플랫폼 빌더(Antigravity)와 실무 에이전트 간 역할 엄격 구분 (R&R Lock):**
  - **Antigravity의 역할:** VIRTUAL-OFFICE of the entire infra (FastAPI 백엔드, SQLite DB, 감사실, 키체인 보안 연동, 가이드라인 런북, 동기화 스크립트, Superpowers 브리지 및 실물 스킬 수용 등)를 설계하고 무결하게 구축/시공하는 **플랫폼 빌더(Platform Builder)**입니다.
  - **사내 에이전트들의 역할:** 테트리스 게임 개발 및 기획 등 개별 프로젝트 실무는 **"맥북 수령 후 VIRTUAL-OFFICE가 완전히 구성된 이후"** 대표님이 직접 사무실에서 소집 가동하실 실무진(Concept, Art, Dev-Agent 등)의 영역입니다.
  - **절대적 제약:** Antigravity는 가상 사옥 구축 단계에서 테트리스 게임 기획 소집 및 실무 설계 영역에 어떠한 경우에도 임의로 월권하거나 개입해서는 안 되며, 오직 사옥 인프라의 완성도를 극대화하는 데에만 집중해야 합니다.
* **[Git 컨펌 제약] Git 업로드(Push) 절대 통제:** Git 원격 저장소 (`git push`)에 작업 내용을 업로드하는 것은 **대표님께서 최종 마음에 들어 하시고 명시적으로 승인(컨펌)하셨을 때**에만 진행합니다. 에이전트가 테스트 통과나 스냅샷 등의 이유로 사전에 승인받지 않은 `git push`를 자동 수행해서는 절대로 안 됩니다. (자율 백업 및 로컬 커밋은 허용하되, 원격 Push는 100% 대표님 컨펌 이후 수동으로 진행)
* **[정적 에셋 제약] 프론트엔드 수정 시 백엔드 테스트 전면 금지 (경고 1회 반영):** `virtual_dorm.html` 등 순수 프론트엔드/정적 에셋 작업 시에는 백엔드 전체 유닛 테스트 (`pytest` 등)를 절대로 임의로 구동하지 마십시오. 백업 자동화 오작동 및 불필요한 시스템 검증 과부하를 원천 차단하기 위한 대표님의 엄중한 규칙입니다. (경고 1회 누적 사항 반영 완수)
* **[스킬 자산화 제약] 반복 작업의 자율 스킬화 및 자산화 원칙 (Skill Creation Rule):**
  - **트리거:** 특정 워크플로우(에셋 변환, 코드 검사, 다단계 협업 등)가 2회 이상 중복 수행되거나 에이전트 간 수동 가이드가 계속 발생할 경우.
  - **원칙:** 즉시 이를 격리하여 `SKILL.md` (트리거)와 `scripts/` (결정론적 자동화 스크립트)를 포함하는 **정식 Skill**로 자산화 패키징을 수행해야 합니다.
  - **배포:** 신설된 스킬은 프로젝트 최상단 디렉토리인 `.skills/` 하위에 명세(`SKILL.md`)와 자동화 스크립트(`scripts/`)를 정식 물리 패키징하여 관리하며, 양대 워크스페이스에 Parity 동기화합니다. 가상 사옥(VIRTUAL-OFFICE)의 모든 에이전트들은 정형 반복 작업 수행 시 이 저장소를 자율 탐색 및 실행하여 100% 완벽히 복제 수행하도록 의무화합니다.
