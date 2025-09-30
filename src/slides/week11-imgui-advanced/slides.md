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
        glm::vec3 forward = current_rot * glm::vec3(0, 0, -1);
        target = position + forward * orbit_distance;

        if (t >= 1.0f) {
            is_animating = false;
        }
    }

    float EaseInOutCubic(float t) {
        return t < 0.5f ? 4 * t * t * t : 1 - pow(-2 * t + 2, 3) / 2;
    }

    // 프리셋 카메라 위치들
    void SetPresetView(const std::string& preset) {
        if (preset == "Front") {
            AnimateTo(glm::vec3(0, 0, 15), glm::vec3(0, 0, 0));
        } else if (preset == "Top") {
            AnimateTo(glm::vec3(0, 20, 0), glm::vec3(0, 0, 0));
        } else if (preset == "Side") {
            AnimateTo(glm::vec3(15, 5, 0), glm::vec3(0, 0, 0));
        } else if (preset == "Isometric") {
            AnimateTo(glm::vec3(10, 10, 10), glm::vec3(0, 0, 0));
        }
    }

    // Getter 메서드들
    glm::mat4 GetViewMatrix() const { return view_matrix; }
    glm::mat4 GetProjectionMatrix() const { return projection_matrix; }
    glm::vec3 GetPosition() const { return position; }
    glm::vec3 GetTarget() const { return target; }
    float GetFOV() const { return fov; }
    CameraMode GetMode() const { return mode; }

    // Setter 메서드들
    void SetMode(CameraMode new_mode) { mode = new_mode; }
    void SetAspectRatio(float new_aspect) { aspect_ratio = new_aspect; }
    void SetTarget(glm::vec3 new_target) {
        target = new_target;
        if (mode == CameraMode::OrbitTarget) {
            UpdateOrbitPosition();
        }
    }

private:
    glm::mat4 view_matrix;
    glm::mat4 projection_matrix;
};

} // namespace SemiconductorHMI
```

### 3D 모델 렌더링 시스템

#### 2. 메시 렌더러 구현
```cpp
// MeshRenderer.h
#pragma once
#include <vector>
#include <memory>
#include <string>
#include <unordered_map>
#include <glm/glm.hpp>
#include <GL/gl3w.h>

namespace SemiconductorHMI {

struct Vertex {
    glm::vec3 position;
    glm::vec3 normal;
    glm::vec2 tex_coords;
    glm::vec3 tangent;
};

struct Material {
    glm::vec3 ambient;
    glm::vec3 diffuse;
    glm::vec3 specular;
    float shininess;

    GLuint diffuse_texture;
    GLuint normal_texture;
    GLuint specular_texture;

    Material() : ambient(0.2f), diffuse(0.8f), specular(1.0f), shininess(32.0f),
                diffuse_texture(0), normal_texture(0), specular_texture(0) {}
};

class Mesh {
private:
    std::vector<Vertex> vertices;
    std::vector<unsigned int> indices;
    Material material;

    GLuint VAO, VBO, EBO;
    bool initialized;

public:
    Mesh(std::vector<Vertex> verts, std::vector<unsigned int> inds, Material mat)
        : vertices(std::move(verts)), indices(std::move(inds)), material(mat), initialized(false) {
        SetupMesh();
    }

    ~Mesh() {
        if (initialized) {
            glDeleteVertexArrays(1, &VAO);
            glDeleteBuffers(1, &VBO);
            glDeleteBuffers(1, &EBO);
        }
    }

    void Draw(GLuint shader_program) {
        // 머티리얼 바인딩
        BindMaterial(shader_program);

        // 메시 그리기
        glBindVertexArray(VAO);
        glDrawElements(GL_TRIANGLES, indices.size(), GL_UNSIGNED_INT, 0);
        glBindVertexArray(0);
    }

private:
    void SetupMesh() {
        glGenVertexArrays(1, &VAO);
        glGenBuffers(1, &VBO);
        glGenBuffers(1, &EBO);

        glBindVertexArray(VAO);

        glBindBuffer(GL_ARRAY_BUFFER, VBO);
        glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(Vertex), &vertices[0], GL_STATIC_DRAW);

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO);
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int), &indices[0], GL_STATIC_DRAW);

        // 정점 속성 설정
        // Position
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)0);
        // Normal
        glEnableVertexAttribArray(1);
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, normal));
        // Texture Coords
        glEnableVertexAttribArray(2);
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, tex_coords));
        // Tangent
        glEnableVertexAttribArray(3);
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, tangent));

        glBindVertexArray(0);
        initialized = true;
    }

    void BindMaterial(GLuint shader_program) {
        glUniform3fv(glGetUniformLocation(shader_program, "material.ambient"), 1, &material.ambient[0]);
        glUniform3fv(glGetUniformLocation(shader_program, "material.diffuse"), 1, &material.diffuse[0]);
        glUniform3fv(glGetUniformLocation(shader_program, "material.specular"), 1, &material.specular[0]);
        glUniform1f(glGetUniformLocation(shader_program, "material.shininess"), material.shininess);

        // 텍스처 바인딩
        if (material.diffuse_texture) {
            glActiveTexture(GL_TEXTURE0);
            glBindTexture(GL_TEXTURE_2D, material.diffuse_texture);
            glUniform1i(glGetUniformLocation(shader_program, "material.texture_diffuse"), 0);
        }

        if (material.normal_texture) {
            glActiveTexture(GL_TEXTURE1);
            glBindTexture(GL_TEXTURE_2D, material.normal_texture);
            glUniform1i(glGetUniformLocation(shader_program, "material.texture_normal"), 1);
        }

        if (material.specular_texture) {
            glActiveTexture(GL_TEXTURE2);
            glBindTexture(GL_TEXTURE_2D, material.specular_texture);
            glUniform1i(glGetUniformLocation(shader_program, "material.texture_specular"), 2);
        }
    }
};

class Model {
private:
    std::vector<std::unique_ptr<Mesh>> meshes;
    std::string directory;
    glm::mat4 model_matrix;

public:
    Model() : model_matrix(1.0f) {}

    void AddMesh(std::unique_ptr<Mesh> mesh) {
        meshes.push_back(std::move(mesh));
    }

    void Draw(GLuint shader_program) {
        for (auto& mesh : meshes) {
            mesh->Draw(shader_program);
        }
    }

    void SetTransform(const glm::mat4& transform) {
        model_matrix = transform;
    }

    glm::mat4 GetTransform() const {
        return model_matrix;
    }

    // 기본 도형 생성 메서드들
    static std::unique_ptr<Model> CreateCube(float size = 1.0f) {
        auto model = std::make_unique<Model>();

        std::vector<Vertex> vertices = {
            // Front face
            {{-size, -size,  size}, {0, 0, 1}, {0, 0}, {1, 0, 0}},
            {{ size, -size,  size}, {0, 0, 1}, {1, 0}, {1, 0, 0}},
            {{ size,  size,  size}, {0, 0, 1}, {1, 1}, {1, 0, 0}},
            {{-size,  size,  size}, {0, 0, 1}, {0, 1}, {1, 0, 0}},
            // Back face
            {{-size, -size, -size}, {0, 0, -1}, {1, 0}, {-1, 0, 0}},
            {{-size,  size, -size}, {0, 0, -1}, {1, 1}, {-1, 0, 0}},
            {{ size,  size, -size}, {0, 0, -1}, {0, 1}, {-1, 0, 0}},
            {{ size, -size, -size}, {0, 0, -1}, {0, 0}, {-1, 0, 0}},
        };

        std::vector<unsigned int> indices = {
            0, 1, 2, 2, 3, 0,   // front
            4, 5, 6, 6, 7, 4,   // back
            3, 2, 6, 6, 5, 3,   // top
            4, 7, 1, 1, 0, 4,   // bottom
            4, 0, 3, 3, 5, 4,   // left
            1, 7, 6, 6, 2, 1    // right
        };

        Material mat;
        mat.diffuse = glm::vec3(0.7f, 0.7f, 0.7f);
        mat.specular = glm::vec3(0.5f, 0.5f, 0.5f);
        mat.shininess = 32.0f;

        auto mesh = std::make_unique<Mesh>(std::move(vertices), std::move(indices), mat);
        model->AddMesh(std::move(mesh));

        return model;
    }

    static std::unique_ptr<Model> CreateSphere(float radius = 1.0f, int segments = 32) {
        auto model = std::make_unique<Model>();

        std::vector<Vertex> vertices;
        std::vector<unsigned int> indices;

        // 구체 정점 생성
        for (int i = 0; i <= segments; ++i) {
            float theta = i * glm::pi<float>() / segments;

            for (int j = 0; j <= segments; ++j) {
                float phi = j * 2 * glm::pi<float>() / segments;

                Vertex vertex;
                vertex.position.x = radius * sin(theta) * cos(phi);
                vertex.position.y = radius * cos(theta);
                vertex.position.z = radius * sin(theta) * sin(phi);

                vertex.normal = glm::normalize(vertex.position);
                vertex.tex_coords.x = (float)j / segments;
                vertex.tex_coords.y = (float)i / segments;

                // 탄젠트 계산
                vertex.tangent.x = -sin(phi);
                vertex.tangent.y = 0;
                vertex.tangent.z = cos(phi);

                vertices.push_back(vertex);
            }
        }

        // 인덱스 생성
        for (int i = 0; i < segments; ++i) {
            for (int j = 0; j < segments; ++j) {
                int current = i * (segments + 1) + j;
                int next = current + segments + 1;

                indices.push_back(current);
                indices.push_back(next);
                indices.push_back(current + 1);

                indices.push_back(current + 1);
                indices.push_back(next);
                indices.push_back(next + 1);
            }
        }

        Material mat;
        mat.diffuse = glm::vec3(0.8f, 0.3f, 0.3f);
        mat.specular = glm::vec3(1.0f, 1.0f, 1.0f);
        mat.shininess = 64.0f;

        auto mesh = std::make_unique<Mesh>(std::move(vertices), std::move(indices), mat);
        model->AddMesh(std::move(mesh));

        return model;
    }

    static std::unique_ptr<Model> CreateCylinder(float radius = 1.0f, float height = 2.0f, int segments = 32) {
        auto model = std::make_unique<Model>();

        std::vector<Vertex> vertices;
        std::vector<unsigned int> indices;

        // 실린더 측면 정점 생성
        for (int i = 0; i <= segments; ++i) {
            float angle = i * 2 * glm::pi<float>() / segments;
            float x = cos(angle);
            float z = sin(angle);

            // 아래쪽 정점
            Vertex bottom_vertex;
            bottom_vertex.position = glm::vec3(x * radius, -height/2, z * radius);
            bottom_vertex.normal = glm::vec3(x, 0, z);
            bottom_vertex.tex_coords = glm::vec2((float)i / segments, 0);
            bottom_vertex.tangent = glm::vec3(-z, 0, x);
            vertices.push_back(bottom_vertex);

            // 위쪽 정점
            Vertex top_vertex;
            top_vertex.position = glm::vec3(x * radius, height/2, z * radius);
            top_vertex.normal = glm::vec3(x, 0, z);
            top_vertex.tex_coords = glm::vec2((float)i / segments, 1);
            top_vertex.tangent = glm::vec3(-z, 0, x);
            vertices.push_back(top_vertex);
        }

        // 측면 인덱스 생성
        for (int i = 0; i < segments; ++i) {
            int current = i * 2;
            int next = (i + 1) * 2;

            // 하단 삼각형
            indices.push_back(current);
            indices.push_back(next);
            indices.push_back(current + 1);

            // 상단 삼각형
            indices.push_back(current + 1);
            indices.push_back(next);
            indices.push_back(next + 1);
        }

        // 상하 뚜껑 정점 및 인덱스 추가 (생략 - 복잡성을 위해)

        Material mat;
        mat.diffuse = glm::vec3(0.3f, 0.8f, 0.3f);
        mat.specular = glm::vec3(0.7f, 0.7f, 0.7f);
        mat.shininess = 32.0f;

        auto mesh = std::make_unique<Mesh>(std::move(vertices), std::move(indices), mat);
        model->AddMesh(std::move(mesh));

        return model;
    }
};

} // namespace SemiconductorHMI
```

---

## 실습 2: 물리 기반 렌더링 (PBR) 구현

### 실습 목표
- 물리 기반 렌더링 셰이더 구현
- 머티리얼 시스템 확장
- 환경 매핑 및 IBL (Image-Based Lighting)
- 실시간 그림자 시스템

### PBR 셰이더 시스템

#### 1. PBR 셰이더 구현
```cpp
// PBRShader.h
#pragma once
#include <string>
#include <glm/glm.hpp>
#include <GL/gl3w.h>

namespace SemiconductorHMI {

class PBRShader {
private:
    GLuint program_id;

    // 유니폼 위치 캐시
    GLint mvp_matrix_location;
    GLint model_matrix_location;
    GLint view_matrix_location;
    GLint projection_matrix_location;
    GLint normal_matrix_location;

    GLint camera_pos_location;
    GLint light_positions_location;
    GLint light_colors_location;
    GLint light_count_location;

    GLint albedo_location;
    GLint metallic_location;
    GLint roughness_location;
    GLint ao_location;

public:
    PBRShader() : program_id(0) {}

    bool Initialize() {
        const char* vertex_shader = R"(
        #version 450 core

        layout (location = 0) in vec3 aPos;
        layout (location = 1) in vec3 aNormal;
        layout (location = 2) in vec2 aTexCoords;
        layout (location = 3) in vec3 aTangent;

        uniform mat4 uModel;
        uniform mat4 uView;
        uniform mat4 uProjection;
        uniform mat3 uNormalMatrix;

        out vec3 FragPos;
        out vec3 Normal;
        out vec2 TexCoords;
        out vec3 Tangent;
        out vec3 Bitangent;

        void main() {
            FragPos = vec3(uModel * vec4(aPos, 1.0));
            Normal = uNormalMatrix * aNormal;
            TexCoords = aTexCoords;
            Tangent = uNormalMatrix * aTangent;
            Bitangent = cross(Normal, Tangent);

            gl_Position = uProjection * uView * vec4(FragPos, 1.0);
        }
        )";

        const char* fragment_shader = R"(
        #version 450 core

        in vec3 FragPos;
        in vec3 Normal;
        in vec2 TexCoords;
        in vec3 Tangent;
        in vec3 Bitangent;

        uniform vec3 uCameraPos;
        uniform vec3 uLightPositions[4];
        uniform vec3 uLightColors[4];
        uniform int uLightCount;

        uniform vec3 uAlbedo;
        uniform float uMetallic;
        uniform float uRoughness;
        uniform float uAO;

        uniform sampler2D uAlbedoMap;
        uniform sampler2D uNormalMap;
        uniform sampler2D uMetallicMap;
        uniform sampler2D uRoughnessMap;
        uniform sampler2D uAOMap;

        out vec4 FragColor;

        const float PI = 3.14159265359;

        // 분산 함수 (Normal Distribution Function)
        float DistributionGGX(vec3 N, vec3 H, float roughness) {
            float a = roughness * roughness;
            float a2 = a * a;
            float NdotH = max(dot(N, H), 0.0);
            float NdotH2 = NdotH * NdotH;

            float num = a2;
            float denom = (NdotH2 * (a2 - 1.0) + 1.0);
            denom = PI * denom * denom;

            return num / denom;
        }

        // 기하학적 셰도잉 함수
        float GeometrySchlickGGX(float NdotV, float roughness) {
            float r = (roughness + 1.0);
            float k = (r * r) / 8.0;

            float num = NdotV;
            float denom = NdotV * (1.0 - k) + k;

            return num / denom;
        }

        float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness) {
            float NdotV = max(dot(N, V), 0.0);
            float NdotL = max(dot(N, L), 0.0);
            float ggx2 = GeometrySchlickGGX(NdotV, roughness);
            float ggx1 = GeometrySchlickGGX(NdotL, roughness);

            return ggx1 * ggx2;
        }

        // 프레넬 반사 계수
        vec3 FresnelSchlick(float cosTheta, vec3 F0) {
            return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
        }

        vec3 GetNormalFromMap() {
            vec3 tangentNormal = texture(uNormalMap, TexCoords).xyz * 2.0 - 1.0;

            vec3 N = normalize(Normal);
            vec3 T = normalize(Tangent);
            vec3 B = normalize(Bitangent);
            mat3 TBN = mat3(T, B, N);

            return normalize(TBN * tangentNormal);
        }

        void main() {
            // 머티리얼 속성 샘플링
            vec3 albedo = pow(texture(uAlbedoMap, TexCoords).rgb * uAlbedo, 2.2);
            float metallic = texture(uMetallicMap, TexCoords).r * uMetallic;
            float roughness = texture(uRoughnessMap, TexCoords).r * uRoughness;
            float ao = texture(uAOMap, TexCoords).r * uAO;

            // 법선 벡터 계산
            vec3 N = GetNormalFromMap();
            vec3 V = normalize(uCameraPos - FragPos);

            // F0 계산 (금속의 경우 알베도, 비금속의 경우 0.04)
            vec3 F0 = vec3(0.04);
            F0 = mix(F0, albedo, metallic);

            vec3 Lo = vec3(0.0);

            // 모든 광원에 대한 계산
            for(int i = 0; i < uLightCount; ++i) {
                vec3 L = normalize(uLightPositions[i] - FragPos);
                vec3 H = normalize(V + L);
                float distance = length(uLightPositions[i] - FragPos);
                float attenuation = 1.0 / (distance * distance);
                vec3 radiance = uLightColors[i] * attenuation;

                // Cook-Torrance BRDF
                float NDF = DistributionGGX(N, H, roughness);
                float G = GeometrySmith(N, V, L, roughness);
                vec3 F = FresnelSchlick(max(dot(H, V), 0.0), F0);

                vec3 kS = F;
                vec3 kD = vec3(1.0) - kS;
                kD *= 1.0 - metallic;

                vec3 numerator = NDF * G * F;
                float denominator = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0) + 0.0001;
                vec3 specular = numerator / denominator;

                float NdotL = max(dot(N, L), 0.0);
                Lo += (kD * albedo / PI + specular) * radiance * NdotL;
            }

            // 환경광 (간단한 IBL 근사)
            vec3 ambient = vec3(0.03) * albedo * ao;
            vec3 color = ambient + Lo;

            // HDR 톤매핑 및 감마 보정
            color = color / (color + vec3(1.0));
            color = pow(color, vec3(1.0/2.2));

            FragColor = vec4(color, 1.0);
        }
        )";

        program_id = CreateShaderProgram(vertex_shader, fragment_shader);
        if (program_id == 0) return false;

        // 유니폼 위치 캐시
        CacheUniformLocations();

        return true;
    }

    void Use() {
        glUseProgram(program_id);
    }

    void SetMatrices(const glm::mat4& model, const glm::mat4& view, const glm::mat4& projection) {
        glUniformMatrix4fv(model_matrix_location, 1, GL_FALSE, &model[0][0]);
        glUniformMatrix4fv(view_matrix_location, 1, GL_FALSE, &view[0][0]);
        glUniformMatrix4fv(projection_matrix_location, 1, GL_FALSE, &projection[0][0]);

        glm::mat3 normal_matrix = glm::transpose(glm::inverse(glm::mat3(model)));
        glUniformMatrix3fv(normal_matrix_location, 1, GL_FALSE, &normal_matrix[0][0]);
    }

    void SetCamera(const glm::vec3& camera_pos) {
        glUniform3fv(camera_pos_location, 1, &camera_pos[0]);
    }

    void SetLights(const std::vector<glm::vec3>& positions, const std::vector<glm::vec3>& colors) {
        int count = std::min((int)positions.size(), 4);
        glUniform1i(light_count_location, count);

        if (count > 0) {
            glUniform3fv(light_positions_location, count, &positions[0][0]);
            glUniform3fv(light_colors_location, count, &colors[0][0]);
        }
    }

    void SetMaterial(const glm::vec3& albedo, float metallic, float roughness, float ao) {
        glUniform3fv(albedo_location, 1, &albedo[0]);
        glUniform1f(metallic_location, metallic);
        glUniform1f(roughness_location, roughness);
        glUniform1f(ao_location, ao);
    }

private:
    void CacheUniformLocations() {
        model_matrix_location = glGetUniformLocation(program_id, "uModel");
        view_matrix_location = glGetUniformLocation(program_id, "uView");
        projection_matrix_location = glGetUniformLocation(program_id, "uProjection");
        normal_matrix_location = glGetUniformLocation(program_id, "uNormalMatrix");

        camera_pos_location = glGetUniformLocation(program_id, "uCameraPos");
        light_positions_location = glGetUniformLocation(program_id, "uLightPositions");
        light_colors_location = glGetUniformLocation(program_id, "uLightColors");
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

---