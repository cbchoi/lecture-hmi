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
---
theme: default
class: text-center
highlighter: shiki
lineNumbers: true
drawings:
  persist: false
transition: slide-left
title: Week 11 - C++ Advanced Patterns (Template Metaprogramming, Performance, Modern C++)
mdc: true
---

# Week 11: C++ Advanced Patterns

## Template Metaprogramming, Performance Optimization, Modern C++

반도체 HMI 시스템을 위한 C++ 고급 기법

---
layout: two-cols
---

# 📚 **1. Template Metaprogramming**

## 1.1 Template Basics Review

### Function Template

```cpp
namespace SemiconductorHMI {

// 기본 함수 템플릿
template<typename T>
T Clamp(T value, T min, T max) {
    if (value < min) return min;
    if (value > max) return max;
    return value;
}

// 사용 예시
void UpdateTemperature(float temp) {
    // 컴파일 타임에 Clamp<float> 생성
    float clamped = Clamp(temp, 20.0f, 80.0f);
}

void UpdatePressure(int pressure) {
    // 컴파일 타임에 Clamp<int> 생성
    int clamped = Clamp(pressure, 0, 1000);
}

}
```

::right::

## 템플릿 동작 원리

**컴파일 타임 코드 생성**
- 템플릿은 코드를 생성하는 "틀"
- 각 타입마다 별도의 함수가 생성됨
- 타입 안전성 보장

**자동 타입 추론**
```cpp
// 명시적 타입 지정
Clamp<float>(temp, 20.0f, 80.0f);

// 타입 추론 (C++17부터 권장)
Clamp(temp, 20.0f, 80.0f);
```

**장점**
- 런타임 오버헤드 없음
- 타입 안전성
- 코드 재사용

**단점**
- 컴파일 시간 증가
- 바이너리 크기 증가
- 에러 메시지 복잡

---
layout: two-cols
---

### Class Template

```cpp
namespace SemiconductorHMI {

// 클래스 템플릿
template<typename T, size_t Capacity>
class RingBuffer {
private:
    std::array<T, Capacity> buffer;
    size_t read_index = 0;
    size_t write_index = 0;
    size_t count = 0;

public:
    bool Push(const T& item) {
        if (count >= Capacity) {
            return false;  // 버퍼 가득 찼음
        }

        buffer[write_index] = item;
        write_index = (write_index + 1) % Capacity;
        count++;
        return true;
    }

    bool Pop(T& item) {
        if (count == 0) {
            return false;  // 버퍼 비어있음
        }

        item = buffer[read_index];
        read_index = (read_index + 1) % Capacity;
        count--;
        return true;
    }

    size_t Size() const { return count; }
    bool IsEmpty() const { return count == 0; }
    bool IsFull() const { return count >= Capacity; }
};

}
```

::right::

## 클래스 템플릿 사용

**타입과 크기를 컴파일 타임에 결정**
```cpp
// 온도 센서 데이터 버퍼 (float, 100개)
RingBuffer<float, 100> temp_buffer;

// 알람 이벤트 버퍼 (string, 50개)
RingBuffer<std::string, 50> alarm_buffer;

// 센서 측정값 구조체 버퍼
struct SensorReading {
    float value;
    uint64_t timestamp;
};
RingBuffer<SensorReading, 1000> sensor_buffer;
```

**Non-Type Template Parameter**
- `size_t Capacity`는 값 템플릿 매개변수
- 컴파일 타임 상수여야 함
- 각 크기마다 별도 클래스 생성

**장점**
- 크기가 컴파일 타임에 결정되어 최적화
- 스택 할당 가능 (힙 할당 불필요)
- 타입 안전성

**실제 사용 패턴**
```cpp
void ProcessTemperatureData() {
    RingBuffer<float, 100> buffer;

    buffer.Push(25.3f);
    buffer.Push(26.1f);

    float temp;
    if (buffer.Pop(temp)) {
        // 온도 처리
    }
}
```

---
layout: two-cols
---

## 1.2 SFINAE (Substitution Failure Is Not An Error)

### std::enable_if를 통한 조건부 활성화

```cpp
namespace SemiconductorHMI {

// 정수 타입에만 동작하는 함수
template<typename T>
typename std::enable_if<std::is_integral<T>::value, T>::type
ProcessValue(T value) {
    return value * 2;
}

// 부동소수점 타입에만 동작하는 함수
template<typename T>
typename std::enable_if<std::is_floating_point<T>::value, T>::type
ProcessValue(T value) {
    return value * 1.5f;
}

// 사용 예시
void Example() {
    int i = ProcessValue(10);      // 20 (정수 버전)
    float f = ProcessValue(10.0f); // 15.0 (부동소수점 버전)

    // ProcessValue("hello"); // 컴파일 에러!
}

// 더 읽기 쉬운 C++17 버전
template<typename T>
std::enable_if_t<std::is_integral_v<T>, T>
ProcessValueModern(T value) {
    return value * 2;
}

}
```

::right::

## SFINAE 동작 원리

**Substitution Failure Is Not An Error**
- 템플릿 인자 치환 실패는 에러가 아님
- 해당 오버로드를 후보에서 제외
- 다른 오버로드 시도

**std::enable_if 구조**
```cpp
// 조건이 true면 type 멤버 정의
template<bool B, typename T = void>
struct enable_if {
    using type = T;
};

// 조건이 false면 type 멤버 없음
template<typename T>
struct enable_if<false, T> {};
```

**타입 특성 (Type Traits)**
```cpp
std::is_integral<int>::value      // true
std::is_integral<float>::value    // false
std::is_floating_point<double>::value // true
std::is_pointer<int*>::value      // true
std::is_const<const int>::value   // true
```

**실전 예시: 센서 데이터 직렬화**
```cpp
// POD 타입은 memcpy
template<typename T>
std::enable_if_t<std::is_trivially_copyable_v<T>, void>
Serialize(const T& data, std::vector<uint8_t>& buffer) {
    size_t old_size = buffer.size();
    buffer.resize(old_size + sizeof(T));
    std::memcpy(buffer.data() + old_size, &data, sizeof(T));
}

// 복잡한 타입은 직렬화 함수 호출
template<typename T>
std::enable_if_t<!std::is_trivially_copyable_v<T>, void>
Serialize(const T& data, std::vector<uint8_t>& buffer) {
    data.SerializeToBuffer(buffer);
}
```

---
layout: two-cols
---

## 1.3 C++20 Concepts

### Concepts로 제약 조건 명시

```cpp
namespace SemiconductorHMI {

// Concept 정의: Numeric 타입
template<typename T>
concept Numeric = std::is_arithmetic_v<T>;

// Concept 정의: Sensor 인터페이스
template<typename T>
concept Sensor = requires(T sensor) {
    { sensor.Read() } -> std::convertible_to<float>;
    { sensor.GetID() } -> std::convertible_to<int>;
    { sensor.IsOnline() } -> std::same_as<bool>;
};

// Concept 사용: 템플릿 매개변수 제약
template<Numeric T>
T Clamp(T value, T min, T max) {
    if (value < min) return min;
    if (value > max) return max;
    return value;
}

// Concept 사용: 센서 모니터링
template<Sensor S>
class SensorMonitor {
private:
    S& sensor;

public:
    explicit SensorMonitor(S& s) : sensor(s) {}

    void Update() {
        if (sensor.IsOnline()) {
            float value = sensor.Read();
            // 값 처리
        }
    }
};

}
```

::right::

## Concepts vs SFINAE

**SFINAE (C++17 이전)**
```cpp
// 복잡하고 읽기 어려움
template<typename T>
std::enable_if_t<std::is_arithmetic_v<T>, T>
Clamp(T value, T min, T max) {
    // ...
}
```

**Concepts (C++20)**
```cpp
// 간결하고 명확함
template<Numeric T>
T Clamp(T value, T min, T max) {
    // ...
}
```

**Concepts 장점**
- **가독성**: 의도가 명확히 드러남
- **에러 메시지**: 훨씬 읽기 쉬운 컴파일 에러
- **표현력**: 복잡한 제약 조건 표현 가능

**고급 Concept 예시**
```cpp
// Container와 Iterator 제약
template<typename T>
concept Container = requires(T container) {
    typename T::value_type;
    typename T::iterator;
    { container.begin() } -> std::same_as<typename T::iterator>;
    { container.end() } -> std::same_as<typename T::iterator>;
    { container.size() } -> std::convertible_to<size_t>;
};

// Callable 제약
template<typename F, typename... Args>
concept Callable = requires(F func, Args... args) {
    { func(args...) };
};
```

---
layout: two-cols
---

### 실전 예시: 제네릭 데이터 처리기

```cpp
namespace SemiconductorHMI {

// Concept: 측정 가능한 장비
template<typename T>
concept Measurable = requires(const T& equipment) {
    { equipment.GetValue() } -> std::convertible_to<double>;
    { equipment.GetUnit() } -> std::convertible_to<std::string_view>;
    { equipment.GetTimestamp() } -> std::convertible_to<uint64_t>;
};

// Concept: 제어 가능한 장비
template<typename T>
concept Controllable = requires(T& equipment, double value) {
    { equipment.SetValue(value) } -> std::same_as<bool>;
    { equipment.GetStatus() } -> std::convertible_to<std::string_view>;
};

// 측정 전용 장비 모니터
template<Measurable E>
class MeasurementMonitor {
private:
    E& equipment;
    std::vector<double> history;

public:
    explicit MeasurementMonitor(E& eq) : equipment(eq) {}

    void Update() {
        double value = equipment.GetValue();
        history.push_back(value);

        if (history.size() > 1000) {
            history.erase(history.begin());
        }
    }

    double GetAverage() const {
        return std::accumulate(history.begin(), history.end(), 0.0)
               / history.size();
    }
};

}
```

::right::

## 실전 활용 예시

**구체 클래스 구현**
```cpp
// 온도 센서 (측정만 가능)
class TemperatureSensor {
public:
    double GetValue() const { return temperature; }
    std::string_view GetUnit() const { return "°C"; }
    uint64_t GetTimestamp() const { return timestamp; }
private:
    double temperature = 25.0;
    uint64_t timestamp = 0;
};

// 히터 (측정 + 제어 가능)
class Heater {
public:
    double GetValue() const { return temperature; }
    std::string_view GetUnit() const { return "°C"; }
    uint64_t GetTimestamp() const { return timestamp; }

    bool SetValue(double temp) {
        target_temperature = temp;
        return true;
    }
    std::string_view GetStatus() const { return status; }
private:
    double temperature = 25.0;
    double target_temperature = 25.0;
    uint64_t timestamp = 0;
    std::string status = "OK";
};
```

**사용**
```cpp
TemperatureSensor temp_sensor;
Heater heater;

// 둘 다 Measurable이므로 모니터링 가능
MeasurementMonitor<TemperatureSensor> sensor_monitor(temp_sensor);
MeasurementMonitor<Heater> heater_monitor(heater);

sensor_monitor.Update();
heater_monitor.Update();
```

---
layout: center
---

# 🚀 **2. Performance Optimization**

## 성능 측정, 캐시 최적화, 벤치마킹

---
layout: two-cols
---

## 2.1 성능 측정 (Profiling)

### 고해상도 타이머

```cpp
namespace SemiconductorHMI::Profiling {

class ScopedTimer {
private:
    const char* name;
    std::chrono::high_resolution_clock::time_point start;

public:
    explicit ScopedTimer(const char* timer_name)
        : name(timer_name)
        , start(std::chrono::high_resolution_clock::now())
    {}

    ~ScopedTimer() {
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<
            std::chrono::microseconds>(end - start);

        printf("[%s] took %lld μs\n", name, duration.count());
    }
};

// 사용 예시
void ProcessSensorData(const std::vector<float>& data) {
    ScopedTimer timer("ProcessSensorData");

    // 데이터 처리 로직
    for (float value : data) {
        // ...
    }

    // 함수 종료시 자동으로 시간 출력
}

}
```

::right::

## 타이머 사용 패턴

**RAII 패턴으로 자동 측정**
```cpp
void RenderFrame() {
    ScopedTimer timer("RenderFrame");

    {
        ScopedTimer timer("UpdateLogic");
        UpdateGameLogic();
    }  // UpdateLogic 시간 출력

    {
        ScopedTimer timer("RenderScene");
        RenderScene();
    }  // RenderScene 시간 출력

    {
        ScopedTimer timer("RenderUI");
        RenderUI();
    }  // RenderUI 시간 출력
}  // RenderFrame 전체 시간 출력
```

**출력 예시**
```
[UpdateLogic] took 2341 μs
[RenderScene] took 8923 μs
[RenderUI] took 1245 μs
[RenderFrame] took 12567 μs
```

**고급 버전: 통계 수집**
```cpp
class PerformanceProfiler {
private:
    struct TimingData {
        uint64_t total_time_us = 0;
        uint64_t call_count = 0;
        uint64_t min_time_us = UINT64_MAX;
        uint64_t max_time_us = 0;
    };

    std::unordered_map<std::string, TimingData> timings;

public:
    void RecordTiming(const std::string& name, uint64_t time_us);
    void PrintReport() const;
};
```

---
layout: two-cols
---

## 2.2 캐시 친화적 코드

### 배열 구조체 (AoS) vs 구조체 배열 (SoA)

```cpp
namespace SemiconductorHMI {

// Array of Structures (AoS) - 캐시 비효율적
struct Particle_AoS {
    float x, y, z;        // 위치
    float vx, vy, vz;     // 속도
    float r, g, b, a;     // 색상
    float life;           // 수명
};

std::vector<Particle_AoS> particles_aos(10000);

void UpdatePositions_AoS() {
    for (auto& p : particles_aos) {
        // 위치만 업데이트하는데
        // 전체 64바이트를 캐시에 로드
        p.x += p.vx;
        p.y += p.vy;
        p.z += p.vz;
    }
}

// Structure of Arrays (SoA) - 캐시 효율적
struct ParticleSystem_SoA {
    std::vector<float> x, y, z;       // 위치
    std::vector<float> vx, vy, vz;    // 속도
    std::vector<float> r, g, b, a;    // 색상
    std::vector<float> life;          // 수명
};

ParticleSystem_SoA particles_soa;

void UpdatePositions_SoA() {
    for (size_t i = 0; i < particles_soa.x.size(); ++i) {
        // 필요한 데이터만 캐시에 로드
        particles_soa.x[i] += particles_soa.vx[i];
        particles_soa.y[i] += particles_soa.vy[i];
        particles_soa.z[i] += particles_soa.vz[i];
    }
}

}
```

::right::

## 메모리 레이아웃과 캐시

**AoS 메모리 레이아웃**
```
[x y z vx vy vz r g b a life] [x y z vx vy vz r g b a life] ...
 ←─────── 64 bytes ──────→     ←─────── 64 bytes ──────→
```
- 위치 업데이트시 불필요한 색상, 수명도 캐시에 로드
- 캐시 낭비 발생

**SoA 메모리 레이아웃**
```
x: [x x x x x x x x ...]
y: [y y y y y y y y ...]
z: [z z z z z z z z ...]
vx: [vx vx vx vx vx ...]
...
```
- 위치 업데이트시 위치 데이터만 캐시에 로드
- 캐시 효율 극대화

**성능 차이**
```cpp
// 10,000 파티클 벤치마크
AoS: 2.3ms
SoA: 0.8ms  (약 3배 빠름)
```

**선택 기준**
- **AoS**: 객체 단위 접근이 많을 때
- **SoA**: 특정 필드만 접근할 때 (렌더링, 물리 시뮬레이션)

**실전 팁**
```cpp
// 하이브리드 접근: 자주 같이 쓰는 것끼리 묶기
struct ParticleSystem_Hybrid {
    struct Position { float x, y, z; };
    struct Velocity { float vx, vy, vz; };

    std::vector<Position> positions;
    std::vector<Velocity> velocities;
    std::vector<float> life;  // 덜 자주 접근
};
```

---
layout: two-cols
---

### 메모리 정렬 (Alignment)

```cpp
namespace SemiconductorHMI {

// 잘못된 정렬: 19바이트이지만 24바이트 차지
struct BadAlignment {
    char a;      // 1 byte, 3 byte padding
    int b;       // 4 bytes
    char c;      // 1 byte, 7 byte padding
    double d;    // 8 bytes
};  // 총 24 bytes

// 올바른 정렬: 동일한 데이터를 16바이트로
struct GoodAlignment {
    double d;    // 8 bytes
    int b;       // 4 bytes
    char a;      // 1 byte
    char c;      // 1 byte
    // 2 byte padding
};  // 총 16 bytes

// SIMD를 위한 명시적 정렬
struct alignas(16) Vec4 {
    float x, y, z, w;

    // SSE를 통한 벡터 덧셈
    Vec4 operator+(const Vec4& other) const {
        Vec4 result;
        __m128 a = _mm_load_ps(&x);
        __m128 b = _mm_load_ps(&other.x);
        __m128 c = _mm_add_ps(a, b);
        _mm_store_ps(&result.x, c);
        return result;
    }
};

// 캐시 라인 정렬 (64바이트)
struct alignas(64) CacheLinePadded {
    std::atomic<int> counter;
    // 나머지 60바이트는 패딩
    // false sharing 방지
};

}
```

::right::

## 메모리 정렬의 중요성

**정렬되지 않은 접근의 문제**
```cpp
// 정렬되지 않은 포인터
char buffer[100];
int* unaligned_ptr = reinterpret_cast<int*>(buffer + 1);

// CPU에 따라:
// - 성능 저하 (추가 메모리 접근)
// - 크래시 (일부 아키텍처)
*unaligned_ptr = 42;  // 위험!
```

**정렬 요구사항**
```cpp
sizeof(char)   = 1, alignment = 1
sizeof(short)  = 2, alignment = 2
sizeof(int)    = 4, alignment = 4
sizeof(double) = 8, alignment = 8
sizeof(Vec4)   = 16, alignment = 16 (명시적)
```

**False Sharing 방지**
```cpp
// 나쁜 예: 두 스레드가 같은 캐시 라인 공유
struct BadCounter {
    std::atomic<int> counter1;  // 스레드 1 사용
    std::atomic<int> counter2;  // 스레드 2 사용
};  // 8바이트, 같은 캐시 라인에 위치

// 좋은 예: 각각 다른 캐시 라인
struct GoodCounter {
    alignas(64) std::atomic<int> counter1;
    alignas(64) std::atomic<int> counter2;
};  // 각각 64바이트 캐시 라인 차지
```

**실전 사용**
```cpp
// alignof로 정렬 확인
static_assert(alignof(Vec4) == 16);

// aligned_alloc으로 정렬된 메모리 할당
void* ptr = std::aligned_alloc(16, sizeof(Vec4) * 100);
```

---
layout: two-cols
---

## 2.3 벤치마킹

### 마이크로 벤치마크

```cpp
namespace SemiconductorHMI::Benchmark {

template<typename Func>
auto MeasureTime(Func func, size_t iterations = 1000) {
    auto start = std::chrono::high_resolution_clock::now();

    for (size_t i = 0; i < iterations; ++i) {
        func();
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<
        std::chrono::microseconds>(end - start);

    return duration.count() / static_cast<double>(iterations);
}

// 사용 예시
void BenchmarkDataStructures() {
    const size_t N = 10000;
    std::vector<int> vec;
    std::list<int> list;

    // 벡터 벤치마크
    auto vec_time = MeasureTime([&]() {
        vec.clear();
        for (size_t i = 0; i < N; ++i) {
            vec.push_back(i);
        }
    });

    // 리스트 벤치마크
    auto list_time = MeasureTime([&]() {
        list.clear();
        for (size_t i = 0; i < N; ++i) {
            list.push_back(i);
        }
    });

    printf("Vector: %.2f μs\n", vec_time);
    printf("List: %.2f μs\n", list_time);
}

}
```

::right::

## 벤치마킹 주의사항

**컴파일러 최적화 방지**
```cpp
// 나쁜 예: 컴파일러가 최적화로 제거할 수 있음
void BadBenchmark() {
    auto time = MeasureTime([]() {
        int sum = 0;
        for (int i = 0; i < 1000; ++i) {
            sum += i;
        }
        // sum을 사용하지 않으면 전체 루프 제거될 수 있음
    });
}

// 좋은 예: DoNotOptimize로 최적화 방지
void GoodBenchmark() {
    int result = 0;
    auto time = MeasureTime([&]() {
        int sum = 0;
        for (int i = 0; i < 1000; ++i) {
            sum += i;
        }
        result = sum;
    });

    // result를 강제로 사용
    volatile int sink = result;
    (void)sink;
}
```

**워밍업 (Warm-up)**
```cpp
// 첫 실행은 캐시 미스 등으로 느릴 수 있음
template<typename Func>
auto MeasureTimeWithWarmup(Func func, size_t iterations = 1000) {
    // 워밍업
    for (size_t i = 0; i < 10; ++i) {
        func();
    }

    // 실제 측정
    return MeasureTime(func, iterations);
}
```

**통계적 분석**
```cpp
std::vector<double> RunMultipleTimes(auto func, size_t runs = 100) {
    std::vector<double> times;
    for (size_t i = 0; i < runs; ++i) {
        times.push_back(MeasureTime(func));
    }
    return times;
}

double GetMedian(std::vector<double> times) {
    std::sort(times.begin(), times.end());
    return times[times.size() / 2];
}
```

---
layout: center
---

# 💾 **3. Advanced Memory Management**

## Custom Allocators, Memory Pools, Arena Allocation

---
layout: two-cols
---

## 3.1 메모리 풀 (Memory Pool)

### 고정 크기 메모리 풀

```cpp
namespace SemiconductorHMI {

template<size_t BlockSize, size_t BlockCount>
class MemoryPool {
private:
    std::array<std::byte, BlockSize * BlockCount> memory;
    std::array<bool, BlockCount> used;
    size_t next_free = 0;

public:
    MemoryPool() {
        used.fill(false);
    }

    void* Allocate(size_t size) {
        if (size > BlockSize) return nullptr;

        // 다음 빈 블록 검색
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

        return nullptr;  // 풀이 가득 참
    }

    void Deallocate(void* ptr) {
        if (!ptr) return;

        auto* byte_ptr = static_cast<std::byte*>(ptr);
        if (byte_ptr < memory.data() ||
            byte_ptr >= memory.data() + memory.size()) {
            return;  // 이 풀에 속하지 않는 포인터
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

}
```

::right::

## 메모리 풀 장점

**성능 이점**
- **빠른 할당/해제**: O(1) 시간 복잡도
- **단편화 없음**: 고정 크기 블록
- **캐시 친화적**: 연속된 메모리

**사용 시나리오**
```cpp
// 파티클 시스템용 풀
MemoryPool<sizeof(Particle), 10000> particle_pool;

void SpawnParticle() {
    void* mem = particle_pool.Allocate(sizeof(Particle));
    if (mem) {
        Particle* p = new(mem) Particle();  // placement new
        // 파티클 사용
    }
}

void DestroyParticle(Particle* p) {
    p->~Particle();  // 소멸자 명시적 호출
    particle_pool.Deallocate(p);
}
```

**성능 비교**
```cpp
// 일반 할당 (new/delete)
Benchmark: 1000회 할당/해제
Time: 450 μs

// 메모리 풀
Benchmark: 1000회 할당/해제
Time: 85 μs  (약 5배 빠름)
```

**주의사항**
- 블록 크기가 고정되어 있음
- 전체 메모리를 미리 확보
- 스레드 안전성 없음 (필요시 락 추가)

**개선: 스레드 안전 버전**
```cpp
template<size_t BlockSize, size_t BlockCount>
class ThreadSafeMemoryPool {
private:
    MemoryPool<BlockSize, BlockCount> pool;
    std::mutex mutex;

public:
    void* Allocate(size_t size) {
        std::lock_guard lock(mutex);
        return pool.Allocate(size);
    }

    void Deallocate(void* ptr) {
        std::lock_guard lock(mutex);
        pool.Deallocate(ptr);
    }
};
```

---
layout: two-cols
---

## 3.2 아레나 할당자 (Arena Allocator)

### Linear Allocator

```cpp
namespace SemiconductorHMI {

class ArenaAllocator {
private:
    std::unique_ptr<std::byte[]> memory;
    size_t capacity;
    size_t offset = 0;

public:
    explicit ArenaAllocator(size_t size)
        : memory(std::make_unique<std::byte[]>(size))
        , capacity(size)
    {}

    void* Allocate(size_t size, size_t alignment = alignof(std::max_align_t)) {
        // 정렬 계산
        size_t padding = 0;
        size_t current = reinterpret_cast<uintptr_t>(memory.get() + offset);
        size_t aligned = (current + alignment - 1) & ~(alignment - 1);
        padding = aligned - current;

        // 공간 확인
        if (offset + padding + size > capacity) {
            return nullptr;  // 메모리 부족
        }

        void* ptr = memory.get() + offset + padding;
        offset += padding + size;
        return ptr;
    }

    // 개별 해제 불가 (전체 리셋만 가능)
    void Reset() {
        offset = 0;
    }

    size_t GetUsedMemory() const { return offset; }
    size_t GetCapacity() const { return capacity; }
    float GetUsageRatio() const {
        return static_cast<float>(offset) / capacity;
    }
};

}
```

::right::

## 아레나 할당자 사용 패턴

**프레임 단위 할당**
```cpp
class FrameAllocator {
private:
    ArenaAllocator allocator;

public:
    FrameAllocator() : allocator(10 * 1024 * 1024) {}  // 10MB

    void BeginFrame() {
        allocator.Reset();  // 이전 프레임 메모리 재사용
    }

    void* Allocate(size_t size) {
        return allocator.Allocate(size);
    }

    // EndFrame에서 자동으로 리셋
    void EndFrame() {
        // 통계 수집
        printf("Frame memory used: %.2f MB\n",
               allocator.GetUsedMemory() / (1024.0f * 1024.0f));
    }
};

// 사용
FrameAllocator frame_alloc;

void RenderFrame() {
    frame_alloc.BeginFrame();

    // 임시 데이터 할당
    void* temp = frame_alloc.Allocate(1024);
    // 사용...

    // 개별 해제 불필요!

    frame_alloc.EndFrame();  // 모든 메모리 자동 재사용
}
```

**장점**
- **매우 빠름**: 포인터 증가만으로 할당
- **간단함**: 개별 해제 추적 불필요
- **단편화 없음**: 순차 할당

**단점**
- 개별 해제 불가
- 메모리 재사용 제한적
- 수명 관리 필요

**실전 활용**
```cpp
// 문자열 파싱용 임시 버퍼
ArenaAllocator parser_arena(1024 * 1024);

std::vector<std::string_view> ParseCSV(std::string_view csv) {
    parser_arena.Reset();
    std::vector<std::string_view> result;

    // csv 파싱하면서 임시 메모리 할당
    // ...

    return result;
    // 함수 끝나면 arena는 그대로, 다음 호출시 Reset
}
```

---
layout: two-cols
---

## 3.3 Custom Allocator for STL

### STL 컨테이너용 커스텀 할당자

```cpp
namespace SemiconductorHMI {

template<typename T>
class PoolAllocator {
private:
    static constexpr size_t POOL_SIZE = 10000;
    static MemoryPool<sizeof(T), POOL_SIZE> pool;

public:
    using value_type = T;

    PoolAllocator() noexcept = default;

    template<typename U>
    PoolAllocator(const PoolAllocator<U>&) noexcept {}

    T* allocate(size_t n) {
        if (n == 1) {
            return static_cast<T*>(pool.Allocate(sizeof(T)));
        }
        // 여러 개는 일반 할당
        return static_cast<T*>(::operator new(n * sizeof(T)));
    }

    void deallocate(T* ptr, size_t n) noexcept {
        if (n == 1) {
            pool.Deallocate(ptr);
        } else {
            ::operator delete(ptr);
        }
    }

    template<typename U>
    struct rebind {
        using other = PoolAllocator<U>;
    };
};

// 정적 멤버 정의
template<typename T>
MemoryPool<sizeof(T), PoolAllocator<T>::POOL_SIZE>
PoolAllocator<T>::pool;

}
```

::right::

## STL 컨테이너에 적용

**사용 예시**
```cpp
// 일반 vector
std::vector<Particle> normal_particles;

// 풀 할당자 사용 vector
std::vector<Particle, PoolAllocator<Particle>>
    pool_particles;

// 성능 비교
void BenchmarkVectors() {
    const size_t N = 10000;

    auto normal_time = MeasureTime([&]() {
        std::vector<Particle> vec;
        for (size_t i = 0; i < N; ++i) {
            vec.emplace_back();
        }
    });

    auto pool_time = MeasureTime([&]() {
        std::vector<Particle, PoolAllocator<Particle>> vec;
        for (size_t i = 0; i < N; ++i) {
            vec.emplace_back();
        }
    });

    printf("Normal: %.2f μs\n", normal_time);
    printf("Pool: %.2f μs\n", pool_time);
}
```

**다른 컨테이너에도 적용**
```cpp
// list with pool allocator
std::list<Sensor, PoolAllocator<Sensor>> sensor_list;

// map with pool allocator
std::map<int, Equipment,
         std::less<int>,
         PoolAllocator<std::pair<const int, Equipment>>>
    equipment_map;

// unordered_map with pool allocator
std::unordered_map<std::string, float,
                   std::hash<std::string>,
                   std::equal_to<std::string>,
                   PoolAllocator<std::pair<const std::string, float>>>
    sensor_values;
```

---
layout: center
---

# 🎯 **4. C++20 Modern Features**

## Ranges, Coroutines, Modules

---
layout: two-cols
---

## 4.1 Ranges

### ranges로 간결한 데이터 처리

```cpp
#include <ranges>
#include <vector>
#include <algorithm>

namespace SemiconductorHMI {

struct Sensor {
    int id;
    float temperature;
    bool online;
};

void ProcessSensors(const std::vector<Sensor>& sensors) {
    namespace views = std::ranges::views;

    // C++17 방식 (복잡함)
    std::vector<float> temps_old;
    for (const auto& sensor : sensors) {
        if (sensor.online && sensor.temperature > 25.0f) {
            temps_old.push_back(sensor.temperature);
        }
    }
    std::sort(temps_old.begin(), temps_old.end());

    // C++20 Ranges (간결함)
    auto temps = sensors
        | views::filter([](const Sensor& s) {
            return s.online && s.temperature > 25.0f;
          })
        | views::transform([](const Sensor& s) {
            return s.temperature;
          });

    std::vector<float> sorted_temps(temps.begin(), temps.end());
    std::ranges::sort(sorted_temps);

    // 더 간결한 버전 (lazy evaluation)
    for (float temp : sensors
                      | views::filter([](auto& s) { return s.online; })
                      | views::transform([](auto& s) { return s.temperature; })
                      | views::take(10)) {  // 상위 10개만
        printf("%.1f\n", temp);
    }
}

}
```

::right::

## Ranges의 장점

**Lazy Evaluation**
```cpp
// 필요할 때만 계산됨
auto view = sensors
    | views::filter([](auto& s) { return s.online; })
    | views::transform([](auto& s) { return s.temperature; });

// 여기까지 아무것도 실행 안됨

for (float temp : view | views::take(5)) {
    // 여기서 처음 5개만 계산됨
}
```

**Composition (조합)**
```cpp
// 여러 변환을 파이프로 연결
auto pipeline = views::filter([](auto& s) { return s.online; })
              | views::transform([](auto& s) { return s.temperature; })
              | views::filter([](float t) { return t > 25.0f; })
              | views::transform([](float t) { return t * 1.8f + 32.0f; });  // 화씨 변환

auto fahrenheit_temps = sensors | pipeline;
```

**메모리 효율**
```cpp
// 중간 컨테이너 생성 없음
std::vector<Sensor> sensors(1000000);

// C++17: 3개의 임시 vector 생성
auto result_old = [&]() {
    std::vector<Sensor> filtered;
    std::copy_if(sensors.begin(), sensors.end(),
                 std::back_inserter(filtered),
                 [](auto& s) { return s.online; });

    std::vector<float> temps;
    std::transform(filtered.begin(), filtered.end(),
                   std::back_inserter(temps),
                   [](auto& s) { return s.temperature; });
    return temps;
}();

// C++20: 임시 컨테이너 없음, view만 생성
auto result_new = sensors
    | views::filter([](auto& s) { return s.online; })
    | views::transform([](auto& s) { return s.temperature; });
```

---
layout: two-cols
---

### Ranges 고급 기능

```cpp
namespace SemiconductorHMI {

void AdvancedRangesExample() {
    namespace views = std::ranges::views;

    std::vector<int> nums = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    // take, drop
    auto first_five = nums | views::take(5);
    // [1, 2, 3, 4, 5]

    auto skip_five = nums | views::drop(5);
    // [6, 7, 8, 9, 10]

    // split
    std::string csv = "sensor1,25.3,sensor2,26.1,sensor3,24.8";
    auto tokens = csv | views::split(',');
    // ["sensor1", "25.3", "sensor2", "26.1", "sensor3", "24.8"]

    // join
    std::vector<std::vector<int>> nested = {{1,2}, {3,4}, {5,6}};
    auto flattened = nested | views::join;
    // [1, 2, 3, 4, 5, 6]

    // zip (C++23)
    std::vector<std::string> names = {"Sensor1", "Sensor2", "Sensor3"};
    std::vector<float> temps = {25.3f, 26.1f, 24.8f};

    for (auto [name, temp] : views::zip(names, temps)) {
        printf("%s: %.1f°C\n", name.c_str(), temp);
    }

    // chunk
    auto chunks = nums | views::chunk(3);
    // [[1,2,3], [4,5,6], [7,8,9], [10]]

    for (auto chunk : chunks) {
        printf("[");
        for (int n : chunk) printf("%d ", n);
        printf("]\n");
    }
}

}
```

::right::

## 실전 활용 예시

**센서 데이터 필터링 파이프라인**
```cpp
struct SensorReading {
    int sensor_id;
    float value;
    uint64_t timestamp;
    bool valid;
};

class SensorDataProcessor {
public:
    auto GetValidHighTemperatures(
        const std::vector<SensorReading>& readings,
        float threshold)
    {
        namespace views = std::ranges::views;

        return readings
            | views::filter([](const auto& r) { return r.valid; })
            | views::filter([threshold](const auto& r) {
                return r.value > threshold;
              })
            | views::transform([](const auto& r) {
                return std::make_pair(r.sensor_id, r.value);
              });
    }

    // 사용
    void Example(const std::vector<SensorReading>& readings) {
        for (auto [id, temp] : GetValidHighTemperatures(readings, 80.0f)) {
            printf("Sensor %d: %.1f°C (HIGH!)\n", id, temp);
        }
    }
};
```

**통계 계산**
```cpp
float CalculateAverage(const std::vector<SensorReading>& readings) {
    namespace views = std::ranges::views;

    auto valid_values = readings
        | views::filter([](auto& r) { return r.valid; })
        | views::transform([](auto& r) { return r.value; });

    float sum = 0.0f;
    size_t count = 0;
    for (float v : valid_values) {
        sum += v;
        count++;
    }

    return count > 0 ? sum / count : 0.0f;
}
```

---
layout: two-cols
---

## 4.2 Coroutines (코루틴)

### 비동기 작업을 동기적으로 작성

```cpp
#include <coroutine>
#include <optional>

namespace SemiconductorHMI {

// Generator 코루틴
template<typename T>
struct Generator {
    struct promise_type {
        T current_value;

        Generator get_return_object() {
            return Generator{
                std::coroutine_handle<promise_type>::from_promise(*this)
            };
        }

        std::suspend_always initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }

        std::suspend_always yield_value(T value) {
            current_value = value;
            return {};
        }

        void return_void() {}
        void unhandled_exception() { std::terminate(); }
    };

    std::coroutine_handle<promise_type> handle;

    Generator(std::coroutine_handle<promise_type> h) : handle(h) {}
    ~Generator() { if (handle) handle.destroy(); }

    bool next() {
        handle.resume();
        return !handle.done();
    }

    T value() const {
        return handle.promise().current_value;
    }
};

}
```

::right::

## Generator 사용

**순차 데이터 생성**
```cpp
Generator<int> CountUp(int start, int end) {
    for (int i = start; i <= end; ++i) {
        co_yield i;  // 값을 반환하고 일시 중지
    }
}

// 사용
void Example() {
    auto gen = CountUp(1, 5);

    while (gen.next()) {
        printf("%d\n", gen.value());
    }
    // 출력: 1 2 3 4 5
}
```

**센서 데이터 스트림**
```cpp
Generator<SensorReading> ReadSensorStream(int sensor_id) {
    while (true) {
        // 센서에서 데이터 읽기
        float value = ReadFromHardware(sensor_id);
        uint64_t timestamp = GetCurrentTime();

        co_yield SensorReading{
            sensor_id,
            value,
            timestamp,
            true
        };

        // 100ms 대기 (다음 읽기까지)
        std::this_thread::sleep_for(
            std::chrono::milliseconds(100)
        );
    }
}

// 사용
void MonitorSensor() {
    auto stream = ReadSensorStream(1);

    for (int i = 0; i < 10; ++i) {
        if (stream.next()) {
            auto reading = stream.value();
            printf("Sensor %d: %.2f at %llu\n",
                   reading.sensor_id,
                   reading.value,
                   reading.timestamp);
        }
    }
}
```

---
layout: two-cols
---

### Task 코루틴 (비동기 작업)

```cpp
namespace SemiconductorHMI {

template<typename T>
struct Task {
    struct promise_type {
        T value;
        std::exception_ptr exception;

        Task get_return_object() {
            return Task{
                std::coroutine_handle<promise_type>::from_promise(*this)
            };
        }

        std::suspend_never initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }

        void return_value(T v) { value = v; }
        void unhandled_exception() {
            exception = std::current_exception();
        }
    };

    std::coroutine_handle<promise_type> handle;

    Task(std::coroutine_handle<promise_type> h) : handle(h) {}
    ~Task() { if (handle) handle.destroy(); }

    T get() {
        if (!handle.done()) {
            handle.resume();
        }
        if (handle.promise().exception) {
            std::rethrow_exception(handle.promise().exception);
        }
        return handle.promise().value;
    }
};

// 비동기 센서 읽기
Task<float> ReadSensorAsync(int sensor_id) {
    // 하드웨어에서 읽기 (시뮬레이션)
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    float value = static_cast<float>(sensor_id) * 10.5f;
    co_return value;
}

}
```

::right::

## 비동기 작업 체이닝

**여러 비동기 작업 순차 실행**
```cpp
Task<std::vector<float>> ReadMultipleSensorsAsync() {
    std::vector<float> results;

    // 여러 센서를 순차적으로 읽기
    // (코루틴 덕분에 동기 코드처럼 작성)
    for (int i = 1; i <= 5; ++i) {
        float value = co_await ReadSensorAsync(i);
        results.push_back(value);
    }

    co_return results;
}

// 사용
void Example() {
    auto task = ReadMultipleSensorsAsync();
    auto results = task.get();

    for (float value : results) {
        printf("%.1f\n", value);
    }
}
```

**에러 처리**
```cpp
Task<float> SafeReadSensorAsync(int sensor_id) {
    try {
        float value = co_await ReadSensorAsync(sensor_id);

        if (value < 0 || value > 100) {
            throw std::runtime_error("Out of range");
        }

        co_return value;
    } catch (const std::exception& e) {
        printf("Error: %s\n", e.what());
        co_return 0.0f;  // 기본값 반환
    }
}
```

**코루틴의 장점**
- 비동기 코드를 동기식으로 작성
- 콜백 지옥 (callback hell) 회피
- 가독성 향상
- 예외 처리 간편

---
layout: two-cols
---

## 4.3 Modules (C++20)

### 모듈 기본 구조

```cpp
// sensor_module.ixx (모듈 인터페이스)
export module sensor;

import <vector>;
import <string>;

// export: 외부에 공개
export namespace SemiconductorHMI {

class Sensor {
public:
    Sensor(int id, std::string name);

    float Read() const;
    void Calibrate();

private:
    int id_;
    std::string name_;
    float value_ = 0.0f;
};

// 템플릿도 export 가능
export template<typename T>
T Clamp(T value, T min, T max) {
    if (value < min) return min;
    if (value > max) return max;
    return value;
}

}  // namespace SemiconductorHMI

// 내부 구현 (export 안됨)
namespace {

float ReadFromHardware(int sensor_id) {
    // 하드웨어 접근 (외부에서 호출 불가)
    return static_cast<float>(sensor_id) * 10.5f;
}

}  // anonymous namespace
```

::right::

## 모듈 사용

**모듈 임포트**
```cpp
// main.cpp
import sensor;  // 모듈 임포트
import <iostream>;

int main() {
    SemiconductorHMI::Sensor temp_sensor(1, "Temperature");

    float value = temp_sensor.Read();
    std::cout << "Temperature: " << value << "\n";

    // Clamp 템플릿 사용
    float clamped = SemiconductorHMI::Clamp(value, 20.0f, 80.0f);
    std::cout << "Clamped: " << clamped << "\n";

    return 0;
}
```

**모듈 vs 헤더**

| 특징 | 헤더 (#include) | 모듈 (import) |
|------|----------------|---------------|
| 컴파일 속도 | 느림 (매번 파싱) | 빠름 (한 번만 컴파일) |
| 전처리기 | 영향 받음 | 격리됨 |
| 매크로 | 누출됨 | 누출 안됨 |
| 순서 의존성 | 있음 | 없음 |
| ODR 위반 | 발생 가능 | 방지됨 |

**실제 컴파일 시간 비교**
```bash
# 헤더 방식
g++ main.cpp -o main
Time: 8.5s

# 모듈 방식
g++ -std=c++20 -fmodules-ts main.cpp -o main
Time: 2.1s  (약 4배 빠름, 두 번째 컴파일부터)
```

**모듈 파티션**
```cpp
// sensor.ixx
export module sensor;

export import :temperature;  // 서브 모듈
export import :pressure;

// sensor_temperature.ixx
export module sensor:temperature;

export class TemperatureSensor { /*...*/ };
```

---
layout: two-cols
---

### 모듈 실전 활용

```cpp
// equipment_system.ixx
export module equipment_system;

import <memory>;
import <vector>;
import <string>;
import <unordered_map>;

export namespace SemiconductorHMI {

// Equipment 인터페이스
export class IEquipment {
public:
    virtual ~IEquipment() = default;
    virtual float GetValue() const = 0;
    virtual void SetValue(float value) = 0;
    virtual std::string GetStatus() const = 0;
};

// Equipment Manager
export class EquipmentManager {
private:
    std::unordered_map<int, std::unique_ptr<IEquipment>> equipment_map;

public:
    void RegisterEquipment(int id, std::unique_ptr<IEquipment> equipment) {
        equipment_map[id] = std::move(equipment);
    }

    IEquipment* GetEquipment(int id) {
        auto it = equipment_map.find(id);
        return it != equipment_map.end() ? it->second.get() : nullptr;
    }

    std::vector<int> GetAllEquipmentIDs() const {
        std::vector<int> ids;
        for (const auto& [id, _] : equipment_map) {
            ids.push_back(id);
        }
        return ids;
    }

    size_t GetCount() const {
        return equipment_map.size();
    }
};

// 팩토리 함수
export std::unique_ptr<IEquipment> CreateTemperatureSensor(int id);
export std::unique_ptr<IEquipment> CreatePressureSensor(int id);

}  // namespace SemiconductorHMI
```

::right::

## 모듈 구현부

**구현 파일**
```cpp
// equipment_system.cpp
module equipment_system;

import <sstream>;

namespace SemiconductorHMI {

// 내부 구현 클래스 (export 안됨)
class TemperatureSensor : public IEquipment {
private:
    int id_;
    float temperature_ = 25.0f;

public:
    explicit TemperatureSensor(int id) : id_(id) {}

    float GetValue() const override {
        return temperature_;
    }

    void SetValue(float value) override {
        temperature_ = value;
    }

    std::string GetStatus() const override {
        std::ostringstream oss;
        oss << "Sensor " << id_ << ": " << temperature_ << "°C";
        return oss.str();
    }
};

// 팩토리 구현
std::unique_ptr<IEquipment> CreateTemperatureSensor(int id) {
    return std::make_unique<TemperatureSensor>(id);
}

}  // namespace SemiconductorHMI
```

**사용 예시**
```cpp
// application.cpp
import equipment_system;
import <iostream>;

int main() {
    using namespace SemiconductorHMI;

    EquipmentManager manager;

    manager.RegisterEquipment(1, CreateTemperatureSensor(1));
    manager.RegisterEquipment(2, CreateTemperatureSensor(2));

    auto* sensor = manager.GetEquipment(1);
    if (sensor) {
        sensor->SetValue(28.5f);
        std::cout << sensor->GetStatus() << "\n";
    }

    return 0;
}
```

---
layout: center
---

# 🎓 **Summary**

## C++ Advanced Patterns 요약

---

# 핵심 내용 정리

## 1. Template Metaprogramming

- **템플릿 기초**: 컴파일 타임 코드 생성, 타입 안전성
- **SFINAE**: `std::enable_if`로 조건부 템플릿 활성화
- **C++20 Concepts**: 템플릿 제약 조건을 명확하게 표현
  - 가독성 향상, 에러 메시지 개선

## 2. Performance Optimization

- **성능 측정**: `ScopedTimer`로 프로파일링
- **캐시 최적화**:
  - SoA (Structure of Arrays) vs AoS (Array of Structures)
  - 메모리 정렬 (alignment)으로 SIMD 최적화
- **벤치마킹**: 정확한 성능 측정 기법

## 3. Advanced Memory Management

- **메모리 풀**: 고정 크기 블록으로 빠른 할당/해제
- **아레나 할당자**: 프레임 단위 일괄 할당/해제
- **STL 커스텀 할당자**: 컨테이너 성능 최적화

## 4. C++20 Modern Features

- **Ranges**: 파이프라인 스타일 데이터 처리, Lazy evaluation
- **Coroutines**: 비동기 코드를 동기식으로 작성
- **Modules**: 컴파일 속도 개선, 격리된 네임스페이스

---

# 실전 활용 가이드

## 언제 어떤 기법을 사용할까?

### Template Metaprogramming
- ✅ **사용**: 타입 안전한 제네릭 코드, 컴파일 타임 최적화
- ❌ **주의**: 과도한 템플릿은 컴파일 시간 증가

### Performance Optimization
- ✅ **측정 먼저**: 프로파일링 없이 최적화하지 말 것
- ✅ **핫스팟 집중**: 가장 많이 호출되는 코드 우선 최적화
- ✅ **SoA**: 대량의 동일 타입 객체 처리시 (파티클, 센서 배열)

### Memory Management
- ✅ **메모리 풀**: 잦은 할당/해제 (파티클, 이벤트)
- ✅ **아레나**: 프레임 단위 임시 데이터 (렌더링, 파싱)
- ⚠️ **오버엔지니어링 주의**: 대부분은 기본 `new`/`delete`로 충분

### Modern Features
- ✅ **Ranges**: 데이터 필터링/변환 파이프라인
- ✅ **Coroutines**: 비동기 I/O, 제너레이터 패턴
- ✅ **Modules**: 새 프로젝트 (기존 프로젝트는 마이그레이션 비용 고려)

## 반도체 HMI에서의 적용

| 기능 | 추천 기법 |
|------|----------|
| 센서 데이터 스트림 | Coroutines (Generator) |
| 대량 센서 처리 | SoA + Ranges |
| 실시간 렌더링 | 메모리 풀 + 아레나 |
| 플러그인 시스템 | Concepts + Modules |

---
layout: end
---

# Week 11 완료

## 다음 주: ImGUI Advanced Integration

**학습 목표 달성**:
- ✅ Template Metaprogramming 이해
- ✅ 성능 최적화 기법 습득
- ✅ 고급 메모리 관리 패턴
- ✅ C++20 모던 기능 활용

**실전 프로젝트에 적용하세요!**
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

