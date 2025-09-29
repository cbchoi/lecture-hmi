# Week 11: ImGUI C++ 심화 - 고급 렌더링 및 커스텀 시각화

## 🎯 **이론 강의 (45분) - 고급 렌더링 아키텍처 및 3D 통합**

### 1. ImGUI 고급 렌더링 아키텍처

#### 1.1 DrawList API 심화 이해
```cpp
/*
ImGUI 렌더링 파이프라인:
Application Code → ImGUI Draw Commands → Vertex/Index Buffers → GPU

DrawList 구조:
- Commands: 렌더링 명령 목록
- VtxBuffer: 정점 데이터
- IdxBuffer: 인덱스 데이터
- ClipRectStack: 클리핑 영역 스택
*/

#include <imgui.h>
#include <imgui_internal.h>
#include <GL/gl3w.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

namespace SemiconductorHMI {

class AdvancedRenderer {
private:
    struct RenderContext {
        glm::mat4 view_matrix;
        glm::mat4 projection_matrix;
        ImVec2 viewport_size;
        float scale_factor;
    };

    RenderContext context;
    GLuint shader_program;
    GLuint vertex_array;
    GLuint vertex_buffer;
    GLuint element_buffer;

public:
    AdvancedRenderer() : shader_program(0), vertex_array(0), vertex_buffer(0), element_buffer(0) {}

    bool Initialize() {
        // 고급 셰이더 컴파일
        const char* vertex_shader_source = R"(
        #version 450 core
        layout (location = 0) in vec2 aPos;
        layout (location = 1) in vec2 aTexCoord;
        layout (location = 2) in vec4 aColor;

        uniform mat4 uProjection;
        uniform mat4 uView;
        uniform float uTime;

        out vec2 TexCoord;
        out vec4 Color;
        out float Time;

        void main() {
            gl_Position = uProjection * uView * vec4(aPos, 0.0, 1.0);
            TexCoord = aTexCoord;
            Color = aColor;
            Time = uTime;
        }
        )";

        const char* fragment_shader_source = R"(
        #version 450 core
        in vec2 TexCoord;
        in vec4 Color;
        in float Time;

        uniform sampler2D uTexture;
        uniform bool uUseTexture;
        uniform vec4 uTint;

        out vec4 FragColor;

        void main() {
            vec4 baseColor = Color;

            if (uUseTexture) {
                baseColor *= texture(uTexture, TexCoord);
            }

            // 고급 효과: 펄스 애니메이션
            float pulse = 0.5 + 0.5 * sin(Time * 3.14159 * 2.0);
            baseColor.rgb *= (0.8 + 0.2 * pulse);

            FragColor = baseColor * uTint;
        }
        )";

        shader_program = CreateShaderProgram(vertex_shader_source, fragment_shader_source);
        if (shader_program == 0) return false;

        // VAO/VBO 설정
        glGenVertexArrays(1, &vertex_array);
        glGenBuffers(1, &vertex_buffer);
        glGenBuffers(1, &element_buffer);

        return true;
    }

    void BeginFrame(const ImVec2& display_size) {
        context.viewport_size = display_size;
        context.projection_matrix = glm::ortho(0.0f, display_size.x, display_size.y, 0.0f, -1.0f, 1.0f);
        context.view_matrix = glm::mat4(1.0f);
        context.scale_factor = ImGui::GetIO().DisplayFramebufferScale.x;
    }

    // 고급 커스텀 드로잉 함수들
    void DrawGradientRect(const ImVec2& min, const ImVec2& max,
                         const ImVec4& color_tl, const ImVec4& color_tr,
                         const ImVec4& color_bl, const ImVec4& color_br) {
        ImDrawList* draw_list = ImGui::GetWindowDrawList();

        // 4개 정점으로 그라데이션 사각형 생성
        draw_list->PrimReserve(6, 4);

        // 정점 추가
        ImU32 col_tl = ImGui::ColorConvertFloat4ToU32(color_tl);
        ImU32 col_tr = ImGui::ColorConvertFloat4ToU32(color_tr);
        ImU32 col_bl = ImGui::ColorConvertFloat4ToU32(color_bl);
        ImU32 col_br = ImGui::ColorConvertFloat4ToU32(color_br);

        draw_list->PrimWriteVtx(min, ImVec2(0, 0), col_tl);
        draw_list->PrimWriteVtx(ImVec2(max.x, min.y), ImVec2(1, 0), col_tr);
        draw_list->PrimWriteVtx(ImVec2(min.x, max.y), ImVec2(0, 1), col_bl);
        draw_list->PrimWriteVtx(max, ImVec2(1, 1), col_br);

        // 인덱스 추가 (두 개의 삼각형)
        auto idx = (ImDrawIdx)(draw_list->_VtxCurrentIdx - 4);
        draw_list->PrimWriteIdx(idx); draw_list->PrimWriteIdx(idx + 1); draw_list->PrimWriteIdx(idx + 2);
        draw_list->PrimWriteIdx(idx + 1); draw_list->PrimWriteIdx(idx + 3); draw_list->PrimWriteIdx(idx + 2);
    }

    void DrawBezierCurve(const ImVec2& p0, const ImVec2& p1, const ImVec2& p2, const ImVec2& p3,
                        ImU32 color, float thickness, int segments = 50) {
        ImDrawList* draw_list = ImGui::GetWindowDrawList();

        // 베지어 곡선 계산
        std::vector<ImVec2> points;
        points.reserve(segments + 1);

        for (int i = 0; i <= segments; ++i) {
            float t = static_cast<float>(i) / segments;
            float u = 1.0f - t;

            // 3차 베지어 곡선 공식
            ImVec2 point = ImVec2(
                u*u*u * p0.x + 3*u*u*t * p1.x + 3*u*t*t * p2.x + t*t*t * p3.x,
                u*u*u * p0.y + 3*u*u*t * p1.y + 3*u*t*t * p2.y + t*t*t * p3.y
            );
            points.push_back(point);
        }

        // 폴리라인으로 그리기
        draw_list->AddPolyline(points.data(), points.size(), color, false, thickness);
    }

    void DrawCircularProgressBar(const ImVec2& center, float radius, float progress,
                               ImU32 bg_color, ImU32 fg_color, float thickness = 4.0f) {
        ImDrawList* draw_list = ImGui::GetWindowDrawList();

        const int segments = 64;
        const float angle_step = 2.0f * IM_PI / segments;
        const float progress_angle = progress * 2.0f * IM_PI - IM_PI * 0.5f; // -90도에서 시작

        // 배경 원
        draw_list->AddCircle(center, radius, bg_color, segments, thickness);

        // 진행률 호 그리기
        if (progress > 0.0f) {
            int progress_segments = static_cast<int>(progress * segments);

            for (int i = 0; i < progress_segments; ++i) {
                float angle1 = -IM_PI * 0.5f + angle_step * i;
                float angle2 = -IM_PI * 0.5f + angle_step * (i + 1);

                ImVec2 p1 = ImVec2(center.x + cos(angle1) * radius, center.y + sin(angle1) * radius);
                ImVec2 p2 = ImVec2(center.x + cos(angle2) * radius, center.y + sin(angle2) * radius);

                draw_list->AddLine(p1, p2, fg_color, thickness);
            }
        }
    }

private:
    GLuint CreateShaderProgram(const char* vertex_source, const char* fragment_source) {
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
            glGetProgramInfoLog(program, 512, nullptr, info_log);
            printf("Shader program linking failed: %s\n", info_log);
            return 0;
        }

        glDeleteShader(vertex_shader);
        glDeleteShader(fragment_shader);

        return program;
    }

    GLuint CompileShader(GLenum type, const char* source) {
        GLuint shader = glCreateShader(type);
        glShaderSource(shader, 1, &source, nullptr);
        glCompileShader(shader);

        GLint success;
        glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
        if (!success) {
            char info_log[512];
            glGetShaderInfoLog(shader, 512, nullptr, info_log);
            printf("Shader compilation failed: %s\n", info_log);
            return 0;
        }

        return shader;
    }
};

} // namespace SemiconductorHMI
```

---

## 🔧 **기초 실습 (45분) - 커스텀 드로잉 및 위젯 개발**

#### 1.2 3D 렌더링과 ImGUI 통합
```cpp
#include <assimp/Importer.hpp>
#include <assimp/scene.h>
#include <assimp/postprocess.h>

namespace SemiconductorHMI {

struct Vertex3D {
    glm::vec3 position;
    glm::vec3 normal;
    glm::vec2 texCoords;
    glm::vec3 tangent;
};

struct Mesh3D {
    std::vector<Vertex3D> vertices;
    std::vector<unsigned int> indices;
    std::vector<GLuint> textures;

    GLuint VAO, VBO, EBO;

    void SetupMesh() {
        glGenVertexArrays(1, &VAO);
        glGenBuffers(1, &VBO);
        glGenBuffers(1, &EBO);

        glBindVertexArray(VAO);

        glBindBuffer(GL_ARRAY_BUFFER, VBO);
        glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(Vertex3D),
                    &vertices[0], GL_STATIC_DRAW);

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO);
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int),
                    &indices[0], GL_STATIC_DRAW);

        // 정점 속성 설정
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex3D), (void*)0);

        glEnableVertexAttribArray(1);
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex3D),
                             (void*)offsetof(Vertex3D, normal));

        glEnableVertexAttribArray(2);
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex3D),
                             (void*)offsetof(Vertex3D, texCoords));

        glBindVertexArray(0);
    }

    void Draw(GLuint shader_program) {
        glUseProgram(shader_program);
        glBindVertexArray(VAO);
        glDrawElements(GL_TRIANGLES, indices.size(), GL_UNSIGNED_INT, 0);
        glBindVertexArray(0);
    }
};

class Equipment3DModel {
private:
    std::vector<Mesh3D> meshes;
    std::string directory;
    Assimp::Importer importer;

public:
    bool LoadModel(const std::string& path) {
        const aiScene* scene = importer.ReadFile(path,
            aiProcess_Triangulate | aiProcess_FlipUVs | aiProcess_CalcTangentSpace);

        if (!scene || scene->mFlags & AI_SCENE_FLAGS_INCOMPLETE || !scene->mRootNode) {
            printf("ERROR::ASSIMP:: %s\n", importer.GetErrorString());
            return false;
        }

        directory = path.substr(0, path.find_last_of('/'));
        ProcessNode(scene->mRootNode, scene);
        return true;
    }

    void Draw(GLuint shader_program) {
        for (auto& mesh : meshes) {
            mesh.Draw(shader_program);
        }
    }

private:
    void ProcessNode(aiNode* node, const aiScene* scene) {
        // 현재 노드의 모든 메쉬 처리
        for (unsigned int i = 0; i < node->mNumMeshes; i++) {
            aiMesh* mesh = scene->mMeshes[node->mMeshes[i]];
            meshes.push_back(ProcessMesh(mesh, scene));
        }

        // 자식 노드들 재귀 처리
        for (unsigned int i = 0; i < node->mNumChildren; i++) {
            ProcessNode(node->mChildren[i], scene);
        }
    }

    Mesh3D ProcessMesh(aiMesh* mesh, const aiScene* scene) {
        std::vector<Vertex3D> vertices;
        std::vector<unsigned int> indices;
        std::vector<GLuint> textures;

        // 정점 데이터 처리
        for (unsigned int i = 0; i < mesh->mNumVertices; i++) {
            Vertex3D vertex;

            vertex.position = glm::vec3(mesh->mVertices[i].x, mesh->mVertices[i].y, mesh->mVertices[i].z);
            vertex.normal = glm::vec3(mesh->mNormals[i].x, mesh->mNormals[i].y, mesh->mNormals[i].z);

            if (mesh->mTextureCoords[0]) {
                vertex.texCoords = glm::vec2(mesh->mTextureCoords[0][i].x, mesh->mTextureCoords[0][i].y);
            } else {
                vertex.texCoords = glm::vec2(0.0f, 0.0f);
            }

            vertices.push_back(vertex);
        }

        // 인덱스 처리
        for (unsigned int i = 0; i < mesh->mNumFaces; i++) {
            aiFace face = mesh->mFaces[i];
            for (unsigned int j = 0; j < face.mNumIndices; j++) {
                indices.push_back(face.mIndices[j]);
            }
        }

        Mesh3D result;
        result.vertices = vertices;
        result.indices = indices;
        result.textures = textures;
        result.SetupMesh();

        return result;
    }
};

class ImGui3DViewer {
private:
    Equipment3DModel model;
    GLuint framebuffer, color_texture, depth_texture;
    GLuint shader_program;
    glm::mat4 view_matrix, projection_matrix;
    glm::vec3 camera_position;
    glm::vec3 camera_target;
    float camera_distance;
    ImVec2 viewport_size;

public:
    ImGui3DViewer() : framebuffer(0), color_texture(0), depth_texture(0),
                     shader_program(0), camera_distance(5.0f),
                     camera_position(0, 0, 5), camera_target(0, 0, 0) {}

    bool Initialize(const std::string& model_path) {
        // 3D 모델 로드
        if (!model.LoadModel(model_path)) {
            return false;
        }

        // 셰이더 프로그램 생성
        const char* vertex_shader = R"(
        #version 450 core
        layout (location = 0) in vec3 aPos;
        layout (location = 1) in vec3 aNormal;
        layout (location = 2) in vec2 aTexCoord;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        out vec3 FragPos;
        out vec3 Normal;
        out vec2 TexCoord;

        void main() {
            FragPos = vec3(model * vec4(aPos, 1.0));
            Normal = mat3(transpose(inverse(model))) * aNormal;
            TexCoord = aTexCoord;

            gl_Position = projection * view * vec4(FragPos, 1.0);
        }
        )";

        const char* fragment_shader = R"(
        #version 450 core
        in vec3 FragPos;
        in vec3 Normal;
        in vec2 TexCoord;

        uniform vec3 lightPos;
        uniform vec3 lightColor;
        uniform vec3 objectColor;
        uniform vec3 viewPos;

        out vec4 FragColor;

        void main() {
            // 앰비언트 라이팅
            float ambientStrength = 0.3;
            vec3 ambient = ambientStrength * lightColor;

            // 디퓨즈 라이팅
            vec3 norm = normalize(Normal);
            vec3 lightDir = normalize(lightPos - FragPos);
            float diff = max(dot(norm, lightDir), 0.0);
            vec3 diffuse = diff * lightColor;

            // 스펙큘러 라이팅
            float specularStrength = 0.5;
            vec3 viewDir = normalize(viewPos - FragPos);
            vec3 reflectDir = reflect(-lightDir, norm);
            float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
            vec3 specular = specularStrength * spec * lightColor;

            vec3 result = (ambient + diffuse + specular) * objectColor;
            FragColor = vec4(result, 1.0);
        }
        )";

        shader_program = CreateShaderProgram(vertex_shader, fragment_shader);
        return shader_program != 0;
    }

    void SetViewportSize(const ImVec2& size) {
        if (viewport_size.x != size.x || viewport_size.y != size.y) {
            viewport_size = size;
            SetupFramebuffer();
        }
    }

    void Render() {
        if (framebuffer == 0) return;

        // 프레임버퍼에 렌더링
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
        glViewport(0, 0, static_cast<int>(viewport_size.x), static_cast<int>(viewport_size.y));

        glEnable(GL_DEPTH_TEST);
        glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // 뷰 및 프로젝션 매트릭스 설정
        view_matrix = glm::lookAt(camera_position, camera_target, glm::vec3(0, 1, 0));
        projection_matrix = glm::perspective(glm::radians(45.0f),
                                           viewport_size.x / viewport_size.y, 0.1f, 100.0f);

        // 셰이더 유니폼 설정
        glUseProgram(shader_program);

        glm::mat4 model_matrix = glm::mat4(1.0f);

        GLint model_loc = glGetUniformLocation(shader_program, "model");
        GLint view_loc = glGetUniformLocation(shader_program, "view");
        GLint projection_loc = glGetUniformLocation(shader_program, "projection");

        glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm::value_ptr(model_matrix));
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm::value_ptr(view_matrix));
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, glm::value_ptr(projection_matrix));

        // 라이팅 설정
        glUniform3f(glGetUniformLocation(shader_program, "lightPos"), 1.2f, 1.0f, 2.0f);
        glUniform3f(glGetUniformLocation(shader_program, "lightColor"), 1.0f, 1.0f, 1.0f);
        glUniform3f(glGetUniformLocation(shader_program, "objectColor"), 0.8f, 0.8f, 0.9f);
        glUniform3f(glGetUniformLocation(shader_program, "viewPos"),
                   camera_position.x, camera_position.y, camera_position.z);

        // 3D 모델 렌더링
        model.Draw(shader_program);

        glBindFramebuffer(GL_FRAMEBUFFER, 0);
    }

    void RenderImGuiPanel() {
        if (ImGui::Begin("3D Equipment View")) {
            ImVec2 panel_size = ImGui::GetContentRegionAvail();
            SetViewportSize(panel_size);

            Render();

            // 렌더링된 텍스처를 ImGui 이미지로 표시
            ImGui::Image(reinterpret_cast<void*>(static_cast<intptr_t>(color_texture)),
                        viewport_size, ImVec2(0, 1), ImVec2(1, 0));

            // 마우스 인터랙션 처리
            if (ImGui::IsItemHovered()) {
                ImGuiIO& io = ImGui::GetIO();
                if (io.MouseDown[0]) {
                    // 카메라 회전
                    float sensitivity = 0.01f;
                    camera_position = glm::rotate(glm::mat4(1.0f),
                                                io.MouseDelta.x * sensitivity,
                                                glm::vec3(0, 1, 0)) * glm::vec4(camera_position, 1.0f);
                }

                // 마우스 휠로 줌
                if (io.MouseWheel != 0) {
                    camera_distance *= (1.0f - io.MouseWheel * 0.1f);
                    camera_distance = glm::clamp(camera_distance, 1.0f, 20.0f);

                    glm::vec3 direction = glm::normalize(camera_position - camera_target);
                    camera_position = camera_target + direction * camera_distance;
                }
            }
        }
        ImGui::End();
    }

private:
    void SetupFramebuffer() {
        if (framebuffer != 0) {
            glDeleteFramebuffers(1, &framebuffer);
            glDeleteTextures(1, &color_texture);
            glDeleteTextures(1, &depth_texture);
        }

        // 프레임버퍼 생성
        glGenFramebuffers(1, &framebuffer);
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);

        // 컬러 텍스처
        glGenTextures(1, &color_texture);
        glBindTexture(GL_TEXTURE_2D, color_texture);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, static_cast<int>(viewport_size.x),
                    static_cast<int>(viewport_size.y), 0, GL_RGB, GL_UNSIGNED_BYTE, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color_texture, 0);

        // 깊이 텍스처
        glGenTextures(1, &depth_texture);
        glBindTexture(GL_TEXTURE_2D, depth_texture);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, static_cast<int>(viewport_size.x),
                    static_cast<int>(viewport_size.y), 0, GL_DEPTH_COMPONENT, GL_FLOAT, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depth_texture, 0);

        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
            printf("Framebuffer not complete!\n");
        }

        glBindFramebuffer(GL_FRAMEBUFFER, 0);
    }

    GLuint CreateShaderProgram(const char* vertex_source, const char* fragment_source) {
        // 셰이더 컴파일 로직 (이전 예제와 동일)
        // ... 생략 ...
        return 0; // 실제 구현에서는 컴파일된 프로그램 반환
    }
};

} // namespace SemiconductorHMI
```

---

## 🔧 **기초 실습 (45분) - 커스텀 드로잉 및 위젯 개발**

### 2. 성능 최적화 및 메모리 관리

#### 2.1 메모리 풀링 시스템
```cpp
#include <memory_resource>
#include <array>

namespace SemiconductorHMI {

template<size_t BlockSize, size_t BlockCount>
class MemoryPool {
private:
    alignas(std::max_align_t) std::array<std::byte, BlockSize * BlockCount> memory;
    std::array<bool, BlockCount> used;
    size_t next_free;

public:
    MemoryPool() : next_free(0) {
        used.fill(false);
    }

    void* Allocate(size_t size) {
        if (size > BlockSize) return nullptr;

        for (size_t i = next_free; i < BlockCount; ++i) {
            if (!used[i]) {
                used[i] = true;
                next_free = i + 1;
                return &memory[i * BlockSize];
            }
        }

        // 처음부터 다시 검색
        for (size_t i = 0; i < next_free; ++i) {
            if (!used[i]) {
                used[i] = true;
                next_free = i + 1;
                return &memory[i * BlockSize];
            }
        }

        return nullptr; // 풀이 가득 참
    }

    void Deallocate(void* ptr) {
        if (!ptr) return;

        auto* byte_ptr = static_cast<std::byte*>(ptr);
        if (byte_ptr < memory.data() || byte_ptr >= memory.data() + memory.size()) {
            return; // 이 풀에 속하지 않는 포인터
        }

        size_t index = (byte_ptr - memory.data()) / BlockSize;
        if (index < BlockCount) {
            used[index] = false;
            next_free = std::min(next_free, index);
        }
    }

    size_t GetUsedCount() const {
        return std::count(used.begin(), used.end(), true);
    }

    float GetUsageRatio() const {
        return static_cast<float>(GetUsedCount()) / BlockCount;
    }
};

class HighPerformanceRenderer {
private:
    // 다양한 크기의 메모리 풀
    MemoryPool<64, 1024> small_pool;      // 작은 객체용
    MemoryPool<256, 512> medium_pool;     // 중간 객체용
    MemoryPool<1024, 128> large_pool;     // 큰 객체용

    // GPU 리소스 관리
    struct GPUBuffer {
        GLuint buffer_id;
        size_t size;
        GLenum usage;
        bool in_use;
    };

    std::vector<GPUBuffer> vertex_buffers;
    std::vector<GPUBuffer> index_buffers;
    std::queue<size_t> free_vertex_buffers;
    std::queue<size_t> free_index_buffers;

public:
    void* AllocateTemporary(size_t size) {
        if (size <= 64) return small_pool.Allocate(size);
        if (size <= 256) return medium_pool.Allocate(size);
        if (size <= 1024) return large_pool.Allocate(size);

        // 풀 크기를 초과하는 경우 일반 할당
        return std::malloc(size);
    }

    void DeallocateTemporary(void* ptr, size_t size) {
        if (size <= 64) {
            small_pool.Deallocate(ptr);
        } else if (size <= 256) {
            medium_pool.Deallocate(ptr);
        } else if (size <= 1024) {
            large_pool.Deallocate(ptr);
        } else {
            std::free(ptr);
        }
    }

    GLuint AcquireVertexBuffer(size_t size) {
        if (!free_vertex_buffers.empty()) {
            size_t index = free_vertex_buffers.front();
            free_vertex_buffers.pop();

            auto& buffer = vertex_buffers[index];
            if (buffer.size >= size) {
                buffer.in_use = true;
                return buffer.buffer_id;
            }
        }

        // 새 버퍼 생성
        GLuint buffer_id;
        glGenBuffers(1, &buffer_id);
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id);
        glBufferData(GL_ARRAY_BUFFER, size, nullptr, GL_DYNAMIC_DRAW);

        vertex_buffers.push_back({buffer_id, size, GL_DYNAMIC_DRAW, true});
        return buffer_id;
    }

    void ReleaseVertexBuffer(GLuint buffer_id) {
        for (size_t i = 0; i < vertex_buffers.size(); ++i) {
            if (vertex_buffers[i].buffer_id == buffer_id) {
                vertex_buffers[i].in_use = false;
                free_vertex_buffers.push(i);
                break;
            }
        }
    }

    void PrintMemoryStats() {
        printf("Memory Pool Usage:\n");
        printf("  Small Pool (64B): %.1f%% (%zu/%zu)\n",
               small_pool.GetUsageRatio() * 100, small_pool.GetUsedCount(), 1024);
        printf("  Medium Pool (256B): %.1f%% (%zu/%zu)\n",
               medium_pool.GetUsageRatio() * 100, medium_pool.GetUsedCount(), 512);
        printf("  Large Pool (1KB): %.1f%% (%zu/%zu)\n",
               large_pool.GetUsageRatio() * 100, large_pool.GetUsedCount(), 128);

        size_t used_gpu_buffers = 0;
        for (const auto& buffer : vertex_buffers) {
            if (buffer.in_use) used_gpu_buffers++;
        }
        printf("  GPU Vertex Buffers: %zu/%zu in use\n", used_gpu_buffers, vertex_buffers.size());
    }
};

} // namespace SemiconductorHMI
```

---

## 🔧 **기초 실습 (45분) - 커스텀 드로잉 및 위젯 개발**

#### 2.2 프레임 레이트 최적화
```cpp
namespace SemiconductorHMI {

class PerformanceProfiler {
private:
    struct FrameData {
        std::chrono::high_resolution_clock::time_point start_time;
        std::chrono::high_resolution_clock::time_point end_time;
        float cpu_time;
        float gpu_time;
        size_t draw_calls;
        size_t vertices;
    };

    std::array<FrameData, 60> frame_history;
    size_t current_frame_index;
    GLuint timer_queries[2];
    bool queries_available;

public:
    PerformanceProfiler() : current_frame_index(0), queries_available(false) {
        glGenQueries(2, timer_queries);
    }

    ~PerformanceProfiler() {
        glDeleteQueries(2, timer_queries);
    }

    void BeginFrame() {
        auto& frame = frame_history[current_frame_index];
        frame.start_time = std::chrono::high_resolution_clock::now();
        frame.draw_calls = 0;
        frame.vertices = 0;

        // GPU 타이머 시작
        glBeginQuery(GL_TIME_ELAPSED, timer_queries[0]);
    }

    void EndFrame() {
        glEndQuery(GL_TIME_ELAPSED);

        auto& frame = frame_history[current_frame_index];
        frame.end_time = std::chrono::high_resolution_clock::now();

        auto duration = frame.end_time - frame.start_time;
        frame.cpu_time = std::chrono::duration<float, std::milli>(duration).count();

        // GPU 시간 조회 (이전 프레임 결과)
        if (queries_available) {
            GLuint64 gpu_time_ns;
            glGetQueryObjectui64v(timer_queries[1], GL_QUERY_RESULT, &gpu_time_ns);
            frame.gpu_time = gpu_time_ns / 1000000.0f; // 나노초를 밀리초로 변환
        }

        // 쿼리 스왑
        std::swap(timer_queries[0], timer_queries[1]);
        queries_available = true;

        current_frame_index = (current_frame_index + 1) % frame_history.size();
    }

    void AddDrawCall(size_t vertex_count) {
        auto& frame = frame_history[current_frame_index];
        frame.draw_calls++;
        frame.vertices += vertex_count;
    }

    float GetAverageCPUTime() const {
        float total = 0.0f;
        for (const auto& frame : frame_history) {
            total += frame.cpu_time;
        }
        return total / frame_history.size();
    }

    float GetAverageGPUTime() const {
        if (!queries_available) return 0.0f;

        float total = 0.0f;
        for (const auto& frame : frame_history) {
            total += frame.gpu_time;
        }
        return total / frame_history.size();
    }

    size_t GetAverageDrawCalls() const {
        size_t total = 0;
        for (const auto& frame : frame_history) {
            total += frame.draw_calls;
        }
        return total / frame_history.size();
    }

    void RenderPerformanceGraph() {
        if (ImGui::Begin("Performance Monitor")) {
            // CPU 시간 그래프
            std::array<float, 60> cpu_times;
            for (size_t i = 0; i < frame_history.size(); ++i) {
                cpu_times[i] = frame_history[i].cpu_time;
            }

            ImGui::PlotLines("CPU Time (ms)", cpu_times.data(), cpu_times.size(),
                           current_frame_index, nullptr, 0.0f, 50.0f, ImVec2(0, 80));

            // GPU 시간 그래프
            if (queries_available) {
                std::array<float, 60> gpu_times;
                for (size_t i = 0; i < frame_history.size(); ++i) {
                    gpu_times[i] = frame_history[i].gpu_time;
                }

                ImGui::PlotLines("GPU Time (ms)", gpu_times.data(), gpu_times.size(),
                               current_frame_index, nullptr, 0.0f, 50.0f, ImVec2(0, 80));
            }

            // 통계 정보
            ImGui::Separator();
            ImGui::Text("Average CPU Time: %.2f ms", GetAverageCPUTime());
            ImGui::Text("Average GPU Time: %.2f ms", GetAverageGPUTime());
            ImGui::Text("Average FPS: %.1f", 1000.0f / GetAverageCPUTime());
            ImGui::Text("Average Draw Calls: %zu", GetAverageDrawCalls());

            // 성능 경고
            if (GetAverageCPUTime() > 16.67f) { // 60 FPS 기준
                ImGui::TextColored(ImVec4(1, 0, 0, 1), "Warning: Frame time exceeds 16.67ms!");
            }
        }
        ImGui::End();
    }
};

class AdaptiveQualityManager {
private:
    float target_frame_time;
    float quality_scale;
    int shadow_quality;
    int texture_quality;
    bool dynamic_lighting;

public:
    AdaptiveQualityManager(float target_fps = 60.0f)
        : target_frame_time(1000.0f / target_fps)
        , quality_scale(1.0f)
        , shadow_quality(2)
        , texture_quality(2)
        , dynamic_lighting(true) {}

    void UpdateQuality(float current_frame_time) {
        const float tolerance = 2.0f; // 2ms 허용 오차

        if (current_frame_time > target_frame_time + tolerance) {
            // 성능이 목표에 미달하면 품질 낮춤
            ReduceQuality();
        } else if (current_frame_time < target_frame_time - tolerance) {
            // 성능에 여유가 있으면 품질 높임
            IncreaseQuality();
        }
    }

private:
    void ReduceQuality() {
        if (dynamic_lighting) {
            dynamic_lighting = false;
            return;
        }

        if (shadow_quality > 0) {
            shadow_quality--;
            return;
        }

        if (texture_quality > 0) {
            texture_quality--;
            return;
        }

        if (quality_scale > 0.5f) {
            quality_scale -= 0.1f;
        }
    }

    void IncreaseQuality() {
        if (quality_scale < 1.0f) {
            quality_scale += 0.1f;
            return;
        }

        if (texture_quality < 2) {
            texture_quality++;
            return;
        }

        if (shadow_quality < 2) {
            shadow_quality++;
            return;
        }

        if (!dynamic_lighting) {
            dynamic_lighting = true;
        }
    }

public:
    float GetQualityScale() const { return quality_scale; }
    int GetShadowQuality() const { return shadow_quality; }
    int GetTextureQuality() const { return texture_quality; }
    bool IsDynamicLightingEnabled() const { return dynamic_lighting; }
};

} // namespace SemiconductorHMI
```

---

## 🚀 **심화 실습 (45분) - 3D 시각화 통합 및 고급 이벤트 처리**

### 실습 3: 멀티터치 및 제스처 인식

#### 3.1 제스처 인식 시스템
```cpp
// include/input/gesture_recognizer.h
#pragma once

#include <imgui.h>
#include <vector>
#include <chrono>
#include <cmath>

namespace SemiconductorHMI::Input {

enum class GestureType {
    None,
    Tap,
    DoubleTap,
    LongPress,
    Pan,
    Pinch,
    Rotate,
    Swipe
};

struct TouchPoint {
    int id;
    ImVec2 position;
    ImVec2 start_position;
    std::chrono::high_resolution_clock::time_point start_time;
    bool active;
};

struct GestureEvent {
    GestureType type;
    ImVec2 position;
    ImVec2 delta;
    float scale;
    float rotation;
    float velocity;
    int touch_count;
    std::chrono::duration<float> duration;
};

class GestureRecognizer {
private:
    std::vector<TouchPoint> touch_points;
    std::vector<std::function<void(const GestureEvent&)>> gesture_callbacks;

    // 설정값들
    float tap_threshold = 10.0f;        // 픽셀
    float long_press_duration = 0.5f;   // 초
    float double_tap_time = 0.3f;       // 초
    float swipe_threshold = 50.0f;      // 픽셀
    float pinch_threshold = 10.0f;      // 픽셀

    // 상태 추적
    std::chrono::high_resolution_clock::time_point last_tap_time;
    ImVec2 last_tap_position;
    bool is_panning = false;
    bool is_pinching = false;
    float initial_distance = 0.0f;
    float initial_angle = 0.0f;

public:
    void Update() {
        ImGuiIO& io = ImGui::GetIO();

        // 단일 터치 처리 (마우스 시뮬레이션)
        UpdateSingleTouch(io);

        // 멀티터치 처리 (실제 구현시 플랫폼별 API 필요)
        // UpdateMultiTouch();

        // 제스처 인식
        RecognizeGestures();

        // 비활성 터치 포인트 정리
        CleanupInactiveTouches();
    }

    void AddGestureCallback(std::function<void(const GestureEvent&)> callback) {
        gesture_callbacks.push_back(callback);
    }

private:
    void UpdateSingleTouch(ImGuiIO& io) {
        if (io.MouseDown[0]) {
            // 터치 시작 또는 계속
            if (touch_points.empty() || !touch_points[0].active) {
                // 새로운 터치 시작
                TouchPoint touch;
                touch.id = 0;
                touch.position = io.MousePos;
                touch.start_position = io.MousePos;
                touch.start_time = std::chrono::high_resolution_clock::now();
                touch.active = true;

                if (touch_points.empty()) {
                    touch_points.push_back(touch);
                } else {
                    touch_points[0] = touch;
                }
            } else {
                // 터치 위치 업데이트
                touch_points[0].position = io.MousePos;
            }
        } else {
            // 터치 종료
            if (!touch_points.empty() && touch_points[0].active) {
                touch_points[0].active = false;
            }
        }
    }

    void RecognizeGestures() {
        if (touch_points.empty()) return;

        const auto& primary_touch = touch_points[0];

        if (primary_touch.active) {
            RecognizeActiveGestures(primary_touch);
        } else {
            RecognizeEndGestures(primary_touch);
        }
    }

    void RecognizeActiveGestures(const TouchPoint& touch) {
        auto now = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration<float>(now - touch.start_time);
        ImVec2 delta = ImVec2(touch.position.x - touch.start_position.x,
                             touch.position.y - touch.start_position.y);
        float distance = std::sqrt(delta.x * delta.x + delta.y * delta.y);

        // Long Press 감지
        if (duration.count() > long_press_duration && distance < tap_threshold && !is_panning) {
            GestureEvent event;
            event.type = GestureType::LongPress;
            event.position = touch.position;
            event.delta = delta;
            event.touch_count = 1;
            event.duration = duration;

            TriggerGestureEvent(event);
        }

        // Pan 감지
        if (distance > tap_threshold && !is_panning) {
            is_panning = true;
        }

        if (is_panning) {
            GestureEvent event;
            event.type = GestureType::Pan;
            event.position = touch.position;
            event.delta = delta;
            event.touch_count = 1;
            event.duration = duration;

            TriggerGestureEvent(event);
        }
    }

    void RecognizeEndGestures(const TouchPoint& touch) {
        auto now = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration<float>(now - touch.start_time);
        ImVec2 delta = ImVec2(touch.position.x - touch.start_position.x,
                             touch.position.y - touch.start_position.y);
        float distance = std::sqrt(delta.x * delta.x + delta.y * delta.y);

        if (is_panning) {
            // Pan 종료
            is_panning = false;

            // Swipe 감지
            if (distance > swipe_threshold && duration.count() < 0.5f) {
                GestureEvent event;
                event.type = GestureType::Swipe;
                event.position = touch.position;
                event.delta = delta;
                event.velocity = distance / duration.count();
                event.touch_count = 1;
                event.duration = duration;

                TriggerGestureEvent(event);
            }
        } else if (distance < tap_threshold) {
            // Tap 또는 Double Tap 감지
            auto time_since_last_tap = std::chrono::duration<float>(now - last_tap_time);

            if (time_since_last_tap.count() < double_tap_time &&
                std::abs(touch.position.x - last_tap_position.x) < tap_threshold &&
                std::abs(touch.position.y - last_tap_position.y) < tap_threshold) {
                // Double Tap
                GestureEvent event;
                event.type = GestureType::DoubleTap;
                event.position = touch.position;
                event.delta = delta;
                event.touch_count = 1;
                event.duration = duration;

                TriggerGestureEvent(event);

                // 마지막 탭 시간 리셋 (트리플 탭 방지)
                last_tap_time = std::chrono::high_resolution_clock::time_point{};
            } else {
                // Single Tap
                GestureEvent event;
                event.type = GestureType::Tap;
                event.position = touch.position;
                event.delta = delta;
                event.touch_count = 1;
                event.duration = duration;

                TriggerGestureEvent(event);

                last_tap_time = now;
                last_tap_position = touch.position;
            }
        }
    }

    void TriggerGestureEvent(const GestureEvent& event) {
        for (const auto& callback : gesture_callbacks) {
            callback(event);
        }
    }

    void CleanupInactiveTouches() {
        touch_points.erase(
            std::remove_if(touch_points.begin(), touch_points.end(),
                [](const TouchPoint& touch) { return !touch.active; }),
            touch_points.end()
        );
    }

    float CalculateDistance(const ImVec2& p1, const ImVec2& p2) {
        float dx = p2.x - p1.x;
        float dy = p2.y - p1.y;
        return std::sqrt(dx * dx + dy * dy);
    }

    float CalculateAngle(const ImVec2& p1, const ImVec2& p2) {
        return std::atan2(p2.y - p1.y, p2.x - p1.x);
    }
};

} // namespace SemiconductorHMI::Input
```

---

## 💼 **Hands-on 프로젝트 (45분) - 실시간 반도체 장비 3D 모니터링 시스템**

### 최종 프로젝트: 통합 3D HMI 플랫폼

#### 4.1 통합 애플리케이션 클래스
```cpp
// include/advanced_semiconductor_hmi.h
#pragma once

#include "hmi_application.h"
#include "ui_components/wafer_map_widget.h"
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