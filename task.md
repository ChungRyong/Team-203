# 🎯 Team-203 VIRTUAL_DORM 화면보호기 개발 태스크 보드 (task.md)

---

## 🛌 1. 🎨 HTML5 Canvas 도트 캐릭터 및 물리 물리 모션 구현
- [x] `virtual_dorm.html` 뼈대 코드 및 True Black (`#000000`) 스타일 시트 구축
- [x] 자바스크립트 Canvas API 활용 에이전트 3종 (Hermes, Blinky, Dev-Agent) Pixel Art 도트 드로잉 모듈 코딩
- [x] 캐릭터 3종의 화면 바운더리 내 탄성 충돌 및 무작위 속도 배회 방랑 알고리즘 구현
- [x] 10 FPS 초저전력 프레임 갱신율(Eco-Frame Mode) 적용

## 📡 2. 🔌 실전 API 데이터 브리지 및 스마트 슬립 스케줄러 구현
- [x] FastAPI `api/tasks` 및 `api/audit/summary` fetch 호출 모듈 작성
- [x] 에이전트 실제 상태(활동/징계/대기) 판독을 통한 캐릭터 머리 위 동적 말풍선(Status Bubble) 구현
- [x] API 미감지 시 자율 일상 대사 15종 랜덤 송출 오프라인 Fail-Safe 로직 작성
- [x] 밤 12시 ~ 아침 8시 사이 캔버스 자동 픽셀 블랙아웃 및 완전 수면(Smart Sleep) 스케줄러 코딩

## 🔒 3. 💻 백엔드 CORS 허용 및 HTML 서빙 지원 연동
- [x] `app/main.py` 내 로컬 단독 HTML 호출에 따른 CORS 허용 세팅 추가
- [x] `app/main.py`에 화면보호기 HTML 정적 서빙(`/virtual-dorm`) 라우트 신설 연동
- [x] 가상 오피스 통합 배포 동기화 (Git & Workspace 양방향 복사 완료)

## 🧪 4. 📈 통합 검증 및 최종 시각 테스트
- [x] 화면보호기 API 서빙 정상 200 OK 여부 curl 및 통합 유닛 테스트 검증
- [x] 브라우저 전체화면(F11) 기동 시 도트 캐릭터 모션 및 실시간 API 말풍선 갱신 시각적 검증 완수
- [x] 무인 자동 깃 푸시(Keychain Always-Allow)를 통한 최종 깃허브 배포 마감
