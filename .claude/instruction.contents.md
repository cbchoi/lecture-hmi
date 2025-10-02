# HMI Course Content Management - User Instructions

> **버전**: 1.0.0
> **최종 업데이트**: 2025년 10월 2일
> **콘텐츠 유형**: HMI(Human-Machine Interface) 강의 전용 가이드

## 📖 문서 개요

이 문서는 HMI 강의 콘텐츠 제작자와 강사를 위한 전용 가이드입니다. 범용 프레젠테이션 시스템 내에서 HMI 강의 프로젝트(`course-hmi`)를 효과적으로 관리하고 운영하는 방법을 제공합니다.

## 🎯 HMI 강의 과정 개요

### 강의 목표
- **HCI/HMI 이론 이해**: 인간-기계 상호작용의 기본 원리 학습
- **실무 기술 습득**: C# WPF, Python PySide6, ImGui 프레임워크 실습
- **프로젝트 기반 학습**: 실제 애플리케이션 개발 경험
- **산업 표준 적용**: 현업에서 사용되는 도구와 방법론 습득

### 13주차 커리큘럼 구성

#### Phase 1: 기초 이론 (Week 1-2)
- **Week 01**: HCI/HMI 이론 및 기초 개념
- **Week 02**: C# WPF 기초 및 기본 컴포넌트

#### Phase 2: C# WPF 심화 (Week 3-5)
- **Week 03**: C# 실시간 데이터 처리
- **Week 04**: C# 고급 UI 기법
- **Week 05**: C# 테스트 및 배포

#### Phase 3: Python PySide6 (Week 6-9)
- **Week 06**: Python PySide6 기초
- **Week 07**: Python 실시간 데이터 처리
- **Week 08**: Python 고급 기능
- **Week 09**: Python 배포 및 패키징

#### Phase 4: ImGui 및 통합 (Week 10-13)
- **Week 10**: ImGui 기초
- **Week 11**: ImGui 고급 기능
- **Week 12**: ImGui 고급 기법 및 최적화
- **Week 13**: ImGui 통합 프로젝트

## 📁 HMI 프로젝트 구조

### 디렉토리 구조
```
slides/course-hmi/
├── project.json                    # 프로젝트 메타데이터
├── week01-hci-hmi-theory/         # 1주차: 이론
│   ├── slides.md                  # 강의 슬라이드
│   ├── summary.md                 # 주차 요약
│   ├── slides-01-intro.md         # 세부 슬라이드 (필요시)
│   ├── slides-02-principles.md
│   └── resources/                 # 리소스 폴더
│       ├── images/
│       └── references/
├── week02-csharp-wpf-basics/      # 2주차: C# WPF 기초
│   ├── slides.md
│   ├── summary.md
│   └── resources/
│       ├── code/                  # 코드 예제
│       │   ├── BasicWPF/
│       │   └── Examples/
│       └── images/
├── week03-csharp-realtime-data/   # 3주차: 실시간 데이터
├── ...
└── week13-imgui-integrated-project/
```

### project.json 템플릿
```json
{
  "id": "course-hmi",
  "title": "Human-Machine Interface 프로그래밍",
  "description": "HCI/HMI 이론부터 실무까지 체계적으로 학습하는 13주차 과정",
  "type": "course",
  "category": "engineering",
  "duration": "13 weeks",
  "level": "intermediate",
  "prerequisites": [
    "기본적인 프로그래밍 경험",
    "객체지향 프로그래밍 이해",
    "개발 환경 설정 경험"
  ],
  "learning_outcomes": [
    "HCI/HMI 설계 원칙 이해",
    "C# WPF 애플리케이션 개발",
    "Python PySide6 GUI 프로그래밍",
    "ImGui 실시간 인터페이스 구현",
    "크로스 플랫폼 GUI 개발 역량"
  ],
  "technology_stack": [
    "C# WPF",
    "Python PySide6",
    "C++ ImGui",
    "Visual Studio",
    "PyCharm/VS Code"
  ],
  "author": {
    "name": "강의자명",
    "email": "instructor@example.com",
    "affiliation": "소속 기관"
  },
  "created": "2025-03-01",
  "updated": "2025-10-02",
  "version": "1.0.0"
}
```

## 📝 주차별 콘텐츠 작성 가이드

### summary.md 표준 템플릿
```markdown
# Week XX: [주제 제목]

## 🎯 학습 목표
- 구체적이고 측정 가능한 목표 1
- 구체적이고 측정 가능한 목표 2
- 구체적이고 측정 가능한 목표 3

## 📚 주요 내용
### 이론 파트 (30분)
- 핵심 개념 1
- 핵심 개념 2
- 핵심 개념 3

### 실습 파트 (90분)
- 실습 1: 기본 구현
- 실습 2: 심화 응용
- 실습 3: 문제 해결

### 프로젝트 파트 (선택, 30분)
- 개인 프로젝트 진행
- 팀 프로젝트 진행

## ⏰ 시간 배분
- **이론 강의**: 30분
- **실습 진행**: 90분
- **질의응답**: 15분
- **개별 지도**: 15분
- **총 소요시간**: 150분 (2.5시간)

## 👥 대상 및 준비사항
### 대상 학습자
- **수준**: 중급 (프로그래밍 기초 지식 보유)
- **사전 지식**: [구체적인 선수 지식]
- **도구 경험**: [필요한 도구 사용 경험]

### 사전 준비사항
- [ ] 개발 환경 설정 확인
- [ ] 선수 학습 내용 복습
- [ ] 실습 자료 다운로드
- [ ] 프로젝트 환경 준비

## 💻 개발 환경 및 도구
### 필수 소프트웨어
- **Windows**: Visual Studio 2022, Python 3.9+
- **macOS**: VS Code, Python 3.9+, Mono
- **Linux**: VS Code, Python 3.9+, Mono

### 추천 도구
- Git (버전 관리)
- Postman (API 테스트, 해당시)
- 디자인 도구 (Figma, Sketch 등)

## 📖 참고 자료
### 필수 읽기 자료
- [공식 문서 링크]
- [교재 해당 챕터]

### 추가 학습 자료
- [동영상 튜토리얼]
- [블로그 포스트]
- [GitHub 예제]

### 관련 논문 (고급)
- [학술 논문 1]
- [연구 자료 2]

## 🔗 연관 주차
- **선수 주차**: Week XX (관련 내용)
- **후속 주차**: Week XX (발전 내용)
- **병행 학습**: 개인 프로젝트 진행

## 📋 평가 및 과제
### 주차 평가
- **실습 완료도**: 70%
- **개념 이해도**: 20%
- **질문 및 참여**: 10%

### 과제
- **과제 1**: [과제명 및 설명]
- **제출 기한**: 다음 주차 시작 전
- **평가 기준**: [구체적인 루브릭]

## ⚠️ 주의사항 및 팁
### 일반적인 문제
- **문제 1**: [문제 설명] → [해결책]
- **문제 2**: [문제 설명] → [해결책]

### 성공 팁
- **팁 1**: [구체적인 조언]
- **팁 2**: [실습 관련 팁]

### 추가 도전 과제
- **심화 과제**: [고급 학습자를 위한 추가 과제]
```

## 🎨 슬라이드 작성 가이드라인

### slides.md 구조 템플릿
```markdown
---
title: "Week XX: 주제 제목"
theme: academic
transition: slide
---

# Week XX: 주제 제목
> HMI Programming Course
> 부제목 또는 한 줄 설명

---

## 📋 오늘의 목표

:::: {.columns}
::: {.column width="50%"}
### 이론 목표
- 핵심 개념 이해
- 원리 파악
:::

::: {.column width="50%"}
### 실습 목표
- 실제 구현 경험
- 문제 해결 능력
:::
::::

---

## 🗺️ 진행 순서

1. **이론 파트** (30분)
   - 개념 소개
   - 원리 설명

2. **실습 파트** (90분)
   - 단계별 실습
   - 응용 과제

3. **정리 및 Q&A** (30분)

---

# 📖 이론 파트

---

## 핵심 개념 1

### 정의
[개념에 대한 명확한 정의]

### 중요성
- 이유 1
- 이유 2
- 이유 3

---

## 핵심 개념 2

### 예시
```csharp
// C# 코드 예시
public class Example {
    public void Method() {
        // 구현 내용
    }
}
```

---

# 💻 실습 파트

---

## 실습 1: 기본 구현

### 목표
[실습의 구체적인 목표]

### 단계
1. 프로젝트 생성
2. 기본 구조 작성
3. 기능 구현
4. 테스트 및 확인

---

## 코드 실습

```csharp
// 단계별 코드 설명
public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        // 초기화 코드
    }

    private void Button_Click(object sender, RoutedEventArgs e)
    {
        // 이벤트 처리
    }
}
```

---

## 실습 2: 심화 응용

### 도전 과제
[더 복잡한 구현 과제]

### 힌트
- 힌트 1
- 힌트 2

---

# 🔍 문제 해결

---

## 일반적인 오류

### 오류 1: [오류명]
```
Error Message: [에러 메시지]
```

**해결책**:
1. [해결 단계 1]
2. [해결 단계 2]

---

## 디버깅 팁

### Visual Studio에서
- 브레이크포인트 설정
- 변수 값 확인
- 호출 스택 분석

### 로그 활용
```csharp
Debug.WriteLine($"변수 값: {value}");
```

---

# 📝 정리

---

## 오늘 배운 내용

### 핵심 포인트
- 포인트 1
- 포인트 2
- 포인트 3

### 실습 성과
- 구현한 기능 1
- 구현한 기능 2

---

## 다음 주차 예고

### Week XX: [다음 주제]
- 오늘 내용의 확장
- 새로운 개념 도입
- 더 복잡한 프로젝트

### 사전 준비
- [준비 사항 1]
- [준비 사항 2]

---

## ❓ 질의응답

질문해 주세요!

**연락처**:
- Email: instructor@example.com
- Office Hours: 매주 [시간]
- 온라인: [플랫폼]

---

## 📚 과제 안내

### 이번 주 과제
- **과제명**: [구체적인 과제명]
- **제출 기한**: [날짜]
- **제출 방법**: [방법]

### 평가 기준
- 기능 구현: 60%
- 코드 품질: 25%
- 문서화: 15%
```

## 🛠️ 콘텐츠 제작 워크플로우

### 1. 주차 계획 수립
```bash
# 1. 새 주차 폴더 생성
mkdir slides/course-hmi/week##-topic-name

# 2. 기본 파일 생성
cd slides/course-hmi/week##-topic-name
touch slides.md summary.md
mkdir resources/{images,code,data}
```

### 2. 콘텐츠 작성
```bash
# 3. 메타데이터 작성 (summary.md 먼저)
# 4. 슬라이드 구조 설계 (slides.md)
# 5. 리소스 준비 (resources/)
```

### 3. 검토 및 테스트
```bash
# 6. 로컬 미리보기
npm run dev

# 7. 브라우저에서 확인
# http://localhost:5173?project=course-hmi&session=week##

# 8. PDF 생성 테스트
npm run export-pdf -- --project course-hmi --session week##
```

### 4. 품질 검증
- [ ] 학습 목표 명확성
- [ ] 콘텐츠 완성도
- [ ] 코드 동작 확인
- [ ] 슬라이드 가독성
- [ ] 시간 배분 적절성

## 🎯 콘텐츠 품질 기준

### 교육적 품질
- **명확한 학습 목표**: 구체적이고 측정 가능
- **체계적 구성**: 논리적 순서와 단계별 진행
- **실습 중심**: 이론 30% + 실습 70% 비율
- **즉시 피드백**: 실습 결과 확인 가능

### 기술적 품질
- **동작하는 코드**: 모든 예제 코드 검증 완료
- **환경 독립성**: 다양한 개발 환경에서 동작
- **최신 기술**: 현재 산업 표준 반영
- **보안 고려**: 안전한 코딩 관행 적용

### 시각적 품질
- **일관된 디자인**: HMI 강의 전용 테마 적용
- **적절한 폰트 크기**: 강의실 환경 고려
- **색상 대비**: 접근성 기준 준수
- **이미지 품질**: 고해상도 스크린샷 및 다이어그램

## 📊 성과 측정 및 개선

### 학습자 피드백 수집
- **주차별 설문조사**: 난이도, 유용성, 개선점
- **실시간 질문**: 이해도 체크
- **프로젝트 결과**: 최종 구현 품질

### 콘텐츠 개선 사이클
1. **피드백 분석**: 학습자 의견 종합
2. **성과 데이터 검토**: 과제 수행률, 이해도
3. **콘텐츠 업데이트**: 취약 부분 보완
4. **버전 관리**: 개선 이력 추적

---

📧 **콘텐츠 관련 문의**: 이 HMI 강의 콘텐츠에 대한 질문이나 개선 제안은 프로젝트 이슈 트래커를 이용해 주세요.

🔄 **업데이트**: 이 가이드는 강의 진행과 학습자 피드백을 바탕으로 지속적으로 개선됩니다.

🎓 **목표**: 실무 역량을 갖춘 HMI 개발자 양성을 위한 체계적이고 실용적인 교육 과정 제공