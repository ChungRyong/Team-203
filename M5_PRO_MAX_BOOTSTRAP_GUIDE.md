# 🚀 M5 Pro Max 사용자 수동 부트스트랩 가이드 (USER-ACTION GUIDE)

에이전트(Hermes)가 자율 프로비저닝을 완수하기 위해, 보안 및 시스템 정책상 **대표님께서 직접 실행해주셔야 하는 필수 작업**입니다.

## 🛠️ 대표님 수행 작업 리스트

### 1. Xcode Command Line Tools 설치 (최초 1회)
터미널에서 아래 명령어를 실행한 후, 화면에 뜨는 macOS 팝업창에서 **[설치]** 버튼을 클릭하십시오.
```bash
xcode-select --install
```

### 2. Homebrew 무인 설치 및 권한 승인 (최초 1회)
아래 명령어를 복사하여 터미널에 실행하십시오. 중간에 `Password:` 요청이 나오면 **Mac 로그인 암호**를 입력하십시오. (입력 시 글자가 보이지 않는 것이 정상이니 그대로 치고 Enter를 누르시면 됩니다.)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 3. Homebrew 환경 변수 적용 (설치 후 필수)
설치가 끝난 후 터미널 하단의 `Next steps` 안내에 따라 아래 명령어를 실행하여 경로를 설정하십시오.
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

---

## 💡 에이전트 안내 사항 (Hermes 전용)
- 위 작업들이 완료된 후에만 `brew install` 및 `python3.13` 설치 단계가 정상 작동합니다.
- 사용자가 "설치 완료"라고 응답하면 즉시 $	ext{export PATH}$를 수행하고 프로비저닝을 재개하십시오.
