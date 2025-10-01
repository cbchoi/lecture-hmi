# Week 12: ImGUI C++ 고급 기능 - 플러그인 시스템 및 확장성

## 🎯 이번 주 학습 목표
1. **플러그인 아키텍처**: 동적 로딩 시스템 및 모듈화 설계
2. **고급 데이터 시각화**: BigData 처리 및 실시간 차트 엔진
3. **멀티스레딩 통합**: 동시성 제어 및 비동기 처리
4. **국제화 및 확장성**: 글로벌 HMI 플랫폼 구축

---

## 📚 이론 강의: 플러그인 아키텍처 및 확장성 설계

### 1. 플러그인 아키텍처 설계

#### 1.1 플러그인 인터페이스 정의

<div class="grid grid-cols-2 gap-8">
<div>

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
    virtual std::vector<std::string>
        GetDependencies() const = 0;

    // 라이프사이클 관리
    virtual bool Initialize() = 0;
    virtual void Shutdown() = 0;
    virtual bool IsInitialized() const = 0;

    // ImGUI 통합
    virtual void OnUpdate(float deltaTime) = 0;
    virtual void OnRender() = 0;
    virtual void OnImGuiRender() = 0;
};
```

</div>
<div>

**IPlugin 인터페이스 설명**:

**메타데이터 메서드**:
- `GetName()`: 플러그인 고유 이름
- `GetVersion()`: 버전 정보 (예: "1.0.0")
- `GetDescription()`: 플러그인 설명
- `GetDependencies()`: 의존하는 다른 플러그인 목록

**라이프사이클 메서드**:
- `Initialize()`: 플러그인 초기화
  - 리소스 할당
  - 설정 파일 로드
  - 의존성 확인
- `Shutdown()`: 플러그인 정리
  - 리소스 해제
  - 연결 종료
- `IsInitialized()`: 초기화 상태 확인

**ImGUI 통합 메서드**:
- `OnUpdate(deltaTime)`: 프레임마다 호출
  - 로직 업데이트
  - 데이터 처리
- `OnRender()`: 렌더링 전 호출
- `OnImGuiRender()`: ImGUI 렌더링
  - UI 그리기
  - 사용자 입력 처리

</div>
</div>

---

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
// 위젯 플러그인 인터페이스
class IWidgetPlugin : public IPlugin {
public:
    virtual void RenderWidget(
        const char* name,
        bool* open = nullptr) = 0;
    virtual ImVec2 GetPreferredSize() const = 0;
    virtual bool IsResizable() const = 0;
};

// 데이터 소스 플러그인 인터페이스
class IDataSourcePlugin : public IPlugin {
public:
    virtual bool Connect(
        const std::string& connectionString) = 0;
    virtual void Disconnect() = 0;
    virtual bool IsConnected() const = 0;
    virtual std::vector<uint8_t> ReadData() = 0;
    virtual bool WriteData(
        const std::vector<uint8_t>& data) = 0;
};

// 플러그인 팩토리
class IPluginFactory {
public:
    virtual ~IPluginFactory() = default;
    virtual std::unique_ptr<IPlugin>
        CreatePlugin() = 0;
    virtual std::string GetPluginType() const = 0;
};

} // namespace SemiconductorHMI::Plugin
```

</div>
<div>

**IWidgetPlugin (위젯 플러그인)**:
- `RenderWidget()`: 위젯 UI 렌더링
  - `name`: 윈도우 이름
  - `open`: 닫기 버튼 처리
- `GetPreferredSize()`: 기본 크기 반환
- `IsResizable()`: 크기 조절 가능 여부

**사용 예시**:
```cpp
class CustomGaugePlugin : public IWidgetPlugin {
    void RenderWidget(const char* name, bool* open) {
        ImGui::Begin(name, open);
        // 게이지 렌더링
        DrawCircularGauge();
        ImGui::End();
    }

    ImVec2 GetPreferredSize() const {
        return ImVec2(300, 300);
    }
};
```

**IDataSourcePlugin (데이터 소스)**:
- `Connect()`: 데이터 소스 연결
  - MQTT, OPC-UA, Modbus 등
- `ReadData()`: 데이터 읽기
- `WriteData()`: 데이터 쓰기
- 실시간 장비 통신에 사용

**IPluginFactory (팩토리)**:
- 플러그인 인스턴스 생성
- 타입 정보 제공
- DLL 내보내기 함수로 사용

</div>
</div>
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

### 2. 고급 데이터 시각화 엔진

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

### 3. 멀티스레딩 및 동시성 제어

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

## 🛠️ 기초 실습: 플러그인 시스템 및 고급 차트 개발

### 실습 1: 반도체 장비 모니터링 플러그인 개발

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
