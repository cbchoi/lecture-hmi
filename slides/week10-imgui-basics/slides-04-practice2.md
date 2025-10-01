private:
    void DrawTicks(ImDrawList* draw_list, const ImVec2& center) {
        const int tick_count = 11;
        const float tick_length = 8.0f;
        const float angle_range = 1.5f * IM_PI;
        const float start_angle = 0.75f * IM_PI;

        for (int i = 0; i < tick_count; ++i) {
            float angle = start_angle + (angle_range / (tick_count - 1)) * i;

            ImVec2 tick_start = ImVec2(
                center.x + std::cos(angle) * (radius + 5),
                center.y + std::sin(angle) * (radius + 5)
            );
            ImVec2 tick_end = ImVec2(
                center.x + std::cos(angle) * (radius + 5 + tick_length),
                center.y + std::sin(angle) * (radius + 5 + tick_length)
            );

            draw_list->AddLine(tick_start, tick_end, IM_COL32(200, 200, 200, 255), 2.0f);

            // 숫자 표시
            if (i % 2 == 0) {
                float value = min_value + (max_value - min_value) * i / (tick_count - 1);
                ImVec2 text_pos = ImVec2(
                    center.x + std::cos(angle) * (radius + 20) - 10,
                    center.y + std::sin(angle) * (radius + 20) - 8
                );

                char text[16];
                snprintf(text, sizeof(text), "%.0f", value);
                draw_list->AddText(text_pos, IM_COL32(200, 200, 200, 255), text);
            }
        }
    }

    void DrawText(const ImVec2& center) {
        // 현재 값 표시
        char value_text[32];
        snprintf(value_text, sizeof(value_text), "%.1f", current_value);

        ImVec2 text_size = ImGui::CalcTextSize(value_text);
        ImVec2 text_pos = ImVec2(center.x - text_size.x/2, center.y - text_size.y/2);

        ImGui::SetCursorScreenPos(text_pos);
        ImGui::Text("%s", value_text);

        // 라벨 표시
        text_size = ImGui::CalcTextSize(label.c_str());
        text_pos = ImVec2(center.x - text_size.x/2, center.y + 15);

        ImGui::SetCursorScreenPos(text_pos);
        ImGui::Text("%s", label.c_str());
    }
};

} // namespace SemiconductorHMI::UI
```

#### 4.2 히트맵 시각화 위젯
```cpp
// include/ui_components/heatmap.h
#pragma once

#include <imgui.h>
#include <vector>
#include <algorithm>
#include <cmath>

namespace SemiconductorHMI::UI {

class Heatmap {
private:
    std::string title;
    std::vector<std::vector<float>> data;
    int width, height;
    float min_value, max_value;
    bool auto_scale;
    std::vector<ImVec4> color_map;

public:
    Heatmap(const std::string& heatmap_title, int w, int h)
        : title(heatmap_title)
        , width(w)
        , height(h)
        , min_value(0.0f)
        , max_value(1.0f)
        , auto_scale(true) {

        data.resize(height, std::vector<float>(width, 0.0f));
        InitializeColorMap();
    }

    void SetData(const std::vector<std::vector<float>>& new_data) {
        if (new_data.size() == height && new_data[0].size() == width) {
            data = new_data;

            if (auto_scale) {
                UpdateScale();
            }
        }
    }

    void SetValue(int x, int y, float value) {
        if (x >= 0 && x < width && y >= 0 && y < height) {
            data[y][x] = value;

            if (auto_scale) {
                UpdateScale();
            }
        }
    }

    void SetRange(float min_val, float max_val) {
        min_value = min_val;
        max_value = max_val;
        auto_scale = false;
    }

    void Render(const ImVec2& size = ImVec2(0, 0)) {
        if (ImGui::BeginChild(title.c_str(), size, true)) {
            ImDrawList* draw_list = ImGui::GetWindowDrawList();
            ImVec2 canvas_pos = ImGui::GetCursorScreenPos();
            ImVec2 canvas_size = ImGui::GetContentRegionAvail();

            if (canvas_size.x < 100.0f) canvas_size.x = 100.0f;
            if (canvas_size.y < 100.0f) canvas_size.y = 100.0f;

            // 셀 크기 계산
            float cell_width = canvas_size.x / width;
            float cell_height = canvas_size.y / height;

            // 히트맵 렌더링
            for (int y = 0; y < height; ++y) {
                for (int x = 0; x < width; ++x) {
                    float normalized_value = (data[y][x] - min_value) / (max_value - min_value);
                    normalized_value = std::clamp(normalized_value, 0.0f, 1.0f);

                    ImVec4 color = GetColorFromValue(normalized_value);
                    ImU32 color_u32 = ImGui::ColorConvertFloat4ToU32(color);

                    ImVec2 cell_min = ImVec2(
                        canvas_pos.x + x * cell_width,
                        canvas_pos.y + y * cell_height
                    );
                    ImVec2 cell_max = ImVec2(
                        cell_min.x + cell_width,
                        cell_min.y + cell_height
                    );

                    draw_list->AddRectFilled(cell_min, cell_max, color_u32);

                    // 테두리 그리기 (선택적)
                    draw_list->AddRect(cell_min, cell_max, IM_COL32(50, 50, 50, 255));
                }
            }

            // 컬러바 렌더링
            RenderColorBar(draw_list, canvas_pos, canvas_size);

            ImGui::SetCursorScreenPos(ImVec2(canvas_pos.x, canvas_pos.y + canvas_size.y));
        }
        ImGui::EndChild();
    }

private:
    void InitializeColorMap() {
        // 파란색에서 빨간색으로 그라데이션
        color_map = {
            ImVec4(0.0f, 0.0f, 1.0f, 1.0f),  // Blue
            ImVec4(0.0f, 1.0f, 1.0f, 1.0f),  // Cyan
            ImVec4(0.0f, 1.0f, 0.0f, 1.0f),  // Green
            ImVec4(1.0f, 1.0f, 0.0f, 1.0f),  // Yellow
            ImVec4(1.0f, 0.5f, 0.0f, 1.0f),  // Orange
            ImVec4(1.0f, 0.0f, 0.0f, 1.0f)   // Red
        };
    }

    ImVec4 GetColorFromValue(float normalized_value) {
        if (color_map.empty()) return ImVec4(0, 0, 0, 1);

        float scaled_value = normalized_value * (color_map.size() - 1);
        int index = static_cast<int>(scaled_value);
        float fraction = scaled_value - index;

        if (index >= color_map.size() - 1) {
            return color_map.back();
        }

        // 선형 보간
        const ImVec4& color1 = color_map[index];
        const ImVec4& color2 = color_map[index + 1];

        return ImVec4(
            color1.x + (color2.x - color1.x) * fraction,
            color1.y + (color2.y - color1.y) * fraction,
            color1.z + (color2.z - color1.z) * fraction,
            color1.w + (color2.w - color1.w) * fraction
        );
    }

    void UpdateScale() {
        min_value = std::numeric_limits<float>::max();
        max_value = std::numeric_limits<float>::lowest();

        for (const auto& row : data) {
            for (float value : row) {
                min_value = std::min(min_value, value);
                max_value = std::max(max_value, value);
            }
        }

        // 약간의 여백 추가
        float range = max_value - min_value;
        min_value -= range * 0.05f;
        max_value += range * 0.05f;
    }

    void RenderColorBar(ImDrawList* draw_list, const ImVec2& canvas_pos, const ImVec2& canvas_size) {
        const float colorbar_width = 20.0f;
        const float colorbar_height = canvas_size.y * 0.8f;
        const ImVec2 colorbar_pos = ImVec2(
            canvas_pos.x + canvas_size.x + 10,
            canvas_pos.y + (canvas_size.y - colorbar_height) / 2
        );

        // 컬러바 그라데이션
        const int gradient_steps = 100;
        for (int i = 0; i < gradient_steps; ++i) {
            float normalized_value = static_cast<float>(i) / (gradient_steps - 1);
            ImVec4 color = GetColorFromValue(normalized_value);
            ImU32 color_u32 = ImGui::ColorConvertFloat4ToU32(color);

            float y_start = colorbar_pos.y + (colorbar_height / gradient_steps) * i;
            float y_end = y_start + (colorbar_height / gradient_steps);

            draw_list->AddRectFilled(
                ImVec2(colorbar_pos.x, y_start),
                ImVec2(colorbar_pos.x + colorbar_width, y_end),
                color_u32
            );
        }

        // 컬러바 테두리
        draw_list->AddRect(
            colorbar_pos,
            ImVec2(colorbar_pos.x + colorbar_width, colorbar_pos.y + colorbar_height),
            IM_COL32(200, 200, 200, 255)
        );

        // 스케일 표시
        char max_text[16], min_text[16];
        snprintf(max_text, sizeof(max_text), "%.2f", max_value);
        snprintf(min_text, sizeof(min_text), "%.2f", min_value);

        draw_list->AddText(
            ImVec2(colorbar_pos.x + colorbar_width + 5, colorbar_pos.y - 8),
            IM_COL32(200, 200, 200, 255),
            max_text
        );

        draw_list->AddText(
            ImVec2(colorbar_pos.x + colorbar_width + 5, colorbar_pos.y + colorbar_height - 8),
            IM_COL32(200, 200, 200, 255),
            min_text
        );
    }
};

} // namespace SemiconductorHMI::UI
```

### 실습 5: 고성능 데이터 처리 시스템

#### 5.1 멀티스레드 데이터 프로세서
```cpp
// include/data_processor.h
#pragma once

#include <thread>
#include <atomic>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <vector>
#include <functional>
#include <chrono>
#include <memory>

namespace SemiconductorHMI {

struct ProcessData {
    std::chrono::high_resolution_clock::time_point timestamp;
    std::vector<float> sensor_values;
    int equipment_id;
};

class DataProcessor {
private:
    std::atomic<bool> running{false};
    std::vector<std::thread> worker_threads;

    // 데이터 큐
    std::queue<ProcessData> data_queue;
    std::mutex queue_mutex;
    std::condition_variable queue_cv;

    // 처리된 데이터 콜백
    std::function<void(const ProcessData&)> data_callback;

    // 성능 메트릭
    std::atomic<uint64_t> processed_count{0};
    std::atomic<uint64_t> dropped_count{0};
    std::chrono::high_resolution_clock::time_point start_time;

    static constexpr size_t MAX_QUEUE_SIZE = 10000;

public:
    DataProcessor(size_t num_threads = std::thread::hardware_concurrency()) {
        worker_threads.reserve(num_threads);
    }

    ~DataProcessor() {
        Stop();
    }

    void Start() {
        if (running.exchange(true)) return;

        start_time = std::chrono::high_resolution_clock::now();

        // 워커 스레드들 시작
        for (size_t i = 0; i < worker_threads.capacity(); ++i) {
            worker_threads.emplace_back(&DataProcessor::WorkerLoop, this);
        }
    }

    void Stop() {
        if (!running.exchange(false)) return;

        // 모든 워커들에게 종료 신호
        queue_cv.notify_all();

        // 스레드들 종료 대기
        for (auto& thread : worker_threads) {
            if (thread.joinable()) {
                thread.join();
            }
        }

        worker_threads.clear();
    }

    bool PushData(const ProcessData& data) {
        std::unique_lock<std::mutex> lock(queue_mutex);

        if (data_queue.size() >= MAX_QUEUE_SIZE) {
            dropped_count++;
            return false; // 큐가 가득 참
        }

        data_queue.push(data);
        queue_cv.notify_one();
        return true;
    }

    void SetDataCallback(std::function<void(const ProcessData&)> callback) {
        data_callback = std::move(callback);
    }

    // 성능 메트릭 조회
    uint64_t GetProcessedCount() const { return processed_count; }
    uint64_t GetDroppedCount() const { return dropped_count; }

    double GetProcessingRate() const {
        auto now = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration<double>(now - start_time);
        return processed_count / duration.count();
    }

    size_t GetQueueSize() const {
        std::lock_guard<std::mutex> lock(queue_mutex);
        return data_queue.size();
    }

private:
    void WorkerLoop() {
        while (running) {
            ProcessData data;

            // 큐에서 데이터 가져오기
            {
                std::unique_lock<std::mutex> lock(queue_mutex);
                queue_cv.wait(lock, [this] { return !data_queue.empty() || !running; });

                if (!running) break;

                if (data_queue.empty()) continue;

                data = std::move(data_queue.front());
                data_queue.pop();
            }

            // 데이터 처리
            ProcessSingleData(data);
            processed_count++;

            // 콜백 호출
            if (data_callback) {
                data_callback(data);
            }
        }
    }

    void ProcessSingleData(ProcessData& data) {
        // 시뮬레이션된 데이터 처리 (필터링, 변환 등)

        // 1. 이동 평균 필터 적용
        ApplyMovingAverageFilter(data.sensor_values);

        // 2. 이상값 제거
        RemoveOutliers(data.sensor_values);

        // 3. 단위 변환 또는 스케일링
        for (auto& value : data.sensor_values) {
            value = value * 1.001f + 0.01f; // 간단한 변환 예제
        }
    }

    void ApplyMovingAverageFilter(std::vector<float>& values) {
        static thread_local std::vector<std::vector<float>> history(
            std::thread::hardware_concurrency(), std::vector<float>(10, 0.0f)
        );

        // 간단한 이동 평균 구현 (실제로는 더 정교한 필터 필요)
        static thread_local size_t thread_id = 0;
        static thread_local bool id_initialized = false;

        if (!id_initialized) {
            thread_id = std::hash<std::thread::id>{}(std::this_thread::get_id()) %
                       std::thread::hardware_concurrency();
            id_initialized = true;
        }

        auto& local_history = history[thread_id];

        for (size_t i = 0; i < values.size() && i < local_history.size(); ++i) {
            local_history[i] = values[i];

            // 마지막 N개 값의 평균 계산
            float sum = 0.0f;
            for (float hist_val : local_history) {
                sum += hist_val;
            }
            values[i] = sum / local_history.size();
        }
    }

    void RemoveOutliers(std::vector<float>& values) {
        if (values.size() < 3) return;

        // 간단한 IQR 기반 이상값 제거
        std::vector<float> sorted_values = values;
        std::sort(sorted_values.begin(), sorted_values.end());

        size_t q1_idx = sorted_values.size() / 4;
        size_t q3_idx = 3 * sorted_values.size() / 4;

        float q1 = sorted_values[q1_idx];
        float q3 = sorted_values[q3_idx];
        float iqr = q3 - q1;

        float lower_bound = q1 - 1.5f * iqr;
        float upper_bound = q3 + 1.5f * iqr;

        for (auto& value : values) {
            if (value < lower_bound || value > upper_bound) {
                // 이상값을 중간값으로 대체
                value = sorted_values[sorted_values.size() / 2];
            }
        }
    }
};

} // namespace SemiconductorHMI
```

#### 5.2 실시간 데이터 시뮬레이터
```cpp
// include/data_simulator.h
#pragma once

#include "data_processor.h"
#include <random>
#include <thread>
#include <atomic>
#include <chrono>

namespace SemiconductorHMI {

class DataSimulator {
private:
    std::atomic<bool> running{false};
    std::thread simulator_thread;
    DataProcessor* data_processor;

    // 시뮬레이션 파라미터
    int sampling_rate_hz = 1000; // 1kHz
    int num_sensors = 16;

    // 랜덤 생성기
    std::random_device rd;
    std::mt19937 gen;
    std::normal_distribution<float> noise_dist;

    // 시뮬레이션된 센서 기준값들
    std::vector<float> base_values;
    std::vector<float> trend_slopes;

public:
    DataSimulator(DataProcessor* processor)
        : data_processor(processor)
        , gen(rd())
        , noise_dist(0.0f, 0.1f) {

        InitializeSensorSimulation();
    }

    ~DataSimulator() {
        Stop();
    }

    void Start() {
        if (running.exchange(true)) return;

        simulator_thread = std::thread(&DataSimulator::SimulationLoop, this);
    }

    void Stop() {
        if (!running.exchange(false)) return;

        if (simulator_thread.joinable()) {
            simulator_thread.join();
        }
    }

    void SetSamplingRate(int rate_hz) {
        sampling_rate_hz = rate_hz;
    }

    void SetSensorCount(int count) {
        num_sensors = count;
        InitializeSensorSimulation();
    }

private:
    void InitializeSensorSimulation() {
        base_values.clear();
        trend_slopes.clear();

        std::uniform_real_distribution<float> base_dist(10.0f, 100.0f);
        std::uniform_real_distribution<float> slope_dist(-0.01f, 0.01f);

        for (int i = 0; i < num_sensors; ++i) {
            base_values.push_back(base_dist(gen));
            trend_slopes.push_back(slope_dist(gen));
        }
    }

    void SimulationLoop() {
        auto next_sample_time = std::chrono::high_resolution_clock::now();
        const auto sample_interval = std::chrono::microseconds(1000000 / sampling_rate_hz);

        uint64_t sample_count = 0;

        while (running) {
            // 다음 샘플 시간까지 대기
            std::this_thread::sleep_until(next_sample_time);
            next_sample_time += sample_interval;

            // 센서 데이터 생성
            ProcessData data;
            data.timestamp = std::chrono::high_resolution_clock::now();
            data.equipment_id = 1;
            data.sensor_values.reserve(num_sensors);

            for (int i = 0; i < num_sensors; ++i) {
                float value = GenerateSensorValue(i, sample_count);
                data.sensor_values.push_back(value);
            }

            // 데이터 프로세서에 전송
            if (data_processor && !data_processor->PushData(data)) {
                // 큐가 가득 찬 경우 경고 (실제로는 로깅 시스템 사용)
                static auto last_warning = std::chrono::steady_clock::now();
                auto now = std::chrono::steady_clock::now();
                if (now - last_warning > std::chrono::seconds(1)) {
                    // printf("Warning: Data queue is full, dropping samples\n");
                    last_warning = now;
                }
            }

            sample_count++;
        }
    }

    float GenerateSensorValue(int sensor_id, uint64_t sample_count) {
        float time_sec = static_cast<float>(sample_count) / sampling_rate_hz;

        // 기본값 + 트렌드 + 주기적 변화 + 노이즈
        float base = base_values[sensor_id];
        float trend = trend_slopes[sensor_id] * time_sec;

        // 다양한 주파수의 사인파 합성
        float periodic = 0.0f;
        periodic += 5.0f * std::sin(2.0f * M_PI * 0.1f * time_sec);  // 0.1Hz
        periodic += 2.0f * std::sin(2.0f * M_PI * 0.5f * time_sec);  // 0.5Hz
        periodic += 1.0f * std::sin(2.0f * M_PI * 2.0f * time_sec);  // 2Hz

        float noise = noise_dist(gen);

        // 센서별 특성 추가
        switch (sensor_id % 4) {
            case 0: // 압력 센서 (로그 스케일 특성)
                return base + trend + periodic * 0.1f + noise;
            case 1: // 온도 센서 (느린 변화)
                return base + trend * 0.1f + periodic * 0.05f + noise * 0.5f;
            case 2: // 유량 센서 (빠른 변화)
                return base + trend + periodic * 2.0f + noise * 2.0f;
            case 3: // 전력 센서 (스파이크 특성)
                if (sample_count % 10000 == 0) { // 가끔 스파이크
                    return base + trend + periodic + 50.0f + noise;
                }
                return base + trend + periodic + noise;
            default:
                return base + trend + periodic + noise;
        }
    }
};

} // namespace SemiconductorHMI
```

---

## 💼 **Hands-on 프로젝트 (45분) - 반도체 장비 모니터링 HMI 프로토타입**

### 최종 프로젝트: 통합 반도체 HMI 시스템

#### 4.1 통합 메인 애플리케이션
```cpp
// include/advanced_semiconductor_hmi.h
#pragma once

#include "hmi_application.h"
#include "data_processor.h"
#include "data_simulator.h"
#include "ui_components/realtime_chart.h"
#include "ui_components/circular_gauge.h"
#include "ui_components/heatmap.h"
#include "ui_components/equipment_status_panel.h"

#include <memory>
#include <unordered_map>
#include <array>

namespace SemiconductorHMI {

class AdvancedSemiconductorHMI : public HMIApplication {
private:
    // 데이터 처리 시스템
    std::unique_ptr<DataProcessor> data_processor;
    std::unique_ptr<DataSimulator> data_simulator;

    // UI 컴포넌트들
    std::unordered_map<std::string, std::unique_ptr<UI::RealtimeChart>> charts;
    std::unordered_map<std::string, std::unique_ptr<UI::CircularGauge>> gauges;
    std::unique_ptr<UI::Heatmap> wafer_heatmap;
    std::unique_ptr<UI::EquipmentStatusPanel> status_panel;

    // 최신 데이터 저장
    ProcessData latest_data;
    std::mutex data_mutex;

    // UI 상태
    bool show_charts = true;
    bool show_gauges = true;
    bool show_heatmap = true;
    bool show_status = true;
    bool show_performance = true;
    int selected_chart_sensor = 0;

    // 웨이퍼 맵 시뮬레이션
    std::array<std::array<float, 32>, 32> wafer_temperature_map;

public:
    AdvancedSemiconductorHMI()
        : HMIApplication("Advanced Semiconductor Equipment HMI", 1920, 1080) {

        InitializeWaferMap();
    }

protected:
    void OnStartup() override {
        // 데이터 처리 시스템 초기화
        data_processor = std::make_unique<DataProcessor>(4); // 4개 워커 스레드
        data_simulator = std::make_unique<DataSimulator>(data_processor.get());

        // 데이터 콜백 설정
        data_processor->SetDataCallback([this](const ProcessData& data) {
            OnDataProcessed(data);
        });

        // UI 컴포넌트 초기화
        InitializeCharts();
        InitializeGauges();
        InitializeHeatmap();
        InitializeStatusPanel();

        // 시뮬레이션 시작
        data_processor->Start();
        data_simulator->Start();
    }

    void OnShutdown() override {
        data_simulator.reset();
        data_processor.reset();
    }

    void OnUpdate(float delta_time) override {
        // 웨이퍼 맵 업데이트 (시뮬레이션)
        UpdateWaferHeatmap();
    }

    void OnRender() override {
        RenderMainMenuBar();
        SetupDockSpace();

        if (show_charts) RenderChartsWindow();
        if (show_gauges) RenderGaugesWindow();
        if (show_heatmap) RenderHeatmapWindow();
        if (show_status) status_panel->Render();
        if (show_performance) RenderPerformanceWindow();
    }

private:
    void InitializeCharts() {
        // 주요 센서별 차트 생성
        const std::vector<std::string> sensor_names = {
            "Chamber Pressure", "RF Power", "Gas Flow Rate",
            "Substrate Temperature", "Plasma Density", "Voltage"
        };

        const std::vector<ImVec4> colors = {
            ImVec4(0.0f, 1.0f, 1.0f, 1.0f),  // Cyan
            ImVec4(1.0f, 0.0f, 1.0f, 1.0f),  // Magenta
            ImVec4(0.0f, 1.0f, 0.0f, 1.0f),  // Green
            ImVec4(1.0f, 0.5f, 0.0f, 1.0f),  // Orange
            ImVec4(1.0f, 1.0f, 0.0f, 1.0f),  // Yellow
            ImVec4(0.5f, 0.5f, 1.0f, 1.0f)   // Light Blue
        };

        for (size_t i = 0; i < sensor_names.size(); ++i) {
            auto chart = std::make_unique<UI::RealtimeChart>(sensor_names[i], 1000);
            chart->SetLineColor(colors[i]);
            chart->SetAutoScale(true);
            charts[sensor_names[i]] = std::move(chart);
        }
    }

    void InitializeGauges() {
        // 중요 파라미터별 게이지 생성
        auto pressure_gauge = std::make_unique<UI::CircularGauge>("Pressure (Torr)", 0.0f, 0.1f);
        pressure_gauge->SetThresholds(0.07f, 0.09f);
        pressure_gauge->SetSize(60.0f, 10.0f);
        gauges["pressure"] = std::move(pressure_gauge);

        auto temperature_gauge = std::make_unique<UI::CircularGauge>("Temperature (°C)", 0.0f, 1000.0f);
        temperature_gauge->SetThresholds(700.0f, 900.0f);
        temperature_gauge->SetSize(60.0f, 10.0f);
        gauges["temperature"] = std::move(temperature_gauge);

        auto power_gauge = std::make_unique<UI::CircularGauge>("RF Power (W)", 0.0f, 2000.0f);
        power_gauge->SetThresholds(1400.0f, 1800.0f);
        power_gauge->SetSize(60.0f, 10.0f);
        gauges["power"] = std::move(power_gauge);
    }

    void InitializeHeatmap() {
        wafer_heatmap = std::make_unique<UI::Heatmap>("Wafer Temperature Map", 32, 32);
        wafer_heatmap->SetRange(200.0f, 800.0f);
    }

    void InitializeStatusPanel() {
        status_panel = std::make_unique<UI::EquipmentStatusPanel>("Equipment Status");

        // 초기 장비 상태 설정
        using namespace UI;
        status_panel->UpdateEquipmentStatus("CVD-Chamber-01", {
            EquipmentState::Running, "PECVD SiO2 deposition in progress", {}, 87.3f, 156, false
        });

        status_panel->UpdateEquipmentStatus("PVD-Chamber-02", {
            EquipmentState::Running, "Al sputtering - Wafer #4567", {}, 92.1f, 234, false
        });

        status_panel->UpdateEquipmentStatus("ETCH-Chamber-03", {
            EquipmentState::Idle, "Ready for next recipe", {}, 0.0f, 0, false
        });

        status_panel->UpdateEquipmentStatus("CMP-Station-04", {
            EquipmentState::Maintenance, "Preventive maintenance cycle", {}, 0.0f, 0, false
        });
    }

    void InitializeWaferMap() {
        // 웨이퍼 온도 맵 초기화 (원형 패턴)
        const float center_x = 16.0f;
        const float center_y = 16.0f;
        const float max_radius = 15.0f;

        for (int y = 0; y < 32; ++y) {
            for (int x = 0; x < 32; ++x) {
                float dx = x - center_x;
                float dy = y - center_y;
                float distance = std::sqrt(dx*dx + dy*dy);

                if (distance <= max_radius) {
                    // 중심에서 가장자리로 갈수록 온도 감소
                    float normalized_distance = distance / max_radius;
                    wafer_temperature_map[y][x] = 600.0f - normalized_distance * 200.0f;
                } else {
                    wafer_temperature_map[y][x] = 300.0f; // 웨이퍼 외부
                }
            }
        }
    }

    void OnDataProcessed(const ProcessData& data) {
        std::lock_guard<std::mutex> lock(data_mutex);
        latest_data = data;

        // 차트 업데이트
        if (data.sensor_values.size() >= 6) {
            charts["Chamber Pressure"]->AddDataPoint(data.sensor_values[0]);
            charts["RF Power"]->AddDataPoint(data.sensor_values[1]);
            charts["Gas Flow Rate"]->AddDataPoint(data.sensor_values[2]);
            charts["Substrate Temperature"]->AddDataPoint(data.sensor_values[3]);
            charts["Plasma Density"]->AddDataPoint(data.sensor_values[4]);
            charts["Voltage"]->AddDataPoint(data.sensor_values[5]);

            // 게이지 업데이트
            gauges["pressure"]->SetValue(data.sensor_values[0] / 1000.0f); // mTorr to Torr
            gauges["temperature"]->SetValue(data.sensor_values[3]);
            gauges["power"]->SetValue(data.sensor_values[1]);
        }
    }

    void UpdateWaferHeatmap() {
        // 웨이퍼 온도 맵 동적 업데이트 (시뮬레이션)
        static float time_accumulator = 0.0f;
        time_accumulator += ImGui::GetIO().DeltaTime;

        if (time_accumulator >= 0.1f) { // 100ms마다 업데이트
            std::vector<std::vector<float>> heatmap_data(32, std::vector<float>(32));

            for (int y = 0; y < 32; ++y) {
                for (int x = 0; x < 32; ++x) {
                    // 시간에 따른 온도 변화 시뮬레이션
                    float base_temp = wafer_temperature_map[y][x];
                    float variation = 10.0f * std::sin(time_accumulator * 0.5f + x * 0.1f + y * 0.1f);
                    heatmap_data[y][x] = base_temp + variation;
                }
            }

            wafer_heatmap->SetData(heatmap_data);
            time_accumulator = 0.0f;
        }
    }

    void RenderMainMenuBar() {
        if (ImGui::BeginMainMenuBar()) {
            if (ImGui::BeginMenu("View")) {
                ImGui::MenuItem("Real-time Charts", nullptr, &show_charts);
                ImGui::MenuItem("Gauge Panel", nullptr, &show_gauges);
                ImGui::MenuItem("Wafer Heatmap", nullptr, &show_heatmap);
                ImGui::MenuItem("Equipment Status", nullptr, &show_status);
                ImGui::MenuItem("Performance Metrics", nullptr, &show_performance);
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("Control")) {
                if (ImGui::MenuItem("Start Process")) {
                    // 프로세스 시작 로직
                }
                if (ImGui::MenuItem("Stop Process")) {
                    // 프로세스 중지 로직
                }
                if (ImGui::MenuItem("Emergency Stop")) {
                    // 비상 정지 로직
                }
                ImGui::EndMenu();
            }

            ImGui::EndMainMenuBar();
        }
    }

    void SetupDockSpace() {
        static bool dockspace_open = true;
        static ImGuiDockNodeFlags dockspace_flags = ImGuiDockNodeFlags_None;

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

    void RenderChartsWindow() {
        if (ImGui::Begin("Real-time Sensor Data", &show_charts)) {
            // 센서 선택 콤보박스
            const char* sensor_names[] = {
                "Chamber Pressure", "RF Power", "Gas Flow Rate",
                "Substrate Temperature", "Plasma Density", "Voltage"
            };

            ImGui::Combo("Selected Sensor", &selected_chart_sensor, sensor_names, 6);

            // 선택된 센서의 대형 차트
            if (selected_chart_sensor < 6) {
                std::string sensor_name = sensor_names[selected_chart_sensor];
                if (charts.find(sensor_name) != charts.end()) {
                    charts[sensor_name]->Render(ImVec2(-1, 200));
                }
            }

            ImGui::Separator();

            // 모든 센서의 작은 차트들
            if (ImGui::BeginChild("Mini Charts", ImVec2(0, 0), true)) {
                int chart_count = 0;
                float chart_width = ImGui::GetContentRegionAvail().x / 3.0f - 10.0f;

                for (auto& [name, chart] : charts) {
                    if (chart_count % 3 != 0) ImGui::SameLine();

                    chart->Render(ImVec2(chart_width, 120));
                    chart_count++;
                }
            }
            ImGui::EndChild();
        }
        ImGui::End();
    }

    void RenderGaugesWindow() {
        if (ImGui::Begin("Critical Parameters", &show_gauges)) {
            // 게이지들을 격자로 배열
            int gauge_count = 0;
            for (auto& [name, gauge] : gauges) {
                if (gauge_count % 3 != 0) ImGui::SameLine();

                if (ImGui::BeginChild(name.c_str(), ImVec2(150, 180), true)) {
                    gauge->Render();
                }
                ImGui::EndChild();
                gauge_count++;
            }
        }
        ImGui::End();
    }

    void RenderHeatmapWindow() {
        if (ImGui::Begin("Wafer Temperature Distribution", &show_heatmap)) {
            wafer_heatmap->Render(ImVec2(-1, -1));
        }
        ImGui::End();
    }

    void RenderPerformanceWindow() {
        if (ImGui::Begin("System Performance", &show_performance)) {
            // 데이터 처리 성능
            ImGui::Text("Data Processing Performance:");
            ImGui::Text("Processed Samples: %llu", data_processor->GetProcessedCount());
            ImGui::Text("Dropped Samples: %llu", data_processor->GetDroppedCount());
            ImGui::Text("Processing Rate: %.1f samples/sec", data_processor->GetProcessingRate());
            ImGui::Text("Queue Size: %zu", data_processor->GetQueueSize());

            ImGui::Separator();

            // 애플리케이션 성능
            ImGui::Text("Application Performance:");
            ImGui::Text("Frame Time: %.3f ms", GetFrameTime() * 1000.0f);
            ImGui::Text("FPS: %.1f", GetFPS());

            // 메모리 사용량 (플랫폼별 구현 필요)
            ImGui::Text("Memory Usage: N/A MB");

            ImGui::Separator();

            // ImGUI 렌더링 통계
            ImGuiIO& io = ImGui::GetIO();
            ImGui::Text("Render Statistics:");
            ImGui::Text("Vertices: %d", io.MetricsRenderVertices);
            ImGui::Text("Indices: %d", io.MetricsRenderIndices);
            ImGui::Text("Windows: %d", io.MetricsRenderWindows);
        }
        ImGui::End();
    }
};

} // namespace SemiconductorHMI
```

#### 4.2 최종 메인 함수
```cpp
// src/main.cpp
#include "advanced_semiconductor_hmi.h"
#include <iostream>
#include <exception>

#ifdef _WIN32
#include <windows.h>
#endif

int main() {
    try {
        // 윈도우에서 콘솔 출력 활성화
        #ifdef _WIN32
        AllocConsole();
        freopen_s((FILE**)stdout, "CONOUT$", "w", stdout);
        freopen_s((FILE**)stderr, "CONOUT$", "w", stderr);
        #endif

        std::cout << "Starting Advanced Semiconductor HMI Application..." << std::endl;

        SemiconductorHMI::AdvancedSemiconductorHMI app;

        if (!app.Initialize()) {
            std::cerr << "Failed to initialize application" << std::endl;
            return -1;
        }

        std::cout << "Application initialized successfully. Starting main loop..." << std::endl;
        app.Run();

        std::cout << "Application terminated successfully." << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return -1;
    } catch (...) {
        std::cerr << "Unknown exception occurred" << std::endl;
        return -1;
    }

    return 0;
}
```

#### 4.3 빌드 스크립트
```cmake
