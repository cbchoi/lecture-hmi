
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

