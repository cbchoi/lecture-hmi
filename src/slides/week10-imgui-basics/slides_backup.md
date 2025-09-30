# Week 10: ImGUI C++ 기초 및 실시간 반도체 HMI 개발

## 🎯 **이론 강의 (45분) - ImGUI 개념 및 C++ 아키텍처**

### 1. ImGUI (Immediate Mode GUI) 개념

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
# CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(SemiconductorHMI VERSION 1.0.0 LANGUAGES CXX)

# C++ 표준 설정
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 빌드 타입별 컴파일러 플래그
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -O0 -DDEBUG")
else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -DNDEBUG -march=native")
endif()

# 패키지 찾기
find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)
find_package(Threads REQUIRED)

# ImGUI 라이브러리 설정
set(IMGUI_DIR ${CMAKE_CURRENT_SOURCE_DIR}/third_party/imgui)
set(IMGUI_SOURCES
    ${IMGUI_DIR}/imgui.cpp
    ${IMGUI_DIR}/imgui_demo.cpp
    ${IMGUI_DIR}/imgui_draw.cpp
    ${IMGUI_DIR}/imgui_tables.cpp
    ${IMGUI_DIR}/imgui_widgets.cpp
    ${IMGUI_DIR}/backends/imgui_impl_glfw.cpp
    ${IMGUI_DIR}/backends/imgui_impl_opengl3.cpp
)

# GLAD 라이브러리
set(GLAD_DIR ${CMAKE_CURRENT_SOURCE_DIR}/third_party/glad)
set(GLAD_SOURCES
    ${GLAD_DIR}/src/glad.c
)

# 프로젝트 소스 파일
set(PROJECT_SOURCES
    src/main.cpp
    src/application.cpp
    src/hmi_manager.cpp
    src/data_processor.cpp
    src/ui_components.cpp
    src/equipment_interface.cpp
)

# 실행 파일 생성
add_executable(${PROJECT_NAME}
    ${PROJECT_SOURCES}
    ${IMGUI_SOURCES}
    ${GLAD_SOURCES}
)

# 인클루드 디렉토리
target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${IMGUI_DIR}
    ${IMGUI_DIR}/backends
    ${GLAD_DIR}/include
)

# 링킹 라이브러리
target_link_libraries(${PROJECT_NAME}
    OpenGL::GL
    glfw
    Threads::Threads
)

# 컴파일러별 특정 설정
if(MSVC)
    target_compile_definitions(${PROJECT_NAME} PRIVATE _CRT_SECURE_NO_WARNINGS)
    target_compile_options(${PROJECT_NAME} PRIVATE /W4)
else()
    target_compile_options(${PROJECT_NAME} PRIVATE
        -Wall -Wextra -Wpedantic -Werror
        -Wno-unused-parameter
    )
endif()

# 설치 규칙
install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION bin
)

# 리소스 파일 복사
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/resources/
    DESTINATION share/${PROJECT_NAME}/resources
)
```

### 3. 모던 C++ 기법 활용

#### 3.1 RAII 및 스마트 포인터
```cpp
#include <memory>
#include <vector>
#include <string>
#include <functional>

namespace SemiconductorHMI {

// RAII를 활용한 OpenGL 리소스 관리
class GLTexture {
private:
    GLuint texture_id = 0;

public:
    GLTexture(int width, int height, GLenum format = GL_RGBA) {
        glGenTextures(1, &texture_id);
        glBindTexture(GL_TEXTURE_2D, texture_id);
        glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    }

    ~GLTexture() {
        if (texture_id != 0) {
            glDeleteTextures(1, &texture_id);
        }
    }

    // 이동 생성자/대입연산자
    GLTexture(GLTexture&& other) noexcept : texture_id(other.texture_id) {
        other.texture_id = 0;
    }

    GLTexture& operator=(GLTexture&& other) noexcept {
        if (this != &other) {
            if (texture_id != 0) {
                glDeleteTextures(1, &texture_id);
            }
            texture_id = other.texture_id;
            other.texture_id = 0;
        }
        return *this;
    }

    // 복사 방지
    GLTexture(const GLTexture&) = delete;
    GLTexture& operator=(const GLTexture&) = delete;

    GLuint GetID() const { return texture_id; }
};

// 스마트 포인터를 활용한 UI 컴포넌트 관리
class UIComponent {
public:
    virtual ~UIComponent() = default;
    virtual void Render() = 0;
    virtual void Update(float delta_time) {}
};

class EquipmentPanel : public UIComponent {
private:
    std::string panel_name;
    std::vector<std::unique_ptr<UIComponent>> child_components;

public:
    explicit EquipmentPanel(std::string name) : panel_name(std::move(name)) {}

    void AddComponent(std::unique_ptr<UIComponent> component) {
        child_components.push_back(std::move(component));
    }

    void Render() override {
        if (ImGui::Begin(panel_name.c_str())) {
            for (auto& component : child_components) {
                component->Render();
            }
        }
        ImGui::End();
    }

    void Update(float delta_time) override {
        for (auto& component : child_components) {
            component->Update(delta_time);
        }
    }
};

} // namespace SemiconductorHMI
```

#### 3.2 템플릿 및 컨셉을 활용한 제네릭 프로그래밍
```cpp
#include <concepts>
#include <type_traits>
#include <ranges>
#include <algorithm>

namespace SemiconductorHMI {

// C++20 컨셉을 활용한 타입 제약
template<typename T>
concept Numeric = std::is_arithmetic_v<T>;

template<typename T>
concept Renderable = requires(T t) {
    t.Render();
};

// 제네릭 데이터 시리즈 클래스
template<Numeric T>
class DataSeries {
private:
    std::vector<T> data;
    std::vector<std::chrono::high_resolution_clock::time_point> timestamps;
    size_t max_size;

public:
    explicit DataSeries(size_t max_points = 1000) : max_size(max_points) {
        data.reserve(max_size);
        timestamps.reserve(max_size);
    }

    void AddPoint(T value) {
        auto now = std::chrono::high_resolution_clock::now();

        if (data.size() >= max_size) {
            data.erase(data.begin());
            timestamps.erase(timestamps.begin());
        }

        data.push_back(value);
        timestamps.push_back(now);
    }

    // 최근 N개 포인트의 평균 계산
    template<std::integral U>
    T GetRecentAverage(U count) const {
        if (data.empty()) return T{};

        size_t actual_count = std::min(static_cast<size_t>(count), data.size());
        auto recent_data = data | std::views::take_last(actual_count);

        T sum = std::accumulate(recent_data.begin(), recent_data.end(), T{});
        return sum / static_cast<T>(actual_count);
    }

    // 데이터 범위 반환
    auto GetDataRange() const { return std::views::all(data); }
    auto GetTimestamps() const { return std::views::all(timestamps); }

    T GetMin() const {
        if (data.empty()) return T{};
        return *std::ranges::min_element(data);
    }

    T GetMax() const {
        if (data.empty()) return T{};
        return *std::ranges::max_element(data);
    }
};

// 변분 템플릿을 활용한 UI 컴포넌트 팩토리
template<typename ComponentType, typename... Args>
std::unique_ptr<ComponentType> CreateComponent(Args&&... args) {
    return std::make_unique<ComponentType>(std::forward<Args>(args)...);
}

// 함수형 프로그래밍 스타일의 이벤트 처리
class EventDispatcher {
private:
    std::unordered_map<std::string, std::vector<std::function<void()>>> event_handlers;

public:
    template<typename Func>
    void Subscribe(const std::string& event_name, Func&& handler) {
        event_handlers[event_name].emplace_back(std::forward<Func>(handler));
    }

    void Dispatch(const std::string& event_name) {
        if (auto it = event_handlers.find(event_name); it != event_handlers.end()) {
            std::ranges::for_each(it->second, [](const auto& handler) {
                handler();
            });
        }
    }
};

} // namespace SemiconductorHMI
```

---

## 🔧 **기초 실습 (45분) - 기본 애플리케이션 구축**

### 실습 1: ImGUI 애플리케이션 기본 구조

#### 1.1 메인 애플리케이션 클래스
```cpp
// include/hmi_application.h
#pragma once

#include <imgui.h>
#include <backends/imgui_impl_glfw.h>
#include <backends/imgui_impl_opengl3.h>
#include <GLFW/glfw3.h>
#include <glad/glad.h>

#include <memory>
#include <vector>
#include <string>
#include <chrono>

namespace SemiconductorHMI {

class HMIApplication {
private:
    GLFWwindow* window = nullptr;
    std::string window_title;
    int window_width, window_height;
    bool vsync_enabled = true;

    // 성능 측정
    std::chrono::high_resolution_clock::time_point last_frame_time;
    float frame_time = 0.0f;
    float fps = 0.0f;

public:
    HMIApplication(const std::string& title, int width = 1920, int height = 1080);
    ~HMIApplication();

    bool Initialize();
    void Run();
    void Shutdown();

protected:
    virtual void OnStartup() {}
    virtual void OnUpdate(float delta_time) {}
    virtual void OnRender() = 0;
    virtual void OnShutdown() {}

    // 유틸리티 함수들
    void SetVSync(bool enabled);
    float GetFrameTime() const { return frame_time; }
    float GetFPS() const { return fps; }

private:
    void UpdatePerformanceMetrics();
    static void GLFWErrorCallback(int error, const char* description);
};

} // namespace SemiconductorHMI
```

#### 1.2 메인 애플리케이션 구현
```cpp
// src/hmi_application.cpp
#include "hmi_application.h"
#include <iostream>
#include <stdexcept>

namespace SemiconductorHMI {

HMIApplication::HMIApplication(const std::string& title, int width, int height)
    : window_title(title), window_width(width), window_height(height) {
    last_frame_time = std::chrono::high_resolution_clock::now();
}

HMIApplication::~HMIApplication() {
    Shutdown();
}

bool HMIApplication::Initialize() {
    // GLFW 에러 콜백 설정
    glfwSetErrorCallback(GLFWErrorCallback);

    // GLFW 초기화
    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW" << std::endl;
        return false;
    }

    // OpenGL 버전 및 프로파일 설정
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 5);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);

    // 윈도우 설정
    glfwWindowHint(GLFW_SAMPLES, 4); // MSAA
    glfwWindowHint(GLFW_DOUBLEBUFFER, GLFW_TRUE);

    // 윈도우 생성
    window = glfwCreateWindow(window_width, window_height, window_title.c_str(), nullptr, nullptr);
    if (!window) {
        std::cerr << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return false;
    }

    glfwMakeContextCurrent(window);
    SetVSync(vsync_enabled);

    // GLAD 초기화
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        std::cerr << "Failed to initialize GLAD" << std::endl;
        return false;
    }

    // OpenGL 정보 출력
    std::cout << "OpenGL Version: " << glGetString(GL_VERSION) << std::endl;
    std::cout << "GLSL Version: " << glGetString(GL_SHADING_LANGUAGE_VERSION) << std::endl;
    std::cout << "Renderer: " << glGetString(GL_RENDERER) << std::endl;

    // ImGUI 초기화
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();

    // ImGUI 설정
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    io.ConfigFlags |= ImGuiConfigFlags_DockingEnable;
    io.ConfigFlags |= ImGuiConfigFlags_ViewportsEnable;

    // 폰트 로딩
    io.Fonts->AddFontFromFileTTF("resources/fonts/Roboto-Regular.ttf", 16.0f);
    io.Fonts->AddFontFromFileTTF("resources/fonts/RobotoMono-Regular.ttf", 14.0f);

    // 스타일 설정
    ImGui::StyleColorsDark();
    ImGuiStyle& style = ImGui::GetStyle();
    if (io.ConfigFlags & ImGuiConfigFlags_ViewportsEnable) {
        style.WindowRounding = 0.0f;
        style.Colors[ImGuiCol_WindowBg].w = 1.0f;
    }

    // 백엔드 초기화
    ImGui_ImplGlfw_InitForOpenGL(window, true);
    ImGui_ImplOpenGL3_Init("#version 450");

    // OpenGL 설정
    glEnable(GL_MULTISAMPLE);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    OnStartup();
    return true;
}

void HMIApplication::Run() {
    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();

        // 성능 측정 업데이트
        UpdatePerformanceMetrics();

        // 애플리케이션 업데이트
        OnUpdate(frame_time);

        // 새 프레임 시작
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        // 애플리케이션 렌더링
        OnRender();

        // ImGUI 렌더링 완료
        ImGui::Render();

        // OpenGL 뷰포트 및 클리어
        int display_w, display_h;
        glfwGetFramebufferSize(window, &display_w, &display_h);
        glViewport(0, 0, display_w, display_h);
        glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        // ImGUI 드로우 데이터 렌더링
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

        // 멀티 뷰포트 지원
        ImGuiIO& io = ImGui::GetIO();
        if (io.ConfigFlags & ImGuiConfigFlags_ViewportsEnable) {
            GLFWwindow* backup_current_context = glfwGetCurrentContext();
            ImGui::UpdatePlatformWindows();
            ImGui::RenderPlatformWindowsDefault();
            glfwMakeContextCurrent(backup_current_context);
        }

        glfwSwapBuffers(window);
    }
}

void HMIApplication::Shutdown() {
    if (window) {
        OnShutdown();

        ImGui_ImplOpenGL3_Shutdown();
        ImGui_ImplGlfw_Shutdown();
        ImGui::DestroyContext();

        glfwDestroyWindow(window);
        glfwTerminate();
        window = nullptr;
    }
}

void HMIApplication::SetVSync(bool enabled) {
    vsync_enabled = enabled;
    glfwSwapInterval(enabled ? 1 : 0);
}

void HMIApplication::UpdatePerformanceMetrics() {
    auto current_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration<float>(current_time - last_frame_time);
    frame_time = duration.count();
    fps = 1.0f / frame_time;
    last_frame_time = current_time;
}

void HMIApplication::GLFWErrorCallback(int error, const char* description) {
    std::cerr << "GLFW Error " << error << ": " << description << std::endl;
}

} // namespace SemiconductorHMI
```

### 실습 2: 기본 UI 컴포넌트 구현

#### 2.1 실시간 차트 위젯
```cpp
// include/ui_components/realtime_chart.h
#pragma once

#include <imgui.h>
#include <vector>
#include <string>
#include <chrono>
#include <algorithm>

namespace SemiconductorHMI::UI {

class RealtimeChart {
private:
    std::string chart_title;
    std::vector<float> data_points;
    std::vector<std::chrono::high_resolution_clock::time_point> timestamps;
    size_t max_points;
    float min_value, max_value;
    bool auto_scale;
    ImVec4 line_color;
    float line_thickness;

public:
    RealtimeChart(const std::string& title, size_t max_data_points = 1000)
        : chart_title(title)
        , max_points(max_data_points)
        , min_value(0.0f)
        , max_value(100.0f)
        , auto_scale(true)
        , line_color(0.0f, 1.0f, 0.0f, 1.0f)
        , line_thickness(2.0f) {
        data_points.reserve(max_points);
        timestamps.reserve(max_points);
    }

    void AddDataPoint(float value) {
        auto now = std::chrono::high_resolution_clock::now();

        // 최대 포인트 수 제한
        if (data_points.size() >= max_points) {
            data_points.erase(data_points.begin());
            timestamps.erase(timestamps.begin());
        }

        data_points.push_back(value);
        timestamps.push_back(now);

        // 자동 스케일링
        if (auto_scale && !data_points.empty()) {
            auto [min_it, max_it] = std::minmax_element(data_points.begin(), data_points.end());
            min_value = *min_it - (*max_it - *min_it) * 0.1f;
            max_value = *max_it + (*max_it - *min_it) * 0.1f;
        }
    }

    void Render(const ImVec2& size = ImVec2(0, 0)) {
        if (ImGui::BeginChild(chart_title.c_str(), size, true)) {
            ImDrawList* draw_list = ImGui::GetWindowDrawList();
            ImVec2 canvas_pos = ImGui::GetCursorScreenPos();
            ImVec2 canvas_size = ImGui::GetContentRegionAvail();

            if (canvas_size.x < 50.0f) canvas_size.x = 50.0f;
            if (canvas_size.y < 50.0f) canvas_size.y = 50.0f;

            // 배경 그리기
            draw_list->AddRectFilled(canvas_pos,
                ImVec2(canvas_pos.x + canvas_size.x, canvas_pos.y + canvas_size.y),
                IM_COL32(20, 20, 20, 255));

            // 그리드 그리기
            DrawGrid(draw_list, canvas_pos, canvas_size);

            // 데이터 라인 그리기
            if (data_points.size() >= 2) {
                DrawDataLine(draw_list, canvas_pos, canvas_size);
            }

            // 현재 값 표시
            if (!data_points.empty()) {
                ImGui::SetCursorScreenPos(ImVec2(canvas_pos.x + 5, canvas_pos.y + 5));
                ImGui::Text("%s: %.2f", chart_title.c_str(), data_points.back());
            }

            ImGui::SetCursorScreenPos(ImVec2(canvas_pos.x, canvas_pos.y + canvas_size.y));
        }
        ImGui::EndChild();
    }

    void SetRange(float min_val, float max_val) {
        min_value = min_val;
        max_value = max_val;
        auto_scale = false;
    }

    void SetAutoScale(bool enable) { auto_scale = enable; }
    void SetLineColor(const ImVec4& color) { line_color = color; }
    void SetLineThickness(float thickness) { line_thickness = thickness; }

private:
    void DrawGrid(ImDrawList* draw_list, const ImVec2& canvas_pos, const ImVec2& canvas_size) {
        const ImU32 grid_color = IM_COL32(50, 50, 50, 255);
        const int grid_lines = 10;

        // 수직 그리드 라인
        for (int i = 0; i <= grid_lines; ++i) {
            float x = canvas_pos.x + (canvas_size.x / grid_lines) * i;
            draw_list->AddLine(ImVec2(x, canvas_pos.y),
                              ImVec2(x, canvas_pos.y + canvas_size.y), grid_color);
        }

        // 수평 그리드 라인
        for (int i = 0; i <= grid_lines; ++i) {
            float y = canvas_pos.y + (canvas_size.y / grid_lines) * i;
            draw_list->AddLine(ImVec2(canvas_pos.x, y),
                              ImVec2(canvas_pos.x + canvas_size.x, y), grid_color);
        }
    }

    void DrawDataLine(ImDrawList* draw_list, const ImVec2& canvas_pos, const ImVec2& canvas_size) {
        const ImU32 line_col = ImGui::ColorConvertFloat4ToU32(line_color);
        const float value_range = max_value - min_value;

        if (value_range <= 0.0f) return;

        for (size_t i = 1; i < data_points.size(); ++i) {
            // 이전 점
            float prev_x = canvas_pos.x + (canvas_size.x / (data_points.size() - 1)) * (i - 1);
            float prev_y = canvas_pos.y + canvas_size.y -
                          ((data_points[i - 1] - min_value) / value_range) * canvas_size.y;

            // 현재 점
            float curr_x = canvas_pos.x + (canvas_size.x / (data_points.size() - 1)) * i;
            float curr_y = canvas_pos.y + canvas_size.y -
                          ((data_points[i] - min_value) / value_range) * canvas_size.y;

            draw_list->AddLine(ImVec2(prev_x, prev_y), ImVec2(curr_x, curr_y),
                              line_col, line_thickness);
        }
    }
};

} // namespace SemiconductorHMI::UI
```

#### 2.2 장비 상태 패널
```cpp
// include/ui_components/equipment_status_panel.h
#pragma once

#include <imgui.h>
#include <string>
#include <unordered_map>
#include <chrono>

namespace SemiconductorHMI::UI {

enum class EquipmentState {
    Idle,
    Running,
    Error,
    Maintenance,
    Offline
};

struct EquipmentStatus {
    EquipmentState state = EquipmentState::Idle;
    std::string status_message;
    std::chrono::system_clock::time_point last_update;
    float utilization = 0.0f;
    int process_count = 0;
    bool alarm_active = false;
};

class EquipmentStatusPanel {
private:
    std::string panel_title;
    std::unordered_map<std::string, EquipmentStatus> equipment_status;

    // 상태별 색상 정의
    static inline const std::unordered_map<EquipmentState, ImVec4> state_colors = {
        {EquipmentState::Idle, ImVec4(0.5f, 0.5f, 0.5f, 1.0f)},      // Gray
        {EquipmentState::Running, ImVec4(0.0f, 1.0f, 0.0f, 1.0f)},   // Green
        {EquipmentState::Error, ImVec4(1.0f, 0.0f, 0.0f, 1.0f)},     // Red
        {EquipmentState::Maintenance, ImVec4(1.0f, 1.0f, 0.0f, 1.0f)}, // Yellow
        {EquipmentState::Offline, ImVec4(0.3f, 0.3f, 0.3f, 1.0f)}    // Dark Gray
    };

    static inline const std::unordered_map<EquipmentState, std::string> state_names = {
        {EquipmentState::Idle, "IDLE"},
        {EquipmentState::Running, "RUNNING"},
        {EquipmentState::Error, "ERROR"},
        {EquipmentState::Maintenance, "MAINTENANCE"},
        {EquipmentState::Offline, "OFFLINE"}
    };

public:
    explicit EquipmentStatusPanel(const std::string& title) : panel_title(title) {}

    void UpdateEquipmentStatus(const std::string& equipment_id, const EquipmentStatus& status) {
        equipment_status[equipment_id] = status;
        equipment_status[equipment_id].last_update = std::chrono::system_clock::now();
    }

    void Render() {
        if (ImGui::Begin(panel_title.c_str())) {
            // 헤더 정보
            ImGui::Text("Equipment Count: %zu", equipment_status.size());
            ImGui::Separator();

            // 장비별 상태 표시
            for (const auto& [equipment_id, status] : equipment_status) {
                RenderEquipmentItem(equipment_id, status);
            }
        }
        ImGui::End();
    }

private:
    void RenderEquipmentItem(const std::string& equipment_id, const EquipmentStatus& status) {
        ImGui::PushID(equipment_id.c_str());

        // 상태 인디케이터
        const auto& color = state_colors.at(status.state);
        ImGui::ColorButton("##status", color, ImGuiColorEditFlags_NoTooltip, ImVec2(20, 20));

        ImGui::SameLine();
        ImGui::Text("%s", equipment_id.c_str());

        ImGui::SameLine();
        ImGui::Text("[%s]", state_names.at(status.state).c_str());

        // 알람 표시
        if (status.alarm_active) {
            ImGui::SameLine();
            ImGui::TextColored(ImVec4(1.0f, 0.0f, 0.0f, 1.0f), "⚠ ALARM");
        }

        // 상세 정보 (들여쓰기)
        ImGui::Indent();

        if (!status.status_message.empty()) {
            ImGui::Text("Status: %s", status.status_message.c_str());
        }

        ImGui::Text("Utilization: %.1f%%", status.utilization);
        ImGui::Text("Process Count: %d", status.process_count);

        // 마지막 업데이트 시간
        auto time_since_update = std::chrono::system_clock::now() - status.last_update;
        auto seconds = std::chrono::duration_cast<std::chrono::seconds>(time_since_update).count();
        ImGui::Text("Last Update: %ld seconds ago", seconds);

        ImGui::Unindent();
        ImGui::Separator();

        ImGui::PopID();
    }
};

} // namespace SemiconductorHMI::UI
```

### 실습 3: 메인 애플리케이션 구현

#### 3.1 반도체 HMI 메인 클래스
```cpp
// include/semiconductor_hmi.h
#pragma once

#include "hmi_application.h"
#include "ui_components/realtime_chart.h"
#include "ui_components/equipment_status_panel.h"
#include <random>
#include <thread>

namespace SemiconductorHMI {

class SemiconductorHMIApp : public HMIApplication {
private:
    // UI 컴포넌트들
    std::unique_ptr<UI::RealtimeChart> pressure_chart;
    std::unique_ptr<UI::RealtimeChart> temperature_chart;
    std::unique_ptr<UI::RealtimeChart> power_chart;
    std::unique_ptr<UI::EquipmentStatusPanel> status_panel;

    // 시뮬레이션 데이터
    std::random_device rd;
    std::mt19937 gen;
    std::uniform_real_distribution<float> pressure_dist;
    std::uniform_real_distribution<float> temperature_dist;
    std::uniform_real_distribution<float> power_dist;

    // 메뉴바 상태
    bool show_demo_window = false;
    bool show_metrics_window = true;

public:
    SemiconductorHMIApp()
        : HMIApplication("Semiconductor Equipment HMI", 1920, 1080)
        , gen(rd())
        , pressure_dist(0.001f, 0.1f)    // Torr
        , temperature_dist(200.0f, 800.0f) // Celsius
        , power_dist(500.0f, 1500.0f)     // Watts
    {}

protected:
    void OnStartup() override {
        // UI 컴포넌트 초기화
        pressure_chart = std::make_unique<UI::RealtimeChart>("Chamber Pressure (Torr)", 500);
        pressure_chart->SetRange(0.0f, 0.2f);
        pressure_chart->SetLineColor(ImVec4(0.0f, 1.0f, 1.0f, 1.0f)); // Cyan

        temperature_chart = std::make_unique<UI::RealtimeChart>("Substrate Temperature (°C)", 500);
        temperature_chart->SetRange(0.0f, 1000.0f);
        temperature_chart->SetLineColor(ImVec4(1.0f, 0.5f, 0.0f, 1.0f)); // Orange

        power_chart = std::make_unique<UI::RealtimeChart>("RF Power (W)", 500);
        power_chart->SetRange(0.0f, 2000.0f);
        power_chart->SetLineColor(ImVec4(1.0f, 0.0f, 1.0f, 1.0f)); // Magenta

        status_panel = std::make_unique<UI::EquipmentStatusPanel>("Equipment Status");

        // 초기 장비 상태 설정
        InitializeEquipmentStatus();
    }

    void OnUpdate(float delta_time) override {
        // 시뮬레이션 데이터 생성 (10Hz 업데이트)
        static float update_timer = 0.0f;
        update_timer += delta_time;

        if (update_timer >= 0.1f) { // 100ms마다 업데이트
            // 실시간 데이터 생성
            float pressure = pressure_dist(gen);
            float temperature = temperature_dist(gen);
            float power = power_dist(gen);

            // 차트에 데이터 추가
            pressure_chart->AddDataPoint(pressure);
            temperature_chart->AddDataPoint(temperature);
            power_chart->AddDataPoint(power);

            // 장비 상태 업데이트
            UpdateEquipmentStatus();

            update_timer = 0.0f;
        }
    }

    void OnRender() override {
        // 메인 메뉴바
        RenderMainMenuBar();

        // 도킹 스페이스 설정
        SetupDockSpace();

        // 실시간 차트 창
        RenderChartsWindow();

        // 장비 상태 창
        status_panel->Render();

        // 성능 메트릭 창
        if (show_metrics_window) {
            RenderMetricsWindow();
        }

        // ImGUI 데모 창
        if (show_demo_window) {
            ImGui::ShowDemoWindow(&show_demo_window);
        }
    }

private:
    void InitializeEquipmentStatus() {
        using namespace UI;

        status_panel->UpdateEquipmentStatus("CVD-Chamber-01", {
            EquipmentState::Running, "Processing wafer batch #1234", {}, 85.5f, 42, false
        });

        status_panel->UpdateEquipmentStatus("PVD-Chamber-02", {
            EquipmentState::Idle, "Ready for next process", {}, 0.0f, 0, false
        });

        status_panel->UpdateEquipmentStatus("ETCH-Chamber-03", {
            EquipmentState::Error, "Gas line pressure low", {}, 0.0f, 0, true
        });

        status_panel->UpdateEquipmentStatus("CMP-Station-04", {
            EquipmentState::Maintenance, "Scheduled PM in progress", {}, 0.0f, 0, false
        });
    }

    void UpdateEquipmentStatus() {
        using namespace UI;

        // 간단한 상태 시뮬레이션
        static int update_counter = 0;
        update_counter++;

        if (update_counter % 50 == 0) { // 5초마다 상태 변경
            auto utilization = std::uniform_real_distribution<float>(0.0f, 100.0f)(gen);
            status_panel->UpdateEquipmentStatus("CVD-Chamber-01", {
                EquipmentState::Running, "Processing wafer batch #1234", {}, utilization, 42, false
            });
        }
    }

    void RenderMainMenuBar() {
        if (ImGui::BeginMainMenuBar()) {
            if (ImGui::BeginMenu("File")) {
                if (ImGui::MenuItem("New Recipe")) {
                    // 새 레시피 생성 로직
                }
                if (ImGui::MenuItem("Load Recipe")) {
                    // 레시피 로드 로직
                }
                ImGui::Separator();
                if (ImGui::MenuItem("Exit")) {
                    glfwSetWindowShouldClose(window, GLFW_TRUE);
                }
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("View")) {
                ImGui::MenuItem("Equipment Status", nullptr, &show_metrics_window);
                ImGui::MenuItem("Performance Metrics", nullptr, &show_metrics_window);
                ImGui::Separator();
                ImGui::MenuItem("ImGui Demo", nullptr, &show_demo_window);
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("Tools")) {
                if (ImGui::MenuItem("Calibration")) {
                    // 캘리브레이션 다이얼로그
                }
                if (ImGui::MenuItem("Data Export")) {
                    // 데이터 내보내기
                }
                ImGui::EndMenu();
            }

            ImGui::EndMainMenuBar();
        }
    }

    void SetupDockSpace() {
        static bool dockspace_open = true;
        static ImGuiDockNodeFlags dockspace_flags = ImGuiDockNodeFlags_None;

        ImGuiWindowFlags window_flags = ImGuiWindowFlags_MenuBar | ImGuiWindowFlags_NoDocking;
        ImGuiViewport* viewport = ImGui::GetMainViewport();
        ImGui::SetNextWindowPos(viewport->Pos);
        ImGui::SetNextWindowSize(viewport->Size);
        ImGui::SetNextWindowViewport(viewport->ID);

        window_flags |= ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoCollapse;
        window_flags |= ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoMove;
        window_flags |= ImGuiWindowFlags_NoBringToFrontOnFocus | ImGuiWindowFlags_NoNavFocus;

        if (dockspace_flags & ImGuiDockNodeFlags_PassthruCentralNode)
            window_flags |= ImGuiWindowFlags_NoBackground;

        ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, 0.0f);
        ImGui::PushStyleVar(ImGuiStyleVar_WindowBorderSize, 0.0f);
        ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0.0f, 0.0f));

        ImGui::Begin("DockSpace Demo", &dockspace_open, window_flags);
        ImGui::PopStyleVar(3);

        ImGuiIO& io = ImGui::GetIO();
        if (io.ConfigFlags & ImGuiConfigFlags_DockingEnable) {
            ImGuiID dockspace_id = ImGui::GetID("MyDockSpace");
            ImGui::DockSpace(dockspace_id, ImVec2(0.0f, 0.0f), dockspace_flags);
        }

        ImGui::End();
    }

    void RenderChartsWindow() {
        if (ImGui::Begin("Real-time Data")) {
            // 차트들을 수직으로 배열
            float chart_height = (ImGui::GetContentRegionAvail().y - 20.0f) / 3.0f;

            pressure_chart->Render(ImVec2(-1, chart_height));
            temperature_chart->Render(ImVec2(-1, chart_height));
            power_chart->Render(ImVec2(-1, chart_height));
        }
        ImGui::End();
    }

    void RenderMetricsWindow() {
        if (ImGui::Begin("Performance Metrics", &show_metrics_window)) {
            ImGui::Text("Application average %.3f ms/frame (%.1f FPS)",
                       GetFrameTime() * 1000.0f, GetFPS());

            ImGui::Separator();

            // 메모리 사용량 (플랫폼별로 다르게 구현 필요)
            ImGui::Text("Memory Usage: N/A");
            ImGui::Text("GPU Memory: N/A");

            ImGui::Separator();

            // ImGUI 메트릭
            ImGuiIO& io = ImGui::GetIO();
            ImGui::Text("Dear ImGui %s", ImGui::GetVersion());
            ImGui::Text("Vertices: %d, Indices: %d", io.MetricsRenderVertices, io.MetricsRenderIndices);
            ImGui::Text("Windows: %d, Active: %d", io.MetricsRenderWindows, io.MetricsActiveWindows);
        }
        ImGui::End();
    }
};

} // namespace SemiconductorHMI
```

#### 3.2 메인 함수
```cpp
// src/main.cpp
#include "semiconductor_hmi.h"
#include <iostream>
#include <exception>

int main() {
    try {
        SemiconductorHMI::SemiconductorHMIApp app;

        if (!app.Initialize()) {
            std::cerr << "Failed to initialize application" << std::endl;
            return -1;
        }

        app.Run();

    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return -1;
    } catch (...) {
        std::cerr << "Unknown exception occurred" << std::endl;
        return -1;
    }

    return 0;
}
```

---

## 🚀 **심화 실습 (45분) - 커스텀 위젯 및 실시간 데이터 처리**

### 실습 4: 고급 시각화 위젯

#### 4.1 원형 게이지 위젯
```cpp
// include/ui_components/circular_gauge.h
#pragma once

#include <imgui.h>
#include <cmath>
#include <algorithm>

namespace SemiconductorHMI::UI {

class CircularGauge {
private:
    std::string label;
    float current_value;
    float min_value, max_value;
    float warning_threshold, critical_threshold;
    ImVec4 normal_color, warning_color, critical_color;
    float radius;
    float thickness;
    bool show_text;

public:
    CircularGauge(const std::string& gauge_label, float min_val = 0.0f, float max_val = 100.0f)
        : label(gauge_label)
        , current_value(0.0f)
        , min_value(min_val)
        , max_value(max_val)
        , warning_threshold(max_val * 0.7f)
        , critical_threshold(max_val * 0.9f)
        , normal_color(0.0f, 1.0f, 0.0f, 1.0f)    // Green
        , warning_color(1.0f, 1.0f, 0.0f, 1.0f)   // Yellow
        , critical_color(1.0f, 0.0f, 0.0f, 1.0f)  // Red
        , radius(50.0f)
        , thickness(8.0f)
        , show_text(true) {}

    void SetValue(float value) {
        current_value = std::clamp(value, min_value, max_value);
    }

    void SetThresholds(float warning, float critical) {
        warning_threshold = warning;
        critical_threshold = critical;
    }

    void SetColors(const ImVec4& normal, const ImVec4& warning, const ImVec4& critical) {
        normal_color = normal;
        warning_color = warning;
        critical_color = critical;
    }

    void SetSize(float gauge_radius, float gauge_thickness) {
        radius = gauge_radius;
        thickness = gauge_thickness;
    }

    void Render() {
        ImDrawList* draw_list = ImGui::GetWindowDrawList();
        ImVec2 canvas_pos = ImGui::GetCursorScreenPos();
        ImVec2 center = ImVec2(canvas_pos.x + radius + 10, canvas_pos.y + radius + 10);

        // 배경 원
        draw_list->AddCircle(center, radius, IM_COL32(60, 60, 60, 255), 64, thickness);

        // 게이지 호 그리기
        float normalized_value = (current_value - min_value) / (max_value - min_value);
        float angle_range = 1.5f * IM_PI; // 270도
        float start_angle = 0.75f * IM_PI; // 135도에서 시작
        float end_angle = start_angle + angle_range * normalized_value;

        // 색상 결정
        ImVec4 gauge_color = normal_color;
        if (current_value >= critical_threshold) {
            gauge_color = critical_color;
        } else if (current_value >= warning_threshold) {
            gauge_color = warning_color;
        }

        // 게이지 호 그리기 (부드러운 그라데이션을 위해 세그먼트로 나누어 그리기)
        const int segments = 64;
        float angle_step = angle_range / segments;
        float current_angle = start_angle;

        for (int i = 0; i < segments && current_angle < end_angle; ++i) {
            float next_angle = std::min(current_angle + angle_step, end_angle);

            ImVec2 p1 = ImVec2(
                center.x + std::cos(current_angle) * (radius - thickness/2),
                center.y + std::sin(current_angle) * (radius - thickness/2)
            );
            ImVec2 p2 = ImVec2(
                center.x + std::cos(next_angle) * (radius - thickness/2),
                center.y + std::sin(next_angle) * (radius - thickness/2)
            );

            draw_list->AddLine(p1, p2, ImGui::ColorConvertFloat4ToU32(gauge_color), thickness);
            current_angle = next_angle;
        }

        // 눈금 표시
        DrawTicks(draw_list, center);

        // 텍스트 표시
        if (show_text) {
            DrawText(center);
        }

        // ImGui 커서 위치 업데이트
        ImGui::SetCursorScreenPos(ImVec2(canvas_pos.x, canvas_pos.y + (radius + 10) * 2 + 20));
    }

private:
    void DrawTicks(ImDrawList* draw_list, const ImVec2& center) {
        const int tick_count = 11;
        const float tick_length = 8.0f;
        const float angle_range = 1.5f * IM_PI;
        const float start_angle = 0.75f * IM_PI;

        for (int i = 0; i < tick_count; ++i) {
            float angle = start_angle + (angle_range / (tick_count - 1)) * i;

            ImVec2 tick_start = ImVec2(
                center.x + std::cos(angle) * (radius + 5),
                center.y + std::sin(angle) * (radius + 5)
            );
            ImVec2 tick_end = ImVec2(
                center.x + std::cos(angle) * (radius + 5 + tick_length),
                center.y + std::sin(angle) * (radius + 5 + tick_length)
            );

            draw_list->AddLine(tick_start, tick_end, IM_COL32(200, 200, 200, 255), 2.0f);

            // 숫자 표시
            if (i % 2 == 0) {
                float value = min_value + (max_value - min_value) * i / (tick_count - 1);
                ImVec2 text_pos = ImVec2(
                    center.x + std::cos(angle) * (radius + 20) - 10,
                    center.y + std::sin(angle) * (radius + 20) - 8
                );

                char text[16];
                snprintf(text, sizeof(text), "%.0f", value);
                draw_list->AddText(text_pos, IM_COL32(200, 200, 200, 255), text);
            }
        }
    }

    void DrawText(const ImVec2& center) {
        // 현재 값 표시
        char value_text[32];
        snprintf(value_text, sizeof(value_text), "%.1f", current_value);

        ImVec2 text_size = ImGui::CalcTextSize(value_text);
        ImVec2 text_pos = ImVec2(center.x - text_size.x/2, center.y - text_size.y/2);

        ImGui::SetCursorScreenPos(text_pos);
        ImGui::Text("%s", value_text);

        // 라벨 표시
        text_size = ImGui::CalcTextSize(label.c_str());
        text_pos = ImVec2(center.x - text_size.x/2, center.y + 15);

        ImGui::SetCursorScreenPos(text_pos);
        ImGui::Text("%s", label.c_str());
    }
};

} // namespace SemiconductorHMI::UI
```

#### 4.2 히트맵 시각화 위젯
```cpp
// include/ui_components/heatmap.h
#pragma once

#include <imgui.h>
#include <vector>
#include <algorithm>
#include <cmath>

namespace SemiconductorHMI::UI {

class Heatmap {
private:
    std::string title;
    std::vector<std::vector<float>> data;
    int width, height;
    float min_value, max_value;
    bool auto_scale;
    std::vector<ImVec4> color_map;

public:
    Heatmap(const std::string& heatmap_title, int w, int h)
        : title(heatmap_title)
        , width(w)
        , height(h)
        , min_value(0.0f)
        , max_value(1.0f)
        , auto_scale(true) {

        data.resize(height, std::vector<float>(width, 0.0f));
        InitializeColorMap();
    }

    void SetData(const std::vector<std::vector<float>>& new_data) {
        if (new_data.size() == height && new_data[0].size() == width) {
            data = new_data;

            if (auto_scale) {
                UpdateScale();
            }
        }
    }

    void SetValue(int x, int y, float value) {
        if (x >= 0 && x < width && y >= 0 && y < height) {
            data[y][x] = value;

            if (auto_scale) {
                UpdateScale();
            }
        }
    }

    void SetRange(float min_val, float max_val) {
        min_value = min_val;
        max_value = max_val;
        auto_scale = false;
    }

    void Render(const ImVec2& size = ImVec2(0, 0)) {
        if (ImGui::BeginChild(title.c_str(), size, true)) {
            ImDrawList* draw_list = ImGui::GetWindowDrawList();
            ImVec2 canvas_pos = ImGui::GetCursorScreenPos();
            ImVec2 canvas_size = ImGui::GetContentRegionAvail();

            if (canvas_size.x < 100.0f) canvas_size.x = 100.0f;
            if (canvas_size.y < 100.0f) canvas_size.y = 100.0f;

            // 셀 크기 계산
            float cell_width = canvas_size.x / width;
            float cell_height = canvas_size.y / height;

            // 히트맵 렌더링
            for (int y = 0; y < height; ++y) {
                for (int x = 0; x < width; ++x) {
                    float normalized_value = (data[y][x] - min_value) / (max_value - min_value);
                    normalized_value = std::clamp(normalized_value, 0.0f, 1.0f);

                    ImVec4 color = GetColorFromValue(normalized_value);
                    ImU32 color_u32 = ImGui::ColorConvertFloat4ToU32(color);

                    ImVec2 cell_min = ImVec2(
                        canvas_pos.x + x * cell_width,
                        canvas_pos.y + y * cell_height
                    );
                    ImVec2 cell_max = ImVec2(
                        cell_min.x + cell_width,
                        cell_min.y + cell_height
                    );

                    draw_list->AddRectFilled(cell_min, cell_max, color_u32);

                    // 테두리 그리기 (선택적)
                    draw_list->AddRect(cell_min, cell_max, IM_COL32(50, 50, 50, 255));
                }
            }

            // 컬러바 렌더링
            RenderColorBar(draw_list, canvas_pos, canvas_size);

            ImGui::SetCursorScreenPos(ImVec2(canvas_pos.x, canvas_pos.y + canvas_size.y));
        }
        ImGui::EndChild();
    }

private:
    void InitializeColorMap() {
        // 파란색에서 빨간색으로 그라데이션
        color_map = {
            ImVec4(0.0f, 0.0f, 1.0f, 1.0f),  // Blue
            ImVec4(0.0f, 1.0f, 1.0f, 1.0f),  // Cyan
            ImVec4(0.0f, 1.0f, 0.0f, 1.0f),  // Green
            ImVec4(1.0f, 1.0f, 0.0f, 1.0f),  // Yellow
            ImVec4(1.0f, 0.5f, 0.0f, 1.0f),  // Orange
            ImVec4(1.0f, 0.0f, 0.0f, 1.0f)   // Red
        };
    }

    ImVec4 GetColorFromValue(float normalized_value) {
        if (color_map.empty()) return ImVec4(0, 0, 0, 1);

        float scaled_value = normalized_value * (color_map.size() - 1);
        int index = static_cast<int>(scaled_value);
        float fraction = scaled_value - index;

        if (index >= color_map.size() - 1) {
            return color_map.back();
        }

        // 선형 보간
        const ImVec4& color1 = color_map[index];
        const ImVec4& color2 = color_map[index + 1];

        return ImVec4(
            color1.x + (color2.x - color1.x) * fraction,
            color1.y + (color2.y - color1.y) * fraction,
            color1.z + (color2.z - color1.z) * fraction,
            color1.w + (color2.w - color1.w) * fraction
        );
    }

    void UpdateScale() {
        min_value = std::numeric_limits<float>::max();
        max_value = std::numeric_limits<float>::lowest();

        for (const auto& row : data) {
            for (float value : row) {
                min_value = std::min(min_value, value);
                max_value = std::max(max_value, value);
            }
        }

        // 약간의 여백 추가
        float range = max_value - min_value;
        min_value -= range * 0.05f;
        max_value += range * 0.05f;
    }

    void RenderColorBar(ImDrawList* draw_list, const ImVec2& canvas_pos, const ImVec2& canvas_size) {
        const float colorbar_width = 20.0f;
        const float colorbar_height = canvas_size.y * 0.8f;
        const ImVec2 colorbar_pos = ImVec2(
            canvas_pos.x + canvas_size.x + 10,
            canvas_pos.y + (canvas_size.y - colorbar_height) / 2
        );

        // 컬러바 그라데이션
        const int gradient_steps = 100;
        for (int i = 0; i < gradient_steps; ++i) {
            float normalized_value = static_cast<float>(i) / (gradient_steps - 1);
            ImVec4 color = GetColorFromValue(normalized_value);
            ImU32 color_u32 = ImGui::ColorConvertFloat4ToU32(color);

            float y_start = colorbar_pos.y + (colorbar_height / gradient_steps) * i;
            float y_end = y_start + (colorbar_height / gradient_steps);

            draw_list->AddRectFilled(
                ImVec2(colorbar_pos.x, y_start),
                ImVec2(colorbar_pos.x + colorbar_width, y_end),
                color_u32
            );
        }

        // 컬러바 테두리
        draw_list->AddRect(
            colorbar_pos,
            ImVec2(colorbar_pos.x + colorbar_width, colorbar_pos.y + colorbar_height),
            IM_COL32(200, 200, 200, 255)
        );

        // 스케일 표시
        char max_text[16], min_text[16];
        snprintf(max_text, sizeof(max_text), "%.2f", max_value);
        snprintf(min_text, sizeof(min_text), "%.2f", min_value);

        draw_list->AddText(
            ImVec2(colorbar_pos.x + colorbar_width + 5, colorbar_pos.y - 8),
            IM_COL32(200, 200, 200, 255),
            max_text
        );

        draw_list->AddText(
            ImVec2(colorbar_pos.x + colorbar_width + 5, colorbar_pos.y + colorbar_height - 8),
            IM_COL32(200, 200, 200, 255),
            min_text
        );
    }
};

} // namespace SemiconductorHMI::UI
```

### 실습 5: 고성능 데이터 처리 시스템

#### 5.1 멀티스레드 데이터 프로세서
```cpp
// include/data_processor.h
#pragma once

#include <thread>
#include <atomic>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <vector>
#include <functional>
#include <chrono>
#include <memory>

namespace SemiconductorHMI {

struct ProcessData {
    std::chrono::high_resolution_clock::time_point timestamp;
    std::vector<float> sensor_values;
    int equipment_id;
};

class DataProcessor {
private:
    std::atomic<bool> running{false};
    std::vector<std::thread> worker_threads;

    // 데이터 큐
    std::queue<ProcessData> data_queue;
    std::mutex queue_mutex;
    std::condition_variable queue_cv;

    // 처리된 데이터 콜백
    std::function<void(const ProcessData&)> data_callback;

    // 성능 메트릭
    std::atomic<uint64_t> processed_count{0};
    std::atomic<uint64_t> dropped_count{0};
    std::chrono::high_resolution_clock::time_point start_time;

    static constexpr size_t MAX_QUEUE_SIZE = 10000;

public:
    DataProcessor(size_t num_threads = std::thread::hardware_concurrency()) {
        worker_threads.reserve(num_threads);
    }

    ~DataProcessor() {
        Stop();
    }

    void Start() {
        if (running.exchange(true)) return;

        start_time = std::chrono::high_resolution_clock::now();

        // 워커 스레드들 시작
        for (size_t i = 0; i < worker_threads.capacity(); ++i) {
            worker_threads.emplace_back(&DataProcessor::WorkerLoop, this);
        }
    }

    void Stop() {
        if (!running.exchange(false)) return;

        // 모든 워커들에게 종료 신호
        queue_cv.notify_all();

        // 스레드들 종료 대기
        for (auto& thread : worker_threads) {
            if (thread.joinable()) {
                thread.join();
            }
        }

        worker_threads.clear();
    }

    bool PushData(const ProcessData& data) {
        std::unique_lock<std::mutex> lock(queue_mutex);

        if (data_queue.size() >= MAX_QUEUE_SIZE) {
            dropped_count++;
            return false; // 큐가 가득 참
        }

        data_queue.push(data);
        queue_cv.notify_one();
        return true;
    }

    void SetDataCallback(std::function<void(const ProcessData&)> callback) {
        data_callback = std::move(callback);
    }

    // 성능 메트릭 조회
    uint64_t GetProcessedCount() const { return processed_count; }
    uint64_t GetDroppedCount() const { return dropped_count; }

    double GetProcessingRate() const {
        auto now = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration<double>(now - start_time);
        return processed_count / duration.count();
    }

    size_t GetQueueSize() const {
        std::lock_guard<std::mutex> lock(queue_mutex);
        return data_queue.size();
    }

private:
    void WorkerLoop() {
        while (running) {
            ProcessData data;

            // 큐에서 데이터 가져오기
            {
                std::unique_lock<std::mutex> lock(queue_mutex);
                queue_cv.wait(lock, [this] { return !data_queue.empty() || !running; });

                if (!running) break;

                if (data_queue.empty()) continue;

                data = std::move(data_queue.front());
                data_queue.pop();
            }

            // 데이터 처리
            ProcessSingleData(data);
            processed_count++;

            // 콜백 호출
            if (data_callback) {
                data_callback(data);
            }
        }
    }

    void ProcessSingleData(ProcessData& data) {
        // 시뮬레이션된 데이터 처리 (필터링, 변환 등)

        // 1. 이동 평균 필터 적용
        ApplyMovingAverageFilter(data.sensor_values);

        // 2. 이상값 제거
        RemoveOutliers(data.sensor_values);

        // 3. 단위 변환 또는 스케일링
        for (auto& value : data.sensor_values) {
            value = value * 1.001f + 0.01f; // 간단한 변환 예제
        }
    }

    void ApplyMovingAverageFilter(std::vector<float>& values) {
        static thread_local std::vector<std::vector<float>> history(
            std::thread::hardware_concurrency(), std::vector<float>(10, 0.0f)
        );

        // 간단한 이동 평균 구현 (실제로는 더 정교한 필터 필요)
        static thread_local size_t thread_id = 0;
        static thread_local bool id_initialized = false;

        if (!id_initialized) {
            thread_id = std::hash<std::thread::id>{}(std::this_thread::get_id()) %
                       std::thread::hardware_concurrency();
            id_initialized = true;
        }

        auto& local_history = history[thread_id];

        for (size_t i = 0; i < values.size() && i < local_history.size(); ++i) {
            local_history[i] = values[i];

            // 마지막 N개 값의 평균 계산
            float sum = 0.0f;
            for (float hist_val : local_history) {
                sum += hist_val;
            }
            values[i] = sum / local_history.size();
        }
    }

    void RemoveOutliers(std::vector<float>& values) {
        if (values.size() < 3) return;

        // 간단한 IQR 기반 이상값 제거
        std::vector<float> sorted_values = values;
        std::sort(sorted_values.begin(), sorted_values.end());

        size_t q1_idx = sorted_values.size() / 4;
        size_t q3_idx = 3 * sorted_values.size() / 4;

        float q1 = sorted_values[q1_idx];
        float q3 = sorted_values[q3_idx];
        float iqr = q3 - q1;

        float lower_bound = q1 - 1.5f * iqr;
        float upper_bound = q3 + 1.5f * iqr;

        for (auto& value : values) {
            if (value < lower_bound || value > upper_bound) {
                // 이상값을 중간값으로 대체
                value = sorted_values[sorted_values.size() / 2];
            }
        }
    }
};

} // namespace SemiconductorHMI
```

#### 5.2 실시간 데이터 시뮬레이터
```cpp
// include/data_simulator.h
#pragma once

#include "data_processor.h"
#include <random>
#include <thread>
#include <atomic>
#include <chrono>

namespace SemiconductorHMI {

class DataSimulator {
private:
    std::atomic<bool> running{false};
    std::thread simulator_thread;
    DataProcessor* data_processor;

    // 시뮬레이션 파라미터
    int sampling_rate_hz = 1000; // 1kHz
    int num_sensors = 16;

    // 랜덤 생성기
    std::random_device rd;
    std::mt19937 gen;
    std::normal_distribution<float> noise_dist;

    // 시뮬레이션된 센서 기준값들
    std::vector<float> base_values;
    std::vector<float> trend_slopes;

public:
    DataSimulator(DataProcessor* processor)
        : data_processor(processor)
        , gen(rd())
        , noise_dist(0.0f, 0.1f) {

        InitializeSensorSimulation();
    }

    ~DataSimulator() {
        Stop();
    }

    void Start() {
        if (running.exchange(true)) return;

        simulator_thread = std::thread(&DataSimulator::SimulationLoop, this);
    }

    void Stop() {
        if (!running.exchange(false)) return;

        if (simulator_thread.joinable()) {
            simulator_thread.join();
        }
    }

    void SetSamplingRate(int rate_hz) {
        sampling_rate_hz = rate_hz;
    }

    void SetSensorCount(int count) {
        num_sensors = count;
        InitializeSensorSimulation();
    }

private:
    void InitializeSensorSimulation() {
        base_values.clear();
        trend_slopes.clear();

        std::uniform_real_distribution<float> base_dist(10.0f, 100.0f);
        std::uniform_real_distribution<float> slope_dist(-0.01f, 0.01f);

        for (int i = 0; i < num_sensors; ++i) {
            base_values.push_back(base_dist(gen));
            trend_slopes.push_back(slope_dist(gen));
        }
    }

    void SimulationLoop() {
        auto next_sample_time = std::chrono::high_resolution_clock::now();
        const auto sample_interval = std::chrono::microseconds(1000000 / sampling_rate_hz);

        uint64_t sample_count = 0;

        while (running) {
            // 다음 샘플 시간까지 대기
            std::this_thread::sleep_until(next_sample_time);
            next_sample_time += sample_interval;

            // 센서 데이터 생성
            ProcessData data;
            data.timestamp = std::chrono::high_resolution_clock::now();
            data.equipment_id = 1;
            data.sensor_values.reserve(num_sensors);

            for (int i = 0; i < num_sensors; ++i) {
                float value = GenerateSensorValue(i, sample_count);
                data.sensor_values.push_back(value);
            }

            // 데이터 프로세서에 전송
            if (data_processor && !data_processor->PushData(data)) {
                // 큐가 가득 찬 경우 경고 (실제로는 로깅 시스템 사용)
                static auto last_warning = std::chrono::steady_clock::now();
                auto now = std::chrono::steady_clock::now();
                if (now - last_warning > std::chrono::seconds(1)) {
                    // printf("Warning: Data queue is full, dropping samples\n");
                    last_warning = now;
                }
            }

            sample_count++;
        }
    }

    float GenerateSensorValue(int sensor_id, uint64_t sample_count) {
        float time_sec = static_cast<float>(sample_count) / sampling_rate_hz;

        // 기본값 + 트렌드 + 주기적 변화 + 노이즈
        float base = base_values[sensor_id];
        float trend = trend_slopes[sensor_id] * time_sec;

        // 다양한 주파수의 사인파 합성
        float periodic = 0.0f;
        periodic += 5.0f * std::sin(2.0f * M_PI * 0.1f * time_sec);  // 0.1Hz
        periodic += 2.0f * std::sin(2.0f * M_PI * 0.5f * time_sec);  // 0.5Hz
        periodic += 1.0f * std::sin(2.0f * M_PI * 2.0f * time_sec);  // 2Hz

        float noise = noise_dist(gen);

        // 센서별 특성 추가
        switch (sensor_id % 4) {
            case 0: // 압력 센서 (로그 스케일 특성)
                return base + trend + periodic * 0.1f + noise;
            case 1: // 온도 센서 (느린 변화)
                return base + trend * 0.1f + periodic * 0.05f + noise * 0.5f;
            case 2: // 유량 센서 (빠른 변화)
                return base + trend + periodic * 2.0f + noise * 2.0f;
            case 3: // 전력 센서 (스파이크 특성)
                if (sample_count % 10000 == 0) { // 가끔 스파이크
                    return base + trend + periodic + 50.0f + noise;
                }
                return base + trend + periodic + noise;
            default:
                return base + trend + periodic + noise;
        }
    }
};

} // namespace SemiconductorHMI
```

---

## 💼 **Hands-on 프로젝트 (45분) - 반도체 장비 모니터링 HMI 프로토타입**

### 최종 프로젝트: 통합 반도체 HMI 시스템

#### 4.1 통합 메인 애플리케이션
```cpp
// include/advanced_semiconductor_hmi.h
#pragma once

#include "hmi_application.h"
#include "data_processor.h"
#include "data_simulator.h"
#include "ui_components/realtime_chart.h"
#include "ui_components/circular_gauge.h"
#include "ui_components/heatmap.h"
#include "ui_components/equipment_status_panel.h"

#include <memory>
#include <unordered_map>
#include <array>

namespace SemiconductorHMI {

class AdvancedSemiconductorHMI : public HMIApplication {
private:
    // 데이터 처리 시스템
    std::unique_ptr<DataProcessor> data_processor;
    std::unique_ptr<DataSimulator> data_simulator;

    // UI 컴포넌트들
    std::unordered_map<std::string, std::unique_ptr<UI::RealtimeChart>> charts;
    std::unordered_map<std::string, std::unique_ptr<UI::CircularGauge>> gauges;
    std::unique_ptr<UI::Heatmap> wafer_heatmap;
    std::unique_ptr<UI::EquipmentStatusPanel> status_panel;

    // 최신 데이터 저장
    ProcessData latest_data;
    std::mutex data_mutex;

    // UI 상태
    bool show_charts = true;
    bool show_gauges = true;
    bool show_heatmap = true;
    bool show_status = true;
    bool show_performance = true;
    int selected_chart_sensor = 0;

    // 웨이퍼 맵 시뮬레이션
    std::array<std::array<float, 32>, 32> wafer_temperature_map;

public:
    AdvancedSemiconductorHMI()
        : HMIApplication("Advanced Semiconductor Equipment HMI", 1920, 1080) {

        InitializeWaferMap();
    }

protected:
    void OnStartup() override {
        // 데이터 처리 시스템 초기화
        data_processor = std::make_unique<DataProcessor>(4); // 4개 워커 스레드
        data_simulator = std::make_unique<DataSimulator>(data_processor.get());

        // 데이터 콜백 설정
        data_processor->SetDataCallback([this](const ProcessData& data) {
            OnDataProcessed(data);
        });

        // UI 컴포넌트 초기화
        InitializeCharts();
        InitializeGauges();
        InitializeHeatmap();
        InitializeStatusPanel();

        // 시뮬레이션 시작
        data_processor->Start();
        data_simulator->Start();
    }

    void OnShutdown() override {
        data_simulator.reset();
        data_processor.reset();
    }

    void OnUpdate(float delta_time) override {
        // 웨이퍼 맵 업데이트 (시뮬레이션)
        UpdateWaferHeatmap();
    }

    void OnRender() override {
        RenderMainMenuBar();
        SetupDockSpace();

        if (show_charts) RenderChartsWindow();
        if (show_gauges) RenderGaugesWindow();
        if (show_heatmap) RenderHeatmapWindow();
        if (show_status) status_panel->Render();
        if (show_performance) RenderPerformanceWindow();
    }

private:
    void InitializeCharts() {
        // 주요 센서별 차트 생성
        const std::vector<std::string> sensor_names = {
            "Chamber Pressure", "RF Power", "Gas Flow Rate",
            "Substrate Temperature", "Plasma Density", "Voltage"
        };

        const std::vector<ImVec4> colors = {
            ImVec4(0.0f, 1.0f, 1.0f, 1.0f),  // Cyan
            ImVec4(1.0f, 0.0f, 1.0f, 1.0f),  // Magenta
            ImVec4(0.0f, 1.0f, 0.0f, 1.0f),  // Green
            ImVec4(1.0f, 0.5f, 0.0f, 1.0f),  // Orange
            ImVec4(1.0f, 1.0f, 0.0f, 1.0f),  // Yellow
            ImVec4(0.5f, 0.5f, 1.0f, 1.0f)   // Light Blue
        };

        for (size_t i = 0; i < sensor_names.size(); ++i) {
            auto chart = std::make_unique<UI::RealtimeChart>(sensor_names[i], 1000);
            chart->SetLineColor(colors[i]);
            chart->SetAutoScale(true);
            charts[sensor_names[i]] = std::move(chart);
        }
    }

    void InitializeGauges() {
        // 중요 파라미터별 게이지 생성
        auto pressure_gauge = std::make_unique<UI::CircularGauge>("Pressure (Torr)", 0.0f, 0.1f);
        pressure_gauge->SetThresholds(0.07f, 0.09f);
        pressure_gauge->SetSize(60.0f, 10.0f);
        gauges["pressure"] = std::move(pressure_gauge);

        auto temperature_gauge = std::make_unique<UI::CircularGauge>("Temperature (°C)", 0.0f, 1000.0f);
        temperature_gauge->SetThresholds(700.0f, 900.0f);
        temperature_gauge->SetSize(60.0f, 10.0f);
        gauges["temperature"] = std::move(temperature_gauge);

        auto power_gauge = std::make_unique<UI::CircularGauge>("RF Power (W)", 0.0f, 2000.0f);
        power_gauge->SetThresholds(1400.0f, 1800.0f);
        power_gauge->SetSize(60.0f, 10.0f);
        gauges["power"] = std::move(power_gauge);
    }

    void InitializeHeatmap() {
        wafer_heatmap = std::make_unique<UI::Heatmap>("Wafer Temperature Map", 32, 32);
        wafer_heatmap->SetRange(200.0f, 800.0f);
    }

    void InitializeStatusPanel() {
        status_panel = std::make_unique<UI::EquipmentStatusPanel>("Equipment Status");

        // 초기 장비 상태 설정
        using namespace UI;
        status_panel->UpdateEquipmentStatus("CVD-Chamber-01", {
            EquipmentState::Running, "PECVD SiO2 deposition in progress", {}, 87.3f, 156, false
        });

        status_panel->UpdateEquipmentStatus("PVD-Chamber-02", {
            EquipmentState::Running, "Al sputtering - Wafer #4567", {}, 92.1f, 234, false
        });

        status_panel->UpdateEquipmentStatus("ETCH-Chamber-03", {
            EquipmentState::Idle, "Ready for next recipe", {}, 0.0f, 0, false
        });

        status_panel->UpdateEquipmentStatus("CMP-Station-04", {
            EquipmentState::Maintenance, "Preventive maintenance cycle", {}, 0.0f, 0, false
        });
    }

    void InitializeWaferMap() {
        // 웨이퍼 온도 맵 초기화 (원형 패턴)
        const float center_x = 16.0f;
        const float center_y = 16.0f;
        const float max_radius = 15.0f;

        for (int y = 0; y < 32; ++y) {
            for (int x = 0; x < 32; ++x) {
                float dx = x - center_x;
                float dy = y - center_y;
                float distance = std::sqrt(dx*dx + dy*dy);

                if (distance <= max_radius) {
                    // 중심에서 가장자리로 갈수록 온도 감소
                    float normalized_distance = distance / max_radius;
                    wafer_temperature_map[y][x] = 600.0f - normalized_distance * 200.0f;
                } else {
                    wafer_temperature_map[y][x] = 300.0f; // 웨이퍼 외부
                }
            }
        }
    }

    void OnDataProcessed(const ProcessData& data) {
        std::lock_guard<std::mutex> lock(data_mutex);
        latest_data = data;

        // 차트 업데이트
        if (data.sensor_values.size() >= 6) {
            charts["Chamber Pressure"]->AddDataPoint(data.sensor_values[0]);
            charts["RF Power"]->AddDataPoint(data.sensor_values[1]);
            charts["Gas Flow Rate"]->AddDataPoint(data.sensor_values[2]);
            charts["Substrate Temperature"]->AddDataPoint(data.sensor_values[3]);
            charts["Plasma Density"]->AddDataPoint(data.sensor_values[4]);
            charts["Voltage"]->AddDataPoint(data.sensor_values[5]);

            // 게이지 업데이트
            gauges["pressure"]->SetValue(data.sensor_values[0] / 1000.0f); // mTorr to Torr
            gauges["temperature"]->SetValue(data.sensor_values[3]);
            gauges["power"]->SetValue(data.sensor_values[1]);
        }
    }

    void UpdateWaferHeatmap() {
        // 웨이퍼 온도 맵 동적 업데이트 (시뮬레이션)
        static float time_accumulator = 0.0f;
        time_accumulator += ImGui::GetIO().DeltaTime;

        if (time_accumulator >= 0.1f) { // 100ms마다 업데이트
            std::vector<std::vector<float>> heatmap_data(32, std::vector<float>(32));

            for (int y = 0; y < 32; ++y) {
                for (int x = 0; x < 32; ++x) {
                    // 시간에 따른 온도 변화 시뮬레이션
                    float base_temp = wafer_temperature_map[y][x];
                    float variation = 10.0f * std::sin(time_accumulator * 0.5f + x * 0.1f + y * 0.1f);
                    heatmap_data[y][x] = base_temp + variation;
                }
            }

            wafer_heatmap->SetData(heatmap_data);
            time_accumulator = 0.0f;
        }
    }

    void RenderMainMenuBar() {
        if (ImGui::BeginMainMenuBar()) {
            if (ImGui::BeginMenu("View")) {
                ImGui::MenuItem("Real-time Charts", nullptr, &show_charts);
                ImGui::MenuItem("Gauge Panel", nullptr, &show_gauges);
                ImGui::MenuItem("Wafer Heatmap", nullptr, &show_heatmap);
                ImGui::MenuItem("Equipment Status", nullptr, &show_status);
                ImGui::MenuItem("Performance Metrics", nullptr, &show_performance);
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("Control")) {
                if (ImGui::MenuItem("Start Process")) {
                    // 프로세스 시작 로직
                }
                if (ImGui::MenuItem("Stop Process")) {
                    // 프로세스 중지 로직
                }
                if (ImGui::MenuItem("Emergency Stop")) {
                    // 비상 정지 로직
                }
                ImGui::EndMenu();
            }

            ImGui::EndMainMenuBar();
        }
    }

    void SetupDockSpace() {
        static bool dockspace_open = true;
        static ImGuiDockNodeFlags dockspace_flags = ImGuiDockNodeFlags_None;

        ImGuiWindowFlags window_flags = ImGuiWindowFlags_MenuBar | ImGuiWindowFlags_NoDocking;
        ImGuiViewport* viewport = ImGui::GetMainViewport();
        ImGui::SetNextWindowPos(viewport->Pos);
        ImGui::SetNextWindowSize(viewport->Size);
        ImGui::SetNextWindowViewport(viewport->ID);

        window_flags |= ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoCollapse;
        window_flags |= ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoMove;
        window_flags |= ImGuiWindowFlags_NoBringToFrontOnFocus | ImGuiWindowFlags_NoNavFocus;

        ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, 0.0f);
        ImGui::PushStyleVar(ImGuiStyleVar_WindowBorderSize, 0.0f);
        ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0.0f, 0.0f));

        ImGui::Begin("DockSpace", &dockspace_open, window_flags);
        ImGui::PopStyleVar(3);

        ImGuiIO& io = ImGui::GetIO();
        if (io.ConfigFlags & ImGuiConfigFlags_DockingEnable) {
            ImGuiID dockspace_id = ImGui::GetID("MainDockSpace");
            ImGui::DockSpace(dockspace_id, ImVec2(0.0f, 0.0f), dockspace_flags);
        }

        ImGui::End();
    }

    void RenderChartsWindow() {
        if (ImGui::Begin("Real-time Sensor Data", &show_charts)) {
            // 센서 선택 콤보박스
            const char* sensor_names[] = {
                "Chamber Pressure", "RF Power", "Gas Flow Rate",
                "Substrate Temperature", "Plasma Density", "Voltage"
            };

            ImGui::Combo("Selected Sensor", &selected_chart_sensor, sensor_names, 6);

            // 선택된 센서의 대형 차트
            if (selected_chart_sensor < 6) {
                std::string sensor_name = sensor_names[selected_chart_sensor];
                if (charts.find(sensor_name) != charts.end()) {
                    charts[sensor_name]->Render(ImVec2(-1, 200));
                }
            }

            ImGui::Separator();

            // 모든 센서의 작은 차트들
            if (ImGui::BeginChild("Mini Charts", ImVec2(0, 0), true)) {
                int chart_count = 0;
                float chart_width = ImGui::GetContentRegionAvail().x / 3.0f - 10.0f;

                for (auto& [name, chart] : charts) {
                    if (chart_count % 3 != 0) ImGui::SameLine();

                    chart->Render(ImVec2(chart_width, 120));
                    chart_count++;
                }
            }
            ImGui::EndChild();
        }
        ImGui::End();
    }

    void RenderGaugesWindow() {
        if (ImGui::Begin("Critical Parameters", &show_gauges)) {
            // 게이지들을 격자로 배열
            int gauge_count = 0;
            for (auto& [name, gauge] : gauges) {
                if (gauge_count % 3 != 0) ImGui::SameLine();

                if (ImGui::BeginChild(name.c_str(), ImVec2(150, 180), true)) {
                    gauge->Render();
                }
                ImGui::EndChild();
                gauge_count++;
            }
        }
        ImGui::End();
    }

    void RenderHeatmapWindow() {
        if (ImGui::Begin("Wafer Temperature Distribution", &show_heatmap)) {
            wafer_heatmap->Render(ImVec2(-1, -1));
        }
        ImGui::End();
    }

    void RenderPerformanceWindow() {
        if (ImGui::Begin("System Performance", &show_performance)) {
            // 데이터 처리 성능
            ImGui::Text("Data Processing Performance:");
            ImGui::Text("Processed Samples: %llu", data_processor->GetProcessedCount());
            ImGui::Text("Dropped Samples: %llu", data_processor->GetDroppedCount());
            ImGui::Text("Processing Rate: %.1f samples/sec", data_processor->GetProcessingRate());
            ImGui::Text("Queue Size: %zu", data_processor->GetQueueSize());

            ImGui::Separator();

            // 애플리케이션 성능
            ImGui::Text("Application Performance:");
            ImGui::Text("Frame Time: %.3f ms", GetFrameTime() * 1000.0f);
            ImGui::Text("FPS: %.1f", GetFPS());

            // 메모리 사용량 (플랫폼별 구현 필요)
            ImGui::Text("Memory Usage: N/A MB");

            ImGui::Separator();

            // ImGUI 렌더링 통계
            ImGuiIO& io = ImGui::GetIO();
            ImGui::Text("Render Statistics:");
            ImGui::Text("Vertices: %d", io.MetricsRenderVertices);
            ImGui::Text("Indices: %d", io.MetricsRenderIndices);
            ImGui::Text("Windows: %d", io.MetricsRenderWindows);
        }
        ImGui::End();
    }
};

} // namespace SemiconductorHMI
```

#### 4.2 최종 메인 함수
```cpp
// src/main.cpp
#include "advanced_semiconductor_hmi.h"
#include <iostream>
#include <exception>

#ifdef _WIN32
#include <windows.h>
#endif

int main() {
    try {
        // 윈도우에서 콘솔 출력 활성화
        #ifdef _WIN32
        AllocConsole();
        freopen_s((FILE**)stdout, "CONOUT$", "w", stdout);
        freopen_s((FILE**)stderr, "CONOUT$", "w", stderr);
        #endif

        std::cout << "Starting Advanced Semiconductor HMI Application..." << std::endl;

        SemiconductorHMI::AdvancedSemiconductorHMI app;

        if (!app.Initialize()) {
            std::cerr << "Failed to initialize application" << std::endl;
            return -1;
        }

        std::cout << "Application initialized successfully. Starting main loop..." << std::endl;
        app.Run();

        std::cout << "Application terminated successfully." << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return -1;
    } catch (...) {
        std::cerr << "Unknown exception occurred" << std::endl;
        return -1;
    }

    return 0;
}
```

#### 4.3 빌드 스크립트
```cmake
# CMakeLists.txt (최종 버전)
cmake_minimum_required(VERSION 3.16)
project(AdvancedSemiconductorHMI VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 컴파일러별 최적화 옵션
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    if(MSVC)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /O2 /DNDEBUG")
    else()
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -DNDEBUG -march=native -flto")
    endif()
else()
    if(MSVC)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /Od /DDEBUG")
    else()
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -O0 -DDEBUG")
    endif()
endif()

# 패키지 찾기
find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)
find_package(Threads REQUIRED)

# ImGUI 및 의존성 설정
set(IMGUI_DIR ${CMAKE_CURRENT_SOURCE_DIR}/third_party/imgui)
set(GLAD_DIR ${CMAKE_CURRENT_SOURCE_DIR}/third_party/glad)

# 소스 파일들
set(PROJECT_SOURCES
    src/main.cpp
    src/hmi_application.cpp

    # ImGUI
    ${IMGUI_DIR}/imgui.cpp
    ${IMGUI_DIR}/imgui_demo.cpp
    ${IMGUI_DIR}/imgui_draw.cpp
    ${IMGUI_DIR}/imgui_tables.cpp
    ${IMGUI_DIR}/imgui_widgets.cpp
    ${IMGUI_DIR}/backends/imgui_impl_glfw.cpp
    ${IMGUI_DIR}/backends/imgui_impl_opengl3.cpp

    # GLAD
    ${GLAD_DIR}/src/glad.c
)

# 실행 파일 생성
add_executable(${PROJECT_NAME} ${PROJECT_SOURCES})

# 인클루드 디렉토리
target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${IMGUI_DIR}
    ${IMGUI_DIR}/backends
    ${GLAD_DIR}/include
)

# 링킹
target_link_libraries(${PROJECT_NAME}
    OpenGL::GL
    glfw
    Threads::Threads
)

# 컴파일러별 옵션
if(MSVC)
    target_compile_definitions(${PROJECT_NAME} PRIVATE _CRT_SECURE_NO_WARNINGS)
    target_compile_options(${PROJECT_NAME} PRIVATE /W4)
else()
    target_compile_options(${PROJECT_NAME} PRIVATE
        -Wall -Wextra -Wpedantic
        -Wno-unused-parameter
    )
endif()

# 리소스 복사
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/resources
     DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

# 설치
install(TARGETS ${PROJECT_NAME} RUNTIME DESTINATION bin)
install(DIRECTORY resources/ DESTINATION share/${PROJECT_NAME}/resources)
```

---

## 🎨 **심화 학습 (30분) - ImGUI 스타일링 및 테마 시스템**

### 5. 커스텀 스타일링 및 테마 구현

#### 5.1 ImGUI 스타일 시스템
```cpp
/*
ImGUI 스타일 시스템:
- ImGuiStyle 구조체를 통한 전역 스타일 설정
- 개별 위젯별 스타일 오버라이드
- 컬러 테마 및 크기 설정
- 애니메이션 및 트랜지션 효과
*/

namespace SemiconductorHMI {

// 산업용 테마 컬러 정의
struct IndustrialTheme {
    // 기본 배경 색상
    static constexpr ImU32 BACKGROUND_DARK = IM_COL32(25, 25, 25, 255);
    static constexpr ImU32 BACKGROUND_MEDIUM = IM_COL32(40, 40, 40, 255);
    static constexpr ImU32 BACKGROUND_LIGHT = IM_COL32(55, 55, 55, 255);

    // 액센트 컬러 (상태별)
    static constexpr ImU32 STATUS_NORMAL = IM_COL32(70, 130, 180, 255);    // Steel Blue
    static constexpr ImU32 STATUS_WARNING = IM_COL32(255, 165, 0, 255);    // Orange
    static constexpr ImU32 STATUS_ERROR = IM_COL32(220, 20, 60, 255);      // Crimson
    static constexpr ImU32 STATUS_SUCCESS = IM_COL32(50, 205, 50, 255);    // Lime Green

    // 텍스트 컬러
    static constexpr ImU32 TEXT_PRIMARY = IM_COL32(240, 240, 240, 255);
    static constexpr ImU32 TEXT_SECONDARY = IM_COL32(170, 170, 170, 255);
    static constexpr ImU32 TEXT_DISABLED = IM_COL32(100, 100, 100, 255);

    // 그래프 컬러 팔레트
    static constexpr std::array<ImU32, 8> GRAPH_COLORS = {{
        IM_COL32(31, 119, 180, 255),   // 블루
        IM_COL32(255, 127, 14, 255),   // 오렌지
        IM_COL32(44, 160, 44, 255),    // 그린
        IM_COL32(214, 39, 40, 255),    // 레드
        IM_COL32(148, 103, 189, 255),  // 퍼플
        IM_COL32(140, 86, 75, 255),    // 브라운
        IM_COL32(227, 119, 194, 255),  // 핑크
        IM_COL32(127, 127, 127, 255)   // 그레이
    }};
};

// 고급 스타일 매니저
class StyleManager {
private:
    ImGuiStyle default_style_;
    std::unordered_map<std::string, ImGuiStyle> custom_styles_;
    std::string current_theme_;

    // 애니메이션 상태
    struct AnimationState {
        float target_value;
        float current_value;
        float animation_speed;
        bool is_animating;
    };

    std::unordered_map<std::string, AnimationState> animations_;

public:
    StyleManager() {
        default_style_ = ImGui::GetStyle();
        current_theme_ = "Industrial";
        SetupIndustrialTheme();
    }

    // 산업용 테마 설정
    void SetupIndustrialTheme() {
        ImGuiStyle& style = ImGui::GetStyle();

        // 색상 설정
        style.Colors[ImGuiCol_Text] = ImVec4(0.94f, 0.94f, 0.94f, 1.00f);
        style.Colors[ImGuiCol_TextDisabled] = ImVec4(0.39f, 0.39f, 0.39f, 1.00f);
        style.Colors[ImGuiCol_WindowBg] = ImVec4(0.10f, 0.10f, 0.10f, 0.94f);
        style.Colors[ImGuiCol_ChildBg] = ImVec4(0.16f, 0.16f, 0.16f, 1.00f);
        style.Colors[ImGuiCol_PopupBg] = ImVec4(0.08f, 0.08f, 0.08f, 0.94f);
        style.Colors[ImGuiCol_Border] = ImVec4(0.22f, 0.22f, 0.22f, 0.50f);
        style.Colors[ImGuiCol_BorderShadow] = ImVec4(0.00f, 0.00f, 0.00f, 0.00f);
        style.Colors[ImGuiCol_FrameBg] = ImVec4(0.16f, 0.29f, 0.48f, 0.54f);
        style.Colors[ImGuiCol_FrameBgHovered] = ImVec4(0.26f, 0.59f, 0.98f, 0.40f);
        style.Colors[ImGuiCol_FrameBgActive] = ImVec4(0.26f, 0.59f, 0.98f, 0.67f);
        style.Colors[ImGuiCol_TitleBg] = ImVec4(0.04f, 0.04f, 0.04f, 1.00f);
        style.Colors[ImGuiCol_TitleBgActive] = ImVec4(0.16f, 0.29f, 0.48f, 1.00f);
        style.Colors[ImGuiCol_TitleBgCollapsed] = ImVec4(0.00f, 0.00f, 0.00f, 0.51f);
        style.Colors[ImGuiCol_MenuBarBg] = ImVec4(0.14f, 0.14f, 0.14f, 1.00f);
        style.Colors[ImGuiCol_ScrollbarBg] = ImVec4(0.02f, 0.02f, 0.02f, 0.53f);
        style.Colors[ImGuiCol_ScrollbarGrab] = ImVec4(0.31f, 0.31f, 0.31f, 1.00f);
        style.Colors[ImGuiCol_ScrollbarGrabHovered] = ImVec4(0.41f, 0.41f, 0.41f, 1.00f);
        style.Colors[ImGuiCol_ScrollbarGrabActive] = ImVec4(0.51f, 0.51f, 0.51f, 1.00f);
        style.Colors[ImGuiCol_CheckMark] = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
        style.Colors[ImGuiCol_SliderGrab] = ImVec4(0.24f, 0.52f, 0.88f, 1.00f);
        style.Colors[ImGuiCol_SliderGrabActive] = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
        style.Colors[ImGuiCol_Button] = ImVec4(0.26f, 0.59f, 0.98f, 0.40f);
        style.Colors[ImGuiCol_ButtonHovered] = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
        style.Colors[ImGuiCol_ButtonActive] = ImVec4(0.06f, 0.53f, 0.98f, 1.00f);
        style.Colors[ImGuiCol_Header] = ImVec4(0.26f, 0.59f, 0.98f, 0.31f);
        style.Colors[ImGuiCol_HeaderHovered] = ImVec4(0.26f, 0.59f, 0.98f, 0.80f);
        style.Colors[ImGuiCol_HeaderActive] = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
        style.Colors[ImGuiCol_Separator] = style.Colors[ImGuiCol_Border];
        style.Colors[ImGuiCol_SeparatorHovered] = ImVec4(0.10f, 0.40f, 0.75f, 0.78f);
        style.Colors[ImGuiCol_SeparatorActive] = ImVec4(0.10f, 0.40f, 0.75f, 1.00f);
        style.Colors[ImGuiCol_ResizeGrip] = ImVec4(0.26f, 0.59f, 0.98f, 0.25f);
        style.Colors[ImGuiCol_ResizeGripHovered] = ImVec4(0.26f, 0.59f, 0.98f, 0.67f);
        style.Colors[ImGuiCol_ResizeGripActive] = ImVec4(0.26f, 0.59f, 0.98f, 0.95f);
        style.Colors[ImGuiCol_Tab] = ImLerp(style.Colors[ImGuiCol_Header], style.Colors[ImGuiCol_TitleBgActive], 0.80f);
        style.Colors[ImGuiCol_TabHovered] = style.Colors[ImGuiCol_HeaderHovered];
        style.Colors[ImGuiCol_TabActive] = ImLerp(style.Colors[ImGuiCol_HeaderActive], style.Colors[ImGuiCol_TitleBgActive], 0.60f);
        style.Colors[ImGuiCol_TabUnfocused] = ImLerp(style.Colors[ImGuiCol_Tab], style.Colors[ImGuiCol_TitleBg], 0.80f);
        style.Colors[ImGuiCol_TabUnfocusedActive] = ImLerp(style.Colors[ImGuiCol_TabActive], style.Colors[ImGuiCol_TitleBg], 0.40f);
        style.Colors[ImGuiCol_PlotLines] = ImVec4(0.61f, 0.61f, 0.61f, 1.00f);
        style.Colors[ImGuiCol_PlotLinesHovered] = ImVec4(1.00f, 0.43f, 0.35f, 1.00f);
        style.Colors[ImGuiCol_PlotHistogram] = ImVec4(0.90f, 0.70f, 0.00f, 1.00f);
        style.Colors[ImGuiCol_PlotHistogramHovered] = ImVec4(1.00f, 0.60f, 0.00f, 1.00f);
        style.Colors[ImGuiCol_TextSelectedBg] = ImVec4(0.26f, 0.59f, 0.98f, 0.35f);
        style.Colors[ImGuiCol_DragDropTarget] = ImVec4(1.00f, 1.00f, 0.00f, 0.90f);
        style.Colors[ImGuiCol_NavHighlight] = style.Colors[ImGuiCol_HeaderHovered];
        style.Colors[ImGuiCol_NavWindowingHighlight] = ImVec4(1.00f, 1.00f, 1.00f, 0.70f);
        style.Colors[ImGuiCol_NavWindowingDimBg] = ImVec4(0.80f, 0.80f, 0.80f, 0.35f);
        style.Colors[ImGuiCol_ModalWindowDimBg] = ImVec4(0.80f, 0.80f, 0.80f, 0.35f);

        // 크기 및 간격 설정
        style.WindowPadding = ImVec2(8, 8);
        style.FramePadding = ImVec2(5, 2);
        style.CellPadding = ImVec2(6, 6);
        style.ItemSpacing = ImVec2(6, 6);
        style.ItemInnerSpacing = ImVec2(6, 6);
        style.TouchExtraPadding = ImVec2(0, 0);
        style.IndentSpacing = 25;
        style.ScrollbarSize = 15;
        style.GrabMinSize = 10;

        // 둥근 모서리 설정
        style.WindowRounding = 7.0f;
        style.ChildRounding = 4.0f;
        style.FrameRounding = 3.0f;
        style.PopupRounding = 4.0f;
        style.ScrollbarRounding = 9.0f;
        style.GrabRounding = 3.0f;
        style.LogSliderDeadzone = 4.0f;
        style.TabRounding = 4.0f;

        // 경계선 설정
        style.WindowBorderSize = 1.0f;
        style.ChildBorderSize = 1.0f;
        style.PopupBorderSize = 1.0f;
        style.FrameBorderSize = 0.0f;
        style.TabBorderSize = 0.0f;

        // 기타 설정
        style.WindowTitleAlign = ImVec2(0.0f, 0.5f);
        style.WindowMenuButtonPosition = ImGuiDir_Left;
        style.ColorButtonPosition = ImGuiDir_Right;
        style.ButtonTextAlign = ImVec2(0.5f, 0.5f);
        style.SelectableTextAlign = ImVec2(0.0f, 0.0f);
        style.DisplaySafeAreaPadding = ImVec2(3, 3);
    }

    // 애니메이션 효과가 적용된 컬러 전환
    ImVec4 AnimateColor(const std::string& id, const ImVec4& target_color, float speed = 5.0f) {
        auto it = animations_.find(id);
        if (it == animations_.end()) {
            animations_[id] = {1.0f, 0.0f, speed, true};
            it = animations_.find(id);
        }

        AnimationState& anim = it->second;

        if (anim.is_animating) {
            float delta_time = ImGui::GetIO().DeltaTime;
            anim.current_value += (anim.target_value - anim.current_value) * anim.animation_speed * delta_time;

            if (std::abs(anim.target_value - anim.current_value) < 0.01f) {
                anim.current_value = anim.target_value;
                anim.is_animating = false;
            }
        }

        // 현재 색상과 목표 색상 사이를 보간
        ImVec4 current_color = ImGui::GetStyle().Colors[ImGuiCol_Button]; // 기본 색상
        return ImVec4(
            current_color.x + (target_color.x - current_color.x) * anim.current_value,
            current_color.y + (target_color.y - current_color.y) * anim.current_value,
            current_color.z + (target_color.z - current_color.z) * anim.current_value,
            current_color.w + (target_color.w - current_color.w) * anim.current_value
        );
    }

    // 상태별 컬러 반환
    static ImVec4 GetStatusColor(int status) {
        switch (status) {
            case 0: return ImColor(IndustrialTheme::STATUS_NORMAL);
            case 1: return ImColor(IndustrialTheme::STATUS_WARNING);
            case 2: return ImColor(IndustrialTheme::STATUS_ERROR);
            case 3: return ImColor(IndustrialTheme::STATUS_SUCCESS);
            default: return ImColor(IndustrialTheme::TEXT_SECONDARY);
        }
    }

    // 그래프 컬러 반환
    static ImVec4 GetGraphColor(size_t index) {
        return ImColor(IndustrialTheme::GRAPH_COLORS[index % IndustrialTheme::GRAPH_COLORS.size()]);
    }
};

// 커스텀 렌더링 유틸리티
class RenderUtils {
public:
    // 그라디언트 배경 렌더링
    static void DrawGradientRect(const ImVec2& min, const ImVec2& max,
                               ImU32 color_top, ImU32 color_bottom) {
        ImDrawList* draw_list = ImGui::GetWindowDrawList();
        draw_list->AddRectFilledMultiColor(min, max, color_top, color_top, color_bottom, color_bottom);
    }

    // 그림자 효과
    static void DrawShadowRect(const ImVec2& min, const ImVec2& max,
                             float rounding, ImU32 shadow_color = IM_COL32(0, 0, 0, 80)) {
        ImDrawList* draw_list = ImGui::GetWindowDrawList();
        ImVec2 shadow_min = ImVec2(min.x + 2, min.y + 2);
        ImVec2 shadow_max = ImVec2(max.x + 2, max.y + 2);
        draw_list->AddRectFilled(shadow_min, shadow_max, shadow_color, rounding);
    }

    // LED 스타일 인디케이터
    static void DrawLED(const ImVec2& center, float radius, bool is_on, ImU32 on_color = IM_COL32(0, 255, 0, 255)) {
        ImDrawList* draw_list = ImGui::GetWindowDrawList();
        ImU32 color = is_on ? on_color : IM_COL32(50, 50, 50, 255);
        draw_list->AddCircleFilled(center, radius, color);

        if (is_on) {
            // 글로우 효과
            for (int i = 1; i <= 3; i++) {
                ImU32 glow_color = IM_COL32(
                    (on_color >> IM_COL32_R_SHIFT) & 0xFF,
                    (on_color >> IM_COL32_G_SHIFT) & 0xFF,
                    (on_color >> IM_COL32_B_SHIFT) & 0xFF,
                    80 / i
                );
                draw_list->AddCircle(center, radius + i, glow_color, 0, 2.0f);
            }
        }
    }

    // 3D 스타일 버튼 효과
    static bool Button3D(const char* label, const ImVec2& size = ImVec2(0, 0)) {
        ImGui::PushStyleVar(ImGuiStyleVar_FrameRounding, 6.0f);
        ImGui::PushStyleVar(ImGuiStyleVar_FramePadding, ImVec2(8, 6));

        ImVec2 pos = ImGui::GetCursorScreenPos();
        ImVec2 button_size = size;
        if (button_size.x == 0) button_size.x = ImGui::CalcTextSize(label).x + 16;
        if (button_size.y == 0) button_size.y = ImGui::GetTextLineHeight() + 12;

        // 그림자 그리기
        DrawShadowRect(pos, ImVec2(pos.x + button_size.x, pos.y + button_size.y), 6.0f);

        bool result = ImGui::Button(label, button_size);

        ImGui::PopStyleVar(2);
        return result;
    }
};

} // namespace SemiconductorHMI
```

#### 5.2 다이나믹 테마 전환 시스템
```cpp
// 동적 테마 관리 클래스
class ThemeManager {
private:
    enum class Theme {
        INDUSTRIAL_DARK,
        INDUSTRIAL_LIGHT,
        HIGH_CONTRAST,
        COLORBLIND_FRIENDLY
    };

    Theme current_theme_;
    float transition_progress_;
    bool is_transitioning_;

    // 테마별 컬러 팔레트
    struct ThemePalette {
        std::array<ImVec4, ImGuiCol_COUNT> colors;
        std::string name;
    };

    std::unordered_map<Theme, ThemePalette> theme_palettes_;

public:
    ThemeManager() : current_theme_(Theme::INDUSTRIAL_DARK),
                    transition_progress_(0.0f),
                    is_transitioning_(false) {
        InitializeThemes();
    }

    void InitializeThemes() {
        // 산업용 다크 테마
        auto& dark_theme = theme_palettes_[Theme::INDUSTRIAL_DARK];
        dark_theme.name = "Industrial Dark";
        // ... 컬러 설정

        // 산업용 라이트 테마
        auto& light_theme = theme_palettes_[Theme::INDUSTRIAL_LIGHT];
        light_theme.name = "Industrial Light";
        light_theme.colors[ImGuiCol_WindowBg] = ImVec4(0.95f, 0.95f, 0.95f, 1.00f);
        light_theme.colors[ImGuiCol_Text] = ImVec4(0.10f, 0.10f, 0.10f, 1.00f);
        // ... 추가 컬러 설정

        // 고대비 테마 (접근성)
        auto& high_contrast = theme_palettes_[Theme::HIGH_CONTRAST];
        high_contrast.name = "High Contrast";
        high_contrast.colors[ImGuiCol_WindowBg] = ImVec4(0.00f, 0.00f, 0.00f, 1.00f);
        high_contrast.colors[ImGuiCol_Text] = ImVec4(1.00f, 1.00f, 1.00f, 1.00f);
        high_contrast.colors[ImGuiCol_Button] = ImVec4(1.00f, 1.00f, 0.00f, 1.00f);
        // ... 추가 설정

        // 색맹 친화적 테마
        auto& colorblind = theme_palettes_[Theme::COLORBLIND_FRIENDLY];
        colorblind.name = "Colorblind Friendly";
        // Deuteranopia (녹색맹)를 고려한 컬러 팔레트
        colorblind.colors[ImGuiCol_Button] = ImVec4(0.0f, 0.4f, 0.8f, 1.0f);     // 파랑
        colorblind.colors[ImGuiCol_ButtonHovered] = ImVec4(1.0f, 0.6f, 0.0f, 1.0f); // 오렌지
        // ... 추가 설정
    }

    void SetTheme(Theme theme) {
        if (theme != current_theme_ && !is_transitioning_) {
            current_theme_ = theme;
            is_transitioning_ = true;
            transition_progress_ = 0.0f;
        }
    }

    void Update() {
        if (is_transitioning_) {
            transition_progress_ += ImGui::GetIO().DeltaTime * 2.0f; // 2초간 전환

            if (transition_progress_ >= 1.0f) {
                transition_progress_ = 1.0f;
                is_transitioning_ = false;
            }

            ApplyThemeTransition();
        }
    }

    void ApplyThemeTransition() {
        ImGuiStyle& style = ImGui::GetStyle();
        const auto& target_palette = theme_palettes_[current_theme_];

        // 부드러운 컬러 전환
        for (int i = 0; i < ImGuiCol_COUNT; i++) {
            ImVec4 current_color = style.Colors[i];
            ImVec4 target_color = target_palette.colors[i];

            style.Colors[i] = ImVec4(
                current_color.x + (target_color.x - current_color.x) * transition_progress_,
                current_color.y + (target_color.y - current_color.y) * transition_progress_,
                current_color.z + (target_color.z - current_color.z) * transition_progress_,
                current_color.w + (target_color.w - current_color.w) * transition_progress_
            );
        }
    }

    void ShowThemeSelector() {
        if (ImGui::BeginCombo("Theme", theme_palettes_[current_theme_].name.c_str())) {
            for (const auto& [theme, palette] : theme_palettes_) {
                bool is_selected = (current_theme_ == theme);
                if (ImGui::Selectable(palette.name.c_str(), is_selected)) {
                    SetTheme(theme);
                }
                if (is_selected) {
                    ImGui::SetItemDefaultFocus();
                }
            }
            ImGui::EndCombo();
        }
    }
};
```

### 6. 고급 위젯 및 컴포넌트 라이브러리

#### 6.1 산업용 계측기 위젯 컬렉션
```cpp
// 고급 산업용 위젯 라이브러리
namespace IndustrialWidgets {

// 디지털 디스플레이 스타일 숫자 표시기
class DigitalDisplay {
private:
    std::string format_string_;
    ImVec4 digit_color_;
    ImVec4 background_color_;
    float font_scale_;
    bool show_leading_zeros_;

public:
    DigitalDisplay(const std::string& format = "%.2f")
        : format_string_(format)
        , digit_color_(0.0f, 1.0f, 0.0f, 1.0f)  // 그린 LED 스타일
        , background_color_(0.05f, 0.05f, 0.05f, 1.0f)
        , font_scale_(1.5f)
        , show_leading_zeros_(true) {}

    void Render(const char* label, double value, const ImVec2& size = ImVec2(120, 40)) {
        ImGui::PushStyleVar(ImGuiStyleVar_FrameRounding, 2.0f);
        ImGui::PushStyleColor(ImGuiCol_FrameBg, background_color_);

        ImGui::BeginChild(label, size, true, ImGuiWindowFlags_NoScrollbar);

        // 배경 렌더링
        ImDrawList* draw_list = ImGui::GetWindowDrawList();
        ImVec2 p_min = ImGui::GetWindowPos();
        ImVec2 p_max = ImVec2(p_min.x + size.x, p_min.y + size.y);

        // 내부 그림자 효과
        draw_list->AddRectFilled(p_min, p_max, ImColor(0.02f, 0.02f, 0.02f, 1.0f), 2.0f);
        draw_list->AddRect(ImVec2(p_min.x + 1, p_min.y + 1),
                          ImVec2(p_max.x - 1, p_max.y - 1),
                          ImColor(0.1f, 0.1f, 0.1f, 1.0f), 2.0f);

        // 텍스트 렌더링
        char buffer[64];
        snprintf(buffer, sizeof(buffer), format_string_.c_str(), value);

        ImGui::PushStyleColor(ImGuiCol_Text, digit_color_);

        // 중앙 정렬
        ImVec2 text_size = ImGui::CalcTextSize(buffer);
        ImVec2 text_pos = ImVec2(
            p_min.x + (size.x - text_size.x) * 0.5f,
            p_min.y + (size.y - text_size.y) * 0.5f
        );

        ImGui::SetCursorScreenPos(text_pos);
        ImGui::Text("%s", buffer);

        ImGui::PopStyleColor();
        ImGui::EndChild();
        ImGui::PopStyleColor();
        ImGui::PopStyleVar();

        // 레이블 표시
        if (strlen(label) > 0) {
            ImGui::SameLine();
            ImGui::Text(" %s", label);
        }
    }

    void SetDigitColor(const ImVec4& color) { digit_color_ = color; }
    void SetBackgroundColor(const ImVec4& color) { background_color_ = color; }
    void SetFormat(const std::string& format) { format_string_ = format; }
};

// 멀티 채널 오실로스코프 위젯
class Oscilloscope {
private:
    struct Channel {
        std::vector<float> data;
        ImVec4 color;
        bool enabled;
        float scale;
        float offset;
        std::string label;

        Channel() : color(1.0f, 1.0f, 1.0f, 1.0f), enabled(true),
                   scale(1.0f), offset(0.0f), label("CH") {}
    };

    std::array<Channel, 8> channels_;
    size_t buffer_size_;
    float time_scale_;
    float voltage_scale_;
    bool auto_scale_;
    ImVec2 grid_spacing_;

public:
    Oscilloscope(size_t buffer_size = 1000)
        : buffer_size_(buffer_size)
        , time_scale_(1.0f)
        , voltage_scale_(1.0f)
        , auto_scale_(true)
        , grid_spacing_(50.0f, 25.0f) {

        for (size_t i = 0; i < channels_.size(); i++) {
            channels_[i].data.reserve(buffer_size_);
            channels_[i].color = StyleManager::GetGraphColor(i);
            channels_[i].label = "CH" + std::to_string(i + 1);
        }
    }

    void AddDataPoint(size_t channel, float value) {
        if (channel >= channels_.size()) return;

        auto& ch = channels_[channel];
        ch.data.push_back(value);

        if (ch.data.size() > buffer_size_) {
            ch.data.erase(ch.data.begin());
        }
    }

    void Render(const char* label, const ImVec2& size = ImVec2(400, 300)) {
        if (!ImGui::BeginChild(label, size, true)) {
            ImGui::EndChild();
            return;
        }

        ImDrawList* draw_list = ImGui::GetWindowDrawList();
        ImVec2 canvas_p0 = ImGui::GetCursorScreenPos();
        ImVec2 canvas_sz = ImGui::GetContentRegionAvail();
        ImVec2 canvas_p1 = ImVec2(canvas_p0.x + canvas_sz.x, canvas_p0.y + canvas_sz.y);

        // 배경
        draw_list->AddRectFilled(canvas_p0, canvas_p1, IM_COL32(10, 10, 10, 255));

        // 그리드 그리기
        DrawGrid(draw_list, canvas_p0, canvas_p1);

        // 채널 데이터 그리기
        for (size_t i = 0; i < channels_.size(); i++) {
            if (channels_[i].enabled && !channels_[i].data.empty()) {
                DrawChannel(draw_list, canvas_p0, canvas_sz, channels_[i]);
            }
        }

        // 측정값 오버레이
        DrawMeasurements(draw_list, canvas_p0, canvas_sz);

        ImGui::InvisibleButton("canvas", canvas_sz);
        ImGui::EndChild();

        // 컨트롤 패널
        ShowControlPanel();
    }

private:
    void DrawGrid(ImDrawList* draw_list, const ImVec2& p0, const ImVec2& p1) {
        ImU32 grid_color = IM_COL32(50, 50, 50, 255);

        // 세로 그리드
        for (float x = p0.x; x < p1.x; x += grid_spacing_.x) {
            draw_list->AddLine(ImVec2(x, p0.y), ImVec2(x, p1.y), grid_color);
        }

        // 가로 그리드
        for (float y = p0.y; y < p1.y; y += grid_spacing_.y) {
            draw_list->AddLine(ImVec2(p0.x, y), ImVec2(p1.x, y), grid_color);
        }

        // 중심축 (더 밝게)
        float center_y = p0.y + (p1.y - p0.y) * 0.5f;
        draw_list->AddLine(ImVec2(p0.x, center_y), ImVec2(p1.x, center_y),
                          IM_COL32(100, 100, 100, 255), 2.0f);
    }

    void DrawChannel(ImDrawList* draw_list, const ImVec2& canvas_pos,
                    const ImVec2& canvas_size, const Channel& channel) {
        if (channel.data.size() < 2) return;

        std::vector<ImVec2> points;
        points.reserve(channel.data.size());

        float x_step = canvas_size.x / static_cast<float>(channel.data.size() - 1);
        float y_center = canvas_pos.y + canvas_size.y * 0.5f;
        float y_scale = canvas_size.y * 0.4f * voltage_scale_ * channel.scale;

        for (size_t i = 0; i < channel.data.size(); i++) {
            float x = canvas_pos.x + i * x_step;
            float y = y_center - (channel.data[i] + channel.offset) * y_scale;
            points.emplace_back(x, y);
        }

        // 연결된 선으로 그리기
        for (size_t i = 0; i < points.size() - 1; i++) {
            draw_list->AddLine(points[i], points[i + 1], ImColor(channel.color), 2.0f);
        }

        // 채널 레이블
        draw_list->AddText(ImVec2(canvas_pos.x + 5, canvas_pos.y + 5),
                          ImColor(channel.color), channel.label.c_str());
    }

    void DrawMeasurements(ImDrawList* draw_list, const ImVec2& canvas_pos, const ImVec2& canvas_size) {
        // 측정 정보 표시 (RMS, 평균, 피크 등)
        ImVec2 info_pos = ImVec2(canvas_pos.x + canvas_size.x - 150, canvas_pos.y + 5);

        for (size_t i = 0; i < channels_.size(); i++) {
            if (!channels_[i].enabled || channels_[i].data.empty()) continue;

            // 통계 계산
            float min_val = *std::min_element(channels_[i].data.begin(), channels_[i].data.end());
            float max_val = *std::max_element(channels_[i].data.begin(), channels_[i].data.end());
            float avg_val = std::accumulate(channels_[i].data.begin(), channels_[i].data.end(), 0.0f) / channels_[i].data.size();

            char info_text[128];
            snprintf(info_text, sizeof(info_text), "%s: %.2f V (%.2f~%.2f)",
                    channels_[i].label.c_str(), avg_val, min_val, max_val);

            draw_list->AddText(ImVec2(info_pos.x, info_pos.y + i * 15),
                              ImColor(channels_[i].color), info_text);
        }
    }

    void ShowControlPanel() {
        if (ImGui::CollapsingHeader("Oscilloscope Controls")) {
            ImGui::Columns(2);

            // 시간축 제어
            ImGui::SliderFloat("Time Scale", &time_scale_, 0.1f, 10.0f);
            ImGui::SliderFloat("Voltage Scale", &voltage_scale_, 0.1f, 10.0f);
            ImGui::Checkbox("Auto Scale", &auto_scale_);

            ImGui::NextColumn();

            // 채널 제어
            for (size_t i = 0; i < 4; i++) { // 처음 4개 채널만 표시
                auto& ch = channels_[i];
                ImGui::PushID(static_cast<int>(i));

                ImGui::Checkbox(ch.label.c_str(), &ch.enabled);
                if (ch.enabled) {
                    ImGui::SameLine();
                    ImGui::ColorEdit3("", reinterpret_cast<float*>(&ch.color),
                                    ImGuiColorEditFlags_NoInputs | ImGuiColorEditFlags_NoLabel);

                    ImGui::SliderFloat("Scale", &ch.scale, 0.1f, 5.0f);
                    ImGui::SliderFloat("Offset", &ch.offset, -2.0f, 2.0f);
                }

                ImGui::PopID();
            }

            ImGui::Columns(1);
        }
    }
};

// 반도체 웨이퍼 맵 시각화 위젯
class WaferMap {
private:
    struct Die {
        int x, y;
        int bin_code;
        float value;
        bool is_edge;

        Die(int x = 0, int y = 0) : x(x), y(y), bin_code(1), value(0.0f), is_edge(false) {}
    };

    std::vector<std::vector<Die>> wafer_data_;
    int wafer_diameter_;
    int die_size_x_, die_size_y_;
    float zoom_level_;
    ImVec2 pan_offset_;
    std::unordered_map<int, ImVec4> bin_colors_;

public:
    WaferMap(int diameter = 300) : wafer_diameter_(diameter), die_size_x_(5), die_size_y_(5),
                                  zoom_level_(1.0f), pan_offset_(0, 0) {
        InitializeBinColors();
        GenerateWaferData();
    }

private:
    void InitializeBinColors() {
        bin_colors_[1] = ImVec4(0.2f, 0.8f, 0.2f, 1.0f);  // Pass - Green
        bin_colors_[2] = ImVec4(0.8f, 0.8f, 0.2f, 1.0f);  // Retest - Yellow
        bin_colors_[3] = ImVec4(0.8f, 0.4f, 0.2f, 1.0f);  // Fail1 - Orange
        bin_colors_[4] = ImVec4(0.8f, 0.2f, 0.2f, 1.0f);  // Fail2 - Red
        bin_colors_[0] = ImVec4(0.3f, 0.3f, 0.3f, 1.0f);  // No Test - Gray
    }

    void GenerateWaferData() {
        // 웨이퍼 데이터 생성 (원형 패턴)
        int radius = wafer_diameter_ / 2;
        int dies_per_radius = radius / std::max(die_size_x_, die_size_y_);

        wafer_data_.clear();
        wafer_data_.resize(dies_per_radius * 2 + 1);

        for (int i = 0; i < wafer_data_.size(); i++) {
            wafer_data_[i].resize(dies_per_radius * 2 + 1);

            for (int j = 0; j < wafer_data_[i].size(); j++) {
                int x = i - dies_per_radius;
                int y = j - dies_per_radius;

                wafer_data_[i][j] = Die(x, y);

                // 원형 웨이퍼 모양 생성
                float distance = std::sqrt(x * x + y * y);
                if (distance <= dies_per_radius) {
                    // 가장자리 다이 표시
                    if (distance > dies_per_radius * 0.9f) {
                        wafer_data_[i][j].is_edge = true;
                    }

                    // 랜덤 bin code 할당 (실제로는 테스트 결과)
                    if (distance <= dies_per_radius * 0.8f) {
                        wafer_data_[i][j].bin_code = (rand() % 10 < 8) ? 1 : (rand() % 4 + 2);
                    } else {
                        wafer_data_[i][j].bin_code = (rand() % 10 < 6) ? 1 : (rand() % 4 + 2);
                    }

                    wafer_data_[i][j].value = static_cast<float>(rand()) / RAND_MAX;
                } else {
                    wafer_data_[i][j].bin_code = 0; // 웨이퍼 밖
                }
            }
        }
    }

public:
    void Render(const char* label, const ImVec2& size = ImVec2(400, 400)) {
        if (!ImGui::BeginChild(label, size, true)) {
            ImGui::EndChild();
            return;
        }

        ImDrawList* draw_list = ImGui::GetWindowDrawList();
        ImVec2 canvas_p0 = ImGui::GetCursorScreenPos();
        ImVec2 canvas_sz = ImGui::GetContentRegionAvail();
        ImVec2 canvas_p1 = ImVec2(canvas_p0.x + canvas_sz.x, canvas_p0.y + canvas_sz.y);
        ImVec2 canvas_center = ImVec2(canvas_p0.x + canvas_sz.x * 0.5f, canvas_p0.y + canvas_sz.y * 0.5f);

        // 배경
        draw_list->AddRectFilled(canvas_p0, canvas_p1, IM_COL32(20, 20, 20, 255));

        // 웨이퍼 외곽 원 그리기
        float wafer_radius = std::min(canvas_sz.x, canvas_sz.y) * 0.4f * zoom_level_;
        draw_list->AddCircle(ImVec2(canvas_center.x + pan_offset_.x, canvas_center.y + pan_offset_.y),
                            wafer_radius, IM_COL32(100, 100, 100, 255), 0, 3.0f);

        // 다이들 그리기
        float die_size = wafer_radius / (wafer_data_.size() / 2.0f);

        for (size_t i = 0; i < wafer_data_.size(); i++) {
            for (size_t j = 0; j < wafer_data_[i].size(); j++) {
                const Die& die = wafer_data_[i][j];

                if (die.bin_code == 0) continue; // 웨이퍼 밖

                float die_x = canvas_center.x + pan_offset_.x + die.x * die_size;
                float die_y = canvas_center.y + pan_offset_.y + die.y * die_size;

                ImVec2 die_min = ImVec2(die_x - die_size * 0.4f, die_y - die_size * 0.4f);
                ImVec2 die_max = ImVec2(die_x + die_size * 0.4f, die_y + die_size * 0.4f);

                ImVec4 die_color = bin_colors_[die.bin_code];
                draw_list->AddRectFilled(die_min, die_max, ImColor(die_color), 1.0f);

                // 가장자리 다이 표시
                if (die.is_edge) {
                    draw_list->AddRect(die_min, die_max, IM_COL32(255, 255, 255, 100), 1.0f);
                }
            }
        }

        // 범례 그리기
        DrawLegend(draw_list, canvas_p0, canvas_sz);

        // 인터랙션 처리
        HandleInteraction(canvas_p0, canvas_sz);

        ImGui::EndChild();
    }

private:
    void DrawLegend(ImDrawList* draw_list, const ImVec2& canvas_pos, const ImVec2& canvas_size) {
        ImVec2 legend_pos = ImVec2(canvas_pos.x + 10, canvas_pos.y + 10);

        int y_offset = 0;
        for (const auto& [bin_code, color] : bin_colors_) {
            if (bin_code == 0) continue;

            ImVec2 color_rect_min = ImVec2(legend_pos.x, legend_pos.y + y_offset * 20);
            ImVec2 color_rect_max = ImVec2(legend_pos.x + 15, legend_pos.y + y_offset * 20 + 15);

            draw_list->AddRectFilled(color_rect_min, color_rect_max, ImColor(color));

            const char* bin_name = "";
            switch (bin_code) {
                case 1: bin_name = "Pass"; break;
                case 2: bin_name = "Retest"; break;
                case 3: bin_name = "Fail1"; break;
                case 4: bin_name = "Fail2"; break;
            }

            draw_list->AddText(ImVec2(legend_pos.x + 20, legend_pos.y + y_offset * 20),
                              IM_COL32(255, 255, 255, 255), bin_name);

            y_offset++;
        }
    }

    void HandleInteraction(const ImVec2& canvas_pos, const ImVec2& canvas_size) {
        ImGuiIO& io = ImGui::GetIO();

        // 마우스가 캔버스 위에 있는지 확인
        bool is_hovered = ImGui::IsItemHovered();

        if (is_hovered) {
            // 줌 처리
            if (io.MouseWheel != 0.0f) {
                zoom_level_ *= (1.0f + io.MouseWheel * 0.1f);
                zoom_level_ = std::clamp(zoom_level_, 0.1f, 5.0f);
            }

            // 패닝 처리
            if (ImGui::IsMouseDragging(ImGuiMouseButton_Left)) {
                pan_offset_.x += io.MouseDelta.x;
                pan_offset_.y += io.MouseDelta.y;
            }

            // 다이 정보 툴팁
            ImVec2 mouse_pos = io.MousePos;
            ImVec2 canvas_center = ImVec2(canvas_pos.x + canvas_size.x * 0.5f, canvas_pos.y + canvas_size.y * 0.5f);

            // 마우스 위치에 해당하는 다이 찾기
            float wafer_radius = std::min(canvas_size.x, canvas_size.y) * 0.4f * zoom_level_;
            float die_size = wafer_radius / (wafer_data_.size() / 2.0f);

            float rel_x = (mouse_pos.x - canvas_center.x - pan_offset_.x) / die_size;
            float rel_y = (mouse_pos.y - canvas_center.y - pan_offset_.y) / die_size;

            int die_i = static_cast<int>(rel_y + wafer_data_.size() / 2);
            int die_j = static_cast<int>(rel_x + wafer_data_[0].size() / 2);

            if (die_i >= 0 && die_i < wafer_data_.size() &&
                die_j >= 0 && die_j < wafer_data_[die_i].size() &&
                wafer_data_[die_i][die_j].bin_code != 0) {

                const Die& die = wafer_data_[die_i][die_j];

                ImGui::BeginTooltip();
                ImGui::Text("Die (%d, %d)", die.x, die.y);
                ImGui::Text("Bin: %d", die.bin_code);
                ImGui::Text("Value: %.3f", die.value);
                ImGui::EndTooltip();
            }
        }

        ImGui::InvisibleButton("wafer_canvas", canvas_size);
    }
};

} // namespace IndustrialWidgets
```

---

## 🎯 **성능 최적화 (30분) - 실시간 시스템 최적화 기법**

### 7. ImGUI 성능 최적화 전략

#### 7.1 렌더링 성능 최적화
```cpp
namespace PerformanceOptimization {

// 프레임 성능 모니터링 클래스
class PerformanceMonitor {
private:
    static constexpr size_t HISTORY_SIZE = 300; // 5초간 60FPS

    std::array<float, HISTORY_SIZE> frame_times_;
    std::array<float, HISTORY_SIZE> cpu_times_;
    std::array<float, HISTORY_SIZE> render_times_;
    size_t frame_index_;

    std::chrono::high_resolution_clock::time_point last_frame_time_;
    std::chrono::high_resolution_clock::time_point frame_start_time_;

    // 성능 통계
    struct PerformanceStats {
        float avg_fps;
        float min_fps;
        float max_fps;
        float avg_frame_time;
        float avg_cpu_time;
        float avg_render_time;
        size_t draw_calls;
        size_t vertices;
    } stats_;

public:
    PerformanceMonitor() : frame_index_(0) {
        frame_times_.fill(0.0f);
        cpu_times_.fill(0.0f);
        render_times_.fill(0.0f);
        last_frame_time_ = std::chrono::high_resolution_clock::now();
    }

    void BeginFrame() {
        frame_start_time_ = std::chrono::high_resolution_clock::now();

        // 이전 프레임 시간 계산
        auto current_time = frame_start_time_;
        float frame_time = std::chrono::duration<float>(current_time - last_frame_time_).count();

        frame_times_[frame_index_] = frame_time * 1000.0f; // ms 단위로 변환
        last_frame_time_ = current_time;

        frame_index_ = (frame_index_ + 1) % HISTORY_SIZE;
    }

    void MarkCPUEnd() {
        auto cpu_end = std::chrono::high_resolution_clock::now();
        float cpu_time = std::chrono::duration<float>(cpu_end - frame_start_time_).count();
        cpu_times_[frame_index_] = cpu_time * 1000.0f;
    }

    void EndFrame() {
        auto frame_end = std::chrono::high_resolution_clock::now();
        float render_time = std::chrono::duration<float>(frame_end - frame_start_time_).count();
        render_times_[frame_index_] = render_time * 1000.0f;

        UpdateStats();
    }

    void UpdateStats() {
        // 평균, 최소, 최대값 계산
        float sum_frame_time = 0.0f;
        float sum_cpu_time = 0.0f;
        float sum_render_time = 0.0f;
        float min_frame_time = frame_times_[0];
        float max_frame_time = frame_times_[0];

        for (size_t i = 0; i < HISTORY_SIZE; i++) {
            sum_frame_time += frame_times_[i];
            sum_cpu_time += cpu_times_[i];
            sum_render_time += render_times_[i];

            min_frame_time = std::min(min_frame_time, frame_times_[i]);
            max_frame_time = std::max(max_frame_time, frame_times_[i]);
        }

        stats_.avg_frame_time = sum_frame_time / HISTORY_SIZE;
        stats_.avg_cpu_time = sum_cpu_time / HISTORY_SIZE;
        stats_.avg_render_time = sum_render_time / HISTORY_SIZE;

        stats_.avg_fps = 1000.0f / stats_.avg_frame_time;
        stats_.min_fps = 1000.0f / max_frame_time;
        stats_.max_fps = 1000.0f / min_frame_time;

        // ImGui 통계 수집
        ImGuiIO& io = ImGui::GetIO();
        stats_.vertices = io.MetricsRenderVertices;
        stats_.draw_calls = io.MetricsRenderIndices / 3; // 삼각형 기준
    }

    void ShowPerformanceWindow() {
        if (ImGui::Begin("Performance Monitor")) {

            // 실시간 FPS 표시
            ImGui::Text("FPS: %.1f (%.2f ms)", stats_.avg_fps, stats_.avg_frame_time);
            ImGui::Text("Range: %.1f - %.1f FPS", stats_.min_fps, stats_.max_fps);

            ImGui::Separator();

            // 시간 분석
            ImGui::Text("CPU Time: %.2f ms", stats_.avg_cpu_time);
            ImGui::Text("Render Time: %.2f ms", stats_.avg_render_time);

            ImGui::Separator();

            // 렌더링 통계
            ImGui::Text("Draw Calls: %zu", stats_.draw_calls);
            ImGui::Text("Vertices: %zu", stats_.vertices);

            ImGui::Separator();

            // 프레임 시간 그래프
            ImGui::PlotLines("Frame Times (ms)", frame_times_.data(), HISTORY_SIZE,
                           frame_index_, nullptr, 0.0f, 33.33f, ImVec2(0, 80));

            // CPU vs Render 시간 비교
            static float combined_data[HISTORY_SIZE * 2];
            for (size_t i = 0; i < HISTORY_SIZE; i++) {
                combined_data[i] = cpu_times_[i];
                combined_data[i + HISTORY_SIZE] = render_times_[i];
            }

            ImGui::PlotHistogram("CPU vs Render", combined_data, HISTORY_SIZE * 2, 0,
                               nullptr, 0.0f, 10.0f, ImVec2(0, 80));

            // 성능 경고
            if (stats_.avg_fps < 30.0f) {
                ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(1.0f, 0.0f, 0.0f, 1.0f));
                ImGui::Text("WARNING: Low FPS detected!");
                ImGui::PopStyleColor();
            }

            if (stats_.draw_calls > 1000) {
                ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(1.0f, 0.5f, 0.0f, 1.0f));
                ImGui::Text("WARNING: High draw call count!");
                ImGui::PopStyleColor();
            }
        }
        ImGui::End();
    }

    const PerformanceStats& GetStats() const { return stats_; }
};

// 메모리 효율적인 대용량 데이터 렌더링
class EfficientDataRenderer {
private:
    struct RenderBatch {
        std::vector<ImVec2> vertices;
        std::vector<ImU32> colors;
        std::vector<ImDrawIdx> indices;
        size_t vertex_count;
        size_t index_count;

        void Reset() {
            vertices.clear();
            colors.clear();
            indices.clear();
            vertex_count = 0;
            index_count = 0;
        }
    };

    static constexpr size_t MAX_VERTICES_PER_BATCH = 65536;
    static constexpr size_t MAX_INDICES_PER_BATCH = MAX_VERTICES_PER_BATCH * 3;

    std::vector<RenderBatch> batches_;
    size_t current_batch_;

    // 시야 절두체 컬링
    struct FrustumCuller {
        ImVec2 view_min, view_max;

        bool IsVisible(const ImVec2& pos, float size) const {
            return !(pos.x + size < view_min.x || pos.x - size > view_max.x ||
                    pos.y + size < view_min.y || pos.y - size > view_max.y);
        }

        bool IsVisible(const ImVec2& min, const ImVec2& max) const {
            return !(max.x < view_min.x || min.x > view_max.x ||
                    max.y < view_min.y || min.y > view_max.y);
        }
    } frustum_;

public:
    EfficientDataRenderer() : current_batch_(0) {
        batches_.resize(16); // 초기 배치 수
    }

    void BeginRender(const ImVec2& view_min, const ImVec2& view_max) {
        // 시야 설정
        frustum_.view_min = view_min;
        frustum_.view_max = view_max;

        // 모든 배치 리셋
        for (auto& batch : batches_) {
            batch.Reset();
        }
        current_batch_ = 0;
    }

    void AddPoint(const ImVec2& pos, float size, ImU32 color) {
        // 컬링 체크
        if (!frustum_.IsVisible(pos, size)) return;

        // 현재 배치 가져오기
        RenderBatch& batch = GetCurrentBatch();

        // 배치가 가득 찬 경우 새 배치로 이동
        if (batch.vertex_count + 4 > MAX_VERTICES_PER_BATCH) {
            current_batch_++;
            if (current_batch_ >= batches_.size()) {
                batches_.emplace_back();
            }
        }

        // 점을 사각형으로 렌더링
        ImVec2 min_pos = ImVec2(pos.x - size, pos.y - size);
        ImVec2 max_pos = ImVec2(pos.x + size, pos.y + size);

        AddQuad(min_pos, max_pos, color);
    }

    void AddLine(const ImVec2& p1, const ImVec2& p2, float thickness, ImU32 color) {
        // 선분 컬링 체크
        ImVec2 line_min = ImVec2(std::min(p1.x, p2.x) - thickness, std::min(p1.y, p2.y) - thickness);
        ImVec2 line_max = ImVec2(std::max(p1.x, p2.x) + thickness, std::max(p1.y, p2.y) + thickness);

        if (!frustum_.IsVisible(line_min, line_max)) return;

        // 선분을 사각형으로 변환하여 렌더링
        ImVec2 dir = ImVec2(p2.x - p1.x, p2.y - p1.y);
        float len = std::sqrt(dir.x * dir.x + dir.y * dir.y);
        if (len < 0.001f) return;

        dir.x /= len;
        dir.y /= len;

        ImVec2 perp = ImVec2(-dir.y * thickness, dir.x * thickness);

        ImVec2 v1 = ImVec2(p1.x + perp.x, p1.y + perp.y);
        ImVec2 v2 = ImVec2(p1.x - perp.x, p1.y - perp.y);
        ImVec2 v3 = ImVec2(p2.x - perp.x, p2.y - perp.y);
        ImVec2 v4 = ImVec2(p2.x + perp.x, p2.y + perp.y);

        AddQuad(v1, v2, v3, v4, color);
    }

    void EndRender(ImDrawList* draw_list) {
        // 모든 배치를 렌더링
        for (size_t i = 0; i <= current_batch_ && i < batches_.size(); i++) {
            const RenderBatch& batch = batches_[i];
            if (batch.vertex_count == 0) continue;

            // ImDrawList에 배치 데이터 추가
            int vtx_current_idx = draw_list->VtxBuffer.Size;
            draw_list->VtxBuffer.resize(vtx_current_idx + batch.vertex_count);
            draw_list->IdxBuffer.reserve(draw_list->IdxBuffer.Size + batch.index_count);

            // 정점 데이터 복사
            for (size_t v = 0; v < batch.vertex_count; v++) {
                draw_list->VtxBuffer[vtx_current_idx + v] = ImDrawVert{
                    batch.vertices[v],
                    ImVec2(0, 0), // UV (텍스처를 사용하지 않으므로 0)
                    batch.colors[v]
                };
            }

            // 인덱스 데이터 복사 (오프셋 적용)
            for (size_t idx = 0; idx < batch.index_count; idx++) {
                draw_list->IdxBuffer.push_back(vtx_current_idx + batch.indices[idx]);
            }
        }
    }

private:
    RenderBatch& GetCurrentBatch() {
        if (current_batch_ >= batches_.size()) {
            batches_.emplace_back();
        }
        return batches_[current_batch_];
    }

    void AddQuad(const ImVec2& min, const ImVec2& max, ImU32 color) {
        AddQuad(ImVec2(min.x, min.y), ImVec2(min.x, max.y),
               ImVec2(max.x, max.y), ImVec2(max.x, min.y), color);
    }

    void AddQuad(const ImVec2& v1, const ImVec2& v2, const ImVec2& v3, const ImVec2& v4, ImU32 color) {
        RenderBatch& batch = GetCurrentBatch();

        size_t base_idx = batch.vertex_count;

        // 4개 정점 추가
        batch.vertices.insert(batch.vertices.end(), {v1, v2, v3, v4});
        batch.colors.insert(batch.colors.end(), {color, color, color, color});

        // 2개 삼각형을 위한 6개 인덱스 추가
        std::vector<ImDrawIdx> quad_indices = {
            static_cast<ImDrawIdx>(base_idx), static_cast<ImDrawIdx>(base_idx + 1), static_cast<ImDrawIdx>(base_idx + 2),
            static_cast<ImDrawIdx>(base_idx), static_cast<ImDrawIdx>(base_idx + 2), static_cast<ImDrawIdx>(base_idx + 3)
        };

        batch.indices.insert(batch.indices.end(), quad_indices.begin(), quad_indices.end());

        batch.vertex_count += 4;
        batch.index_count += 6;
    }
};

// 적응형 레벨 오브 디테일 (LOD) 시스템
class AdaptiveLODSystem {
private:
    struct LODLevel {
        float min_distance;
        float max_distance;
        float detail_reduction_factor;
        size_t max_elements;
    };

    std::vector<LODLevel> lod_levels_;
    float camera_distance_;

public:
    AdaptiveLODSystem() {
        // LOD 레벨 초기화
        lod_levels_ = {
            {0.0f,   50.0f,  1.0f,    10000}, // 최고 디테일
            {50.0f,  100.0f, 0.5f,    5000},  // 중간 디테일
            {100.0f, 200.0f, 0.25f,   2000},  // 낮은 디테일
            {200.0f, 400.0f, 0.1f,    500},   // 매우 낮은 디테일
            {400.0f, 1000.0f, 0.05f,  100}    // 최소 디테일
        };
    }

    void SetCameraDistance(float distance) {
        camera_distance_ = distance;
    }

    LODLevel GetCurrentLOD() const {
        for (const auto& level : lod_levels_) {
            if (camera_distance_ >= level.min_distance && camera_distance_ < level.max_distance) {
                return level;
            }
        }
        return lod_levels_.back(); // 최소 디테일 반환
    }

    bool ShouldRenderElement(size_t element_index, size_t total_elements) const {
        LODLevel current_lod = GetCurrentLOD();

        // 최대 요소 수 제한
        if (element_index >= current_lod.max_elements) {
            return false;
        }

        // 거리 기반 건너뛰기
        float skip_probability = 1.0f - current_lod.detail_reduction_factor;
        return (element_index % static_cast<size_t>(1.0f / current_lod.detail_reduction_factor)) == 0;
    }

    float GetRenderScale() const {
        return GetCurrentLOD().detail_reduction_factor;
    }
};

} // namespace PerformanceOptimization
```

---

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "\uae30\uc874 \ud30c\uc77c \uad6c\uc870 \ubd84\uc11d", "status": "completed", "activeForm": "\uae30\uc874 \ud30c\uc77c \uad6c\uc870 \ubd84\uc11d \uc911"}, {"content": "1\uc8fc\ucc28 HCI/HMI \uc774\ub860 \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "1\uc8fc\ucc28 HCI/HMI \uc774\ub860 \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "2\uc8fc\ucc28 C# WPF \uae30\ucd08 \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "2\uc8fc\ucc28 C# WPF \uae30\ucd08 \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "3\uc8fc\ucc28 C# \uc2e4\uc2dc\uac04 \ub370\uc774\ud130 \ucc98\ub9ac \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "3\uc8fc\ucc28 C# \uc2e4\uc2dc\uac04 \ub370\uc774\ud130 \ucc98\ub9ac \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "4\uc8fc\ucc28 C# \uace0\uae09 UI/UX \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "4\uc8fc\ucc28 C# \uace0\uae09 UI/UX \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "5\uc8fc\ucc28 C# \ud14c\uc2a4\ud2b8/\ubc30\ud3ec \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "5\uc8fc\ucc28 C# \ud14c\uc2a4\ud2b8/\ubc30\ud3ec \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "6\uc8fc\ucc28 Python PySide6 \uae30\ucd08 \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "6\uc8fc\ucc28 Python PySide6 \uae30\ucd08 \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "7\uc8fc\ucc28 Python PySide6 \uc2e4\uc2dc\uac04 \ub370\uc774\ud130 \ucc98\ub9ac \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "7\uc8fc\ucc28 Python PySide6 \uc2e4\uc2dc\uac04 \ub370\uc774\ud130 \ucc98\ub9ac \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "8\uc8fc\ucc28 Python PySide6 \uace0\uae09 \uae30\ub2a5 \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "8\uc8fc\ucc28 Python PySide6 \uace0\uae09 \uae30\ub2a5 \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "9\uc8fc\ucc28 Python PySide6 \ubc30\ud3ec \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "9\uc8fc\ucc28 Python PySide6 \ubc30\ud3ec \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "10\uc8fc\ucc28 ImGUI C++ \uae30\ucd08 \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "10\uc8fc\ucc28 ImGUI C++ \uae30\ucd08 \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "11\uc8fc\ucc28 ImGUI C++ \uc2ec\ud654 \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "in_progress", "activeForm": "11\uc8fc\ucc28 ImGUI C++ \uc2ec\ud654 \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "12\uc8fc\ucc28 ImGUI C++ \uace0\uae09 \uae30\ub2a5 \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "pending", "activeForm": "12\uc8fc\ucc28 ImGUI C++ \uace0\uae09 \uae30\ub2a5 \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "13\uc8fc\ucc28 ImGUI C++ \ud1b5\ud569 \ud504\ub85c\uc81d\ud2b8 \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "pending", "activeForm": "13\uc8fc\ucc28 ImGUI C++ \ud1b5\ud569 \ud504\ub85c\uc81d\ud2b8 \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "acceptance \uae30\uc900\uc73c\ub85c revision \uc218\ud589", "status": "pending", "activeForm": "acceptance \uae30\uc900\uc73c\ub85c revision \uc218\ud589 \uc911"}]