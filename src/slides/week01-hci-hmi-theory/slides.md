# 반도체 장비를 위한 HCI/HMI 이론 기초
> 산업용 인터페이스 설계의 핵심 원리와 실제 적용

---

## 📋 오늘의 학습 목표

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #007bff; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #1a365d;">HCI vs HMI:</strong> 개념적 차이점과 반도체 환경에서의 적용</li>
        <li><strong style="color: #1a365d;">산업 환경:</strong> 반도체 FAB의 특수한 요구사항 이해</li>
        <li><strong style="color: #1a365d;">설계 원칙:</strong> 사용자 중심 인터페이스 설계 방법론</li>
        <li><strong style="color: #1a365d;">실무 적용:</strong> 실제 장비 운영자 관점에서의 분석</li>
    </ul>
</div>

---

## 🗺️ 강의 진행 순서

<div style="display: flex; flex-direction: column; gap: 1rem; margin: 1.5rem 0;">
    <div style="display: flex; align-items: center; background: #e8f5e8; padding: 1rem; border-radius: 8px;">
        <div style="background: #28a745; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">1</div>
        <span style="color: #155724;"><strong>이론 (45분):</strong> HCI/HMI 개념과 반도체 환경 특성</span>
    </div>
    <div style="display: flex; align-items: center; background: #e3f2fd; padding: 1rem; border-radius: 8px;">
        <div style="background: #2196f3; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">2</div>
        <span style="color: #0d47a1;"><strong>기초 실습 (45분):</strong> 기존 장비 HMI 분석 및 페르소나 개발</span>
    </div>
    <div style="display: flex; align-items: center; background: #f3e5f5; padding: 1rem; border-radius: 8px;">
        <div style="background: #9c27b0; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">3</div>
        <span style="color: #4a148c;"><strong>심화 실습 (45분):</strong> HMI 프로토타입 설계</span>
    </div>
    <div style="display: flex; align-items: center; background: #fff3cd; padding: 1rem; border-radius: 8px;">
        <div style="background: #f39c12; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">4</div>
        <span style="color: #856404;"><strong>Hands-on (45분):</strong> 요구사항 도출 시뮬레이션</span>
    </div>
</div>

---

# 📖 이론 강의 (45분)

---

## HCI와 HMI의 개념적 차이

<div style="margin: 2rem 0;">

### 🖥️ Human Computer Interaction (HCI)

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #0d47a1;">범위:</strong> 사람과 컴퓨터 시스템 간의 상호작용 전반</li>
        <li><strong style="color: #0d47a1;">초점:</strong> 사용성, 접근성, 사용자 경험 최적화</li>
        <li><strong style="color: #0d47a1;">환경:</strong> 일반적인 컴퓨팅 환경 (오피스, 모바일, 웹)</li>
        <li><strong style="color: #0d47a1;">사용자:</strong> 다양한 배경과 숙련도의 일반 사용자</li>
    </ul>
</div>

### 🏭 Human Machine Interface (HMI)

<div style="background: #f3e5f5; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #9c27b0; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #4a148c;">범위:</strong> 사람과 산업 기계/시스템 간의 직접적 제어 인터페이스</li>
        <li><strong style="color: #4a148c;">초점:</strong> 안전성, 정확성, 효율성, 신뢰성</li>
        <li><strong style="color: #4a148c;">환경:</strong> 산업 현장 (제조, 공정, 자동화)</li>
        <li><strong style="color: #4a148c;">사용자:</strong> 전문 운영자, 기술자, 엔지니어</li>
    </ul>
</div>

</div>

---

## 반도체 제조 환경의 특수성

<div style="margin: 2rem 0;">

### 🏗️ 물리적 환경 제약사항

<div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #f39c12; margin: 1.5rem 0;">
    <p style="margin: 0; color: #856404; font-weight: 500; font-size: 1.1em;">
        ⚠️ 클린룸 환경에서는 특수한 복장과 장비로 인해 조작성이 제한되며, 정밀한 공정 제어가 필수적입니다.
    </p>
</div>

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #6c757d; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #495057;">클린룸 Class 1-100:</strong> 먼지 입자 극도 제한, 장갑 착용 필수</li>
        <li><strong style="color: #495057;">진동 최소화:</strong> 나노미터 단위 정밀도 요구</li>
        <li><strong style="color: #495057;">온습도 제어:</strong> ±0.1°C, ±1% RH 정밀 제어</li>
        <li><strong style="color: #495057;">조명 환경:</strong> 황색 조명으로 인한 색상 인식 제한</li>
    </ul>
</div>

### ⚡ 운영 특성

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #dc3545; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #721c24;">24/7 연속 운영:</strong> 장비 가동률 95% 이상 유지</li>
        <li><strong style="color: #721c24;">교대 근무:</strong> 3교대 시스템으로 인한 일관성 요구</li>
        <li><strong style="color: #721c24;">고비용 장비:</strong> 장비당 수십억 원, 다운타임 최소화 필수</li>
        <li><strong style="color: #721c24;">품질 임계성:</strong> 단일 오류로 인한 막대한 손실 가능</li>
    </ul>
</div>

</div>

---

## 인지 부하 이론과 정보 설계

<div style="margin: 2rem 0;">

### 🧠 인지 부하 모델

<div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #155724;">감각 기억:</strong> 0.5-3초, 시각/청각 정보 임시 저장</li>
        <li><strong style="color: #155724;">작업 기억:</strong> 7±2개 항목, 동시 처리 한계</li>
        <li><strong style="color: #155724;">장기 기억:</strong> 패턴 인식과 전문 지식 저장</li>
    </ul>
</div>

### 📊 반도체 공정 정보의 특성

<div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #f39c12; margin: 1.5rem 0;">
    <p style="margin: 0; color: #856404; font-weight: 500; font-size: 1.1em;">
        ⚠️ 반도체 공정에서는 수백 개의 센서 데이터를 실시간으로 모니터링해야 하므로 정보 우선순위화가 필수적입니다.
    </p>
</div>

### 💡 효과적 정보 표현 전략

<div style="display: flex; flex-direction: column; gap: 1rem; margin: 1.5rem 0;">
    <div style="display: flex; align-items: center; background: #e8f5e8; padding: 1rem; border-radius: 8px;">
        <div style="background: #28a745; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">1</div>
        <span style="color: #155724;"><strong>정보 계층화:</strong> 중요도에 따른 시각적 우선순위 설정</span>
    </div>
    <div style="display: flex; align-items: center; background: #e3f2fd; padding: 1rem; border-radius: 8px;">
        <div style="background: #2196f3; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">2</div>
        <span style="color: #0d47a1;"><strong>그룹핑:</strong> 관련 정보의 공간적 근접성 확보</span>
    </div>
    <div style="display: flex; align-items: center; background: #f3e5f5; padding: 1rem; border-radius: 8px;">
        <div style="background: #9c27b0; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">3</div>
        <span style="color: #4a148c;"><strong>일관성:</strong> 표준화된 색상, 기호, 레이아웃 사용</span>
    </div>
</div>

</div>

---

## 안전 중심 인터페이스 설계

<div style="margin: 2rem 0;">

### 🛡️ 안전성 설계 원칙

<div style="background: #f8d7da; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #dc3545; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #721c24;">Fail-Safe 설계:</strong> 시스템 오류 시 안전한 상태로 복귀</li>
        <li><strong style="color: #721c24;">이중 확인:</strong> 중요한 조작에 대한 확인 단계 추가</li>
        <li><strong style="color: #721c24;">명확한 피드백:</strong> 조작 결과의 즉시적이고 명확한 표시</li>
        <li><strong style="color: #721c24;">오류 방지:</strong> 잘못된 조작을 원천적으로 차단</li>
    </ul>
</div>

### ⚠️ 알람 및 경고 시스템

<div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #f39c12; margin: 1.5rem 0;">
    <p style="margin: 0; color: #856404; font-weight: 500; font-size: 1.1em;">
        💡 알람 우선순위 시스템을 통해 운영자가 가장 중요한 상황에 집중할 수 있도록 설계해야 합니다.
    </p>
</div>

### 🎯 알람 분류 체계

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #6c757d; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #495057;">Critical (빨강):</strong> 즉시 조치 필요, 장비 정지 위험</li>
        <li><strong style="color: #495057;">Warning (주황):</strong> 주의 필요, 성능 저하 가능</li>
        <li><strong style="color: #495057;">Advisory (노랑):</strong> 정보 제공, 예방적 조치 권장</li>
        <li><strong style="color: #495057;">Information (파랑):</strong> 상태 정보, 로깅 목적</li>
    </ul>
</div>

</div>

---

## 반도체 장비 운영자 특성 분석

<div style="margin: 2rem 0;">

### 👥 사용자 그룹 분류

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #0d47a1;">운영자 (Operator):</strong> 일상적인 장비 운전 및 모니터링</li>
        <li><strong style="color: #0d47a1;">기술자 (Technician):</strong> 장비 유지보수 및 문제 해결</li>
        <li><strong style="color: #0d47a1;">엔지니어 (Engineer):</strong> 공정 개선 및 고급 설정</li>
        <li><strong style="color: #0d47a1;">관리자 (Supervisor):</strong> 전체 시스템 감독 및 의사결정</li>
    </ul>
</div>

### 🔧 운영자별 요구사항

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1.5rem 0;">
    <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px;">
        <h4 style="color: #155724; margin: 0 0 0.5rem 0;">운영자</h4>
        <ul style="margin: 0; font-size: 0.9em; line-height: 1.6;">
            <li>직관적인 상태 표시</li>
            <li>간단한 조작 인터페이스</li>
            <li>명확한 알람 메시지</li>
        </ul>
    </div>
    <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px;">
        <h4 style="color: #0d47a1; margin: 0 0 0.5rem 0;">기술자</h4>
        <ul style="margin: 0; font-size: 0.9em; line-height: 1.6;">
            <li>상세한 진단 정보</li>
            <li>히스토리 데이터 접근</li>
            <li>고급 설정 권한</li>
        </ul>
    </div>
</div>

</div>

---

## 표준 및 가이드라인

<div style="margin: 2rem 0;">

### 📋 관련 표준

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #6c757d; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #495057;">SEMI E95:</strong> Human Factors Engineering Guidelines</li>
        <li><strong style="color: #495057;">ISO 9241:</strong> Ergonomics of Human-System Interaction</li>
        <li><strong style="color: #495057;">IEC 62682:</strong> Management of alarm systems for the process industries</li>
        <li><strong style="color: #495057;">ANSI/ISA-101:</strong> Human Machine Interfaces for Process Automation Systems</li>
    </ul>
</div>

### 🎨 시각적 설계 가이드라인

<div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #f39c12; margin: 1.5rem 0;">
    <p style="margin: 0; color: #856404; font-weight: 500; font-size: 1.1em;">
        💡 반도체 환경의 황색 조명을 고려하여 색상 대비와 가독성을 최적화해야 합니다.
    </p>
</div>

</div>

---

# 💻 기초 실습 (45분)

---

## 실습 1: 기존 HMI 사례 분석

<div style="margin: 2rem 0;">

### 🔍 분석 대상 선정

<div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #155724;">Applied Materials:</strong> Centura 시리즈 CVD 장비</li>
        <li><strong style="color: #155724;">ASML:</strong> PAS 5500 리소그래피 시스템</li>
        <li><strong style="color: #155724;">Tokyo Electron:</strong> Formula 시리즈 에칭 장비</li>
        <li><strong style="color: #155724;">KLA-Tencor:</strong> Surfscan 검사 장비</li>
    </ul>
</div>

### 📊 평가 체크리스트

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #6c757d; margin: 1rem 0;">

**정보 구성:**
- [ ] 중요한 정보가 화면 상단/중앙에 배치되어 있는가?
- [ ] 관련 정보들이 그룹화되어 있는가?
- [ ] 정보 밀도가 적절한가?

**시각적 설계:**
- [ ] 색상 사용이 일관적이고 의미가 있는가?
- [ ] 폰트 크기와 대비가 가독성을 보장하는가?
- [ ] 아이콘과 기호가 직관적인가?

**사용성:**
- [ ] 자주 사용하는 기능에 쉽게 접근할 수 있는가?
- [ ] 오류 메시지가 명확하고 해결 방법을 제시하는가?
- [ ] 사용자 권한에 따른 접근 제어가 있는가?

</div>

</div>

---

## 실습 2: 페르소나 개발

<div style="margin: 2rem 0;">

### 👤 주요 페르소나 템플릿

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">

**페르소나 1: 장비 운영자**
- **이름:** 김현수 (32세, 경력 5년)
- **배경:** 전자공학 전문대 졸업, 3교대 근무
- **목표:** 안전하고 효율적인 장비 운영
- **페인 포인트:** 복잡한 알람 메시지, 야간 근무 시 피로
- **기술 수준:** 중급 (기본적인 컴퓨터 활용 가능)

**페르소나 2: 유지보수 기술자**
- **이름:** 이미영 (38세, 경력 10년)
- **배경:** 기계공학 학사, 전문 기술 보유
- **목표:** 신속한 문제 진단 및 해결
- **페인 포인트:** 불충분한 진단 정보, 복잡한 메뉴 구조
- **기술 수준:** 고급 (고급 기능 활용 가능)

</div>

### 📝 시나리오 작성 예시

<div style="background: #f3e5f5; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #9c27b0; margin: 1rem 0;">

**시나리오: 비정상 온도 알람 대응**

1. **상황:** CVD 공정 중 챔버 온도가 설정값을 초과
2. **알람 발생:** 화면에 경고 메시지 표시
3. **운영자 대응:**
   - 알람 내용 확인
   - 관련 센서 데이터 조회
   - 표준 대응 절차 수행
   - 필요시 기술자 호출
4. **결과:** 정상 상태 복구 및 로그 기록

</div>

</div>

---

# 🚀 심화 실습 (45분)

---

## 실습 3: HMI 프로토타입 설계

<div style="margin: 2rem 0;">

### 🎨 와이어프레임 설계 원칙

<div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #155724;">화면 구성:</strong> 3분할 레이아웃 (헤더, 메인, 사이드바)</li>
        <li><strong style="color: #155724;">정보 계층:</strong> 상태 → 제어 → 세부정보 순서</li>
        <li><strong style="color: #155724;">네비게이션:</strong> 브레드크럼과 메뉴 병행</li>
        <li><strong style="color: #155724;">반응형:</strong> 다양한 화면 크기 지원</li>
    </ul>
</div>

### 📐 레이아웃 구조

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #6c757d; margin: 1rem 0;">

```
┌─────────────────────────────────────────────┐
│  헤더: 장비명, 상태, 시간, 알람 요약        │
├─────────────────────────────────────────────┤
│ 사이드바 │        메인 콘텐츠 영역          │
│  메뉴    │                                 │
│  트리    │  ┌─────────────────────────┐     │
│         │  │      상태 대시보드       │     │
│         │  └─────────────────────────┘     │
│         │  ┌─────────────────────────┐     │
│         │  │      제어 패널          │     │
│         │  └─────────────────────────┘     │
└─────────────────────────────────────────────┘
```

</div>

### 🎯 핵심 화면 설계

<div style="display: flex; flex-direction: column; gap: 1rem; margin: 1.5rem 0;">
    <div style="display: flex; align-items: center; background: #e8f5e8; padding: 1rem; border-radius: 8px;">
        <div style="background: #28a745; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">1</div>
        <span style="color: #155724;"><strong>메인 대시보드:</strong> 전체 장비 상태 한눈에 파악</span>
    </div>
    <div style="display: flex; align-items: center; background: #e3f2fd; padding: 1rem; border-radius: 8px;">
        <div style="background: #2196f3; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">2</div>
        <span style="color: #0d47a1;"><strong>공정 모니터링:</strong> 실시간 센서 데이터 시각화</span>
    </div>
    <div style="display: flex; align-items: center; background: #f3e5f5; padding: 1rem; border-radius: 8px;">
        <div style="background: #9c27b0; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">3</div>
        <span style="color: #4a148c;"><strong>알람 관리:</strong> 우선순위별 알람 표시 및 관리</span>
    </div>
    <div style="display: flex; align-items: center; background: #fff3cd; padding: 1rem; border-radius: 8px;">
        <div style="background: #f39c12; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">4</div>
        <span style="color: #856404;"><strong>제어 인터페이스:</strong> 안전한 장비 제어 및 설정</span>
    </div>
</div>

</div>

---

## 실습 4: 사용성 평가 기준 수립

<div style="margin: 2rem 0;">

### 📏 정량적 평가 지표

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #0d47a1;">작업 완료 시간:</strong> 표준 작업 수행 소요 시간</li>
        <li><strong style="color: #0d47a1;">오류 발생률:</strong> 작업 중 실수 빈도</li>
        <li><strong style="color: #0d47a1;">학습 시간:</strong> 신규 사용자 적응 기간</li>
        <li><strong style="color: #0d47a1;">인지 부하:</strong> 정보 처리 복잡도 측정</li>
    </ul>
</div>

### 📝 정성적 평가 기준

<div style="background: #f3e5f5; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #9c27b0; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #4a148c;">직관성:</strong> 설명 없이 사용 가능한 정도</li>
        <li><strong style="color: #4a148c;">일관성:</strong> 전체 시스템에서 동일한 패턴 유지</li>
        <li><strong style="color: #4a148c;">피드백:</strong> 사용자 행동에 대한 명확한 반응</li>
        <li><strong style="color: #4a148c;">예측 가능성:</strong> 결과를 예상할 수 있는 정도</li>
    </ul>
</div>

</div>

---

# 🎯 Hands-on 프로젝트 (45분)

---

## 요구사항 도출 시뮬레이션

<div style="margin: 2rem 0;">

### 🎭 역할 분담

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1.5rem 0;">
    <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px;">
        <h4 style="color: #155724; margin: 0 0 0.5rem 0;">인터뷰어 (설계자)</h4>
        <ul style="margin: 0; font-size: 0.9em; line-height: 1.6;">
            <li>체계적인 질문 수행</li>
            <li>요구사항 문서화</li>
            <li>우선순위 설정</li>
        </ul>
    </div>
    <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px;">
        <h4 style="color: #0d47a1; margin: 0 0 0.5rem 0;">인터뷰이 (운영자)</h4>
        <ul style="margin: 0; font-size: 0.9em; line-height: 1.6;">
            <li>실제 업무 상황 설명</li>
            <li>페인 포인트 공유</li>
            <li>개선 아이디어 제시</li>
        </ul>
    </div>
</div>

### 📋 인터뷰 가이드

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #6c757d; margin: 1rem 0;">

**기본 정보 수집:**
- 담당 장비 및 공정
- 업무 경력 및 교육 배경
- 일상적인 작업 루틴
- 교대 근무 패턴

**현재 시스템 평가:**
- 가장 자주 사용하는 기능
- 어려운 점이나 불편한 점
- 오류나 문제 상황 경험
- 개선 희망 사항

**새로운 요구사항:**
- 추가로 필요한 기능
- 더 나은 정보 표시 방법
- 작업 효율성 향상 아이디어

</div>

</div>

---

## 요구사항 문서 작성

<div style="margin: 2rem 0;">

### 📄 기능 요구사항 템플릿

<div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;">

**FR-001: 실시간 상태 모니터링**
- **설명:** 장비의 주요 파라미터를 실시간으로 표시
- **우선순위:** 높음
- **상세:** 온도, 압력, 유량 등 핵심 지표 1초 간격 업데이트
- **수용 기준:** 데이터 지연 시간 < 500ms

**FR-002: 알람 관리 시스템**
- **설명:** 중요도별 알람 분류 및 표시
- **우선순위:** 높음
- **상세:** Critical, Warning, Advisory 3단계 분류
- **수용 기준:** 알람 발생 후 3초 이내 표시

</div>

### 📊 비기능 요구사항

<div style="background: #f3e5f5; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #9c27b0; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #4a148c;">성능:</strong> 화면 전환 시간 < 2초</li>
        <li><strong style="color: #4a148c;">가용성:</strong> 99.9% 이상 (월 43분 이하 다운타임)</li>
        <li><strong style="color: #4a148c;">보안:</strong> 역할 기반 접근 제어</li>
        <li><strong style="color: #4a148c;">사용성:</strong> 신규 사용자 1시간 이내 기본 기능 숙달</li>
    </ul>
</div>

</div>

---

## 📝 학습 정리 및 다음 단계

<div style="margin: 2rem 0;">

### ✅ 오늘 학습한 핵심 내용

<div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #155724;">HCI vs HMI:</strong> 개념적 차이와 반도체 환경에서의 특수성</li>
        <li><strong style="color: #155724;">인지 부하:</strong> 정보 처리 한계를 고려한 인터페이스 설계</li>
        <li><strong style="color: #155724;">안전 설계:</strong> 오류 방지와 명확한 피드백의 중요성</li>
        <li><strong style="color: #155724;">사용자 중심:</strong> 페르소나와 시나리오 기반 설계 접근법</li>
    </ul>
</div>

### 🚀 다음 주차 예고: C# WPF 기초

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #0d47a1;">이론:</strong> .NET Framework와 WPF 아키텍처</li>
        <li><strong style="color: #0d47a1;">실습:</strong> MVVM 패턴을 활용한 기본 HMI 구현</li>
        <li><strong style="color: #0d47a1;">프로젝트:</strong> 반도체 장비 모니터링 창 개발 시작</li>
    </ul>
</div>

### 📚 사전 준비 사항

<div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #f39c12; margin: 1.5rem 0;">
    <p style="margin: 0; color: #856404; font-weight: 500; font-size: 1.1em;">
        💡 다음 주까지 Visual Studio 2022 설치 및 .NET 6.0 SDK 준비해 주세요.
    </p>
</div>

</div>

---

## ❓ 질의응답

<div style="margin: 2rem 0;">

<div style="background: #f8f9fa; padding: 2rem; border-radius: 8px; text-align: center; border: 2px dashed #6c757d;">
    <h3 style="color: #495057; margin: 0 0 1rem 0;">💬 질문해 주세요!</h3>
    <p style="margin: 0; color: #6c757d; font-style: italic;">
        HCI/HMI 이론이나 반도체 환경 특성에 대해<br>
        궁금한 점이 있으시면 언제든지 질문해 주세요.
    </p>
</div>

</div>