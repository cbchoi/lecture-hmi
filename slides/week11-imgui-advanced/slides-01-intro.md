# Week 11: ImGUI C++ 심화 - 고급 렌더링 및 커스텀 시각화

## 🎯 **이론 강의 - 고급 렌더링 아키텍처 및 3D 통합**

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

## 🔧 **기초 실습 - 커스텀 드로잉 및 위젯 개발**

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

## 🔧 **기초 실습 - 커스텀 드로잉 및 위젯 개발**

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
