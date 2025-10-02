# HMI Course Content Technical Specification

> **버전**: 1.0.0
> **최종 업데이트**: 2025년 10월 2일
> **문서 유형**: HMI 강의 콘텐츠 기술 명세서

## 📖 문서 개요

이 문서는 HMI 강의 프로젝트의 콘텐츠 구조, 파일 형식, 메타데이터 스키마, 품질 기준을 정의합니다. 범용 프레젠테이션 시스템 내에서 HMI 강의 콘텐츠의 일관성과 상호 운용성을 보장하기 위한 기술적 요구사항을 포함합니다.

## 🗂️ HMI 프로젝트 파일 구조

### 프로젝트 루트 구조
```
slides/course-hmi/
├── project.json                    # 프로젝트 메타데이터 (필수)
├── README.md                       # 프로젝트 개요 (권장)
├── week01-hci-hmi-theory/         # 주차별 폴더
│   ├── slides.md                  # 메인 슬라이드 (필수)
│   ├── summary.md                 # 주차 요약 (필수)
│   ├── slides-01-intro.md         # 세분화된 슬라이드 (선택)
│   ├── slides-02-principles.md
│   └── resources/                 # 리소스 폴더 (선택)
│       ├── images/                # 이미지 파일
│       │   ├── hci-principles.png
│       │   └── interface-examples.jpg
│       ├── code/                  # 코드 예제
│       │   ├── examples/
│       │   └── exercises/
│       ├── data/                  # 데이터 파일
│       │   └── sample-datasets/
│       └── references/            # 참고 자료
│           ├── papers/
│           └── documentation/
├── week02-csharp-wpf-basics/
├── ...
└── assets/                        # 공통 에셋 (선택)
    ├── themes/                    # 프로젝트별 테마
    ├── templates/                 # 템플릿 파일
    └── shared-resources/          # 공유 리소스
```

### 파일 명명 규칙

#### 폴더 명명
- **형식**: `week[NN]-[topic-description]`
- **예시**: `week01-hci-hmi-theory`, `week05-csharp-test-deploy`
- **규칙**:
  - 소문자 영문 + 하이픈 조합
  - 순차적 번호 (01-13)
  - 명확한 주제 설명

#### 파일 명명
- **필수 파일**:
  - `slides.md`: 메인 슬라이드
  - `summary.md`: 주차 요약 및 메타데이터
- **선택 파일**:
  - `slides-[NN]-[description].md`: 세분화된 슬라이드
  - `exercises.md`: 실습 문제 모음
  - `solutions.md`: 해답 및 해설

## 📋 메타데이터 스키마

### project.json 스키마
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^course-hmi$",
      "description": "프로젝트 고유 식별자"
    },
    "title": {
      "type": "string",
      "minLength": 10,
      "maxLength": 100,
      "description": "프로젝트 제목"
    },
    "description": {
      "type": "string",
      "minLength": 50,
      "maxLength": 500,
      "description": "프로젝트 상세 설명"
    },
    "type": {
      "type": "string",
      "enum": ["course"],
      "description": "콘텐츠 유형"
    },
    "category": {
      "type": "string",
      "enum": ["engineering", "computer-science"],
      "description": "학문 분야"
    },
    "duration": {
      "type": "string",
      "pattern": "^[1-9][0-9]* weeks?$",
      "description": "과정 기간"
    },
    "level": {
      "type": "string",
      "enum": ["beginner", "intermediate", "advanced"],
      "description": "난이도"
    },
    "prerequisites": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1,
      "description": "선수 조건"
    },
    "learning_outcomes": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 3,
      "maxItems": 10,
      "description": "학습 성과"
    },
    "technology_stack": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1,
      "description": "사용 기술"
    },
    "author": {
      "type": "object",
      "properties": {
        "name": {"type": "string", "minLength": 2},
        "email": {"type": "string", "format": "email"},
        "affiliation": {"type": "string"}
      },
      "required": ["name", "email"]
    },
    "created": {
      "type": "string",
      "format": "date",
      "description": "생성일 (YYYY-MM-DD)"
    },
    "updated": {
      "type": "string",
      "format": "date",
      "description": "최종 수정일 (YYYY-MM-DD)"
    },
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
      "description": "버전 (Semantic Versioning)"
    }
  },
  "required": [
    "id", "title", "description", "type", "category",
    "duration", "level", "prerequisites", "learning_outcomes",
    "technology_stack", "author", "created", "updated", "version"
  ]
}
```

### summary.md 메타데이터 구조
```yaml
---
week: 1
title: "HCI/HMI 이론 및 기초 개념"
description: "인간-기계 상호작용의 기본 원리와 HMI 설계 원칙 학습"
duration: 150  # 분 단위
difficulty: 2  # 1-5 스케일
tech_focus:
  - "HCI Theory"
  - "User Experience"
  - "Interface Design"
learning_objectives:
  - "HCI/HMI 기본 개념 이해"
  - "사용자 중심 설계 원칙 습득"
  - "인터페이스 평가 방법 학습"
prerequisites:
  - "기본적인 컴퓨터 사용 능력"
  - "소프트웨어 UI 사용 경험"
resources:
  code_examples: false
  datasets: false
  external_tools: []
assessment:
  type: "quiz_and_discussion"
  weight: 5  # 전체 과정에서의 비중 (%)
tags:
  - "theory"
  - "fundamentals"
  - "design-principles"
---
```

## 🎯 콘텐츠 품질 기준

### 교육적 품질 메트릭

#### 학습 목표 명확성
- **SMART 기준**: Specific, Measurable, Achievable, Relevant, Time-bound
- **검증 방법**: 목표 달성 측정 가능 여부 확인
- **최소 요구사항**: 주차당 3-5개의 구체적 목표

#### 내용 구조화
```markdown
# 표준 슬라이드 구조
1. 도입 (10% - 학습 목표, 개요)
2. 이론 설명 (30% - 핵심 개념)
3. 실습 진행 (50% - 단계별 실습)
4. 정리 및 평가 (10% - 요약, 다음 단계)
```

#### 상호작용성
- **질문-응답 구조**: 슬라이드당 최소 1개의 상호작용 요소
- **실습 활동**: 이론 30% + 실습 70% 비율 유지
- **피드백 루프**: 즉시 확인 가능한 결과 제공

### 기술적 품질 기준

#### 코드 품질
```csharp
// ✅ 좋은 예제: 명확한 주석과 구조
/// <summary>
/// 사용자 입력을 처리하는 이벤트 핸들러
/// </summary>
/// <param name="sender">이벤트 발생 객체</param>
/// <param name="e">이벤트 인수</param>
private void OnButtonClick(object sender, RoutedEventArgs e)
{
    // 입력 검증
    if (string.IsNullOrEmpty(InputTextBox.Text))
    {
        MessageBox.Show("입력값이 필요합니다.");
        return;
    }

    // 처리 로직
    ProcessUserInput(InputTextBox.Text);
}
```

#### 코드 예제 기준
- **완전성**: 실행 가능한 완전한 코드
- **주석 비율**: 코드 대비 20-30% 수준의 설명 주석
- **오류 처리**: 예외 상황 처리 코드 포함
- **성능**: 효율적인 알고리즘 및 자료구조 사용

#### 멀티미디어 기준
```yaml
이미지:
  - 포맷: PNG (스크린샷), SVG (다이어그램), JPG (사진)
  - 해상도: 최소 1920x1080 기준
  - 압축: 품질 손실 최소화
  - 대체텍스트: 모든 이미지에 alt 태그 필수

비디오 (해당시):
  - 포맷: MP4 (H.264)
  - 해상도: 1920x1080, 30fps
  - 길이: 5분 이내 권장
  - 자막: 선택사항

오디오 (해당시):
  - 포맷: MP3 또는 WAV
  - 품질: 44.1kHz, 16-bit 이상
  - 볼륨: 정규화된 레벨
```

## 🔧 HMI 특화 요구사항

### 기술 스택별 표준

#### C# WPF 섹션 (Week 2-5)
```xml
<!-- XAML 코드 표준 -->
<Window x:Class="HMIExample.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="HMI Example" Height="600" Width="800">
    <Grid>
        <!-- 명확한 레이아웃 구조 -->
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <!-- 콘텐츠 영역 -->
    </Grid>
</Window>
```

```csharp
// C# 코드 스타일 가이드
namespace HMIExample
{
    /// <summary>
    /// HMI 메인 윈도우 클래스
    /// </summary>
    public partial class MainWindow : Window
    {
        #region 필드
        private readonly DataService _dataService;
        #endregion

        #region 생성자
        public MainWindow()
        {
            InitializeComponent();
            _dataService = new DataService();
        }
        #endregion

        #region 이벤트 핸들러
        private void OnDataReceived(object sender, DataEventArgs e)
        {
            // UI 스레드에서 안전한 업데이트
            Dispatcher.Invoke(() => {
                DataDisplay.Text = e.Data.ToString();
            });
        }
        #endregion
    }
}
```

#### Python PySide6 섹션 (Week 6-9)
```python
# Python 코드 스타일 가이드 (PEP 8 준수)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QWidget, QPushButton, QLabel
)
from PySide6.QtCore import QTimer, Signal
import sys
from typing import Optional


class HMIMainWindow(QMainWindow):
    """HMI 메인 윈도우 클래스

    실시간 데이터 표시 및 사용자 인터랙션을 담당하는
    메인 윈도우 구현
    """

    # 시그널 정의
    data_updated = Signal(str)

    def __init__(self) -> None:
        """생성자: UI 초기화 및 타이머 설정"""
        super().__init__()
        self._setup_ui()
        self._setup_timer()

    def _setup_ui(self) -> None:
        """UI 컴포넌트 초기화"""
        self.setWindowTitle("HMI Example")
        self.setGeometry(100, 100, 800, 600)

        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 레이아웃 구성
        layout = QVBoxLayout(central_widget)

        # 라벨 추가
        self.data_label = QLabel("Data: N/A")
        layout.addWidget(self.data_label)

        # 버튼 추가
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._on_refresh_clicked)
        layout.addWidget(self.refresh_button)

    def _setup_timer(self) -> None:
        """데이터 업데이트 타이머 설정"""
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_data)
        self.timer.start(1000)  # 1초마다 업데이트

    def _on_refresh_clicked(self) -> None:
        """새로고침 버튼 클릭 핸들러"""
        self._update_data()

    def _update_data(self) -> None:
        """데이터 업데이트 메서드"""
        # 실제 데이터 가져오기 로직
        new_data = self._fetch_data()
        self.data_label.setText(f"Data: {new_data}")
        self.data_updated.emit(new_data)

    def _fetch_data(self) -> str:
        """데이터 가져오기 (플레이스홀더)"""
        import random
        return f"{random.randint(1, 100)}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HMIMainWindow()
    window.show()
    sys.exit(app.exec())
```

#### ImGui 섹션 (Week 10-13)
```cpp
// C++ ImGui 코드 스타일 가이드
#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include <vector>
#include <memory>

class HMIApplication
{
private:
    GLFWwindow* m_window;
    std::vector<float> m_data_points;
    bool m_show_demo_window;
    float m_sensor_value;

public:
    HMIApplication()
        : m_window(nullptr)
        , m_show_demo_window(false)
        , m_sensor_value(0.0f)
    {
        m_data_points.reserve(100);
    }

    bool Initialize()
    {
        // GLFW 초기화
        if (!glfwInit()) {
            std::cerr << "GLFW 초기화 실패" << std::endl;
            return false;
        }

        // 윈도우 생성
        m_window = glfwCreateWindow(1280, 720, "HMI ImGui Example", nullptr, nullptr);
        if (!m_window) {
            std::cerr << "윈도우 생성 실패" << std::endl;
            glfwTerminate();
            return false;
        }

        glfwMakeContextCurrent(m_window);
        glfwSwapInterval(1); // V-Sync 활성화

        // ImGui 초기화
        IMGUI_CHECKVERSION();
        ImGui::CreateContext();
        ImGuiIO& io = ImGui::GetIO();
        io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;

        // 스타일 설정
        ImGui::StyleColorsDark();

        // 플랫폼/렌더러 바인딩
        ImGui_ImplGlfw_InitForOpenGL(m_window, true);
        ImGui_ImplOpenGL3_Init("#version 130");

        return true;
    }

    void Run()
    {
        while (!glfwWindowShouldClose(m_window)) {
            glfwPollEvents();

            // ImGui 프레임 시작
            ImGui_ImplOpenGL3_NewFrame();
            ImGui_ImplGlfw_NewFrame();
            ImGui::NewFrame();

            // UI 렌더링
            RenderUI();

            // 렌더링
            ImGui::Render();
            int display_w, display_h;
            glfwGetFramebufferSize(m_window, &display_w, &display_h);
            glViewport(0, 0, display_w, display_h);
            glClearColor(0.45f, 0.55f, 0.60f, 1.00f);
            glClear(GL_COLOR_BUFFER_BIT);
            ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

            glfwSwapBuffers(m_window);
        }
    }

private:
    void RenderUI()
    {
        // 메인 제어 패널
        ImGui::Begin("HMI Control Panel");

        // 센서 값 표시
        ImGui::Text("Sensor Value: %.2f", m_sensor_value);
        ImGui::SliderFloat("Adjust", &m_sensor_value, 0.0f, 100.0f);

        // 데이터 그래프
        if (ImGui::CollapsingHeader("Data Visualization")) {
            UpdateDataPoints();

            if (!m_data_points.empty()) {
                ImGui::PlotLines("Sensor Data",
                    m_data_points.data(),
                    static_cast<int>(m_data_points.size()),
                    0, nullptr, 0.0f, 100.0f,
                    ImVec2(0, 80));
            }
        }

        // 설정 옵션
        ImGui::Checkbox("Show Demo Window", &m_show_demo_window);

        ImGui::End();

        // 데모 윈도우 (필요시)
        if (m_show_demo_window) {
            ImGui::ShowDemoWindow(&m_show_demo_window);
        }
    }

    void UpdateDataPoints()
    {
        // 새 데이터 포인트 추가
        m_data_points.push_back(m_sensor_value);

        // 최대 100개 포인트 유지
        if (m_data_points.size() > 100) {
            m_data_points.erase(m_data_points.begin());
        }
    }
};
```

## 📊 품질 보증 및 검증

### 자동화된 검증 도구

#### 콘텐츠 검증 스크립트
```python
#!/usr/bin/env python3
"""
HMI 강의 콘텐츠 품질 검증 도구
"""
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any
import yaml


class HMIContentValidator:
    """HMI 콘텐츠 유효성 검사기"""

    def __init__(self, course_path: Path):
        self.course_path = Path(course_path)
        self.errors = []
        self.warnings = []

    def validate_project_structure(self) -> bool:
        """프로젝트 구조 검증"""
        required_files = ['project.json']
        required_dirs = []

        for file in required_files:
            if not (self.course_path / file).exists():
                self.errors.append(f"필수 파일 누락: {file}")

        # 주차별 폴더 검증
        week_pattern = re.compile(r'^week\d{2}-[a-z0-9\-]+$')
        week_dirs = [d for d in self.course_path.iterdir()
                     if d.is_dir() and week_pattern.match(d.name)]

        if len(week_dirs) != 13:
            self.warnings.append(f"주차 폴더 수 불일치: {len(week_dirs)}/13")

        return len(self.errors) == 0

    def validate_metadata(self) -> bool:
        """메타데이터 검증"""
        project_json = self.course_path / 'project.json'

        if not project_json.exists():
            self.errors.append("project.json 파일이 없습니다")
            return False

        try:
            with open(project_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 필수 필드 검증
            required_fields = [
                'id', 'title', 'description', 'type', 'category',
                'duration', 'level', 'prerequisites', 'learning_outcomes',
                'technology_stack', 'author', 'created', 'updated', 'version'
            ]

            for field in required_fields:
                if field not in data:
                    self.errors.append(f"project.json에 필수 필드 누락: {field}")

            # 값 검증
            if data.get('id') != 'course-hmi':
                self.errors.append("project.json의 id는 'course-hmi'여야 합니다")

            if data.get('type') != 'course':
                self.errors.append("project.json의 type은 'course'여야 합니다")

        except json.JSONDecodeError as e:
            self.errors.append(f"project.json 파싱 오류: {e}")
            return False

        return len(self.errors) == 0

    def validate_week_content(self, week_dir: Path) -> bool:
        """주차별 콘텐츠 검증"""
        required_files = ['slides.md', 'summary.md']

        for file in required_files:
            file_path = week_dir / file
            if not file_path.exists():
                self.errors.append(f"{week_dir.name}: 필수 파일 누락 - {file}")
                continue

            # 파일 내용 검증
            if file == 'slides.md':
                self._validate_slides_content(file_path)
            elif file == 'summary.md':
                self._validate_summary_content(file_path)

        return True

    def _validate_slides_content(self, slides_path: Path) -> None:
        """슬라이드 콘텐츠 검증"""
        with open(slides_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 빈 슬라이드 검사
        if content.endswith('\n---\n') or content.endswith('---'):
            self.errors.append(f"{slides_path}: 파일 끝에 '---' 있음 (빈 슬라이드 생성)")

        # 제목 구조 검사
        h1_count = len(re.findall(r'^# ', content, re.MULTILINE))
        if h1_count == 0:
            self.warnings.append(f"{slides_path}: H1 제목이 없습니다")
        elif h1_count > 1:
            self.warnings.append(f"{slides_path}: H1 제목이 여러 개입니다")

        # 코드 블록 검사
        code_blocks = re.findall(r'```(\w+)(?:\s+\[(\d+-\d+)\])?\n', content)
        for lang, line_range in code_blocks:
            if lang in ['csharp', 'python', 'cpp'] and not line_range:
                self.warnings.append(f"{slides_path}: {lang} 코드 블록에 라인 번호 없음")

    def _validate_summary_content(self, summary_path: Path) -> None:
        """요약 파일 검증"""
        with open(summary_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # YAML 프론트매터 검사
        if content.startswith('---\n'):
            try:
                yaml_end = content.find('\n---\n', 4)
                if yaml_end > 0:
                    yaml_content = content[4:yaml_end]
                    metadata = yaml.safe_load(yaml_content)

                    # 필수 메타데이터 필드 검증
                    required_fields = ['week', 'title', 'description', 'duration']
                    for field in required_fields:
                        if field not in metadata:
                            self.warnings.append(f"{summary_path}: 메타데이터 필드 누락 - {field}")
            except yaml.YAMLError:
                self.warnings.append(f"{summary_path}: YAML 메타데이터 파싱 오류")
        else:
            self.warnings.append(f"{summary_path}: YAML 메타데이터가 없습니다")

    def run_validation(self) -> Dict[str, Any]:
        """전체 검증 실행"""
        self.errors.clear()
        self.warnings.clear()

        # 1. 프로젝트 구조 검증
        self.validate_project_structure()

        # 2. 메타데이터 검증
        self.validate_metadata()

        # 3. 주차별 콘텐츠 검증
        week_pattern = re.compile(r'^week\d{2}-')
        for week_dir in self.course_path.iterdir():
            if week_dir.is_dir() and week_pattern.match(week_dir.name):
                self.validate_week_content(week_dir)

        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'total_issues': len(self.errors) + len(self.warnings)
        }


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='HMI 강의 콘텐츠 검증')
    parser.add_argument('course_path', help='course-hmi 폴더 경로')
    parser.add_argument('--strict', action='store_true', help='경고도 오류로 처리')

    args = parser.parse_args()

    validator = HMIContentValidator(args.course_path)
    result = validator.run_validation()

    print(f"검증 결과: {'통과' if result['valid'] else '실패'}")
    print(f"총 이슈: {result['total_issues']}개")

    if result['errors']:
        print("\n오류:")
        for error in result['errors']:
            print(f"  ❌ {error}")

    if result['warnings']:
        print("\n경고:")
        for warning in result['warnings']:
            print(f"  ⚠️  {warning}")

    # 종료 코드 설정
    if result['errors'] or (args.strict and result['warnings']):
        exit(1)
    else:
        exit(0)


if __name__ == '__main__':
    main()
```

### 품질 체크리스트

#### 주차별 콘텐츠 체크리스트
- [ ] **구조 완성도**
  - [ ] slides.md 파일 존재
  - [ ] summary.md 파일 존재 및 메타데이터 완성
  - [ ] 필요한 리소스 파일 준비 완료
- [ ] **교육적 품질**
  - [ ] 명확한 학습 목표 3-5개
  - [ ] 논리적 내용 구성 (도입→이론→실습→정리)
  - [ ] 적절한 시간 배분 (이론 30% + 실습 70%)
- [ ] **기술적 품질**
  - [ ] 모든 코드 예제 동작 확인
  - [ ] 오류 처리 및 예외 상황 고려
  - [ ] 주석 및 설명 충분성
- [ ] **시각적 품질**
  - [ ] 슬라이드 가독성 (한 화면에 표시)
  - [ ] 이미지 해상도 및 대체 텍스트
  - [ ] 일관된 디자인 및 레이아웃

## 🔄 버전 관리 및 배포

### 콘텐츠 버전 관리
- **Semantic Versioning**: MAJOR.MINOR.PATCH
  - **MAJOR**: 커리큘럼 구조 변경
  - **MINOR**: 새로운 주차 또는 주요 기능 추가
  - **PATCH**: 오류 수정, 콘텐츠 개선

### 배포 프로세스
1. **개발**: 로컬 환경에서 콘텐츠 작성
2. **검증**: 자동화 도구를 통한 품질 검사
3. **리뷰**: 동료 검토 및 피드백 반영
4. **테스트**: 실제 강의 환경에서 시연
5. **배포**: 프로덕션 환경 업데이트

---

📧 **기술 지원**: HMI 강의 콘텐츠 기술 명세에 대한 문의는 개발팀에 연락해 주세요.

🔄 **업데이트**: 이 명세서는 시스템 발전과 함께 지속적으로 개선됩니다.

⚙️ **목표**: 일관되고 고품질의 HMI 교육 콘텐츠 제공을 위한 기술적 기반 구축