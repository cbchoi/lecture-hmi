
            if (ImGui::BeginTabItem("네트워크")) {
                ImGui::Text("MQTT 브로커 설정");

                static char broker_host[256] = "localhost";
                static int broker_port = 1883;

                ImGui::InputText("호스트", broker_host, sizeof(broker_host));
                ImGui::InputInt("포트", &broker_port);

                if (ImGui::Button("연결")) {
                    mqtt_client_->Connect(broker_host, broker_port);
                }

                ImGui::SameLine();
                if (ImGui::Button("연결 해제")) {
                    mqtt_client_->Disconnect();
                }

                ImGui::EndTabItem();
            }

            if (ImGui::BeginTabItem("데이터")) {
                ImGui::Text("데이터 보관 설정");
                ImGui::EndTabItem();
            }

            ImGui::EndTabBar();
        }

        ImGui::End();
    }

    void RenderAccessibilityPanel() {
        ImGui::Begin("접근성 설정", &show_accessibility_panel_);

        static float text_scale = 1.0f;
        if (accessibility_manager_->AccessibleSliderFloat("텍스트 크기", &text_scale, 0.5f, 3.0f)) {
            accessibility_manager_->SetTextScale(text_scale);
        }

        static bool high_contrast = false;
        if (ImGui::Checkbox("고대비 모드", &high_contrast)) {
            accessibility_manager_->EnableHighContrast(high_contrast);
        }

        static bool screen_reader = false;
        if (ImGui::Checkbox("스크린 리더 지원", &screen_reader)) {
            accessibility_manager_->EnableScreenReaderSupport(screen_reader);
        }

        ImGui::End();
    }

    void RenderStatusBar() {
        ImGuiWindowFlags window_flags = ImGuiWindowFlags_NoScrollbar |
                                       ImGuiWindowFlags_NoSavedSettings |
                                       ImGuiWindowFlags_MenuBar;

        ImGuiViewport* viewport = ImGui::GetMainViewport();
        float height = ImGui::GetFrameHeight();

        ImGui::SetNextWindowPos(ImVec2(viewport->WorkPos.x, viewport->WorkPos.y + viewport->WorkSize.y - height));
        ImGui::SetNextWindowSize(ImVec2(viewport->WorkSize.x, height));
        ImGui::SetNextWindowViewport(viewport->ID);

        ImGui::Begin("StatusBar", nullptr, window_flags);

        // MQTT 연결 상태
        ImGui::Text("MQTT: %s", status_.mqtt_connected ? "연결됨" : "연결 끊김");
        ImGui::SameLine();

        // 활성 플러그인 수
        ImGui::Text("플러그인: %d개", status_.active_plugins);
        ImGui::SameLine();

        // 시스템 리소스
        ImGui::Text("CPU: %.1f%% | 메모리: %.1f MB", status_.cpu_usage, status_.memory_usage);

        ImGui::End();
    }

    void Shutdown() {
        if (mqtt_client_) {
            mqtt_client_->Disconnect();
        }
    }
};

} // namespace SemiconductorHMI

// 메인 애플리케이션 진입점
int main() {
    try {
        SemiconductorHMI::AdvancedIndustrialHMIPlatform platform;
        platform.Run();
    } catch (const std::exception& e) {
        // 오류 처리 및 로깅
        return -1;
    }

    return 0;
}
```

## 🎯 학습 성과 및 다음 단계

### ✅ 이번 주 완성 사항
- 동적 플러그인 시스템 구축
- 고급 데이터 시각화 엔진 개발
- 멀티스레딩 렌더링 시스템 구현
- 국제화 및 접근성 지원 완성
- MQTT 기반 외부 시스템 통합
- 완전한 산업용 HMI 플랫폼 개발

### 🔄 13주차 예고: "ImGUI C++ 통합 프로젝트"
- 전체 시스템 통합 및 최적화
- 배포 및 설치 시스템 구축
- 성능 튜닝 및 보안 강화

---

## 🔧 **고급 심화 실습 (30분) - 커스텀 렌더링 파이프라인 및 성능 최적화**

### 5. 커스텀 렌더링 백엔드 개발

#### 5.1 고성능 렌더링 파이프라인
```cpp
// CustomRenderPipeline.h
#pragma once
#include <imgui.h>
#include <memory>
#include <vector>
#include <unordered_map>
#include <GL/gl3w.h>

namespace SemiconductorHMI::Rendering {

// 고급 셰이더 관리자
class ShaderManager {
private:
    struct ShaderProgram {
        GLuint program_id;
        std::unordered_map<std::string, GLint> uniform_locations;
        std::string vertex_source;
        std::string fragment_source;
        std::string name;
    };

    std::unordered_map<std::string, std::unique_ptr<ShaderProgram>> shaders_;
    GLuint current_program_;

public:
    ShaderManager() : current_program_(0) {}

    bool LoadShader(const std::string& name, const std::string& vertex_source, const std::string& fragment_source) {
        auto shader = std::make_unique<ShaderProgram>();
        shader->name = name;
        shader->vertex_source = vertex_source;
        shader->fragment_source = fragment_source;

        // 정점 셰이더 컴파일
        GLuint vertex_shader = CompileShader(GL_VERTEX_SHADER, vertex_source);
        if (vertex_shader == 0) return false;

        // 프래그먼트 셰이더 컴파일
        GLuint fragment_shader = CompileShader(GL_FRAGMENT_SHADER, fragment_source);
        if (fragment_shader == 0) {
            glDeleteShader(vertex_shader);
            return false;
        }

        // 프로그램 링크
        shader->program_id = LinkProgram(vertex_shader, fragment_shader);
        if (shader->program_id == 0) {
            glDeleteShader(vertex_shader);
            glDeleteShader(fragment_shader);
            return false;
        }

        // 정리
        glDeleteShader(vertex_shader);
        glDeleteShader(fragment_shader);

        // Uniform 위치 캐싱
        CacheUniformLocations(*shader);

        shaders_[name] = std::move(shader);
        return true;
    }

    void UseShader(const std::string& name) {
        auto it = shaders_.find(name);
        if (it != shaders_.end()) {
            glUseProgram(it->second->program_id);
            current_program_ = it->second->program_id;
        }
    }

    void SetUniform(const std::string& shader_name, const std::string& uniform_name, float value) {
        auto shader_it = shaders_.find(shader_name);
        if (shader_it == shaders_.end()) return;

        auto uniform_it = shader_it->second->uniform_locations.find(uniform_name);
        if (uniform_it != shader_it->second->uniform_locations.end()) {
            glUniform1f(uniform_it->second, value);
        }
    }

    void SetUniform(const std::string& shader_name, const std::string& uniform_name, const ImVec2& value) {
        auto shader_it = shaders_.find(shader_name);
        if (shader_it == shaders_.end()) return;

        auto uniform_it = shader_it->second->uniform_locations.find(uniform_name);
        if (uniform_it != shader_it->second->uniform_locations.end()) {
            glUniform2f(uniform_it->second, value.x, value.y);
        }
    }

    void SetUniform(const std::string& shader_name, const std::string& uniform_name, const ImVec4& value) {
        auto shader_it = shaders_.find(shader_name);
        if (shader_it == shaders_.end()) return;

        auto uniform_it = shader_it->second->uniform_locations.find(uniform_name);
        if (uniform_it != shader_it->second->uniform_locations.end()) {
            glUniform4f(uniform_it->second, value.x, value.y, value.z, value.w);
        }
    }

private:
    GLuint CompileShader(GLenum type, const std::string& source) {
        GLuint shader = glCreateShader(type);
        const char* source_ptr = source.c_str();
        glShaderSource(shader, 1, &source_ptr, nullptr);
        glCompileShader(shader);

        GLint success;
        glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
        if (!success) {
            char info_log[512];
            glGetShaderInfoLog(shader, 512, nullptr, info_log);
            // 로그 출력 (실제 구현에서는 로깅 시스템 사용)
            glDeleteShader(shader);
            return 0;
        }

        return shader;
    }

    GLuint LinkProgram(GLuint vertex_shader, GLuint fragment_shader) {
        GLuint program = glCreateProgram();
        glAttachShader(program, vertex_shader);
        glAttachShader(program, fragment_shader);
        glLinkProgram(program);

        GLint success;
        glGetProgramiv(program, GL_LINK_STATUS, &success);
        if (!success) {
            char info_log[512];
            glGetProgramInfoLog(program, 512, nullptr, info_log);
            // 로그 출력
            glDeleteProgram(program);
            return 0;
        }

        return program;
    }

    void CacheUniformLocations(ShaderProgram& shader) {
        GLint uniform_count;
        glGetProgramiv(shader.program_id, GL_ACTIVE_UNIFORMS, &uniform_count);

        for (GLint i = 0; i < uniform_count; i++) {
            char name[256];
            GLsizei length;
            GLint size;
            GLenum type;

            glGetActiveUniform(shader.program_id, i, sizeof(name), &length, &size, &type, name);
            GLint location = glGetUniformLocation(shader.program_id, name);

            if (location >= 0) {
                shader.uniform_locations[std::string(name)] = location;
            }
        }
    }
};

// 고성능 텍스처 관리자
class TextureManager {
private:
    struct TextureInfo {
        GLuint texture_id;
        int width, height, channels;
        GLenum format;
        std::string name;
        bool is_loaded;
    };

    std::unordered_map<std::string, std::unique_ptr<TextureInfo>> textures_;
    std::vector<GLuint> texture_pool_; // 재사용 가능한 텍스처 풀

public:
    GLuint LoadTexture(const std::string& name, int width, int height, GLenum format, const void* data = nullptr) {
        auto texture_info = std::make_unique<TextureInfo>();
        texture_info->name = name;
        texture_info->width = width;
        texture_info->height = height;
        texture_info->format = format;
        texture_info->is_loaded = false;

        // 텍스처 생성
        glGenTextures(1, &texture_info->texture_id);
        glBindTexture(GL_TEXTURE_2D, texture_info->texture_id);

        // 텍스처 파라미터 설정
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

        // 텍스처 데이터 업로드
        if (data) {
            glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, data);
            texture_info->is_loaded = true;
        } else {
            glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, nullptr);
        }

        GLuint texture_id = texture_info->texture_id;
        textures_[name] = std::move(texture_info);

        return texture_id;
    }

    GLuint GetTexture(const std::string& name) {
        auto it = textures_.find(name);
        return (it != textures_.end()) ? it->second->texture_id : 0;
    }

    void UpdateTexture(const std::string& name, const void* data) {
        auto it = textures_.find(name);
        if (it != textures_.end() && data) {
            glBindTexture(GL_TEXTURE_2D, it->second->texture_id);
            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0,
                           it->second->width, it->second->height,
                           it->second->format, GL_UNSIGNED_BYTE, data);
            it->second->is_loaded = true;
        }
    }

    void DeleteTexture(const std::string& name) {
        auto it = textures_.find(name);
        if (it != textures_.end()) {
            glDeleteTextures(1, &it->second->texture_id);
            textures_.erase(it);
        }
    }

    // 텍스처 풀에서 재사용 가능한 텍스처 가져오기
    GLuint GetPooledTexture(int width, int height, GLenum format) {
        // 간단한 구현 - 실제로는 크기와 포맷이 일치하는 텍스처 찾기
        if (!texture_pool_.empty()) {
            GLuint texture = texture_pool_.back();
            texture_pool_.pop_back();
            return texture;
        }

        // 새 텍스처 생성
        GLuint texture;
        glGenTextures(1, &texture);
        glBindTexture(GL_TEXTURE_2D, texture);
        glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, nullptr);
        return texture;
    }

    void ReturnToPool(GLuint texture) {
        texture_pool_.push_back(texture);
    }
};

// 고급 렌더링 파이프라인
class CustomRenderPipeline {
private:
    ShaderManager shader_manager_;
    TextureManager texture_manager_;

    // 렌더 타겟들
    GLuint main_framebuffer_;
    GLuint color_texture_;
    GLuint depth_texture_;
    GLuint intermediate_framebuffer_;
    GLuint intermediate_texture_;

    // 포스트 프로세싱 체인
    std::vector<std::string> post_process_passes_;

    int screen_width_, screen_height_;

public:
    CustomRenderPipeline() : main_framebuffer_(0), color_texture_(0), depth_texture_(0),
                            intermediate_framebuffer_(0), intermediate_texture_(0),
                            screen_width_(0), screen_height_(0) {}

    bool Initialize(int width, int height) {
        screen_width_ = width;
        screen_height_ = height;

        // 기본 셰이더들 로드
        LoadDefaultShaders();

        // 프레임버퍼 설정
        SetupFramebuffers();

        return true;
    }

    void Resize(int width, int height) {
        if (width == screen_width_ && height == screen_height_) return;

        screen_width_ = width;
        screen_height_ = height;

        // 텍스처 크기 변경
        ResizeTextures();
    }

    void BeginFrame() {
        // 메인 프레임버퍼에 렌더링 시작
        glBindFramebuffer(GL_FRAMEBUFFER, main_framebuffer_);
        glViewport(0, 0, screen_width_, screen_height_);

        glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        glEnable(GL_DEPTH_TEST);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    }

    void EndFrame() {
        // 포스트 프로세싱 수행
        ApplyPostProcessing();

        // 최종 결과를 백버퍼에 렌더링
        PresentToBackbuffer();
    }

    void AddPostProcessPass(const std::string& shader_name) {
        post_process_passes_.push_back(shader_name);
    }

    void RenderFullscreenQuad() {
        // 전체 화면 사각형 렌더링 (포스트 프로세싱용)
        static GLuint quad_vao = 0;
        if (quad_vao == 0) {
            float quad_vertices[] = {
                -1.0f,  1.0f, 0.0f, 1.0f,
                -1.0f, -1.0f, 0.0f, 0.0f,
                 1.0f, -1.0f, 1.0f, 0.0f,
                 1.0f,  1.0f, 1.0f, 1.0f
            };

            GLuint quad_vbo;
            glGenVertexArrays(1, &quad_vao);
            glGenBuffers(1, &quad_vbo);

            glBindVertexArray(quad_vao);
            glBindBuffer(GL_ARRAY_BUFFER, quad_vbo);
            glBufferData(GL_ARRAY_BUFFER, sizeof(quad_vertices), quad_vertices, GL_STATIC_DRAW);

            glEnableVertexAttribArray(0);
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)0);
            glEnableVertexAttribArray(1);
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)(2 * sizeof(float)));
        }

        glBindVertexArray(quad_vao);
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4);
    }

    ShaderManager& GetShaderManager() { return shader_manager_; }
    TextureManager& GetTextureManager() { return texture_manager_; }

private:
    void LoadDefaultShaders() {
        // 기본 정점 셰이더
        std::string default_vertex = R"(
            #version 330 core
            layout (location = 0) in vec2 aPos;
            layout (location = 1) in vec2 aTexCoord;

            out vec2 TexCoord;

            uniform mat4 uProjection;
            uniform mat4 uModelView;

            void main() {
                TexCoord = aTexCoord;
                gl_Position = uProjection * uModelView * vec4(aPos, 0.0, 1.0);
            }
        )";

        // 기본 프래그먼트 셰이더
        std::string default_fragment = R"(
            #version 330 core
            out vec4 FragColor;

            in vec2 TexCoord;
            uniform sampler2D uTexture;
            uniform vec4 uColor;

            void main() {
                FragColor = texture(uTexture, TexCoord) * uColor;
            }
        )";

        // 블룸 효과 셰이더
        std::string bloom_fragment = R"(
            #version 330 core
            out vec4 FragColor;

            in vec2 TexCoord;
            uniform sampler2D uTexture;
            uniform bool uHorizontal;
            uniform float uBloomThreshold;

            void main() {
                vec3 color = texture(uTexture, TexCoord).rgb;

                if (uHorizontal) {
                    // 수평 블러
                    vec2 tex_offset = 1.0 / textureSize(uTexture, 0);
                    vec3 result = color * 0.227027;

                    for(int i = 1; i < 5; ++i) {
                        result += texture(uTexture, TexCoord + vec2(tex_offset.x * i, 0.0)).rgb * 0.1945946;
                        result += texture(uTexture, TexCoord - vec2(tex_offset.x * i, 0.0)).rgb * 0.1945946;
                    }

                    FragColor = vec4(result, 1.0);
                } else {
                    // 수직 블러
                    vec2 tex_offset = 1.0 / textureSize(uTexture, 0);
                    vec3 result = color * 0.227027;

                    for(int i = 1; i < 5; ++i) {
                        result += texture(uTexture, TexCoord + vec2(0.0, tex_offset.y * i)).rgb * 0.1945946;
                        result += texture(uTexture, TexCoord - vec2(0.0, tex_offset.y * i)).rgb * 0.1945946;
                    }

                    FragColor = vec4(result, 1.0);
                }
            }
        )";

        // 톤 매핑 셰이더
        std::string tonemap_fragment = R"(
            #version 330 core
            out vec4 FragColor;

            in vec2 TexCoord;
            uniform sampler2D uHDRTexture;
            uniform sampler2D uBloomTexture;
            uniform float uExposure;
            uniform float uGamma;

            void main() {
                vec3 hdr_color = texture(uHDRTexture, TexCoord).rgb;
                vec3 bloom_color = texture(uBloomTexture, TexCoord).rgb;

                // 블룸 추가
                hdr_color += bloom_color;

                // 톤 매핑 (Reinhard)
                vec3 mapped = hdr_color / (hdr_color + vec3(1.0));

                // 감마 보정
                mapped = pow(mapped, vec3(1.0 / uGamma));

                FragColor = vec4(mapped, 1.0);
            }
        )";

        shader_manager_.LoadShader("default", default_vertex, default_fragment);
        shader_manager_.LoadShader("bloom", default_vertex, bloom_fragment);
        shader_manager_.LoadShader("tonemap", default_vertex, tonemap_fragment);
    }

    void SetupFramebuffers() {
        // 메인 프레임버퍼 생성
        glGenFramebuffers(1, &main_framebuffer_);
        glBindFramebuffer(GL_FRAMEBUFFER, main_framebuffer_);

        // 컬러 텍스처 생성
        color_texture_ = texture_manager_.LoadTexture("main_color", screen_width_, screen_height_, GL_RGBA16F);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color_texture_, 0);

        // 깊이 텍스처 생성
        depth_texture_ = texture_manager_.LoadTexture("main_depth", screen_width_, screen_height_, GL_DEPTH_COMPONENT24);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depth_texture_, 0);

        // 중간 프레임버퍼 생성 (포스트 프로세싱용)
        glGenFramebuffers(1, &intermediate_framebuffer_);
        glBindFramebuffer(GL_FRAMEBUFFER, intermediate_framebuffer_);

        intermediate_texture_ = texture_manager_.LoadTexture("intermediate", screen_width_, screen_height_, GL_RGBA16F);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, intermediate_texture_, 0);

        glBindFramebuffer(GL_FRAMEBUFFER, 0);
    }

    void ResizeTextures() {
        // 기존 텍스처들 업데이트
        texture_manager_.DeleteTexture("main_color");
        texture_manager_.DeleteTexture("main_depth");
        texture_manager_.DeleteTexture("intermediate");

        color_texture_ = texture_manager_.LoadTexture("main_color", screen_width_, screen_height_, GL_RGBA16F);
        depth_texture_ = texture_manager_.LoadTexture("main_depth", screen_width_, screen_height_, GL_DEPTH_COMPONENT24);
        intermediate_texture_ = texture_manager_.LoadTexture("intermediate", screen_width_, screen_height_, GL_RGBA16F);

        // 프레임버퍼 재설정
        glBindFramebuffer(GL_FRAMEBUFFER, main_framebuffer_);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color_texture_, 0);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depth_texture_, 0);

        glBindFramebuffer(GL_FRAMEBUFFER, intermediate_framebuffer_);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, intermediate_texture_, 0);

        glBindFramebuffer(GL_FRAMEBUFFER, 0);
    }

    void ApplyPostProcessing() {
        // 포스트 프로세싱 효과들을 순차적으로 적용
        GLuint source_texture = color_texture_;
        GLuint target_framebuffer = intermediate_framebuffer_;

        for (const std::string& pass : post_process_passes_) {
            glBindFramebuffer(GL_FRAMEBUFFER, target_framebuffer);
            glViewport(0, 0, screen_width_, screen_height_);

            shader_manager_.UseShader(pass);
            glActiveTexture(GL_TEXTURE0);
            glBindTexture(GL_TEXTURE_2D, source_texture);

            RenderFullscreenQuad();

            // 다음 패스를 위해 소스와 타겟 교체
            source_texture = intermediate_texture_;
            target_framebuffer = (target_framebuffer == intermediate_framebuffer_) ? main_framebuffer_ : intermediate_framebuffer_;
        }
    }

    void PresentToBackbuffer() {
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        glViewport(0, 0, screen_width_, screen_height_);

        shader_manager_.UseShader("default");
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, color_texture_);

        RenderFullscreenQuad();
    }
};

} // namespace SemiconductorHMI::Rendering
```

#### 5.2 실시간 성능 프로파일러
```cpp
// PerformanceProfiler.h
#pragma once
#include <chrono>
#include <string>
#include <unordered_map>
#include <vector>
#include <mutex>
#include <memory>

namespace SemiconductorHMI::Profiling {

class PerformanceProfiler {
private:
    struct ProfileData {
        std::string name;
        std::chrono::high_resolution_clock::time_point start_time;
        std::chrono::duration<double, std::milli> accumulated_time{0};
        size_t call_count = 0;
        double min_time = std::numeric_limits<double>::max();
        double max_time = 0.0;
        bool is_active = false;
    };

    std::unordered_map<std::string, std::unique_ptr<ProfileData>> profiles_;
    std::vector<std::pair<std::string, double>> frame_times_; // 프레임별 시간 저장
    std::mutex profiles_mutex_;

    // 히스토리 관리
    static constexpr size_t MAX_HISTORY_SIZE = 1000;
    std::unordered_map<std::string, std::vector<double>> time_history_;

public:
    static PerformanceProfiler& GetInstance() {
        static PerformanceProfiler instance;
        return instance;
    }

    void BeginProfile(const std::string& name) {
        std::lock_guard<std::mutex> lock(profiles_mutex_);

        auto it = profiles_.find(name);
        if (it == profiles_.end()) {
            profiles_[name] = std::make_unique<ProfileData>();
            profiles_[name]->name = name;
        }

        ProfileData& data = *profiles_[name];
        if (!data.is_active) {
            data.start_time = std::chrono::high_resolution_clock::now();
            data.is_active = true;
        }
    }

    void EndProfile(const std::string& name) {
        auto end_time = std::chrono::high_resolution_clock::now();

        std::lock_guard<std::mutex> lock(profiles_mutex_);

        auto it = profiles_.find(name);
        if (it != profiles_.end() && it->second->is_active) {
            ProfileData& data = *it->second;

            auto duration = std::chrono::duration<double, std::milli>(end_time - data.start_time);
            double duration_ms = duration.count();

            data.accumulated_time += duration;
            data.call_count++;
            data.min_time = std::min(data.min_time, duration_ms);
            data.max_time = std::max(data.max_time, duration_ms);
            data.is_active = false;

            // 히스토리에 추가
            auto& history = time_history_[name];
            history.push_back(duration_ms);
            if (history.size() > MAX_HISTORY_SIZE) {
                history.erase(history.begin());
            }
        }
    }

    void ShowProfilerWindow() {
        if (ImGui::Begin("Performance Profiler")) {

            // 요약 통계
            ImGui::Text("Active Profiles: %zu", profiles_.size());
            ImGui::Separator();

            // 테이블로 프로필 데이터 표시
            if (ImGui::BeginTable("ProfileTable", 6, ImGuiTableFlags_Borders | ImGuiTableFlags_Resizable)) {
                ImGui::TableSetupColumn("Name");
                ImGui::TableSetupColumn("Calls");
                ImGui::TableSetupColumn("Total (ms)");
                ImGui::TableSetupColumn("Avg (ms)");
                ImGui::TableSetupColumn("Min (ms)");
                ImGui::TableSetupColumn("Max (ms)");
                ImGui::TableHeadersRow();

                std::lock_guard<std::mutex> lock(profiles_mutex_);
                for (const auto& [name, data] : profiles_) {
                    if (data->call_count == 0) continue;

                    ImGui::TableNextRow();
                    ImGui::TableNextColumn();
                    ImGui::Text("%s", name.c_str());

                    ImGui::TableNextColumn();
                    ImGui::Text("%zu", data->call_count);

                    ImGui::TableNextColumn();
                    ImGui::Text("%.3f", data->accumulated_time.count());

                    ImGui::TableNextColumn();
                    double avg_time = data->accumulated_time.count() / data->call_count;
                    ImGui::Text("%.3f", avg_time);

                    ImGui::TableNextColumn();
                    ImGui::Text("%.3f", data->min_time);

                    ImGui::TableNextColumn();
                    ImGui::Text("%.3f", data->max_time);
                }

                ImGui::EndTable();
            }

            ImGui::Separator();

            // 시간 그래프
            for (const auto& [name, history] : time_history_) {
                if (history.empty()) continue;

                std::string plot_label = name + " Time History";
                ImGui::PlotLines(plot_label.c_str(), history.data(), static_cast<int>(history.size()),
                                0, nullptr, 0.0f, FLT_MAX, ImVec2(0, 80));
            }

            // 리셋 버튼
            if (ImGui::Button("Reset All Profiles")) {
                ResetAllProfiles();
            }
        }
        ImGui::End();
    }

    void ResetAllProfiles() {
        std::lock_guard<std::mutex> lock(profiles_mutex_);
        for (auto& [name, data] : profiles_) {
            data->accumulated_time = std::chrono::duration<double, std::milli>(0);
            data->call_count = 0;
            data->min_time = std::numeric_limits<double>::max();
            data->max_time = 0.0;
            data->is_active = false;
        }
        time_history_.clear();
    }

    // 특정 프로필의 평균 시간 반환
    double GetAverageTime(const std::string& name) const {
        std::lock_guard<std::mutex> lock(profiles_mutex_);
        auto it = profiles_.find(name);
        if (it != profiles_.end() && it->second->call_count > 0) {
            return it->second->accumulated_time.count() / it->second->call_count;
        }
        return 0.0;
    }
};

// RAII 스타일 프로파일러 도우미 클래스
class ScopedProfiler {
private:
    std::string profile_name_;

public:
    explicit ScopedProfiler(const std::string& name) : profile_name_(name) {
        PerformanceProfiler::GetInstance().BeginProfile(profile_name_);
    }

    ~ScopedProfiler() {
        PerformanceProfiler::GetInstance().EndProfile(profile_name_);
    }
};

// 매크로로 편리하게 사용
#define PROFILE_SCOPE(name) ScopedProfiler _prof(name)
#define PROFILE_FUNCTION() ScopedProfiler _prof(__FUNCTION__)

} // namespace SemiconductorHMI::Profiling
```

### 6. 고급 메모리 관리 및 최적화

#### 6.1 커스텀 메모리 풀 시스템
```cpp
// MemoryManager.h
#pragma once
#include <memory>
#include <vector>
#include <mutex>
#include <unordered_map>
