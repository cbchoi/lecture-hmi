# Week 12: ImGUI C++ 고급 기능 - 플러그인 시스템 및 확장성

## 🎯 이번 주 학습 목표
1. **플러그인 아키텍처**: 동적 로딩 시스템 및 모듈화 설계
2. **고급 데이터 시각화**: BigData 처리 및 실시간 차트 엔진
3. **멀티스레딩 통합**: 동시성 제어 및 비동기 처리
4. **국제화 및 확장성**: 글로벌 HMI 플랫폼 구축

---

## 📚 이론 강의 (45분): 플러그인 아키텍처 및 확장성 설계

### 1. 플러그인 아키텍처 설계 (15분)

#### 1.1 플러그인 인터페이스 정의

```cpp
// PluginInterface.h
#pragma once
#include <memory>
#include <string>
#include <vector>
#include <imgui.h>

namespace SemiconductorHMI::Plugin {

// 플러그인 기본 인터페이스
class IPlugin {
public:
    virtual ~IPlugin() = default;

    // 플러그인 메타데이터
    virtual std::string GetName() const = 0;
    virtual std::string GetVersion() const = 0;
    virtual std::string GetDescription() const = 0;
    virtual std::vector<std::string> GetDependencies() const = 0;

    // 라이프사이클 관리
    virtual bool Initialize() = 0;
    virtual void Shutdown() = 0;
    virtual bool IsInitialized() const = 0;

    // ImGUI 통합
    virtual void OnUpdate(float deltaTime) = 0;
    virtual void OnRender() = 0;
    virtual void OnImGuiRender() = 0;
};

// 위젯 플러그인 인터페이스
class IWidgetPlugin : public IPlugin {
public:
    virtual void RenderWidget(const char* name, bool* open = nullptr) = 0;
    virtual ImVec2 GetPreferredSize() const = 0;
    virtual bool IsResizable() const = 0;
};

// 데이터 소스 플러그인 인터페이스
class IDataSourcePlugin : public IPlugin {
public:
    virtual bool Connect(const std::string& connectionString) = 0;
    virtual void Disconnect() = 0;
    virtual bool IsConnected() const = 0;
    virtual std::vector<uint8_t> ReadData() = 0;
    virtual bool WriteData(const std::vector<uint8_t>& data) = 0;
};

// 플러그인 팩토리
class IPluginFactory {
public:
    virtual ~IPluginFactory() = default;
    virtual std::unique_ptr<IPlugin> CreatePlugin() = 0;
    virtual std::string GetPluginType() const = 0;
};

} // namespace SemiconductorHMI::Plugin
```

#### 1.2 동적 플러그인 로더

```cpp
// PluginManager.h
#pragma once
#include "PluginInterface.h"
#include <boost/dll.hpp>
#include <boost/filesystem.hpp>
#include <unordered_map>
#include <memory>

namespace SemiconductorHMI::Plugin {

struct PluginInfo {
    std::string name;
    std::string version;
    std::string description;
    std::string filepath;
    boost::dll::shared_library library;
    std::unique_ptr<IPlugin> instance;
    bool initialized = false;
};

class PluginManager {
private:
    std::unordered_map<std::string, std::unique_ptr<PluginInfo>> plugins_;
    std::vector<std::string> plugin_directories_;

public:
    // 플러그인 디렉토리 관리
    void AddPluginDirectory(const std::string& directory) {
        plugin_directories_.push_back(directory);
    }

    // 플러그인 검색 및 로드
    bool ScanAndLoadPlugins() {
        for (const auto& dir : plugin_directories_) {
            ScanDirectory(dir);
        }
        return InitializeAllPlugins();
    }

    // 개별 플러그인 로드
    bool LoadPlugin(const std::string& filepath) {
        try {
            auto library = boost::dll::shared_library(
                filepath,
                boost::dll::load_mode::append_decorations
            );

            // 플러그인 팩토리 함수 가져오기
            auto create_plugin = library.get<std::unique_ptr<IPlugin>()>(
                "create_plugin"
            );

            auto plugin = create_plugin();
            if (!plugin) {
                return false;
            }

            auto info = std::make_unique<PluginInfo>();
            info->name = plugin->GetName();
            info->version = plugin->GetVersion();
            info->description = plugin->GetDescription();
            info->filepath = filepath;
            info->library = std::move(library);
            info->instance = std::move(plugin);

            plugins_[info->name] = std::move(info);
            return true;

        } catch (const std::exception& e) {
            // 로깅: 플러그인 로드 실패
            return false;
        }
    }

    // 플러그인 초기화
    bool InitializePlugin(const std::string& name) {
        auto it = plugins_.find(name);
        if (it == plugins_.end()) return false;

        auto& info = it->second;
        if (info->initialized) return true;

        // 의존성 확인
        for (const auto& dep : info->instance->GetDependencies()) {
            if (!IsPluginInitialized(dep)) {
                if (!InitializePlugin(dep)) {
                    return false;
                }
            }
        }

        info->initialized = info->instance->Initialize();
        return info->initialized;
    }

    // 플러그인 관리
    IPlugin* GetPlugin(const std::string& name) {
        auto it = plugins_.find(name);
        return (it != plugins_.end()) ? it->second->instance.get() : nullptr;
    }

    template<typename T>
    T* GetPlugin(const std::string& name) {
        return dynamic_cast<T*>(GetPlugin(name));
    }

    // 모든 플러그인 업데이트
    void UpdateAllPlugins(float deltaTime) {
        for (auto& [name, info] : plugins_) {
            if (info->initialized) {
                info->instance->OnUpdate(deltaTime);
            }
        }
    }

    void RenderAllPlugins() {
        for (auto& [name, info] : plugins_) {
            if (info->initialized) {
                info->instance->OnRender();
                info->instance->OnImGuiRender();
            }
        }
    }

private:
    void ScanDirectory(const std::string& directory) {
        namespace fs = boost::filesystem;

        if (!fs::exists(directory) || !fs::is_directory(directory)) {
            return;
        }

        for (auto& entry : fs::directory_iterator(directory)) {
            if (entry.path().extension() == ".dll" ||
                entry.path().extension() == ".so" ||
                entry.path().extension() == ".dylib") {
                LoadPlugin(entry.path().string());
            }
        }
    }

    bool InitializeAllPlugins() {
        bool success = true;
        for (auto& [name, info] : plugins_) {
            if (!InitializePlugin(name)) {
                success = false;
            }
        }
        return success;
    }

    bool IsPluginInitialized(const std::string& name) {
        auto it = plugins_.find(name);
        return (it != plugins_.end()) && it->second->initialized;
    }
};

} // namespace SemiconductorHMI::Plugin
```

### 2. 고급 데이터 시각화 엔진 (15분)

#### 2.1 BigData 처리 시스템

```cpp
// DataVisualizationEngine.h
#pragma once
#include <vector>
#include <memory>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <atomic>
#include <imgui.h>

namespace SemiconductorHMI::Visualization {

// 데이터 포인트 구조
struct DataPoint {
    double timestamp;
    double value;
    uint32_t quality;  // 데이터 품질 지표

    DataPoint(double t, double v, uint32_t q = 100)
        : timestamp(t), value(v), quality(q) {}
};

// 시계열 데이터 버퍼
class TimeSeriesBuffer {
private:
    std::vector<DataPoint> data_;
    mutable std::shared_mutex mutex_;
    size_t max_size_;
    size_t write_index_ = 0;
    bool is_circular_ = false;

public:
    explicit TimeSeriesBuffer(size_t max_size = 100000)
        : max_size_(max_size) {
        data_.reserve(max_size_);
    }

    void AddPoint(const DataPoint& point) {
        std::unique_lock lock(mutex_);

        if (data_.size() < max_size_) {
            data_.push_back(point);
        } else {
            // 순환 버퍼로 전환
            data_[write_index_] = point;
            write_index_ = (write_index_ + 1) % max_size_;
            is_circular_ = true;
        }
    }

    void AddPoints(const std::vector<DataPoint>& points) {
        std::unique_lock lock(mutex_);
        for (const auto& point : points) {
            if (data_.size() < max_size_) {
                data_.push_back(point);
            } else {
                data_[write_index_] = point;
                write_index_ = (write_index_ + 1) % max_size_;
                is_circular_ = true;
            }
        }
    }

    std::vector<DataPoint> GetRange(double start_time, double end_time) const {
        std::shared_lock lock(mutex_);
        std::vector<DataPoint> result;

        for (const auto& point : data_) {
            if (point.timestamp >= start_time && point.timestamp <= end_time) {
                result.push_back(point);
            }
        }

        return result;
    }

    size_t Size() const {
        std::shared_lock lock(mutex_);
        return data_.size();
    }

    DataPoint GetLatest() const {
        std::shared_lock lock(mutex_);
        if (data_.empty()) return DataPoint(0, 0, 0);

        if (is_circular_) {
            size_t latest_index = (write_index_ + max_size_ - 1) % max_size_;
            return data_[latest_index];
        } else {
            return data_.back();
        }
    }
};

// 고성능 차트 렌더러
class AdvancedChartRenderer {
private:
    struct ChartStyle {
        ImU32 line_color = IM_COL32(255, 255, 255, 255);
        ImU32 fill_color = IM_COL32(255, 255, 255, 64);
        ImU32 grid_color = IM_COL32(128, 128, 128, 128);
        float line_thickness = 1.0f;
        bool show_grid = true;
        bool show_fill = false;
        bool show_points = false;
        float point_size = 3.0f;
    };

    ChartStyle style_;

public:
    void SetStyle(const ChartStyle& style) {
        style_ = style;
    }

    void RenderTimeSeriesChart(
        const char* label,
        const TimeSeriesBuffer& buffer,
        const ImVec2& size,
        double time_range = 60.0) {

        ImGui::BeginChild(label, size, true);

        ImDrawList* draw_list = ImGui::GetWindowDrawList();
        ImVec2 canvas_pos = ImGui::GetCursorScreenPos();
        ImVec2 canvas_size = ImGui::GetContentRegionAvail();

        if (canvas_size.x <= 0 || canvas_size.y <= 0) {
            ImGui::EndChild();
            return;
        }

        double current_time = ImGui::GetTime();
        double start_time = current_time - time_range;

        auto data_points = buffer.GetRange(start_time, current_time);
        if (data_points.empty()) {
            ImGui::EndChild();
            return;
        }

        // 데이터 범위 계산
        double min_value = data_points[0].value;
        double max_value = data_points[0].value;
        for (const auto& point : data_points) {
            min_value = std::min(min_value, point.value);
            max_value = std::max(max_value, point.value);
        }

        double value_range = max_value - min_value;
        if (value_range == 0) value_range = 1.0;

        // 그리드 렌더링
        if (style_.show_grid) {
            RenderGrid(draw_list, canvas_pos, canvas_size);
        }

        // 데이터 포인트를 화면 좌표로 변환
        std::vector<ImVec2> screen_points;
        screen_points.reserve(data_points.size());

        for (const auto& point : data_points) {
            float x = canvas_pos.x +
                     ((point.timestamp - start_time) / time_range) * canvas_size.x;
            float y = canvas_pos.y + canvas_size.y -
                     ((point.value - min_value) / value_range) * canvas_size.y;
            screen_points.emplace_back(x, y);
        }

        // 영역 채우기
        if (style_.show_fill && screen_points.size() > 1) {
            std::vector<ImVec2> fill_points = screen_points;
            fill_points.emplace_back(screen_points.back().x, canvas_pos.y + canvas_size.y);
            fill_points.emplace_back(screen_points.front().x, canvas_pos.y + canvas_size.y);

            draw_list->AddConvexPolyFilled(
                fill_points.data(),
                fill_points.size(),
                style_.fill_color
            );
        }

        // 라인 렌더링
        if (screen_points.size() > 1) {
            for (size_t i = 1; i < screen_points.size(); ++i) {
                draw_list->AddLine(
                    screen_points[i-1],
                    screen_points[i],
                    style_.line_color,
                    style_.line_thickness
                );
            }
        }

        // 포인트 렌더링
        if (style_.show_points) {
            for (const auto& point : screen_points) {
                draw_list->AddCircleFilled(
                    point,
                    style_.point_size,
                    style_.line_color
                );
            }
        }

        // 툴팁 표시
        RenderTooltip(data_points, screen_points, canvas_pos, canvas_size,
                     start_time, time_range, min_value, value_range);

        ImGui::EndChild();
    }

private:
    void RenderGrid(ImDrawList* draw_list, ImVec2 canvas_pos, ImVec2 canvas_size) {
        const int grid_lines_x = 10;
        const int grid_lines_y = 5;

        // 수직 그리드 라인
        for (int i = 0; i <= grid_lines_x; ++i) {
            float x = canvas_pos.x + (canvas_size.x / grid_lines_x) * i;
            draw_list->AddLine(
                ImVec2(x, canvas_pos.y),
                ImVec2(x, canvas_pos.y + canvas_size.y),
                style_.grid_color
            );
        }

        // 수평 그리드 라인
        for (int i = 0; i <= grid_lines_y; ++i) {
            float y = canvas_pos.y + (canvas_size.y / grid_lines_y) * i;
            draw_list->AddLine(
                ImVec2(canvas_pos.x, y),
                ImVec2(canvas_pos.x + canvas_size.x, y),
                style_.grid_color
            );
        }
    }

    void RenderTooltip(
        const std::vector<DataPoint>& data_points,
        const std::vector<ImVec2>& screen_points,
        ImVec2 canvas_pos, ImVec2 canvas_size,
        double start_time, double time_range,
        double min_value, double value_range) {

        ImVec2 mouse_pos = ImGui::GetMousePos();

        // 마우스가 차트 영역 내에 있는지 확인
        if (mouse_pos.x >= canvas_pos.x &&
            mouse_pos.x <= canvas_pos.x + canvas_size.x &&
            mouse_pos.y >= canvas_pos.y &&
            mouse_pos.y <= canvas_pos.y + canvas_size.y) {

            // 가장 가까운 데이터 포인트 찾기
            float min_distance = FLT_MAX;
            size_t closest_index = 0;

            for (size_t i = 0; i < screen_points.size(); ++i) {
                float distance = std::sqrt(
                    std::pow(screen_points[i].x - mouse_pos.x, 2) +
                    std::pow(screen_points[i].y - mouse_pos.y, 2)
                );

                if (distance < min_distance) {
                    min_distance = distance;
                    closest_index = i;
                }
            }

            if (min_distance < 20.0f && closest_index < data_points.size()) {
                ImGui::BeginTooltip();
                ImGui::Text("Time: %.2f", data_points[closest_index].timestamp);
                ImGui::Text("Value: %.4f", data_points[closest_index].value);
                ImGui::Text("Quality: %u%%", data_points[closest_index].quality);
                ImGui::EndTooltip();
            }
        }
    }
};

} // namespace SemiconductorHMI::Visualization
```

### 3. 멀티스레딩 및 동시성 제어 (15분)

#### 3.1 스레드 안전 렌더링 시스템

```cpp
// ThreadSafeRenderer.h
#pragma once
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <queue>
#include <functional>
#include <future>

namespace SemiconductorHMI::Threading {

// 렌더링 명령
struct RenderCommand {
    std::function<void()> execute;
    std::string name;
    uint32_t priority = 0;

    RenderCommand(std::function<void()> func, const std::string& n, uint32_t p = 0)
        : execute(std::move(func)), name(n), priority(p) {}
};

// 우선순위 비교자
struct RenderCommandCompare {
    bool operator()(const RenderCommand& a, const RenderCommand& b) const {
        return a.priority < b.priority;  // 높은 우선순위가 먼저
    }
};

// 스레드 안전 렌더링 큐
class ThreadSafeRenderQueue {
private:
    std::priority_queue<RenderCommand, std::vector<RenderCommand>, RenderCommandCompare> commands_;
    mutable std::mutex mutex_;
    std::condition_variable condition_;
    std::atomic<bool> shutdown_{false};

public:
    void Enqueue(RenderCommand command) {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            commands_.push(std::move(command));
        }
        condition_.notify_one();
    }

    bool Dequeue(RenderCommand& command, std::chrono::milliseconds timeout = std::chrono::milliseconds(100)) {
        std::unique_lock<std::mutex> lock(mutex_);

        if (condition_.wait_for(lock, timeout, [this] { return !commands_.empty() || shutdown_; })) {
            if (!commands_.empty()) {
                command = std::move(const_cast<RenderCommand&>(commands_.top()));
                commands_.pop();
                return true;
            }
        }
        return false;
    }

    void Shutdown() {
        shutdown_ = true;
        condition_.notify_all();
    }

    size_t Size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return commands_.size();
    }
};

// 멀티스레드 렌더러
class MultiThreadedRenderer {
private:
    ThreadSafeRenderQueue render_queue_;
    ThreadSafeRenderQueue ui_queue_;

    std::vector<std::thread> worker_threads_;
    std::thread ui_thread_;

    std::atomic<bool> running_{false};
    std::atomic<bool> vsync_enabled_{true};

    // 프레임 동기화
    mutable std::mutex frame_mutex_;
    std::condition_variable frame_condition_;
    std::atomic<uint64_t> frame_counter_{0};

public:
    MultiThreadedRenderer(size_t worker_count = std::thread::hardware_concurrency()) {
        StartWorkerThreads(worker_count);
        StartUIThread();
    }

    ~MultiThreadedRenderer() {
        Shutdown();
    }

    // 렌더링 작업 큐잉
    template<typename F>
    auto QueueRenderTask(F&& func, const std::string& name, uint32_t priority = 0)
        -> std::future<decltype(func())> {

        using ReturnType = decltype(func());
        auto task = std::make_shared<std::packaged_task<ReturnType()>>(std::forward<F>(func));
        auto future = task->get_future();

        render_queue_.Enqueue(RenderCommand(
            [task]() { (*task)(); },
            name,
            priority
        ));

        return future;
    }

    // UI 작업 큐잉 (메인 스레드에서 실행)
    template<typename F>
    void QueueUITask(F&& func, const std::string& name, uint32_t priority = 0) {
        ui_queue_.Enqueue(RenderCommand(
            std::forward<F>(func),
            name,
            priority
        ));
    }

    // 프레임 동기화
    void WaitForFrame() {
        std::unique_lock<std::mutex> lock(frame_mutex_);
        uint64_t current_frame = frame_counter_.load();
        frame_condition_.wait(lock, [this, current_frame] {
            return frame_counter_.load() > current_frame;
        });
    }

    void CompleteFrame() {
        {
            std::lock_guard<std::mutex> lock(frame_mutex_);
            frame_counter_++;
        }
        frame_condition_.notify_all();
    }

    // VSync 제어
    void EnableVSync(bool enable) {
        vsync_enabled_ = enable;
    }

    bool IsVSyncEnabled() const {
        return vsync_enabled_;
    }

private:
    void StartWorkerThreads(size_t count) {
        running_ = true;
        worker_threads_.reserve(count);

        for (size_t i = 0; i < count; ++i) {
            worker_threads_.emplace_back([this, i]() {
                WorkerThreadLoop(i);
            });
        }
    }

    void StartUIThread() {
        ui_thread_ = std::thread([this]() {
            UIThreadLoop();
        });
    }

    void WorkerThreadLoop(size_t thread_id) {
        while (running_) {
            RenderCommand command;
            if (render_queue_.Dequeue(command)) {
                try {
                    command.execute();
                } catch (const std::exception& e) {
                    // 로깅: 렌더링 작업 실패
                }
            }
        }
    }

    void UIThreadLoop() {
        while (running_) {
            RenderCommand command;
            if (ui_queue_.Dequeue(command)) {
                try {
                    command.execute();
                } catch (const std::exception& e) {
                    // 로깅: UI 작업 실패
                }
            }
        }
    }

    void Shutdown() {
        if (running_) {
            running_ = false;

            render_queue_.Shutdown();
            ui_queue_.Shutdown();

            for (auto& thread : worker_threads_) {
                if (thread.joinable()) {
                    thread.join();
                }
            }

            if (ui_thread_.joinable()) {
                ui_thread_.join();
            }
        }
    }
};

} // namespace SemiconductorHMI::Threading

---

## 🛠️ 기초 실습 (45분): 플러그인 시스템 및 고급 차트 개발

### 실습 1: 반도체 장비 모니터링 플러그인 개발 (20분)

#### 1.1 CVD 장비 모니터링 플러그인

```cpp
// CVDMonitorPlugin.cpp
#include "PluginInterface.h"
#include "DataVisualizationEngine.h"
#include <imgui.h>
#include <chrono>
#include <random>

namespace SemiconductorHMI::Plugin {

class CVDMonitorPlugin : public IWidgetPlugin {
private:
    bool initialized_ = false;
    std::string name_ = "CVD Equipment Monitor";
    std::string version_ = "1.0.0";

    // 실시간 데이터
    Visualization::TimeSeriesBuffer temperature_data_{10000};
    Visualization::TimeSeriesBuffer pressure_data_{10000};
    Visualization::TimeSeriesBuffer flow_rate_data_{10000};
    Visualization::AdvancedChartRenderer chart_renderer_;

    // 시뮬레이션 데이터 생성
    std::mt19937 random_gen_{std::random_device{}()};
    std::normal_distribution<double> temp_dist_{250.0, 10.0};    // 250°C ± 10°C
    std::normal_distribution<double> pressure_dist_{0.1, 0.01}; // 0.1 Torr ± 0.01
    std::normal_distribution<double> flow_dist_{50.0, 2.0};     // 50 sccm ± 2.0

    double last_update_time_ = 0.0;

public:
    // IPlugin 인터페이스 구현
    std::string GetName() const override { return name_; }
    std::string GetVersion() const override { return version_; }
    std::string GetDescription() const override {
        return "CVD 장비의 온도, 압력, 가스 유량을 실시간 모니터링";
    }
    std::vector<std::string> GetDependencies() const override { return {}; }

    bool Initialize() override {
        // 차트 스타일 설정
        Visualization::ChartStyle temp_style{};
        temp_style.line_color = IM_COL32(255, 100, 100, 255);  // 빨간색
        temp_style.fill_color = IM_COL32(255, 100, 100, 64);
        temp_style.line_thickness = 2.0f;
        temp_style.show_grid = true;
        temp_style.show_fill = true;

        initialized_ = true;
        return true;
    }

    void Shutdown() override {
        initialized_ = false;
    }

    bool IsInitialized() const override {
        return initialized_;
    }

    void OnUpdate(float deltaTime) override {
        if (!initialized_) return;

        double current_time = ImGui::GetTime();

        // 100ms마다 데이터 업데이트
        if (current_time - last_update_time_ > 0.1) {
            // 시뮬레이션 데이터 생성
            double temperature = temp_dist_(random_gen_);
            double pressure = pressure_dist_(random_gen_);
            double flow_rate = flow_dist_(random_gen_);

            // 데이터 추가
            temperature_data_.AddPoint({current_time, temperature, 100});
            pressure_data_.AddPoint({current_time, pressure, 100});
            flow_rate_data_.AddPoint({current_time, flow_rate, 100});

            last_update_time_ = current_time;
        }
    }

    void OnRender() override {
        // 3D 렌더링이 필요한 경우 여기서 수행
    }

    void OnImGuiRender() override {
        // 메인 렌더링은 RenderWidget에서 수행
    }

    // IWidgetPlugin 인터페이스 구현
    void RenderWidget(const char* name, bool* open = nullptr) override {
        if (!initialized_) return;

        ImGui::SetNextWindowSize(ImVec2(800, 600), ImGuiCond_FirstUseEver);
        if (ImGui::Begin(name, open, ImGuiWindowFlags_MenuBar)) {

            // 메뉴바
            if (ImGui::BeginMenuBar()) {
                if (ImGui::BeginMenu("설정")) {
                    ImGui::MenuItem("알람 설정");
                    ImGui::MenuItem("데이터 내보내기");
                    ImGui::Separator();
                    ImGui::MenuItem("차트 스타일");
                    ImGui::EndMenu();
                }
                ImGui::EndMenuBar();
            }

            // 현재 값 표시
            auto latest_temp = temperature_data_.GetLatest();
            auto latest_pressure = pressure_data_.GetLatest();
            auto latest_flow = flow_rate_data_.GetLatest();

            ImGui::Columns(3, "current_values");

            // 온도
            ImGui::Text("온도");
            ImGui::Text("%.1f °C", latest_temp.value);
            if (latest_temp.value > 270.0f) {
                ImGui::TextColored(ImVec4(1.0f, 0.0f, 0.0f, 1.0f), "경고: 고온");
            }

            ImGui::NextColumn();

            // 압력
            ImGui::Text("압력");
            ImGui::Text("%.3f Torr", latest_pressure.value);
            if (latest_pressure.value > 0.15f) {
                ImGui::TextColored(ImVec4(1.0f, 1.0f, 0.0f, 1.0f), "주의: 고압");
            }

            ImGui::NextColumn();

            // 유량
            ImGui::Text("가스 유량");
            ImGui::Text("%.1f sccm", latest_flow.value);

            ImGui::Columns(1);
            ImGui::Separator();

            // 차트 영역
            ImVec2 chart_size = ImVec2(-1, (ImGui::GetContentRegionAvail().y - 20) / 3);

            // 온도 차트
            ImGui::Text("온도 트렌드");
            chart_renderer_.RenderTimeSeriesChart(
                "temperature_chart",
                temperature_data_,
                chart_size,
                60.0  // 60초 범위
            );

            // 압력 차트
            ImGui::Text("압력 트렌드");
            chart_renderer_.RenderTimeSeriesChart(
                "pressure_chart",
                pressure_data_,
                chart_size,
                60.0
            );

            // 유량 차트
            ImGui::Text("가스 유량 트렌드");
            chart_renderer_.RenderTimeSeriesChart(
                "flow_chart",
                flow_rate_data_,
                chart_size,
                60.0
            );
        }
        ImGui::End();
    }

    ImVec2 GetPreferredSize() const override {
        return ImVec2(800, 600);
    }

    bool IsResizable() const override {
        return true;
    }
};

} // namespace SemiconductorHMI::Plugin

// 플러그인 팩토리 함수 (DLL 내보내기)
extern "C" {
    __declspec(dllexport) std::unique_ptr<SemiconductorHMI::Plugin::IPlugin> create_plugin() {
        return std::make_unique<SemiconductorHMI::Plugin::CVDMonitorPlugin>();
    }
}
```

#### 1.2 OPC-UA 데이터 소스 플러그인

```cpp
// OPCUADataSourcePlugin.cpp
#include "PluginInterface.h"
#include <boost/asio.hpp>
#include <curl/curl.h>
#include <json/json.h>

namespace SemiconductorHMI::Plugin {

class OPCUADataSourcePlugin : public IDataSourcePlugin {
private:
    bool initialized_ = false;
    bool connected_ = false;
    std::string connection_string_;

    // HTTP 클라이언트 (OPC-UA REST Gateway 사용)
    CURL* curl_handle_ = nullptr;
    std::string response_buffer_;

    // 연결 설정
    struct ConnectionConfig {
        std::string server_url;
        std::string username;
        std::string password;
        std::string namespace_uri;
        int timeout_ms = 5000;
    } config_;

public:
    std::string GetName() const override { return "OPC-UA Data Source"; }
    std::string GetVersion() const override { return "1.0.0"; }
    std::string GetDescription() const override {
        return "OPC-UA 서버로부터 실시간 데이터 수집";
    }
    std::vector<std::string> GetDependencies() const override { return {}; }

    bool Initialize() override {
        curl_global_init(CURL_GLOBAL_DEFAULT);
        curl_handle_ = curl_easy_init();

        if (!curl_handle_) {
            return false;
        }

        // cURL 기본 설정
        curl_easy_setopt(curl_handle_, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl_handle_, CURLOPT_WRITEDATA, &response_buffer_);
        curl_easy_setopt(curl_handle_, CURLOPT_TIMEOUT, 5L);

        initialized_ = true;
        return true;
    }

    void Shutdown() override {
        Disconnect();

        if (curl_handle_) {
            curl_easy_cleanup(curl_handle_);
            curl_handle_ = nullptr;
        }

        curl_global_cleanup();
        initialized_ = false;
    }

    bool IsInitialized() const override {
        return initialized_;
    }

    void OnUpdate(float deltaTime) override {
        // 연결 상태 모니터링
        if (connected_) {
            // 주기적 헬스체크
            static float health_check_timer = 0.0f;
            health_check_timer += deltaTime;

            if (health_check_timer > 30.0f) {  // 30초마다
                CheckConnection();
                health_check_timer = 0.0f;
            }
        }
    }

    void OnRender() override {}
    void OnImGuiRender() override {}

    // IDataSourcePlugin 인터페이스 구현
    bool Connect(const std::string& connectionString) override {
        if (!initialized_) return false;

        connection_string_ = connectionString;

        // 연결 문자열 파싱 (JSON 형태)
        Json::Value config;
        Json::Reader reader;

        if (!reader.parse(connectionString, config)) {
            return false;
        }

        config_.server_url = config.get("server_url", "").asString();
        config_.username = config.get("username", "").asString();
        config_.password = config.get("password", "").asString();
        config_.namespace_uri = config.get("namespace_uri", "").asString();
        config_.timeout_ms = config.get("timeout_ms", 5000).asInt();

        // 연결 테스트
        std::string test_url = config_.server_url + "/session/create";

        response_buffer_.clear();
        curl_easy_setopt(curl_handle_, CURLOPT_URL, test_url.c_str());
        curl_easy_setopt(curl_handle_, CURLOPT_POST, 1L);

        // 인증 헤더 설정
        struct curl_slist* headers = nullptr;
        std::string auth_header = "Authorization: Basic " +
                                EncodeBase64(config_.username + ":" + config_.password);
        headers = curl_slist_append(headers, auth_header.c_str());
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl_handle_, CURLOPT_HTTPHEADER, headers);

        CURLcode res = curl_easy_perform(curl_handle_);
        curl_slist_free_all(headers);

        if (res == CURLE_OK) {
            long response_code;
            curl_easy_getinfo(curl_handle_, CURLINFO_RESPONSE_CODE, &response_code);

            if (response_code == 200) {
                connected_ = true;
                return true;
            }
        }

        return false;
    }

    void Disconnect() override {
        if (connected_) {
            // 세션 종료 요청
            std::string disconnect_url = config_.server_url + "/session/close";

            curl_easy_setopt(curl_handle_, CURLOPT_URL, disconnect_url.c_str());
            curl_easy_setopt(curl_handle_, CURLOPT_POST, 1L);
            curl_easy_perform(curl_handle_);

            connected_ = false;
        }
    }

    bool IsConnected() const override {
        return connected_;
    }

    std::vector<uint8_t> ReadData() override {
        if (!connected_) return {};

        // 데이터 읽기 요청
        std::string read_url = config_.server_url + "/values/read";

        Json::Value request;
        Json::Value nodes(Json::arrayValue);

        // 읽을 노드 ID들 설정
        nodes.append("ns=2;s=Temperature");
        nodes.append("ns=2;s=Pressure");
        nodes.append("ns=2;s=FlowRate");

        request["nodes"] = nodes;
        request["namespace"] = config_.namespace_uri;

        Json::StreamWriterBuilder builder;
        std::string json_string = Json::writeString(builder, request);

        response_buffer_.clear();
        curl_easy_setopt(curl_handle_, CURLOPT_URL, read_url.c_str());
        curl_easy_setopt(curl_handle_, CURLOPT_POSTFIELDS, json_string.c_str());

        CURLcode res = curl_easy_perform(curl_handle_);

        if (res == CURLE_OK) {
            return std::vector<uint8_t>(response_buffer_.begin(), response_buffer_.end());
        }

        return {};
    }

    bool WriteData(const std::vector<uint8_t>& data) override {
        if (!connected_) return false;

        std::string write_url = config_.server_url + "/values/write";
        std::string data_string(data.begin(), data.end());

        response_buffer_.clear();
        curl_easy_setopt(curl_handle_, CURLOPT_URL, write_url.c_str());
        curl_easy_setopt(curl_handle_, CURLOPT_POSTFIELDS, data_string.c_str());

        CURLcode res = curl_easy_perform(curl_handle_);

        if (res == CURLE_OK) {
            long response_code;
            curl_easy_getinfo(curl_handle_, CURLINFO_RESPONSE_CODE, &response_code);
            return response_code == 200;
        }

        return false;
    }

private:
    static size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* buffer) {
        size_t total_size = size * nmemb;
        buffer->append(static_cast<char*>(contents), total_size);
        return total_size;
    }

    void CheckConnection() {
        // 간단한 헬스체크 요청
        std::string health_url = config_.server_url + "/health";

        response_buffer_.clear();
        curl_easy_setopt(curl_handle_, CURLOPT_URL, health_url.c_str());
        curl_easy_setopt(curl_handle_, CURLOPT_HTTPGET, 1L);

        CURLcode res = curl_easy_perform(curl_handle_);

        if (res != CURLE_OK) {
            connected_ = false;
        }
    }

    std::string EncodeBase64(const std::string& input) {
        // Base64 인코딩 구현 (간단한 버전)
        std::string encoded;
        // 실제 구현에서는 OpenSSL 또는 다른 라이브러리 사용
        return encoded;
    }
};

} // namespace SemiconductorHMI::Plugin

extern "C" {
    __declspec(dllexport) std::unique_ptr<SemiconductorHMI::Plugin::IPlugin> create_plugin() {
        return std::make_unique<SemiconductorHMI::Plugin::OPCUADataSourcePlugin>();
    }
}
```

### 실습 2: 고급 데이터 시각화 대시보드 구현 (25분)

#### 2.1 다중 차트 대시보드

```cpp
// AdvancedDashboard.cpp
#include "DataVisualizationEngine.h"
#include "ThreadSafeRenderer.h"
#include <imgui.h>
#include <vector>
#include <memory>

namespace SemiconductorHMI::Dashboard {

class AdvancedVisualizationDashboard {
private:
    struct ChartConfiguration {
        std::string title;
        std::string unit;
        ImU32 color;
        double min_range;
        double max_range;
        bool auto_scale;
        Visualization::TimeSeriesBuffer* data_buffer;
    };

    std::vector<ChartConfiguration> chart_configs_;
    Visualization::AdvancedChartRenderer chart_renderer_;
    Threading::MultiThreadedRenderer* thread_renderer_;

    // 레이아웃 설정
    struct LayoutConfig {
        int columns = 2;
        int rows = 2;
        float margin = 10.0f;
        bool synchronized_time = true;
        double time_range = 300.0;  // 5분
    } layout_;

    // 성능 모니터링
    struct PerformanceMetrics {
        float frame_time = 0.0f;
        float render_time = 0.0f;
        int data_points_rendered = 0;
        float memory_usage_mb = 0.0f;
    } performance_;

public:
    AdvancedVisualizationDashboard(Threading::MultiThreadedRenderer* renderer)
        : thread_renderer_(renderer) {
        InitializeDefaultCharts();
    }

    void AddChart(const std::string& title,
                  const std::string& unit,
                  ImU32 color,
                  Visualization::TimeSeriesBuffer* buffer,
                  double min_range = 0.0,
                  double max_range = 100.0,
                  bool auto_scale = true) {

        ChartConfiguration config;
        config.title = title;
        config.unit = unit;
        config.color = color;
        config.min_range = min_range;
        config.max_range = max_range;
        config.auto_scale = auto_scale;
        config.data_buffer = buffer;

        chart_configs_.push_back(config);
    }

    void Render() {
        ImGui::Begin("고급 데이터 시각화 대시보드", nullptr,
                     ImGuiWindowFlags_MenuBar | ImGuiWindowFlags_NoScrollbar);

        RenderMenuBar();
        RenderPerformancePanel();
        RenderChartsGrid();

        ImGui::End();
    }

private:
    void InitializeDefaultCharts() {
        // 기본 차트 설정은 외부에서 추가
    }

    void RenderMenuBar() {
        if (ImGui::BeginMenuBar()) {
            if (ImGui::BeginMenu("레이아웃")) {
                ImGui::SliderInt("열 수", &layout_.columns, 1, 4);
                ImGui::SliderInt("행 수", &layout_.rows, 1, 4);
                ImGui::SliderFloat("여백", &layout_.margin, 5.0f, 20.0f);
                ImGui::Checkbox("시간 동기화", &layout_.synchronized_time);
                ImGui::SliderFloat("시간 범위 (초)", (float*)&layout_.time_range, 10.0, 3600.0);
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("차트 설정")) {
                for (size_t i = 0; i < chart_configs_.size(); ++i) {
                    auto& config = chart_configs_[i];
                    if (ImGui::TreeNode(config.title.c_str())) {
                        ImGui::Checkbox("자동 스케일", &config.auto_scale);
                        if (!config.auto_scale) {
                            ImGui::SliderFloat("최소값", (float*)&config.min_range, -1000.0f, 1000.0f);
                            ImGui::SliderFloat("최대값", (float*)&config.max_range, -1000.0f, 1000.0f);
                        }

                        // 색상 선택
                        float color[4];
                        ImGui::ColorConvertU32ToFloat4(config.color, color);
                        if (ImGui::ColorEdit4("색상", color)) {
                            config.color = ImGui::ColorConvertFloat4ToU32(ImVec4(color[0], color[1], color[2], color[3]));
                        }

                        ImGui::TreePop();
                    }
                }
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("성능")) {
                ImGui::Text("프레임 시간: %.2f ms", performance_.frame_time);
                ImGui::Text("렌더 시간: %.2f ms", performance_.render_time);
                ImGui::Text("데이터 포인트: %d", performance_.data_points_rendered);
                ImGui::Text("메모리 사용량: %.1f MB", performance_.memory_usage_mb);
                ImGui::EndMenu();
            }

            ImGui::EndMenuBar();
        }
    }

    void RenderPerformancePanel() {
        // 성능 정보는 최소화된 형태로 표시
        ImGui::Text("FPS: %.1f | 렌더링: %.2f ms | 메모리: %.1f MB",
                   ImGui::GetIO().Framerate,
                   performance_.render_time,
                   performance_.memory_usage_mb);
        ImGui::Separator();
    }

    void RenderChartsGrid() {
        auto start_time = std::chrono::high_resolution_clock::now();

        ImVec2 content_region = ImGui::GetContentRegionAvail();
        float chart_width = (content_region.x - layout_.margin * (layout_.columns + 1)) / layout_.columns;
        float chart_height = (content_region.y - layout_.margin * (layout_.rows + 1)) / layout_.rows;

        performance_.data_points_rendered = 0;

        for (int row = 0; row < layout_.rows; ++row) {
            for (int col = 0; col < layout_.columns; ++col) {
                size_t chart_index = row * layout_.columns + col;
                if (chart_index >= chart_configs_.size()) break;

                ImVec2 chart_pos = ImVec2(
                    layout_.margin + col * (chart_width + layout_.margin),
                    layout_.margin + row * (chart_height + layout_.margin)
                );

                ImGui::SetCursorPos(chart_pos);
                RenderSingleChart(chart_configs_[chart_index], ImVec2(chart_width, chart_height));
            }
        }

        auto end_time = std::chrono::high_resolution_clock::now();
        performance_.render_time = std::chrono::duration<float, std::milli>(end_time - start_time).count();
    }

    void RenderSingleChart(const ChartConfiguration& config, ImVec2 size) {
        if (!config.data_buffer) return;

        ImGui::BeginChild(config.title.c_str(), size, true);

        // 차트 제목
        ImGui::Text("%s (%s)", config.title.c_str(), config.unit.c_str());

        // 현재 값 표시
        auto latest = config.data_buffer->GetLatest();
        ImGui::SameLine();
        ImGui::Text("현재: %.2f", latest.value);

        // 차트 스타일 설정
        Visualization::ChartStyle style;
        style.line_color = config.color;
        style.fill_color = (config.color & 0x00FFFFFF) | 0x40000000;  // 25% 투명도
        style.line_thickness = 1.5f;
        style.show_grid = true;
        style.show_fill = true;

        // 차트 렌더링
        ImVec2 chart_size = ImVec2(size.x - 20, size.y - 60);

        // 멀티스레드 렌더링 큐잉
        if (thread_renderer_) {
            thread_renderer_->QueueRenderTask([this, &config, chart_size]() {
                chart_renderer_.RenderTimeSeriesChart(
                    (config.title + "_chart").c_str(),
                    *config.data_buffer,
                    chart_size,
                    layout_.time_range
                );
            }, "chart_render_" + config.title, 10);
        } else {
            chart_renderer_.RenderTimeSeriesChart(
                (config.title + "_chart").c_str(),
                *config.data_buffer,
                chart_size,
                layout_.time_range
            );
        }

        performance_.data_points_rendered += config.data_buffer->Size();

        ImGui::EndChild();
    }
};

} // namespace SemiconductorHMI::Dashboard

---

## 🔬 심화 실습 (45분): 멀티스레딩 통합 및 외부 시스템 연동

### 실습 3: 국제화 및 접근성 지원 시스템 (20분)

#### 3.1 다국어 지원 시스템

```cpp
// InternationalizationSystem.h
#pragma once
#include <unordered_map>
#include <string>
#include <memory>
#include <locale>
#include <unicode/unistr.h>
#include <unicode/ucnv.h>
#include <unicode/udat.h>
#include <unicode/unum.h>

namespace SemiconductorHMI::I18n {

enum class Language {
    KOREAN,
    ENGLISH,
    JAPANESE,
    CHINESE_SIMPLIFIED,
    CHINESE_TRADITIONAL,
    GERMAN,
    FRENCH
};

enum class TextDirection {
    LEFT_TO_RIGHT,
    RIGHT_TO_LEFT
};

struct LocaleInfo {
    Language language;
    std::string locale_code;
    std::string display_name;
    TextDirection text_direction;
    std::string font_name;
    float font_scale = 1.0f;
};

class LocalizationManager {
private:
    std::unordered_map<std::string, std::unordered_map<std::string, std::u16string>> translations_;
    Language current_language_ = Language::KOREAN;
    std::unordered_map<Language, LocaleInfo> locale_info_;

    // Unicode 변환기
    UConverter* utf8_converter_ = nullptr;
    UConverter* utf16_converter_ = nullptr;

public:
    LocalizationManager() {
        InitializeLocales();
        InitializeConverters();
        LoadTranslations();
    }

    ~LocalizationManager() {
        if (utf8_converter_) ucnv_close(utf8_converter_);
        if (utf16_converter_) ucnv_close(utf16_converter_);
    }

    // 언어 설정
    void SetLanguage(Language language) {
        current_language_ = language;
        UpdateImGuiLocale();
    }

    Language GetCurrentLanguage() const {
        return current_language_;
    }

    // 텍스트 번역
    std::string GetText(const std::string& key) const {
        return GetText(key, current_language_);
    }

    std::string GetText(const std::string& key, Language language) const {
        auto lang_it = translations_.find(GetLanguageCode(language));
        if (lang_it == translations_.end()) {
            return key;  // 번역을 찾을 수 없으면 키 반환
        }

        auto text_it = lang_it->second.find(key);
        if (text_it == lang_it->second.end()) {
            return key;
        }

        // UTF-16에서 UTF-8로 변환
        return ConvertUTF16ToUTF8(text_it->second);
    }

    // 형식화된 텍스트 (매개변수 지원)
    template<typename... Args>
    std::string GetFormattedText(const std::string& key, Args... args) const {
        std::string format_string = GetText(key);
        return FormatString(format_string, args...);
    }

    // 숫자 형식화
    std::string FormatNumber(double value, int decimal_places = 2) const {
        UErrorCode status = U_ZERO_ERROR;

        // 현재 로케일에 맞는 숫자 포맷터 생성
        UNumberFormat* formatter = unum_open(
            UNUM_DECIMAL,
            nullptr, 0,
            GetLanguageCode(current_language_).c_str(),
            nullptr,
            &status
        );

        if (U_FAILURE(status)) {
            return std::to_string(value);
        }

        unum_setAttribute(formatter, UNUM_MAX_FRACTION_DIGITS, decimal_places);
        unum_setAttribute(formatter, UNUM_MIN_FRACTION_DIGITS, decimal_places);

        UChar buffer[256];
        int32_t length = unum_formatDouble(formatter, value, buffer, 256, nullptr, &status);

        unum_close(formatter);

        if (U_SUCCESS(status)) {
            return ConvertUCharToUTF8(buffer, length);
        }

        return std::to_string(value);
    }

    // 날짜/시간 형식화
    std::string FormatDateTime(time_t timestamp, const std::string& pattern = "yyyy-MM-dd HH:mm:ss") const {
        UErrorCode status = U_ZERO_ERROR;

        UDateFormat* formatter = udat_open(
            UDAT_PATTERN,
            UDAT_PATTERN,
            GetLanguageCode(current_language_).c_str(),
            nullptr, 0,
            pattern.c_str(), pattern.length(),
            &status
        );

        if (U_FAILURE(status)) {
            return std::ctime(&timestamp);
        }

        UChar buffer[256];
        int32_t length = udat_format(formatter, timestamp * 1000.0, buffer, 256, nullptr, &status);

        udat_close(formatter);

        if (U_SUCCESS(status)) {
            return ConvertUCharToUTF8(buffer, length);
        }

        return std::ctime(&timestamp);
    }

    // 로케일 정보 가져오기
    const LocaleInfo& GetLocaleInfo() const {
        auto it = locale_info_.find(current_language_);
        return it->second;
    }

private:
    void InitializeLocales() {
        locale_info_[Language::KOREAN] = {
            Language::KOREAN, "ko_KR", "한국어", TextDirection::LEFT_TO_RIGHT, "NotoSansCJK-Regular.ttc", 1.0f
        };
        locale_info_[Language::ENGLISH] = {
            Language::ENGLISH, "en_US", "English", TextDirection::LEFT_TO_RIGHT, "Roboto-Regular.ttf", 1.0f
        };
        locale_info_[Language::JAPANESE] = {
            Language::JAPANESE, "ja_JP", "日本語", TextDirection::LEFT_TO_RIGHT, "NotoSansCJK-Regular.ttc", 1.0f
        };
        locale_info_[Language::CHINESE_SIMPLIFIED] = {
            Language::CHINESE_SIMPLIFIED, "zh_CN", "简体中文", TextDirection::LEFT_TO_RIGHT, "NotoSansCJK-Regular.ttc", 1.0f
        };
        locale_info_[Language::CHINESE_TRADITIONAL] = {
            Language::CHINESE_TRADITIONAL, "zh_TW", "繁體中文", TextDirection::LEFT_TO_RIGHT, "NotoSansCJK-Regular.ttc", 1.0f
        };
        locale_info_[Language::GERMAN] = {
            Language::GERMAN, "de_DE", "Deutsch", TextDirection::LEFT_TO_RIGHT, "Roboto-Regular.ttf", 1.0f
        };
        locale_info_[Language::FRENCH] = {
            Language::FRENCH, "fr_FR", "Français", TextDirection::LEFT_TO_RIGHT, "Roboto-Regular.ttf", 1.0f
        };
    }

    void InitializeConverters() {
        UErrorCode status = U_ZERO_ERROR;
        utf8_converter_ = ucnv_open("UTF-8", &status);
        utf16_converter_ = ucnv_open("UTF-16", &status);
    }

    void LoadTranslations() {
        // 한국어 번역
        translations_["ko_KR"]["app.title"] = u"반도체 장비 모니터링 시스템";
        translations_["ko_KR"]["menu.file"] = u"파일";
        translations_["ko_KR"]["menu.settings"] = u"설정";
        translations_["ko_KR"]["menu.help"] = u"도움말";
        translations_["ko_KR"]["status.connected"] = u"연결됨";
        translations_["ko_KR"]["status.disconnected"] = u"연결 끊김";
        translations_["ko_KR"]["equipment.temperature"] = u"온도";
        translations_["ko_KR"]["equipment.pressure"] = u"압력";
        translations_["ko_KR"]["equipment.flow_rate"] = u"유량";
        translations_["ko_KR"]["unit.celsius"] = u"°C";
        translations_["ko_KR"]["unit.torr"] = u"Torr";
        translations_["ko_KR"]["unit.sccm"] = u"sccm";

        // 영어 번역
        translations_["en_US"]["app.title"] = u"Semiconductor Equipment Monitoring System";
        translations_["en_US"]["menu.file"] = u"File";
        translations_["en_US"]["menu.settings"] = u"Settings";
        translations_["en_US"]["menu.help"] = u"Help";
        translations_["en_US"]["status.connected"] = u"Connected";
        translations_["en_US"]["status.disconnected"] = u"Disconnected";
        translations_["en_US"]["equipment.temperature"] = u"Temperature";
        translations_["en_US"]["equipment.pressure"] = u"Pressure";
        translations_["en_US"]["equipment.flow_rate"] = u"Flow Rate";
        translations_["en_US"]["unit.celsius"] = u"°C";
        translations_["en_US"]["unit.torr"] = u"Torr";
        translations_["en_US"]["unit.sccm"] = u"sccm";

        // 일본어 번역
        translations_["ja_JP"]["app.title"] = u"半導体装置監視システム";
        translations_["ja_JP"]["menu.file"] = u"ファイル";
        translations_["ja_JP"]["menu.settings"] = u"設定";
        translations_["ja_JP"]["menu.help"] = u"ヘルプ";
        translations_["ja_JP"]["status.connected"] = u"接続済み";
        translations_["ja_JP"]["status.disconnected"] = u"切断";
        translations_["ja_JP"]["equipment.temperature"] = u"温度";
        translations_["ja_JP"]["equipment.pressure"] = u"圧力";
        translations_["ja_JP"]["equipment.flow_rate"] = u"流量";
        translations_["ja_JP"]["unit.celsius"] = u"°C";
        translations_["ja_JP"]["unit.torr"] = u"Torr";
        translations_["ja_JP"]["unit.sccm"] = u"sccm";
    }

    std::string GetLanguageCode(Language language) const {
        auto it = locale_info_.find(language);
        return (it != locale_info_.end()) ? it->second.locale_code : "en_US";
    }

    void UpdateImGuiLocale() {
        // ImGui 폰트 및 스타일 업데이트
        const auto& locale_info = GetLocaleInfo();

        // 폰트 스케일 적용
        ImGui::GetIO().FontGlobalScale = locale_info.font_scale;

        // RTL 언어 지원 (필요한 경우)
        if (locale_info.text_direction == TextDirection::RIGHT_TO_LEFT) {
            // RTL 레이아웃 설정 (ImGui가 지원하는 경우)
        }
    }

    std::string ConvertUTF16ToUTF8(const std::u16string& utf16_str) const {
        if (!utf8_converter_ || !utf16_converter_) return "";

        UErrorCode status = U_ZERO_ERROR;

        // UTF-16을 UTF-8로 변환
        char utf8_buffer[1024];
        int32_t utf8_length = ucnv_fromUChars(
            utf8_converter_,
            utf8_buffer, sizeof(utf8_buffer),
            reinterpret_cast<const UChar*>(utf16_str.c_str()), utf16_str.length(),
            &status
        );

        if (U_SUCCESS(status)) {
            return std::string(utf8_buffer, utf8_length);
        }

        return "";
    }

    std::string ConvertUCharToUTF8(const UChar* uchar_str, int32_t length) const {
        if (!utf8_converter_) return "";

        UErrorCode status = U_ZERO_ERROR;

        char utf8_buffer[1024];
        int32_t utf8_length = ucnv_fromUChars(
            utf8_converter_,
            utf8_buffer, sizeof(utf8_buffer),
            uchar_str, length,
            &status
        );

        if (U_SUCCESS(status)) {
            return std::string(utf8_buffer, utf8_length);
        }

        return "";
    }

    template<typename... Args>
    std::string FormatString(const std::string& format, Args... args) const {
        int size = std::snprintf(nullptr, 0, format.c_str(), args...) + 1;
        std::unique_ptr<char[]> buf(new char[size]);
        std::snprintf(buf.get(), size, format.c_str(), args...);
        return std::string(buf.get(), buf.get() + size - 1);
    }
};

} // namespace SemiconductorHMI::I18n
```

#### 3.2 접근성 지원 시스템

```cpp
// AccessibilitySystem.h
#pragma once
#include <imgui.h>
#include <vector>
#include <string>
#include <memory>

namespace SemiconductorHMI::Accessibility {

enum class AccessibilityMode {
    NORMAL,
    HIGH_CONTRAST,
    LARGE_TEXT,
    SCREEN_READER,
    COLORBLIND_FRIENDLY
};

struct AccessibilitySettings {
    AccessibilityMode mode = AccessibilityMode::NORMAL;
    float text_scale = 1.0f;
    float ui_scale = 1.0f;
    bool high_contrast = false;
    bool screen_reader_support = false;
    bool reduce_motion = false;
    bool focus_indicators = true;
    ImU32 focus_color = IM_COL32(255, 255, 0, 255);
};

class AccessibilityManager {
private:
    AccessibilitySettings settings_;
    std::vector<std::string> focus_history_;
    std::string current_focus_;

    // 색맹 지원을 위한 색상 팔레트
    struct ColorblindPalette {
        ImU32 primary = IM_COL32(0, 119, 187, 255);      // 파란색
        ImU32 secondary = IM_COL32(255, 119, 0, 255);    // 주황색
        ImU32 success = IM_COL32(0, 153, 136, 255);      // 청록색
        ImU32 warning = IM_COL32(255, 193, 7, 255);      // 노란색
        ImU32 danger = IM_COL32(220, 53, 69, 255);       // 빨간색
        ImU32 background = IM_COL32(248, 249, 250, 255); // 밝은 회색
        ImU32 text = IM_COL32(33, 37, 41, 255);          // 어두운 회색
    } colorblind_palette_;

public:
    void Initialize() {
        ApplyAccessibilitySettings();
    }

    void SetAccessibilityMode(AccessibilityMode mode) {
        settings_.mode = mode;
        ApplyAccessibilitySettings();
    }

    void SetTextScale(float scale) {
        settings_.text_scale = std::clamp(scale, 0.5f, 3.0f);
        ApplyTextScaling();
    }

    void SetUIScale(float scale) {
        settings_.ui_scale = std::clamp(scale, 0.5f, 2.0f);
        ApplyUIScaling();
    }

    void EnableHighContrast(bool enable) {
        settings_.high_contrast = enable;
        ApplyHighContrastTheme();
    }

    void EnableScreenReaderSupport(bool enable) {
        settings_.screen_reader_support = enable;
    }

    // 접근성 지원 위젯들
    bool AccessibleButton(const char* label, const ImVec2& size = ImVec2(0, 0)) {
        bool result = false;

        // 포커스 표시
        if (settings_.focus_indicators && ImGui::IsItemFocused()) {
            ImDrawList* draw_list = ImGui::GetWindowDrawList();
            ImVec2 pos = ImGui::GetItemRectMin();
            ImVec2 size_rect = ImGui::GetItemRectSize();

            draw_list->AddRect(pos, ImVec2(pos.x + size_rect.x, pos.y + size_rect.y),
                             settings_.focus_color, 0.0f, 0, 3.0f);
        }

        // 일반 버튼 렌더링
        result = ImGui::Button(label, size);

        // 스크린 리더 지원
        if (settings_.screen_reader_support && ImGui::IsItemHovered()) {
            AddToAccessibilityDescription(std::string("Button: ") + label);
        }

        return result;
    }

    void AccessibleText(const char* text, ImU32 color = 0) {
        if (settings_.high_contrast && color != 0) {
            // 고대비 모드에서는 색상을 조정
            color = AdjustColorForHighContrast(color);
        }

        if (color != 0) {
            ImGui::TextColored(ImGui::ColorConvertU32ToFloat4(color), "%s", text);
        } else {
            ImGui::Text("%s", text);
        }

        if (settings_.screen_reader_support && ImGui::IsItemHovered()) {
            AddToAccessibilityDescription(text);
        }
    }

    bool AccessibleSliderFloat(const char* label, float* v, float v_min, float v_max,
                              const char* format = "%.3f", ImGuiSliderFlags flags = 0) {
        bool result = ImGui::SliderFloat(label, v, v_min, v_max, format, flags);

        // 키보드 접근성 개선
        if (ImGui::IsItemFocused()) {
            // 더 큰 증감 단위 제공
            if (ImGui::IsKeyPressed(ImGuiKey_PageUp)) {
                *v = std::min(*v + (v_max - v_min) * 0.1f, v_max);
                result = true;
            }
            if (ImGui::IsKeyPressed(ImGuiKey_PageDown)) {
                *v = std::max(*v - (v_max - v_min) * 0.1f, v_min);
                result = true;
            }
        }

        if (settings_.screen_reader_support && result) {
            char desc[256];
            snprintf(desc, sizeof(desc), "%s: %.3f", label, *v);
            AddToAccessibilityDescription(desc);
        }

        return result;
    }

    void AccessibleProgressBar(float fraction, const ImVec2& size_arg = ImVec2(-1, 0),
                              const char* overlay = nullptr) {
        ImGui::ProgressBar(fraction, size_arg, overlay);

        if (settings_.screen_reader_support && ImGui::IsItemHovered()) {
            char desc[256];
            snprintf(desc, sizeof(desc), "Progress: %.1f%%", fraction * 100.0f);
            if (overlay) {
                snprintf(desc, sizeof(desc), "Progress: %s (%.1f%%)", overlay, fraction * 100.0f);
            }
            AddToAccessibilityDescription(desc);
        }
    }

    // 색상 조정 (색맹 지원)
    ImU32 GetAccessibleColor(const std::string& semantic_name) {
        if (settings_.mode == AccessibilityMode::COLORBLIND_FRIENDLY) {
            if (semantic_name == "primary") return colorblind_palette_.primary;
            if (semantic_name == "secondary") return colorblind_palette_.secondary;
            if (semantic_name == "success") return colorblind_palette_.success;
            if (semantic_name == "warning") return colorblind_palette_.warning;
            if (semantic_name == "danger") return colorblind_palette_.danger;
            if (semantic_name == "background") return colorblind_palette_.background;
            if (semantic_name == "text") return colorblind_palette_.text;
        }

        // 기본 색상 반환
        return IM_COL32_WHITE;
    }

    // 스크린 리더 설명 추가
    void AddToAccessibilityDescription(const std::string& description) {
        if (settings_.screen_reader_support) {
            // 실제 구현에서는 OS의 접근성 API를 통해 스크린 리더에 정보 전달
            // Windows: MSAA, UI Automation
            // macOS: NSAccessibility
            // Linux: AT-SPI
        }
    }

private:
    void ApplyAccessibilitySettings() {
        switch (settings_.mode) {
            case AccessibilityMode::HIGH_CONTRAST:
                EnableHighContrast(true);
                break;
            case AccessibilityMode::LARGE_TEXT:
                SetTextScale(1.5f);
                SetUIScale(1.2f);
                break;
            case AccessibilityMode::SCREEN_READER:
                settings_.screen_reader_support = true;
                settings_.focus_indicators = true;
                break;
            case AccessibilityMode::COLORBLIND_FRIENDLY:
                ApplyColorblindTheme();
                break;
            default:
                break;
        }
    }

    void ApplyTextScaling() {
        ImGuiIO& io = ImGui::GetIO();
        io.FontGlobalScale = settings_.text_scale;
    }

    void ApplyUIScaling() {
        ImGuiStyle& style = ImGui::GetStyle();
        style.ScaleAllSizes(settings_.ui_scale);
    }

    void ApplyHighContrastTheme() {
        if (!settings_.high_contrast) return;

        ImGuiStyle& style = ImGui::GetStyle();

        // 고대비 색상 설정
        style.Colors[ImGuiCol_WindowBg] = ImVec4(0.0f, 0.0f, 0.0f, 1.0f);
        style.Colors[ImGuiCol_Text] = ImVec4(1.0f, 1.0f, 1.0f, 1.0f);
        style.Colors[ImGuiCol_Button] = ImVec4(0.2f, 0.2f, 0.2f, 1.0f);
        style.Colors[ImGuiCol_ButtonHovered] = ImVec4(0.4f, 0.4f, 0.4f, 1.0f);
        style.Colors[ImGuiCol_ButtonActive] = ImVec4(0.6f, 0.6f, 0.6f, 1.0f);
        style.Colors[ImGuiCol_FrameBg] = ImVec4(0.1f, 0.1f, 0.1f, 1.0f);
        style.Colors[ImGuiCol_FrameBgHovered] = ImVec4(0.3f, 0.3f, 0.3f, 1.0f);
        style.Colors[ImGuiCol_FrameBgActive] = ImVec4(0.5f, 0.5f, 0.5f, 1.0f);
    }

    void ApplyColorblindTheme() {
        // 색맹 친화적 테마 적용
        // 주로 파란색과 주황색을 기반으로 한 색상 팔레트 사용
    }

    ImU32 AdjustColorForHighContrast(ImU32 color) {
        if (!settings_.high_contrast) return color;

        // 색상의 명도 조정
        float r, g, b, a;
        ImGui::ColorConvertU32ToFloat4(color, &r, &g, &b, &a);

        // 명도 계산
        float luminance = 0.299f * r + 0.587f * g + 0.114f * b;

        // 명도가 0.5보다 작으면 더 어둡게, 크면 더 밝게
        if (luminance < 0.5f) {
            r = g = b = 0.0f;  // 검은색
        } else {
            r = g = b = 1.0f;  // 흰색
        }

        return ImGui::ColorConvertFloat4ToU32(ImVec4(r, g, b, a));
    }
};

} // namespace SemiconductorHMI::Accessibility
```

### 실습 4: 외부 시스템 통합 및 실시간 데이터 동기화 (25분)

#### 4.1 MQTT 브로커 통합

```cpp
// MQTTIntegration.h
#pragma once
#include <mosquitto.h>
#include <json/json.h>
#include <thread>
#include <mutex>
#include <queue>
#include <atomic>
#include <functional>

namespace SemiconductorHMI::Integration {

struct MQTTMessage {
    std::string topic;
    std::string payload;
    int qos;
    bool retain;
    std::chrono::system_clock::time_point timestamp;
};

class MQTTClient {
private:
    struct mosquitto* mosq_ = nullptr;
    std::string client_id_;
    std::string broker_host_;
    int broker_port_ = 1883;
    std::string username_;
    std::string password_;

    std::atomic<bool> connected_{false};
    std::atomic<bool> running_{false};

    // 메시지 큐
    std::queue<MQTTMessage> incoming_messages_;
    std::queue<MQTTMessage> outgoing_messages_;
    mutable std::mutex message_mutex_;

    // 콜백 함수들
    std::function<void(const std::string&, const std::string&)> message_callback_;
    std::function<void(bool)> connection_callback_;

    std::thread worker_thread_;

public:
    MQTTClient(const std::string& client_id) : client_id_(client_id) {
        mosquitto_lib_init();
        mosq_ = mosquitto_new(client_id.c_str(), true, this);

        if (mosq_) {
            mosquitto_connect_callback_set(mosq_, OnConnect);
            mosquitto_disconnect_callback_set(mosq_, OnDisconnect);
            mosquitto_message_callback_set(mosq_, OnMessage);
            mosquitto_publish_callback_set(mosq_, OnPublish);
        }
    }

    ~MQTTClient() {
        Disconnect();
        if (mosq_) {
            mosquitto_destroy(mosq_);
        }
        mosquitto_lib_cleanup();
    }

    bool Connect(const std::string& host, int port = 1883,
                const std::string& username = "", const std::string& password = "") {
        broker_host_ = host;
        broker_port_ = port;
        username_ = username;
        password_ = password;

        if (!username.empty()) {
            mosquitto_username_pw_set(mosq_, username.c_str(), password.c_str());
        }

        int result = mosquitto_connect(mosq_, host.c_str(), port, 60);
        if (result == MOSQ_ERR_SUCCESS) {
            running_ = true;
            worker_thread_ = std::thread(&MQTTClient::WorkerLoop, this);
            return true;
        }

        return false;
    }

    void Disconnect() {
        if (running_) {
            running_ = false;
            mosquitto_disconnect(mosq_);

            if (worker_thread_.joinable()) {
                worker_thread_.join();
            }
        }
    }

    bool IsConnected() const {
        return connected_.load();
    }

    // 구독/발행
    bool Subscribe(const std::string& topic, int qos = 0) {
        if (!connected_) return false;
        return mosquitto_subscribe(mosq_, nullptr, topic.c_str(), qos) == MOSQ_ERR_SUCCESS;
    }

    bool Publish(const std::string& topic, const std::string& payload,
                int qos = 0, bool retain = false) {
        std::lock_guard<std::mutex> lock(message_mutex_);
        outgoing_messages_.push({topic, payload, qos, retain, std::chrono::system_clock::now()});
        return true;
    }

    // 장비 데이터 발행 (JSON 형태)
    bool PublishEquipmentData(const std::string& equipment_id,
                             const std::string& parameter,
                             double value,
                             const std::string& unit,
                             uint32_t quality = 100) {
        Json::Value data;
        data["equipment_id"] = equipment_id;
        data["parameter"] = parameter;
        data["value"] = value;
        data["unit"] = unit;
        data["quality"] = quality;
        data["timestamp"] = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();

        Json::StreamWriterBuilder builder;
        std::string json_string = Json::writeString(builder, data);

        std::string topic = "semiconductor/equipment/" + equipment_id + "/" + parameter;
        return Publish(topic, json_string, 1);
    }

    // 알람 발행
    bool PublishAlarm(const std::string& equipment_id,
                     const std::string& alarm_type,
                     const std::string& message,
                     int severity = 1) {
        Json::Value alarm;
        alarm["equipment_id"] = equipment_id;
        alarm["type"] = alarm_type;
        alarm["message"] = message;
        alarm["severity"] = severity;
        alarm["timestamp"] = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();

        Json::StreamWriterBuilder builder;
        std::string json_string = Json::writeString(builder, alarm);

        std::string topic = "semiconductor/alarms/" + equipment_id;
        return Publish(topic, json_string, 2, true);  // QoS 2, retain
    }

    // 콜백 설정
    void SetMessageCallback(std::function<void(const std::string&, const std::string&)> callback) {
        message_callback_ = callback;
    }

    void SetConnectionCallback(std::function<void(bool)> callback) {
        connection_callback_ = callback;
    }

    // 메시지 처리
    std::vector<MQTTMessage> GetPendingMessages() {
        std::lock_guard<std::mutex> lock(message_mutex_);
        std::vector<MQTTMessage> messages;

        while (!incoming_messages_.empty()) {
            messages.push_back(incoming_messages_.front());
            incoming_messages_.pop();
        }

        return messages;
    }

private:
    void WorkerLoop() {
        while (running_) {
            // 네트워크 루프
            mosquitto_loop(mosq_, 10, 1);

            // 송신 메시지 처리
            ProcessOutgoingMessages();

            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }

    void ProcessOutgoingMessages() {
        std::lock_guard<std::mutex> lock(message_mutex_);

        while (!outgoing_messages_.empty()) {
            const auto& msg = outgoing_messages_.front();

            mosquitto_publish(mosq_, nullptr,
                            msg.topic.c_str(),
                            msg.payload.length(),
                            msg.payload.c_str(),
                            msg.qos,
                            msg.retain);

            outgoing_messages_.pop();
        }
    }

    // MQTT 콜백들
    static void OnConnect(struct mosquitto* mosq, void* userdata, int result) {
        MQTTClient* client = static_cast<MQTTClient*>(userdata);
        client->connected_ = (result == 0);

        if (client->connection_callback_) {
            client->connection_callback_(client->connected_);
        }
    }

    static void OnDisconnect(struct mosquitto* mosq, void* userdata, int result) {
        MQTTClient* client = static_cast<MQTTClient*>(userdata);
        client->connected_ = false;

        if (client->connection_callback_) {
            client->connection_callback_(false);
        }
    }

    static void OnMessage(struct mosquitto* mosq, void* userdata,
                         const struct mosquitto_message* message) {
        MQTTClient* client = static_cast<MQTTClient*>(userdata);

        std::string topic(message->topic);
        std::string payload(static_cast<char*>(message->payload), message->payloadlen);

        {
            std::lock_guard<std::mutex> lock(client->message_mutex_);
            client->incoming_messages_.push({
                topic, payload, message->qos, message->retain,
                std::chrono::system_clock::now()
            });
        }

        if (client->message_callback_) {
            client->message_callback_(topic, payload);
        }
    }

    static void OnPublish(struct mosquitto* mosq, void* userdata, int mid) {
        // 발행 완료 처리
    }
};

} // namespace SemiconductorHMI::Integration
```

---

## 🚀 Hands-on 프로젝트 (45분): 완전한 산업용 HMI 플랫폼 구축

### 프로젝트: "차세대 반도체 팹 통합 모니터링 시스템"

#### 최종 통합 애플리케이션

```cpp
// AdvancedIndustrialHMIPlatform.cpp
#include "PluginInterface.h"
#include "DataVisualizationEngine.h"
#include "ThreadSafeRenderer.h"
#include "InternationalizationSystem.h"
#include "AccessibilitySystem.h"
#include "MQTTIntegration.h"
#include <imgui.h>
#include <memory>
#include <vector>

namespace SemiconductorHMI {

class AdvancedIndustrialHMIPlatform {
private:
    // 핵심 시스템들
    std::unique_ptr<Plugin::PluginManager> plugin_manager_;
    std::unique_ptr<Threading::MultiThreadedRenderer> thread_renderer_;
    std::unique_ptr<I18n::LocalizationManager> localization_manager_;
    std::unique_ptr<Accessibility::AccessibilityManager> accessibility_manager_;
    std::unique_ptr<Integration::MQTTClient> mqtt_client_;

    // 데이터 관리
    std::unordered_map<std::string, std::unique_ptr<Visualization::TimeSeriesBuffer>> data_buffers_;

    // UI 상태
    bool show_demo_window_ = false;
    bool show_plugin_manager_ = false;
    bool show_settings_ = false;
    bool show_accessibility_panel_ = false;

    // 시스템 상태
    struct SystemStatus {
        bool mqtt_connected = false;
        int active_plugins = 0;
        float cpu_usage = 0.0f;
        float memory_usage = 0.0f;
        int active_connections = 0;
    } status_;

public:
    AdvancedIndustrialHMIPlatform() {
        Initialize();
    }

    ~AdvancedIndustrialHMIPlatform() {
        Shutdown();
    }

    bool Initialize() {
        // 멀티스레드 렌더러 초기화
        thread_renderer_ = std::make_unique<Threading::MultiThreadedRenderer>(4);

        // 플러그인 매니저 초기화
        plugin_manager_ = std::make_unique<Plugin::PluginManager>();
        plugin_manager_->AddPluginDirectory("./plugins");
        plugin_manager_->AddPluginDirectory("./equipment_plugins");

        // 국제화 시스템 초기화
        localization_manager_ = std::make_unique<I18n::LocalizationManager>();
        localization_manager_->SetLanguage(I18n::Language::KOREAN);

        // 접근성 시스템 초기화
        accessibility_manager_ = std::make_unique<Accessibility::AccessibilityManager>();
        accessibility_manager_->Initialize();

        // MQTT 클라이언트 초기화
        mqtt_client_ = std::make_unique<Integration::MQTTClient>("HMI_Platform_" +
                                                               std::to_string(std::time(nullptr)));

        // MQTT 콜백 설정
        mqtt_client_->SetConnectionCallback([this](bool connected) {
            status_.mqtt_connected = connected;
            if (connected) {
                SubscribeToEquipmentTopics();
            }
        });

        mqtt_client_->SetMessageCallback([this](const std::string& topic, const std::string& payload) {
            ProcessMQTTMessage(topic, payload);
        });

        // 데이터 버퍼 초기화
        InitializeDataBuffers();

        // 플러그인 로드
        plugin_manager_->ScanAndLoadPlugins();

        return true;
    }

    void Run() {
        while (true) {
            Update();
            Render();

            // VSync 대기
            if (thread_renderer_->IsVSyncEnabled()) {
                thread_renderer_->WaitForFrame();
            }
        }
    }

    void Update() {
        // 플러그인 업데이트
        plugin_manager_->UpdateAllPlugins(ImGui::GetIO().DeltaTime);

        // MQTT 메시지 처리
        ProcessPendingMQTTMessages();

        // 시스템 상태 업데이트
        UpdateSystemStatus();
    }

    void Render() {
        // 메인 메뉴바
        RenderMainMenuBar();

        // 메인 도킹 공간
        RenderMainDockSpace();

        // 시스템 창들
        if (show_plugin_manager_) RenderPluginManager();
        if (show_settings_) RenderSettings();
        if (show_accessibility_panel_) RenderAccessibilityPanel();

        // 플러그인 렌더링
        plugin_manager_->RenderAllPlugins();

        // 상태바
        RenderStatusBar();

        // 프레임 완료
        thread_renderer_->CompleteFrame();
    }

private:
    void InitializeDataBuffers() {
        // 장비별 데이터 버퍼 생성
        std::vector<std::string> equipment_ids = {"CVD001", "PVD002", "ETCH003", "CMP004"};
        std::vector<std::string> parameters = {"temperature", "pressure", "flow_rate", "power"};

        for (const auto& eq_id : equipment_ids) {
            for (const auto& param : parameters) {
                std::string key = eq_id + "_" + param;
                data_buffers_[key] = std::make_unique<Visualization::TimeSeriesBuffer>(50000);
            }
        }
    }

    void SubscribeToEquipmentTopics() {
        mqtt_client_->Subscribe("semiconductor/equipment/+/+", 1);
        mqtt_client_->Subscribe("semiconductor/alarms/+", 2);
        mqtt_client_->Subscribe("semiconductor/system/status", 1);
    }

    void ProcessMQTTMessage(const std::string& topic, const std::string& payload) {
        try {
            Json::Value data;
            Json::Reader reader;

            if (reader.parse(payload, data)) {
                if (topic.find("semiconductor/equipment/") == 0) {
                    ProcessEquipmentData(data);
                } else if (topic.find("semiconductor/alarms/") == 0) {
                    ProcessAlarmData(data);
                } else if (topic.find("semiconductor/system/") == 0) {
                    ProcessSystemData(data);
                }
            }
        } catch (const std::exception& e) {
            // 로깅: JSON 파싱 오류
        }
    }

    void ProcessEquipmentData(const Json::Value& data) {
        std::string equipment_id = data.get("equipment_id", "").asString();
        std::string parameter = data.get("parameter", "").asString();
        double value = data.get("value", 0.0).asDouble();
        uint32_t quality = data.get("quality", 100).asUInt();
        int64_t timestamp = data.get("timestamp", 0).asInt64();

        std::string key = equipment_id + "_" + parameter;
        auto it = data_buffers_.find(key);
        if (it != data_buffers_.end()) {
            double time_seconds = timestamp / 1000.0;
            it->second->AddPoint({time_seconds, value, quality});
        }
    }

    void ProcessAlarmData(const Json::Value& data) {
        // 알람 처리 로직
        std::string equipment_id = data.get("equipment_id", "").asString();
        std::string type = data.get("type", "").asString();
        std::string message = data.get("message", "").asString();
        int severity = data.get("severity", 1).asInt();

        // 알람 로그에 추가 및 UI 업데이트
    }

    void ProcessSystemData(const Json::Value& data) {
        // 시스템 상태 데이터 처리
    }

    void ProcessPendingMQTTMessages() {
        auto messages = mqtt_client_->GetPendingMessages();
        for (const auto& msg : messages) {
            ProcessMQTTMessage(msg.topic, msg.payload);
        }
    }

    void UpdateSystemStatus() {
        status_.active_plugins = 0;  // 실제 활성 플러그인 수 계산
        // CPU 및 메모리 사용량 업데이트
        // 활성 연결 수 업데이트
    }

    void RenderMainMenuBar() {
        if (ImGui::BeginMainMenuBar()) {
            if (ImGui::BeginMenu(localization_manager_->GetText("menu.file").c_str())) {
                ImGui::MenuItem("새 프로젝트");
                ImGui::MenuItem("열기");
                ImGui::MenuItem("저장");
                ImGui::Separator();
                ImGui::MenuItem("종료");
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("플러그인")) {
                ImGui::MenuItem("플러그인 관리자", nullptr, &show_plugin_manager_);
                ImGui::MenuItem("플러그인 개발 도구");
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("도구")) {
                ImGui::MenuItem("데이터 내보내기");
                ImGui::MenuItem("보고서 생성");
                ImGui::MenuItem("시스템 진단");
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu(localization_manager_->GetText("menu.settings").c_str())) {
                ImGui::MenuItem("일반 설정", nullptr, &show_settings_);
                ImGui::MenuItem("접근성", nullptr, &show_accessibility_panel_);
                ImGui::MenuItem("네트워크 설정");
                ImGui::EndMenu();
            }

            // 언어 선택
            if (ImGui::BeginMenu("Language")) {
                if (ImGui::MenuItem("한국어")) {
                    localization_manager_->SetLanguage(I18n::Language::KOREAN);
                }
                if (ImGui::MenuItem("English")) {
                    localization_manager_->SetLanguage(I18n::Language::ENGLISH);
                }
                if (ImGui::MenuItem("日本語")) {
                    localization_manager_->SetLanguage(I18n::Language::JAPANESE);
                }
                ImGui::EndMenu();
            }

            ImGui::EndMainMenuBar();
        }
    }

    void RenderMainDockSpace() {
        static bool first_time = true;
        static ImGuiID dockspace_id;

        ImGuiWindowFlags window_flags = ImGuiWindowFlags_NoBringToFrontOnFocus |
                                       ImGuiWindowFlags_NoNavFocus |
                                       ImGuiWindowFlags_NoTitleBar |
                                       ImGuiWindowFlags_NoCollapse |
                                       ImGuiWindowFlags_NoResize |
                                       ImGuiWindowFlags_NoMove;

        ImGuiViewport* viewport = ImGui::GetMainViewport();
        ImGui::SetNextWindowPos(viewport->WorkPos);
        ImGui::SetNextWindowSize(viewport->WorkSize);
        ImGui::SetNextWindowViewport(viewport->ID);

        ImGui::Begin("DockSpace", nullptr, window_flags);

        dockspace_id = ImGui::GetID("MainDockSpace");
        ImGui::DockSpace(dockspace_id, ImVec2(0.0f, 0.0f), ImGuiDockNodeFlags_None);

        if (first_time) {
            first_time = false;
            SetupDefaultLayout(dockspace_id);
        }

        ImGui::End();
    }

    void SetupDefaultLayout(ImGuiID dockspace_id) {
        // 기본 레이아웃 설정
        ImGui::DockBuilderRemoveNode(dockspace_id);
        ImGui::DockBuilderAddNode(dockspace_id, ImGuiDockNodeFlags_DockSpace);
        ImGui::DockBuilderSetNodeSize(dockspace_id, ImGui::GetMainViewport()->Size);

        auto dock_left = ImGui::DockBuilderSplitNode(dockspace_id, ImGuiDir_Left, 0.25f, nullptr, &dockspace_id);
        auto dock_bottom = ImGui::DockBuilderSplitNode(dockspace_id, ImGuiDir_Down, 0.3f, nullptr, &dockspace_id);

        ImGui::DockBuilderDockWindow("Equipment List", dock_left);
        ImGui::DockBuilderDockWindow("Alarms", dock_bottom);
        ImGui::DockBuilderDockWindow("CVD Equipment Monitor", dockspace_id);

        ImGui::DockBuilderFinish(dockspace_id);
    }

    void RenderPluginManager() {
        ImGui::Begin("플러그인 관리자", &show_plugin_manager_);

        if (ImGui::Button("플러그인 새로고침")) {
            plugin_manager_->ScanAndLoadPlugins();
        }

        ImGui::SameLine();
        if (ImGui::Button("플러그인 폴더 열기")) {
            // 시스템 파일 탐색기로 플러그인 폴더 열기
        }

        ImGui::Separator();

        // 로드된 플러그인 목록 표시
        ImGui::Text("로드된 플러그인: %d개", status_.active_plugins);

        ImGui::End();
    }

    void RenderSettings() {
        ImGui::Begin("설정", &show_settings_);

        if (ImGui::BeginTabBar("SettingsTabs")) {
            if (ImGui::BeginTabItem("일반")) {
                ImGui::Text("일반 설정");
                ImGui::EndTabItem();
            }

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
- 실제 반도체 팹 환경 시뮬레이션
- 최종 프로젝트 발표 및 평가