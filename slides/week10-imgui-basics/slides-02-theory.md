---
layout: cover
---

# Week 10 - ImGUI 기초 + C++ 고급 기법
## 이론 강의 (120분)

RAII, Smart Pointers, Move Semantics를 활용한 안전한 리소스 관리

---

# 1. RAII 패턴 (Resource Acquisition Is Initialization)

## 1.1 RAII 기본 개념

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
// ❌ 나쁜 예: 수동 리소스 관리
class BadFileHandler {
private:
    FILE* file;

public:
    BadFileHandler(const char* filename) {
        file = fopen(filename, "r");
        if (!file) {
            throw std::runtime_error("Failed to open file");
        }
    }

    ~BadFileHandler() {
        // ❌ 예외 발생 시 누수 가능
        if (file) {
            fclose(file);
        }
    }

    void Process() {
        char buffer[1024];
        // ❌ 예외 발생 시 파일이 닫히지 않음
        if (fgets(buffer, sizeof(buffer), file) == nullptr) {
            throw std::runtime_error("Read error");
        }
    }
};
```

```cpp
// ✅ 좋은 예: RAII 패턴 적용
class GoodFileHandler {
private:
    std::unique_ptr<FILE, decltype(&fclose)> file;

public:
    GoodFileHandler(const char* filename)
        : file(fopen(filename, "r"), &fclose) {
        if (!file) {
            throw std::runtime_error("Failed to open file");
        }
    }

    // ✅ 소멸자가 자동 호출 (예외 발생해도)
    // file의 unique_ptr가 자동으로 fclose 호출

    void Process() {
        char buffer[1024];
        // ✅ 예외 발생해도 스택 해제 시 파일 자동 닫힘
        if (fgets(buffer, sizeof(buffer), file.get()) == nullptr) {
            throw std::runtime_error("Read error");
        }
    }
};
```

</div>
<div>

**RAII (Resource Acquisition Is Initialization) 패턴**:

1. **핵심 원칙**
   - 리소스 획득 = 객체 초기화
   - 리소스 해제 = 객체 소멸
   - 스택 기반 자동 생명주기 관리

2. **RAII가 관리하는 리소스**
   - 파일 핸들 (FILE*, fstream)
   - 메모리 (new/delete)
   - 뮤텍스 락 (std::lock_guard)
   - 네트워크 소켓
   - OpenGL 리소스 (텍스처, 버퍼)

3. **RAII 장점**
   - **예외 안전성**: 예외 발생 시에도 자동 정리
   - **누수 방지**: 명시적 해제 불필요
   - **가독성**: 리소스 생명주기가 명확
   - **RAII vs finally**: C++는 finally 없음 → RAII 사용

**반도체 HMI 적용**:
```cpp
// 장비 통신 포트 관리
class SerialPort {
    int fd;
public:
    SerialPort(const char* device) {
        fd = open(device, O_RDWR);
        if (fd < 0) throw std::runtime_error("Open failed");
        // 포트 설정...
    }
    ~SerialPort() {
        if (fd >= 0) close(fd);  // 자동 닫힘
    }
};

{
    SerialPort port("/dev/ttyUSB0");
    port.Write(command);
    // 예외 발생해도 포트 자동 닫힘
} // SerialPort 소멸자 자동 호출
```

**주의사항**:
- ❌ 소멸자에서 예외 던지지 말 것
- ✅ 복사 방지 또는 이동 의미론 구현
- ✅ Rule of Five 준수 (소멸자 정의 시)

</div>
</div>

---

## 1.2 OpenGL 리소스 RAII 관리

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
// OpenGL 텍스처 RAII 래퍼
class GLTexture {
private:
    GLuint texture_id = 0;
    int width, height;

public:
    GLTexture(int w, int h, GLenum format = GL_RGBA)
        : width(w), height(h) {
        // 리소스 획득 (생성자)
        glGenTextures(1, &texture_id);
        glBindTexture(GL_TEXTURE_2D, texture_id);
        glTexImage2D(GL_TEXTURE_2D, 0, format,
                     width, height, 0, format,
                     GL_UNSIGNED_BYTE, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    }

    ~GLTexture() {
        // 리소스 해제 (소멸자)
        if (texture_id != 0) {
            glDeleteTextures(1, &texture_id);
        }
    }

    // 복사 방지 (리소스는 하나만)
    GLTexture(const GLTexture&) = delete;
    GLTexture& operator=(const GLTexture&) = delete;

    // 이동 허용 (소유권 이전)
    GLTexture(GLTexture&& other) noexcept
        : texture_id(other.texture_id)
        , width(other.width)
        , height(other.height) {
        other.texture_id = 0;  // 원본 무효화
    }

    GLTexture& operator=(GLTexture&& other) noexcept {
        if (this != &other) {
            // 기존 리소스 해제
            if (texture_id != 0) {
                glDeleteTextures(1, &texture_id);
            }
            // 소유권 이전
            texture_id = other.texture_id;
            width = other.width;
            height = other.height;
            other.texture_id = 0;
        }
        return *this;
    }

    // 접근자
    GLuint GetID() const { return texture_id; }
    int GetWidth() const { return width; }
    int GetHeight() const { return height; }

    // 텍스처 업데이트
    void UpdateData(const void* data) {
        glBindTexture(GL_TEXTURE_2D, texture_id);
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0,
                        width, height, GL_RGBA,
                        GL_UNSIGNED_BYTE, data);
    }

    void Bind(int unit = 0) const {
        glActiveTexture(GL_TEXTURE0 + unit);
        glBindTexture(GL_TEXTURE_2D, texture_id);
    }
};
```

```cpp
// OpenGL VAO/VBO RAII 래퍼
class GLBuffer {
private:
    GLuint buffer_id = 0;
    GLenum target;
    size_t size_bytes;

public:
    GLBuffer(GLenum target_type)
        : target(target_type), size_bytes(0) {
        glGenBuffers(1, &buffer_id);
    }

    ~GLBuffer() {
        if (buffer_id != 0) {
            glDeleteBuffers(1, &buffer_id);
        }
    }

    // 복사/이동 (텍스처와 동일)
    GLBuffer(const GLBuffer&) = delete;
    GLBuffer& operator=(const GLBuffer&) = delete;
    GLBuffer(GLBuffer&& other) noexcept
        : buffer_id(other.buffer_id)
        , target(other.target)
        , size_bytes(other.size_bytes) {
        other.buffer_id = 0;
    }

    GLBuffer& operator=(GLBuffer&& other) noexcept {
        if (this != &other) {
            if (buffer_id != 0) {
                glDeleteBuffers(1, &buffer_id);
            }
            buffer_id = other.buffer_id;
            target = other.target;
            size_bytes = other.size_bytes;
            other.buffer_id = 0;
        }
        return *this;
    }

    template<typename T>
    void SetData(const std::vector<T>& data, GLenum usage = GL_STATIC_DRAW) {
        size_bytes = data.size() * sizeof(T);
        glBindBuffer(target, buffer_id);
        glBufferData(target, size_bytes, data.data(), usage);
    }

    void Bind() const {
        glBindBuffer(target, buffer_id);
    }

    GLuint GetID() const { return buffer_id; }
};
```

```cpp
// 사용 예시: 웨이퍼 맵 렌더링
class WaferMapRenderer {
private:
    GLTexture wafer_texture;
    GLBuffer vertex_buffer;
    GLBuffer index_buffer;

public:
    WaferMapRenderer(int width, int height)
        : wafer_texture(width, height)
        , vertex_buffer(GL_ARRAY_BUFFER)
        , index_buffer(GL_ELEMENT_ARRAY_BUFFER) {

        // 정점 데이터 설정
        std::vector<float> vertices = {
            // x,    y,    u,   v
            -1.0f, -1.0f, 0.0f, 0.0f,
             1.0f, -1.0f, 1.0f, 0.0f,
             1.0f,  1.0f, 1.0f, 1.0f,
            -1.0f,  1.0f, 0.0f, 1.0f
        };
        vertex_buffer.SetData(vertices);

        std::vector<unsigned int> indices = {0, 1, 2, 2, 3, 0};
        index_buffer.SetData(indices);
    }

    // ✅ 소멸 시 모든 OpenGL 리소스 자동 해제
    // ~WaferMapRenderer() = default;

    void Render() {
        wafer_texture.Bind(0);
        vertex_buffer.Bind();
        index_buffer.Bind();
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0);
    }
};
```

</div>
<div>

**OpenGL RAII 패턴 설명**:

1. **생성자에서 리소스 획득**
   - `glGenTextures()` / `glGenBuffers()` 호출
   - 실패 시 예외 던지기
   - 초기 설정 완료

2. **소멸자에서 리소스 해제**
   - `glDeleteTextures()` / `glDeleteBuffers()` 호출
   - ID가 0인지 체크 (이중 해제 방지)
   - `noexcept` 보장 (소멸자는 예외 던지지 않음)

3. **복사 방지, 이동 허용**
   - **복사 금지**: OpenGL 리소스는 복제 불가
   - **이동 허용**: 소유권 이전 가능
   - 이동 후 원본 무효화 (`texture_id = 0`)

**이동 의미론 (Move Semantics)**:
```cpp
GLTexture CreateTexture() {
    GLTexture tex(1024, 1024);
    // ... 설정
    return tex;  // ✅ 이동 반환 (복사 없음)
}

GLTexture my_texture = CreateTexture();  // ✅ 이동 생성
```

**Rule of Five**:
```cpp
class GLResource {
    // 5가지 특수 멤버 함수 정의 필요
    ~GLResource();                          // 1. 소멸자
    GLResource(const GLResource&) = delete; // 2. 복사 생성자
    GLResource& operator=(const GLResource&) = delete; // 3. 복사 대입
    GLResource(GLResource&&) noexcept;      // 4. 이동 생성자
    GLResource& operator=(GLResource&&) noexcept; // 5. 이동 대입
};
```

**반도체 HMI 적용**:
- 웨이퍼 맵 텍스처 (수백 개)
- 그래프 버텍스 버퍼 (실시간 업데이트)
- 3D 장비 모델 메시
- → 모두 RAII로 자동 관리, 누수 없음

**성능 고려사항**:
- 이동은 O(1) (포인터 복사만)
- 복사 방지로 불필요한 GPU 리소스 생성 방지
- 스마트 포인터와 조합 시 더욱 강력

</div>
</div>

---

# 2. Smart Pointers (스마트 포인터)

## 2.1 unique_ptr - 단독 소유권

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <memory>
#include <vector>
#include <string>

// ❌ 나쁜 예: Raw pointer 사용
class BadUIComponent {
private:
    UIWidget* widget;  // ❌ 수동 메모리 관리

public:
    BadUIComponent() {
        widget = new UIWidget();  // ❌ new 사용
    }

    ~BadUIComponent() {
        delete widget;  // ❌ delete 잊으면 누수
    }

    // ❌ 복사 시 얕은 복사 문제
    // ❌ 예외 발생 시 누수
};
```

```cpp
// ✅ 좋은 예: unique_ptr 사용
class GoodUIComponent {
private:
    std::unique_ptr<UIWidget> widget;  // ✅ 자동 관리

public:
    GoodUIComponent()
        : widget(std::make_unique<UIWidget>()) {  // ✅ make_unique 사용
        // ✅ 예외 안전
    }

    // ✅ 소멸자 자동 생성 (unique_ptr가 자동 해제)
    // ~GoodUIComponent() = default;

    // ✅ 복사 자동 금지 (unique_ptr은 복사 불가)
    // ✅ 이동은 자동 지원

    void UpdateWidget(std::unique_ptr<UIWidget> new_widget) {
        widget = std::move(new_widget);  // ✅ 소유권 이전
        // 기존 widget 자동 삭제됨
    }

    UIWidget* GetWidget() const {
        return widget.get();  // ✅ raw pointer 반환 (관찰만)
    }
};
```

```cpp
// unique_ptr을 활용한 UI 컴포넌트 계층 구조
class UIComponent {
public:
    virtual ~UIComponent() = default;
    virtual void Render() = 0;
    virtual void Update(float dt) {}
};

class Panel : public UIComponent {
private:
    std::string name;
    std::vector<std::unique_ptr<UIComponent>> children;  // ✅ 자식 소유

public:
    explicit Panel(std::string panel_name)
        : name(std::move(panel_name)) {}

    // ✅ 소유권 이전 (이동)
    void AddChild(std::unique_ptr<UIComponent> child) {
        children.push_back(std::move(child));
    }

    // ✅ 팩토리 패턴
    template<typename T, typename... Args>
    T* CreateChild(Args&&... args) {
        auto child = std::make_unique<T>(std::forward<Args>(args)...);
        T* ptr = child.get();
        children.push_back(std::move(child));
        return ptr;  // ✅ 관찰 포인터 반환
    }

    void Render() override {
        ImGui::Begin(name.c_str());
        for (auto& child : children) {
            child->Render();  // ✅ -> 연산자 사용
        }
        ImGui::End();
    }

    ~Panel() override {
        // ✅ children의 모든 unique_ptr 자동 소멸
        // ✅ 역순으로 소멸 (스택처럼)
    }
};
```

```cpp
// 사용 예시
void CreateEquipmentUI() {
    auto main_panel = std::make_unique<Panel>("Equipment Monitor");

    // ✅ 자식 생성 및 추가
    main_panel->AddChild(std::make_unique<TemperatureWidget>());
    main_panel->AddChild(std::make_unique<PressureWidget>());

    // ✅ 팩토리 메서드 사용
    auto* status = main_panel->CreateChild<StatusWidget>("IDLE");
    status->SetColor(ImVec4(0, 1, 0, 1));

    // ✅ 스코프 종료 시 자동 삭제
    // - main_panel 삭제
    // - 모든 자식들 자동 삭제 (역순)
}
```

</div>
<div>

**unique_ptr 핵심 특징**:

1. **단독 소유권 (Exclusive Ownership)**
   - 한 시점에 하나의 unique_ptr만 객체 소유
   - 복사 불가능 (`= delete`)
   - 이동 가능 (소유권 이전)

2. **오버헤드 없음**
   - Raw pointer와 동일한 크기 (8바이트, 64비트)
   - 런타임 오버헤드 없음 (컴파일 타임 최적화)
   - 참조 카운팅 없음 (shared_ptr과 차이)

3. **예외 안전성**
   - `make_unique<T>(args...)` 사용 권장
   - 예외 발생 시 자동 정리
   - RAII 패턴과 완벽한 조합

**make_unique vs new**:
```cpp
// ❌ 나쁜 예: new 직접 사용
std::unique_ptr<Widget> w1(new Widget());

// 문제 상황:
foo(std::unique_ptr<Widget>(new Widget()), risky_function());
// risky_function()이 예외 던지면 Widget 누수 가능

// ✅ 좋은 예: make_unique 사용
auto w2 = std::make_unique<Widget>();

// 안전:
foo(std::make_unique<Widget>(), risky_function());
// 예외 발생해도 누수 없음 (순서 보장)
```

**unique_ptr API**:
```cpp
unique_ptr<T> ptr = make_unique<T>(args);

ptr.get();          // raw pointer 반환 (관찰)
ptr.reset();        // 객체 삭제, nullptr로 설정
ptr.reset(new T);   // 기존 삭제, 새 객체 소유
ptr.release();      // 소유권 포기, raw pointer 반환
ptr.operator*();    // 역참조
ptr.operator->();   // 멤버 접근
bool(ptr);          // nullptr 체크
```

**소유권 이전 패턴**:
```cpp
// 1. 함수 반환 (이동)
std::unique_ptr<Widget> CreateWidget() {
    return std::make_unique<Widget>();  // RVO + move
}

// 2. 컨테이너 저장
std::vector<std::unique_ptr<Widget>> widgets;
widgets.push_back(std::make_unique<Widget>());  // move

// 3. 함수 인자 (sink)
void TakeOwnership(std::unique_ptr<Widget> w) {
    // w가 소유권 가짐
}
TakeOwnership(std::move(my_widget));  // 명시적 이동
```

**반도체 HMI 적용**:
- UI 컴포넌트 계층 (Panel → Widget)
- 일시적 데이터 (센서 판독값 버퍼)
- 장비 상태 머신 (State 객체)

</div>
</div>

---

## 2.2 shared_ptr - 공유 소유권

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <memory>
#include <vector>
#include <unordered_map>
#include <string>

// shared_ptr 기본 사용
class Equipment {
private:
    std::string equipment_id;
    int status;

public:
    explicit Equipment(std::string id)
        : equipment_id(std::move(id)), status(0) {}

    void UpdateStatus(int new_status) {
        status = new_status;
    }

    const std::string& GetID() const { return equipment_id; }
    int GetStatus() const { return status; }

    ~Equipment() {
        std::cout << "Equipment " << equipment_id << " destroyed\n";
    }
};

// 여러 곳에서 Equipment를 공유하는 시스템
class EquipmentManager {
private:
    // Equipment 저장소 (원본)
    std::unordered_map<std::string, std::shared_ptr<Equipment>> equipments;

public:
    // Equipment 생성 및 저장
    std::shared_ptr<Equipment> CreateEquipment(const std::string& id) {
        auto equipment = std::make_shared<Equipment>(id);
        equipments[id] = equipment;
        return equipment;  // ✅ shared_ptr 복사 (ref count 증가)
    }

    // Equipment 조회
    std::shared_ptr<Equipment> GetEquipment(const std::string& id) {
        auto it = equipments.find(id);
        if (it != equipments.end()) {
            return it->second;  // ✅ shared_ptr 복사
        }
        return nullptr;
    }

    // Equipment 제거
    void RemoveEquipment(const std::string& id) {
        equipments.erase(id);
        // ✅ ref count 감소
        // ✅ 다른 곳에서 사용 중이면 아직 삭제 안 됨
    }

    size_t GetEquipmentCount() const {
        return equipments.size();
    }
};
```

```cpp
// 관찰자 패턴에서 shared_ptr 활용
class DataLogger {
private:
    std::shared_ptr<Equipment> equipment;  // ✅ 공유 소유권
    std::string log_file;

public:
    DataLogger(std::shared_ptr<Equipment> eq, std::string file)
        : equipment(eq)  // ✅ shared_ptr 복사 (ref count++)
        , log_file(std::move(file)) {}

    void LogStatus() {
        if (equipment) {  // ✅ nullptr 체크
            std::cout << "Logging " << equipment->GetID()
                      << ": " << equipment->GetStatus() << "\n";
        }
    }

    // ✅ DataLogger 소멸 시 ref count 감소
    // ✅ Equipment는 다른 곳에서 사용 중이면 유지됨
};

class UIDisplay {
private:
    std::shared_ptr<Equipment> equipment;  // ✅ 동일 Equipment 공유

public:
    UIDisplay(std::shared_ptr<Equipment> eq)
        : equipment(eq) {}  // ref count++

    void Render() {
        if (equipment) {
            ImGui::Text("Equipment: %s", equipment->GetID().c_str());
            ImGui::Text("Status: %d", equipment->GetStatus());
        }
    }
};
```

```cpp
// 사용 예시: 여러 시스템에서 Equipment 공유
void SharedEquipmentExample() {
    EquipmentManager manager;

    // Equipment 생성 (ref count = 1)
    auto chamber_a = manager.CreateEquipment("CHAMBER-A");
    std::cout << "Ref count: " << chamber_a.use_count() << "\n";  // 2 (manager + chamber_a)

    {
        // 여러 시스템에서 공유
        DataLogger logger(chamber_a, "chamber_a.log");  // ref count = 3
        UIDisplay display(chamber_a);                   // ref count = 4

        std::cout << "Ref count: " << chamber_a.use_count() << "\n";  // 4

        chamber_a->UpdateStatus(1);  // 모든 곳에서 동일한 객체 보임

        logger.LogStatus();  // "Logging CHAMBER-A: 1"
        display.Render();    // UI에도 Status: 1 표시

    }  // ✅ logger, display 소멸 → ref count = 2

    std::cout << "Ref count: " << chamber_a.use_count() << "\n";  // 2

    manager.RemoveEquipment("CHAMBER-A");  // ref count = 1
    std::cout << "Ref count: " << chamber_a.use_count() << "\n";  // 1

}  // ✅ chamber_a 소멸 → ref count = 0 → Equipment 삭제
```

```cpp
// shared_ptr 성능 고려사항
class PerformanceSensitiveCode {
private:
    std::shared_ptr<HeavyData> data;

public:
    // ✅ const& 전달 (ref count 증가 없음)
    void ProcessData(const std::shared_ptr<HeavyData>& data_ref) {
        // 읽기만 하는 경우 복사 불필요
        std::cout << data_ref->GetSize() << "\n";
    }

    // ✅ 소유권 필요 시에만 복사
    void StoreData(std::shared_ptr<HeavyData> data_copy) {
        data = std::move(data_copy);  // ✅ 이동으로 ref count 증가 회피
    }

    // ❌ 값 전달 (ref count 증가/감소 오버헤드)
    void BadProcessData(std::shared_ptr<HeavyData> data_copy) {
        // ref count 원자적 연산 (느림)
    }
};
```

</div>
<div>

**shared_ptr 핵심 특징**:

1. **공유 소유권 (Shared Ownership)**
   - 여러 shared_ptr가 동일 객체 소유 가능
   - 복사 가능 (참조 카운트 증가)
   - 마지막 shared_ptr 소멸 시 객체 삭제

2. **참조 카운팅 (Reference Counting)**
   - **Control Block** 사용 (heap 할당)
   - 강한 참조 카운트 (strong count)
   - 약한 참조 카운트 (weak count, weak_ptr용)
   - 원자적 연산 (atomic, 멀티스레드 안전)

3. **오버헤드**
   - 크기: 16바이트 (포인터 2개)
     - 객체 포인터 (8바이트)
     - Control block 포인터 (8바이트)
   - 성능:
     - 복사/소멸 시 원자적 증감 (atomic increment/decrement)
     - make_shared 사용 시 한 번의 할당
     - new 사용 시 두 번의 할당 (객체 + control block)

**make_shared vs new**:
```cpp
// ❌ 나쁜 예: new 사용 (할당 2회)
auto p1 = std::shared_ptr<Widget>(new Widget());
// 1. new Widget() - Widget 할당
// 2. shared_ptr 생성 - Control block 할당

// ✅ 좋은 예: make_shared (할당 1회)
auto p2 = std::make_shared<Widget>();
// Widget + Control block을 한 번에 할당 (효율적)
```

**shared_ptr API**:
```cpp
shared_ptr<T> p = make_shared<T>(args);

p.use_count();      // 참조 카운트 조회
p.unique();         // use_count() == 1 체크
p.reset();          // 참조 해제
p.reset(new T);     // 새 객체 소유
p.get();            // raw pointer 반환
p.operator*();      // 역참조
p.operator->();     // 멤버 접근
```

**순환 참조 문제**:
```cpp
// ❌ 순환 참조 → 메모리 누수
class Node {
    std::shared_ptr<Node> next;  // ❌ 순환 참조
    std::shared_ptr<Node> prev;  // ❌ 순환 참조
};

Node* a = new Node();
Node* b = new Node();
a->next = b;  // a → b
b->prev = a;  // b → a
// ref count 영원히 0이 안 됨!

// ✅ weak_ptr로 해결 (다음 슬라이드)
```

**반도체 HMI 적용**:
- 여러 UI에서 동일 장비 데이터 공유
- 레시피 객체 (여러 프로세스에서 참조)
- 로그 시스템 (장비 정보 공유)
- 캐시 시스템 (동일 데이터 중복 제거)

**사용 가이드**:
- ✅ 소유권 명확히 구분 (unique vs shared)
- ✅ const& 전달로 불필요한 ref count 증가 방지
- ✅ make_shared 사용으로 성능 최적화
- ❌ shared_ptr 남용 주의 (대부분은 unique_ptr 충분)

</div>
</div>

---

## 2.3 weak_ptr - 약한 참조

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <memory>
#include <vector>
#include <iostream>

// ❌ 순환 참조 문제
class BadNode {
public:
    std::shared_ptr<BadNode> next;
    std::shared_ptr<BadNode> prev;  // ❌ 순환 참조
    int data;

    BadNode(int d) : data(d) {}
    ~BadNode() {
        std::cout << "Node " << data << " destroyed\n";
    }
};

void CircularReferenceDemo() {
    auto node1 = std::make_shared<BadNode>(1);  // ref count = 1
    auto node2 = std::make_shared<BadNode>(2);  // ref count = 1

    node1->next = node2;  // node2 ref count = 2
    node2->prev = node1;  // node1 ref count = 2

    // ❌ 스코프 종료 시:
    // - node1 지역 변수 소멸 → node1 ref count = 1 (여전히 node2->prev가 가짐)
    // - node2 지역 변수 소멸 → node2 ref count = 1 (여전히 node1->next가 가짐)
    // - 둘 다 삭제 안 됨! 메모리 누수!
}  // ❌ 소멸자 호출 안 됨
```

```cpp
// ✅ weak_ptr로 순환 참조 해결
class GoodNode {
public:
    std::shared_ptr<GoodNode> next;  // ✅ 강한 참조 (소유)
    std::weak_ptr<GoodNode> prev;    // ✅ 약한 참조 (관찰만)
    int data;

    GoodNode(int d) : data(d) {}
    ~GoodNode() {
        std::cout << "Node " << data << " destroyed\n";
    }
};

void WeakPtrSolutionDemo() {
    auto node1 = std::make_shared<GoodNode>(1);  // ref count = 1
    auto node2 = std::make_shared<GoodNode>(2);  // ref count = 1

    node1->next = node2;  // node2 ref count = 2 (shared_ptr)
    node2->prev = node1;  // node1 ref count = 1 (weak_ptr는 증가 안 함!)

    // ✅ 스코프 종료 시:
    // - node1 지역 변수 소멸 → node1 ref count = 0 → node1 삭제됨
    // - node2 지역 변수 소멸 → node2 ref count = 1
    // - node1 삭제로 node1->next 삭제 → node2 ref count = 0 → node2 삭제됨
    // ✅ 정상적으로 메모리 해제!
}  // "Node 1 destroyed\n" "Node 2 destroyed\n"
```

```cpp
// weak_ptr 사용 패턴: lock()으로 임시 shared_ptr 얻기
class Equipment;

class EquipmentObserver {
private:
    std::weak_ptr<Equipment> observed_equipment;  // ✅ 약한 참조

public:
    EquipmentObserver(std::shared_ptr<Equipment> eq)
        : observed_equipment(eq) {}  // ✅ weak_ptr는 ref count 증가 안 함

    void CheckStatus() {
        // ✅ lock()으로 임시 shared_ptr 얻기
        if (auto eq = observed_equipment.lock()) {
            // eq는 shared_ptr<Equipment>
            // Equipment가 아직 살아있음 (ref count 임시 증가)
            std::cout << "Equipment status: " << eq->GetStatus() << "\n";
        } else {
            // Equipment가 이미 삭제됨
            std::cout << "Equipment no longer exists\n";
        }
        // ✅ eq 소멸 → ref count 원래대로
    }

    bool IsValid() const {
        return !observed_equipment.expired();  // ✅ 객체 존재 여부
    }
};
```

```cpp
// 캐시 시스템에서 weak_ptr 활용
class DataCache {
private:
    // weak_ptr로 캐시 (객체가 삭제되면 자동으로 expired)
    std::unordered_map<std::string, std::weak_ptr<CachedData>> cache;

public:
    std::shared_ptr<CachedData> GetOrLoad(const std::string& key) {
        // 1. 캐시 확인
        auto it = cache.find(key);
        if (it != cache.end()) {
            // weak_ptr를 shared_ptr로 변환 시도
            if (auto cached = it->second.lock()) {
                std::cout << "Cache hit: " << key << "\n";
                return cached;  // ✅ 캐시 적중
            } else {
                // 객체가 삭제됨 → 캐시 엔트리 제거
                cache.erase(it);
            }
        }

        // 2. 캐시 미스 → 새로 로드
        std::cout << "Cache miss: " << key << "\n";
        auto data = std::make_shared<CachedData>(key);
        cache[key] = data;  // ✅ weak_ptr 저장 (ref count 증가 안 함)
        return data;
    }

    void CleanupExpired() {
        // 만료된 weak_ptr 정리
        for (auto it = cache.begin(); it != cache.end(); ) {
            if (it->second.expired()) {
                it = cache.erase(it);
            } else {
                ++it;
            }
        }
    }

    size_t GetCacheSize() const { return cache.size(); }
};
```

```cpp
// 사용 예시: Observer 패턴
class EventBus {
private:
    std::vector<std::weak_ptr<EventListener>> listeners;  // ✅ 약한 참조

public:
    void Subscribe(std::shared_ptr<EventListener> listener) {
        listeners.push_back(listener);  // ✅ ref count 증가 안 함
    }

    void NotifyAll(const Event& event) {
        // 삭제된 리스너 자동 제거
        listeners.erase(
            std::remove_if(listeners.begin(), listeners.end(),
                [&](std::weak_ptr<EventListener>& weak_listener) {
                    if (auto listener = weak_listener.lock()) {
                        listener->OnEvent(event);  // ✅ 이벤트 전달
                        return false;  // 유지
                    }
                    return true;  // ✅ 삭제된 리스너 제거
                }),
            listeners.end()
        );
    }
};
```

</div>
<div>

**weak_ptr 핵심 특징**:

1. **약한 참조 (Weak Reference)**
   - 객체를 가리키지만 소유하지 않음
   - **참조 카운트 증가 안 함** (strong count)
   - weak count만 증가 (control block 유지용)
   - 객체 삭제를 막지 않음

2. **순환 참조 해결**
   ```
   ❌ shared_ptr → shared_ptr (순환 참조)
   Node A ──────→ Node B
        ↖──────/

   ✅ shared_ptr → weak_ptr (순환 끊김)
   Node A ──────→ Node B
        ←·····/ (약한 참조)
   ```

3. **사용 방법**
   - `lock()`: weak_ptr → shared_ptr 변환 (안전)
   - `expired()`: 객체가 삭제됐는지 확인
   - 직접 역참조 불가 (항상 lock() 먼저)

**weak_ptr API**:
```cpp
std::weak_ptr<T> wp;

auto sp = wp.lock();     // shared_ptr 반환 (nullptr 가능)
bool valid = !wp.expired();  // 객체 존재 여부
long count = wp.use_count(); // 현재 shared_ptr 개수
wp.reset();              // weak_ptr 초기화
```

**lock() vs expired()**:
```cpp
// ❌ 나쁜 예: expired() 후 lock() (race condition)
if (!wp.expired()) {
    auto sp = wp.lock();  // ❌ 사이에 객체 삭제될 수 있음!
    sp->DoSomething();    // ❌ nullptr 역참조 가능
}

// ✅ 좋은 예: lock()만 사용
if (auto sp = wp.lock()) {  // ✅ 원자적 변환
    sp->DoSomething();      // ✅ 안전
}
```

**Control Block 수명**:
```cpp
auto sp = std::make_shared<int>(42);
std::weak_ptr<int> wp = sp;

// Strong count = 1, Weak count = 1
// Control block 존재

sp.reset();  // 객체 삭제, Strong count = 0
             // ✅ 하지만 Control block은 유지 (Weak count = 1)

bool is_expired = wp.expired();  // true
auto sp2 = wp.lock();            // nullptr

// wp 소멸 → Weak count = 0 → Control block 삭제
```

**반도체 HMI 적용 사례**:

1. **Observer 패턴**
   - 이벤트 버스가 리스너를 weak_ptr로 보관
   - 리스너 삭제 시 자동으로 구독 해제

2. **캐시 시스템**
   - weak_ptr로 캐시 보관
   - 다른 곳에서 사용 안 하면 자동 정리

3. **부모-자식 관계**
   - 부모 → 자식: shared_ptr (소유)
   - 자식 → 부모: weak_ptr (순환 방지)

4. **UI 계층 구조**
   - Panel → Widget: shared_ptr
   - Widget → Panel: weak_ptr (parent 역참조)

**성능 고려**:
- lock() 호출은 원자적 연산 (atomic)
- 자주 호출하면 성능 영향
- 한 번 lock()하고 로컬 변수에 저장

</div>
</div>

---

# 3. Move Semantics (이동 의미론)

## 3.1 L-value vs R-value

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <iostream>
#include <vector>
#include <string>

// L-value와 R-value 구분
void ValueCategoryDemo() {
    int x = 10;           // x는 L-value (이름 있음, 주소 가짐)
    int y = x + 5;        // (x + 5)는 R-value (임시값, 주소 없음)

    int* ptr = &x;        // ✅ L-value는 주소 가능
    // int* ptr2 = &(x + 5);  // ❌ R-value는 주소 불가 (컴파일 에러)

    std::string s1 = "Hello";  // s1: L-value, "Hello": R-value
    std::string s2 = s1;       // s1: L-value (복사)
    std::string s3 = s1 + " World";  // (s1 + " World"): R-value (이동 가능)
}
```

```cpp
// ❌ 복사 생성자 (L-value 참조)
class CopyExample {
private:
    int* data;
    size_t size;

public:
    // 복사 생성자
    CopyExample(const CopyExample& other)
        : size(other.size) {
        std::cout << "Copy constructor\n";
        data = new int[size];  // ❌ 메모리 할당
        std::memcpy(data, other.data, size * sizeof(int));  // ❌ 복사
    }

    // 복사 대입 연산자
    CopyExample& operator=(const CopyExample& other) {
        std::cout << "Copy assignment\n";
        if (this != &other) {
            delete[] data;  // 기존 메모리 해제
            size = other.size;
            data = new int[size];  // ❌ 새 메모리 할당
            std::memcpy(data, other.data, size * sizeof(int));  // ❌ 복사
        }
        return *this;
    }
};
```

```cpp
// ✅ 이동 생성자 (R-value 참조)
class MoveExample {
private:
    int* data;
    size_t size;

public:
    // 이동 생성자 (R-value 참조 &&)
    MoveExample(MoveExample&& other) noexcept
        : data(other.data)    // ✅ 포인터만 복사 (얕은 복사)
        , size(other.size) {
        std::cout << "Move constructor\n";
        // ✅ 원본 무효화 (이중 삭제 방지)
        other.data = nullptr;
        other.size = 0;
    }

    // 이동 대입 연산자
    MoveExample& operator=(MoveExample&& other) noexcept {
        std::cout << "Move assignment\n";
        if (this != &other) {
            delete[] data;  // 기존 메모리 해제

            // ✅ 소유권 이전 (포인터 스왑)
            data = other.data;
            size = other.size;

            // ✅ 원본 무효화
            other.data = nullptr;
            other.size = 0;
        }
        return *this;
    }

    ~MoveExample() {
        delete[] data;  // ✅ nullptr 삭제는 안전
    }
};
```

```cpp
// 복사 vs 이동 성능 비교
void PerformanceComparison() {
    std::vector<int> source(1000000, 42);

    // ❌ 복사 (느림)
    auto start = std::chrono::high_resolution_clock::now();
    std::vector<int> dest1 = source;  // 100만 개 int 복사
    auto end = std::chrono::high_resolution_clock::now();
    std::cout << "Copy: " << std::chrono::duration<double, std::milli>(end - start).count() << "ms\n";

    // ✅ 이동 (빠름)
    start = std::chrono::high_resolution_clock::now();
    std::vector<int> dest2 = std::move(source);  // 포인터 3개만 복사
    end = std::chrono::high_resolution_clock::now();
    std::cout << "Move: " << std::chrono::duration<double, std::milli>(end - start).count() << "ms\n";

    // source는 이제 비어있음 (moved-from 상태)
    std::cout << "Source size after move: " << source.size() << "\n";  // 0
}
```

```cpp
// std::move의 역할
void MoveSemanticDemo() {
    std::string s1 = "Hello, World!";

    // ❌ 복사 (s1은 L-value)
    std::string s2 = s1;              // 복사 생성자 호출

    // ✅ 이동 (std::move로 R-value로 캐스팅)
    std::string s3 = std::move(s1);   // 이동 생성자 호출

    std::cout << "s1: " << s1 << "\n";  // "" (빈 문자열, moved-from)
    std::cout << "s2: " << s2 << "\n";  // "Hello, World!" (복사본)
    std::cout << "s3: " << s3 << "\n";  // "Hello, World!" (이동됨)

    // ⚠️ s1 사용 가능하지만 상태 불명확 (moved-from)
    // ✅ s1.clear()나 s1 = "new value" 는 안전
    // ❌ s1의 내용 가정하지 말 것
}
```

</div>
<div>

**L-value vs R-value**:

| 구분 | L-value | R-value |
|------|---------|---------|
| **정의** | 이름이 있는 값 | 임시 값 (temporary) |
| **주소** | 주소 가짐 (&x 가능) | 주소 없음 |
| **대입** | 대입 가능 (x = 10) | 대입 불가 |
| **수명** | 명시적 스코프 | 표현식 끝까지 |
| **예시** | 변수, 함수 반환 참조 | 리터럴, 함수 반환 값, 연산 결과 |

**R-value Reference (&&)**:
```cpp
void foo(int& x);        // L-value 참조
void bar(int&& x);       // R-value 참조

int a = 10;
foo(a);         // ✅ a는 L-value
foo(10);        // ❌ 10은 R-value (컴파일 에러)

bar(a);         // ❌ a는 L-value (컴파일 에러)
bar(10);        // ✅ 10은 R-value
bar(std::move(a));  // ✅ std::move로 R-value로 캐스팅
```

**std::move의 역할**:
```cpp
template<typename T>
typename remove_reference<T>::type&& move(T&& t) noexcept {
    return static_cast<typename remove_reference<T>::type&&>(t);
}

// std::move는 단순히 캐스팅만 함
// L-value → R-value reference로 변환
// 실제 "이동"은 하지 않음! (이름이 오해의 소지 있음)
```

**이동 의미론의 장점**:

1. **성능 향상**
   - 복사: O(n) (데이터 크기)
   - 이동: O(1) (포인터만 복사)

2. **불필요한 복사 제거**
   ```cpp
   std::vector<std::string> CreateLargeVector() {
       std::vector<std::string> v;
       v.push_back("...");
       // ...
       return v;  // ✅ 이동 (RVO + move semantics)
   }

   auto result = CreateLargeVector();  // ✅ 복사 없음!
   ```

3. **Move-only 타입 지원**
   - unique_ptr (복사 불가, 이동만 가능)
   - thread, mutex (복사 불가)

**반도체 HMI 적용**:
- 대용량 센서 데이터 전달
- UI 컴포넌트 소유권 이전
- 임시 버퍼 최적화

**주의사항**:
```cpp
std::string s = "Hello";
std::string s2 = std::move(s);
// ⚠️ s는 "moved-from" 상태
// ✅ s.empty() 체크 가능
// ✅ s = "new" 대입 가능
// ❌ s의 내용 가정하지 말 것
```

</div>
</div>

---

## 3.2 Perfect Forwarding (완벽한 전달)

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <utility>
#include <memory>
#include <iostream>

// ❌ 나쁜 예: 값 전달 (복사 발생)
template<typename T>
std::unique_ptr<T> BadMakeUnique(T value) {
    // value는 복사본 (비효율적)
    return std::unique_ptr<T>(new T(value));
}

// ❌ 나쁜 예: L-value 참조 (R-value 받을 수 없음)
template<typename T>
std::unique_ptr<T> BadMakeUnique2(T& value) {
    return std::unique_ptr<T>(new T(value));
}
// BadMakeUnique2(Widget());  // ❌ 컴파일 에러 (R-value 전달 불가)

// ❌ 나쁜 예: Const L-value 참조 (이동 불가)
template<typename T>
std::unique_ptr<T> BadMakeUnique3(const T& value) {
    // ✅ L-value와 R-value 둘 다 받을 수 있음
    // ❌ 하지만 항상 복사 (이동 못함)
    return std::unique_ptr<T>(new T(value));
}
```

```cpp
// ✅ 좋은 예: Universal Reference + Perfect Forwarding
template<typename T>
std::unique_ptr<T> GoodMakeUnique(T&& value) {
    // T&&: Universal Reference (Forwarding Reference)
    // std::forward: 원래 타입 유지하며 전달
    return std::unique_ptr<T>(new T(std::forward<T>(value)));
}

void PerfectForwardingDemo() {
    Widget w;

    // L-value 전달 → 복사 생성자
    auto p1 = GoodMakeUnique(w);  // T&& → Widget&

    // R-value 전달 → 이동 생성자
    auto p2 = GoodMakeUnique(Widget());  // T&& → Widget&&

    // std::move + L-value → 이동 생성자
    auto p3 = GoodMakeUnique(std::move(w));  // T&& → Widget&&
}
```

```cpp
// Perfect Forwarding 실전 예제: 팩토리 함수
template<typename T, typename... Args>
std::unique_ptr<T> CreateComponent(Args&&... args) {
    // ✅ 가변 인자 템플릿
    // ✅ Perfect Forwarding
    return std::make_unique<T>(std::forward<Args>(args)...);
}

class TemperatureWidget {
private:
    std::string label;
    double min_temp, max_temp;

public:
    TemperatureWidget(std::string lbl, double min_t, double max_t)
        : label(std::move(lbl)), min_temp(min_t), max_temp(max_t) {
        std::cout << "TemperatureWidget created: " << label << "\n";
    }
};

void FactoryDemo() {
    // ✅ 모든 인자가 완벽하게 전달됨
    // - "Temperature": R-value → 이동
    // - 0.0, 100.0: R-value → 값 전달
    auto widget = CreateComponent<TemperatureWidget>(
        "Temperature",  // R-value (문자열 리터럴)
        0.0,            // R-value
        100.0           // R-value
    );

    std::string label = "Pressure";
    // ✅ label은 L-value → 복사
    auto widget2 = CreateComponent<TemperatureWidget>(
        label,    // L-value → 복사
        0.0,
        10.0
    );

    // ✅ std::move로 label 이동
    auto widget3 = CreateComponent<TemperatureWidget>(
        std::move(label),  // R-value로 캐스팅 → 이동
        0.0,
        10.0
    );
}
```

```cpp
// emplace_back vs push_back
void EmplaceDemo() {
    std::vector<TemperatureWidget> widgets;
    widgets.reserve(10);

    // ❌ push_back: 임시 객체 생성 후 이동
    widgets.push_back(TemperatureWidget("Temp1", 0.0, 100.0));
    // 1. TemperatureWidget 생성자 (임시 객체)
    // 2. 이동 생성자 (vector로 이동)
    // 3. 소멸자 (임시 객체)

    // ✅ emplace_back: 제자리 생성 (Perfect Forwarding)
    widgets.emplace_back("Temp2", 0.0, 100.0);
    // 1. TemperatureWidget 생성자 (vector 내부에서 바로 생성)
    // → 더 효율적!
}
```

```cpp
// Reference Collapsing 규칙
template<typename T>
void foo(T&& param) {
    // T가 int&일 때:
    // T&& = int& && → int& (Reference Collapsing)

    // T가 int일 때:
    // T&& = int&& (R-value reference)
}

int x = 10;
foo(x);          // T = int&,  T&& = int& &&  → int&
foo(10);         // T = int,   T&& = int&&
foo(std::move(x)); // T = int,   T&& = int&&
```

```cpp
// std::forward 동작 원리
template<typename T>
T&& forward(typename remove_reference<T>::type& t) noexcept {
    return static_cast<T&&>(t);
}

// 사용 예:
template<typename T>
void wrapper(T&& arg) {
    // ❌ arg 자체는 L-value (이름이 있음)
    foo(arg);             // 항상 L-value로 전달

    // ✅ std::forward로 원래 value category 복원
    foo(std::forward<T>(arg));  // T가 int&면 L-value로, int면 R-value로 전달
}
```

</div>
<div>

**Perfect Forwarding (완벽한 전달)**:

1. **Universal Reference (T&&)**
   - 템플릿 매개변수 `T&&`는 특별함
   - L-value 받으면 L-value 참조로 추론
   - R-value 받으면 R-value 참조로 추론

2. **Reference Collapsing 규칙**
   ```
   T&  &  → T&     (L-value ref + L-value ref = L-value ref)
   T&  && → T&     (L-value ref + R-value ref = L-value ref)
   T&& &  → T&     (R-value ref + L-value ref = L-value ref)
   T&& && → T&&    (R-value ref + R-value ref = R-value ref)

   요약: & 하나라도 있으면 &
   ```

3. **std::forward의 역할**
   ```cpp
   // L-value로 전달받았으면 L-value로 전달
   // R-value로 전달받았으면 R-value로 전달

   wrapper(x);           // x: L-value
   → foo(arg)            // L-value로 전달
   → foo(forward(arg))   // L-value로 전달

   wrapper(Widget());    // Widget(): R-value
   → foo(arg)            // L-value로 전달 (❌)
   → foo(forward(arg))   // R-value로 전달 (✅)
   ```

**std::forward vs std::move**:

| | std::forward | std::move |
|---|--------------|-----------|
| **용도** | 템플릿에서 value category 보존 | 명시적 R-value 변환 |
| **사용처** | Universal reference (T&&) | 일반 L-value |
| **결과** | 조건부 (L or R) | 항상 R-value |

```cpp
template<typename T>
void foo(T&& arg) {
    bar(std::forward<T>(arg));  // ✅ Perfect forwarding
}

void baz(Widget& w) {
    Widget w2 = std::move(w);   // ✅ 명시적 이동
}
```

**emplace_back의 장점**:
```cpp
// push_back
vector.push_back(Widget(arg1, arg2));
// 1. Widget 생성 (임시)
// 2. 이동 생성자
// 3. 소멸자 (임시)

// emplace_back
vector.emplace_back(arg1, arg2);
// 1. Widget 생성 (제자리)
// → 1단계로 줄어듦!
```

**반도체 HMI 적용**:

```cpp
// UI 컴포넌트 팩토리
class UIPanel {
    std::vector<std::unique_ptr<Widget>> widgets;

public:
    template<typename WidgetType, typename... Args>
    WidgetType* AddWidget(Args&&... args) {
        auto widget = std::make_unique<WidgetType>(
            std::forward<Args>(args)...  // ✅ Perfect forwarding
        );
        WidgetType* ptr = widget.get();
        widgets.push_back(std::move(widget));
        return ptr;
    }
};

// 사용
panel.AddWidget<TemperatureWidget>("Temp", 0.0, 100.0);
// 모든 인자가 효율적으로 전달됨
```

**주의사항**:
- Universal reference는 **템플릿에서만** (T&&)
- 일반 R-value reference와 구분: `Widget&&` (일반), `T&&` (universal)
- `std::forward<T>` 타입 명시 필요

</div>
</div>

---

# 4. 메모리 관리 고급 기법

## 4.1 Custom Allocator (커스텀 할당자)

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <memory>
#include <vector>
#include <array>
#include <cstddef>

// Memory Pool Allocator (고정 크기 블록)
template<typename T, size_t BlockSize = 4096>
class PoolAllocator {
private:
    // 메모리 풀
    struct Block {
        std::array<std::byte, BlockSize> data;
        Block* next;
    };

    Block* free_blocks = nullptr;
    std::vector<std::unique_ptr<Block>> all_blocks;

public:
    using value_type = T;

    PoolAllocator() = default;

    template<typename U>
    PoolAllocator(const PoolAllocator<U, BlockSize>&) noexcept {}

    T* allocate(std::size_t n) {
        const size_t bytes = n * sizeof(T);

        if (bytes > BlockSize) {
            // 블록 크기 초과 → 일반 할당
            return static_cast<T*>(::operator new(bytes));
        }

        if (!free_blocks) {
            // 새 블록 생성
            auto new_block = std::make_unique<Block>();
            free_blocks = new_block.get();
            free_blocks->next = nullptr;
            all_blocks.push_back(std::move(new_block));
        }

        // 프리 리스트에서 할당
        Block* block = free_blocks;
        free_blocks = free_blocks->next;

        return reinterpret_cast<T*>(block->data.data());
    }

    void deallocate(T* p, std::size_t n) noexcept {
        const size_t bytes = n * sizeof(T);

        if (bytes > BlockSize) {
            // 일반 할당한 경우
            ::operator delete(p);
            return;
        }

        // 프리 리스트에 반환
        Block* block = reinterpret_cast<Block*>(p);
        block->next = free_blocks;
        free_blocks = block;
    }

    template<typename U>
    struct rebind {
        using other = PoolAllocator<U, BlockSize>;
    };
};

template<typename T, typename U, size_t BlockSize>
bool operator==(const PoolAllocator<T, BlockSize>&,
                const PoolAllocator<U, BlockSize>&) noexcept {
    return true;
}

template<typename T, typename U, size_t BlockSize>
bool operator!=(const PoolAllocator<T, BlockSize>&,
                const PoolAllocator<U, BlockSize>&) noexcept {
    return false;
}
```

```cpp
// Stack Allocator (스택 메모리 사용)
template<typename T, size_t N>
class StackAllocator {
private:
    alignas(T) std::byte buffer[N * sizeof(T)];
    std::byte* current = buffer;

public:
    using value_type = T;

    StackAllocator() = default;

    template<typename U>
    StackAllocator(const StackAllocator<U, N>&) noexcept {}

    T* allocate(std::size_t n) {
        const size_t bytes = n * sizeof(T);
        const size_t remaining = (buffer + sizeof(buffer)) - current;

        if (bytes > remaining) {
            throw std::bad_alloc();  // 스택 공간 부족
        }

        T* result = reinterpret_cast<T*>(current);
        current += bytes;
        return result;
    }

    void deallocate(T*, std::size_t) noexcept {
        // 스택 할당자는 개별 해제 안 함
        // 스코프 종료 시 전체 리셋
    }

    void reset() noexcept {
        current = buffer;  // 스택 포인터 리셋
    }

    template<typename U>
    struct rebind {
        using other = StackAllocator<U, N>;
    };
};
```

```cpp
// 사용 예시: 임시 데이터 버퍼
void RenderFrame() {
    // ✅ 프레임마다 리셋되는 임시 버퍼
    StackAllocator<float, 10000> temp_allocator;

    // ✅ 스택 메모리 사용 (빠름, 캐시 친화적)
    std::vector<float, StackAllocator<float, 10000>>
        temp_vertices(temp_allocator);

    temp_vertices.reserve(1000);

    // 정점 데이터 생성
    for (int i = 0; i < 1000; ++i) {
        temp_vertices.push_back(/* ... */);
    }

    // 렌더링
    RenderVertices(temp_vertices.data(), temp_vertices.size());

    // ✅ 스코프 종료 시 자동 정리 (deallocate 호출 없음)
}
```

```cpp
// Performance comparison
void AllocationBenchmark() {
    constexpr size_t COUNT = 100000;

    // ❌ 기본 할당자 (느림)
    auto start = std::chrono::high_resolution_clock::now();
    {
        std::vector<int> v;
        for (size_t i = 0; i < COUNT; ++i) {
            v.push_back(i);  // 여러 번 재할당
        }
    }
    auto end = std::chrono::high_resolution_clock::now();
    std::cout << "Default allocator: "
              << std::chrono::duration<double, std::milli>(end - start).count()
              << "ms\n";

    // ✅ Pool 할당자 (빠름)
    start = std::chrono::high_resolution_clock::now();
    {
        std::vector<int, PoolAllocator<int>> v;
        v.reserve(COUNT);
        for (size_t i = 0; i < COUNT; ++i) {
            v.push_back(i);
        }
    }
    end = std::chrono::high_resolution_clock::now();
    std::cout << "Pool allocator: "
              << std::chrono::duration<double, std::milli>(end - start).count()
              << "ms\n";
}
```

</div>
<div>

**Custom Allocator 개념**:

1. **표준 할당자 문제점**
   - `malloc/free`: 느림 (시스템 호출)
   - 단편화 (Fragmentation)
   - 캐시 미스 증가

2. **Pool Allocator**
   - 고정 크기 블록 미리 할당
   - Free list로 빠른 할당/해제
   - 단편화 감소
   - **사용처**: 동일 크기 객체 많을 때

3. **Stack Allocator**
   - 스택 메모리 사용 (로컬 배열)
   - 선형 할당 (포인터만 증가)
   - 개별 해제 없음 (전체 리셋)
   - **사용처**: 임시 데이터 (프레임마다 리셋)

**Allocator 인터페이스 (C++17)**:
```cpp
template<typename T>
struct Allocator {
    using value_type = T;

    T* allocate(std::size_t n);
    void deallocate(T* p, std::size_t n);

    template<typename U>
    struct rebind {
        using other = Allocator<U>;
    };
};
```

**PMR (Polymorphic Memory Resource, C++17)**:
```cpp
#include <memory_resource>

std::pmr::monotonic_buffer_resource pool(8192);
std::pmr::vector<int> vec(&pool);  // PMR 할당자 사용

// 장점: 런타임에 할당자 교체 가능
```

**성능 비교**:

| Allocator | 할당 속도 | 해제 속도 | 메모리 효율 | 사용 난이도 |
|-----------|-----------|-----------|-------------|-------------|
| **malloc/free** | 느림 | 느림 | 보통 | 쉬움 |
| **Pool** | 빠름 | 빠름 | 좋음 (고정 크기) | 보통 |
| **Stack** | 매우 빠름 | 즉시 | 매우 좋음 | 어려움 |

**반도체 HMI 적용**:

```cpp
// 실시간 센서 데이터 버퍼
class SensorDataBuffer {
    // ✅ Pool allocator (재사용)
    using Allocator = PoolAllocator<SensorReading, 4096>;
    std::vector<SensorReading, Allocator> buffer;

public:
    void AddReading(const SensorReading& reading) {
        buffer.push_back(reading);  // ✅ 빠른 할당
    }
};

// 프레임별 UI 렌더링 데이터
void RenderUI() {
    // ✅ Stack allocator (임시 데이터)
    StackAllocator<Vertex, 10000> alloc;
    std::pmr::vector<Vertex> vertices(&alloc);

    // 정점 생성...

    // ✅ 스코프 종료 시 자동 정리
}
```

**주의사항**:
- 할당자는 **상태없음** (stateless) 권장
- `rebind` 구현 필수 (컨테이너 내부 노드용)
- 스레드 안전성 고려

</div>
</div>

---

## 4.2 RAII + Custom Deleter

<div class="grid grid-cols-2 gap-8">
<div>

```cpp
#include <memory>
#include <cstdio>
#include <GL/gl.h>

// ❌ 나쁜 예: C 리소스 수동 관리
void BadFileHandling() {
    FILE* file = fopen("data.txt", "r");
    if (!file) return;

    // ... 작업 ...

    fclose(file);  // ❌ 예외 발생 시 누수
}

// ✅ 좋은 예: unique_ptr + custom deleter
void GoodFileHandling() {
    auto file = std::unique_ptr<FILE, decltype(&fclose)>(
        fopen("data.txt", "r"),
        &fclose  // ✅ Custom deleter
    );

    if (!file) return;

    // ... 작업 ...

    // ✅ 자동으로 fclose() 호출
}
```

```cpp
// Lambda를 사용한 Custom Deleter
class GLResourceManager {
public:
    // OpenGL 텍스처 RAII
    using GLTexturePtr = std::unique_ptr<GLuint, std::function<void(GLuint*)>>;

    static GLTexturePtr CreateTexture(int width, int height) {
        GLuint* tex_id = new GLuint;
        glGenTextures(1, tex_id);
        glBindTexture(GL_TEXTURE_2D, *tex_id);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);

        // ✅ Lambda deleter
        return GLTexturePtr(tex_id, [](GLuint* id) {
            if (id && *id != 0) {
                glDeleteTextures(1, id);
            }
            delete id;
        });
    }

    // OpenGL 버퍼 RAII
    using GLBufferPtr = std::unique_ptr<GLuint, std::function<void(GLuint*)>>;

    static GLBufferPtr CreateBuffer() {
        GLuint* buf_id = new GLuint;
        glGenBuffers(1, buf_id);

        return GLBufferPtr(buf_id, [](GLuint* id) {
            if (id && *id != 0) {
                glDeleteBuffers(1, id);
            }
            delete id;
        });
    }
};
```

```cpp
// Functor를 사용한 Custom Deleter
struct SocketDeleter {
    void operator()(int* socket_fd) const {
        if (socket_fd && *socket_fd >= 0) {
            close(*socket_fd);
            std::cout << "Socket closed: " << *socket_fd << "\n";
        }
        delete socket_fd;
    }
};

class NetworkConnection {
private:
    std::unique_ptr<int, SocketDeleter> socket;

public:
    NetworkConnection(const char* host, int port) {
        int* fd = new int;
        *fd = socket(AF_INET, SOCK_STREAM, 0);

        if (*fd < 0) {
            delete fd;
            throw std::runtime_error("Socket creation failed");
        }

        // ... connect ...

        socket.reset(fd);  // ✅ SocketDeleter로 관리
    }

    void Send(const char* data, size_t len) {
        if (socket && *socket >= 0) {
            write(*socket, data, len);
        }
    }

    // ✅ 소멸 시 SocketDeleter 자동 호출
};
```

```cpp
// shared_ptr with custom deleter
class ThreadPool {
public:
    using ThreadHandle = std::shared_ptr<std::thread>;

    static ThreadHandle CreateThread(std::function<void()> task) {
        // ✅ shared_ptr + lambda deleter
        return ThreadHandle(
            new std::thread(task),
            [](std::thread* t) {
                if (t->joinable()) {
                    t->join();  // ✅ 자동 join
                    std::cout << "Thread joined\n";
                }
                delete t;
            }
        );
    }
};

void ThreadPoolDemo() {
    {
        auto thread1 = ThreadPool::CreateThread([]() {
            std::cout << "Worker thread running\n";
            std::this_thread::sleep_for(std::chrono::seconds(1));
        });

        auto thread2 = ThreadPool::CreateThread([]() {
            std::cout << "Another worker running\n";
        });

        // ✅ 스코프 종료 시 자동으로 join() 호출
    }  // thread1, thread2 삭제 → join() → delete

    std::cout << "All threads completed\n";
}
```

```cpp
// 복잡한 리소스 정리 로직
struct DatabaseDeleter {
    std::string connection_string;

    void operator()(DatabaseConnection* conn) const {
        if (conn) {
            std::cout << "Closing database: " << connection_string << "\n";
            conn->Commit();       // ✅ 커밋
            conn->Disconnect();   // ✅ 연결 해제
            conn->LogActivity();  // ✅ 로그 기록
            delete conn;
        }
    }
};

class DatabaseManager {
public:
    using DBPtr = std::unique_ptr<DatabaseConnection, DatabaseDeleter>;

    static DBPtr Connect(const std::string& conn_str) {
        auto* conn = new DatabaseConnection(conn_str);
        return DBPtr(conn, DatabaseDeleter{conn_str});
    }
};
```

</div>
<div>

**Custom Deleter 패턴**:

1. **목적**
   - unique_ptr/shared_ptr는 기본적으로 `delete` 호출
   - C 리소스 (FILE*, socket, OpenGL ID 등)는 다른 정리 함수 필요
   - Custom deleter로 정리 로직 커스터마이징

2. **Deleter 종류**

   **함수 포인터**:
   ```cpp
   unique_ptr<FILE, decltype(&fclose)> file(fopen("f.txt", "r"), &fclose);
   ```

   **Lambda**:
   ```cpp
   auto deleter = [](GLuint* id) { glDeleteTextures(1, id); delete id; };
   unique_ptr<GLuint, decltype(deleter)> tex(new GLuint, deleter);
   ```

   **Functor (함수 객체)**:
   ```cpp
   struct MyDeleter {
       void operator()(T* ptr) const { /* cleanup */ }
   };
   unique_ptr<T, MyDeleter> ptr(new T);
   ```

3. **unique_ptr vs shared_ptr deleter**

   **unique_ptr**:
   ```cpp
   unique_ptr<T, DeleterType> ptr;
   // DeleterType이 템플릿 인자
   // 타입이 다르면 다른 타입
   ```

   **shared_ptr**:
   ```cpp
   shared_ptr<T> ptr(new T, deleter);
   // deleter는 생성자 인자
   // 타입 무관 (type erasure)
   ```

**성능 고려**:

| Deleter 타입 | unique_ptr 크기 | 성능 |
|--------------|-----------------|------|
| **기본 delete** | 8바이트 | 최적 |
| **함수 포인터** | 16바이트 | 좋음 |
| **Stateless 람다** | 8바이트 | 최적 |
| **Stateful 람다** | 8+상태 크기 | 보통 |
| **Functor** | 8+상태 크기 | 보통 |

```cpp
// Stateless lambda (크기 증가 없음)
auto del1 = [](T* p) { delete p; };
unique_ptr<T, decltype(del1)> p1(new T, del1);  // 8 bytes

// Stateful lambda (상태 저장 → 크기 증가)
std::string name = "resource";
auto del2 = [name](T* p) { std::cout << name; delete p; };
unique_ptr<T, decltype(del2)> p2(new T, del2);  // 8 + sizeof(string)
```

**반도체 HMI 적용**:

```cpp
// 시리얼 포트 RAII
struct SerialPortDeleter {
    void operator()(int* fd) const {
        if (fd && *fd >= 0) {
            tcflush(*fd, TCIOFLUSH);  // 버퍼 비우기
            close(*fd);
            std::cout << "Serial port closed\n";
        }
        delete fd;
    }
};

using SerialPortPtr = unique_ptr<int, SerialPortDeleter>;

SerialPortPtr OpenSerialPort(const char* device) {
    int* fd = new int;
    *fd = open(device, O_RDWR | O_NOCTTY);

    if (*fd < 0) {
        delete fd;
        throw std::runtime_error("Failed to open serial port");
    }

    // ... 포트 설정 ...

    return SerialPortPtr(fd);  // ✅ 자동 정리
}
```

**주의사항**:
- Deleter는 예외 던지지 말 것 (`noexcept`)
- shared_ptr deleter는 복사 가능해야 함
- Deleter는 nullptr 체크해야 함

</div>
</div>

---

# 요약

## C++ 고급 기법 정리

<div class="grid grid-cols-2 gap-8">
<div>

**1. RAII (Resource Acquisition Is Initialization)**
- 생성자 = 리소스 획득
- 소멸자 = 리소스 해제
- 예외 안전성 보장
- 수동 관리 불필요

**2. Smart Pointers**

**unique_ptr**:
- 단독 소유권
- 복사 불가, 이동 가능
- 오버헤드 없음 (8바이트)
- 사용: 기본 선택

**shared_ptr**:
- 공유 소유권
- 참조 카운팅
- 오버헤드 있음 (16바이트 + control block)
- 사용: 진짜 공유 필요할 때만

**weak_ptr**:
- 약한 참조
- 순환 참조 해결
- lock()으로 임시 접근
- 사용: Observer, 캐시

**3. Move Semantics**
- L-value vs R-value
- 이동 생성자/대입
- std::move (캐스팅)
- 성능 향상 (복사 제거)

**4. Perfect Forwarding**
- Universal Reference (T&&)
- std::forward
- 가변 인자 템플릿
- emplace_back 활용

</div>
<div>

**반도체 HMI 설계 원칙**:

```cpp
// ✅ 권장 패턴
class EquipmentController {
    // 소유 → unique_ptr
    unique_ptr<SerialPort> port;

    // 공유 → shared_ptr
    shared_ptr<RecipeData> current_recipe;

    // 관찰 → weak_ptr
    weak_ptr<Logger> logger;

    // OpenGL → RAII 래퍼
    GLTexture wafer_map_texture;
    GLBuffer vertex_buffer;

public:
    // Perfect forwarding 팩토리
    template<typename T, typename... Args>
    unique_ptr<T> CreateComponent(Args&&... args) {
        return make_unique<T>(forward<Args>(args)...);
    }

    // Move-only API
    void SetRecipe(shared_ptr<RecipeData> recipe) {
        current_recipe = move(recipe);
    }
};
```

**성능 최적화 체크리스트**:
- ✅ unique_ptr을 기본으로 사용
- ✅ shared_ptr은 진짜 필요할 때만
- ✅ 함수 반환은 값 반환 (RVO)
- ✅ 함수 인자는 const& (읽기) 또는 && (소유)
- ✅ emplace_back > push_back
- ✅ make_unique/make_shared 사용
- ✅ std::move로 불필요한 복사 제거
- ❌ raw pointer 최소화
- ❌ new/delete 직접 사용 금지

</div>
</div>
