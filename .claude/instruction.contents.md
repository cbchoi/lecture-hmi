# 슬라이드 콘텐츠 작성 지침

## 목적
이 문서는 Reveal.js 기반 강의 슬라이드 제작 시 가독성과 일관성을 보장하기 위한 작성 지침입니다.

## 핵심 원칙

### 1. 한 슬라이드, 한 화면
- 모든 슬라이드는 **스크롤 없이 한 화면에 표시**되어야 합니다
- 화면을 넘어가는 콘텐츠는 여러 슬라이드로 분할합니다
- 적정 높이: 1400x900px 기준 약 80% 이내

### 2. 명확한 구조
- 논리적인 제목 계층 구조를 유지합니다
- 한 슬라이드는 하나의 개념이나 주제를 다룹니다
- 관련 내용은 연속된 슬라이드로 구성합니다

### 3. 시각적 균형
- 2단 레이아웃 사용 시 양쪽 분량의 균형을 맞춥니다
- 텍스트와 코드의 비율을 적절히 조절합니다
- 여백을 활용하여 가독성을 높입니다

## 슬라이드 작성 규칙

### 제목 구조

```markdown
# Week 01: 주차 제목
## 대주제
### 중주제
#### 세부 항목
```

**규칙:**
- `#` 주차 제목은 파일당 1회만 사용
- `##` 대주제는 새로운 섹션 시작 시
- `###` 중주제는 섹션 내 구분 시
- `####` 세부 항목은 상세 설명 시

### 슬라이드 구분

```markdown
---
```

**규칙:**
1. 슬라이드 사이에만 사용
2. 파일 시작에는 불필요
3. **파일 끝에는 절대 금지** (빈 슬라이드 방지)
4. **2단 레이아웃 내부에는 절대 금지**

**올바른 예:**
```markdown
### 슬라이드 1
내용

---

### 슬라이드 2
내용
```

**잘못된 예:**
```markdown
### 슬라이드 1
내용

---
```
(파일 끝)

### 코드 블록 작성

#### 기본 형식
```markdown
```language [start-end]
code content
\```
```

**예시:**
```markdown
```python [1-10]
def hello():
    print("Hello, World!")
\```
```

#### 라인 번호 규칙
1. **반드시 `[start-end]` 형식 사용**
   - ✅ `[1-25]`
   - ❌ `{1-25}`, `(1-25)`

2. **연속된 범위 지정**
   - Part 1: `[1-25]`
   - Part 2: `[26-50]`
   - Part 3: `[51-75]`

3. **코드 내부에 라인 번호 절대 금지**
   ```markdown
   # ❌ 잘못된 예
   ```python [1-3]
   1  def hello():
   2      print("Hello")
   3      return
   \```

   # ✅ 올바른 예
   ```python [1-3]
   def hello():
       print("Hello")
       return
   \```
   ```

#### 지원 언어
- Python: `python`
- JavaScript: `javascript`
- C#: `csharp`
- C++: `cpp`
- CSS: `css`
- HTML: `html`
- Bash: `bash`

### 2단 레이아웃 작성

#### 기본 템플릿
```markdown
### 제목

<div class="grid grid-cols-2 gap-8">
<div>

왼쪽 내용 (주로 코드)

</div>
<div>

오른쪽 내용 (주로 설명)

</div>
</div>
```

#### 작성 규칙

1. **코드 + 설명 패턴**
```markdown
<div class="grid grid-cols-2 gap-8">
<div>

```python [1-15]
class Example:
    def __init__(self):
        self.value = 0
\```

</div>
<div>

**클래스 설명**
- **Line 1**: 클래스 선언
- **Line 2**: 생성자 정의
- **Line 3**: 초기값 설정

</div>
</div>
```

2. **절대 금지 사항**
```markdown
# ❌ 레이아웃 중간에 --- 사용 금지
<div class="grid grid-cols-2 gap-8">
<div>

코드

---  # 이것이 문제!
</div>
<div>

설명

</div>
</div>
```

3. **양쪽 균형 유지**
   - 코드 20줄 → 설명 10-15개 항목
   - 코드가 길면 여러 Part로 분할
   - 설명이 짧으면 코드를 줄이거나 설명 추가

### 코드 분할 전략

#### 긴 코드 분할 방법

**원칙:**
- 한 슬라이드당 코드 25줄 이하 권장
- 논리적 단위로 분할 (함수, 클래스 단위)
- Part 번호로 연속성 표시

**예시:**
```markdown
---

#### Python 코드 - Part 1

<div class="grid grid-cols-2 gap-8">
<div>

```python [1-25]
# 첫 번째 부분
import numpy as np

class DataAnalyzer:
    def __init__(self):
        self.data = []

    def load_data(self, filename):
        # 데이터 로드
        pass
\```

</div>
<div>

**클래스 초기화 및 데이터 로드**
- **Line 1**: NumPy import
- **Line 3**: DataAnalyzer 클래스 선언
- **Line 4-5**: 생성자 정의
- **Line 7-9**: 데이터 로드 메서드

</div>
</div>

---

#### Python 코드 - Part 2

<div class="grid grid-cols-2 gap-8">
<div>

```python [26-50]
    def analyze(self):
        # 데이터 분석
        results = {}
        results['mean'] = np.mean(self.data)
        results['std'] = np.std(self.data)
        return results
\```

</div>
<div>

**데이터 분석 메서드**
- **Line 26**: 분석 메서드 시작
- **Line 28-30**: 통계 계산
- **Line 31**: 결과 반환

</div>
</div>
```

### 적정 분량 가이드

#### 텍스트 전용 슬라이드
```markdown
### 제목

**소제목**
- 항목 1 (1-2줄)
- 항목 2 (1-2줄)
- 항목 3 (1-2줄)
- 항목 4 (1-2줄)
- 항목 5 (1-2줄)

**권장:** 5-10개 항목
**최대:** 15개 항목
```

#### 코드 슬라이드
```markdown
### 제목

<div class="grid grid-cols-2 gap-8">
<div>

```language [1-25]
# 코드 20-25줄
\```

</div>
<div>

**설명**
- 10-15개 설명 항목

</div>
</div>

**권장:** 코드 20-25줄 + 설명 10-15항목
**최대:** 코드 30줄 + 설명 20항목
```

#### 이미지 + 설명 슬라이드
```markdown
### 제목

![이미지](path/to/image.png)

- 설명 1
- 설명 2
- 설명 3

**권장:** 이미지 1개 + 설명 3-5항목
```

## 스타일 가이드

### 강조 표현

```markdown
**굵게** - 중요한 용어, 키워드
*기울임* - 약한 강조
`코드` - 인라인 코드, 변수명
```

### 리스트

```markdown
# Unordered list
- 항목 1
- 항목 2
  - 하위 항목 (2칸 들여쓰기)

# Ordered list
1. 첫 번째
2. 두 번째
3. 세 번째
```

### 링크

```markdown
[표시 텍스트](https://url.com)
[문서 참조](./docs/reference.md)
```

## 콘텐츠 작성 프로세스

### 1. 계획 단계
1. 전체 주제 파악
2. 섹션별 분할 계획
3. 슬라이드 개수 추정
4. 코드 예제 준비

### 2. 초안 작성
1. 제목 구조 먼저 작성
2. 각 슬라이드 내용 채우기
3. 코드 블록 추가
4. 설명 작성

### 3. 검토 및 수정
1. 브라우저에서 미리보기
2. 한 화면 초과 슬라이드 분할
3. 레이아웃 균형 조정
4. 오타 및 문법 검사

### 4. 최종 검증
```bash
# 개발 서버 실행
npm run dev

# 브라우저에서 확인
http://localhost:5173/?week=01
```

**체크리스트:**
- [ ] 모든 슬라이드가 한 화면에 표시되는가?
- [ ] 라인 번호가 올바르게 표시되는가?
- [ ] 2단 레이아웃이 깨지지 않았는가?
- [ ] 빈 슬라이드가 없는가?
- [ ] 코드와 설명이 일치하는가?

## 문제 해결 가이드

### 빈 슬라이드 발생
**증상:** 내용 없는 빈 슬라이드가 나타남

**원인:**
1. 파일 끝에 `---` 존재
2. 연속된 `---` 존재

**해결:**
```bash
# 파일 끝 --- 제거
sed -i '$ { /^---$/d }' slides/week01/slides.md

# 중복 --- 검사
grep -n "^---$" slides/week01/slides.md
```

### 라인 번호 미표시
**증상:** 코드 블록에 라인 번호가 표시되지 않음

**원인:**
1. 잘못된 형식 사용 `{1-25}`
2. 코드 내부에 하드코딩된 번호

**해결:**
```bash
# 잘못된 형식 수정
sed -i 's/```\([a-z]*\) {\([0-9-]*\)}/```\1 [\2]/g' slides/week01/slides.md

# 하드코딩된 라인 번호 제거 (Python 스크립트 실행)
python3 scripts/remove_line_numbers.py slides/week01/slides.md
```

### 레이아웃 깨짐
**증상:** 2단 레이아웃이 세로로 표시됨

**원인:** 레이아웃 중간에 `---` 존재

**해결:**
```bash
python3 scripts/fix_grid_layout.py slides/week01/slides.md
```

### 코드 화면 넘침
**증상:** 코드가 오른쪽으로 넘어감

**원인:** 긴 줄

**해결:**
- CSS 자동 줄바꿈 확인 (이미 적용됨)
- 코드 줄 길이 조정
- 주석으로 분할

## 베스트 프랙티스

### 1. 코드 주석
```python
# ✅ 간결하고 명확한 주석
def calculate_mean(data):
    """평균 계산"""
    return sum(data) / len(data)

# ❌ 너무 긴 주석
def calculate_mean(data):
    """
    이 함수는 입력된 데이터 리스트의 산술 평균을 계산합니다.
    매우 긴 설명은 슬라이드 설명 섹션에 작성하세요.
    """
    return sum(data) / len(data)
```

### 2. 설명 작성
```markdown
# ✅ 명확하고 구조적
**데이터 로드 함수**
- **Line 1-3**: 파일 열기 및 읽기
- **Line 4-6**: 데이터 파싱
- **Line 7**: 결과 반환

# ❌ 장황한 설명
**데이터 로드 함수**
이 함수는 파일을 읽어서 데이터를 로드하는 기능을 수행합니다.
먼저 파일을 열고, 그 다음에 내용을 읽고, 파싱한 후 반환합니다.
```

### 3. 슬라이드 흐름
```markdown
# ✅ 논리적 흐름
1. 개념 소개
2. 문제 정의
3. 해결 방법
4. 코드 예제
5. 결과 분석

# ❌ 흐름 없음
1. 코드 예제
2. 개념 소개
3. 결과 분석
4. 문제 정의
```

## 템플릿

### 코드 설명 슬라이드
```markdown
---

### [제목] - Part [N]

<div class="grid grid-cols-2 gap-8">
<div>

```[language] [start-end]
# 코드 내용
\```

</div>
<div>

**[소제목]**
- **Line X-Y**: [설명]
- **Line Z**: [설명]

**[추가 섹션]**
- [내용]

</div>
</div>
```

### 개념 설명 슬라이드
```markdown
---

### [제목]

#### [소제목 1]
- [항목 1]
- [항목 2]

#### [소제목 2]
- [항목 3]
- [항목 4]

**[강조 내용]**
[중요 정보]
```

### 실습 슬라이드
```markdown
---

### [실습 제목]

#### 목표
[실습 목표 설명]

#### 단계
1. [단계 1]
2. [단계 2]
3. [단계 3]

#### 성공 기준
- [기준 1]
- [기준 2]
```

## 참고 자료

### 관련 문서
- [specification.contents.md](./specification.contents.md) - 기술 명세
- [Reveal.js 문서](https://revealjs.com/) - 공식 문서
- [Markdown 가이드](https://www.markdownguide.org/) - 마크다운 문법

### 유용한 스크립트
```bash
# slides/ 디렉토리
scripts/
├── remove_line_numbers.py    # 하드코딩 라인 번호 제거
├── fix_grid_layout.py        # 그리드 레이아웃 수정
└── validate_slides.py        # 슬라이드 검증
```

### 자주 사용하는 명령어
```bash
# 개발 서버 실행
npm run dev

# 특정 주차 보기
http://localhost:5173/?week=01

# 파일 동기화
cp src/slides/week01/*.md slides/week01/

# Git 커밋
git add slides/
git commit -m "Update week01 slides"
```

## 버전 정보
- **버전**: 1.0.0
- **최종 수정**: 2025-01-10
- **작성자**: HMI Lecture Team
- **Reveal.js 버전**: 5.0.4
