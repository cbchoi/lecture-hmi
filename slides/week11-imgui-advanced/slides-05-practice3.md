        light_count_location = glGetUniformLocation(program_id, "uLightCount");

        albedo_location = glGetUniformLocation(program_id, "uAlbedo");
        metallic_location = glGetUniformLocation(program_id, "uMetallic");
        roughness_location = glGetUniformLocation(program_id, "uRoughness");
        ao_location = glGetUniformLocation(program_id, "uAO");
    }

    GLuint CreateShaderProgram(const char* vertex_source, const char* fragment_source) {
        // 셰이더 컴파일 코드 (이전 예제와 동일)
        GLuint vertex_shader = CompileShader(GL_VERTEX_SHADER, vertex_source);
        GLuint fragment_shader = CompileShader(GL_FRAGMENT_SHADER, fragment_source);

        if (vertex_shader == 0 || fragment_shader == 0) {
            return 0;
        }

        GLuint program = glCreateProgram();
        glAttachShader(program, vertex_shader);
        glAttachShader(program, fragment_shader);
        glLinkProgram(program);

        GLint success;
        glGetProgramiv(program, GL_LINK_STATUS, &success);
        if (!success) {
            char info_log[512];
            glGetProgramInfoLog(program, 512, NULL, info_log);
            printf("Shader program linking failed: %s\n", info_log);
            return 0;
        }

        glDeleteShader(vertex_shader);
        glDeleteShader(fragment_shader);

        return program;
    }

    GLuint CompileShader(GLenum type, const char* source) {
        GLuint shader = glCreateShader(type);
        glShaderSource(shader, 1, &source, NULL);
        glCompileShader(shader);

        GLint success;
        glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
        if (!success) {
            char info_log[512];
            glGetShaderInfoLog(shader, 512, NULL, info_log);
            printf("Shader compilation failed: %s\n", info_log);
            return 0;
        }

        return shader;
    }
};

} // namespace SemiconductorHMI
```

---

## 실습 3: 고급 ImGui 위젯 및 커스텀 렌더링

### 실습 목표
- 커스텀 ImGui 위젯 개발
- 2D/3D 혼합 인터페이스 구현
- 고급 시각화 컴포넌트 (히트맵, 3D 그래프)
- 인터랙티브 3D 씬 편집기

### 커스텀 3D 위젯 구현

#### 1. 3D 뷰포트 위젯
```cpp
// Custom3DWidget.h
#pragma once
#include <imgui.h>
#include <imgui_internal.h>
#include <memory>
#include <vector>
#include <functional>

namespace SemiconductorHMI {

class Custom3DViewport {
private:
    std::unique_ptr<Advanced3DCamera> camera;
    std::unique_ptr<PBRShader> pbr_shader;
    std::vector<std::unique_ptr<Model>> models;

    GLuint framebuffer;
    GLuint color_texture;
    GLuint depth_texture;

    ImVec2 viewport_size;
    bool is_initialized;
    bool is_focused;

    // 인터랙션 상태
    bool is_dragging_gizmo;
    int selected_object;
    glm::vec3 gizmo_position;

    // 렌더링 설정
    bool enable_wireframe;
    bool enable_grid;
    bool enable_shadows;
    float grid_size;
    glm::vec3 background_color;

    // 조명 설정
    std::vector<glm::vec3> light_positions;
    std::vector<glm::vec3> light_colors;

public:
    Custom3DViewport(float width = 800.0f, float height = 600.0f)
        : viewport_size(width, height), is_initialized(false), is_focused(false)
        , is_dragging_gizmo(false), selected_object(-1), gizmo_position(0.0f)
        , enable_wireframe(false), enable_grid(true), enable_shadows(true)
        , grid_size(10.0f), background_color(0.2f, 0.2f, 0.2f) {

        camera = std::make_unique<Advanced3DCamera>(width, height);
        pbr_shader = std::make_unique<PBRShader>();

        // 기본 조명 설정
        light_positions = {
            glm::vec3(10.0f, 10.0f, 10.0f),
            glm::vec3(-10.0f, 10.0f, 10.0f),
            glm::vec3(0.0f, -10.0f, 5.0f)
        };

        light_colors = {
            glm::vec3(300.0f, 300.0f, 300.0f),
            glm::vec3(200.0f, 200.0f, 250.0f),
            glm::vec3(100.0f, 100.0f, 100.0f)
        };
    }

    bool Initialize() {
        if (!pbr_shader->Initialize()) {
            return false;
        }

        CreateFramebuffer();
        is_initialized = true;
        return true;
    }

    void Render(const char* window_name = "3D Viewport") {
        if (!is_initialized) return;

        ImGui::Begin(window_name, nullptr, ImGuiWindowFlags_MenuBar);

        // 메뉴바 렌더링
        RenderMenuBar();

        // 뷰포트 크기 체크 및 업데이트
        ImVec2 content_region = ImGui::GetContentRegionAvail();
        if (content_region.x != viewport_size.x || content_region.y != viewport_size.y) {
            ResizeViewport(content_region.x, content_region.y);
        }

        // 포커스 상태 업데이트
        is_focused = ImGui::IsWindowFocused();

        // 3D 씬 렌더링
        Render3DScene();

        // 텍스처를 ImGui 이미지로 표시
        ImGui::Image((void*)(intptr_t)color_texture, viewport_size, ImVec2(0, 1), ImVec2(1, 0));

        // 뷰포트 위의 오버레이 UI
        RenderOverlayUI();

        // 입력 처리
        HandleInput();

        ImGui::End();

        // 사이드 패널들
        RenderControlPanels();
    }

private:
    void CreateFramebuffer() {
        // 프레임버퍼 생성
        glGenFramebuffers(1, &framebuffer);
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);

        // 컬러 텍스처 생성
        glGenTextures(1, &color_texture);
        glBindTexture(GL_TEXTURE_2D, color_texture);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, (int)viewport_size.x, (int)viewport_size.y,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, NULL);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color_texture, 0);

        // 깊이 텍스처 생성
        glGenTextures(1, &depth_texture);
        glBindTexture(GL_TEXTURE_2D, depth_texture);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, (int)viewport_size.x, (int)viewport_size.y,
                     0, GL_DEPTH_COMPONENT, GL_FLOAT, NULL);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depth_texture, 0);

        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
            printf("Framebuffer not complete!\n");
        }

        glBindFramebuffer(GL_FRAMEBUFFER, 0);
    }

    void ResizeViewport(float width, float height) {
        viewport_size = ImVec2(width, height);
        camera->SetAspectRatio(width / height);

        // 텍스처 크기 조정
        glBindTexture(GL_TEXTURE_2D, color_texture);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, (int)width, (int)height, 0, GL_RGBA, GL_UNSIGNED_BYTE, NULL);

        glBindTexture(GL_TEXTURE_2D, depth_texture);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, (int)width, (int)height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, NULL);
    }

    void Render3DScene() {
        // 프레임버퍼 바인딩
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
        glViewport(0, 0, (int)viewport_size.x, (int)viewport_size.y);

        // 클리어
        glClearColor(background_color.r, background_color.g, background_color.b, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // 깊이 테스트 활성화
        glEnable(GL_DEPTH_TEST);

        // 카메라 업데이트
        camera->Update(ImGui::GetIO().DeltaTime);

        // 셰이더 사용
        pbr_shader->Use();
        pbr_shader->SetCamera(camera->GetPosition());
        pbr_shader->SetLights(light_positions, light_colors);

        // 그리드 렌더링
        if (enable_grid) {
            RenderGrid();
        }

        // 모델들 렌더링
        for (size_t i = 0; i < models.size(); ++i) {
            glm::mat4 model_matrix = models[i]->GetTransform();

            // 선택된 객체 하이라이트
            if ((int)i == selected_object) {
                // 아웃라인 효과를 위한 스텐실 렌더링 등
            }

            pbr_shader->SetMatrices(model_matrix, camera->GetViewMatrix(), camera->GetProjectionMatrix());

            // 와이어프레임 모드
            if (enable_wireframe) {
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
            }

            models[i]->Draw(pbr_shader->GetProgramID());

            if (enable_wireframe) {
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
            }
        }

        // 기즈모 렌더링
        if (selected_object >= 0) {
            RenderGizmo();
        }

        glBindFramebuffer(GL_FRAMEBUFFER, 0);
    }

    void RenderGrid() {
        // 간단한 그리드 렌더링 구현
        // 실제로는 별도의 그리드 셰이더와 지오메트리 필요
    }

    void RenderGizmo() {
        // 3D 변환 기즈모 렌더링
        // 이동, 회전, 스케일 핸들 표시
    }

    void RenderMenuBar() {
        if (ImGui::BeginMenuBar()) {
            if (ImGui::BeginMenu("뷰")) {
                ImGui::MenuItem("와이어프레임", nullptr, &enable_wireframe);
                ImGui::MenuItem("그리드", nullptr, &enable_grid);
                ImGui::MenuItem("그림자", nullptr, &enable_shadows);
                ImGui::Separator();

                if (ImGui::BeginMenu("카메라 프리셋")) {
                    if (ImGui::MenuItem("정면")) camera->SetPresetView("Front");
                    if (ImGui::MenuItem("상단")) camera->SetPresetView("Top");
                    if (ImGui::MenuItem("측면")) camera->SetPresetView("Side");
                    if (ImGui::MenuItem("등각투상")) camera->SetPresetView("Isometric");
                    ImGui::EndMenu();
                }

                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("객체")) {
                if (ImGui::MenuItem("큐브 추가")) {
                    AddCube();
                }
                if (ImGui::MenuItem("구체 추가")) {
                    AddSphere();
                }
                if (ImGui::MenuItem("실린더 추가")) {
                    AddCylinder();
                }
                ImGui::Separator();
                if (ImGui::MenuItem("선택된 객체 삭제") && selected_object >= 0) {
                    DeleteSelectedObject();
                }
                ImGui::EndMenu();
            }

            ImGui::EndMenuBar();
        }
    }

    void RenderOverlayUI() {
        // 뷰포트 위에 표시되는 오버레이 UI
        ImDrawList* draw_list = ImGui::GetWindowDrawList();
        ImVec2 canvas_pos = ImGui::GetCursorScreenPos() - ImVec2(0, viewport_size.y);

        // 좌표계 표시
        RenderCoordinateSystem(draw_list, canvas_pos);

        // 정보 패널
        RenderInfoPanel(draw_list, canvas_pos);
    }

    void RenderCoordinateSystem(ImDrawList* draw_list, ImVec2 canvas_pos) {
        ImVec2 origin = ImVec2(canvas_pos.x + 50, canvas_pos.y + viewport_size.y - 50);
        float axis_length = 30.0f;

        // X축 (빨강)
        draw_list->AddLine(origin,
                          ImVec2(origin.x + axis_length, origin.y),
                          IM_COL32(255, 0, 0, 255), 2.0f);
        draw_list->AddText(ImVec2(origin.x + axis_length + 5, origin.y - 8),
                          IM_COL32(255, 0, 0, 255), "X");

        // Y축 (초록)
        draw_list->AddLine(origin,
                          ImVec2(origin.x, origin.y - axis_length),
                          IM_COL32(0, 255, 0, 255), 2.0f);
        draw_list->AddText(ImVec2(origin.x - 8, origin.y - axis_length - 15),
                          IM_COL32(0, 255, 0, 255), "Y");

        // Z축 (파랑) - 2D에서는 대각선으로 표현
        draw_list->AddLine(origin,
                          ImVec2(origin.x - axis_length * 0.7f, origin.y + axis_length * 0.7f),
                          IM_COL32(0, 0, 255, 255), 2.0f);
        draw_list->AddText(ImVec2(origin.x - axis_length * 0.7f - 15, origin.y + axis_length * 0.7f),
                          IM_COL32(0, 0, 255, 255), "Z");
    }

    void RenderInfoPanel(ImDrawList* draw_list, ImVec2 canvas_pos) {
        ImVec2 panel_pos = ImVec2(canvas_pos.x + 10, canvas_pos.y + 10);
        ImVec2 panel_size = ImVec2(200, 80);

        // 반투명 배경
        draw_list->AddRectFilled(panel_pos,
                                ImVec2(panel_pos.x + panel_size.x, panel_pos.y + panel_size.y),
                                IM_COL32(0, 0, 0, 128), 5.0f);

        // 정보 텍스트
        glm::vec3 cam_pos = camera->GetPosition();
        char info_text[256];
        snprintf(info_text, sizeof(info_text),
                "카메라: (%.1f, %.1f, %.1f)\n"
                "객체 수: %zu\n"
                "선택됨: %s",
                cam_pos.x, cam_pos.y, cam_pos.z,
                models.size(),
                selected_object >= 0 ? "예" : "없음");

        draw_list->AddText(ImVec2(panel_pos.x + 10, panel_pos.y + 10),
                          IM_COL32(255, 255, 255, 255), info_text);
    }

    void RenderControlPanels() {
        // 객체 속성 패널
        if (ImGui::Begin("객체 속성")) {
            if (selected_object >= 0 && selected_object < (int)models.size()) {
                RenderObjectProperties();
            } else {
                ImGui::Text("선택된 객체가 없습니다.");
            }
        }
        ImGui::End();

        // 조명 설정 패널
        if (ImGui::Begin("조명 설정")) {
            RenderLightingControls();
        }
        ImGui::End();

        // 렌더링 설정 패널
        if (ImGui::Begin("렌더링 설정")) {
            RenderRenderingControls();
        }
        ImGui::End();
    }

    void RenderObjectProperties() {
        if (selected_object < 0 || selected_object >= (int)models.size()) return;

        auto& model = models[selected_object];
        glm::mat4 transform = model->GetTransform();

        // 변환 행렬에서 위치, 회전, 스케일 추출 (간단화)
        glm::vec3 position = glm::vec3(transform[3]);

        ImGui::Text("객체 #%d", selected_object);
        ImGui::Separator();

        // 위치 조정
        float pos[3] = { position.x, position.y, position.z };
        if (ImGui::DragFloat3("위치", pos, 0.1f)) {
            // 새로운 변환 매트릭스 생성 (간단화)
            glm::mat4 new_transform = transform;
            new_transform[3] = glm::vec4(pos[0], pos[1], pos[2], 1.0f);
            model->SetTransform(new_transform);
            gizmo_position = glm::vec3(pos[0], pos[1], pos[2]);
        }

        // 회전 조정 (오일러 각도)
        static float rotation[3] = { 0.0f, 0.0f, 0.0f };
        if (ImGui::DragFloat3("회전", rotation, 1.0f)) {
            // 회전 적용 로직
        }

        // 스케일 조정
        static float scale[3] = { 1.0f, 1.0f, 1.0f };
        if (ImGui::DragFloat3("스케일", scale, 0.01f, 0.1f, 10.0f)) {
            // 스케일 적용 로직
        }

        ImGui::Separator();

        if (ImGui::Button("객체 삭제")) {
            DeleteSelectedObject();
        }
    }

    void RenderLightingControls() {
        ImGui::Text("조명 설정");
        ImGui::Separator();

        for (size_t i = 0; i < light_positions.size(); ++i) {
            ImGui::PushID((int)i);

            char label[32];
            snprintf(label, sizeof(label), "조명 #%zu", i + 1);
            if (ImGui::CollapsingHeader(label)) {

                float pos[3] = { light_positions[i].x, light_positions[i].y, light_positions[i].z };
                if (ImGui::DragFloat3("위치", pos, 0.5f)) {
                    light_positions[i] = glm::vec3(pos[0], pos[1], pos[2]);
                }

                float color[3] = { light_colors[i].r / 300.0f, light_colors[i].g / 300.0f, light_colors[i].b / 300.0f };
                if (ImGui::ColorEdit3("색상", color)) {
                    light_colors[i] = glm::vec3(color[0], color[1], color[2]) * 300.0f;
                }

                float intensity = glm::length(light_colors[i]) / 300.0f;
                if (ImGui::SliderFloat("강도", &intensity, 0.0f, 5.0f)) {
                    glm::vec3 normalized = glm::normalize(light_colors[i]);
                    light_colors[i] = normalized * intensity * 300.0f;
                }
            }

            ImGui::PopID();
        }

        if (ImGui::Button("조명 추가") && light_positions.size() < 4) {
            light_positions.push_back(glm::vec3(0.0f, 10.0f, 0.0f));
            light_colors.push_back(glm::vec3(300.0f, 300.0f, 300.0f));
        }
    }

    void RenderRenderingControls() {
        ImGui::Text("렌더링 설정");
        ImGui::Separator();

        ImGui::Checkbox("와이어프레임", &enable_wireframe);
        ImGui::Checkbox("그리드 표시", &enable_grid);
        ImGui::Checkbox("그림자", &enable_shadows);

        ImGui::SliderFloat("그리드 크기", &grid_size, 1.0f, 50.0f);

        float bg_color[3] = { background_color.r, background_color.g, background_color.b };
        if (ImGui::ColorEdit3("배경색", bg_color)) {
            background_color = glm::vec3(bg_color[0], bg_color[1], bg_color[2]);
        }

        ImGui::Separator();

        // 카메라 설정
        ImGui::Text("카메라 설정");

        float fov = camera->GetFOV();
        if (ImGui::SliderFloat("시야각", &fov, 10.0f, 120.0f)) {
            // FOV 설정 로직
        }

        // 카메라 모드 선택
        const char* camera_modes[] = { "자유 회전", "궤도", "1인칭", "상단" };
        int current_mode = (int)camera->GetMode();
        if (ImGui::Combo("카메라 모드", &current_mode, camera_modes, 4)) {
            camera->SetMode((CameraMode)current_mode);
        }
    }

    void HandleInput() {
        if (!is_focused) return;

        ImGuiIO& io = ImGui::GetIO();

        // 객체 선택 (마우스 클릭)
        if (ImGui::IsMouseClicked(ImGuiMouseButton_Left) && !io.KeyCtrl) {
            // 레이캐스팅을 통한 객체 선택
            // 간단화: 마우스 위치 기반 선택
            HandleObjectSelection();
        }

        // 삭제 키
        if (ImGui::IsKeyPressed(ImGuiKey_Delete) && selected_object >= 0) {
            DeleteSelectedObject();
        }

        // 복사 (Ctrl+D)
        if (io.KeyCtrl && ImGui::IsKeyPressed(ImGuiKey_D) && selected_object >= 0) {
            DuplicateSelectedObject();
        }
    }

    void HandleObjectSelection() {
        // 실제로는 레이캐스팅 구현 필요
        // 여기서는 간단한 예제
        ImVec2 mouse_pos = ImGui::GetMousePos();
        ImVec2 window_pos = ImGui::GetWindowPos();
        ImVec2 content_pos = ImGui::GetWindowContentRegionMin();

        // 뷰포트 내 상대 좌표 계산
        ImVec2 relative_pos = ImVec2(
            mouse_pos.x - window_pos.x - content_pos.x,
            mouse_pos.y - window_pos.y - content_pos.y
        );

        // 간단한 선택 로직 (실제로는 3D 레이캐스팅 필요)
        selected_object = (selected_object + 1) % (int)models.size();
        if (models.empty()) selected_object = -1;
    }

    void AddCube() {
        auto cube = Model::CreateCube(1.0f);
        glm::mat4 transform = glm::translate(glm::mat4(1.0f), glm::vec3(0, 0, 0));
        cube->SetTransform(transform);
        models.push_back(std::move(cube));
        selected_object = (int)models.size() - 1;
    }

    void AddSphere() {
        auto sphere = Model::CreateSphere(1.0f, 32);
        glm::mat4 transform = glm::translate(glm::mat4(1.0f), glm::vec3(2, 0, 0));
        sphere->SetTransform(transform);
        models.push_back(std::move(sphere));
        selected_object = (int)models.size() - 1;
    }

    void AddCylinder() {
        auto cylinder = Model::CreateCylinder(1.0f, 2.0f, 32);
        glm::mat4 transform = glm::translate(glm::mat4(1.0f), glm::vec3(-2, 0, 0));
        cylinder->SetTransform(transform);
        models.push_back(std::move(cylinder));
        selected_object = (int)models.size() - 1;
    }

    void DeleteSelectedObject() {
        if (selected_object >= 0 && selected_object < (int)models.size()) {
            models.erase(models.begin() + selected_object);
            selected_object = -1;
        }
    }

    void DuplicateSelectedObject() {
        if (selected_object >= 0 && selected_object < (int)models.size()) {
            // 간단한 복제 (실제로는 깊은 복사 필요)
            // 여기서는 새로운 기본 객체 추가로 대체
            AddCube();
        }
    }
};

} // namespace SemiconductorHMI
```

---

## ❓ 질의응답

<div style="margin: 2rem 0;">

<div style="background: #f8f9fa; padding: 2rem; border-radius: 8px; text-align: center; border: 2px dashed #6c757d;">
    <h3 style="color: #495057; margin: 0 0 1rem 0;">💬 질문해 주세요!</h3>
    <p style="margin: 0; color: #6c757d; font-style: italic;">
        ImGui의 고급 3D 렌더링, PBR 셰이더, 커스텀 위젯 개발에 대해<br>
        궁금한 점이 있으시면 언제든지 질문해 주세요.
    </p>
</div>

</div>

