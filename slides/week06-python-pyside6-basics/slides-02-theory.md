# 🚀 이론 강의: PySide6 개념 및 Qt 아키텍처 (45분)

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

