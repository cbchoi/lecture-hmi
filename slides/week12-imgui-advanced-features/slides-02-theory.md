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

### 실습 2: 고급 데이터 시각화 대시보드 구현

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

## 🔬 심화 실습: 멀티스레딩 통합 및 외부 시스템 연동

### 실습 3: 국제화 및 접근성 지원 시스템

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
