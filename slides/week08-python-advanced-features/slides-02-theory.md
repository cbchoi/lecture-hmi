# 🚀 이론 강의: Python 고급 기능

---

## Generator 패턴

### 🔄 Generator와 yield

**메모리 효율적인 반복자**

<div class="grid grid-cols-2 gap-8">
<div>

```python
# 일반 함수 vs Generator
def normal_range(n):
    """일반 함수: 전체 리스트 생성"""
    result = []
    for i in range(n):
        result.append(i)
    return result  # 메모리에 전체 리스트 저장

def generator_range(n):
    """Generator: 필요할 때마다 값 생성"""
    for i in range(n):
        yield i  # 값을 하나씩 생성

# 사용 비교
normal_list = normal_range(1000000)  # 800만 바이트 메모리
gen = generator_range(1000000)       # 200 바이트 메모리

# Generator 반복
for value in gen:
    print(value)  # 필요할 때마다 생성

# Generator 표현식
gen_expr = (x**2 for x in range(1000000))
squares = [x for x in gen_expr if x % 2 == 0]

# 반도체 HMI 적용: 대용량 센서 데이터 처리
def read_sensor_stream(sensor_id: str):
    """센서 데이터 스트림 (무한 생성)"""
    import random
    import time

    while True:
        # 센서 읽기 시뮬레이션
        temperature = 25.0 + random.uniform(-5, 5)
        pressure = 1.0 + random.uniform(-0.1, 0.1)

        yield {
            'sensor_id': sensor_id,
            'temperature': temperature,
            'pressure': pressure,
            'timestamp': time.time()
        }

        time.sleep(0.1)  # 100ms 주기

# 사용
sensor_stream = read_sensor_stream("S001")

# 처음 10개 데이터만 가져오기
for i, data in enumerate(sensor_stream):
    if i >= 10:
        break
    print(f"Temperature: {data['temperature']:.2f}°C")

# 조건에 맞는 데이터만 필터링
def filter_high_temp(stream, threshold=30.0):
    """높은 온도만 필터링"""
    for data in stream:
        if data['temperature'] > threshold:
            yield data

# 체인 방식으로 사용
high_temp_stream = filter_high_temp(
    read_sensor_stream("S001"),
    threshold=28.0
)

for data in high_temp_stream:
    print(f"Alert! High temperature: {data['temperature']:.2f}°C")
    if should_stop_monitoring():
        break
```

</div>
<div>

**Generator 핵심 개념**:

**yield 키워드**:
- 함수를 Generator로 변환
- 값을 반환하고 상태 유지
- `return`과 달리 함수 종료 안 함
- 다음 호출 시 이어서 실행

**장점**:
- **메모리 효율**: 전체 데이터를 메모리에 안 둠
- **지연 평가**: 필요할 때만 계산
- **무한 시퀀스**: 끝없는 스트림 표현
- **파이프라인**: 여러 generator 연결

**실행 흐름**:
```python
def count_up_to(n):
    i = 0
    while i < n:
        yield i
        i += 1

gen = count_up_to(3)
print(next(gen))  # 0 (첫 yield까지 실행)
print(next(gen))  # 1 (다음 yield까지)
print(next(gen))  # 2
print(next(gen))  # StopIteration 예외
```

**Generator 표현식**:
```python
# 리스트 컴프리헨션
squares_list = [x**2 for x in range(1000000)]
# 메모리: 전체 리스트 저장

# Generator 표현식 (괄호 사용)
squares_gen = (x**2 for x in range(1000000))
# 메모리: Generator 객체만 저장

# 필요한 만큼만 사용
first_10 = list(squares_gen)[:10]
```

**반도체 데이터 처리**:
```python
def process_wafer_data(wafer_file):
    """대용량 웨이퍼 데이터 처리"""
    with open(wafer_file, 'r') as f:
        for line in f:  # 파일도 generator
            # 한 줄씩 처리 (전체 파일 로드 안 함)
            data = parse_wafer_line(line)
            if data['defect_count'] > 0:
                yield data

# 파이프라인
wafer_stream = process_wafer_data('wafers.csv')
high_defect = (w for w in wafer_stream
               if w['defect_count'] > 10)
critical_wafers = (w for w in high_defect
                   if w['location'] == 'center')

for wafer in critical_wafers:
    alert_ops_team(wafer)
```

**itertools 활용**:
```python
from itertools import (
    islice, chain, cycle, repeat
)

# 무한 센서 시퀬레이션
sensor_cycle = cycle(['S001', 'S002', 'S003'])
# S001, S002, S003, S001, S002, ...

# 처음 N개만
first_100 = islice(
    read_sensor_stream("S001"),
    100
)

# 여러 스트림 연결
all_sensors = chain(
    read_sensor_stream("S001"),
    read_sensor_stream("S002"),
    read_sensor_stream("S003")
)
```

</div>
</div>

---

### 🔧 Generator Advanced: send(), throw(), close()

**양방향 통신 Generator**

<div class="grid grid-cols-2 gap-8">
<div>

```python
def averaging_generator():
    """실행 중 평균 계산 Generator"""
    total = 0.0
    count = 0
    average = None

    while True:
        # send()로 받은 값
        value = yield average
        total += value
        count += 1
        average = total / count

# 사용
avg_gen = averaging_generator()
next(avg_gen)  # Generator 시작 (초기화)

print(avg_gen.send(10))  # 10.0
print(avg_gen.send(20))  # 15.0
print(avg_gen.send(30))  # 20.0

# 반도체 HMI: PID 제어 Generator
def pid_controller(setpoint, kp=1.0, ki=0.1, kd=0.05):
    """PID 제어기 Generator"""
    integral = 0
    previous_error = 0

    while True:
        # 현재 측정값 받기
        current_value = yield

        # PID 계산
        error = setpoint - current_value
        integral += error
        derivative = error - previous_error

        # 출력 계산
        output = (kp * error) + (ki * integral) + (kd * derivative)
        previous_error = error

        # 출력 전송
        adjustment = yield output

# 사용
pid = pid_controller(setpoint=150.0)
next(pid)  # 초기화

current_temp = 140.0
adjustment = pid.send(current_temp)
print(f"Adjust by: {adjustment}")

current_temp = 145.0
adjustment = pid.send(current_temp)
print(f"Adjust by: {adjustment}")

# throw(): Generator에 예외 주입
def resilient_processor():
    """예외 처리 가능한 Generator"""
    while True:
        try:
            data = yield
            print(f"Processing: {data}")
            result = process_data(data)
            yield result
        except ValueError as e:
            print(f"Invalid data: {e}")
            yield None
        except StopProcessing:
            print("Stopping processor")
            break

processor = resilient_processor()
next(processor)

processor.send({'value': 100})
# ValueError 주입
processor.throw(ValueError, "Bad sensor data")
# 계속 실행 가능

# close(): Generator 종료
def monitored_stream():
    """모니터링 가능한 스트림"""
    try:
        while True:
            data = yield get_sensor_data()
    except GeneratorExit:
        # 정리 작업
        cleanup_resources()
        print("Stream closed gracefully")

stream = monitored_stream()
next(stream)

# 사용 후 정리
stream.close()  # GeneratorExit 예외 발생
```

</div>
<div>

**send() 메서드**:
- Generator에 값 전송
- `value = yield`로 받음
- 양방향 통신 가능
- 코루틴 패턴의 기초

**실행 순서**:
```python
def gen():
    x = yield 1      # (1) 1을 yield
    print(f"Got {x}")
    y = yield 2      # (3) 2를 yield
    print(f"Got {y}")

g = gen()
print(next(g))       # (1) → 출력: 1
print(g.send(10))    # (2) x=10, (3) → 출력: Got 10, 2
print(g.send(20))    # (4) y=20 → 출력: Got 20, StopIteration
```

**throw() 메서드**:
- Generator 내부에 예외 발생
- try-except로 처리 가능
- 에러 복구 메커니즘

**사용 예시**:
```python
def error_handler():
    errors = []
    while True:
        try:
            data = yield
            process(data)
        except Exception as e:
            errors.append(e)
            yield f"Error: {e}"

handler = error_handler()
next(handler)

handler.send(good_data)
# 에러 주입
handler.throw(TimeoutError("Sensor timeout"))
```

**close() 메서드**:
- Generator 종료
- `GeneratorExit` 예외 발생
- finally 블록 실행
- 리소스 정리

**Context Manager와 결합**:
```python
from contextlib import contextmanager

@contextmanager
def sensor_monitor(sensor_id):
    """Generator 기반 Context Manager"""
    stream = start_monitoring(sensor_id)
    try:
        yield stream
    finally:
        stream.close()  # 자동 정리

# 사용
with sensor_monitor("S001") as stream:
    for data in stream:
        process(data)
# 자동으로 close() 호출
```

**실무 패턴: 상태 머신**:
```python
def equipment_state_machine():
    """장비 상태 머신 Generator"""
    state = "IDLE"

    while True:
        command = yield state

        if state == "IDLE":
            if command == "START":
                state = "RUNNING"
        elif state == "RUNNING":
            if command == "STOP":
                state = "IDLE"
            elif command == "ERROR":
                state = "ERROR"
        elif state == "ERROR":
            if command == "RESET":
                state = "IDLE"

sm = equipment_state_machine()
next(sm)  # IDLE

print(sm.send("START"))   # RUNNING
print(sm.send("ERROR"))   # ERROR
print(sm.send("RESET"))   # IDLE
```

</div>
</div>

---

## Iterator Protocol

### 🔁 `__iter__` 와 `__next__`

**커스텀 반복자 구현**

<div class="grid grid-cols-2 gap-8">
<div>

```python
# Iterator Protocol 구현
class SensorDataIterator:
    """센서 데이터 반복자"""

    def __init__(self, sensor_id, count=100):
        self.sensor_id = sensor_id
        self.count = count
        self.index = 0

    def __iter__(self):
        """반복자 자신을 반환"""
        return self

    def __next__(self):
        """다음 값 반환"""
        if self.index >= self.count:
            raise StopIteration

        # 센서 데이터 생성
        data = {
            'sensor_id': self.sensor_id,
            'index': self.index,
            'value': self.read_sensor(),
            'timestamp': time.time()
        }

        self.index += 1
        return data

    def read_sensor(self):
        """실제 센서 읽기"""
        import random
        return 25.0 + random.uniform(-5, 5)

# 사용
sensor_iter = SensorDataIterator("S001", count=10)

for data in sensor_iter:
    print(f"Value: {data['value']:.2f}")

# Iterable vs Iterator
class EquipmentCollection:
    """Iterable: __iter__ 구현"""

    def __init__(self):
        self.equipment = [
            {"id": "E001", "name": "Etcher"},
            {"id": "E002", "name": "CVD"},
            {"id": "E003", "name": "CMP"}
        ]

    def __iter__(self):
        """새로운 Iterator 반환"""
        return iter(self.equipment)

# 사용
collection = EquipmentCollection()

# 여러 번 반복 가능
for equip in collection:
    print(equip['name'])

for equip in collection:  # 다시 반복 가능
    print(equip['id'])

# Custom Iterator로 더 복잡한 로직
class FilteredEquipmentIterator:
    """필터링된 장비 Iterator"""

    def __init__(self, equipment_list, status_filter):
        self.equipment = equipment_list
        self.status_filter = status_filter
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        # 조건에 맞는 다음 항목 찾기
        while self.index < len(self.equipment):
            equip = self.equipment[self.index]
            self.index += 1

            if equip['status'] == self.status_filter:
                return equip

        raise StopIteration

# 무한 Iterator
class InfiniteCounter:
    """무한 카운터"""

    def __init__(self, start=0, step=1):
        self.current = start
        self.step = step

    def __iter__(self):
        return self

    def __next__(self):
        value = self.current
        self.current += self.step
        return value

# 사용 (주의: 무한 루프!)
counter = InfiniteCounter(start=0, step=5)
for i, value in enumerate(counter):
    if i >= 10:
        break
    print(value)  # 0, 5, 10, 15, ...
```

</div>
<div>

**Iterator Protocol**:
- **`__iter__()`**: 반복자 객체 반환
- **`__next__()`**: 다음 값 반환
- **`StopIteration`**: 반복 종료 신호

**Iterable vs Iterator**:
```python
# Iterable: __iter__만 구현
class MyIterable:
    def __iter__(self):
        return MyIterator()

# Iterator: __iter__ + __next__ 구현
class MyIterator:
    def __iter__(self):
        return self

    def __next__(self):
        ...
```

**차이점**:
- **Iterable**: 반복 가능한 객체
  - `__iter__()` 구현
  - `for` 루프에서 사용 가능
  - 여러 번 반복 가능

- **Iterator**: 반복자
  - `__iter__()` + `__next__()` 구현
  - 한 번만 반복 가능 (상태 유지)
  - 직접 `next()` 호출 가능

**내장 Iterator 함수**:
```python
# iter(): Iterable → Iterator
my_list = [1, 2, 3]
iterator = iter(my_list)

print(next(iterator))  # 1
print(next(iterator))  # 2
print(next(iterator))  # 3
print(next(iterator))  # StopIteration

# iter(callable, sentinel)
# sentinel 값까지 호출
def read_sensor():
    import random
    return random.randint(0, 10)

sensor_iter = iter(read_sensor, 5)
# 5가 나올 때까지 read_sensor() 호출
for value in sensor_iter:
    print(value)
```

**반도체 HMI 적용**:
```python
class WaferBatchIterator:
    """Wafer Batch 반복자"""

    def __init__(self, batch_id, wafer_count=25):
        self.batch_id = batch_id
        self.wafer_count = wafer_count
        self.current_slot = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_slot >= self.wafer_count:
            raise StopIteration

        wafer = {
            'batch_id': self.batch_id,
            'slot': self.current_slot,
            'wafer_id': f"W{self.batch_id}_{self.current_slot:02d}",
            'status': self.check_wafer_status(self.current_slot)
        }

        self.current_slot += 1
        return wafer

# 사용
batch = WaferBatchIterator("B001", wafer_count=25)

for wafer in batch:
    if wafer['status'] == 'defective':
        mark_for_rework(wafer)
```

**reversed() 지원**:
```python
class ReversibleCollection:
    def __init__(self, items):
        self.items = items

    def __iter__(self):
        return iter(self.items)

    def __reversed__(self):
        return reversed(self.items)

coll = ReversibleCollection([1, 2, 3])
print(list(coll))           # [1, 2, 3]
print(list(reversed(coll))) # [3, 2, 1]
```

</div>
</div>

---

## Magic Methods (Dunder Methods)

### ✨ Python Special Methods

**객체 동작 커스터마이징**

<div class="grid grid-cols-2 gap-8">
<div>

```python
class Equipment:
    """Magic Methods를 활용한 장비 클래스"""

    def __init__(self, equipment_id, name, capacity):
        self.equipment_id = equipment_id
        self.name = name
        self.capacity = capacity
        self.current_load = 0

    # 문자열 표현
    def __str__(self):
        """사용자용 문자열 (print)"""
        return f"{self.name} ({self.equipment_id})"

    def __repr__(self):
        """개발자용 문자열 (디버깅)"""
        return (f"Equipment(equipment_id='{self.equipment_id}', "
                f"name='{self.name}', capacity={self.capacity})")

    # 비교 연산자
    def __eq__(self, other):
        """=="""
        if not isinstance(other, Equipment):
            return NotImplemented
        return self.equipment_id == other.equipment_id

    def __lt__(self, other):
        """<"""
        if not isinstance(other, Equipment):
            return NotImplemented
        return self.current_load < other.current_load

    def __le__(self, other):
        """<="""
        return self < other or self == other

    # 산술 연산자
    def __add__(self, wafer_count):
        """+ (웨이퍼 추가)"""
        new_load = self.current_load + wafer_count
        if new_load > self.capacity:
            raise ValueError(
                f"Exceeds capacity {self.capacity}")

        result = Equipment(
            self.equipment_id, self.name, self.capacity)
        result.current_load = new_load
        return result

    def __iadd__(self, wafer_count):
        """+= (in-place)"""
        self.current_load += wafer_count
        if self.current_load > self.capacity:
            raise ValueError("Exceeds capacity")
        return self

    # 컨테이너 프로토콜
    def __len__(self):
        """len()"""
        return self.current_load

    def __bool__(self):
        """bool() / if 문"""
        return self.current_load > 0

    # Callable
    def __call__(self, command):
        """함수처럼 호출 가능"""
        if command == "start":
            self.start_process()
        elif command == "stop":
            self.stop_process()
        return f"Executed: {command}"

    # Context Manager
    def __enter__(self):
        """with 진입"""
        self.start_process()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """with 종료"""
        self.stop_process()
        return False

    # 해시 (dict 키로 사용)
    def __hash__(self):
        """hash()"""
        return hash(self.equipment_id)

# 사용 예시
e1 = Equipment("E001", "Etcher", 25)
e2 = Equipment("E002", "CVD", 25)

# __str__, __repr__
print(e1)          # Etcher (E001)
print(repr(e1))    # Equipment(equipment_id='E001', ...)

# __eq__, __lt__
print(e1 == e2)    # False
e1.current_load = 10
e2.current_load = 15
print(e1 < e2)     # True

# __add__, __iadd__
e3 = e1 + 5        # 새 객체 생성
e1 += 3            # 자기 자신 수정

# __len__, __bool__
print(len(e1))     # 13
if e1:
    print("Has wafers")

# __call__
e1("start")        # 함수처럼 호출

# __enter__, __exit__
with e1:
    # 자동 start
    process_wafers()
# 자동 stop

# __hash__
equipment_dict = {e1: "Running", e2: "Idle"}
```

</div>
<div>

**주요 Magic Methods**:

**문자열 표현**:
- `__str__()`: `print()`, `str()`
  - 사용자 친화적
- `__repr__()`: `repr()`, 디버깅
  - 재생성 가능한 표현
- `__format__()`: `f"{obj:format}"`

**비교 연산자**:
- `__eq__(self, other)`: `==`
- `__ne__(self, other)`: `!=`
- `__lt__(self, other)`: `<`
- `__le__(self, other)`: `<=`
- `__gt__(self, other)`: `>`
- `__ge__(self, other)`: `>=`

**산술 연산자**:
- `__add__(self, other)`: `+`
- `__sub__(self, other)`: `-`
- `__mul__(self, other)`: `*`
- `__truediv__(self, other)`: `/`
- `__iadd__(self, other)`: `+=` (in-place)

**컨테이너**:
- `__len__()`: `len(obj)`
- `__getitem__(key)`: `obj[key]`
- `__setitem__(key, value)`: `obj[key] = value`
- `__delitem__(key)`: `del obj[key]`
- `__contains__(item)`: `item in obj`

**실무 예시: 데이터 컨테이너**:
```python
class SensorDataCollection:
    def __init__(self):
        self.data = []

    def __getitem__(self, index):
        """인덱싱/슬라이싱"""
        return self.data[index]

    def __setitem__(self, index, value):
        """값 설정"""
        self.data[index] = value

    def __len__(self):
        return len(self.data)

    def __contains__(self, value):
        """in 연산자"""
        return value in self.data

collection = SensorDataCollection()
collection[0] = 25.5
print(len(collection))
print(25.5 in collection)
```

**Callable 객체**:
```python
class Alarm:
    def __init__(self, threshold):
        self.threshold = threshold
        self.triggered = False

    def __call__(self, value):
        """함수처럼 호출"""
        if value > self.threshold:
            self.triggered = True
            return "ALARM!"
        return "OK"

alarm = Alarm(threshold=100)
print(alarm(95))   # OK
print(alarm(105))  # ALARM!
```

**속성 접근**:
- `__getattr__(name)`: 없는 속성 접근
- `__setattr__(name, value)`: 속성 설정
- `__delattr__(name)`: 속성 삭제
- `__getattribute__(name)`: 모든 속성 접근

```python
class DynamicEquipment:
    def __getattr__(self, name):
        """없는 속성 → 센서 읽기"""
        if name.startswith('sensor_'):
            return self.read_sensor(name)
        raise AttributeError(name)

equip = DynamicEquipment()
print(equip.sensor_temperature)  # 동적 생성
```

</div>
</div>

---

### 🎭 Advanced Magic Methods

**컨텍스트, Descriptor, 메타클래스**

<div class="grid grid-cols-2 gap-8">
<div>

```python
# 1. Context Manager Protocol
class DatabaseTransaction:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def __enter__(self):
        """with 진입"""
        import sqlite3
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("BEGIN TRANSACTION")
        print("Transaction started")
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        """with 종료"""
        if exc_type is None:
            # 정상 종료: commit
            self.connection.commit()
            print("Transaction committed")
        else:
            # 예외 발생: rollback
            self.connection.rollback()
            print(f"Transaction rolled back: {exc_val}")

        self.connection.close()
        return False  # 예외 전파

# 사용
with DatabaseTransaction("equipment.db") as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ...")
    # 에러 발생 시 자동 롤백

# 2. Descriptor Protocol
class ValidatedAttribute:
    def __init__(self, validator):
        self.validator = validator
        self.data = {}

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.data.get(id(instance), None)

    def __set__(self, instance, value):
        if not self.validator(value):
            raise ValueError(
                f"Invalid {self.name}: {value}")
        self.data[id(instance)] = value

    def __delete__(self, instance):
        self.data.pop(id(instance), None)

class Equipment:
    # Descriptor 사용
    temperature = ValidatedAttribute(
        lambda x: 0 <= x <= 300)
    pressure = ValidatedAttribute(
        lambda x: 0 <= x <= 10)

    def __init__(self, temp, pressure):
        self.temperature = temp  # 검증됨
        self.pressure = pressure

# 3. 연산자 오버로딩 고급
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        """벡터 덧셈"""
        return Vector(
            self.x + other.x,
            self.y + other.y)

    def __mul__(self, scalar):
        """스칼라 곱"""
        return Vector(
            self.x * scalar,
            self.y * scalar)

    def __rmul__(self, scalar):
        """역순 곱셈 (3 * vector)"""
        return self * scalar

    def __abs__(self):
        """크기"""
        return (self.x**2 + self.y**2)**0.5

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(3, 4)
v2 = Vector(1, 2)
print(v1 + v2)      # Vector(4, 6)
print(v1 * 2)       # Vector(6, 8)
print(3 * v1)       # Vector(9, 12)
print(abs(v1))      # 5.0
```

</div>
<div>

**4. 인덱싱/슬라이싱 고급**:
```python
class Matrix:
    def __init__(self, rows, cols):
        self.data = [
            [0] * cols for _ in range(rows)]
        self.rows = rows
        self.cols = cols

    def __getitem__(self, key):
        """인덱싱/슬라이싱"""
        if isinstance(key, tuple):
            # matrix[i, j]
            row, col = key
            return self.data[row][col]
        else:
            # matrix[i]
            return self.data[key]

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            row, col = key
            self.data[row][col] = value
        else:
            self.data[key] = value

m = Matrix(3, 3)
m[0, 0] = 1
m[1, 1] = 2
print(m[0, 0])  # 1
```

**5. 메타클래스 기초**:
```python
class SingletonMeta(type):
    """싱글톤 메타클래스"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(
                *args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class EquipmentManager(metaclass=SingletonMeta):
    def __init__(self):
        self.equipment = []

# 항상 같은 인스턴스
m1 = EquipmentManager()
m2 = EquipmentManager()
print(m1 is m2)  # True
```

**6. 프로퍼티 고급**:
```python
class CachedProperty:
    """캐싱 프로퍼티"""
    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __get__(self, instance, owner):
        if instance is None:
            return self

        # 캐시 확인
        cache_name = f"_cached_{self.name}"
        if not hasattr(instance, cache_name):
            # 계산 및 캐싱
            value = self.func(instance)
            setattr(instance, cache_name, value)
            return value

        return getattr(instance, cache_name)

class DataAnalyzer:
    @CachedProperty
    def expensive_calculation(self):
        """비용이 큰 계산 (캐시됨)"""
        import time
        time.sleep(2)
        return sum(range(1000000))

analyzer = DataAnalyzer()
print(analyzer.expensive_calculation)  # 2초
print(analyzer.expensive_calculation)  # 즉시 (캐시)
```

**반도체 HMI 통합 예시**:
```python
class WaferProcessor:
    # Descriptor로 검증
    temperature = ValidatedAttribute(
        lambda x: -20 <= x <= 400)

    def __init__(self, processor_id):
        self.processor_id = processor_id
        self.wafers = []
        self.temperature = 25.0

    # 문자열 표현
    def __str__(self):
        return f"Processor {self.processor_id}"

    def __repr__(self):
        return (f"WaferProcessor("
                f"'{self.processor_id}', "
                f"wafers={len(self.wafers)})")

    # 컨테이너
    def __len__(self):
        return len(self.wafers)

    def __getitem__(self, index):
        return self.wafers[index]

    # Callable
    def __call__(self, wafer_id):
        """웨이퍼 처리"""
        return self.process_wafer(wafer_id)

    # Context Manager
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
```

</div>
</div>

---
