# 🎯 Team-203 VIRTUAL-OFFICE 에이전트 자율 스킬 및 키체인 보안 연동 태스크 보드 (task.md)

---

## 🏢 1. 🔌 로컬 의존성 제거 및 프로젝트 공식 스킬 저장소 통합
- [x] `.gemini/config/skills/workspace-parity` 내 로컬 심볼릭 링크 및 폴더 완전 제거
- [x] `Team-203` 프로젝트 최상단의 `.skills/` 디렉토리를 가상 사옥 공유 스킬 단일 저장소로 공식 설정

## ⚖️ 2. 📑 사내 운영 규정 및 가이드라인 정밀 개편
- [x] `MEMORY.md` 내 스킬 자산화 제약 조항 개정 (.gemini 의존 조항 전면 삭제)
- [x] `VIRTUAL_OFFICE.md` 내 제5조 [에이전트 자율 스킬 실행 및 자산화 규칙] 신설 명문화

## 🛡️ 3. 🔑 macOS Keychain 기반의 하드웨어 보안 연동 구현
- [/] `PM_AGENT_INFRA_PROVISIONING_GUIDE.md`에 키체인 등록 명령어 및 가이드 공식 수록
- [ ] `bootstrap.py` 리팩토링: macOS 키체인 연동을 통해 민감한 토큰/API 자동 추출 및 `.env` 파일 무인 동적 생성 모듈 탑재

## 🔄 4. 👥 이중 워크스페이스 동기화 및 깃 버전 관리
- [ ] Secondary Workspace (`/Users/jabiseu/Documents/workspace/Team-203`)의 모든 수정 파일 Parity 동기화
- [ ] 로컬 작업 내역 스테이징 및 Git 로컬 커밋 생성 (Git Push는 대표님 지시 시에만 수행)
- [ ] `walkthrough.md` 작성 및 최종 완료 보고
