# ❌ 잘못된 방법: Python threading 모듈 사용
import threading
from PySide6.QtWidgets import QLabel

def worker_function():
    # GUI 객체에 직접 접근 (위험!)
    label.setText("Updated from thread")  # 크래시 가능성

# ✅ 올바른 방법: QThread 사용
from PySide6.QtCore import QThread, Signal

class DataWorker(QThread):
    data_ready = Signal(str)

    def run(self):
        # 백그라운드 작업 수행
        result = self.process_data()
        # 시그널을 통해 안전하게 UI 업데이트
        self.data_ready.emit(result)
```

##### **1.1.2 Worker 패턴 구현**

<div class="code-block">

**Worker 패턴**은 QThread를 상속받지 않고 QObject를 상속받는 클래스를 별도 스레드로 이동시키는 방법입니다.

```python
from PySide6.QtCore import QObject, QThread, Signal, Slot
import time

class DataWorker(QObject):
    """데이터 처리 워커 클래스"""

    # 시그널 정의
    progress_updated = Signal(int)
    data_processed = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.is_running = False

    @Slot()
    def start_processing(self):
        """데이터 처리 시작"""
        self.is_running = True

        for i in range(100):
            if not self.is_running:
                break

            # 시뮬레이션 데이터 처리
            time.sleep(0.1)
            self.progress_updated.emit(i + 1)

            # 처리된 데이터 전송
            data = {
                'timestamp': time.time(),
                'value': i * 0.5,
                'status': 'processing'
            }
            self.data_processed.emit(data)

    @Slot()
    def stop_processing(self):
        """데이터 처리 중지"""
        self.is_running = False

# 메인 윈도우에서 워커 사용
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_worker()

    def setup_worker(self):
        """워커 스레드 설정"""
        # 워커 객체 생성
        self.worker = DataWorker()

        # 새 스레드 생성 및 워커 이동
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        # 시그널 연결
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.data_processed.connect(self.handle_data)

        # 스레드 시작
        self.worker_thread.start()

    def update_progress(self, value):
        """진행률 업데이트"""
        self.progress_bar.setValue(value)

    def handle_data(self, data):
        """처리된 데이터 핸들링"""
        self.display_data(data)
```

</div>

#### **1.2 실시간 데이터 수집 아키텍처**

##### **1.2.1 데이터 수집 전략**

<div class="architecture-diagram">

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Equipment     │────│  Data Collector  │────│   UI Thread     │
│   (Serial/TCP)  │    │   (Worker)       │    │   (Display)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Data Storage   │
                       │    (SQLite)      │
                       └──────────────────┘
```

**핵심 구성 요소**:
1. **Data Collector**: 장비에서 실시간 데이터 수집
2. **Data Processor**: 원시 데이터 변환 및 필터링
3. **Data Storage**: 데이터베이스 저장 및 이력 관리
4. **UI Updater**: 안전한 UI 업데이트

</div>

##### **1.2.2 성능 고려사항**

```python
class HighPerformanceDataCollector(QObject):
    """고성능 데이터 수집기"""

    def __init__(self, batch_size=100):
        super().__init__()
        self.batch_size = batch_size
        self.data_buffer = []
        self.last_update = time.time()

    def collect_data_point(self, data):
        """데이터 포인트 수집"""
        # 버퍼에 데이터 추가
        self.data_buffer.append(data)

        # 배치 처리로 성능 향상
        if len(self.data_buffer) >= self.batch_size:
            self.process_batch()

    def process_batch(self):
        """배치 단위 데이터 처리"""
        if not self.data_buffer:
            return

        # 배치 데이터 처리
        batch_data = self.data_buffer.copy()
        self.data_buffer.clear()

        # 백그라운드에서 처리
        self.process_data_async(batch_data)
```

#### **1.3 통신 프로토콜 및 인터페이스**

##### **1.3.1 시리얼 통신 (QSerialPort)**

```python
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from PySide6.QtCore import QIODevice

class SerialCommunicator(QObject):
    """시리얼 통신 관리자"""

    data_received = Signal(bytes)
    connection_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self.serial_port = QSerialPort()
        self.serial_port.readyRead.connect(self.read_data)

    def connect_to_device(self, port_name, baud_rate=9600):
        """장비 연결"""
        self.serial_port.setPortName(port_name)
        self.serial_port.setBaudRate(baud_rate)
        self.serial_port.setDataBits(QSerialPort.Data8)
        self.serial_port.setParity(QSerialPort.NoParity)
        self.serial_port.setStopBits(QSerialPort.OneStop)

        if self.serial_port.open(QIODevice.ReadWrite):
            self.connection_changed.emit(True)
            return True
        return False

    def read_data(self):
        """데이터 읽기"""
        data = self.serial_port.readAll()
        self.data_received.emit(data.data())

    def send_command(self, command):
        """명령 전송"""
        if self.serial_port.isOpen():
            self.serial_port.write(command.encode())
```

##### **1.3.2 네트워크 통신 (QTcpSocket)**

```python
from PySide6.QtNetwork import QTcpSocket, QHostAddress

class TcpCommunicator(QObject):
    """TCP 네트워크 통신 관리자"""

    data_received = Signal(bytes)
    connection_status = Signal(bool)

    def __init__(self):
        super().__init__()
        self.tcp_socket = QTcpSocket()
        self.tcp_socket.readyRead.connect(self.read_data)
        self.tcp_socket.connected.connect(lambda: self.connection_status.emit(True))
        self.tcp_socket.disconnected.connect(lambda: self.connection_status.emit(False))

    def connect_to_server(self, host, port):
        """서버 연결"""
        self.tcp_socket.connectToHost(QHostAddress(host), port)

    def read_data(self):
        """데이터 읽기"""
        data = self.tcp_socket.readAll()
        self.data_received.emit(data.data())

    def send_data(self, data):
        """데이터 전송"""
        if self.tcp_socket.state() == QTcpSocket.ConnectedState:
            self.tcp_socket.write(data)
```

---

## 2️⃣ 기초 실습 (45분)
### 🛠️ **QThread 기반 실시간 데이터 수집 시스템**

#### **2.1 기본 멀티스레딩 구현**

##### **2.1.1 데이터 수집 워커 생성**

<div class="practice-section">

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import random
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QHBoxLayout, QWidget, QPushButton, QLabel,
                               QProgressBar, QTextEdit, QLCDNumber)
from PySide6.QtCore import QObject, QThread, Signal, Slot, QTimer
from PySide6.QtGui import QFont

class EquipmentDataCollector(QObject):
    """반도체 장비 데이터 수집 워커"""

    # 시그널 정의
    data_collected = Signal(dict)
    progress_updated = Signal(int)
    status_changed = Signal(str)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.is_collecting = False
        self.collection_count = 0

        # 시뮬레이션 데이터 범위
        self.temp_range = (300, 400)  # °C
        self.pressure_range = (1.0, 10.0)  # Torr
        self.flow_range = (50, 200)  # sccm

    @Slot()
    def start_collection(self):
        """데이터 수집 시작"""
        self.is_collecting = True
        self.collection_count = 0
        self.status_changed.emit("데이터 수집 시작")

        try:
            while self.is_collecting:
                # 시뮬레이션 데이터 생성
                data_point = self.generate_simulation_data()

                # 데이터 수집 신호 발송
                self.data_collected.emit(data_point)

                # 진행률 업데이트
                self.collection_count += 1
                progress = (self.collection_count % 100) + 1
                self.progress_updated.emit(progress)

                # 수집 간격 (100ms)
                time.sleep(0.1)

        except Exception as e:
            self.error_occurred.emit(f"데이터 수집 오류: {str(e)}")

    @Slot()
    def stop_collection(self):
        """데이터 수집 중지"""
        self.is_collecting = False
        self.status_changed.emit("데이터 수집 중지")

    def generate_simulation_data(self):
        """시뮬레이션 데이터 생성"""
        # 시간에 따른 변화 시뮬레이션
        time_factor = time.time() % 60  # 60초 주기

        # 온도: 사인파 + 노이즈
        base_temp = 350 + 20 * math.sin(time_factor / 10)
        temperature = base_temp + random.uniform(-5, 5)

        # 압력: 코사인파 + 노이즈
        base_pressure = 5.5 + 2 * math.cos(time_factor / 15)
        pressure = base_pressure + random.uniform(-0.5, 0.5)

        # 가스 유량: 랜덤 변화
        gas_flow = 100 + random.uniform(-20, 20)

        # RF 파워: 단계적 변화
        rf_power = 300 + (int(time_factor / 10) % 3) * 50 + random.uniform(-10, 10)

        return {
            'timestamp': datetime.now(),
            'chamber_temperature': round(temperature, 2),
            'chamber_pressure': round(pressure, 3),
            'gas_flow_rate': round(gas_flow, 1),
            'rf_power': round(rf_power, 1),
            'recipe_step': int(time_factor / 10) % 5 + 1,
            'status': 'Running' if self.is_collecting else 'Stopped'
        }

class RealtimeMonitorWindow(QMainWindow):
    """실시간 모니터링 윈도우"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_worker_thread()

        # 데이터 저장용
        self.data_history = []

    def setup_ui(self):
        """UI 설정"""
        self.setWindowTitle("반도체 장비 실시간 모니터링")
        self.setGeometry(100, 100, 800, 600)

        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)

        # 컨트롤 버튼들
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("수집 시작")
        self.stop_button = QPushButton("수집 중지")
        self.stop_button.setEnabled(False)

        self.start_button.clicked.connect(self.start_collection)
        self.stop_button.clicked.connect(self.stop_collection)

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addStretch()

        # 상태 표시
        self.status_label = QLabel("대기 중")
        self.status_label.setFont(QFont("Arial", 12))
        control_layout.addWidget(self.status_label)

        main_layout.addLayout(control_layout)

        # 진행률 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        main_layout.addWidget(self.progress_bar)

        # 데이터 표시 영역
        data_layout = QHBoxLayout()

        # 온도 표시
        temp_layout = QVBoxLayout()
        temp_layout.addWidget(QLabel("챔버 온도 (°C)"))
        self.temp_lcd = QLCDNumber(6)
        self.temp_lcd.setStyleSheet("QLCDNumber { background-color: #001100; color: #00FF00; }")
        temp_layout.addWidget(self.temp_lcd)
        data_layout.addLayout(temp_layout)

        # 압력 표시
        pressure_layout = QVBoxLayout()
        pressure_layout.addWidget(QLabel("챔버 압력 (Torr)"))
        self.pressure_lcd = QLCDNumber(6)
        self.pressure_lcd.setStyleSheet("QLCDNumber { background-color: #000011; color: #0000FF; }")
        pressure_layout.addWidget(self.pressure_lcd)
        data_layout.addLayout(pressure_layout)

        # 가스 유량 표시
        flow_layout = QVBoxLayout()
        flow_layout.addWidget(QLabel("가스 유량 (sccm)"))
        self.flow_lcd = QLCDNumber(6)
        self.flow_lcd.setStyleSheet("QLCDNumber { background-color: #110000; color: #FF0000; }")
        flow_layout.addWidget(self.flow_lcd)
        data_layout.addLayout(flow_layout)

        main_layout.addLayout(data_layout)

        # 로그 표시
        main_layout.addWidget(QLabel("데이터 로그"))
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        main_layout.addWidget(self.log_text)

    def setup_worker_thread(self):
        """워커 스레드 설정"""
        # 워커 객체 생성
        self.data_collector = EquipmentDataCollector()

        # 스레드 생성 및 워커 이동
        self.worker_thread = QThread()
        self.data_collector.moveToThread(self.worker_thread)

        # 시그널 연결
        self.data_collector.data_collected.connect(self.handle_new_data)
        self.data_collector.progress_updated.connect(self.progress_bar.setValue)
        self.data_collector.status_changed.connect(self.status_label.setText)
        self.data_collector.error_occurred.connect(self.handle_error)

        # 스레드 라이프사이클 관리
        self.worker_thread.started.connect(self.data_collector.start_collection)

        # 스레드 시작
        self.worker_thread.start()

    def start_collection(self):
        """데이터 수집 시작"""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # 워커에게 시작 신호 전송
        if hasattr(self.data_collector, 'start_collection'):
            # 이미 실행 중인 경우 재시작
            self.data_collector.stop_collection()
            QTimer.singleShot(100, self.data_collector.start_collection)

    def stop_collection(self):
        """데이터 수집 중지"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # 워커에게 중지 신호 전송
        self.data_collector.stop_collection()

    @Slot(dict)
    def handle_new_data(self, data):
        """새 데이터 처리"""
        # LCD 디스플레이 업데이트
        self.temp_lcd.display(data['chamber_temperature'])
        self.pressure_lcd.display(data['chamber_pressure'])
        self.flow_lcd.display(data['gas_flow_rate'])

        # 데이터 히스토리에 저장
        self.data_history.append(data)

        # 최근 50개 데이터만 유지
        if len(self.data_history) > 50:
            self.data_history.pop(0)

        # 로그에 출력
        timestamp = data['timestamp'].strftime('%H:%M:%S')
        log_entry = (f"[{timestamp}] "
                    f"온도: {data['chamber_temperature']}°C, "
                    f"압력: {data['chamber_pressure']}Torr, "
                    f"유량: {data['gas_flow_rate']}sccm")

        self.log_text.append(log_entry)

        # 스크롤을 최신 로그로 이동
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    @Slot(str)
    def handle_error(self, error_message):
        """오류 처리"""
        self.log_text.append(f"❌ 오류: {error_message}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def closeEvent(self, event):
        """윈도우 종료 시 스레드 정리"""
        self.data_collector.stop_collection()
        self.worker_thread.quit()
        self.worker_thread.wait()
        event.accept()

