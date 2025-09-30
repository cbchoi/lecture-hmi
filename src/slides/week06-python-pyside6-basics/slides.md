# Python PySide6 기초 및 크로스 플랫폼 HMI 개발
## C# WPF에서 Python PySide6로의 전환

---

# 📋 강의 개요

## 🎯 학습 목표
- C# WPF에서 Python PySide6로의 효과적인 전환 및 크로스 플랫폼 HMI 개발 능력 습득
- Qt Designer를 활용한 GUI 설계 및 시그널-슬롯 메커니즘 이해
- 반도체 장비 데이터 처리를 위한 Python 생태계 활용 (NumPy, Pandas, Matplotlib)
- 객체지향 프로그래밍과 MVC 패턴을 적용한 확장 가능한 HMI 아키텍처 구현

## ⏰ 세션 구성
- **이론 강의**: 45분 (PySide6 개념, Qt 아키텍처, C#과의 차이점)
- **기초 실습**: 45분 (Qt Designer UI 설계 및 기본 위젯 활용)
- **심화 실습**: 45분 (시그널-슬롯, 데이터 모델링, 파일 처리)
- **Hands-on**: 45분 (간단한 장비 모니터링 애플리케이션 구현)

---

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

# 🛠️ 기초 실습: Qt Designer UI 설계 및 기본 위젯 활용 (45분)

## Qt Designer를 활용한 UI 설계

### 설치 및 기본 사용법

<div class="code-section">

**Qt Designer 설치 및 실행**

```bash
# PySide6 및 Qt Designer 설치
pip install PySide6
pip install PySide6-tools

# Qt Designer 실행 (Windows)
pyside6-designer

# Linux/Mac에서는 PATH에 추가하거나 직접 실행
python -m PySide6.QtDesigner
```

</div>

### 기본 HMI 인터페이스 설계

<div class="code-section">

**equipment_monitor.ui 파일 구성**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>EquipmentMonitorWidget</class>
 <widget class="QWidget" name="EquipmentMonitorWidget">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Equipment Monitor</string>
  </property>
  <layout class="QGridLayout" name="gridLayout">
   <!-- 헤더 영역 -->
   <item row="0" column="0" colspan="3">
    <widget class="QLabel" name="titleLabel">
     <property name="text">
      <string>Semiconductor Equipment Monitor</string>
     </property>
     <property name="alignment">
      <set>Qt::AlignCenter</set>
     </property>
     <property name="font">
      <font>
       <pointsize>16</pointsize>
       <weight>75</weight>
       <bold>true</bold>
      </font>
     </property>
    </widget>
   </item>

   <!-- 상태 표시 영역 -->
   <item row="1" column="0">
    <widget class="QGroupBox" name="statusGroupBox">
     <property name="title">
      <string>Equipment Status</string>
     </property>
     <layout class="QFormLayout" name="statusFormLayout">
      <item row="0" column="0">
       <widget class="QLabel" name="equipmentIdLabel">
        <property name="text">
         <string>Equipment ID:</string>
        </property>
       </widget>
      </item>
      <item row="0" column="1">
       <widget class="QComboBox" name="equipmentIdComboBox">
        <item>
         <property name="text">
          <string>CVD-001</string>
         </property>
        </item>
        <item>
         <property name="text">
          <string>PVD-002</string>
         </property>
        </item>
        <item>
         <property name="text">
          <string>ETCH-003</string>
         </property>
        </item>
       </widget>
      </item>
      <item row="1" column="0">
       <widget class="QLabel" name="statusLabel">
        <property name="text">
         <string>Status:</string>
        </property>
       </widget>
      </item>
      <item row="1" column="1">
       <widget class="QLabel" name="statusValueLabel">
        <property name="text">
         <string>Idle</string>
        </property>
        <property name="styleSheet">
         <string>color: green; font-weight: bold;</string>
        </property>
       </widget>
      </item>
     </layout>
    </widget>
   </item>

   <!-- 센서 데이터 영역 -->
   <item row="1" column="1">
    <widget class="QGroupBox" name="sensorGroupBox">
     <property name="title">
      <string>Sensor Data</string>
     </property>
     <layout class="QGridLayout" name="sensorGridLayout">
      <!-- 온도 -->
      <item row="0" column="0">
       <widget class="QLabel" name="temperatureLabel">
        <property name="text">
         <string>Temperature:</string>
        </property>
       </widget>
      </item>
      <item row="0" column="1">
       <widget class="QLabel" name="temperatureValueLabel">
        <property name="text">
         <string>0.0 °C</string>
        </property>
       </widget>
      </item>
      <item row="0" column="2">
       <widget class="QProgressBar" name="temperatureProgressBar">
        <property name="maximum">
         <number>300</number>
        </property>
        <property name="value">
         <number>0</number>
        </property>
        <property name="format">
         <string>%v°C</string>
        </property>
       </widget>
      </item>

      <!-- 압력 -->
      <item row="1" column="0">
       <widget class="QLabel" name="pressureLabel">
        <property name="text">
         <string>Pressure:</string>
        </property>
       </widget>
      </item>
      <item row="1" column="1">
       <widget class="QLabel" name="pressureValueLabel">
        <property name="text">
         <string>0.0 Torr</string>
        </property>
       </widget>
      </item>
      <item row="1" column="2">
       <widget class="QProgressBar" name="pressureProgressBar">
        <property name="maximum">
         <number>10</number>
        </property>
        <property name="value">
         <number>0</number>
        </property>
        <property name="format">
         <string>%v Torr</string>
        </property>
       </widget>
      </item>

      <!-- 가스 유량 -->
      <item row="2" column="0">
       <widget class="QLabel" name="gasFlowLabel">
        <property name="text">
         <string>Gas Flow:</string>
        </property>
       </widget>
      </item>
      <item row="2" column="1">
       <widget class="QLabel" name="gasFlowValueLabel">
        <property name="text">
         <string>0.0 sccm</string>
        </property>
       </widget>
      </item>
      <item row="2" column="2">
       <widget class="QProgressBar" name="gasFlowProgressBar">
        <property name="maximum">
         <number>1000</number>
        </property>
        <property name="value">
         <number>0</number>
        </property>
        <property name="format">
         <string>%v sccm</string>
        </property>
       </widget>
      </item>
     </layout>
    </widget>
   </item>

   <!-- 제어 버튼 영역 -->
   <item row="1" column="2">
    <widget class="QGroupBox" name="controlGroupBox">
     <property name="title">
      <string>Process Control</string>
     </property>
     <layout class="QVBoxLayout" name="controlVBoxLayout">
      <item>
       <widget class="QPushButton" name="startButton">
        <property name="text">
         <string>Start Process</string>
        </property>
        <property name="styleSheet">
         <string>QPushButton { background-color: green; color: white; font-weight: bold; }</string>
        </property>
       </widget>
      </item>
      <item>
       <widget class="QPushButton" name="stopButton">
        <property name="text">
         <string>Stop Process</string>
        </property>
        <property name="enabled">
         <bool>false</bool>
        </property>
        <property name="styleSheet">
         <string>QPushButton { background-color: red; color: white; font-weight: bold; }</string>
        </property>
       </widget>
      </item>
      <item>
       <widget class="QPushButton" name="pauseButton">
        <property name="text">
         <string>Pause Process</string>
        </property>
        <property name="enabled">
         <bool>false</bool>
        </property>
        <property name="styleSheet">
         <string>QPushButton { background-color: orange; color: white; font-weight: bold; }</string>
        </property>
       </widget>
      </item>
      <item>
       <spacer name="verticalSpacer">
        <property name="orientation">
         <enum>Qt::Vertical</enum>
        </property>
        <property name="sizeHint" stdset="0">
         <size>
          <width>20</width>
          <height>40</height>
         </size>
        </property>
       </spacer>
      </item>
      <item>
       <widget class="QPushButton" name="settingsButton">
        <property name="text">
         <string>Settings</string>
        </property>
       </widget>
      </item>
     </layout>
    </widget>
   </item>

   <!-- 데이터 테이블 영역 -->
   <item row="2" column="0" colspan="3">
    <widget class="QTabWidget" name="dataTabWidget">
     <property name="currentIndex">
      <number>0</number>
     </property>
     <widget class="QWidget" name="realtimeTab">
      <attribute name="title">
       <string>Real-time Data</string>
      </attribute>
      <layout class="QVBoxLayout" name="realtimeVBoxLayout">
       <item>
        <widget class="QTableWidget" name="dataTableWidget">
         <property name="columnCount">
          <number>5</number>
         </property>
         <column>
          <property name="text">
           <string>Timestamp</string>
          </property>
         </column>
         <column>
          <property name="text">
           <string>Temperature</string>
          </property>
         </column>
         <column>
          <property name="text">
           <string>Pressure</string>
          </property>
         </column>
         <column>
          <property name="text">
           <string>Gas Flow</string>
          </property>
         </column>
         <column>
          <property name="text">
           <string>Status</string>
          </property>
         </column>
        </widget>
       </item>
      </layout>
     </widget>
     <widget class="QWidget" name="chartTab">
      <attribute name="title">
       <string>Chart View</string>
      </attribute>
      <layout class="QVBoxLayout" name="chartVBoxLayout">
       <!-- 여기에 matplotlib 차트 위젯이 들어갈 예정 -->
      </layout>
     </widget>
    </widget>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
```

</div>

### .ui 파일을 Python 코드와 연동

<div class="code-section">

**equipment_monitor.py - UI 파일 연동**

```python
import sys
import os
from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer, Signal, Slot
import random

class EquipmentMonitorWidget(QWidget):
    """장비 모니터링 위젯"""

    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_connections()
        self.setup_simulation()

        # 데이터 저장용
        self.data_history = []

    def load_ui(self):
        """UI 파일 로드"""
        loader = QUiLoader()
        ui_file = QFile("equipment_monitor.ui")

        if not ui_file.open(QFile.ReadOnly):
            print(f"Cannot open UI file: {ui_file.errorString()}")
            return

        self.ui = loader.load(ui_file)
        ui_file.close()

        if not self.ui:
            print("Failed to load UI file")
            return

        # 메인 레이아웃에 UI 추가
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

        # 윈도우 설정
        self.setWindowTitle("Equipment Monitor")
        self.resize(800, 600)

    def setup_connections(self):
        """시그널-슬롯 연결"""
        # 버튼 연결
        self.ui.startButton.clicked.connect(self.start_process)
        self.ui.stopButton.clicked.connect(self.stop_process)
        self.ui.pauseButton.clicked.connect(self.pause_process)
        self.ui.settingsButton.clicked.connect(self.open_settings)

        # 장비 선택 변경
        self.ui.equipmentIdComboBox.currentTextChanged.connect(self.on_equipment_changed)

    def setup_simulation(self):
        """시뮬레이션 타이머 설정"""
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.update_sensor_data)
        # 시작하지 않음 - Start 버튼을 누르면 시작

    @Slot()
    def start_process(self):
        """프로세스 시작"""
        self.ui.statusValueLabel.setText("Running")
        self.ui.statusValueLabel.setStyleSheet("color: green; font-weight: bold;")

        # 버튼 상태 변경
        self.ui.startButton.setEnabled(False)
        self.ui.stopButton.setEnabled(True)
        self.ui.pauseButton.setEnabled(True)

        # 시뮬레이션 시작
        self.simulation_timer.start(1000)  # 1초마다 업데이트

        print("Process started")

    @Slot()
    def stop_process(self):
        """프로세스 정지"""
        self.ui.statusValueLabel.setText("Idle")
        self.ui.statusValueLabel.setStyleSheet("color: gray; font-weight: bold;")

        # 버튼 상태 변경
        self.ui.startButton.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.pauseButton.setEnabled(False)

        # 시뮬레이션 정지
        self.simulation_timer.stop()

        print("Process stopped")

    @Slot()
    def pause_process(self):
        """프로세스 일시정지"""
        if self.simulation_timer.isActive():
            self.simulation_timer.stop()
            self.ui.statusValueLabel.setText("Paused")
            self.ui.statusValueLabel.setStyleSheet("color: orange; font-weight: bold;")
            self.ui.pauseButton.setText("Resume Process")
        else:
            self.simulation_timer.start(1000)
            self.ui.statusValueLabel.setText("Running")
            self.ui.statusValueLabel.setStyleSheet("color: green; font-weight: bold;")
            self.ui.pauseButton.setText("Pause Process")

        print("Process paused/resumed")

    @Slot()
    def open_settings(self):
        """설정 다이얼로그 열기"""
        print("Settings dialog opened")
        # TODO: 설정 다이얼로그 구현

    @Slot(str)
    def on_equipment_changed(self, equipment_id):
        """장비 변경 시"""
        print(f"Equipment changed to: {equipment_id}")
        # 장비별 초기화 로직
        self.reset_display()

    def reset_display(self):
        """디스플레이 리셋"""
        self.ui.temperatureValueLabel.setText("0.0 °C")
        self.ui.pressureValueLabel.setText("0.0 Torr")
        self.ui.gasFlowValueLabel.setText("0.0 sccm")

        self.ui.temperatureProgressBar.setValue(0)
        self.ui.pressureProgressBar.setValue(0)
        self.ui.gasFlowProgressBar.setValue(0)

        # 테이블 클리어
        self.ui.dataTableWidget.setRowCount(0)
        self.data_history.clear()

    def update_sensor_data(self):
        """센서 데이터 업데이트 (시뮬레이션)"""
        # 랜덤 데이터 생성
        temperature = random.uniform(20, 250)
        pressure = random.uniform(0.1, 5.0)
        gas_flow = random.uniform(0, 1000)

        # UI 업데이트
        self.update_display(temperature, pressure, gas_flow)

        # 데이터 저장
        self.save_data_point(temperature, pressure, gas_flow)

    def update_display(self, temperature, pressure, gas_flow):
        """디스플레이 업데이트"""
        # 라벨 업데이트
        self.ui.temperatureValueLabel.setText(f"{temperature:.1f} °C")
        self.ui.pressureValueLabel.setText(f"{pressure:.2f} Torr")
        self.ui.gasFlowValueLabel.setText(f"{gas_flow:.1f} sccm")

        # 프로그레스바 업데이트
        self.ui.temperatureProgressBar.setValue(int(temperature))
        self.ui.pressureProgressBar.setValue(int(pressure))
        self.ui.gasFlowProgressBar.setValue(int(gas_flow))

        # 온도에 따른 색상 변경
        if temperature > 200:
            color = "red"
        elif temperature > 150:
            color = "orange"
        else:
            color = "green"

        self.ui.temperatureValueLabel.setStyleSheet(f"color: {color}; font-weight: bold;")

    def save_data_point(self, temperature, pressure, gas_flow):
        """데이터 포인트 저장"""
        timestamp = datetime.now()
        equipment_id = self.ui.equipmentIdComboBox.currentText()

        data_point = {
            'timestamp': timestamp,
            'equipment_id': equipment_id,
            'temperature': temperature,
            'pressure': pressure,
            'gas_flow': gas_flow,
            'status': self.ui.statusValueLabel.text()
        }

        self.data_history.append(data_point)

        # 테이블에 추가
        self.add_table_row(data_point)

        # 최근 100개 데이터만 유지
        if len(self.data_history) > 100:
            self.data_history = self.data_history[-100:]

            # 테이블도 정리
            if self.ui.dataTableWidget.rowCount() > 100:
                self.ui.dataTableWidget.removeRow(0)

    def add_table_row(self, data_point):
        """테이블에 행 추가"""
        table = self.ui.dataTableWidget
        row_count = table.rowCount()
        table.insertRow(row_count)

        # 데이터 설정
        table.setItem(row_count, 0, QTableWidgetItem(
            data_point['timestamp'].strftime('%H:%M:%S')))
        table.setItem(row_count, 1, QTableWidgetItem(
            f"{data_point['temperature']:.1f}"))
        table.setItem(row_count, 2, QTableWidgetItem(
            f"{data_point['pressure']:.2f}"))
        table.setItem(row_count, 3, QTableWidgetItem(
            f"{data_point['gas_flow']:.1f}"))
        table.setItem(row_count, 4, QTableWidgetItem(
            data_point['status']))

        # 자동 스크롤
        table.scrollToBottom()

# 메인 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # UI 파일이 있는지 확인
    if not os.path.exists("equipment_monitor.ui"):
        print("UI file 'equipment_monitor.ui' not found!")
        print("Please create the UI file using Qt Designer first.")
        sys.exit(1)

    widget = EquipmentMonitorWidget()
    widget.show()

    sys.exit(app.exec())
```

</div>

---

## 4️⃣ Hands-on 실습 (45분)
### 📚 **반도체 CVD 장비 모니터링 시스템 구현**

#### **4.1 프로젝트 개요**

<div class="project-overview">

**🎯 목표**: CVD(Chemical Vapor Deposition) 장비의 실시간 모니터링 및 제어를 위한 완전한 HMI 시스템 구현

**📋 요구사항**:
- 실시간 온도, 압력, 가스 유량 모니터링
- 알람 시스템 및 이벤트 로깅
- 레시피 관리 및 프로세스 제어
- 데이터 저장 및 내보내기 기능
- 설정 관리 및 사용자 인증

</div>

#### **4.2 프로젝트 구조 설계**

```
cvd_monitor/
├── main.py                 # 메인 애플리케이션
├── ui/
│   ├── main_window.ui      # 메인 윈도우 UI
│   ├── recipe_dialog.ui    # 레시피 관리 UI
│   └── settings_dialog.ui  # 설정 UI
├── models/
│   ├── equipment_model.py  # 장비 데이터 모델
│   ├── recipe_model.py     # 레시피 모델
│   └── alarm_model.py      # 알람 모델
├── controllers/
│   ├── main_controller.py  # 메인 컨트롤러
│   ├── data_controller.py  # 데이터 컨트롤러
│   └── alarm_controller.py # 알람 컨트롤러
├── views/
│   ├── main_view.py        # 메인 뷰
│   ├── chart_view.py       # 차트 뷰
│   └── table_view.py       # 테이블 뷰
├── utils/
│   ├── file_manager.py     # 파일 관리
│   ├── settings_manager.py # 설정 관리
│   └── logger.py           # 로깅
└── resources/
    ├── styles.qss          # 스타일시트
    └── icons/              # 아이콘
```

#### **4.3 실습 과제**

##### **🎯 Phase 1: 기본 구조 구현 (15분)**
1. **프로젝트 구조 생성**: 디렉토리 구조에 따른 파일 생성
2. **메인 애플리케이션 작성**: main.py 구현 및 실행 확인
3. **기본 모델 구현**: EquipmentModel 클래스 작성

##### **🎯 Phase 2: UI 및 컨트롤러 구현 (15분)**
1. **Qt Designer UI 설계**: 메인 윈도우 레이아웃 구성
2. **메인 컨트롤러 구현**: 비즈니스 로직 작성
3. **뷰 클래스 구현**: UI와 컨트롤러 연결

##### **🎯 Phase 3: 고급 기능 구현 (15분)**
1. **실시간 차트 구현**: matplotlib 또는 QChart 활용
2. **알람 시스템 구현**: 임계값 체크 및 알림 표시
3. **데이터 저장/로드**: CSV/JSON 파일 처리 기능

#### **4.4 평가 기준**

<div class="evaluation-criteria">

**💯 평가 항목**:
- **코드 품질 (25%)**: PEP8 준수, 주석, 구조화
- **기능 구현 (35%)**: 요구사항 충족도, 안정성
- **UI/UX (20%)**: 사용성, 디자인, 반응성
- **문서화 (20%)**: README, 코드 주석, 사용법

**🏆 우수 작품 기준**:
- 실제 반도체 장비와 유사한 수준의 모니터링 기능
- 안정적인 실시간 데이터 처리
- 직관적이고 전문적인 UI 디자인
- 확장 가능한 아키텍처 구조

</div>

---

## 📝 **학습 정리 및 다음 주차 예고**

### **🎓 오늘 학습한 핵심 내용**
1. **Python PySide6 기초**: Qt 프레임워크 구조 및 위젯 활용
2. **시그널-슬롯 메커니즘**: 이벤트 기반 프로그래밍 패턴
3. **MVC 아키텍처**: 모델-뷰-컨트롤러 분리 설계
4. **Qt Designer 활용**: 비주얼 UI 설계 및 코드 연동
5. **파일 I/O 및 설정 관리**: QSettings와 JSON 데이터 처리

### **🔄 C# WPF vs Python PySide6 비교**
| 항목 | C# WPF | Python PySide6 |
|------|--------|----------------|
| **바인딩** | Data Binding | 시그널-슬롯 |
| **UI 설계** | XAML | Qt Designer + .ui |
| **아키텍처** | MVVM | MVC/MVP |
| **스타일링** | XAML Styles | QSS (CSS-like) |
| **배포** | .NET Runtime | Python + Qt 라이브러리 |

### **📅 다음 주차 예고: Python PySide6 실시간 데이터 처리**
- **QThread 활용 멀티스레딩**: UI 블록킹 방지 기법
- **QTimer 고급 활용**: 정밀한 타이밍 제어
- **시리얼 통신 및 네트워크**: 실제 장비와의 데이터 통신
- **데이터베이스 연동**: SQLite를 활용한 이력 관리
- **성능 최적화**: 대용량 데이터 처리 기법

---

## 실습 1: Python 환경 설정 및 PySide6 개발 도구 구축

### 실습 목표
- Python 가상환경 설정 및 PySide6 설치
- Visual Studio Code 또는 PyCharm 개발환경 구성
- Qt Designer 설치 및 기본 사용법 습득
- 디버깅 도구 및 프로파일링 도구 설정

### Python 개발환경 구축

#### 1. 가상환경 설정 및 PySide6 설치
```bash
# Python 가상환경 생성 (Python 3.9+ 권장)
python -m venv hmi_development
cd hmi_development

# Windows에서 가상환경 활성화
Scripts\activate

# Linux/macOS에서 가상환경 활성화
source bin/activate

# PySide6 및 개발 도구 설치
pip install PySide6[all]  # Qt Designer, qmltools 포함
pip install numpy pandas matplotlib  # 데이터 분석 라이브러리
pip install pyserial  # 시리얼 통신
pip install sqlite3  # 데이터베이스 (Python 3.x 기본 포함)
pip install pytest pytest-qt  # 테스트 프레임워크
pip install black flake8  # 코드 포맷팅 및 린터

# 개발용 추가 라이브러리
pip install memory_profiler  # 메모리 프로파일링
pip install line_profiler  # 라인별 성능 분석
pip install psutil  # 시스템 모니터링

# requirements.txt 생성
pip freeze > requirements.txt
```

#### 2. Visual Studio Code 설정
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./hmi_development/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "files.associations": {
        "*.ui": "xml",
        "*.qml": "qml",
        "*.qss": "css"
    },
    "emmet.includeLanguages": {
        "qml": "javascript"
    }
}

// .vscode/launch.json (디버깅 설정)
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {
                "QT_DEBUG_PLUGINS": "1",
                "QT_LOGGING_RULES": "*.debug=true"
            }
        },
        {
            "name": "Python: HMI Application",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "args": ["--debug"]
        }
    ]
}
```

#### 3. 프로젝트 구조 설정
```python
# project_structure.py - 자동으로 프로젝트 구조 생성
import os
from pathlib import Path

def create_project_structure():
    """표준화된 PySide6 HMI 프로젝트 구조 생성"""

    project_structure = {
        'src': {
            'models': ['__init__.py', 'sensor_data.py', 'equipment_model.py'],
            'views': ['__init__.py', 'main_window.py', 'dialogs.py'],
            'controllers': ['__init__.py', 'main_controller.py', 'data_controller.py'],
            'utils': ['__init__.py', 'logger.py', 'config.py', 'validators.py'],
            'resources': ['__init__.py']
        },
        'ui': ['main_window.ui', 'settings_dialog.ui'],
        'resources': ['icons', 'stylesheets', 'data'],
        'tests': ['__init__.py', 'test_models.py', 'test_views.py', 'test_controllers.py'],
        'docs': ['README.md', 'API.md', 'DEPLOYMENT.md'],
        'config': ['settings.json', 'logging.conf'],
        'scripts': ['build.py', 'deploy.py', 'test_runner.py']
    }

    def create_directory_structure(base_path: Path, structure: dict):
        for key, value in structure.items():
            current_path = base_path / key
            current_path.mkdir(exist_ok=True)

            if isinstance(value, dict):
                create_directory_structure(current_path, value)
            elif isinstance(value, list):
                for item in value:
                    if item.endswith('.py'):
                        (current_path / item).touch()
                    elif item.endswith(('.ui', '.json', '.conf', '.md')):
                        (current_path / item).touch()
                    else:
                        (current_path / item).mkdir(exist_ok=True)

    project_root = Path.cwd() / 'hmi_project'
    project_root.mkdir(exist_ok=True)
    create_directory_structure(project_root, project_structure)

    # 기본 파일들 생성
    create_basic_files(project_root)
    print(f"프로젝트 구조가 생성되었습니다: {project_root}")

def create_basic_files(project_root: Path):
    """기본적인 설정 파일들 생성"""

    # main.py
    main_py_content = '''#!/usr/bin/env python3
"""
반도체 HMI 시스템 메인 엔트리 포인트
"""
import sys
import argparse
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLoggingCategory, qmlRegisterType

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

from controllers.main_controller import MainController
from utils.logger import setup_logging
from utils.config import Config


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='반도체 HMI 시스템')
    parser.add_argument('--debug', action='store_true', help='디버그 모드 활성화')
    parser.add_argument('--config', type=str, help='설정 파일 경로')
    args = parser.parse_args()

    # 로깅 설정
    setup_logging(debug=args.debug)

    # Qt 애플리케이션 생성
    app = QApplication(sys.argv)
    app.setApplicationName("반도체 HMI 시스템")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("HMI Solutions")

    # 설정 로드
    config = Config(args.config)

    # 메인 컨트롤러 생성 및 실행
    controller = MainController(config)
    controller.show()

    # 이벤트 루프 시작
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
'''

    with open(project_root / 'main.py', 'w', encoding='utf-8') as f:
        f.write(main_py_content)

    # config/settings.json
    settings_json_content = '''{
    "application": {
        "name": "반도체 HMI 시스템",
        "version": "1.0.0",
        "window": {
            "width": 1920,
            "height": 1080,
            "fullscreen": false
        }
    },
    "data": {
        "update_interval_ms": 100,
        "buffer_size": 10000,
        "data_retention_days": 30
    },
    "communication": {
        "serial": {
            "port": "COM1",
            "baudrate": 9600,
            "timeout": 1.0
        },
        "tcp": {
            "host": "localhost",
            "port": 8080,
            "timeout": 5.0
        }
    },
    "logging": {
        "level": "INFO",
        "file": "logs/hmi.log",
        "max_size_mb": 10,
        "backup_count": 5
    }
}'''

    (project_root / 'config').mkdir(exist_ok=True)
    with open(project_root / 'config' / 'settings.json', 'w', encoding='utf-8') as f:
        f.write(settings_json_content)

if __name__ == '__main__':
    create_project_structure()
```

### Qt Designer 활용 및 .ui 파일 생성

#### 1. Qt Designer 실행 및 기본 설정
```python
# qt_designer_helper.py - Qt Designer 보조 도구
import subprocess
import sys
from pathlib import Path
from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QMessageBox

class QtDesignerHelper:
    """Qt Designer 보조 클래스"""

    def __init__(self):
        self.designer_path = self.find_designer_executable()

    def find_designer_executable(self) -> Path:
        """시스템에서 Qt Designer 실행 파일 찾기"""
        possible_paths = [
            Path(sys.executable).parent / 'Scripts' / 'pyside6-designer.exe',  # Windows
            Path(sys.executable).parent / 'pyside6-designer',  # Linux/macOS
            Path('/usr/bin/designer'),  # Linux 시스템 설치
            Path('/opt/Qt/Tools/QtCreator/bin/designer'),  # Qt Creator 설치
        ]

        for path in possible_paths:
            if path.exists():
                return path

        raise FileNotFoundError("Qt Designer를 찾을 수 없습니다. PySide6[all]이 설치되었는지 확인하세요.")

    def launch_designer(self, ui_file: Path = None):
        """Qt Designer 실행"""
        args = [str(self.designer_path)]
        if ui_file and ui_file.exists():
            args.append(str(ui_file))

        process = QProcess()
        success = process.startDetached(args[0], args[1:])

        if not success:
            QMessageBox.critical(None, "오류", f"Qt Designer 실행에 실패했습니다: {self.designer_path}")

        return success

    def compile_ui_to_py(self, ui_file: Path, output_file: Path = None):
        """UI 파일을 Python 코드로 변환"""
        if not ui_file.exists():
            raise FileNotFoundError(f"UI 파일을 찾을 수 없습니다: {ui_file}")

        if output_file is None:
            output_file = ui_file.with_suffix('.py')

        # pyside6-uic를 사용하여 변환
        uic_path = Path(sys.executable).parent / 'Scripts' / 'pyside6-uic.exe'
        if not uic_path.exists():
            uic_path = Path(sys.executable).parent / 'pyside6-uic'

        result = subprocess.run(
            [str(uic_path), str(ui_file), '-o', str(output_file)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"UI 컴파일 실패: {result.stderr}")

        print(f"UI 파일이 컴파일되었습니다: {output_file}")
        return output_file

# 사용 예제
if __name__ == '__main__':
    helper = QtDesignerHelper()

    # Qt Designer 실행
    helper.launch_designer()

    # UI 파일 컴파일 (예제)
    # helper.compile_ui_to_py(Path('ui/main_window.ui'))
```

#### 2. 기본 메인 윈도우 UI 설계
```xml
<!-- ui/main_window.ui - Qt Designer에서 생성할 기본 UI -->
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1200</width>
    <height>800</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>반도체 HMI 시스템</string>
  </property>
  <property name="styleSheet">
   <string notr="true">
/* 기본 스타일 시트 */
QMainWindow {
    background-color: #f5f5f5;
}

QToolBar {
    background-color: #2c3e50;
    border: none;
    spacing: 3px;
    color: white;
}

QStatusBar {
    background-color: #34495e;
    color: white;
}

QMenuBar {
    background-color: #2c3e50;
    color: white;
}

QMenuBar::item:selected {
    background-color: #3498db;
}
   </string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <layout class="QGridLayout" name="gridLayout">
    <item row="0" column="0">
     <widget class="QTabWidget" name="tabWidget">
      <property name="currentIndex">
       <number>0</number>
      </property>
      <widget class="QWidget" name="tab_overview">
       <attribute name="title">
        <string>시스템 개요</string>
       </attribute>
       <layout class="QVBoxLayout" name="verticalLayout">
        <item>
         <widget class="QGroupBox" name="groupBox_status">
          <property name="title">
           <string>장비 상태</string>
          </property>
          <layout class="QGridLayout" name="gridLayout_2">
           <item row="0" column="0">
            <widget class="QLabel" name="label_temp">
             <property name="text">
              <string>온도:</string>
             </property>
            </widget>
           </item>
           <item row="0" column="1">
            <widget class="QLCDNumber" name="lcd_temperature">
             <property name="digitCount">
              <number>5</number>
             </property>
             <property name="segmentStyle">
              <enum>QLCDNumber::Flat</enum>
             </property>
            </widget>
           </item>
           <item row="1" column="0">
            <widget class="QLabel" name="label_pressure">
             <property name="text">
              <string>압력:</string>
             </property>
            </widget>
           </item>
           <item row="1" column="1">
            <widget class="QLCDNumber" name="lcd_pressure">
             <property name="digitCount">
              <number>5</number>
             </property>
             <property name="segmentStyle">
              <enum>QLCDNumber::Flat</enum>
             </property>
            </widget>
           </item>
          </layout>
         </widget>
        </item>
        <item>
         <widget class="QGroupBox" name="groupBox_control">
          <property name="title">
           <string>제어</string>
          </property>
          <layout class="QHBoxLayout" name="horizontalLayout">
           <item>
            <widget class="QPushButton" name="btn_start">
             <property name="text">
              <string>시작</string>
             </property>
             <property name="styleSheet">
              <string notr="true">
QPushButton {
    background-color: #27ae60;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 5px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2ecc71;
}

QPushButton:pressed {
    background-color: #219a52;
}
              </string>
             </property>
            </widget>
           </item>
           <item>
            <widget class="QPushButton" name="btn_stop">
             <property name="text">
              <string>정지</string>
             </property>
             <property name="styleSheet">
              <string notr="true">
QPushButton {
    background-color: #e74c3c;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 5px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #c0392b;
}

QPushButton:pressed {
    background-color: #a93226;
}
              </string>
             </property>
            </widget>
           </item>
           <item>
            <spacer name="horizontalSpacer">
             <property name="orientation">
              <enum>Qt::Horizontal</enum>
             </property>
             <property name="sizeHint" stdset="0">
              <size>
               <width>40</width>
               <height>20</height>
              </size>
             </property>
            </spacer>
           </item>
          </layout>
         </widget>
        </item>
       </layout>
      </widget>
      <widget class="QWidget" name="tab_data">
       <attribute name="title">
        <string>데이터</string>
       </attribute>
       <layout class="QVBoxLayout" name="verticalLayout_2">
        <item>
         <widget class="QTableWidget" name="table_data">
          <property name="alternatingRowColors">
           <bool>true</bool>
          </property>
          <property name="sortingEnabled">
           <bool>true</bool>
          </property>
          <column>
           <property name="text">
            <string>시간</string>
           </property>
          </column>
          <column>
           <property name="text">
            <string>온도</string>
           </property>
          </column>
          <column>
           <property name="text">
            <string>압력</string>
           </property>
          </column>
          <column>
           <property name="text">
            <string>상태</string>
           </property>
          </column>
         </widget>
        </item>
       </layout>
      </widget>
     </widget>
    </item>
   </layout>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>1200</width>
     <height>22</height>
    </rect>
   </property>
   <widget class="QMenu" name="menu_file">
    <property name="title">
     <string>파일</string>
    </property>
    <addaction name="action_new"/>
    <addaction name="action_open"/>
    <addaction name="action_save"/>
    <addaction name="separator"/>
    <addaction name="action_exit"/>
   </widget>
   <widget class="QMenu" name="menu_tools">
    <property name="title">
     <string>도구</string>
    </property>
    <addaction name="action_settings"/>
    <addaction name="action_calibration"/>
   </widget>
   <addaction name="menu_file"/>
   <addaction name="menu_tools"/>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
  <widget class="QToolBar" name="toolBar">
   <property name="windowTitle">
    <string>toolBar</string>
   </property>
   <attribute name="toolBarArea">
    <enum>TopToolBarArea</enum>
   </attribute>
   <attribute name="toolBarBreak">
    <bool>false</bool>
   </attribute>
   <addaction name="action_start"/>
   <addaction name="action_stop"/>
   <addaction name="separator"/>
   <addaction name="action_settings"/>
  </widget>
  <action name="action_new">
   <property name="text">
    <string>새로 만들기</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+N</string>
   </property>
  </action>
  <action name="action_open">
   <property name="text">
    <string>열기</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+O</string>
   </property>
  </action>
  <action name="action_save">
   <property name="text">
    <string>저장</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+S</string>
   </property>
  </action>
  <action name="action_exit">
   <property name="text">
    <string>종료</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+Q</string>
   </property>
  </action>
  <action name="action_settings">
   <property name="text">
    <string>설정</string>
   </property>
  </action>
  <action name="action_calibration">
   <property name="text">
    <string>캘리브레이션</string>
   </property>
  </action>
  <action name="action_start">
   <property name="text">
    <string>시작</string>
   </property>
   <property name="toolTip">
    <string>시스템 시작</string>
   </property>
  </action>
  <action name="action_stop">
   <property name="text">
    <string>정지</string>
   </property>
   <property name="toolTip">
    <string>시스템 정지</string>
   </property>
  </action>
 </widget>
 <resources/>
 <connections/>
</ui>
```

---

## 실습 2: MVC 아키텍처 및 시그널-슬롯 시스템

### 실습 목표
- MVC (Model-View-Controller) 패턴 구현
- 시그널-슬롯 메커니즘을 활용한 이벤트 처리
- 데이터 모델과 뷰의 분리
- 커스텀 시그널 생성 및 활용

### Model 계층 구현

#### 1. 센서 데이터 모델
```python
# src/models/sensor_data.py
from PySide6.QtCore import QObject, Signal, QTimer, Property
from PySide6.QtWidgets import QApplication
from datetime import datetime
import random
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

class SensorType(Enum):
    """센서 타입 열거형"""
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    FLOW_RATE = "flow_rate"
    VOLTAGE = "voltage"
    CURRENT = "current"

class SensorStatus(Enum):
    """센서 상태 열거형"""
    NORMAL = "normal"
    WARNING = "warning"
    ERROR = "error"
    OFFLINE = "offline"

@dataclass
class SensorReading:
    """센서 측정값 데이터 클래스"""
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    status: SensorStatus = SensorStatus.NORMAL
    min_value: float = None
    max_value: float = None

    def is_within_range(self) -> bool:
        """측정값이 정상 범위 내에 있는지 확인"""
        if self.min_value is not None and self.value < self.min_value:
            return False
        if self.max_value is not None and self.value > self.max_value:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type.value,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status.value,
            'min_value': self.min_value,
            'max_value': self.max_value
        }

class SensorDataModel(QObject):
    """센서 데이터 모델 클래스"""

    # 시그널 정의
    dataChanged = Signal(SensorReading)  # 데이터 변경 시그널
    statusChanged = Signal(str, SensorStatus)  # 상태 변경 시그널
    alertTriggered = Signal(str, str)  # 경고 시그널 (센서 ID, 메시지)
    batchDataReady = Signal(list)  # 배치 데이터 준비 시그널

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sensors: Dict[str, SensorReading] = {}
        self._data_history: List[SensorReading] = []
        self._max_history_size = 10000

        # 시뮬레이션을 위한 타이머
        self._simulation_timer = QTimer()
        self._simulation_timer.timeout.connect(self._generate_simulation_data)
        self._is_simulation_active = False

        # 센서 설정 초기화
        self._init_sensors()

    def _init_sensors(self):
        """기본 센서들 초기화"""
        sensor_configs = [
            {
                'id': 'TEMP_001',
                'type': SensorType.TEMPERATURE,
                'unit': '°C',
                'min_value': 20.0,
                'max_value': 80.0,
                'base_value': 25.0
            },
            {
                'id': 'PRES_001',
                'type': SensorType.PRESSURE,
                'unit': 'Torr',
                'min_value': 0.1,
                'max_value': 100.0,
                'base_value': 10.0
            },
            {
                'id': 'FLOW_001',
                'type': SensorType.FLOW_RATE,
                'unit': 'sccm',
                'min_value': 0.0,
                'max_value': 500.0,
                'base_value': 100.0
            }
        ]

        for config in sensor_configs:
            reading = SensorReading(
                sensor_id=config['id'],
                sensor_type=config['type'],
                value=config['base_value'],
                unit=config['unit'],
                min_value=config['min_value'],
                max_value=config['max_value']
            )
            self._sensors[config['id']] = reading

    def add_sensor_reading(self, reading: SensorReading):
        """센서 측정값 추가"""
        # 상태 체크
        if not reading.is_within_range():
            if reading.value < reading.min_value:
                reading.status = SensorStatus.ERROR
                self.alertTriggered.emit(
                    reading.sensor_id,
                    f"측정값이 최소값보다 낮습니다: {reading.value} < {reading.min_value}"
                )
            elif reading.value > reading.max_value:
                reading.status = SensorStatus.ERROR
                self.alertTriggered.emit(
                    reading.sensor_id,
                    f"측정값이 최대값보다 높습니다: {reading.value} > {reading.max_value}"
                )

        # 데이터 저장
        self._sensors[reading.sensor_id] = reading
        self._data_history.append(reading)

        # 히스토리 크기 관리
        if len(self._data_history) > self._max_history_size:
            self._data_history.pop(0)

        # 시그널 방출
        self.dataChanged.emit(reading)

        # 상태가 변경된 경우
        if reading.sensor_id in self._sensors:
            old_status = self._sensors[reading.sensor_id].status
            if old_status != reading.status:
                self.statusChanged.emit(reading.sensor_id, reading.status)

    def get_sensor_reading(self, sensor_id: str) -> SensorReading:
        """특정 센서의 최신 측정값 반환"""
        return self._sensors.get(sensor_id)

    def get_all_sensors(self) -> Dict[str, SensorReading]:
        """모든 센서의 최신 측정값 반환"""
        return self._sensors.copy()

    def get_sensor_history(self, sensor_id: str, count: int = 100) -> List[SensorReading]:
        """특정 센서의 히스토리 반환"""
        history = [reading for reading in self._data_history
                  if reading.sensor_id == sensor_id]
        return history[-count:] if count > 0 else history

    def get_statistics(self, sensor_id: str) -> Dict[str, float]:
        """센서 통계 정보 반환"""
        history = self.get_sensor_history(sensor_id, 0)  # 전체 히스토리
        if not history:
            return {}

        values = [reading.value for reading in history]
        return {
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'count': len(values)
        }

    def start_simulation(self, interval_ms: int = 1000):
        """시뮬레이션 시작"""
        self._simulation_timer.setInterval(interval_ms)
        self._simulation_timer.start()
        self._is_simulation_active = True

    def stop_simulation(self):
        """시뮬레이션 정지"""
        self._simulation_timer.stop()
        self._is_simulation_active = False

    def _generate_simulation_data(self):
        """시뮬레이션 데이터 생성"""
        for sensor_id, sensor in self._sensors.items():
            # 기본값 중심으로 노이즈가 있는 데이터 생성
            if sensor.sensor_type == SensorType.TEMPERATURE:
                base_value = 25.0
                noise_amplitude = 2.0
            elif sensor.sensor_type == SensorType.PRESSURE:
                base_value = 10.0
                noise_amplitude = 1.0
            else:  # FLOW_RATE
                base_value = 100.0
                noise_amplitude = 10.0

            # 랜덤 노이즈 추가 (가끔 이상값 생성)
            if random.random() < 0.05:  # 5% 확률로 이상값
                value = base_value + random.uniform(-noise_amplitude * 5, noise_amplitude * 5)
            else:
                value = base_value + random.uniform(-noise_amplitude, noise_amplitude)

            # 새로운 측정값 생성
            new_reading = SensorReading(
                sensor_id=sensor_id,
                sensor_type=sensor.sensor_type,
                value=round(value, 2),
                unit=sensor.unit,
                min_value=sensor.min_value,
                max_value=sensor.max_value
            )

            self.add_sensor_reading(new_reading)

    @Property(bool, notify=dataChanged)
    def is_simulation_active(self) -> bool:
        """시뮬레이션 활성 상태 프로퍼티"""
        return self._is_simulation_active

    def clear_history(self):
        """히스토리 클리어"""
        self._data_history.clear()

    def export_data(self, file_path: str, format: str = 'json'):
        """데이터 내보내기"""
        import json
        import csv

        if format.lower() == 'json':
            data = [reading.to_dict() for reading in self._data_history]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        elif format.lower() == 'csv':
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                if self._data_history:
                    writer = csv.DictWriter(f, fieldnames=self._data_history[0].to_dict().keys())
                    writer.writeheader()
                    for reading in self._data_history:
                        writer.writerow(reading.to_dict())
```

#### 2. 장비 모델
```python
# src/models/equipment_model.py
from PySide6.QtCore import QObject, Signal, QTimer, Property
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

class EquipmentState(Enum):
    """장비 상태 열거형"""
    IDLE = "idle"
    RUNNING = "running"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    EMERGENCY_STOP = "emergency_stop"

class ProcessState(Enum):
    """공정 상태 열거형"""
    READY = "ready"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ABORTED = "aborted"
    PAUSED = "paused"

@dataclass
class Recipe:
    """레시피 데이터 클래스"""
    name: str
    description: str
    steps: list
    total_time: float  # seconds
    parameters: Dict[str, Any]
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class EquipmentModel(QObject):
    """장비 모델 클래스"""

    # 시그널 정의
    stateChanged = Signal(EquipmentState, EquipmentState)  # 이전 상태, 새 상태
    processStateChanged = Signal(ProcessState)
    recipeStarted = Signal(str)  # 레시피 이름
    recipeCompleted = Signal(str, bool)  # 레시피 이름, 성공 여부
    emergencyStopTriggered = Signal(str)  # 이유
    parameterChanged = Signal(str, object)  # 파라미터 이름, 값

    def __init__(self, parent=None):
        super().__init__(parent)

        # 상태 변수들
        self._equipment_state = EquipmentState.IDLE
        self._process_state = ProcessState.READY
        self._current_recipe: Optional[Recipe] = None
        self._current_step = 0
        self._process_progress = 0.0  # 0.0 ~ 1.0

        # 장비 파라미터들
        self._parameters = {
            'temperature_setpoint': 25.0,
            'pressure_setpoint': 10.0,
            'flow_rate_setpoint': 100.0,
            'process_time': 0.0,
            'recipe_name': '',
            'operator_id': '',
            'lot_number': ''
        }

        # 프로세스 타이머
        self._process_timer = QTimer()
        self._process_timer.timeout.connect(self._update_process)

        # 기본 레시피들
        self._available_recipes = self._create_default_recipes()

    def _create_default_recipes(self) -> Dict[str, Recipe]:
        """기본 레시피들 생성"""
        recipes = {}

        # 기본 CVD 레시피
        cvd_recipe = Recipe(
            name="Standard_CVD",
            description="표준 CVD 공정",
            steps=[
                {"name": "Preheat", "temperature": 200, "time": 60},
                {"name": "Deposition", "temperature": 400, "time": 300},
                {"name": "Cool down", "temperature": 25, "time": 120}
            ],
            total_time=480.0,  # 8 minutes
            parameters={
                "chamber_pressure": 0.5,
                "gas_flow": 50.0,
                "rf_power": 100.0
            }
        )
        recipes[cvd_recipe.name] = cvd_recipe

        # 빠른 테스트 레시피
        quick_test = Recipe(
            name="Quick_Test",
            description="빠른 테스트 공정",
            steps=[
                {"name": "Test", "temperature": 50, "time": 30}
            ],
            total_time=30.0,
            parameters={
                "test_mode": True
            }
        )
        recipes[quick_test.name] = quick_test

        return recipes

    @Property(EquipmentState, notify=stateChanged)
    def equipment_state(self) -> EquipmentState:
        """장비 상태 프로퍼티"""
        return self._equipment_state

    @equipment_state.setter
    def equipment_state(self, new_state: EquipmentState):
        """장비 상태 설정"""
        if self._equipment_state != new_state:
            old_state = self._equipment_state
            self._equipment_state = new_state
            self.stateChanged.emit(old_state, new_state)

    @Property(ProcessState, notify=processStateChanged)
    def process_state(self) -> ProcessState:
        """공정 상태 프로퍼티"""
        return self._process_state

    @process_state.setter
    def process_state(self, new_state: ProcessState):
        """공정 상태 설정"""
        if self._process_state != new_state:
            self._process_state = new_state
            self.processStateChanged.emit(new_state)

    @Property(float, notify=parameterChanged)
    def process_progress(self) -> float:
        """공정 진행률 프로퍼티"""
        return self._process_progress

    def get_parameter(self, name: str) -> Any:
        """파라미터 값 반환"""
        return self._parameters.get(name)

    def set_parameter(self, name: str, value: Any):
        """파라미터 값 설정"""
        if name in self._parameters and self._parameters[name] != value:
            self._parameters[name] = value
            self.parameterChanged.emit(name, value)

    def get_all_parameters(self) -> Dict[str, Any]:
        """모든 파라미터 반환"""
        return self._parameters.copy()

    def get_available_recipes(self) -> Dict[str, Recipe]:
        """사용 가능한 레시피들 반환"""
        return self._available_recipes.copy()

    def start_recipe(self, recipe_name: str) -> bool:
        """레시피 시작"""
        if self._equipment_state != EquipmentState.IDLE:
            return False

        if recipe_name not in self._available_recipes:
            return False

        self._current_recipe = self._available_recipes[recipe_name]
        self._current_step = 0
        self._process_progress = 0.0

        # 상태 변경
        self.equipment_state = EquipmentState.RUNNING
        self.process_state = ProcessState.PROCESSING

        # 파라미터 업데이트
        self.set_parameter('recipe_name', recipe_name)
        self.set_parameter('process_time', 0.0)

        # 프로세스 타이머 시작 (1초마다 업데이트)
        self._process_timer.start(1000)

        # 시그널 방출
        self.recipeStarted.emit(recipe_name)

        return True

    def pause_recipe(self) -> bool:
        """레시피 일시정지"""
        if self._process_state == ProcessState.PROCESSING:
            self.process_state = ProcessState.PAUSED
            self._process_timer.stop()
            return True
        return False

    def resume_recipe(self) -> bool:
        """레시피 재개"""
        if self._process_state == ProcessState.PAUSED:
            self.process_state = ProcessState.PROCESSING
            self._process_timer.start(1000)
            return True
        return False

    def stop_recipe(self, abort: bool = False) -> bool:
        """레시피 정지"""
        if self._process_state in [ProcessState.PROCESSING, ProcessState.PAUSED]:
            self._process_timer.stop()

            if abort:
                self.process_state = ProcessState.ABORTED
            else:
                self.process_state = ProcessState.COMPLETED

            self.equipment_state = EquipmentState.IDLE

            # 시그널 방출
            recipe_name = self._current_recipe.name if self._current_recipe else "Unknown"
            self.recipeCompleted.emit(recipe_name, not abort)

            # 리셋
            self._current_recipe = None
            self._current_step = 0
            self._process_progress = 0.0
            self.set_parameter('process_time', 0.0)

            return True
        return False

    def emergency_stop(self, reason: str = "사용자 요청"):
        """비상 정지"""
        self._process_timer.stop()
        self.equipment_state = EquipmentState.EMERGENCY_STOP
        self.process_state = ProcessState.ABORTED

        # 모든 설정값을 안전 상태로
        self.set_parameter('temperature_setpoint', 25.0)
        self.set_parameter('pressure_setpoint', 0.1)
        self.set_parameter('flow_rate_setpoint', 0.0)

        self.emergencyStopTriggered.emit(reason)

    def reset_from_emergency(self) -> bool:
        """비상정지에서 복구"""
        if self._equipment_state == EquipmentState.EMERGENCY_STOP:
            self.equipment_state = EquipmentState.IDLE
            self.process_state = ProcessState.READY
            return True
        return False

    def _update_process(self):
        """프로세스 업데이트 (타이머 콜백)"""
        if not self._current_recipe:
            return

        # 경과 시간 증가
        current_time = self.get_parameter('process_time') + 1.0
        self.set_parameter('process_time', current_time)

        # 진행률 계산
        total_time = self._current_recipe.total_time
        self._process_progress = min(current_time / total_time, 1.0)

        # 완료 체크
        if current_time >= total_time:
            self.stop_recipe(abort=False)

        # 파라미터 변경 시그널
        self.parameterChanged.emit('process_progress', self._process_progress)
```

### View 계층 구현

#### 3. 메인 윈도우 클래스
```python
# src/views/main_window.py
from PySide6.QtWidgets import (QMainWindow, QApplication, QMessageBox,
                              QTableWidgetItem, QHeaderView, QSystemTrayIcon,
                              QMenu, QStatusBar, QProgressBar)
from PySide6.QtCore import QTimer, Slot, Qt, QSize
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor

from ..models.sensor_data import SensorDataModel, SensorReading, SensorStatus
from ..models.equipment_model import EquipmentModel, EquipmentState, ProcessState
from ..utils.logger import get_logger
from ..utils.config import Config

# UI 파일에서 생성된 클래스 (pyside6-uic로 변환)
try:
    from ..ui.main_window_ui import Ui_MainWindow
except ImportError:
    # UI 파일이 없는 경우 기본 클래스 생성
    class Ui_MainWindow:
        def setupUi(self, MainWindow):
            pass

class MainWindow(QMainWindow, Ui_MainWindow):
    """메인 윈도우 클래스"""

    def __init__(self, sensor_model: SensorDataModel, equipment_model: EquipmentModel,
                 config: Config, parent=None):
        super().__init__(parent)

        # 모델들
        self.sensor_model = sensor_model
        self.equipment_model = equipment_model
        self.config = config
        self.logger = get_logger(__name__)

        # UI 설정
        self.setupUi(self)
        self.setWindowTitle(f"{self.config.get('application.name')} v{self.config.get('application.version')}")
        self.resize(
            self.config.get('application.window.width', 1200),
            self.config.get('application.window.height', 800)
        )

        # UI 구성 요소들 초기화
        self._setup_ui_components()
        self._setup_system_tray()
        self._connect_signals()

        # 상태 업데이트 타이머
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(100)  # 100ms마다 업데이트

        self.logger.info("메인 윈도우가 초기화되었습니다")

    def _setup_ui_components(self):
        """UI 구성 요소들 설정"""
        # 상태 바 설정
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 진행률 표시
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # 상태 라벨들
        self.status_equipment = self.status_bar.addWidget(
            self.statusBar().showMessage("장비: 대기중")
        )

        # 테이블 위젯 설정
        if hasattr(self, 'table_data'):
            self.table_data.setColumnCount(4)
            self.table_data.setHorizontalHeaderLabels(["시간", "센서 ID", "값", "상태"])
            self.table_data.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.table_data.setAlternatingRowColors(True)
            self.table_data.setSortingEnabled(True)

        # LCD 디스플레이 초기값 설정
        if hasattr(self, 'lcd_temperature'):
            self.lcd_temperature.display(25.0)
        if hasattr(self, 'lcd_pressure'):
            self.lcd_pressure.display(10.0)

    def _setup_system_tray(self):
        """시스템 트레이 설정"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)

            # 트레이 아이콘 생성
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(0, 120, 255))  # 파란색
            self.tray_icon.setIcon(QIcon(pixmap))

            # 트레이 메뉴
            tray_menu = QMenu()
            show_action = tray_menu.addAction("창 보이기")
            show_action.triggered.connect(self.show)

            quit_action = tray_menu.addAction("종료")
            quit_action.triggered.connect(QApplication.quit)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self._tray_icon_activated)
            self.tray_icon.show()

    def _connect_signals(self):
        """시그널-슬롯 연결"""
        # 센서 모델 시그널들
        self.sensor_model.dataChanged.connect(self._on_sensor_data_changed)
        self.sensor_model.alertTriggered.connect(self._on_sensor_alert)

        # 장비 모델 시그널들
        self.equipment_model.stateChanged.connect(self._on_equipment_state_changed)
        self.equipment_model.processStateChanged.connect(self._on_process_state_changed)
        self.equipment_model.recipeStarted.connect(self._on_recipe_started)
        self.equipment_model.recipeCompleted.connect(self._on_recipe_completed)
        self.equipment_model.emergencyStopTriggered.connect(self._on_emergency_stop)
        self.equipment_model.parameterChanged.connect(self._on_parameter_changed)

        # UI 버튼들
        if hasattr(self, 'btn_start'):
            self.btn_start.clicked.connect(self._on_start_clicked)
        if hasattr(self, 'btn_stop'):
            self.btn_stop.clicked.connect(self._on_stop_clicked)

        # 액션들
        if hasattr(self, 'action_exit'):
            self.action_exit.triggered.connect(self.close)
        if hasattr(self, 'action_settings'):
            self.action_settings.triggered.connect(self._show_settings_dialog)

    @Slot(SensorReading)
    def _on_sensor_data_changed(self, reading: SensorReading):
        """센서 데이터 변경 처리"""
        # LCD 디스플레이 업데이트
        if reading.sensor_type.value == "temperature" and hasattr(self, 'lcd_temperature'):
            self.lcd_temperature.display(reading.value)
        elif reading.sensor_type.value == "pressure" and hasattr(self, 'lcd_pressure'):
            self.lcd_pressure.display(reading.value)

        # 테이블에 데이터 추가
        self._add_data_to_table(reading)

    @Slot(str, str)
    def _on_sensor_alert(self, sensor_id: str, message: str):
        """센서 경고 처리"""
        self.logger.warning(f"센서 경고 [{sensor_id}]: {message}")

        # 시스템 트레이 알림
        if hasattr(self, 'tray_icon'):
            self.tray_icon.showMessage("센서 경고", f"{sensor_id}: {message}",
                                     QSystemTrayIcon.Warning, 5000)

        # 상태바에 표시
        self.status_bar.showMessage(f"경고: {sensor_id} - {message}", 10000)

    @Slot(object, object)
    def _on_equipment_state_changed(self, old_state: EquipmentState, new_state: EquipmentState):
        """장비 상태 변경 처리"""
        self.logger.info(f"장비 상태 변경: {old_state.value} -> {new_state.value}")

        # 상태바 업데이트
        status_text = {
            EquipmentState.IDLE: "대기중",
            EquipmentState.RUNNING: "실행중",
            EquipmentState.MAINTENANCE: "정비중",
            EquipmentState.ERROR: "오류",
            EquipmentState.EMERGENCY_STOP: "비상정지"
        }

        self.status_bar.showMessage(f"장비: {status_text.get(new_state, new_state.value)}")

        # UI 상태 업데이트
        is_idle = new_state == EquipmentState.IDLE
        if hasattr(self, 'btn_start'):
            self.btn_start.setEnabled(is_idle)
        if hasattr(self, 'btn_stop'):
            self.btn_stop.setEnabled(not is_idle)

    @Slot(object)
    def _on_process_state_changed(self, new_state: ProcessState):
        """공정 상태 변경 처리"""
        self.logger.info(f"공정 상태 변경: {new_state.value}")

        # 진행률 바 표시/숨김
        if new_state == ProcessState.PROCESSING:
            self.progress_bar.setVisible(True)
        else:
            self.progress_bar.setVisible(False)

    @Slot(str)
    def _on_recipe_started(self, recipe_name: str):
        """레시피 시작 처리"""
        self.logger.info(f"레시피 시작: {recipe_name}")
        QMessageBox.information(self, "레시피 시작", f"'{recipe_name}' 레시피가 시작되었습니다.")

    @Slot(str, bool)
    def _on_recipe_completed(self, recipe_name: str, success: bool):
        """레시피 완료 처리"""
        self.logger.info(f"레시피 완료: {recipe_name}, 성공: {success}")

        if success:
            QMessageBox.information(self, "레시피 완료", f"'{recipe_name}' 레시피가 성공적으로 완료되었습니다.")
        else:
            QMessageBox.warning(self, "레시피 중단", f"'{recipe_name}' 레시피가 중단되었습니다.")

    @Slot(str)
    def _on_emergency_stop(self, reason: str):
        """비상정지 처리"""
        self.logger.critical(f"비상정지 발생: {reason}")
        QMessageBox.critical(self, "비상정지", f"비상정지가 발생했습니다.\n이유: {reason}")

    @Slot(str, object)
    def _on_parameter_changed(self, name: str, value):
        """파라미터 변경 처리"""
        if name == 'process_progress':
            self.progress_bar.setValue(int(value * 100))

    def _add_data_to_table(self, reading: SensorReading):
        """테이블에 데이터 추가"""
        if not hasattr(self, 'table_data'):
            return

        row = self.table_data.rowCount()
        self.table_data.insertRow(row)

        # 데이터 추가
        self.table_data.setItem(row, 0, QTableWidgetItem(
            reading.timestamp.strftime("%H:%M:%S")
        ))
        self.table_data.setItem(row, 1, QTableWidgetItem(reading.sensor_id))
        self.table_data.setItem(row, 2, QTableWidgetItem(
            f"{reading.value:.2f} {reading.unit}"
        ))

        # 상태에 따른 색상 설정
        status_item = QTableWidgetItem(reading.status.value)
        if reading.status == SensorStatus.ERROR:
            status_item.setBackground(QColor(255, 200, 200))  # 연한 빨강
        elif reading.status == SensorStatus.WARNING:
            status_item.setBackground(QColor(255, 255, 200))  # 연한 노랑

        self.table_data.setItem(row, 3, status_item)

        # 테이블 크기 제한 (최대 1000행)
        if self.table_data.rowCount() > 1000:
            self.table_data.removeRow(0)

        # 최신 데이터로 스크롤
        self.table_data.scrollToBottom()

    def _update_display(self):
        """디스플레이 업데이트"""
        # 현재 시간 상태바에 표시
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # self.status_bar에 시간 표시는 다른 메시지와 충돌할 수 있으므로 생략

    @Slot()
    def _on_start_clicked(self):
        """시작 버튼 클릭 처리"""
        # 기본 레시피로 시작
        success = self.equipment_model.start_recipe("Quick_Test")
        if not success:
            QMessageBox.warning(self, "시작 실패", "레시피를 시작할 수 없습니다.")

    @Slot()
    def _on_stop_clicked(self):
        """정지 버튼 클릭 처리"""
        self.equipment_model.stop_recipe()

    def _show_settings_dialog(self):
        """설정 다이얼로그 표시"""
        QMessageBox.information(self, "설정", "설정 다이얼로그가 구현되지 않았습니다.")

    def _tray_icon_activated(self, reason):
        """트레이 아이콘 클릭 처리"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()

    def closeEvent(self, event):
        """창 닫기 이벤트"""
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            # 트레이로 최소화
            self.hide()
            self.tray_icon.showMessage(
                "시스템 트레이",
                "애플리케이션이 트레이로 최소화되었습니다.",
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            # 완전 종료
            event.accept()
```

---

## ❓ 질의응답

<div style="margin: 2rem 0;">

<div style="background: #f8f9fa; padding: 2rem; border-radius: 8px; text-align: center; border: 2px dashed #6c757d;">
    <h3 style="color: #495057; margin: 0 0 1rem 0;">💬 질문해 주세요!</h3>
    <p style="margin: 0; color: #6c757d; font-style: italic;">
        Python PySide6의 MVC 아키텍처, 시그널-슬롯 시스템, Qt Designer 활용에 대해<br>
        궁금한 점이 있으시면 언제든지 질문해 주세요.
    </p>
</div>

</div>

---