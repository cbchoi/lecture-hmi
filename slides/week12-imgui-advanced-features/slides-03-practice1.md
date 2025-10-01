
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

### 실습 4: 외부 시스템 통합 및 실시간 데이터 동기화

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

## 🚀 Hands-on 프로젝트: 완전한 산업용 HMI 플랫폼 구축

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
