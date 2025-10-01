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
