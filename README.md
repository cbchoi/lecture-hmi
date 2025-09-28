# System Programming Lecture Slides

이 프로젝트는 강의를 위한 reveal.js 기반 프레젠테이션 시스템입니다.

## 📁 프로젝트 구조

```
reveal.js/
├── src/                    # 렌더링 컴포넌트
│   ├── index.html         # 메인 페이지
│   ├── css/               # 스타일시트
│   │   └── main.css       # 메인 CSS 파일
│   └── themes/            # 테마 파일
│       └── custom.css     # 커스텀 테마 (한글 폰트 지원)
├── tools/                  # 개발 도구
│   ├── bootstrap.py       # 동적 index.html 생성기
│   ├── export-pdf.mjs     # PDF 생성 스크립트
│   └── server.js          # Express 서버 설정
├── scripts/                # 실행 스크립트
│   ├── start-dev.bat      # Windows 개발 서버 실행
│   ├── start-dev.sh       # Linux/Mac 개발 서버 실행
│   ├── stop-dev.bat       # Windows 개발 서버 종료
│   ├── stop-dev.sh        # Linux/Mac 개발 서버 종료
│   ├── export-pdf.bat     # Windows PDF 생성
│   ├── export-pdf.sh      # Linux/Mac PDF 생성
│   └── setup-linux.sh     # Linux Chrome 의존성 설치
├── config/                 # 설정 파일
│   └── vite.config.ts     # Vite 설정
├── slides/                 # 강의 자료
│   ├── week01/
│   │   ├── slides.md      # 강의 슬라이드
│   │   ├── summary.md     # 주차별 요약
│   │   └── code/          # 주차별 코드 예제
│   ├── week02/
│   ├── week03/            # 파일과 디렉토리 API
│   ├── week04/            # 프로세스와 스레드 관리
│   ├── week05/            # 동기화와 뮤텍스
│   └── ...
├── template/               # 슬라이드 템플릿
├── pdf-exports/           # 생성된 PDF 저장소
└── .gitignore             # Git 제외 파일 목록
```

## 🚀 빠른 시작

### Windows 사용자

1. **개발 서버 시작**
   ```cmd
   scripts\start-dev.bat
   ```

2. **개발 서버 종료**
   ```cmd
   scripts\stop-dev.bat
   ```

3. **PDF 생성** (개별 주차)
   ```cmd
   scripts\export-pdf.bat 03
   ```

### Linux/Mac 사용자

**Linux 첫 실행 시 (PDF 기능 사용하려면):**
```bash
./scripts/setup-linux.sh
```

1. **개발 서버 시작**
   ```bash
   ./scripts/start-dev.sh
   ```

2. **개발 서버 종료**
   ```bash
   ./scripts/stop-dev.sh
   ```

3. **PDF 생성** (개별 주차)
   ```bash
   ./scripts/export-pdf.sh 03
   ```

## 📋 시스템 요구사항

### 공통
- Node.js 18+
- npm 8+

### PDF 생성 (Linux/WSL)
PDF 생성을 위해서는 Chrome 실행에 필요한 라이브러리가 설치되어야 합니다:

**자동 설치 (권장):**
```bash
./scripts/setup-linux.sh
```

**수동 설치:**
```bash
sudo apt update
# Ubuntu 24.04+ (최신)
sudo apt install -y \
  libnss3 \
  libatk-bridge2.0-0 \
  libdrm2 \
  libxcomposite1 \
  libxdamage1 \
  libxrandr2 \
  libgbm1 \
  libxss1 \
  libasound2t64 \
  libgtk-3-0t64

# 또는 이전 버전용
sudo apt install -y \
  libnss3 \
  libatk-bridge2.0-0 \
  libdrm2 \
  libxcomposite1 \
  libxdamage1 \
  libxrandr2 \
  libgbm1 \
  libxss1 \
  libasound2 \
  libgtk-3-0
```

## 💻 사용법

### 개발 모드

1. 적절한 플랫폼의 시작 스크립트를 실행
2. 브라우저에서 `http://localhost:5173` 접속
3. 원하는 주차를 선택하여 강의 확인

### PDF 생성

1. 개발 서버가 실행 중인지 확인
2. 해당 플랫폼의 PDF 생성 스크립트 실행
3. `pdf-exports/` 폴더에서 생성된 PDF 확인

### 새 강의 추가

1. `slides/weekXX/` 폴더 생성
2. `slides/weekXX/slides.md` 파일 생성 (강의 내용)
3. `slides/weekXX/summary.md` 파일 생성 (주차별 요약)
4. `tools/bootstrap.py` 실행하여 index.html 자동 생성
5. 개발 서버에서 확인

## 🛠️ 고급 사용법

### 수동 명령어

개발용 스크립트 대신 npm 명령어를 직접 사용할 수도 있습니다:

```bash
# 개발 서버 시작
npm run dev

# PDF 생성
npm run export-pdf -- --week 03

# 프로덕션 빌드
npm run build

# 프로덕션 서버
npm run start
```

### PDF 생성 옵션

```bash
# 특정 주차
npm run export-pdf -- --week 03

# 모든 주차
npm run export-pdf -- --all

# 커스텀 포트
npm run export-pdf -- --week 03 --port 8080
```

## 🎨 테마 및 커스터마이징

- **기본 테마**: Custom (화이트 기반, 한글 폰트 최적화)
- **커스텀 스타일**: `src/themes/custom.css`
  - Noto Sans KR 폰트 지원
  - PDF 전용 여백 및 스타일링
  - 코드 블록 한글 주석 지원
- **템플릿**: `template/` 폴더의 8가지 마크다운 템플릿
- **PDF 최적화**: 한글 폰트 렌더링 및 여백 개선

## 📝 슬라이드 작성법

마크다운 문법을 사용하여 슬라이드를 작성합니다:

```markdown
# 강의 제목

---

## 섹션 제목

내용...

---

### 코드 예제

```c
#include <stdio.h>
int main() {
    printf("Hello World\\n");
    return 0;
}
```

---
```

## 🔧 문제 해결

### PDF 생성 실패
- Linux/WSL: Chrome 라이브러리 설치 확인
- Windows: 개발 서버 실행 상태 확인
- 모든 플랫폼: 의존성 설치 확인 (`npm install`)

### 포트 충돌
- 다른 포트 사용: `config/vite.config.ts` 수정
- 실행 중인 프로세스 확인

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.