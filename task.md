# 🎯 Team-203 VIRTUAL-OFFICE 가상 CTO 피드백 조치 및 인프라 고도화 태스크 보드 (task.md)

---

## 🏢 1. 🔌 로컬 의존성 제거 및 프로젝트 공식 스킬 저장소 통합
- [x] `.gemini/config/skills/workspace-parity` 내 로컬 심볼릭 링크 및 폴더 완전 제거
- [x] `Team-203` 프로젝트 최상단의 `.skills/` 디렉토리를 가상 사옥 공유 스킬 단일 저장소로 공식 설정

## ⚖️ 2. 📑 사내 운영 규정 및 가이드라인 정밀 개편
- [x] `MEMORY.md` 내 스킬 자산화 제약 조항 개정 (.gemini 의존 조항 전면 삭제)
- [x] `VIRTUAL_OFFICE.md` 내 제5조 [에이전트 자율 스킬 실행 및 자산화 규칙] 신설 명문화
- [x] `MEMORY.md` 내 플랫폼 빌더(Antigravity)와 실무 에이전트 간 R&R Lock 조항 명문화

## 👑 3. 🛡️ 가상 CTO(Claude-Code) 기술 피드백 조치 및 안전성 고도화 (11대 개선 과제)
- [/] **[Xcode CLT 확인]** 1단계 진단에 `xcode-select --install` 자동 확인 및 설치 단계 신설
- [ ] **[Ollama 기동 방식]** 2단계에 `open -a Ollama` 실패 시 `ollama serve &`로 자동 분기 기동 로직 추가
- [ ] **[let TIMEOUT-- 호환]** 2단계 zsh 호환을 위해 `((TIMEOUT--))` 문법으로 안전 교체
- [ ] **[디렉토리 검증]** 3단계 ComfyUI 클론 전 `mkdir -p`를 선행하여 경로 미존재로 인한 abort 예방
- [ ] **[pip 환경 격리]** ComfyUI venv 비활성화 후 전역 설치되던 의존성 문제를 venv 격리 단계 내부 설치로 수정
- [ ] **[ComfyUI 헬스체크]** 3단계 ComfyUI 포트(8188) 기동 직후 최대 30초 결정적 폴링 상태 체크 신설
- [ ] **[포트 보안 조임]** FastAPI 및 ComfyUI 포트 바인딩을 `0.0.0.0`에서 안전한 루프백 `127.0.0.1`로 변경
- [ ] **[의존성 파일 확인]** 4단계 `requirements.txt` 설치 전 물리 파일 실존 여부 체크 가드 탑재
- [ ] **[보안 권한 설정]** `.env` 생성 직후 즉시 `chmod 600 .env`를 실행하여 타 사용자의 비밀정보 읽기 탈취 원천 차단
- [ ] **[uvicorn venv 기동]** 5단계 Uvicorn 백그라운드 구동 전 반드시 `source venv/bin/activate` 선행 기동 명시
- [ ] **[sed 취약점 해결]** `.env` 정보 주입 시 특수문자 깨짐 및 취약점이 있는 `sed` 대신 파이썬 원라인(`python3 -c`) 안전 치환 엔진으로 교체

## 🔄 4. 👥 이중 워크스페이스 동기화 및 깃 버전 관리
- [ ] Secondary Workspace (`/Users/jabiseu/Documents/workspace/Team-203`)의 모든 수정 파일 Parity 동기화
- [ ] 로컬 작업 내역 스테이징 및 Git 로컬 커밋 생성 (Git Push는 대표님 지시 시에만 수행)
- [ ] `walkthrough.md` 작성 및 최종 완료 보고
