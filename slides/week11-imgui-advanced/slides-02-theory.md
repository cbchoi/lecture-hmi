
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
