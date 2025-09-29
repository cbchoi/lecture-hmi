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