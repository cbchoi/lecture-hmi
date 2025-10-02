# 🛠️ 기초 실습: Qt Designer UI 설계 및 기본 위젯 활용

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

## 4️⃣ Hands-on 실습
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

##### **🎯 Phase 1: 기본 구조 구현**
1. **프로젝트 구조 생성**: 디렉토리 구조에 따른 파일 생성
2. **메인 애플리케이션 작성**: main.py 구현 및 실행 확인
3. **기본 모델 구현**: EquipmentModel 클래스 작성

##### **🎯 Phase 2: UI 및 컨트롤러 구현**
1. **Qt Designer UI 설계**: 메인 윈도우 레이아웃 구성
2. **메인 컨트롤러 구현**: 비즈니스 로직 작성
3. **뷰 클래스 구현**: UI와 컨트롤러 연결

##### **🎯 Phase 3: 고급 기능 구현**
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
