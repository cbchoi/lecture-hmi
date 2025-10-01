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
