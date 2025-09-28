# Reveal.js Presentation System - Technical Specification

> **버전**: 3.0.0
> **최종 업데이트**: 2025년 9월 27일
> **시스템 유형**: 범용 프레젠테이션 관리 시스템

## 📖 문서 구분

이 명세서는 두 가지 관점으로 구분하여 작성되었습니다:

### 🔧 System Requirements (시스템 요구사항)
**대상**: 시스템 관리자, 개발자, DevOps 엔지니어
- 기술적 아키텍처 및 구현 사항
- 시스템 설치, 배포, 운영 가이드
- 성능, 보안, 모니터링 요구사항

### 📝 Content Requirements (콘텐츠 요구사항)
**대상**: 콘텐츠 제작자, 강사, 발표자
- 콘텐츠 구조 및 작성 가이드라인
- 메타데이터 및 품질 기준
- 콘텐츠 검증 및 배포 프로세스

---

## 🔧 SYSTEM REQUIREMENTS

### 시스템 아키텍처

#### 1. 기술 스택
```
Frontend:     HTML5, CSS3, JavaScript (ES6+), Reveal.js 4.x
Build Tool:   Vite 5.x
Runtime:      Node.js 18+, Python 3.9+
PDF Engine:   Puppeteer + Chrome Headless
Server:       Express.js (Production)
```

#### 2. 디렉토리 구조
```
project/
├── src/                    # 프론트엔드 렌더링
│   ├── index.html         # SPA 엔트리 포인트
│   ├── css/main.css       # 기본 스타일시트
│   └── themes/custom.css  # 테마 시스템
├── tools/                  # 개발 도구
│   ├── bootstrap.py       # 동적 인덱스 생성
│   ├── export-pdf.mjs     # PDF 생성 엔진
│   └── server.js          # 프로덕션 서버
├── scripts/                # 실행 스크립트
│   ├── *.sh / *.bat       # 크로스 플랫폼 스크립트
│   └── setup-linux.sh     # 환경 설정
├── config/                 # 설정 파일
│   └── vite.config.ts     # 빌드 설정
└── slides/                 # 콘텐츠 저장소
    └── [topic]/           # 주제별 폴더
```

#### 3. 시스템 요구사항

**최소 요구사항**:
- **OS**: Linux, macOS, Windows 10+
- **Memory**: 2GB RAM
- **Storage**: 1GB 여유 공간
- **Network**: HTTP/HTTPS 접근 (CDN용)

**권장 요구사항**:
- **OS**: Ubuntu 20.04+ / macOS 12+ / Windows 11
- **Memory**: 4GB+ RAM
- **Storage**: 5GB+ 여유 공간 (PDF 생성용)
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+

#### 4. 성능 기준

| 메트릭 | 목표 | 허용 범위 |
|--------|------|-----------|
| 서버 시작 시간 | < 1초 | < 3초 |
| 슬라이드 로딩 | < 500ms | < 1초 |
| PDF 생성 (10슬라이드) | < 10초 | < 30초 |
| 메모리 사용량 | < 500MB | < 1GB |
| 동시 사용자 | 50+ | 10+ |

### 배포 및 운영

#### 1. 개발 환경 설정

**자동 설정** (권장):
```bash
# Linux/Mac
./scripts/setup-linux.sh

# Windows
scripts\setup-windows.bat
```

**수동 설정**:
```bash
# 1. Node.js 설치 확인
node --version  # 18+ 필요

# 2. Python 설치 확인
python3 --version  # 3.9+ 필요

# 3. 의존성 설치
npm install

# 4. Chrome 의존성 (Linux)
sudo apt install -y libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2
```

#### 2. 프로덕션 배포

**Docker 컨테이너** (권장):
```dockerfile
FROM node:18-alpine

# 시스템 의존성
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    python3 \
    py3-pip

# 환경 변수
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]
```

**전통적 배포**:
```bash
# 1. 빌드
npm run build

# 2. 정적 파일 서버 설정
# Nginx, Apache, 또는 Express.js 사용

# 3. 프로세스 관리
pm2 start tools/server.js --name presentation-system
```

#### 3. 모니터링 및 로깅

**시스템 헬스 체크**:
```javascript
// tools/health-check.js
const healthChecks = {
    server: async () => {
        const response = await fetch('http://localhost:3000/health');
        return response.ok;
    },

    pdfGeneration: async () => {
        // PDF 생성 테스트
        const testPdf = await generatePDF('test');
        return testPdf.length > 1000;
    },

    contentAccess: async () => {
        // 콘텐츠 접근 테스트
        const slides = await fs.readdir('slides/');
        return slides.length > 0;
    }
};
```

**로그 수집**:
```bash
# 애플리케이션 로그
tail -f logs/app.log

# PDF 생성 로그
tail -f logs/pdf-generation.log

# 에러 로그
tail -f logs/error.log
```

### 보안 요구사항

#### 1. 파일 시스템 보안
```python
# 경로 검증 함수
def validate_topic_path(topic: str) -> bool:
    # 디렉토리 트래버설 방지
    if '..' in topic or topic.startswith('/'):
        return False

    # 허용된 문자만 사용
    return re.match(r'^[a-zA-Z0-9\-_]+$', topic) is not None
```

#### 2. 웹 보안
```html
<!-- Content Security Policy -->
<meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com;
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
    font-src 'self' https://fonts.gstatic.com;
    img-src 'self' data:;
">
```

#### 3. API 보안
```javascript
// 입력 검증 미들웨어
function validateInput(req, res, next) {
    const { topic } = req.params;

    if (!isValidTopic(topic)) {
        return res.status(400).json({ error: 'Invalid topic name' });
    }

    next();
}
```

### CI/CD 파이프라인

#### GitHub Actions 워크플로우:
```yaml
name: System Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  system-test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install system dependencies
      run: |
        sudo apt update
        sudo apt install -y libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2

    - name: Install project dependencies
      run: npm ci

    - name: Run system tests
      run: |
        npm run test:system
        python -m pytest tests/system/

    - name: Test PDF generation
      run: |
        npm run dev &
        sleep 10
        npm run export-pdf -- --week test
        pkill -f vite

    - name: Build production
      run: npm run build

    - name: Deploy to staging
      if: github.ref == 'refs/heads/main'
      run: |
        # 배포 스크립트 실행
        ./scripts/deploy-staging.sh
```

---

## 📝 CONTENT REQUIREMENTS

### 콘텐츠 구조 표준

#### 1. 폴더 구조 규칙
```
slides/
└── [topic-name]/              # 주제명 (영문 소문자, 하이픈)
    ├── slides.md              # 슬라이드 콘텐츠 (필수)
    ├── summary.md             # 메타데이터 및 요약 (필수)
    ├── code/                  # 코드 예제 (선택)
    │   ├── example1.js
    │   └── exercise.py
    ├── images/                # 이미지 리소스 (선택)
    │   ├── diagram.png
    │   └── screenshot.jpg
    └── data/                  # 데이터 파일 (선택)
        └── sample.json
```

#### 2. 파일명 규칙

**주제 폴더명**:
- **영문 소문자 + 하이픈**: `machine-learning`, `web-development`
- **순서가 있는 경우**: `01-introduction`, `02-basics`, `03-advanced`
- **시리즈별 구분**: `week01`, `chapter01`, `session01`

**파일명 표준**:
- `slides.md`: 메인 슬라이드 (필수)
- `summary.md`: 주제 요약 (필수)
- `README.md`: 추가 설명 (선택)

#### 3. 메타데이터 표준

**summary.md 템플릿**:
```markdown
# [주제 제목]

## 🎯 학습 목표
- 구체적이고 측정 가능한 목표 1
- 구체적이고 측정 가능한 목표 2
- 구체적이고 측정 가능한 목표 3

## 📚 주요 내용
- 핵심 개념 1 (이론)
- 핵심 개념 2 (실습)
- 핵심 개념 3 (응용)

## ⏰ 예상 소요 시간
- **발표**: 45분
- **Q&A**: 15분
- **실습**: 30분
- **총합**: 90분

## 👥 대상 청중
- **수준**: 초급/중급/고급
- **사전 지식**: 필요한 배경 지식
- **도구 경험**: 필요한 도구 사용 경험

## 💻 실습 환경
- **운영체제**: Windows 10+, macOS 12+, Ubuntu 20.04+
- **필수 소프트웨어**: Node.js 18+, VS Code
- **선택 소프트웨어**: Docker, Git

## 📖 사전 준비
- [ ] [필수 문서](링크) 읽기
- [ ] 개발 환경 설정
- [ ] 샘플 파일 다운로드

## 🔗 참고 자료
- [공식 문서](URL)
- [튜토리얼](URL)
- [추가 학습 자료](URL)

## 📋 체크리스트
- [ ] 학습 목표 이해
- [ ] 실습 환경 준비
- [ ] 사전 자료 숙지
- [ ] 질문 사항 정리
```

### 콘텐츠 작성 가이드라인

#### 1. 슬라이드 구조

**기본 템플릿**:
```markdown
# [주제 제목]
> 부제목 또는 한 줄 설명

---

## 📋 오늘의 목표

- 목표 1
- 목표 2
- 목표 3

---

## 🗺️ 진행 순서

1. 개념 이해
2. 실습 진행
3. 응용 및 확장
4. 질의응답

---

## 📖 개념 이해

### 핵심 개념 1

설명...

---

### 핵심 개념 2

설명...

---

## 💻 실습 진행

### 실습 1: 기본 사용법

```javascript
// 코드 예제
function example() {
    console.log("Hello World");
}
```

---

### 실습 2: 심화 내용

```python
# Python 예제
def advanced_example():
    return "Advanced concept"
```

---

## 🚀 응용 및 확장

### 실제 활용 사례

- 사례 1
- 사례 2

---

### 추가 학습 방향

- 추천 자료 1
- 추천 자료 2

---

## 📝 정리

### 오늘 배운 내용

- 요약 1
- 요약 2
- 요약 3

---

### 다음 주제 예고

다음에는...

---

## ❓ 질의응답

질문해 주세요!
```

#### 2. 콘텐츠 품질 기준

**텍스트 기준**:
- **글자 수**: 슬라이드당 최대 150자 (한글 기준)
- **목록 항목**: 슬라이드당 최대 7개
- **제목 계층**: 최대 3단계 (H1 > H2 > H3)

**시각적 기준**:
- **폰트 크기**: 최소 24px (발표용)
- **색상 대비**: 4.5:1 이상
- **이미지 해상도**: 최소 1920x1080 (16:9 비율)

**접근성 기준**:
- **대체 텍스트**: 모든 이미지에 필수
- **언어 태그**: 다국어 콘텐츠 시 명시
- **키보드 탐색**: 모든 기능 접근 가능

#### 3. 코드 예제 표준

**파일 구조**:
```
code/
├── examples/          # 완성된 예제
│   ├── basic.js
│   └── advanced.py
├── exercises/         # 연습 문제
│   ├── problem1.js
│   └── problem2.py
└── solutions/         # 해답
    ├── solution1.js
    └── solution2.py
```

**코드 작성 규칙**:
```javascript
// ✅ 좋은 예제: 주석과 설명이 충분함
/**
 * 사용자 데이터를 검증하는 함수
 * @param {Object} user - 사용자 객체
 * @returns {boolean} 검증 결과
 */
function validateUser(user) {
    // 필수 필드 확인
    if (!user.name || !user.email) {
        return false;
    }

    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(user.email);
}

// ❌ 나쁜 예제: 설명 부족, 복잡함
function complex(x,y,z){return x?y.map(i=>i*z).filter(i=>i>0):[];}
```

### 콘텐츠 검증 프로세스

#### 1. 자동 검증

**메타데이터 검증**:
```python
# tools/validate-content.py
def validate_content_structure(topic_path: Path) -> List[str]:
    """콘텐츠 구조 검증"""
    errors = []

    # 필수 파일 확인
    required_files = ['slides.md', 'summary.md']
    for file in required_files:
        if not (topic_path / file).exists():
            errors.append(f"Missing required file: {file}")

    # 메타데이터 검증
    summary_file = topic_path / 'summary.md'
    if summary_file.exists():
        content = summary_file.read_text()
        if '# ' not in content:
            errors.append("Missing title in summary.md")
        if '## 🎯 학습 목표' not in content:
            errors.append("Missing learning objectives")

    return errors
```

**콘텐츠 품질 검증**:
```python
def validate_content_quality(slides_content: str) -> List[str]:
    """콘텐츠 품질 검증"""
    warnings = []

    # 슬라이드 개수 확인
    slide_count = slides_content.count('\n---\n')
    if slide_count > 50:
        warnings.append("Too many slides (>50). Consider splitting.")

    # 텍스트 밀도 확인
    slides = slides_content.split('\n---\n')
    for i, slide in enumerate(slides):
        char_count = len(slide.replace(' ', ''))
        if char_count > 500:
            warnings.append(f"Slide {i+1} has too much text ({char_count} chars)")

    return warnings
```

#### 2. 수동 검토 체크리스트

**콘텐츠 리뷰**:
- [ ] 학습 목표가 명확하고 측정 가능한가?
- [ ] 내용이 논리적 순서로 구성되었는가?
- [ ] 실습과 이론의 균형이 적절한가?
- [ ] 대상 청중에게 적합한 난이도인가?

**기술적 검토**:
- [ ] 모든 코드 예제가 동작하는가?
- [ ] 이미지가 올바르게 표시되는가?
- [ ] 링크가 유효한가?
- [ ] PDF 생성이 정상적인가?

**품질 검토**:
- [ ] 맞춤법과 문법이 올바른가?
- [ ] 용어 사용이 일관성 있는가?
- [ ] 접근성 기준을 만족하는가?
- [ ] 브랜드 가이드라인을 따르는가?

### 콘텐츠 배포 워크플로우

#### 1. 개발 단계
```bash
# 1. 새 주제 브랜치 생성
git checkout -b content/new-topic

# 2. 콘텐츠 작성
mkdir slides/new-topic
# ... 파일 생성 및 작성 ...

# 3. 로컬 검증
python3 tools/validate-content.py slides/new-topic
python3 tools/bootstrap.py
npm run dev

# 4. PDF 생성 테스트
npm run export-pdf -- --topic new-topic
```

#### 2. 검토 단계
```bash
# 1. Pull Request 생성
git push origin content/new-topic
# GitHub에서 PR 생성

# 2. 자동 검증 (CI/CD)
# - 콘텐츠 구조 검증
# - 품질 기준 확인
# - PDF 생성 테스트

# 3. 동료 검토
# - 콘텐츠 리뷰
# - 기술적 검토
# - 품질 검토
```

#### 3. 배포 단계
```bash
# 1. main 브랜치 병합
git checkout main
git merge content/new-topic

# 2. 자동 배포 (CI/CD)
# - 프로덕션 빌드
# - PDF 생성
# - 배포 환경 업데이트

# 3. 배포 검증
# - 프로덕션 환경 테스트
# - 사용자 피드백 수집
```

---

## 🔗 참조 관계

### 시스템 ↔ 콘텐츠 연동점

1. **Bootstrap System**: 콘텐츠 메타데이터 → 시스템 네비게이션
2. **PDF Generation**: 콘텐츠 구조 → PDF 레이아웃
3. **Validation**: 콘텐츠 품질 → 시스템 안정성
4. **Deployment**: 콘텐츠 변경 → 시스템 업데이트

### 단계별 참조 가이드

**단계 1 - 시스템 설치**: System Requirements → [instruction.md](instruction.md)
**단계 2 - 콘텐츠 작성**: Content Requirements → [instruction.md](instruction.md)
**단계 3 - 시스템 테스트**: System + Content → [acceptance_test/](acceptance_test/)
**단계 4 - 운영 관리**: 전체 명세서 + 모니터링

---

이 명세서는 시스템과 콘텐츠 양 측면의 요구사항을 모두 다루며, 각 역할별로 필요한 부분을 참조할 수 있도록 구성되었습니다.