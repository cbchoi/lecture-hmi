# 🚀 이론 강의: PySide6 개념 및 Qt 아키텍처

---

## Python 디자인 패턴

### 🎯 Context Manager Pattern

**`with` 문을 통한 리소스 관리**

<div class="grid grid-cols-2 gap-8">
<div>

```python
# Context Manager Protocol
class DatabaseConnection:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def __enter__(self):
        """진입 시 실행: 리소스 획득"""
        import sqlite3
        self.connection = sqlite3.connect(self.db_path)
        print(f"Database {self.db_path} opened")
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        """종료 시 실행: 리소스 해제"""
        if self.connection:
            if exc_type is None:
                # 예외 없이 정상 종료
                self.connection.commit()
                print("Changes committed")
            else:
                # 예외 발생 시 롤백
                self.connection.rollback()
                print(f"Error occurred: {exc_val}")
                print("Changes rolled back")

            self.connection.close()
            print("Database closed")

        # False 반환 시 예외 전파, True 반환 시 예외 억제
        return False

# 사용
with DatabaseConnection("equipment.db") as conn:
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO equipment (id, name, status)
        VALUES (?, ?, ?)
    """, ("E001", "Etcher", "Running"))
    # with 블록 종료 시 자동으로 commit & close
```

**contextlib를 활용한 간편한 구현**:

```python
from contextlib import contextmanager
import time

@contextmanager
def timer(operation_name):
    """실행 시간 측정 컨텍스트"""
    start = time.perf_counter()
    print(f"Starting {operation_name}...")

    try:
        yield  # 여기서 with 블록 실행
    finally:
        elapsed = time.perf_counter() - start
        print(f"{operation_name} completed in {elapsed:.3f}s")

# 사용
with timer("Data Processing"):
    # 처리 작업
    process_sensor_data()
    calculate_statistics()
# 자동으로 시간 측정 및 출력
```

</div>
<div>

**Context Manager의 핵심**:
- **`__enter__()`**: with 진입 시 호출
  - 리소스 획득 (파일 열기, DB 연결 등)
  - 반환값이 `as` 변수로 전달

- **`__exit__()`**: with 종료 시 호출
  - 리소스 해제 (정리 작업)
  - 예외 발생 여부와 관계없이 실행
  - 예외 정보 수신 (exc_type, exc_val, exc_tb)

**장점**:
- 리소스 누수 방지
- 예외 안전성 보장
- 코드 가독성 향상
- RAII 패턴의 Python 구현

**반도체 HMI 적용**:

```python
@contextmanager
def equipment_operation(equipment_id):
    """장비 작업 컨텍스트"""
    equipment = get_equipment(equipment_id)

    # 시작 전 검증
    if not equipment.is_idle():
        raise EquipmentBusyError(equipment_id)

    equipment.start()
    equipment.log("Operation started")

    try:
        yield equipment
    except Exception as e:
        equipment.abort()
        equipment.log(f"Operation aborted: {e}")
        raise
    finally:
        equipment.stop()
        equipment.log("Operation completed")

# 사용
with equipment_operation("E001") as etcher:
    etcher.set_temperature(250)
    etcher.process_wafer("W12345")
    etcher.wait_until_complete()
# 자동으로 stop() 및 로깅
```

**다중 컨텍스트**:
```python
# 여러 리소스 동시 관리
with (
    DatabaseConnection("equipment.db") as db,
    LogFile("process.log") as log,
    equipment_operation("E001") as etcher
):
    log.write("Starting process")
    etcher.process_wafer("W001")
    db.cursor().execute("INSERT INTO ...")
# 모든 리소스 자동 정리 (역순)
```

**contextlib 유틸리티**:
```python
from contextlib import suppress, redirect_stdout

# 예외 무시
with suppress(FileNotFoundError):
    os.remove("temp_file.txt")

# 출력 리다이렉션
with open("output.txt", "w") as f:
    with redirect_stdout(f):
        print("이 내용은 파일로 저장됨")
```

</div>
</div>

---

### 🔧 Descriptor Pattern

**속성 접근 제어 및 검증**

<div class="grid grid-cols-2 gap-8">
<div>

```python
# Descriptor Protocol
class TemperatureDescriptor:
    def __init__(self, min_value=0, max_value=300):
        self.min_value = min_value
        self.max_value = max_value
        self.data = {}  # 인스턴스별 값 저장

    def __set_name__(self, owner, name):
        """Python 3.6+: descriptor 이름 자동 저장"""
        self.name = name

    def __get__(self, instance, owner):
        """값 읽기"""
        if instance is None:
            return self  # 클래스에서 접근 시
        return self.data.get(id(instance), self.min_value)

    def __set__(self, instance, value):
        """값 쓰기 (검증 포함)"""
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"{self.name} must be numeric, "
                f"got {type(value).__name__}"
            )

        if not (self.min_value <= value <= self.max_value):
            raise ValueError(
                f"{self.name} must be between "
                f"{self.min_value} and {self.max_value}, "
                f"got {value}"
            )

        self.data[id(instance)] = value
        print(f"{self.name} set to {value}")

    def __delete__(self, instance):
        """값 삭제"""
        self.data.pop(id(instance), None)

class Equipment:
    # Descriptor 인스턴스를 클래스 변수로 선언
    temperature = TemperatureDescriptor(0, 300)
    pressure = TemperatureDescriptor(0, 10)

    def __init__(self, equipment_id):
        self.equipment_id = equipment_id
        self.temperature = 25  # Descriptor를 통해 검증됨
        self.pressure = 1.0

# 사용
etcher = Equipment("E001")
etcher.temperature = 150  # OK
# 출력: temperature set to 150

try:
    etcher.temperature = 350  # ValueError!
except ValueError as e:
    print(e)
# 출력: temperature must be between 0 and 300, got 350

try:
    etcher.temperature = "hot"  # TypeError!
except TypeError as e:
    print(e)
# 출력: temperature must be numeric, got str
```

</div>
<div>

**Descriptor Protocol**:
- **`__get__(self, instance, owner)`**: 속성 읽기
- **`__set__(self, instance, value)`**: 속성 쓰기
- **`__delete__(self, instance)`**: 속성 삭제
- **`__set_name__(self, owner, name)`**: 이름 자동 설정

**장점**:
- 재사용 가능한 검증 로직
- DRY 원칙 준수
- @property보다 유연함
- 여러 속성에 동일 로직 적용

**실무 활용 - Typed Descriptor**:

```python
class TypedDescriptor:
    def __init__(self, expected_type,
                 validator=None, default=None):
        self.expected_type = expected_type
        self.validator = validator
        self.default = default
        self.data = {}

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.data.get(
            id(instance), self.default)

    def __set__(self, instance, value):
        if not isinstance(value,
                         self.expected_type):
            raise TypeError(
                f"{self.name} must be "
                f"{self.expected_type.__name__}")

        if self.validator and \
           not self.validator(value):
            raise ValueError(
                f"Invalid value for {self.name}: "
                f"{value}")

        self.data[id(instance)] = value

class WaferProcessor:
    # 타입 검증 + 커스텀 검증
    wafer_id = TypedDescriptor(
        str,
        validator=lambda x: x.startswith("W"),
        default=""
    )

    slot_number = TypedDescriptor(
        int,
        validator=lambda x: 1 <= x <= 25,
        default=1
    )

    temperature = TypedDescriptor(
        float,
        validator=lambda x: 0 <= x <= 400,
        default=25.0
    )

processor = WaferProcessor()
processor.wafer_id = "W12345"  # OK
processor.slot_number = 10     # OK
processor.temperature = 250.0  # OK

try:
    processor.wafer_id = 12345  # TypeError
except TypeError as e:
    print(e)

try:
    processor.slot_number = 30  # ValueError
except ValueError as e:
    print(e)
```

**@property와 비교**:
```python
# @property (단일 속성)
class Equipment:
    def __init__(self):
        self._temp = 0

    @property
    def temperature(self):
        return self._temp

    @temperature.setter
    def temperature(self, value):
        if not 0 <= value <= 300:
            raise ValueError("Out of range")
        self._temp = value

# Descriptor (재사용 가능)
class Equipment:
    temperature = RangeDescriptor(0, 300)
    pressure = RangeDescriptor(0, 10)
    voltage = RangeDescriptor(0, 500)
    # 검증 로직 재사용!
```

</div>
</div>

---

### 🏭 Property Pattern

**Pythonic한 getter/setter**

<div class="grid grid-cols-2 gap-8">
<div>

```python
class Equipment:
    def __init__(self, equipment_id):
        self.equipment_id = equipment_id
        self._temperature = 25.0
        self._status = "Idle"
        self._alarm_count = 0

    # Read-only property
    @property
    def equipment_id(self):
        """장비 ID (읽기 전용)"""
        return self._equipment_id

    @equipment_id.setter
    def equipment_id(self, value):
        # 초기 설정만 허용
        if hasattr(self, '_equipment_id'):
            raise AttributeError(
                "equipment_id is read-only after initialization")
        self._equipment_id = value

    # Read-write property with validation
    @property
    def temperature(self):
        """온도 (℃)"""
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Temperature must be numeric")

        if not (0 <= value <= 300):
            raise ValueError(
                f"Temperature {value} out of range [0, 300]")

        old_value = self._temperature
        self._temperature = value

        # 로깅
        print(f"Temperature changed: {old_value} → {value}")

        # 알람 체크
        if value > 250:
            self._trigger_high_temp_alarm()

    @temperature.deleter
    def temperature(self):
        """온도 리셋"""
        print("Resetting temperature to default")
        self._temperature = 25.0

    # Computed property (계산된 속성)
    @property
    def status_display(self):
        """사용자 표시용 상태 문자열"""
        alarm_suffix = ""
        if self._alarm_count > 0:
            alarm_suffix = f" ({self._alarm_count} alarms)"

        return f"[{self.equipment_id}] {self._status}" + alarm_suffix

    # Property with caching
    @property
    def is_healthy(self):
        """장비 건강 상태 (캐시됨)"""
        if not hasattr(self, '_health_cache'):
            # 비용이 큰 계산
            self._health_cache = self._calculate_health()
        return self._health_cache

    def invalidate_health_cache(self):
        """건강 상태 캐시 무효화"""
        if hasattr(self, '_health_cache'):
            delattr(self, '_health_cache')

    def _calculate_health(self):
        """건강 상태 계산 (비용이 큼)"""
        # 복잡한 계산 로직...
        return self._alarm_count == 0 and \
               self._temperature < 250
```

</div>
<div>

**@property 데코레이터**:
- **getter**: `@property`
- **setter**: `@<name>.setter`
- **deleter**: `@<name>.deleter`

**사용 패턴**:

**1. Read-only (읽기 전용)**:
```python
class Wafer:
    def __init__(self, wafer_id):
        self._id = wafer_id
        self._created_at = datetime.now()

    @property
    def wafer_id(self):
        return self._id
    # setter 없음 → 읽기 전용

wafer = Wafer("W001")
print(wafer.wafer_id)  # OK
wafer.wafer_id = "W002"  # AttributeError!
```

**2. Lazy Loading (지연 로딩)**:
```python
class DataAnalyzer:
    def __init__(self, data_path):
        self.data_path = data_path
        self._data = None  # 아직 로드 안 함

    @property
    def data(self):
        """데이터 지연 로딩"""
        if self._data is None:
            print("Loading data...")
            self._data = load_large_dataset(
                self.data_path)
        return self._data

analyzer = DataAnalyzer("sensors.csv")
# 여기까지는 데이터 로드 안 함
result = analyzer.data.mean()
# 첫 접근 시 로드
```

**3. Computed Property (계산)**:
```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height

    @property
    def perimeter(self):
        return 2 * (self.width + self.height)

rect = Rectangle(10, 5)
print(rect.area)       # 50 (계산됨)
print(rect.perimeter)  # 30 (계산됨)
```

**4. 변경 알림 (Change Notification)**:
```python
class ObservableEquipment:
    def __init__(self):
        self._temperature = 25
        self.observers = []

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        old = self._temperature
        self._temperature = value
        # 모든 옵저버에게 알림
        for observer in self.observers:
            observer.on_temperature_changed(
                old, value)
```

**장점**:
- Pythonic한 캡슐화
- 내부 구현 숨김
- 계산 로직 추상화
- 검증 및 로깅 중앙화

</div>
</div>

---

### 🎨 Decorator Pattern (함수/메서드)

**함수 동작 확장**

<div class="grid grid-cols-2 gap-8">
<div>

```python
import functools
import time
from typing import Callable

# 1. 기본 Decorator
def timer(func: Callable) -> Callable:
    """실행 시간 측정 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper

@timer
def process_wafer(wafer_id: str):
    print(f"Processing {wafer_id}...")
    time.sleep(1)
    return f"Completed {wafer_id}"

# 사용
result = process_wafer("W001")
# 출력:
# Processing W001...
# process_wafer took 1.001s

# 2. 파라미터를 받는 Decorator
def retry(max_attempts: int = 3,
          delay: float = 1.0):
    """재시도 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"Attempt {attempt} failed: {e}")
                    print(f"Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def unstable_sensor_read():
    """불안정한 센서 읽기"""
    import random
    if random.random() < 0.7:
        raise IOError("Sensor read failed")
    return 125.5

# 3. 클래스 Decorator
def singleton(cls):
    """싱글톤 패턴 구현"""
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self, db_path):
        self.db_path = db_path
        print(f"Connected to {db_path}")

# 항상 같은 인스턴스 반환
db1 = DatabaseConnection("equipment.db")
db2 = DatabaseConnection("equipment.db")
print(db1 is db2)  # True
```

</div>
<div>

**Decorator 핵심**:
- 함수/클래스를 받아 수정된 버전 반환
- 원본 코드 변경 없이 기능 추가
- `@` 문법으로 간편하게 적용
- `functools.wraps`로 메타데이터 보존

**반도체 HMI 적용 예시**:

```python
def log_equipment_operation(func):
    """장비 작업 로깅"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        logger.info(
            f"[{self.equipment_id}] "
            f"Starting {func.__name__}")

        try:
            result = func(self, *args, **kwargs)
            logger.info(
                f"[{self.equipment_id}] "
                f"{func.__name__} completed")
            return result
        except Exception as e:
            logger.error(
                f"[{self.equipment_id}] "
                f"{func.__name__} failed: {e}")
            raise

    return wrapper

def require_idle_state(func):
    """Idle 상태 검증"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.status != "Idle":
            raise EquipmentBusyError(
                f"Equipment {self.equipment_id} "
                f"is {self.status}")
        return func(self, *args, **kwargs)
    return wrapper

class Equipment:
    @log_equipment_operation
    @require_idle_state
    def start_process(self, recipe):
        """공정 시작"""
        self.status = "Running"
        self.execute_recipe(recipe)
        return True
```

**다중 Decorator 적용**:
```python
@timer
@retry(max_attempts=3)
@log_equipment_operation
def critical_operation():
    # 실행 순서 (아래에서 위로):
    # 1. log_equipment_operation
    # 2. retry
    # 3. timer
    pass
```

**functools.lru_cache (내장)**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(n):
    """비용이 큰 계산 (캐싱)"""
    time.sleep(1)
    return n ** 2

# 첫 호출: 1초 소요
result1 = expensive_calculation(10)

# 두 번째 호출: 즉시 반환 (캐시)
result2 = expensive_calculation(10)
```

**클래스 메서드 Decorator**:
```python
class Equipment:
    @staticmethod
    def validate_id(equipment_id: str):
        """정적 메서드"""
        return equipment_id.startswith("E")

    @classmethod
    def create_default(cls):
        """클래스 메서드"""
        return cls("E000", "Default")

    @property
    def status_code(self):
        """프로퍼티"""
        return self._status_code
```

</div>
</div>

---

## C# WPF vs Python PySide6 비교

### 아키텍처 및 철학의 차이

| 측면 | C# WPF | Python PySide6 |
|------|--------|----------------|
| **플랫폼** | Windows 전용 | 크로스 플랫폼 (Windows, Linux, macOS) |
| **언어** | C# (.NET) | Python |
| **UI 프레임워크** | WPF (Windows Presentation Foundation) | Qt 6.x |
| **데이터 바인딩** | XAML 기반 강력한 바인딩 | 시그널-슬롯 + 수동 바인딩 |
| **UI 설계** | XAML + Blend | Qt Designer + Python 코드 |
| **성능** | 네이티브 컴파일, 높은 성능 | 인터프리터 기반, 적당한 성능 |
| **개발 생산성** | Visual Studio 통합 | 유연한 IDE 선택 |

### 주요 개념 매핑

<div class="code-section">

**C# WPF → Python PySide6 개념 매핑**

```python
# C# WPF 개념 → PySide6 개념
"""
Window → QMainWindow, QWidget
UserControl → QWidget (커스텀)
DataBinding → Signal-Slot + Property
Command → Signal-Slot
MVVM → MVC/MVP (Model-View-Controller)
Dependency Injection → Python 모듈 시스템
ObservableCollection → QAbstractItemModel
INotifyPropertyChanged → QObject.signal
Event → Signal
"""

# 1. C# WPF의 Window
# public partial class MainWindow : Window
# {
#     public MainWindow() { InitializeComponent(); }
# }

# PySide6 equivalent
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import QObject, Signal

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()

# 2. C# WPF의 Data Binding
# <TextBox Text="{Binding Name}" />

# PySide6 equivalent - Signal/Slot 방식
class DataModel(QObject):
    nameChanged = Signal(str)  # C#의 PropertyChanged 이벤트와 유사

    def __init__(self):
        super().__init__()
        self._name = ""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self._name != value:
            self._name = value
            self.nameChanged.emit(value)  # 변경 알림

# 3. C# WPF의 Command
# <Button Command="{Binding SaveCommand}" />

# PySide6 equivalent - Signal/Slot
from PySide6.QtWidgets import QPushButton

button = QPushButton("Save")
button.clicked.connect(self.save_data)  # 직접 연결
```

</div>

## PySide6 핵심 구조

### Qt 모듈 구조

<div class="code-section">

**주요 PySide6 모듈**

```python
# 1. QtWidgets - GUI 위젯 및 레이아웃
from PySide6.QtWidgets import (
    QApplication,        # 애플리케이션 객체
    QMainWindow,         # 메인 윈도우
    QWidget,            # 기본 위젯
    QPushButton,        # 버튼
    QLabel,             # 레이블
    QLineEdit,          # 텍스트 입력
    QTableWidget,       # 테이블
    QVBoxLayout,        # 수직 레이아웃
    QHBoxLayout,        # 수평 레이아웃
    QGridLayout,        # 그리드 레이아웃
    QSplitter,          # 분할 위젯
    QTabWidget,         # 탭 위젯
    QTreeWidget,        # 트리 위젯
    QGraphicsView,      # 그래픽 뷰
    QMenuBar,           # 메뉴바
    QStatusBar,         # 상태바
    QToolBar,           # 툴바
    QDockWidget,        # 도킹 위젯
)

# 2. QtCore - 핵심 기능 (시그널, 슬롯, 타이머 등)
from PySide6.QtCore import (
    QObject,            # 모든 Qt 객체의 기본 클래스
    Signal,             # 시그널 정의
    Slot,               # 슬롯 데코레이터
    QTimer,             # 타이머
    QThread,            # 스레드
    QSettings,          # 설정 관리
    QFileInfo,          # 파일 정보
    QDir,               # 디렉토리
    QDateTime,          # 날짜/시간
    QSize,              # 크기
    QPoint,             # 좌표
    QRect,              # 사각형
    Property,           # 프로퍼티
    QAbstractItemModel, # 데이터 모델
)

# 3. QtGui - 그래픽 및 입력 처리
from PySide6.QtGui import (
    QPixmap,            # 이미지
    QIcon,              # 아이콘
    QFont,              # 폰트
    QColor,             # 색상
    QPainter,           # 그리기
    QPen,               # 펜
    QBrush,             # 브러시
    QKeySequence,       # 키 시퀀스
    QAction,            # 액션
    QValidator,         # 입력 검증
)

# 4. QtCharts - 차트 위젯 (별도 설치 필요)
from PySide6.QtCharts import (
    QChart,             # 차트
    QChartView,         # 차트 뷰
    QLineSeries,        # 라인 시리즈
    QBarSeries,         # 바 시리즈
    QValueAxis,         # 값 축
)

# 5. QtOpenGL - OpenGL 지원
from PySide6.QtOpenGL import QOpenGLWidget

# 6. Qt3DCore, Qt3DRender - 3D 지원 (고급)
# from PySide6.Qt3DCore import QEntity
# from PySide6.Qt3DRender import QCamera
```

</div>

### 시그널-슬롯 메커니즘

<div class="code-section">

**시그널-슬롯 패턴 이해**

```python
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout

class EquipmentController(QObject):
    """장비 컨트롤러 - 시그널 정의"""

    # 커스텀 시그널 정의
    temperatureChanged = Signal(float)          # 온도 변경 시그널
    pressureChanged = Signal(float)             # 압력 변경 시그널
    statusChanged = Signal(str)                 # 상태 변경 시그널
    errorOccurred = Signal(str, int)            # 에러 발생 시그널 (메시지, 코드)
    processCompleted = Signal(bool, str)        # 프로세스 완료 시그널

    def __init__(self):
        super().__init__()
        self._temperature = 0.0
        self._pressure = 0.0
        self._status = "Idle"

    def update_temperature(self, temp):
        """온도 업데이트 및 시그널 발송"""
        if self._temperature != temp:
            self._temperature = temp
            self.temperatureChanged.emit(temp)

            # 임계값 검사
            if temp > 200:
                self.errorOccurred.emit(f"High temperature: {temp}°C", 1001)

    def update_pressure(self, pressure):
        """압력 업데이트 및 시그널 발송"""
        if self._pressure != pressure:
            self._pressure = pressure
            self.pressureChanged.emit(pressure)

    def set_status(self, status):
        """상태 변경 및 시그널 발송"""
        if self._status != status:
            old_status = self._status
            self._status = status
            self.statusChanged.emit(status)
            print(f"Status changed: {old_status} → {status}")

class EquipmentDisplay(QWidget):
    """장비 디스플레이 - 슬롯 정의"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setupUI()
        self.connectSignals()

    def setupUI(self):
        """UI 구성"""
        layout = QVBoxLayout()

        # 온도 표시
        self.temp_label = QLabel("Temperature: 0°C")
        layout.addWidget(self.temp_label)

        # 압력 표시
        self.pressure_label = QLabel("Pressure: 0 Torr")
        layout.addWidget(self.pressure_label)

        # 상태 표시
        self.status_label = QLabel("Status: Idle")
        layout.addWidget(self.status_label)

        # 에러 메시지
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.error_label)

        # 제어 버튼
        self.start_button = QPushButton("Start Process")
        self.stop_button = QPushButton("Stop Process")
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def connectSignals(self):
        """시그널-슬롯 연결"""
        # 컨트롤러 시그널을 디스플레이 슬롯에 연결
        self.controller.temperatureChanged.connect(self.on_temperature_changed)
        self.controller.pressureChanged.connect(self.on_pressure_changed)
        self.controller.statusChanged.connect(self.on_status_changed)
        self.controller.errorOccurred.connect(self.on_error_occurred)

        # 버튼 클릭을 컨트롤러 메서드에 연결
        self.start_button.clicked.connect(self.start_process)
        self.stop_button.clicked.connect(self.stop_process)

    @Slot(float)
    def on_temperature_changed(self, temp):
        """온도 변경 슬롯"""
        self.temp_label.setText(f"Temperature: {temp:.1f}°C")

        # 온도에 따른 색상 변경
        if temp > 200:
            self.temp_label.setStyleSheet("color: red; font-weight: bold;")
        elif temp > 150:
            self.temp_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.temp_label.setStyleSheet("color: green;")

    @Slot(float)
    def on_pressure_changed(self, pressure):
        """압력 변경 슬롯"""
        self.pressure_label.setText(f"Pressure: {pressure:.2f} Torr")

    @Slot(str)
    def on_status_changed(self, status):
        """상태 변경 슬롯"""
        self.status_label.setText(f"Status: {status}")

        # 상태에 따른 버튼 활성화/비활성화
        if status == "Running":
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    @Slot(str, int)
    def on_error_occurred(self, message, error_code):
        """에러 발생 슬롯"""
        self.error_label.setText(f"ERROR {error_code}: {message}")

        # 3초 후 에러 메시지 지우기
        QTimer.singleShot(3000, lambda: self.error_label.setText(""))

    def start_process(self):
        """프로세스 시작"""
        self.controller.set_status("Running")

        # 시뮬레이션을 위한 타이머 설정
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.simulate_data)
        self.simulation_timer.start(1000)  # 1초마다 실행

    def stop_process(self):
        """프로세스 정지"""
        if hasattr(self, 'simulation_timer'):
            self.simulation_timer.stop()
        self.controller.set_status("Idle")

    def simulate_data(self):
        """데이터 시뮬레이션"""
        import random

        # 랜덤 온도/압력 생성
        temp = random.uniform(20, 250)
        pressure = random.uniform(0.1, 5.0)

        self.controller.update_temperature(temp)
        self.controller.update_pressure(pressure)

# 사용 예시
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 컨트롤러와 디스플레이 생성
    controller = EquipmentController()
    display = EquipmentDisplay(controller)

    display.show()
    sys.exit(app.exec())
```

</div>

## Python 생태계와 데이터 처리

### 반도체 HMI에 유용한 Python 라이브러리

<div class="code-section">

**핵심 라이브러리 및 활용**

```python
# 1. NumPy - 수치 계산 및 배열 처리
import numpy as np

class SensorDataProcessor:
    """센서 데이터 처리 클래스"""

    def __init__(self):
        self.temperature_history = np.array([])
        self.pressure_history = np.array([])

    def add_temperature_data(self, temp_data):
        """온도 데이터 추가"""
        self.temperature_history = np.append(self.temperature_history, temp_data)

        # 최근 100개 데이터만 유지
        if len(self.temperature_history) > 100:
            self.temperature_history = self.temperature_history[-100:]

    def calculate_statistics(self):
        """통계 계산"""
        if len(self.temperature_history) == 0:
            return None

        return {
            'mean': np.mean(self.temperature_history),
            'std': np.std(self.temperature_history),
            'min': np.min(self.temperature_history),
            'max': np.max(self.temperature_history),
            'trend': self.calculate_trend()
        }

    def calculate_trend(self):
        """트렌드 계산 (선형 회귀)"""
        if len(self.temperature_history) < 2:
            return 0

        x = np.arange(len(self.temperature_history))
        y = self.temperature_history

        # 최소제곱법으로 기울기 계산
        slope, _ = np.polyfit(x, y, 1)
        return slope

# 2. Pandas - 데이터 프레임 및 시계열 처리
import pandas as pd
from datetime import datetime, timedelta

class EquipmentDataLogger:
    """장비 데이터 로깅"""

    def __init__(self):
        self.data = pd.DataFrame(columns=[
            'timestamp', 'equipment_id', 'temperature',
            'pressure', 'gas_flow', 'status'
        ])

    def log_data(self, equipment_id, temperature, pressure, gas_flow, status):
        """데이터 로깅"""
        new_row = {
            'timestamp': datetime.now(),
            'equipment_id': equipment_id,
            'temperature': temperature,
            'pressure': pressure,
            'gas_flow': gas_flow,
            'status': status
        }

        # DataFrame에 새 행 추가 (pandas 2.0+ 방식)
        self.data = pd.concat([self.data, pd.DataFrame([new_row])],
                             ignore_index=True)

    def get_recent_data(self, equipment_id, hours=1):
        """최근 데이터 조회"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        mask = (self.data['equipment_id'] == equipment_id) & \
               (self.data['timestamp'] >= cutoff_time)

        return self.data[mask].copy()

    def export_to_csv(self, filename):
        """CSV로 내보내기"""
        self.data.to_csv(filename, index=False)

    def get_hourly_summary(self, equipment_id):
        """시간별 요약 통계"""
        equipment_data = self.data[self.data['equipment_id'] == equipment_id].copy()

        if equipment_data.empty:
            return pd.DataFrame()

        # 시간별 그룹핑
        equipment_data.set_index('timestamp', inplace=True)
        hourly_stats = equipment_data.resample('H').agg({
            'temperature': ['mean', 'min', 'max', 'std'],
            'pressure': ['mean', 'min', 'max', 'std'],
            'gas_flow': ['mean', 'min', 'max', 'std']
        })

        return hourly_stats

# 3. Matplotlib - 데이터 시각화
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class RealTimeChart(FigureCanvas):
    """실시간 차트 위젯"""

    def __init__(self, parent=None):
        self.figure = Figure(figsize=(10, 6))
        super().__init__(self.figure)
        self.setParent(parent)

        # 서브플롯 생성
        self.ax1 = self.figure.add_subplot(2, 1, 1)
        self.ax2 = self.figure.add_subplot(2, 1, 2)

        # 데이터 저장용 리스트
        self.time_data = []
        self.temp_data = []
        self.pressure_data = []

        # 라인 객체 생성
        self.temp_line, = self.ax1.plot([], [], 'r-', label='Temperature')
        self.pressure_line, = self.ax2.plot([], [], 'b-', label='Pressure')

        # 축 설정
        self.ax1.set_ylabel('Temperature (°C)')
        self.ax1.legend()
        self.ax1.grid(True)

        self.ax2.set_ylabel('Pressure (Torr)')
        self.ax2.set_xlabel('Time')
        self.ax2.legend()
        self.ax2.grid(True)

        # 타이트한 레이아웃
        self.figure.tight_layout()

    def update_data(self, timestamp, temperature, pressure):
        """데이터 업데이트"""
        self.time_data.append(timestamp)
        self.temp_data.append(temperature)
        self.pressure_data.append(pressure)

        # 최근 50개 데이터만 유지
        if len(self.time_data) > 50:
            self.time_data = self.time_data[-50:]
            self.temp_data = self.temp_data[-50:]
            self.pressure_data = self.pressure_data[-50:]

        # 차트 업데이트
        self.update_chart()

    def update_chart(self):
        """차트 업데이트"""
        if not self.time_data:
            return

        # 데이터 설정
        self.temp_line.set_data(self.time_data, self.temp_data)
        self.pressure_line.set_data(self.time_data, self.pressure_data)

        # 축 범위 자동 조정
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()

        # 그래프 다시 그리기
        self.draw()

# 4. PySerial - 시리얼 통신 (장비 연동)
import serial
import serial.tools.list_ports
from PySide6.QtCore import QThread, Signal

class SerialCommunication(QThread):
    """시리얼 통신 스레드"""

    dataReceived = Signal(str)
    errorOccurred = Signal(str)

    def __init__(self, port, baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.running = False

    def run(self):
        """스레드 실행"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            self.running = True

            while self.running:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.readline().decode('utf-8').strip()
                    self.dataReceived.emit(data)

                self.msleep(100)  # 100ms 대기

        except serial.SerialException as e:
            self.errorOccurred.emit(f"Serial error: {str(e)}")
        except Exception as e:
            self.errorOccurred.emit(f"Unexpected error: {str(e)}")
        finally:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()

    def stop(self):
        """통신 중지"""
        self.running = False
        self.wait()

    def send_command(self, command):
        """명령 전송"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(f"{command}\n".encode('utf-8'))

    @staticmethod
    def get_available_ports():
        """사용 가능한 포트 목록"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
```

</div>

---

