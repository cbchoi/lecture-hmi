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
