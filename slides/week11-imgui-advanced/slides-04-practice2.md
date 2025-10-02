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
