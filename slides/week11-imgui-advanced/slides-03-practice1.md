#include "ui_components/process_flow_widget.h"
#include "visualization/advanced_3d_engine.h"
#include "animation/tween_system.h"
#include "input/gesture_recognizer.h"

namespace SemiconductorHMI {

class AdvancedSemiconductorHMIApp : public HMIApplication {
private:
    // 3D 시각화 엔진
    std::unique_ptr<Visualization::Advanced3DEngine> engine_3d;

    // UI 컴포넌트들
    std::unique_ptr<UI::WaferMapWidget> wafer_map;
    std::unique_ptr<UI::ProcessFlowWidget> process_flow;

    // 시뮬레이션 데이터
    struct EquipmentData {
        float chamber_pressure = 0.05f;     // Torr
        float substrate_temp = 400.0f;      // Celsius
        float rf_power = 1000.0f;           // Watts
        float gas_flow_rate = 50.0f;        // sccm
        bool plasma_on = false;
        bool door_open = false;
    } equipment_data;

    // UI 상태
    bool show_3d_view = true;
    bool show_wafer_map = true;
    bool show_process_flow = true;
    bool show_performance = true;
    bool simulation_running = false;

    // 성능 메트릭
    HighPerformanceRenderer performance_renderer;
    PerformanceProfiler profiler;

public:
    AdvancedSemiconductorHMIApp()
        : HMIApplication("Advanced Semiconductor HMI Platform", 1920, 1080) {}

protected:
    void OnStartup() override {
        // 3D 엔진 초기화
        engine_3d = std::make_unique<Visualization::Advanced3DEngine>();
        if (!engine_3d->Initialize()) {
            throw std::runtime_error("Failed to initialize 3D engine");
        }

        // UI 컴포넌트 초기화
        wafer_map = std::make_unique<UI::WaferMapWidget>(300, 5.0f);
        process_flow = std::make_unique<UI::ProcessFlowWidget>();

        // 프로세스 플로우 설정
        process_flow->LoadProcessDefinition("cvd_process.json");

        // 시뮬레이션 데이터 생성
        GenerateSimulatedWaferData();

        // 성능 프로파일러 시작
        profiler.BeginFrame();
    }

    void OnUpdate(float delta_time) override {
        // 애니메이션 시스템 업데이트
        Animation::g_tween_manager.Update(delta_time);

        // 3D 엔진 업데이트
        engine_3d->Update(delta_time);

        // 시뮬레이션 업데이트
        if (simulation_running) {
            UpdateSimulation(delta_time);
        }

        // 성능 메트릭 업데이트
        performance_renderer.PrintMemoryStats();
    }

    void OnRender() override {
        // 성능 프로파일링 시작
        profiler.BeginFrame();

        // 메인 메뉴바
        RenderMainMenuBar();

        // 도킹 스페이스 설정
        SetupDockSpace();

        // 각 패널 렌더링
        if (show_3d_view) {
            engine_3d->RenderImGuiPanel();
        }

        if (show_wafer_map) {
            wafer_map->Render();
        }

        if (show_process_flow) {
            process_flow->Render();
        }

        if (show_performance) {
            profiler.RenderPerformanceGraph();
        }

        // 상태 패널
        RenderStatusPanel();

        // 제어 패널
        RenderControlPanel();

        // 성능 프로파일링 종료
        profiler.EndFrame();
    }

private:
    void GenerateSimulatedWaferData() {
        std::vector<UI::WaferDie> wafer_data;
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<float> yield_dist(0.0f, 1.0f);
        std::uniform_real_distribution<float> value_dist(0.8f, 1.2f);

        // 300mm 웨이퍼, 5mm 다이 크기
        float wafer_radius = 150.0f;  // mm
        float die_size = 5.0f;        // mm

        for (int y = -30; y <= 30; ++y) {
            for (int x = -30; x <= 30; ++x) {
                float die_center_x = x * die_size;
                float die_center_y = y * die_size;
                float distance = std::sqrt(die_center_x * die_center_x + die_center_y * die_center_y);

                if (distance <= wafer_radius - die_size * 0.5f) {
                    UI::WaferDie die;
                    die.x = x;
                    die.y = y;

                    // 가장자리로 갈수록 수율 감소 시뮬레이션
                    float normalized_distance = distance / wafer_radius;
                    float yield_probability = 0.95f - normalized_distance * 0.15f;

                    if (yield_dist(gen) < yield_probability) {
                        die.state = UI::WaferDieState::Good;
                        die.bin_code = "1";
                    } else {
                        die.state = UI::WaferDieState::Fail;
                        die.bin_code = "F";
                    }

                    die.value = value_dist(gen);
                    wafer_data.push_back(die);
                }
            }
        }

        wafer_map->LoadWaferData(wafer_data);
    }

    void UpdateSimulation(float delta_time) {
        static float sim_time = 0.0f;
        sim_time += delta_time;

        // 장비 데이터 시뮬레이션
        equipment_data.chamber_pressure = 0.05f + 0.01f * std::sin(sim_time * 0.5f);
        equipment_data.substrate_temp = 400.0f + 50.0f * std::sin(sim_time * 0.2f);
        equipment_data.rf_power = 1000.0f + 200.0f * std::sin(sim_time * 0.3f);

        // 3D 엔진에 데이터 전달
        engine_3d->SetEquipmentData("pressure", equipment_data.chamber_pressure);
        engine_3d->SetEquipmentData("temperature", equipment_data.substrate_temp);
        engine_3d->SetEquipmentData("power", equipment_data.rf_power);

        // 플라즈마 상태에 따른 하이라이트
        engine_3d->HighlightComponent("susceptor", equipment_data.plasma_on);

        // 프로세스 플로우 업데이트
        if (equipment_data.plasma_on) {
            process_flow->SetStepStatus(5, UI::ProcessStepStatus::Running, std::fmod(sim_time * 0.1f, 1.0f));
        }
    }

    void RenderMainMenuBar() {
        if (ImGui::BeginMainMenuBar()) {
            if (ImGui::BeginMenu("View")) {
                ImGui::MenuItem("3D Visualization", nullptr, &show_3d_view);
                ImGui::MenuItem("Wafer Map", nullptr, &show_wafer_map);
                ImGui::MenuItem("Process Flow", nullptr, &show_process_flow);
                ImGui::MenuItem("Performance", nullptr, &show_performance);
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("Equipment")) {
                if (ImGui::MenuItem("Start Process")) {
                    StartProcess();
                }
                if (ImGui::MenuItem("Stop Process")) {
                    StopProcess();
                }
                ImGui::Separator();
                if (ImGui::MenuItem("Open Chamber", nullptr, equipment_data.door_open)) {
                    ToggleChamberDoor();
                }
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("Simulation")) {
                ImGui::MenuItem("Enable Simulation", nullptr, &simulation_running);
                if (ImGui::MenuItem("Reset Equipment")) {
                    ResetEquipment();
                }
                ImGui::EndMenu();
            }

            ImGui::EndMainMenuBar();
        }
    }

    void SetupDockSpace() {
        static bool dockspace_open = true;
        ImGuiDockNodeFlags dockspace_flags = ImGuiDockNodeFlags_None;

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

    void RenderStatusPanel() {
        if (ImGui::Begin("Equipment Status")) {
            ImGui::Text("Chamber Status:");
            ImGui::Separator();

            // 상태 표시 (색상 코딩)
            ImVec4 pressure_color = equipment_data.chamber_pressure < 0.1f ?
                ImVec4(0, 1, 0, 1) : ImVec4(1, 1, 0, 1);
            ImGui::TextColored(pressure_color, "Pressure: %.3f Torr", equipment_data.chamber_pressure);

            ImVec4 temp_color = (equipment_data.substrate_temp >= 380.0f && equipment_data.substrate_temp <= 420.0f) ?
                ImVec4(0, 1, 0, 1) : ImVec4(1, 0, 0, 1);
            ImGui::TextColored(temp_color, "Temperature: %.1f °C", equipment_data.substrate_temp);

            ImVec4 power_color = equipment_data.rf_power > 800.0f ?
                ImVec4(0, 1, 0, 1) : ImVec4(1, 1, 0, 1);
            ImGui::TextColored(power_color, "RF Power: %.0f W", equipment_data.rf_power);

            ImGui::Text("Gas Flow: %.1f sccm", equipment_data.gas_flow_rate);

            ImGui::Separator();

            // 플라즈마 상태
            if (equipment_data.plasma_on) {
                ImGui::TextColored(ImVec4(0, 1, 1, 1), "⚡ PLASMA ON");
            } else {
                ImGui::TextColored(ImVec4(0.5f, 0.5f, 0.5f, 1), "⚪ PLASMA OFF");
            }

            // 챔버 도어 상태
            if (equipment_data.door_open) {
                ImGui::TextColored(ImVec4(1, 1, 0, 1), "🚪 DOOR OPEN");
            } else {
                ImGui::TextColored(ImVec4(0, 1, 0, 1), "🔒 DOOR CLOSED");
            }
        }
        ImGui::End();
    }

    void RenderControlPanel() {
        if (ImGui::Begin("Equipment Control")) {
            ImGui::Text("Process Control:");

            if (ImGui::Button("Start Plasma", ImVec2(120, 30))) {
                equipment_data.plasma_on = true;
            }
            ImGui::SameLine();
            if (ImGui::Button("Stop Plasma", ImVec2(120, 30))) {
                equipment_data.plasma_on = false;
            }

            ImGui::Separator();

            ImGui::Text("Manual Control:");
            ImGui::SliderFloat("Pressure", &equipment_data.chamber_pressure, 0.001f, 0.2f, "%.4f Torr");
            ImGui::SliderFloat("Temperature", &equipment_data.substrate_temp, 200.0f, 800.0f, "%.1f °C");
            ImGui::SliderFloat("RF Power", &equipment_data.rf_power, 0.0f, 2000.0f, "%.0f W");
            ImGui::SliderFloat("Gas Flow", &equipment_data.gas_flow_rate, 0.0f, 100.0f, "%.1f sccm");

            ImGui::Separator();

            if (ImGui::Button("Emergency Stop", ImVec2(-1, 40))) {
                EmergencyStop();
            }
        }
        ImGui::End();
    }

    void StartProcess() {
        simulation_running = true;
        equipment_data.plasma_on = true;

        // 애니메이션으로 상태 전환
        Animation::g_tween_manager.TweenFloat(&equipment_data.rf_power,
            equipment_data.rf_power, 1200.0f, 2.0f, Animation::EaseType::EaseInOutQuad);
    }

    void StopProcess() {
        simulation_running = false;
        equipment_data.plasma_on = false;

        // 파워 점진적 감소
        Animation::g_tween_manager.TweenFloat(&equipment_data.rf_power,
            equipment_data.rf_power, 0.0f, 3.0f, Animation::EaseType::EaseOutQuad);
    }

    void ToggleChamberDoor() {
        equipment_data.door_open = !equipment_data.door_open;
        engine_3d->SetEquipmentData("door_open", equipment_data.door_open ? 1.0f : 0.0f);
    }

    void EmergencyStop() {
        simulation_running = false;
        equipment_data.plasma_on = false;
        equipment_data.rf_power = 0.0f;

        // 긴급 정지 이펙트
        // Animation::g_effect_manager.CreateAlarmEffect(ImVec2(960, 540));
    }

    void ResetEquipment() {
        equipment_data = EquipmentData{};
        simulation_running = false;
    }
};

} // namespace SemiconductorHMI
```

---

## 실습 1: 고급 3D 시각화 및 OpenGL 통합

### 실습 목표
- ImGui와 OpenGL을 통합한 3D 렌더링 시스템 구현
- 반도체 장비의 3D 모델링 및 실시간 시각화
- 카메라 컨트롤과 상호작용 구현
- 셰이더 기반 고급 시각 효과

### 3D 카메라 시스템 구현

#### 1. 고급 카메라 컨트롤러
```cpp
// Advanced3DCamera.h
#pragma once
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/quaternion.hpp>
#include <imgui.h>

namespace SemiconductorHMI {

enum class CameraMode {
    FreeRotation,
    OrbitTarget,
    FirstPerson,
    TopDown
};

class Advanced3DCamera {
private:
    // 카메라 상태
    glm::vec3 position;
    glm::vec3 target;
    glm::vec3 up;
    glm::quat orientation;

    // 뷰 파라미터
    float fov;
    float aspect_ratio;
    float near_plane;
    float far_plane;

    // 컨트롤 상태
    CameraMode mode;
    bool is_dragging;
    ImVec2 last_mouse_pos;
    float orbit_distance;
    float rotation_speed;
    float zoom_speed;
    float pan_speed;

    // 애니메이션
    glm::vec3 animation_start_pos;
    glm::vec3 animation_target_pos;
    glm::quat animation_start_rot;
    glm::quat animation_target_rot;
    float animation_time;
    float animation_duration;
    bool is_animating;

public:
    Advanced3DCamera(float viewport_width, float viewport_height)
        : position(0.0f, 5.0f, 10.0f)
        , target(0.0f, 0.0f, 0.0f)
        , up(0.0f, 1.0f, 0.0f)
        , orientation(1.0f, 0.0f, 0.0f, 0.0f)
        , fov(45.0f)
        , aspect_ratio(viewport_width / viewport_height)
        , near_plane(0.1f)
        , far_plane(1000.0f)
        , mode(CameraMode::OrbitTarget)
        , is_dragging(false)
        , orbit_distance(15.0f)
        , rotation_speed(0.5f)
        , zoom_speed(1.0f)
        , pan_speed(0.01f)
        , animation_time(0.0f)
        , animation_duration(1.0f)
        , is_animating(false)
    {
        UpdateOrbitPosition();
    }

    void Update(float delta_time) {
        if (is_animating) {
            UpdateAnimation(delta_time);
        }

        HandleInput(delta_time);
        UpdateMatrices();
    }

    void HandleInput(float delta_time) {
        ImGuiIO& io = ImGui::GetIO();
        ImVec2 mouse_pos = io.MousePos;
        ImVec2 mouse_delta = ImVec2(mouse_pos.x - last_mouse_pos.x,
                                   mouse_pos.y - last_mouse_pos.y);

        // 마우스 드래그 처리
        if (ImGui::IsMouseDown(ImGuiMouseButton_Left)) {
            if (!is_dragging) {
                is_dragging = true;
                last_mouse_pos = mouse_pos;
            } else {
                HandleMouseDrag(mouse_delta, delta_time);
            }
        } else {
            is_dragging = false;
        }

        // 마우스 휠 줌
        if (io.MouseWheel != 0.0f) {
            HandleZoom(io.MouseWheel, delta_time);
        }

        // 키보드 이동
        HandleKeyboard(delta_time);

        last_mouse_pos = mouse_pos;
    }

    void HandleMouseDrag(ImVec2 delta, float delta_time) {
        switch (mode) {
        case CameraMode::OrbitTarget:
            HandleOrbitDrag(delta, delta_time);
            break;
        case CameraMode::FreeRotation:
            HandleFreeDrag(delta, delta_time);
            break;
        case CameraMode::FirstPerson:
            HandleFirstPersonDrag(delta, delta_time);
            break;
        }
    }

    void HandleOrbitDrag(ImVec2 delta, float delta_time) {
        // 구면 좌표계에서 회전
        float theta_delta = -delta.x * rotation_speed * delta_time;
        float phi_delta = -delta.y * rotation_speed * delta_time;

        // 현재 구면 좌표 계산
        glm::vec3 to_camera = position - target;
        float radius = glm::length(to_camera);

        float theta = atan2(to_camera.z, to_camera.x);
        float phi = acos(to_camera.y / radius);

        // 새로운 각도 적용
        theta += theta_delta;
        phi += phi_delta;
        phi = glm::clamp(phi, 0.1f, 3.14159f - 0.1f); // 상하 제한

        // 새로운 위치 계산
        position.x = target.x + radius * sin(phi) * cos(theta);
        position.y = target.y + radius * cos(phi);
        position.z = target.z + radius * sin(phi) * sin(theta);

        orbit_distance = radius;
    }

    void HandleFreeDrag(ImVec2 delta, float delta_time) {
        // 쿼터니언 기반 자유 회전
        float yaw_delta = -delta.x * rotation_speed * delta_time;
        float pitch_delta = -delta.y * rotation_speed * delta_time;

        glm::quat yaw_rotation = glm::angleAxis(yaw_delta, glm::vec3(0, 1, 0));
        glm::quat pitch_rotation = glm::angleAxis(pitch_delta, glm::vec3(1, 0, 0));

        orientation = yaw_rotation * orientation * pitch_rotation;
        orientation = glm::normalize(orientation);

        // 위치 업데이트
        glm::mat4 rotation_matrix = glm::mat4_cast(orientation);
        glm::vec3 forward = -glm::vec3(rotation_matrix[2]);
        target = position + forward * orbit_distance;
    }

    void HandleFirstPersonDrag(ImVec2 delta, float delta_time) {
        // 1인칭 시점 회전
        float yaw_delta = -delta.x * rotation_speed * delta_time;
        float pitch_delta = -delta.y * rotation_speed * delta_time;

        glm::quat yaw_rotation = glm::angleAxis(yaw_delta, up);
        glm::quat pitch_rotation = glm::angleAxis(pitch_delta, glm::vec3(1, 0, 0));

        orientation = yaw_rotation * orientation * pitch_rotation;
        orientation = glm::normalize(orientation);

        // 타겟 업데이트
        glm::mat4 rotation_matrix = glm::mat4_cast(orientation);
        glm::vec3 forward = -glm::vec3(rotation_matrix[2]);
        target = position + forward;
    }

    void HandleZoom(float wheel_delta, float delta_time) {
        switch (mode) {
        case CameraMode::OrbitTarget:
            // 궤도 거리 조정
            orbit_distance -= wheel_delta * zoom_speed;
            orbit_distance = glm::clamp(orbit_distance, 1.0f, 100.0f);
            UpdateOrbitPosition();
            break;
        case CameraMode::FirstPerson:
        case CameraMode::FreeRotation:
            // FOV 조정
            fov -= wheel_delta * 2.0f;
            fov = glm::clamp(fov, 10.0f, 120.0f);
            break;
        }
    }

    void HandleKeyboard(float delta_time) {
        ImGuiIO& io = ImGui::GetIO();
        float move_speed = 5.0f * delta_time;

        glm::vec3 forward = glm::normalize(target - position);
        glm::vec3 right = glm::normalize(glm::cross(forward, up));

        if (io.KeysDown[ImGuiKey_W]) position += forward * move_speed;
        if (io.KeysDown[ImGuiKey_S]) position -= forward * move_speed;
        if (io.KeysDown[ImGuiKey_A]) position -= right * move_speed;
        if (io.KeysDown[ImGuiKey_D]) position += right * move_speed;
        if (io.KeysDown[ImGuiKey_Q]) position += up * move_speed;
        if (io.KeysDown[ImGuiKey_E]) position -= up * move_speed;

        if (mode == CameraMode::FirstPerson) {
            target = position + forward;
        }
    }

    void UpdateOrbitPosition() {
        glm::vec3 to_camera = glm::normalize(position - target);
        position = target + to_camera * orbit_distance;
    }

    void UpdateMatrices() {
        // 뷰 매트릭스 계산
        view_matrix = glm::lookAt(position, target, up);

        // 프로젝션 매트릭스 계산
        projection_matrix = glm::perspective(glm::radians(fov), aspect_ratio, near_plane, far_plane);
    }

    void AnimateTo(glm::vec3 new_position, glm::vec3 new_target, float duration = 1.0f) {
        animation_start_pos = position;
        animation_target_pos = new_position;
        animation_start_rot = glm::quatLookAt(glm::normalize(target - position), up);
        animation_target_rot = glm::quatLookAt(glm::normalize(new_target - new_position), up);

        animation_time = 0.0f;
        animation_duration = duration;
        is_animating = true;
    }

    void UpdateAnimation(float delta_time) {
        animation_time += delta_time;
        float t = glm::clamp(animation_time / animation_duration, 0.0f, 1.0f);

        // 부드러운 보간을 위한 easing function
        float eased_t = EaseInOutCubic(t);

        // 위치 보간
        position = glm::mix(animation_start_pos, animation_target_pos, eased_t);

        // 회전 보간 (slerp)
        glm::quat current_rot = glm::slerp(animation_start_rot, animation_target_rot, eased_t);
