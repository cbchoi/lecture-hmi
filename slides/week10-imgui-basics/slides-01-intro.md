# Week 10: ImGui C++ 기초 및 실시간 반도체 HMI 개발

<!-- .slide: data-background-gradient="linear-gradient(45deg, #2d3748, #4a5568)" -->
<div style="text-align: center; color: white; padding: 3rem 2rem;">
    <div style="margin-bottom: 2rem;">
        <h1 style="font-size: 3.5em; margin-bottom: 0.5rem; color: #81c784; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">시스템 프로그래밍</h1>
        <div style="width: 200px; height: 4px; background: linear-gradient(90deg, #81c784, #4fc3f7); margin: 1rem auto;"></div>
    </div>

    <div style="margin-bottom: 3rem;">
        <h2 style="font-size: 2.2em; margin-bottom: 1rem; color: #e2e8f0; font-weight: 300;">Week 10: ImGui C++ 기초</h2>
        <p style="font-size: 1.2em; color: #cbd5e0; font-style: italic;">실시간 반도체 HMI 개발 기초</p>
    </div>

    <div style="border-top: 2px solid rgba(255,255,255,0.3); padding-top: 2rem; margin-top: 3rem;">
        <p style="font-size: 1.1em; color: #a0aec0; margin-bottom: 0.5rem;"><strong>담당교수:</strong> 최창병</p>
        <p style="font-size: 1.1em; color: #a0aec0; margin-bottom: 0.5rem;"><strong>학과:</strong> 컴퓨터공학과</p>
        <p style="font-size: 1.1em; color: #a0aec0;"><strong>날짜:</strong> 2024년 11월</p>
    </div>
</div>

---

<!-- .slide: data-background-color="#2d3748" -->
<div style="text-align: center; color: white; padding: 2rem;">
    <h1 style="font-size: 3em; margin-bottom: 1rem; color: #81c784;">학습 목표</h1>
    <h2 style="font-size: 1.5em; color: #e2e8f0; font-weight: 300;">이번 강의에서 배울 내용</h2>
</div>

---

## 📌 학습 목표

<div style="margin: 2rem 0;">

### 🎯 주요 학습 내용

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #007bff; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #1a365d;">ImGui 기본 개념:</strong> 즉시 모드 GUI의 특징과 장점 이해</li>
        <li><strong style="color: #1a365d;">C++ 아키텍처:</strong> 모던 C++ 기법을 활용한 HMI 설계</li>
        <li><strong style="color: #1a365d;">실시간 처리:</strong> 반도체 장비의 실시간 데이터 시각화</li>
        <li><strong style="color: #1a365d;">실습 프로젝트:</strong> 기본적인 모니터링 시스템 구현</li>
    </ul>
</div>

### 💡 중요 사항

<div style="background: linear-gradient(135deg, #fff3cd, #ffeaa7); padding: 1.5rem; border-radius: 8px; border: 1px solid #f39c12; margin: 1.5rem 0;">
    <p style="margin: 0; color: #856404; font-weight: 500; font-size: 1.1em;">
        ⚠️ ImGui는 즉시 모드 GUI로서 기존 GUI 프레임워크와는 완전히 다른 접근 방식을 사용합니다. 매 프레임마다 UI를 다시 그리는 개념을 확실히 이해하는 것이 중요합니다.
    </p>
</div>

</div>

---

<!-- .slide: data-background-color="#2d3748" -->
<div style="text-align: center; color: white; padding: 2rem;">
    <h1 style="font-size: 3em; margin-bottom: 1rem; color: #81c784;">이론 강의</h1>
    <h2 style="font-size: 1.5em; color: #e2e8f0; font-weight: 300;">ImGui 개념 및 C++ 아키텍처</h2>
</div>

---

## 📌 ImGui (Immediate Mode GUI) 개념

#### 1.1 즉시 모드 vs 유지 모드 GUI
```cpp
/*
즉시 모드 GUI (Immediate Mode):
- 매 프레임마다 UI를 다시 그림
- 상태를 별도로 저장하지 않음
- 코드와 UI가 직접적으로 연결
- 동적인 UI 변경이 용이

유지 모드 GUI (Retained Mode):
- UI 요소들이 메모리에 지속적으로 유지
- 이벤트 기반으로 업데이트
- 복잡한 상태 관리 필요
- 전통적인 GUI 프레임워크 (Qt, WPF 등)
*/

// 즉시 모드 GUI 예제 (ImGUI)
void RenderUI() {
    static float temperature = 25.0f;
    static bool pump_enabled = false;

    // 매 프레임마다 UI 렌더링
    ImGui::Begin("Chamber Control");

    ImGui::SliderFloat("Temperature", &temperature, 0.0f, 1000.0f);
    ImGui::Checkbox("Pump Enabled", &pump_enabled);

    if (ImGui::Button("Start Process")) {
        StartChamberProcess(temperature, pump_enabled);
    }

    ImGui::End();
}

// 유지 모드 GUI 예제 (전통적 방식)
class ChamberControlPanel : public QWidget {
private:
    QSlider* temperature_slider;
    QCheckBox* pump_checkbox;
    QPushButton* start_button;

public:
    ChamberControlPanel() {
        // UI 요소들을 한 번 생성하고 메모리에 유지
        temperature_slider = new QSlider();
        pump_checkbox = new QCheckBox("Pump Enabled");
        start_button = new QPushButton("Start Process");

        // 이벤트 연결
        connect(start_button, &QPushButton::clicked, this, &ChamberControlPanel::OnStartClicked);
    }
};
```

#### 1.2 ImGUI의 장점과 반도체 장비 HMI 적용성
```cpp
/*
ImGUI의 장점:
1. 실시간 성능: 하드웨어 가속 렌더링으로 60FPS+ 보장
2. 메모리 효율성: 상태 저장 최소화로 메모리 사용량 적음
3. 개발 생산성: 직관적인 코드 작성, 빠른 프로토타이핑
4. 크로스 플랫폼: Windows/Linux/macOS 동일 코드베이스
5. 커스터마이징: 완전한 렌더링 제어 가능

반도체 장비 HMI에서의 적용성:
- 실시간 모니터링: 고속 데이터 업데이트 (1ms 단위)
- 복잡한 시각화: 웨이퍼 맵, 3D 챔버 뷰
- 낮은 지연시간: 제어 명령의 즉각적인 반응
- 안정성: 메모리 누수 없는 장기간 운영
- 성능: CPU/GPU 리소스 최적 활용
*/

namespace SemiconductorHMI {

// 실시간 데이터 구조체
struct RealtimeData {
    std::chrono::high_resolution_clock::time_point timestamp;
    float chamber_pressure;      // Torr
    float rf_power;             // Watts
    float gas_flow_rate;        // sccm
    float substrate_temperature; // Celsius
    bool plasma_on;
    std::array<float, 256> spectrum_data; // OES 스펙트럼
};

// ImGUI 기반 실시간 모니터링 시스템
class RealtimeMonitor {
private:
    std::deque<RealtimeData> data_history;
    static constexpr size_t MAX_HISTORY = 10000; // 10초간 1ms 데이터

public:
    void Update(const RealtimeData& data) {
        data_history.push_back(data);
        if (data_history.size() > MAX_HISTORY) {
            data_history.pop_front();
        }
    }

    void Render() {
        ImGui::Begin("Real-time Monitor", nullptr,
                    ImGuiWindowFlags_NoCollapse | ImGuiWindowFlags_AlwaysAutoResize);

        if (!data_history.empty()) {
            const auto& latest = data_history.back();

            // 실시간 값 표시
            ImGui::Text("Chamber Pressure: %.3f Torr", latest.chamber_pressure);
            ImGui::Text("RF Power: %.1f W", latest.rf_power);
            ImGui::Text("Gas Flow: %.1f sccm", latest.gas_flow_rate);
            ImGui::Text("Temperature: %.1f °C", latest.substrate_temperature);

            // 상태 표시
            ImGui::SameLine();
            if (latest.plasma_on) {
                ImGui::TextColored(ImVec4(0, 1, 0, 1), "PLASMA ON");
            } else {
                ImGui::TextColored(ImVec4(1, 0, 0, 1), "PLASMA OFF");
            }
        }

        ImGui::End();
    }
};

} // namespace SemiconductorHMI
```

### 2. ImGUI 아키텍처 및 렌더링 백엔드

#### 2.1 ImGUI 아키텍처 구조
```cpp
/*
ImGUI 아키텍처:
┌─────────────────┐
│   Application   │ ← 사용자 코드 (UI 로직)
├─────────────────┤
│     ImGUI       │ ← 코어 라이브러리 (위젯, 레이아웃)
├─────────────────┤
│    Backend      │ ← 플랫폼/렌더러 추상화
├─────────────────┤
│ OpenGL/DirectX  │ ← 하드웨어 가속 렌더링
└─────────────────┘
*/

// 기본 애플리케이션 구조
class ImGuiApplication {
private:
    GLFWwindow* window;
    ImGuiIO* io;

public:
    bool Initialize() {
        // GLFW 초기화
        if (!glfwInit()) return false;

        // OpenGL 컨텍스트 설정
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 5);
        glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

        // 윈도우 생성
        window = glfwCreateWindow(1920, 1080, "Semiconductor HMI", nullptr, nullptr);
        if (!window) return false;

        glfwMakeContextCurrent(window);
        glfwSwapInterval(1); // VSync 활성화

        // GLAD 초기화 (OpenGL 함수 로딩)
        if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) return false;

        // ImGUI 초기화
        IMGUI_CHECKVERSION();
        ImGui::CreateContext();
        io = &ImGui::GetIO();

        // 설정
        io->ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
        io->ConfigFlags |= ImGuiConfigFlags_DockingEnable;
        io->ConfigFlags |= ImGuiConfigFlags_ViewportsEnable;

        // 스타일 설정
        ImGui::StyleColorsDark();

        // 백엔드 초기화
        ImGui_ImplGlfw_InitForOpenGL(window, true);
        ImGui_ImplOpenGL3_Init("#version 450");

        return true;
    }

    void Run() {
        while (!glfwWindowShouldClose(window)) {
            glfwPollEvents();

            // ImGUI 프레임 시작
            ImGui_ImplOpenGL3_NewFrame();
            ImGui_ImplGlfw_NewFrame();
            ImGui::NewFrame();

            // UI 렌더링
            RenderUI();

            // 렌더링 완료
            ImGui::Render();

            int display_w, display_h;
            glfwGetFramebufferSize(window, &display_w, &display_h);
            glViewport(0, 0, display_w, display_h);
            glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
            glClear(GL_COLOR_BUFFER_BIT);

            ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

            // 멀티 뷰포트 지원
            if (io->ConfigFlags & ImGuiConfigFlags_ViewportsEnable) {
                GLFWwindow* backup_current_context = glfwGetCurrentContext();
                ImGui::UpdatePlatformWindows();
                ImGui::RenderPlatformWindowsDefault();
                glfwMakeContextCurrent(backup_current_context);
            }

            glfwSwapBuffers(window);
        }
    }

    virtual void RenderUI() = 0;

    void Cleanup() {
        ImGui_ImplOpenGL3_Shutdown();
        ImGui_ImplGlfw_Shutdown();
        ImGui::DestroyContext();

        glfwDestroyWindow(window);
        glfwTerminate();
    }
};
```

#### 2.2 CMake 빌드 시스템 구성
```cmake
