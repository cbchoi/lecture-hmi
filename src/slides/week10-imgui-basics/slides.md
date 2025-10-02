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
---
layout: cover
---

# Week 10 - ImGUI 기초 + C++ 고급 기법
## 이론 강의 (120분)

RAII, Smart Pointers, Move Semantics를 활용한 안전한 리소스 관리

---

# 1. RAII 패턴 (Resource Acquisition Is Initialization)

## 1.1 RAII 기본 개념

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
// ❌ 나쁜 예: 수동 리소스 관리
class BadFileHandler {
private:
    FILE* file;

public:
    BadFileHandler(const char* filename) {
        file = fopen(filename, "r");
        if (!file) {
            throw std::runtime_error("Failed to open file");
        }
    }

    ~BadFileHandler() {
        // ❌ 예외 발생 시 누수 가능
        if (file) {
            fclose(file);
        }
    }

    void Process() {
        char buffer[1024];
        // ❌ 예외 발생 시 파일이 닫히지 않음
        if (fgets(buffer, sizeof(buffer), file) == nullptr) {
            throw std::runtime_error("Read error");
        }
    }
};
```

```cpp
// ✅ 좋은 예: RAII 패턴 적용
class GoodFileHandler {
private:
    std::unique_ptr<FILE, decltype(&fclose)> file;

public:
    GoodFileHandler(const char* filename)
        : file(fopen(filename, "r"), &fclose) {
        if (!file) {
            throw std::runtime_error("Failed to open file");
        }
    }

    // ✅ 소멸자가 자동 호출 (예외 발생해도)
    // file의 unique_ptr가 자동으로 fclose 호출

    void Process() {
        char buffer[1024];
        // ✅ 예외 발생해도 스택 해제 시 파일 자동 닫힘
        if (fgets(buffer, sizeof(buffer), file.get()) == nullptr) {
            throw std::runtime_error("Read error");
        }
    }
};
```

</div>
<div>

**RAII (Resource Acquisition Is Initialization) 패턴**:

1. **핵심 원칙**
   - 리소스 획득 = 객체 초기화
   - 리소스 해제 = 객체 소멸
   - 스택 기반 자동 생명주기 관리

2. **RAII가 관리하는 리소스**
   - 파일 핸들 (FILE*, fstream)
   - 메모리 (new/delete)
   - 뮤텍스 락 (std::lock_guard)
   - 네트워크 소켓
   - OpenGL 리소스 (텍스처, 버퍼)

3. **RAII 장점**
   - **예외 안전성**: 예외 발생 시에도 자동 정리
   - **누수 방지**: 명시적 해제 불필요
   - **가독성**: 리소스 생명주기가 명확
   - **RAII vs finally**: C++는 finally 없음 → RAII 사용

**반도체 HMI 적용**:
```cpp
// 장비 통신 포트 관리
class SerialPort {
    int fd;
public:
    SerialPort(const char* device) {
        fd = open(device, O_RDWR);
        if (fd < 0) throw std::runtime_error("Open failed");
        // 포트 설정...
    }
    ~SerialPort() {
        if (fd >= 0) close(fd);  // 자동 닫힘
    }
};

{
    SerialPort port("/dev/ttyUSB0");
    port.Write(command);
    // 예외 발생해도 포트 자동 닫힘
} // SerialPort 소멸자 자동 호출
```

**주의사항**:
- ❌ 소멸자에서 예외 던지지 말 것
- ✅ 복사 방지 또는 이동 의미론 구현
- ✅ Rule of Five 준수 (소멸자 정의 시)

</div>
</div>

---

## 1.2 OpenGL 리소스 RAII 관리

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
// OpenGL 텍스처 RAII 래퍼
class GLTexture {
private:
    GLuint texture_id = 0;
    int width, height;

public:
    GLTexture(int w, int h, GLenum format = GL_RGBA)
        : width(w), height(h) {
        // 리소스 획득 (생성자)
        glGenTextures(1, &texture_id);
        glBindTexture(GL_TEXTURE_2D, texture_id);
        glTexImage2D(GL_TEXTURE_2D, 0, format,
                     width, height, 0, format,
                     GL_UNSIGNED_BYTE, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    }

    ~GLTexture() {
        // 리소스 해제 (소멸자)
        if (texture_id != 0) {
            glDeleteTextures(1, &texture_id);
        }
    }

    // 복사 방지 (리소스는 하나만)
    GLTexture(const GLTexture&) = delete;
    GLTexture& operator=(const GLTexture&) = delete;

    // 이동 허용 (소유권 이전)
    GLTexture(GLTexture&& other) noexcept
        : texture_id(other.texture_id)
        , width(other.width)
        , height(other.height) {
        other.texture_id = 0;  // 원본 무효화
    }

    GLTexture& operator=(GLTexture&& other) noexcept {
        if (this != &other) {
            // 기존 리소스 해제
            if (texture_id != 0) {
                glDeleteTextures(1, &texture_id);
            }
            // 소유권 이전
            texture_id = other.texture_id;
            width = other.width;
            height = other.height;
            other.texture_id = 0;
        }
        return *this;
    }

    // 접근자
    GLuint GetID() const { return texture_id; }
    int GetWidth() const { return width; }
    int GetHeight() const { return height; }

    // 텍스처 업데이트
    void UpdateData(const void* data) {
        glBindTexture(GL_TEXTURE_2D, texture_id);
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0,
                        width, height, GL_RGBA,
                        GL_UNSIGNED_BYTE, data);
    }

    void Bind(int unit = 0) const {
        glActiveTexture(GL_TEXTURE0 + unit);
        glBindTexture(GL_TEXTURE_2D, texture_id);
    }
};
```

```cpp
// OpenGL VAO/VBO RAII 래퍼
class GLBuffer {
private:
    GLuint buffer_id = 0;
    GLenum target;
    size_t size_bytes;

public:
    GLBuffer(GLenum target_type)
        : target(target_type), size_bytes(0) {
        glGenBuffers(1, &buffer_id);
    }

    ~GLBuffer() {
        if (buffer_id != 0) {
            glDeleteBuffers(1, &buffer_id);
        }
    }

    // 복사/이동 (텍스처와 동일)
    GLBuffer(const GLBuffer&) = delete;
    GLBuffer& operator=(const GLBuffer&) = delete;
    GLBuffer(GLBuffer&& other) noexcept
        : buffer_id(other.buffer_id)
        , target(other.target)
        , size_bytes(other.size_bytes) {
        other.buffer_id = 0;
    }

    GLBuffer& operator=(GLBuffer&& other) noexcept {
        if (this != &other) {
            if (buffer_id != 0) {
                glDeleteBuffers(1, &buffer_id);
            }
            buffer_id = other.buffer_id;
            target = other.target;
            size_bytes = other.size_bytes;
            other.buffer_id = 0;
        }
        return *this;
    }

    template<typename T>
    void SetData(const std::vector<T>& data, GLenum usage = GL_STATIC_DRAW) {
        size_bytes = data.size() * sizeof(T);
        glBindBuffer(target, buffer_id);
        glBufferData(target, size_bytes, data.data(), usage);
    }

    void Bind() const {
        glBindBuffer(target, buffer_id);
    }

    GLuint GetID() const { return buffer_id; }
};
```

```cpp
// 사용 예시: 웨이퍼 맵 렌더링
class WaferMapRenderer {
private:
    GLTexture wafer_texture;
    GLBuffer vertex_buffer;
    GLBuffer index_buffer;

public:
    WaferMapRenderer(int width, int height)
        : wafer_texture(width, height)
        , vertex_buffer(GL_ARRAY_BUFFER)
        , index_buffer(GL_ELEMENT_ARRAY_BUFFER) {

        // 정점 데이터 설정
        std::vector<float> vertices = {
            // x,    y,    u,   v
            -1.0f, -1.0f, 0.0f, 0.0f,
             1.0f, -1.0f, 1.0f, 0.0f,
             1.0f,  1.0f, 1.0f, 1.0f,
            -1.0f,  1.0f, 0.0f, 1.0f
        };
        vertex_buffer.SetData(vertices);

        std::vector<unsigned int> indices = {0, 1, 2, 2, 3, 0};
        index_buffer.SetData(indices);
    }

    // ✅ 소멸 시 모든 OpenGL 리소스 자동 해제
    // ~WaferMapRenderer() = default;

    void Render() {
        wafer_texture.Bind(0);
        vertex_buffer.Bind();
        index_buffer.Bind();
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0);
    }
};
```

</div>
<div>

**OpenGL RAII 패턴 설명**:

1. **생성자에서 리소스 획득**
   - `glGenTextures()` / `glGenBuffers()` 호출
   - 실패 시 예외 던지기
   - 초기 설정 완료

2. **소멸자에서 리소스 해제**
   - `glDeleteTextures()` / `glDeleteBuffers()` 호출
   - ID가 0인지 체크 (이중 해제 방지)
   - `noexcept` 보장 (소멸자는 예외 던지지 않음)

3. **복사 방지, 이동 허용**
   - **복사 금지**: OpenGL 리소스는 복제 불가
   - **이동 허용**: 소유권 이전 가능
   - 이동 후 원본 무효화 (`texture_id = 0`)

**이동 의미론 (Move Semantics)**:
```cpp
GLTexture CreateTexture() {
    GLTexture tex(1024, 1024);
    // ... 설정
    return tex;  // ✅ 이동 반환 (복사 없음)
}

GLTexture my_texture = CreateTexture();  // ✅ 이동 생성
```

**Rule of Five**:
```cpp
class GLResource {
    // 5가지 특수 멤버 함수 정의 필요
    ~GLResource();                          // 1. 소멸자
    GLResource(const GLResource&) = delete; // 2. 복사 생성자
    GLResource& operator=(const GLResource&) = delete; // 3. 복사 대입
    GLResource(GLResource&&) noexcept;      // 4. 이동 생성자
    GLResource& operator=(GLResource&&) noexcept; // 5. 이동 대입
};
```

**반도체 HMI 적용**:
- 웨이퍼 맵 텍스처 (수백 개)
- 그래프 버텍스 버퍼 (실시간 업데이트)
- 3D 장비 모델 메시
- → 모두 RAII로 자동 관리, 누수 없음

**성능 고려사항**:
- 이동은 O(1) (포인터 복사만)
- 복사 방지로 불필요한 GPU 리소스 생성 방지
- 스마트 포인터와 조합 시 더욱 강력

</div>
</div>

---

# 2. Smart Pointers (스마트 포인터)

## 2.1 unique_ptr - 단독 소유권

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <memory>
#include <vector>
#include <string>

// ❌ 나쁜 예: Raw pointer 사용
class BadUIComponent {
private:
    UIWidget* widget;  // ❌ 수동 메모리 관리

public:
    BadUIComponent() {
        widget = new UIWidget();  // ❌ new 사용
    }

    ~BadUIComponent() {
        delete widget;  // ❌ delete 잊으면 누수
    }

    // ❌ 복사 시 얕은 복사 문제
    // ❌ 예외 발생 시 누수
};
```

```cpp
// ✅ 좋은 예: unique_ptr 사용
class GoodUIComponent {
private:
    std::unique_ptr<UIWidget> widget;  // ✅ 자동 관리

public:
    GoodUIComponent()
        : widget(std::make_unique<UIWidget>()) {  // ✅ make_unique 사용
        // ✅ 예외 안전
    }

    // ✅ 소멸자 자동 생성 (unique_ptr가 자동 해제)
    // ~GoodUIComponent() = default;

    // ✅ 복사 자동 금지 (unique_ptr은 복사 불가)
    // ✅ 이동은 자동 지원

    void UpdateWidget(std::unique_ptr<UIWidget> new_widget) {
        widget = std::move(new_widget);  // ✅ 소유권 이전
        // 기존 widget 자동 삭제됨
    }

    UIWidget* GetWidget() const {
        return widget.get();  // ✅ raw pointer 반환 (관찰만)
    }
};
```

```cpp
// unique_ptr을 활용한 UI 컴포넌트 계층 구조
class UIComponent {
public:
    virtual ~UIComponent() = default;
    virtual void Render() = 0;
    virtual void Update(float dt) {}
};

class Panel : public UIComponent {
private:
    std::string name;
    std::vector<std::unique_ptr<UIComponent>> children;  // ✅ 자식 소유

public:
    explicit Panel(std::string panel_name)
        : name(std::move(panel_name)) {}

    // ✅ 소유권 이전 (이동)
    void AddChild(std::unique_ptr<UIComponent> child) {
        children.push_back(std::move(child));
    }

    // ✅ 팩토리 패턴
    template<typename T, typename... Args>
    T* CreateChild(Args&&... args) {
        auto child = std::make_unique<T>(std::forward<Args>(args)...);
        T* ptr = child.get();
        children.push_back(std::move(child));
        return ptr;  // ✅ 관찰 포인터 반환
    }

    void Render() override {
        ImGui::Begin(name.c_str());
        for (auto& child : children) {
            child->Render();  // ✅ -> 연산자 사용
        }
        ImGui::End();
    }

    ~Panel() override {
        // ✅ children의 모든 unique_ptr 자동 소멸
        // ✅ 역순으로 소멸 (스택처럼)
    }
};
```

```cpp
// 사용 예시
void CreateEquipmentUI() {
    auto main_panel = std::make_unique<Panel>("Equipment Monitor");

    // ✅ 자식 생성 및 추가
    main_panel->AddChild(std::make_unique<TemperatureWidget>());
    main_panel->AddChild(std::make_unique<PressureWidget>());

    // ✅ 팩토리 메서드 사용
    auto* status = main_panel->CreateChild<StatusWidget>("IDLE");
    status->SetColor(ImVec4(0, 1, 0, 1));

    // ✅ 스코프 종료 시 자동 삭제
    // - main_panel 삭제
    // - 모든 자식들 자동 삭제 (역순)
}
```

</div>
<div>

**unique_ptr 핵심 특징**:

1. **단독 소유권 (Exclusive Ownership)**
   - 한 시점에 하나의 unique_ptr만 객체 소유
   - 복사 불가능 (`= delete`)
   - 이동 가능 (소유권 이전)

2. **오버헤드 없음**
   - Raw pointer와 동일한 크기 (8바이트, 64비트)
   - 런타임 오버헤드 없음 (컴파일 타임 최적화)
   - 참조 카운팅 없음 (shared_ptr과 차이)

3. **예외 안전성**
   - `make_unique<T>(args...)` 사용 권장
   - 예외 발생 시 자동 정리
   - RAII 패턴과 완벽한 조합

**make_unique vs new**:
```cpp
// ❌ 나쁜 예: new 직접 사용
std::unique_ptr<Widget> w1(new Widget());

// 문제 상황:
foo(std::unique_ptr<Widget>(new Widget()), risky_function());
// risky_function()이 예외 던지면 Widget 누수 가능

// ✅ 좋은 예: make_unique 사용
auto w2 = std::make_unique<Widget>();

// 안전:
foo(std::make_unique<Widget>(), risky_function());
// 예외 발생해도 누수 없음 (순서 보장)
```

**unique_ptr API**:
```cpp
unique_ptr<T> ptr = make_unique<T>(args);

ptr.get();          // raw pointer 반환 (관찰)
ptr.reset();        // 객체 삭제, nullptr로 설정
ptr.reset(new T);   // 기존 삭제, 새 객체 소유
ptr.release();      // 소유권 포기, raw pointer 반환
ptr.operator*();    // 역참조
ptr.operator->();   // 멤버 접근
bool(ptr);          // nullptr 체크
```

**소유권 이전 패턴**:
```cpp
// 1. 함수 반환 (이동)
std::unique_ptr<Widget> CreateWidget() {
    return std::make_unique<Widget>();  // RVO + move
}

// 2. 컨테이너 저장
std::vector<std::unique_ptr<Widget>> widgets;
widgets.push_back(std::make_unique<Widget>());  // move

// 3. 함수 인자 (sink)
void TakeOwnership(std::unique_ptr<Widget> w) {
    // w가 소유권 가짐
}
TakeOwnership(std::move(my_widget));  // 명시적 이동
```

**반도체 HMI 적용**:
- UI 컴포넌트 계층 (Panel → Widget)
- 일시적 데이터 (센서 판독값 버퍼)
- 장비 상태 머신 (State 객체)

</div>
</div>

---

## 2.2 shared_ptr - 공유 소유권

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <memory>
#include <vector>
#include <unordered_map>
#include <string>

// shared_ptr 기본 사용
class Equipment {
private:
    std::string equipment_id;
    int status;

public:
    explicit Equipment(std::string id)
        : equipment_id(std::move(id)), status(0) {}

    void UpdateStatus(int new_status) {
        status = new_status;
    }

    const std::string& GetID() const { return equipment_id; }
    int GetStatus() const { return status; }

    ~Equipment() {
        std::cout << "Equipment " << equipment_id << " destroyed\n";
    }
};

// 여러 곳에서 Equipment를 공유하는 시스템
class EquipmentManager {
private:
    // Equipment 저장소 (원본)
    std::unordered_map<std::string, std::shared_ptr<Equipment>> equipments;

public:
    // Equipment 생성 및 저장
    std::shared_ptr<Equipment> CreateEquipment(const std::string& id) {
        auto equipment = std::make_shared<Equipment>(id);
        equipments[id] = equipment;
        return equipment;  // ✅ shared_ptr 복사 (ref count 증가)
    }

    // Equipment 조회
    std::shared_ptr<Equipment> GetEquipment(const std::string& id) {
        auto it = equipments.find(id);
        if (it != equipments.end()) {
            return it->second;  // ✅ shared_ptr 복사
        }
        return nullptr;
    }

    // Equipment 제거
    void RemoveEquipment(const std::string& id) {
        equipments.erase(id);
        // ✅ ref count 감소
        // ✅ 다른 곳에서 사용 중이면 아직 삭제 안 됨
    }

    size_t GetEquipmentCount() const {
        return equipments.size();
    }
};
```

```cpp
// 관찰자 패턴에서 shared_ptr 활용
class DataLogger {
private:
    std::shared_ptr<Equipment> equipment;  // ✅ 공유 소유권
    std::string log_file;

public:
    DataLogger(std::shared_ptr<Equipment> eq, std::string file)
        : equipment(eq)  // ✅ shared_ptr 복사 (ref count++)
        , log_file(std::move(file)) {}

    void LogStatus() {
        if (equipment) {  // ✅ nullptr 체크
            std::cout << "Logging " << equipment->GetID()
                      << ": " << equipment->GetStatus() << "\n";
        }
    }

    // ✅ DataLogger 소멸 시 ref count 감소
    // ✅ Equipment는 다른 곳에서 사용 중이면 유지됨
};

class UIDisplay {
private:
    std::shared_ptr<Equipment> equipment;  // ✅ 동일 Equipment 공유

public:
    UIDisplay(std::shared_ptr<Equipment> eq)
        : equipment(eq) {}  // ref count++

    void Render() {
        if (equipment) {
            ImGui::Text("Equipment: %s", equipment->GetID().c_str());
            ImGui::Text("Status: %d", equipment->GetStatus());
        }
    }
};
```

```cpp
// 사용 예시: 여러 시스템에서 Equipment 공유
void SharedEquipmentExample() {
    EquipmentManager manager;

    // Equipment 생성 (ref count = 1)
    auto chamber_a = manager.CreateEquipment("CHAMBER-A");
    std::cout << "Ref count: " << chamber_a.use_count() << "\n";  // 2 (manager + chamber_a)

    {
        // 여러 시스템에서 공유
        DataLogger logger(chamber_a, "chamber_a.log");  // ref count = 3
        UIDisplay display(chamber_a);                   // ref count = 4

        std::cout << "Ref count: " << chamber_a.use_count() << "\n";  // 4

        chamber_a->UpdateStatus(1);  // 모든 곳에서 동일한 객체 보임

        logger.LogStatus();  // "Logging CHAMBER-A: 1"
        display.Render();    // UI에도 Status: 1 표시

    }  // ✅ logger, display 소멸 → ref count = 2

    std::cout << "Ref count: " << chamber_a.use_count() << "\n";  // 2

    manager.RemoveEquipment("CHAMBER-A");  // ref count = 1
    std::cout << "Ref count: " << chamber_a.use_count() << "\n";  // 1

}  // ✅ chamber_a 소멸 → ref count = 0 → Equipment 삭제
```

```cpp
// shared_ptr 성능 고려사항
class PerformanceSensitiveCode {
private:
    std::shared_ptr<HeavyData> data;

public:
    // ✅ const& 전달 (ref count 증가 없음)
    void ProcessData(const std::shared_ptr<HeavyData>& data_ref) {
        // 읽기만 하는 경우 복사 불필요
        std::cout << data_ref->GetSize() << "\n";
    }

    // ✅ 소유권 필요 시에만 복사
    void StoreData(std::shared_ptr<HeavyData> data_copy) {
        data = std::move(data_copy);  // ✅ 이동으로 ref count 증가 회피
    }

    // ❌ 값 전달 (ref count 증가/감소 오버헤드)
    void BadProcessData(std::shared_ptr<HeavyData> data_copy) {
        // ref count 원자적 연산 (느림)
    }
};
```

</div>
<div>

**shared_ptr 핵심 특징**:

1. **공유 소유권 (Shared Ownership)**
   - 여러 shared_ptr가 동일 객체 소유 가능
   - 복사 가능 (참조 카운트 증가)
   - 마지막 shared_ptr 소멸 시 객체 삭제

2. **참조 카운팅 (Reference Counting)**
   - **Control Block** 사용 (heap 할당)
   - 강한 참조 카운트 (strong count)
   - 약한 참조 카운트 (weak count, weak_ptr용)
   - 원자적 연산 (atomic, 멀티스레드 안전)

3. **오버헤드**
   - 크기: 16바이트 (포인터 2개)
     - 객체 포인터 (8바이트)
     - Control block 포인터 (8바이트)
   - 성능:
     - 복사/소멸 시 원자적 증감 (atomic increment/decrement)
     - make_shared 사용 시 한 번의 할당
     - new 사용 시 두 번의 할당 (객체 + control block)

**make_shared vs new**:
```cpp
// ❌ 나쁜 예: new 사용 (할당 2회)
auto p1 = std::shared_ptr<Widget>(new Widget());
// 1. new Widget() - Widget 할당
// 2. shared_ptr 생성 - Control block 할당

// ✅ 좋은 예: make_shared (할당 1회)
auto p2 = std::make_shared<Widget>();
// Widget + Control block을 한 번에 할당 (효율적)
```

**shared_ptr API**:
```cpp
shared_ptr<T> p = make_shared<T>(args);

p.use_count();      // 참조 카운트 조회
p.unique();         // use_count() == 1 체크
p.reset();          // 참조 해제
p.reset(new T);     // 새 객체 소유
p.get();            // raw pointer 반환
p.operator*();      // 역참조
p.operator->();     // 멤버 접근
```

**순환 참조 문제**:
```cpp
// ❌ 순환 참조 → 메모리 누수
class Node {
    std::shared_ptr<Node> next;  // ❌ 순환 참조
    std::shared_ptr<Node> prev;  // ❌ 순환 참조
};

Node* a = new Node();
Node* b = new Node();
a->next = b;  // a → b
b->prev = a;  // b → a
// ref count 영원히 0이 안 됨!

// ✅ weak_ptr로 해결 (다음 슬라이드)
```

**반도체 HMI 적용**:
- 여러 UI에서 동일 장비 데이터 공유
- 레시피 객체 (여러 프로세스에서 참조)
- 로그 시스템 (장비 정보 공유)
- 캐시 시스템 (동일 데이터 중복 제거)

**사용 가이드**:
- ✅ 소유권 명확히 구분 (unique vs shared)
- ✅ const& 전달로 불필요한 ref count 증가 방지
- ✅ make_shared 사용으로 성능 최적화
- ❌ shared_ptr 남용 주의 (대부분은 unique_ptr 충분)

</div>
</div>

---

## 2.3 weak_ptr - 약한 참조

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <memory>
#include <vector>
#include <iostream>

// ❌ 순환 참조 문제
class BadNode {
public:
    std::shared_ptr<BadNode> next;
    std::shared_ptr<BadNode> prev;  // ❌ 순환 참조
    int data;

    BadNode(int d) : data(d) {}
    ~BadNode() {
        std::cout << "Node " << data << " destroyed\n";
    }
};

void CircularReferenceDemo() {
    auto node1 = std::make_shared<BadNode>(1);  // ref count = 1
    auto node2 = std::make_shared<BadNode>(2);  // ref count = 1

    node1->next = node2;  // node2 ref count = 2
    node2->prev = node1;  // node1 ref count = 2

    // ❌ 스코프 종료 시:
    // - node1 지역 변수 소멸 → node1 ref count = 1 (여전히 node2->prev가 가짐)
    // - node2 지역 변수 소멸 → node2 ref count = 1 (여전히 node1->next가 가짐)
    // - 둘 다 삭제 안 됨! 메모리 누수!
}  // ❌ 소멸자 호출 안 됨
```

```cpp
// ✅ weak_ptr로 순환 참조 해결
class GoodNode {
public:
    std::shared_ptr<GoodNode> next;  // ✅ 강한 참조 (소유)
    std::weak_ptr<GoodNode> prev;    // ✅ 약한 참조 (관찰만)
    int data;

    GoodNode(int d) : data(d) {}
    ~GoodNode() {
        std::cout << "Node " << data << " destroyed\n";
    }
};

void WeakPtrSolutionDemo() {
    auto node1 = std::make_shared<GoodNode>(1);  // ref count = 1
    auto node2 = std::make_shared<GoodNode>(2);  // ref count = 1

    node1->next = node2;  // node2 ref count = 2 (shared_ptr)
    node2->prev = node1;  // node1 ref count = 1 (weak_ptr는 증가 안 함!)

    // ✅ 스코프 종료 시:
    // - node1 지역 변수 소멸 → node1 ref count = 0 → node1 삭제됨
    // - node2 지역 변수 소멸 → node2 ref count = 1
    // - node1 삭제로 node1->next 삭제 → node2 ref count = 0 → node2 삭제됨
    // ✅ 정상적으로 메모리 해제!
}  // "Node 1 destroyed\n" "Node 2 destroyed\n"
```

```cpp
// weak_ptr 사용 패턴: lock()으로 임시 shared_ptr 얻기
class Equipment;

class EquipmentObserver {
private:
    std::weak_ptr<Equipment> observed_equipment;  // ✅ 약한 참조

public:
    EquipmentObserver(std::shared_ptr<Equipment> eq)
        : observed_equipment(eq) {}  // ✅ weak_ptr는 ref count 증가 안 함

    void CheckStatus() {
        // ✅ lock()으로 임시 shared_ptr 얻기
        if (auto eq = observed_equipment.lock()) {
            // eq는 shared_ptr<Equipment>
            // Equipment가 아직 살아있음 (ref count 임시 증가)
            std::cout << "Equipment status: " << eq->GetStatus() << "\n";
        } else {
            // Equipment가 이미 삭제됨
            std::cout << "Equipment no longer exists\n";
        }
        // ✅ eq 소멸 → ref count 원래대로
    }

    bool IsValid() const {
        return !observed_equipment.expired();  // ✅ 객체 존재 여부
    }
};
```

```cpp
// 캐시 시스템에서 weak_ptr 활용
class DataCache {
private:
    // weak_ptr로 캐시 (객체가 삭제되면 자동으로 expired)
    std::unordered_map<std::string, std::weak_ptr<CachedData>> cache;

public:
    std::shared_ptr<CachedData> GetOrLoad(const std::string& key) {
        // 1. 캐시 확인
        auto it = cache.find(key);
        if (it != cache.end()) {
            // weak_ptr를 shared_ptr로 변환 시도
            if (auto cached = it->second.lock()) {
                std::cout << "Cache hit: " << key << "\n";
                return cached;  // ✅ 캐시 적중
            } else {
                // 객체가 삭제됨 → 캐시 엔트리 제거
                cache.erase(it);
            }
        }

        // 2. 캐시 미스 → 새로 로드
        std::cout << "Cache miss: " << key << "\n";
        auto data = std::make_shared<CachedData>(key);
        cache[key] = data;  // ✅ weak_ptr 저장 (ref count 증가 안 함)
        return data;
    }

    void CleanupExpired() {
        // 만료된 weak_ptr 정리
        for (auto it = cache.begin(); it != cache.end(); ) {
            if (it->second.expired()) {
                it = cache.erase(it);
            } else {
                ++it;
            }
        }
    }

    size_t GetCacheSize() const { return cache.size(); }
};
```

```cpp
// 사용 예시: Observer 패턴
class EventBus {
private:
    std::vector<std::weak_ptr<EventListener>> listeners;  // ✅ 약한 참조

public:
    void Subscribe(std::shared_ptr<EventListener> listener) {
        listeners.push_back(listener);  // ✅ ref count 증가 안 함
    }

    void NotifyAll(const Event& event) {
        // 삭제된 리스너 자동 제거
        listeners.erase(
            std::remove_if(listeners.begin(), listeners.end(),
                [&](std::weak_ptr<EventListener>& weak_listener) {
                    if (auto listener = weak_listener.lock()) {
                        listener->OnEvent(event);  // ✅ 이벤트 전달
                        return false;  // 유지
                    }
                    return true;  // ✅ 삭제된 리스너 제거
                }),
            listeners.end()
        );
    }
};
```

</div>
<div>

**weak_ptr 핵심 특징**:

1. **약한 참조 (Weak Reference)**
   - 객체를 가리키지만 소유하지 않음
   - **참조 카운트 증가 안 함** (strong count)
   - weak count만 증가 (control block 유지용)
   - 객체 삭제를 막지 않음

2. **순환 참조 해결**
   ```
   ❌ shared_ptr → shared_ptr (순환 참조)
   Node A ──────→ Node B
        ↖──────/

   ✅ shared_ptr → weak_ptr (순환 끊김)
   Node A ──────→ Node B
        ←·····/ (약한 참조)
   ```

3. **사용 방법**
   - `lock()`: weak_ptr → shared_ptr 변환 (안전)
   - `expired()`: 객체가 삭제됐는지 확인
   - 직접 역참조 불가 (항상 lock() 먼저)

**weak_ptr API**:
```cpp
std::weak_ptr<T> wp;

auto sp = wp.lock();     // shared_ptr 반환 (nullptr 가능)
bool valid = !wp.expired();  // 객체 존재 여부
long count = wp.use_count(); // 현재 shared_ptr 개수
wp.reset();              // weak_ptr 초기화
```

**lock() vs expired()**:
```cpp
// ❌ 나쁜 예: expired() 후 lock() (race condition)
if (!wp.expired()) {
    auto sp = wp.lock();  // ❌ 사이에 객체 삭제될 수 있음!
    sp->DoSomething();    // ❌ nullptr 역참조 가능
}

// ✅ 좋은 예: lock()만 사용
if (auto sp = wp.lock()) {  // ✅ 원자적 변환
    sp->DoSomething();      // ✅ 안전
}
```

**Control Block 수명**:
```cpp
auto sp = std::make_shared<int>(42);
std::weak_ptr<int> wp = sp;

// Strong count = 1, Weak count = 1
// Control block 존재

sp.reset();  // 객체 삭제, Strong count = 0
             // ✅ 하지만 Control block은 유지 (Weak count = 1)

bool is_expired = wp.expired();  // true
auto sp2 = wp.lock();            // nullptr

// wp 소멸 → Weak count = 0 → Control block 삭제
```

**반도체 HMI 적용 사례**:

1. **Observer 패턴**
   - 이벤트 버스가 리스너를 weak_ptr로 보관
   - 리스너 삭제 시 자동으로 구독 해제

2. **캐시 시스템**
   - weak_ptr로 캐시 보관
   - 다른 곳에서 사용 안 하면 자동 정리

3. **부모-자식 관계**
   - 부모 → 자식: shared_ptr (소유)
   - 자식 → 부모: weak_ptr (순환 방지)

4. **UI 계층 구조**
   - Panel → Widget: shared_ptr
   - Widget → Panel: weak_ptr (parent 역참조)

**성능 고려**:
- lock() 호출은 원자적 연산 (atomic)
- 자주 호출하면 성능 영향
- 한 번 lock()하고 로컬 변수에 저장

</div>
</div>

---

# 3. Move Semantics (이동 의미론)

## 3.1 L-value vs R-value

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <iostream>
#include <vector>
#include <string>

// L-value와 R-value 구분
void ValueCategoryDemo() {
    int x = 10;           // x는 L-value (이름 있음, 주소 가짐)
    int y = x + 5;        // (x + 5)는 R-value (임시값, 주소 없음)

    int* ptr = &x;        // ✅ L-value는 주소 가능
    // int* ptr2 = &(x + 5);  // ❌ R-value는 주소 불가 (컴파일 에러)

    std::string s1 = "Hello";  // s1: L-value, "Hello": R-value
    std::string s2 = s1;       // s1: L-value (복사)
    std::string s3 = s1 + " World";  // (s1 + " World"): R-value (이동 가능)
}
```

```cpp
// ❌ 복사 생성자 (L-value 참조)
class CopyExample {
private:
    int* data;
    size_t size;

public:
    // 복사 생성자
    CopyExample(const CopyExample& other)
        : size(other.size) {
        std::cout << "Copy constructor\n";
        data = new int[size];  // ❌ 메모리 할당
        std::memcpy(data, other.data, size * sizeof(int));  // ❌ 복사
    }

    // 복사 대입 연산자
    CopyExample& operator=(const CopyExample& other) {
        std::cout << "Copy assignment\n";
        if (this != &other) {
            delete[] data;  // 기존 메모리 해제
            size = other.size;
            data = new int[size];  // ❌ 새 메모리 할당
            std::memcpy(data, other.data, size * sizeof(int));  // ❌ 복사
        }
        return *this;
    }
};
```

```cpp
// ✅ 이동 생성자 (R-value 참조)
class MoveExample {
private:
    int* data;
    size_t size;

public:
    // 이동 생성자 (R-value 참조 &&)
    MoveExample(MoveExample&& other) noexcept
        : data(other.data)    // ✅ 포인터만 복사 (얕은 복사)
        , size(other.size) {
        std::cout << "Move constructor\n";
        // ✅ 원본 무효화 (이중 삭제 방지)
        other.data = nullptr;
        other.size = 0;
    }

    // 이동 대입 연산자
    MoveExample& operator=(MoveExample&& other) noexcept {
        std::cout << "Move assignment\n";
        if (this != &other) {
            delete[] data;  // 기존 메모리 해제

            // ✅ 소유권 이전 (포인터 스왑)
            data = other.data;
            size = other.size;

            // ✅ 원본 무효화
            other.data = nullptr;
            other.size = 0;
        }
        return *this;
    }

    ~MoveExample() {
        delete[] data;  // ✅ nullptr 삭제는 안전
    }
};
```

```cpp
// 복사 vs 이동 성능 비교
void PerformanceComparison() {
    std::vector<int> source(1000000, 42);

    // ❌ 복사 (느림)
    auto start = std::chrono::high_resolution_clock::now();
    std::vector<int> dest1 = source;  // 100만 개 int 복사
    auto end = std::chrono::high_resolution_clock::now();
    std::cout << "Copy: " << std::chrono::duration<double, std::milli>(end - start).count() << "ms\n";

    // ✅ 이동 (빠름)
    start = std::chrono::high_resolution_clock::now();
    std::vector<int> dest2 = std::move(source);  // 포인터 3개만 복사
    end = std::chrono::high_resolution_clock::now();
    std::cout << "Move: " << std::chrono::duration<double, std::milli>(end - start).count() << "ms\n";

    // source는 이제 비어있음 (moved-from 상태)
    std::cout << "Source size after move: " << source.size() << "\n";  // 0
}
```

```cpp
// std::move의 역할
void MoveSemanticDemo() {
    std::string s1 = "Hello, World!";

    // ❌ 복사 (s1은 L-value)
    std::string s2 = s1;              // 복사 생성자 호출

    // ✅ 이동 (std::move로 R-value로 캐스팅)
    std::string s3 = std::move(s1);   // 이동 생성자 호출

    std::cout << "s1: " << s1 << "\n";  // "" (빈 문자열, moved-from)
    std::cout << "s2: " << s2 << "\n";  // "Hello, World!" (복사본)
    std::cout << "s3: " << s3 << "\n";  // "Hello, World!" (이동됨)

    // ⚠️ s1 사용 가능하지만 상태 불명확 (moved-from)
    // ✅ s1.clear()나 s1 = "new value" 는 안전
    // ❌ s1의 내용 가정하지 말 것
}
```

</div>
<div>

**L-value vs R-value**:

| 구분 | L-value | R-value |
|------|---------|---------|
| **정의** | 이름이 있는 값 | 임시 값 (temporary) |
| **주소** | 주소 가짐 (&x 가능) | 주소 없음 |
| **대입** | 대입 가능 (x = 10) | 대입 불가 |
| **수명** | 명시적 스코프 | 표현식 끝까지 |
| **예시** | 변수, 함수 반환 참조 | 리터럴, 함수 반환 값, 연산 결과 |

**R-value Reference (&&)**:
```cpp
void foo(int& x);        // L-value 참조
void bar(int&& x);       // R-value 참조

int a = 10;
foo(a);         // ✅ a는 L-value
foo(10);        // ❌ 10은 R-value (컴파일 에러)

bar(a);         // ❌ a는 L-value (컴파일 에러)
bar(10);        // ✅ 10은 R-value
bar(std::move(a));  // ✅ std::move로 R-value로 캐스팅
```

**std::move의 역할**:
```cpp
template<typename T>
typename remove_reference<T>::type&& move(T&& t) noexcept {
    return static_cast<typename remove_reference<T>::type&&>(t);
}

// std::move는 단순히 캐스팅만 함
// L-value → R-value reference로 변환
// 실제 "이동"은 하지 않음! (이름이 오해의 소지 있음)
```

**이동 의미론의 장점**:

1. **성능 향상**
   - 복사: O(n) (데이터 크기)
   - 이동: O(1) (포인터만 복사)

2. **불필요한 복사 제거**
   ```cpp
   std::vector<std::string> CreateLargeVector() {
       std::vector<std::string> v;
       v.push_back("...");
       // ...
       return v;  // ✅ 이동 (RVO + move semantics)
   }

   auto result = CreateLargeVector();  // ✅ 복사 없음!
   ```

3. **Move-only 타입 지원**
   - unique_ptr (복사 불가, 이동만 가능)
   - thread, mutex (복사 불가)

**반도체 HMI 적용**:
- 대용량 센서 데이터 전달
- UI 컴포넌트 소유권 이전
- 임시 버퍼 최적화

**주의사항**:
```cpp
std::string s = "Hello";
std::string s2 = std::move(s);
// ⚠️ s는 "moved-from" 상태
// ✅ s.empty() 체크 가능
// ✅ s = "new" 대입 가능
// ❌ s의 내용 가정하지 말 것
```

</div>
</div>

---

## 3.2 Perfect Forwarding (완벽한 전달)

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <utility>
#include <memory>
#include <iostream>

// ❌ 나쁜 예: 값 전달 (복사 발생)
template<typename T>
std::unique_ptr<T> BadMakeUnique(T value) {
    // value는 복사본 (비효율적)
    return std::unique_ptr<T>(new T(value));
}

// ❌ 나쁜 예: L-value 참조 (R-value 받을 수 없음)
template<typename T>
std::unique_ptr<T> BadMakeUnique2(T& value) {
    return std::unique_ptr<T>(new T(value));
}
// BadMakeUnique2(Widget());  // ❌ 컴파일 에러 (R-value 전달 불가)

// ❌ 나쁜 예: Const L-value 참조 (이동 불가)
template<typename T>
std::unique_ptr<T> BadMakeUnique3(const T& value) {
    // ✅ L-value와 R-value 둘 다 받을 수 있음
    // ❌ 하지만 항상 복사 (이동 못함)
    return std::unique_ptr<T>(new T(value));
}
```

```cpp
// ✅ 좋은 예: Universal Reference + Perfect Forwarding
template<typename T>
std::unique_ptr<T> GoodMakeUnique(T&& value) {
    // T&&: Universal Reference (Forwarding Reference)
    // std::forward: 원래 타입 유지하며 전달
    return std::unique_ptr<T>(new T(std::forward<T>(value)));
}

void PerfectForwardingDemo() {
    Widget w;

    // L-value 전달 → 복사 생성자
    auto p1 = GoodMakeUnique(w);  // T&& → Widget&

    // R-value 전달 → 이동 생성자
    auto p2 = GoodMakeUnique(Widget());  // T&& → Widget&&

    // std::move + L-value → 이동 생성자
    auto p3 = GoodMakeUnique(std::move(w));  // T&& → Widget&&
}
```

```cpp
// Perfect Forwarding 실전 예제: 팩토리 함수
template<typename T, typename... Args>
std::unique_ptr<T> CreateComponent(Args&&... args) {
    // ✅ 가변 인자 템플릿
    // ✅ Perfect Forwarding
    return std::make_unique<T>(std::forward<Args>(args)...);
}

class TemperatureWidget {
private:
    std::string label;
    double min_temp, max_temp;

public:
    TemperatureWidget(std::string lbl, double min_t, double max_t)
        : label(std::move(lbl)), min_temp(min_t), max_temp(max_t) {
        std::cout << "TemperatureWidget created: " << label << "\n";
    }
};

void FactoryDemo() {
    // ✅ 모든 인자가 완벽하게 전달됨
    // - "Temperature": R-value → 이동
    // - 0.0, 100.0: R-value → 값 전달
    auto widget = CreateComponent<TemperatureWidget>(
        "Temperature",  // R-value (문자열 리터럴)
        0.0,            // R-value
        100.0           // R-value
    );

    std::string label = "Pressure";
    // ✅ label은 L-value → 복사
    auto widget2 = CreateComponent<TemperatureWidget>(
        label,    // L-value → 복사
        0.0,
        10.0
    );

    // ✅ std::move로 label 이동
    auto widget3 = CreateComponent<TemperatureWidget>(
        std::move(label),  // R-value로 캐스팅 → 이동
        0.0,
        10.0
    );
}
```

```cpp
// emplace_back vs push_back
void EmplaceDemo() {
    std::vector<TemperatureWidget> widgets;
    widgets.reserve(10);

    // ❌ push_back: 임시 객체 생성 후 이동
    widgets.push_back(TemperatureWidget("Temp1", 0.0, 100.0));
    // 1. TemperatureWidget 생성자 (임시 객체)
    // 2. 이동 생성자 (vector로 이동)
    // 3. 소멸자 (임시 객체)

    // ✅ emplace_back: 제자리 생성 (Perfect Forwarding)
    widgets.emplace_back("Temp2", 0.0, 100.0);
    // 1. TemperatureWidget 생성자 (vector 내부에서 바로 생성)
    // → 더 효율적!
}
```

```cpp
// Reference Collapsing 규칙
template<typename T>
void foo(T&& param) {
    // T가 int&일 때:
    // T&& = int& && → int& (Reference Collapsing)

    // T가 int일 때:
    // T&& = int&& (R-value reference)
}

int x = 10;
foo(x);          // T = int&,  T&& = int& &&  → int&
foo(10);         // T = int,   T&& = int&&
foo(std::move(x)); // T = int,   T&& = int&&
```

```cpp
// std::forward 동작 원리
template<typename T>
T&& forward(typename remove_reference<T>::type& t) noexcept {
    return static_cast<T&&>(t);
}

// 사용 예:
template<typename T>
void wrapper(T&& arg) {
    // ❌ arg 자체는 L-value (이름이 있음)
    foo(arg);             // 항상 L-value로 전달

    // ✅ std::forward로 원래 value category 복원
    foo(std::forward<T>(arg));  // T가 int&면 L-value로, int면 R-value로 전달
}
```

</div>
<div>

**Perfect Forwarding (완벽한 전달)**:

1. **Universal Reference (T&&)**
   - 템플릿 매개변수 `T&&`는 특별함
   - L-value 받으면 L-value 참조로 추론
   - R-value 받으면 R-value 참조로 추론

2. **Reference Collapsing 규칙**
   ```
   T&  &  → T&     (L-value ref + L-value ref = L-value ref)
   T&  && → T&     (L-value ref + R-value ref = L-value ref)
   T&& &  → T&     (R-value ref + L-value ref = L-value ref)
   T&& && → T&&    (R-value ref + R-value ref = R-value ref)

   요약: & 하나라도 있으면 &
   ```

3. **std::forward의 역할**
   ```cpp
   // L-value로 전달받았으면 L-value로 전달
   // R-value로 전달받았으면 R-value로 전달

   wrapper(x);           // x: L-value
   → foo(arg)            // L-value로 전달
   → foo(forward(arg))   // L-value로 전달

   wrapper(Widget());    // Widget(): R-value
   → foo(arg)            // L-value로 전달 (❌)
   → foo(forward(arg))   // R-value로 전달 (✅)
   ```

**std::forward vs std::move**:

| | std::forward | std::move |
|---|--------------|-----------|
| **용도** | 템플릿에서 value category 보존 | 명시적 R-value 변환 |
| **사용처** | Universal reference (T&&) | 일반 L-value |
| **결과** | 조건부 (L or R) | 항상 R-value |

```cpp
template<typename T>
void foo(T&& arg) {
    bar(std::forward<T>(arg));  // ✅ Perfect forwarding
}

void baz(Widget& w) {
    Widget w2 = std::move(w);   // ✅ 명시적 이동
}
```

**emplace_back의 장점**:
```cpp
// push_back
vector.push_back(Widget(arg1, arg2));
// 1. Widget 생성 (임시)
// 2. 이동 생성자
// 3. 소멸자 (임시)

// emplace_back
vector.emplace_back(arg1, arg2);
// 1. Widget 생성 (제자리)
// → 1단계로 줄어듦!
```

**반도체 HMI 적용**:

```cpp
// UI 컴포넌트 팩토리
class UIPanel {
    std::vector<std::unique_ptr<Widget>> widgets;

public:
    template<typename WidgetType, typename... Args>
    WidgetType* AddWidget(Args&&... args) {
        auto widget = std::make_unique<WidgetType>(
            std::forward<Args>(args)...  // ✅ Perfect forwarding
        );
        WidgetType* ptr = widget.get();
        widgets.push_back(std::move(widget));
        return ptr;
    }
};

// 사용
panel.AddWidget<TemperatureWidget>("Temp", 0.0, 100.0);
// 모든 인자가 효율적으로 전달됨
```

**주의사항**:
- Universal reference는 **템플릿에서만** (T&&)
- 일반 R-value reference와 구분: `Widget&&` (일반), `T&&` (universal)
- `std::forward<T>` 타입 명시 필요

</div>
</div>

---

# 4. 메모리 관리 고급 기법

## 4.1 Custom Allocator (커스텀 할당자)

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <memory>
#include <vector>
#include <array>
#include <cstddef>

// Memory Pool Allocator (고정 크기 블록)
template<typename T, size_t BlockSize = 4096>
class PoolAllocator {
private:
    // 메모리 풀
    struct Block {
        std::array<std::byte, BlockSize> data;
        Block* next;
    };

    Block* free_blocks = nullptr;
    std::vector<std::unique_ptr<Block>> all_blocks;

public:
    using value_type = T;

    PoolAllocator() = default;

    template<typename U>
    PoolAllocator(const PoolAllocator<U, BlockSize>&) noexcept {}

    T* allocate(std::size_t n) {
        const size_t bytes = n * sizeof(T);

        if (bytes > BlockSize) {
            // 블록 크기 초과 → 일반 할당
            return static_cast<T*>(::operator new(bytes));
        }

        if (!free_blocks) {
            // 새 블록 생성
            auto new_block = std::make_unique<Block>();
            free_blocks = new_block.get();
            free_blocks->next = nullptr;
            all_blocks.push_back(std::move(new_block));
        }

        // 프리 리스트에서 할당
        Block* block = free_blocks;
        free_blocks = free_blocks->next;

        return reinterpret_cast<T*>(block->data.data());
    }

    void deallocate(T* p, std::size_t n) noexcept {
        const size_t bytes = n * sizeof(T);

        if (bytes > BlockSize) {
            // 일반 할당한 경우
            ::operator delete(p);
            return;
        }

        // 프리 리스트에 반환
        Block* block = reinterpret_cast<Block*>(p);
        block->next = free_blocks;
        free_blocks = block;
    }

    template<typename U>
    struct rebind {
        using other = PoolAllocator<U, BlockSize>;
    };
};

template<typename T, typename U, size_t BlockSize>
bool operator==(const PoolAllocator<T, BlockSize>&,
                const PoolAllocator<U, BlockSize>&) noexcept {
    return true;
}

template<typename T, typename U, size_t BlockSize>
bool operator!=(const PoolAllocator<T, BlockSize>&,
                const PoolAllocator<U, BlockSize>&) noexcept {
    return false;
}
```

```cpp
// Stack Allocator (스택 메모리 사용)
template<typename T, size_t N>
class StackAllocator {
private:
    alignas(T) std::byte buffer[N * sizeof(T)];
    std::byte* current = buffer;

public:
    using value_type = T;

    StackAllocator() = default;

    template<typename U>
    StackAllocator(const StackAllocator<U, N>&) noexcept {}

    T* allocate(std::size_t n) {
        const size_t bytes = n * sizeof(T);
        const size_t remaining = (buffer + sizeof(buffer)) - current;

        if (bytes > remaining) {
            throw std::bad_alloc();  // 스택 공간 부족
        }

        T* result = reinterpret_cast<T*>(current);
        current += bytes;
        return result;
    }

    void deallocate(T*, std::size_t) noexcept {
        // 스택 할당자는 개별 해제 안 함
        // 스코프 종료 시 전체 리셋
    }

    void reset() noexcept {
        current = buffer;  // 스택 포인터 리셋
    }

    template<typename U>
    struct rebind {
        using other = StackAllocator<U, N>;
    };
};
```

```cpp
// 사용 예시: 임시 데이터 버퍼
void RenderFrame() {
    // ✅ 프레임마다 리셋되는 임시 버퍼
    StackAllocator<float, 10000> temp_allocator;

    // ✅ 스택 메모리 사용 (빠름, 캐시 친화적)
    std::vector<float, StackAllocator<float, 10000>>
        temp_vertices(temp_allocator);

    temp_vertices.reserve(1000);

    // 정점 데이터 생성
    for (int i = 0; i < 1000; ++i) {
        temp_vertices.push_back(/* ... */);
    }

    // 렌더링
    RenderVertices(temp_vertices.data(), temp_vertices.size());

    // ✅ 스코프 종료 시 자동 정리 (deallocate 호출 없음)
}
```

```cpp
// Performance comparison
void AllocationBenchmark() {
    constexpr size_t COUNT = 100000;

    // ❌ 기본 할당자 (느림)
    auto start = std::chrono::high_resolution_clock::now();
    {
        std::vector<int> v;
        for (size_t i = 0; i < COUNT; ++i) {
            v.push_back(i);  // 여러 번 재할당
        }
    }
    auto end = std::chrono::high_resolution_clock::now();
    std::cout << "Default allocator: "
              << std::chrono::duration<double, std::milli>(end - start).count()
              << "ms\n";

    // ✅ Pool 할당자 (빠름)
    start = std::chrono::high_resolution_clock::now();
    {
        std::vector<int, PoolAllocator<int>> v;
        v.reserve(COUNT);
        for (size_t i = 0; i < COUNT; ++i) {
            v.push_back(i);
        }
    }
    end = std::chrono::high_resolution_clock::now();
    std::cout << "Pool allocator: "
              << std::chrono::duration<double, std::milli>(end - start).count()
              << "ms\n";
}
```

</div>
<div>

**Custom Allocator 개념**:

1. **표준 할당자 문제점**
   - `malloc/free`: 느림 (시스템 호출)
   - 단편화 (Fragmentation)
   - 캐시 미스 증가

2. **Pool Allocator**
   - 고정 크기 블록 미리 할당
   - Free list로 빠른 할당/해제
   - 단편화 감소
   - **사용처**: 동일 크기 객체 많을 때

3. **Stack Allocator**
   - 스택 메모리 사용 (로컬 배열)
   - 선형 할당 (포인터만 증가)
   - 개별 해제 없음 (전체 리셋)
   - **사용처**: 임시 데이터 (프레임마다 리셋)

**Allocator 인터페이스 (C++17)**:
```cpp
template<typename T>
struct Allocator {
    using value_type = T;

    T* allocate(std::size_t n);
    void deallocate(T* p, std::size_t n);

    template<typename U>
    struct rebind {
        using other = Allocator<U>;
    };
};
```

**PMR (Polymorphic Memory Resource, C++17)**:
```cpp
#include <memory_resource>

std::pmr::monotonic_buffer_resource pool(8192);
std::pmr::vector<int> vec(&pool);  // PMR 할당자 사용

// 장점: 런타임에 할당자 교체 가능
```

**성능 비교**:

| Allocator | 할당 속도 | 해제 속도 | 메모리 효율 | 사용 난이도 |
|-----------|-----------|-----------|-------------|-------------|
| **malloc/free** | 느림 | 느림 | 보통 | 쉬움 |
| **Pool** | 빠름 | 빠름 | 좋음 (고정 크기) | 보통 |
| **Stack** | 매우 빠름 | 즉시 | 매우 좋음 | 어려움 |

**반도체 HMI 적용**:

```cpp
// 실시간 센서 데이터 버퍼
class SensorDataBuffer {
    // ✅ Pool allocator (재사용)
    using Allocator = PoolAllocator<SensorReading, 4096>;
    std::vector<SensorReading, Allocator> buffer;

public:
    void AddReading(const SensorReading& reading) {
        buffer.push_back(reading);  // ✅ 빠른 할당
    }
};

// 프레임별 UI 렌더링 데이터
void RenderUI() {
    // ✅ Stack allocator (임시 데이터)
    StackAllocator<Vertex, 10000> alloc;
    std::pmr::vector<Vertex> vertices(&alloc);

    // 정점 생성...

    // ✅ 스코프 종료 시 자동 정리
}
```

**주의사항**:
- 할당자는 **상태없음** (stateless) 권장
- `rebind` 구현 필수 (컨테이너 내부 노드용)
- 스레드 안전성 고려

</div>
</div>

---

## 4.2 RAII + Custom Deleter

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <memory>
#include <cstdio>
#include <GL/gl.h>

// ❌ 나쁜 예: C 리소스 수동 관리
void BadFileHandling() {
    FILE* file = fopen("data.txt", "r");
    if (!file) return;

    // ... 작업 ...

    fclose(file);  // ❌ 예외 발생 시 누수
}

// ✅ 좋은 예: unique_ptr + custom deleter
void GoodFileHandling() {
    auto file = std::unique_ptr<FILE, decltype(&fclose)>(
        fopen("data.txt", "r"),
        &fclose  // ✅ Custom deleter
    );

    if (!file) return;

    // ... 작업 ...

    // ✅ 자동으로 fclose() 호출
}
```

```cpp
// Lambda를 사용한 Custom Deleter
class GLResourceManager {
public:
    // OpenGL 텍스처 RAII
    using GLTexturePtr = std::unique_ptr<GLuint, std::function<void(GLuint*)>>;

    static GLTexturePtr CreateTexture(int width, int height) {
        GLuint* tex_id = new GLuint;
        glGenTextures(1, tex_id);
        glBindTexture(GL_TEXTURE_2D, *tex_id);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);

        // ✅ Lambda deleter
        return GLTexturePtr(tex_id, [](GLuint* id) {
            if (id && *id != 0) {
                glDeleteTextures(1, id);
            }
            delete id;
        });
    }

    // OpenGL 버퍼 RAII
    using GLBufferPtr = std::unique_ptr<GLuint, std::function<void(GLuint*)>>;

    static GLBufferPtr CreateBuffer() {
        GLuint* buf_id = new GLuint;
        glGenBuffers(1, buf_id);

        return GLBufferPtr(buf_id, [](GLuint* id) {
            if (id && *id != 0) {
                glDeleteBuffers(1, id);
            }
            delete id;
        });
    }
};
```

```cpp
// Functor를 사용한 Custom Deleter
struct SocketDeleter {
    void operator()(int* socket_fd) const {
        if (socket_fd && *socket_fd >= 0) {
            close(*socket_fd);
            std::cout << "Socket closed: " << *socket_fd << "\n";
        }
        delete socket_fd;
    }
};

class NetworkConnection {
private:
    std::unique_ptr<int, SocketDeleter> socket;

public:
    NetworkConnection(const char* host, int port) {
        int* fd = new int;
        *fd = socket(AF_INET, SOCK_STREAM, 0);

        if (*fd < 0) {
            delete fd;
            throw std::runtime_error("Socket creation failed");
        }

        // ... connect ...

        socket.reset(fd);  // ✅ SocketDeleter로 관리
    }

    void Send(const char* data, size_t len) {
        if (socket && *socket >= 0) {
            write(*socket, data, len);
        }
    }

    // ✅ 소멸 시 SocketDeleter 자동 호출
};
```

```cpp
// shared_ptr with custom deleter
class ThreadPool {
public:
    using ThreadHandle = std::shared_ptr<std::thread>;

    static ThreadHandle CreateThread(std::function<void()> task) {
        // ✅ shared_ptr + lambda deleter
        return ThreadHandle(
            new std::thread(task),
            [](std::thread* t) {
                if (t->joinable()) {
                    t->join();  // ✅ 자동 join
                    std::cout << "Thread joined\n";
                }
                delete t;
            }
        );
    }
};

void ThreadPoolDemo() {
    {
        auto thread1 = ThreadPool::CreateThread([]() {
            std::cout << "Worker thread running\n";
            std::this_thread::sleep_for(std::chrono::seconds(1));
        });

        auto thread2 = ThreadPool::CreateThread([]() {
            std::cout << "Another worker running\n";
        });

        // ✅ 스코프 종료 시 자동으로 join() 호출
    }  // thread1, thread2 삭제 → join() → delete

    std::cout << "All threads completed\n";
}
```

```cpp
// 복잡한 리소스 정리 로직
struct DatabaseDeleter {
    std::string connection_string;

    void operator()(DatabaseConnection* conn) const {
        if (conn) {
            std::cout << "Closing database: " << connection_string << "\n";
            conn->Commit();       // ✅ 커밋
            conn->Disconnect();   // ✅ 연결 해제
            conn->LogActivity();  // ✅ 로그 기록
            delete conn;
        }
    }
};

class DatabaseManager {
public:
    using DBPtr = std::unique_ptr<DatabaseConnection, DatabaseDeleter>;

    static DBPtr Connect(const std::string& conn_str) {
        auto* conn = new DatabaseConnection(conn_str);
        return DBPtr(conn, DatabaseDeleter{conn_str});
    }
};
```

</div>
<div>

**Custom Deleter 패턴**:

1. **목적**
   - unique_ptr/shared_ptr는 기본적으로 `delete` 호출
   - C 리소스 (FILE*, socket, OpenGL ID 등)는 다른 정리 함수 필요
   - Custom deleter로 정리 로직 커스터마이징

2. **Deleter 종류**

   **함수 포인터**:
   ```cpp
   unique_ptr<FILE, decltype(&fclose)> file(fopen("f.txt", "r"), &fclose);
   ```

   **Lambda**:
   ```cpp
   auto deleter = [](GLuint* id) { glDeleteTextures(1, id); delete id; };
   unique_ptr<GLuint, decltype(deleter)> tex(new GLuint, deleter);
   ```

   **Functor (함수 객체)**:
   ```cpp
   struct MyDeleter {
       void operator()(T* ptr) const { /* cleanup */ }
   };
   unique_ptr<T, MyDeleter> ptr(new T);
   ```

3. **unique_ptr vs shared_ptr deleter**

   **unique_ptr**:
   ```cpp
   unique_ptr<T, DeleterType> ptr;
   // DeleterType이 템플릿 인자
   // 타입이 다르면 다른 타입
   ```

   **shared_ptr**:
   ```cpp
   shared_ptr<T> ptr(new T, deleter);
   // deleter는 생성자 인자
   // 타입 무관 (type erasure)
   ```

**성능 고려**:

| Deleter 타입 | unique_ptr 크기 | 성능 |
|--------------|-----------------|------|
| **기본 delete** | 8바이트 | 최적 |
| **함수 포인터** | 16바이트 | 좋음 |
| **Stateless 람다** | 8바이트 | 최적 |
| **Stateful 람다** | 8+상태 크기 | 보통 |
| **Functor** | 8+상태 크기 | 보통 |

```cpp
// Stateless lambda (크기 증가 없음)
auto del1 = [](T* p) { delete p; };
unique_ptr<T, decltype(del1)> p1(new T, del1);  // 8 bytes

// Stateful lambda (상태 저장 → 크기 증가)
std::string name = "resource";
auto del2 = [name](T* p) { std::cout << name; delete p; };
unique_ptr<T, decltype(del2)> p2(new T, del2);  // 8 + sizeof(string)
```

**반도체 HMI 적용**:

```cpp
// 시리얼 포트 RAII
struct SerialPortDeleter {
    void operator()(int* fd) const {
        if (fd && *fd >= 0) {
            tcflush(*fd, TCIOFLUSH);  // 버퍼 비우기
            close(*fd);
            std::cout << "Serial port closed\n";
        }
        delete fd;
    }
};

using SerialPortPtr = unique_ptr<int, SerialPortDeleter>;

SerialPortPtr OpenSerialPort(const char* device) {
    int* fd = new int;
    *fd = open(device, O_RDWR | O_NOCTTY);

    if (*fd < 0) {
        delete fd;
        throw std::runtime_error("Failed to open serial port");
    }

    // ... 포트 설정 ...

    return SerialPortPtr(fd);  // ✅ 자동 정리
}
```

**주의사항**:
- Deleter는 예외 던지지 말 것 (`noexcept`)
- shared_ptr deleter는 복사 가능해야 함
- Deleter는 nullptr 체크해야 함

</div>
</div>

---

# 요약

## C++ 고급 기법 정리

<div class="grid grid-cols-2 gap-8">
<div>

**1. RAII (Resource Acquisition Is Initialization)**
- 생성자 = 리소스 획득
- 소멸자 = 리소스 해제
- 예외 안전성 보장
- 수동 관리 불필요

**2. Smart Pointers**

**unique_ptr**:
- 단독 소유권
- 복사 불가, 이동 가능
- 오버헤드 없음 (8바이트)
- 사용: 기본 선택

**shared_ptr**:
- 공유 소유권
- 참조 카운팅
- 오버헤드 있음 (16바이트 + control block)
- 사용: 진짜 공유 필요할 때만

**weak_ptr**:
- 약한 참조
- 순환 참조 해결
- lock()으로 임시 접근
- 사용: Observer, 캐시

**3. Move Semantics**
- L-value vs R-value
- 이동 생성자/대입
- std::move (캐스팅)
- 성능 향상 (복사 제거)

**4. Perfect Forwarding**
- Universal Reference (T&&)
- std::forward
- 가변 인자 템플릿
- emplace_back 활용

</div>
<div>

**반도체 HMI 설계 원칙**:

```cpp
// ✅ 권장 패턴
class EquipmentController {
    // 소유 → unique_ptr
    unique_ptr<SerialPort> port;

    // 공유 → shared_ptr
    shared_ptr<RecipeData> current_recipe;

    // 관찰 → weak_ptr
    weak_ptr<Logger> logger;

    // OpenGL → RAII 래퍼
    GLTexture wafer_map_texture;
    GLBuffer vertex_buffer;

public:
    // Perfect forwarding 팩토리
    template<typename T, typename... Args>
    unique_ptr<T> CreateComponent(Args&&... args) {
        return make_unique<T>(forward<Args>(args)...);
    }

    // Move-only API
    void SetRecipe(shared_ptr<RecipeData> recipe) {
        current_recipe = move(recipe);
    }
};
```

**성능 최적화 체크리스트**:
- ✅ unique_ptr을 기본으로 사용
- ✅ shared_ptr은 진짜 필요할 때만
- ✅ 함수 반환은 값 반환 (RVO)
- ✅ 함수 인자는 const& (읽기) 또는 && (소유)
- ✅ emplace_back > push_back
- ✅ make_unique/make_shared 사용
- ✅ std::move로 불필요한 복사 제거
- ❌ raw pointer 최소화
- ❌ new/delete 직접 사용 금지

</div>
</div>

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

## 🚀 **심화 실습 - 커스텀 위젯 및 실시간 데이터 처리**

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

## 💼 **Hands-on 프로젝트 - 반도체 장비 모니터링 HMI 프로토타입**

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

## 🎨 **심화 학습 - ImGUI 스타일링 및 테마 시스템**

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

## 🎯 **성능 최적화 - 실시간 시스템 최적화 기법**

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
