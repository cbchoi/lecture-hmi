## 실습 1: 인지과학 이론 체험

### 실습 목적
- Miller's Law와 Fitts' Law를 직접 체험하고 측정
- 반도체 HMI 설계에 적용할 수 있는 정량적 데이터 수집
- 이론과 실무의 연결점 이해

### Miller's Law 실험

#### 실험 설계
**도구**: 온라인 실험 플랫폼 (https://www.humanbenchmark.com/tests/sequence)
**참가자**: 전체 수강생 (N=20-30)
**실험 조건**:
- 숫자 시퀀스 기억 과제
- 시퀀스 길이: 3, 5, 7, 9, 11개
- 각 조건당 10회 시행

#### 실험 절차
1. **준비 단계** (5분)
   - 실험 플랫폼 접속 및 설정 확인
   - 개인별 ID 부여 (익명성 보장)
   - 연습 시행 3회 실시

2. **측정 단계** (20분)

<div class="grid grid-cols-2 gap-8">
<div>

```python {1-7}
1  for 시퀀스_길이 in [3, 5, 7, 9, 11]:
2      for 시행 in range(1, 11):
3          숫자_시퀀스_제시(길이=시퀀스_길이, 제시_시간=1초)
4          대기_시간(2초)
5          사용자_입력_대기()
6          정확도_기록(시퀀스_길이, 시행, 정답_여부)
7
```

</div>
<div>

**실험 프로토콜 설명**
- **Line 1**: 5가지 시퀀스 길이 조건을 순차 실행
- **Line 2**: 각 조건별로 10회 반복 시행
- **Line 3**: 지정된 길이의 숫자 시퀀스를 1초간 제시
- **Line 4**: 기억 강화를 위한 2초 대기시간
- **Line 5**: 참가자의 응답 입력 대기
- **Line 6**: 정답 여부를 데이터베이스에 기록

</div>
</div>

3. **데이터 수집** (5분)
   - 개인별 정확도 데이터 수집
   - Excel 파일로 실시간 저장
   - 기초 통계 계산

#### 예상 결과
- **3개 항목**: 정확도 95-100%
- **5개 항목**: 정확도 85-95%
- **7개 항목**: 정확도 70-85%
- **9개 항목**: 정확도 45-65%
- **11개 항목**: 정확도 25-45%

#### HMI 설계 적용
- 동시 표시 파라미터 수 제한
- 정보 그룹핑 전략 수립
- 알람 동시 발생 수 최적화

---

### Fitts' Law 실험

#### 실험 설계
**도구**: 커스텀 웹 애플리케이션
**측정 변수**:
- 목표 거리 (D): 100px, 200px, 400px
- 목표 크기 (W): 20px, 40px, 80px
- 총 9개 조건 조합

---

#### 실험 코드 (JavaScript) - Part 1

<div class="grid grid-cols-2 gap-8">
<div>

```javascript {1-25}
1  // Fitts' Law 실험 구현
2  class FittsLawExperiment {
3      constructor() {
4          this.canvas = document.getElementById('experimentCanvas');
5          this.ctx = this.canvas.getContext('2d');
6          this.results = [];
7          this.currentTrial = 0;
8          this.conditions = this.generateConditions();
9      }
10
11     generateConditions() {
12         const distances = [100, 200, 400];
13         const widths = [20, 40, 80];
14         let conditions = [];
15
16         for(let d of distances) {
17             for(let w of widths) {
18                 conditions.push({
19                     distance: d,
20                     width: w,
21                     indexOfDifficulty: Math.log2(d/w + 1)
22                 });
23             }
24         }
25         return this.shuffleArray(conditions);
```

</div>
<div>

**클래스 초기화 및 조건 생성**
- **Line 2-9**: FittsLawExperiment 클래스 생성자
  - 캔버스 요소와 2D 컨텍스트 초기화
  - 결과 저장 배열과 현재 시행 번호 초기화
  - 실험 조건 생성 메서드 호출

- **Line 11-25**: 실험 조건 생성 메서드
  - **Line 12-13**: 3가지 거리(100, 200, 400px)와 3가지 너비(20, 40, 80px) 정의
  - **Line 16-24**: 9가지 조건 조합 생성 (3×3 = 9개)
  - **Line 21**: Fitts' Law의 난이도 지수(ID) 계산: ID = log₂(D/W + 1)
  - **Line 25**: 조건 순서를 무작위로 섞어 순서 효과 제거

</div>
</div>

---

#### 실험 코드 (JavaScript) - Part 2

<div class="grid grid-cols-2 gap-8">
<div>

```javascript {26-50}
26     startTrial() {
27         const condition = this.conditions[this.currentTrial];
28         this.startTime = performance.now();
29
30         // 시작점과 목표점 그리기
31         this.drawStartPoint(50, 300);
32         this.drawTarget(50 + condition.distance, 300, condition.width);
33
34         this.canvas.addEventListener('click', this.handleClick.bind(this));
35     }
36
37     handleClick(event) {
38         const endTime = performance.now();
39         const rect = this.canvas.getBoundingClientRect();
40         const x = event.clientX - rect.left;
41         const y = event.clientY - rect.top;
42
43         const condition = this.conditions[this.currentTrial];
44         const targetX = 50 + condition.distance;
45         const targetY = 300;
46
47         const hit = this.isWithinTarget(x, y, targetX, targetY, condition.width);
48         const movementTime = endTime - this.startTime;
49
50         this.results.push({
```

</div>
<div>

**시행 시작 및 클릭 처리**
- **Line 26-35**: 개별 시행 시작 메서드
  - **Line 27**: 현재 시행의 실험 조건 가져오기
  - **Line 28**: 고정밀 타이머로 시작 시간 기록
  - **Line 31-32**: 시작점(50, 300)과 목표점 그리기
  - **Line 34**: 클릭 이벤트 리스너 등록

- **Line 37-50**: 클릭 이벤트 처리 메서드
  - **Line 38**: 클릭 시점의 종료 시간 기록
  - **Line 39-41**: 마우스 클릭 좌표를 캔버스 좌표로 변환
  - **Line 44-45**: 목표점의 실제 좌표 계산
  - **Line 47**: 클릭이 목표 영역 내부인지 판정
  - **Line 48**: 이동 시간 계산 (종료시간 - 시작시간)

</div>
</div>

---

#### 실험 코드 (JavaScript) - Part 3

<div class="grid grid-cols-2 gap-8">
<div>

```javascript {51-75}
51         trial: this.currentTrial + 1,
52         distance: condition.distance,
53         width: condition.width,
54         indexOfDifficulty: condition.indexOfDifficulty,
55         movementTime: movementTime,
56         hit: hit,
57         actualX: x,
58         actualY: y
59     });
60
61     this.nextTrial();
62 }
63
64 calculateResults() {
65     const validTrials = this.results.filter(r => r.hit);
66
67     // 회귀분석: MT = a + b * ID
68     const xValues = validTrials.map(r => r.indexOfDifficulty);
69     const yValues = validTrials.map(r => r.movementTime);
70
71     const n = xValues.length;
72     const sumX = xValues.reduce((a, b) => a + b, 0);
73     const sumY = yValues.reduce((a, b) => a + b, 0);
74     const sumXY = xValues.reduce((sum, x, i) => sum + x * yValues[i], 0);
75     const sumXX = xValues.reduce((sum, x) => sum + x * x, 0);
```

</div>
<div>

**결과 저장 및 회귀분석 시작**
- **Line 51-59**: 시행 결과 데이터 객체 생성
  - 시행 번호, 거리, 너비, 난이도 지수 저장
  - 이동 시간, 명중 여부, 실제 클릭 좌표 기록

- **Line 61**: 다음 시행으로 진행

- **Line 64-75**: 결과 계산 메서드
  - **Line 65**: 성공한 시행만 필터링 (명중한 경우만)
  - **Line 68-69**: 회귀분석을 위한 X값(난이도)과 Y값(시간) 추출
  - **Line 71-75**: 선형회귀 계산을 위한 통계값 산출
    - n: 데이터 개수, sumX/Y: 합계, sumXY/XX: 곱의 합계

</div>
</div>

---

#### 실험 코드 (JavaScript) - Part 4

<div class="grid grid-cols-2 gap-8">
<div>

```javascript {76-90}
76     const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
77     const intercept = (sumY - slope * sumX) / n;
78
79     return {
80         a: intercept,
81         b: slope,
82         equation: `MT = ${intercept.toFixed(2)} + ${slope.toFixed(2)} * ID`,
83         rSquared: this.calculateRSquared(xValues, yValues, slope, intercept)
84     };
85 }
86 }
87
88 // 데이터 분석
89 - **회귀식 도출**: MT = a + b × ID
90 - **개인차 분석**: 표준편차, 변이계수
```

</div>
<div>

**회귀분석 완료 및 결과 반환**
- **Line 76-77**: 최소제곱법으로 회귀계수 계산
  - **slope**: Fitts' Law의 기울기 (b), 난이도 증가에 따른 시간 증가율
  - **intercept**: y절편 (a), 기본 반응시간

- **Line 79-84**: 분석 결과 객체 반환
  - **a, b**: 회귀계수 (Fitts' Law: MT = a + b × ID)
  - **equation**: 사람이 읽기 쉬운 수식 문자열
  - **rSquared**: 결정계수 (모델의 설명력)

- **Line 88-90**: 추가 분석 항목
  - 개인별 성능 차이 분석을 위한 통계 지표
  - HMI 설계 가이드라인 도출을 위한 기초 데이터

</div>
</div>

#### 데이터 분석
- **회귀식 도출**: MT = a + b × ID
- **개인차 분석**: 표준편차, 변이계수
- **설계 지침**: 최적 버튼 크기 결정