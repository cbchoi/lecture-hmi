# 슬라이드 콘텐츠 기술 명세서

## 1. 파일 구조

### 1.1 디렉토리 구조
```
slides/
├── week01-hci-hmi-theory/
│   ├── slides.json           # 파일 로드 순서 정의
│   ├── slides-01-intro.md    # 섹션별 분리된 마크다운 파일
│   ├── slides-02-theory.md
│   ├── slides-03-practice1.md
│   ├── slides-04-practice2.md
│   └── slides-05-practice3.md
└── week02-*/
```

### 1.2 slides.json 형식
```json
{
  "files": [
    "slides-01-intro.md",
    "slides-02-theory.md",
    "slides-03-practice1.md",
    "slides-04-practice2.md",
    "slides-05-practice3.md"
  ]
}
```

### 1.3 파일 크기 제한
- **권장**: 파일당 500줄 이하
- **최대**: 파일당 1000줄
- **이유**: 토큰 제한 및 편집 용이성

## 2. 마크다운 문법

### 2.1 슬라이드 구분자
```markdown
---
```
- 수평선 3개로 슬라이드 구분
- 파일 시작에는 불필요
- **파일 끝에는 절대 넣지 않기** (빈 슬라이드 방지)

### 2.2 제목 계층 구조
```markdown
# 주차 제목 (파일당 1회)
## 섹션 제목
### 서브섹션 제목
#### 상세 항목 제목
```

### 2.3 코드 블록

#### 기본 형식
```markdown
```language [start-end]
code content here
\```
```

#### 라인 번호 지정
- **올바른 형식**: `[1-25]`, `[26-50]`, `[101-125]`
- **잘못된 형식**: `{1-25}`, `(1-25)`
- Reveal.js가 자동으로 라인 번호 생성

#### 코드 내용 규칙
- **절대 금지**: 코드 내용에 하드코딩된 라인 번호
  ```markdown
  # 잘못된 예
  ```python [1-5]
  1  for i in range(10):
  2      print(i)
  \```

  # 올바른 예
  ```python [1-5]
  for i in range(10):
      print(i)
  \```
  ```

#### 지원 언어
- `python`
- `javascript`
- `csharp`
- `cpp`
- `java`
- `css`
- `html`
- `bash`

### 2.4 2단 레이아웃

#### 기본 구조
```markdown
<div class="grid grid-cols-2 gap-8">
<div>

왼쪽 내용 (주로 코드)

</div>
<div>

오른쪽 내용 (주로 설명)

</div>
</div>
```

#### 중요 규칙
1. **레이아웃 중간에 `---` 절대 금지**
   ```markdown
   # 잘못된 예 ❌
   <div class="grid grid-cols-2 gap-8">
   <div>

   ```code
   content
   \```

   ---  # 절대 안 됨!
   </div>
   <div>

   설명

   </div>
   </div>

   # 올바른 예 ✅
   <div class="grid grid-cols-2 gap-8">
   <div>

   ```code
   content
   \```

   </div>
   <div>

   설명

   </div>
   </div>
   ```

2. 양쪽 내용의 균형 유지
3. 코드와 설명의 일치성 확보

## 3. 콘텐츠 가이드라인

### 3.1 슬라이드당 적정 분량

#### 텍스트 전용 슬라이드
- **제목 + 목록**: 5-10개 항목
- **제목 + 단락**: 2-3개 단락
- **최대 높이**: 화면 1페이지 이내

#### 코드 포함 슬라이드
- **2단 레이아웃**: 코드 20-25줄 + 설명
- **전체 코드**: 30-40줄 이하
- **분할 기준**: Part 1, Part 2 등으로 나누기

#### 과도한 내용 감지 신호
- 슬라이드가 화면을 넘어감
- 스크롤이 필요함
- 가독성이 떨어짐

### 3.2 코드 분할 전략

#### 긴 코드 분할 방법
```markdown
---

#### JavaScript 코드 - Part 1

<div class="grid grid-cols-2 gap-8">
<div>

```javascript [1-25]
// 첫 25줄
\```

</div>
<div>

**Part 1 설명**
- 항목 1
- 항목 2

</div>
</div>

---

#### JavaScript 코드 - Part 2

<div class="grid grid-cols-2 gap-8">
<div>

```javascript [26-50]
// 다음 25줄
\```

</div>
<div>

**Part 2 설명**
- 항목 3
- 항목 4

</div>
</div>
```

### 3.3 시각적 요소

#### 리스트
- **Unordered list**: `-` 사용
- **Ordered list**: `1.`, `2.` 사용
- **Nested list**: 2칸 들여쓰기

#### 강조
- **굵게**: `**텍스트**`
- *기울임*: `*텍스트*`
- `코드`: `` `텍스트` ``

#### 링크
```markdown
[텍스트](URL)
```

## 4. CSS 스타일링

### 4.1 사용 가능한 클래스

#### Grid 레이아웃
- `grid`: 그리드 컨테이너
- `grid-cols-2`: 2열 레이아웃
- `gap-8`: 2rem 간격

### 4.2 자동 적용되는 스타일

#### 코드 블록
- 자동 줄바꿈 활성화
- 라인 번호 자동 생성
- Syntax highlighting
- 밑줄 제거

#### 제목
- 하단 경계선 자동 추가
- 색상: #2a5599
- 글꼴: Noto Sans KR

## 5. Reveal.js 설정

### 5.1 index.html 필수 설정
```javascript
highlight: {
    highlightOnLoad: true,
    lineNumbers: true
},
markdown: {
    smartypants: true,
    breaks: true
}
```

### 5.2 화면 크기
```javascript
width: 1400,
height: 900,
margin: 0.02
```

## 6. 품질 검증 체크리스트

### 6.1 구조 검증
- [ ] 모든 슬라이드가 화면 1페이지 이내
- [ ] 2단 레이아웃 중간에 `---` 없음
- [ ] 파일 끝에 `---` 없음
- [ ] 빈 슬라이드 없음

### 6.2 코드 검증
- [ ] 모든 코드 블록에 `[start-end]` 라인 번호 있음
- [ ] 코드 내용에 하드코딩된 라인 번호 없음
- [ ] 코드가 화면을 넘어가지 않음

### 6.3 내용 검증
- [ ] 제목 계층 구조가 논리적
- [ ] 코드와 설명이 일치
- [ ] 양쪽 컬럼의 균형이 적절

### 6.4 스타일 검증
- [ ] 모든 링크가 작동
- [ ] 이미지가 표시됨
- [ ] 특수문자가 올바르게 표시

## 7. 문제 해결

### 7.1 빈 슬라이드
**원인**: 파일 끝이나 2단 레이아웃 중간의 `---`
**해결**: 해당 `---` 제거

### 7.2 라인 번호 미표시
**원인**:
1. 잘못된 형식 `{1-25}` 사용
2. Reveal.js 설정 누락
3. 코드 내부에 하드코딩된 번호

**해결**:
1. `[1-25]` 형식으로 수정
2. `lineNumbers: true` 확인
3. 코드 내부 번호 제거

### 7.3 레이아웃 깨짐
**원인**: 2단 레이아웃 중간의 `---`
**해결**:
```bash
# 자동 수정 스크립트
python3 << 'EOF'
file_path = 'slides/week01/slides.md'
with open(file_path, 'r') as f:
    lines = f.readlines()

result = []
i = 0
while i < len(lines):
    if (i + 4 < len(lines) and
        lines[i].strip() == '```' and
        lines[i+2].strip() == '---' and
        lines[i+3].strip() == '</div>'):
        result.append(lines[i])
        result.append(lines[i+1])
        # Skip lines[i+2] (---)
        result.append(lines[i+3])
        result.append(lines[i+4])
        i += 5
    else:
        result.append(lines[i])
        i += 1

with open(file_path, 'w') as f:
    f.writelines(result)
EOF
```

### 7.4 코드 밑줄
**원인**: CSS 링크 스타일이 코드에 적용
**해결**: `custom.css`에 추가
```css
.theme-custom .reveal pre code *,
.theme-custom .reveal code,
.theme-custom .reveal pre {
    text-decoration: none !important;
    border-bottom: none !important;
}
```

## 8. 버전 관리

### 8.1 파일 동기화
```bash
# slides/ 디렉토리가 실제 서빙 파일
# src/slides/ 디렉토리는 소스 파일
cp src/slides/week01/*.md slides/week01/
```

### 8.2 변경 추적
- Git을 사용한 버전 관리 권장
- 주요 변경사항은 커밋 메시지에 명시

## 9. 성능 최적화

### 9.1 파일 크기
- 이미지는 최적화 후 사용
- 불필요한 공백 제거
- 중복 콘텐츠 최소화

### 9.2 로딩 속도
- 큰 파일은 분할
- slides.json으로 효율적 로딩
- 캐싱 활용

## 10. 접근성

### 10.1 텍스트
- 충분한 대비
- 읽기 쉬운 폰트 크기
- 명확한 제목 구조

### 10.2 코드
- 색맹 고려한 syntax highlighting
- 충분한 라인 간격
- 명확한 들여쓰기
