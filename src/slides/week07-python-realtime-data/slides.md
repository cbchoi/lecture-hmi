# Week 7: Python PySide6 실시간 데이터 처리 및 멀티스레딩

## 🎯 **학습 목표**
- **PySide6 멀티스레딩**: QThread를 활용한 UI 블록킹 방지 및 고성능 데이터 처리
- **실시간 통신**: 시리얼/네트워크 프로토콜을 통한 반도체 장비 연동
- **데이터베이스 연동**: SQLite를 활용한 대용량 데이터 저장 및 이력 관리
- **성능 최적화**: 메모리 효율성 및 실시간 처리 성능 향상 기법

---

## 1️⃣ 이론 강의 (45분)
### 📚 **PySide6 멀티스레딩 및 실시간 처리 아키텍처**

#### **1.1 Qt Threading 모델 이해**

<div class="concept-explanation">

**🔄 Qt의 스레드 모델**:
- **메인 스레드 (GUI 스레드)**: UI 업데이트 및 이벤트 처리 전담
- **워커 스레드**: 무거운 작업 및 데이터 처리 담당
- **스레드 간 통신**: 시그널-슬롯을 통한 안전한 데이터 교환

**⚠️ 주의사항**:
- GUI 객체는 메인 스레드에서만 접근 가능
- 스레드 간 직접적인 데이터 공유 금지
- 시그널-슬롯 메커니즘을 통한 스레드 안전 통신

</div>

##### **1.1.1 QThread vs Threading 모듈**

```python
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

# 메인 실행
if __name__ == "__main__":
    import math

    app = QApplication(sys.argv)

    window = RealtimeMonitorWindow()
    window.show()

    sys.exit(app.exec())
```

</div>

#### **2.2 타이머 기반 정밀 제어**

##### **2.2.1 고정밀 데이터 수집**

<div class="code-example">

```python
from PySide6.QtCore import QTimer, QElapsedTimer

class PrecisionDataCollector(QObject):
    """정밀 타이밍 데이터 수집기"""

    data_ready = Signal(dict, float)  # data, elapsed_time

    def __init__(self, interval_ms=100):
        super().__init__()
        self.interval_ms = interval_ms

        # 고정밀 타이머
        self.timer = QTimer()
        self.timer.timeout.connect(self.collect_data)
        self.timer.setTimerType(Qt.PreciseTimer)

        # 경과 시간 측정
        self.elapsed_timer = QElapsedTimer()

        # 성능 통계
        self.collection_stats = {
            'total_collections': 0,
            'average_interval': 0,
            'max_deviation': 0
        }

    def start_collection(self, interval_ms=None):
        """수집 시작"""
        if interval_ms:
            self.interval_ms = interval_ms

        self.elapsed_timer.start()
        self.timer.start(self.interval_ms)

    def stop_collection(self):
        """수집 중지"""
        self.timer.stop()

    def collect_data(self):
        """데이터 수집 및 타이밍 측정"""
        # 실제 경과 시간 측정
        elapsed = self.elapsed_timer.restart()

        # 타이밍 통계 업데이트
        self.update_timing_stats(elapsed)

        # 데이터 생성
        data = self.generate_sample_data()

        # 시그널 발송 (데이터 + 타이밍 정보)
        self.data_ready.emit(data, elapsed)

    def update_timing_stats(self, elapsed):
        """타이밍 통계 업데이트"""
        self.collection_stats['total_collections'] += 1

        # 평균 간격 계산
        total = self.collection_stats['total_collections']
        avg = self.collection_stats['average_interval']
        self.collection_stats['average_interval'] = (avg * (total - 1) + elapsed) / total

        # 최대 편차 추적
        deviation = abs(elapsed - self.interval_ms)
        if deviation > self.collection_stats['max_deviation']:
            self.collection_stats['max_deviation'] = deviation

    def generate_sample_data(self):
        """샘플 데이터 생성"""
        return {
            'timestamp': datetime.now(),
            'value': random.uniform(0, 100),
            'sequence': self.collection_stats['total_collections']
        }
```

</div>

---

## 3️⃣ 심화 실습 (45분)
### ⚡ **데이터베이스 연동 및 고급 통신 구현**

#### **3.1 SQLite 데이터베이스 연동**

##### **3.1.1 데이터 모델 및 ORM**

<div class="database-section">

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from datetime import datetime, timedelta
from PySide6.QtCore import QObject, Signal, Slot
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class EquipmentData:
    """장비 데이터 모델"""
    id: Optional[int] = None
    timestamp: datetime = None
    chamber_temperature: float = 0.0
    chamber_pressure: float = 0.0
    gas_flow_rate: float = 0.0
    rf_power: float = 0.0
    recipe_step: int = 0
    recipe_id: Optional[int] = None
    status: str = "Unknown"
    alarm_flags: str = ""  # JSON string

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class Recipe:
    """레시피 데이터 모델"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    steps: str = ""  # JSON string
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class DatabaseManager(QObject):
    """데이터베이스 관리자"""

    data_saved = Signal(bool)
    data_loaded = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, db_path="equipment_data.db"):
        super().__init__()
        self.db_path = db_path
        self.connection = None
        self.init_database()

    def init_database(self):
        """데이터베이스 초기화"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row

            # 테이블 생성
            self.create_tables()

        except Exception as e:
            self.error_occurred.emit(f"데이터베이스 초기화 실패: {str(e)}")

    def create_tables(self):
        """테이블 생성"""
        cursor = self.connection.cursor()

        # 장비 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                chamber_temperature REAL,
                chamber_pressure REAL,
                gas_flow_rate REAL,
                rf_power REAL,
                recipe_step INTEGER,
                recipe_id INTEGER,
                status TEXT,
                alarm_flags TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')

        # 레시피 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                steps TEXT,  -- JSON
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 알람 로그 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alarm_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                alarm_type TEXT,
                severity TEXT,
                message TEXT,
                acknowledged BOOLEAN DEFAULT FALSE,
                acknowledged_by TEXT,
                acknowledged_at TEXT
            )
        ''')

        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_equipment_timestamp ON equipment_data(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alarm_timestamp ON alarm_logs(timestamp)')

        self.connection.commit()

    @Slot(dict)
    def save_equipment_data(self, data_dict):
        """장비 데이터 저장"""
        try:
            cursor = self.connection.cursor()

            # 데이터 변환
            timestamp_str = data_dict['timestamp'].isoformat()

            cursor.execute('''
                INSERT INTO equipment_data
                (timestamp, chamber_temperature, chamber_pressure, gas_flow_rate,
                 rf_power, recipe_step, status, alarm_flags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp_str,
                data_dict.get('chamber_temperature', 0),
                data_dict.get('chamber_pressure', 0),
                data_dict.get('gas_flow_rate', 0),
                data_dict.get('rf_power', 0),
                data_dict.get('recipe_step', 0),
                data_dict.get('status', 'Unknown'),
                json.dumps(data_dict.get('alarm_flags', {}))
            ))

            self.connection.commit()
            self.data_saved.emit(True)

        except Exception as e:
            self.error_occurred.emit(f"데이터 저장 실패: {str(e)}")
            self.data_saved.emit(False)

    def load_recent_data(self, hours=24):
        """최근 데이터 로드"""
        try:
            cursor = self.connection.cursor()

            # 시간 범위 계산
            start_time = datetime.now() - timedelta(hours=hours)
            start_time_str = start_time.isoformat()

            cursor.execute('''
                SELECT * FROM equipment_data
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 1000
            ''', (start_time_str,))

            rows = cursor.fetchall()

            # 딕셔너리 리스트로 변환
            data_list = []
            for row in rows:
                data = dict(row)
                data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                if data['alarm_flags']:
                    data['alarm_flags'] = json.loads(data['alarm_flags'])
                data_list.append(data)

            self.data_loaded.emit(data_list)
            return data_list

        except Exception as e:
            self.error_occurred.emit(f"데이터 로드 실패: {str(e)}")
            return []

    def save_recipe(self, recipe: Recipe):
        """레시피 저장"""
        try:
            cursor = self.connection.cursor()

            if recipe.id is None:
                # 새 레시피 삽입
                cursor.execute('''
                    INSERT INTO recipes (name, description, steps)
                    VALUES (?, ?, ?)
                ''', (recipe.name, recipe.description, recipe.steps))
                recipe.id = cursor.lastrowid
            else:
                # 기존 레시피 업데이트
                cursor.execute('''
                    UPDATE recipes
                    SET name=?, description=?, steps=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                ''', (recipe.name, recipe.description, recipe.steps, recipe.id))

            self.connection.commit()
            return True

        except Exception as e:
            self.error_occurred.emit(f"레시피 저장 실패: {str(e)}")
            return False

    def get_statistics(self, hours=24):
        """통계 정보 조회"""
        try:
            cursor = self.connection.cursor()

            start_time = datetime.now() - timedelta(hours=hours)
            start_time_str = start_time.isoformat()

            cursor.execute('''
                SELECT
                    COUNT(*) as total_records,
                    AVG(chamber_temperature) as avg_temperature,
                    MIN(chamber_temperature) as min_temperature,
                    MAX(chamber_temperature) as max_temperature,
                    AVG(chamber_pressure) as avg_pressure,
                    MIN(chamber_pressure) as min_pressure,
                    MAX(chamber_pressure) as max_pressure
                FROM equipment_data
                WHERE timestamp >= ?
            ''', (start_time_str,))

            row = cursor.fetchone()
            return dict(row) if row else {}

        except Exception as e:
            self.error_occurred.emit(f"통계 조회 실패: {str(e)}")
            return {}

    def cleanup_old_data(self, days=30):
        """오래된 데이터 정리"""
        try:
            cursor = self.connection.cursor()

            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_date_str = cutoff_date.isoformat()

            cursor.execute('''
                DELETE FROM equipment_data
                WHERE timestamp < ?
            ''', (cutoff_date_str,))

            deleted_count = cursor.rowcount
            self.connection.commit()

            return deleted_count

        except Exception as e:
            self.error_occurred.emit(f"데이터 정리 실패: {str(e)}")
            return 0

    def close(self):
        """데이터베이스 연결 종료"""
        if self.connection:
            self.connection.close()
```

</div>

#### **3.2 실시간 차트 및 시각화**

##### **3.2.1 PyQtGraph 실시간 차트**

<div class="visualization-section">

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyqtgraph as pg
import numpy as np
from collections import deque
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtGui import QFont

# PyQtGraph 설정
pg.setConfigOptions(antialias=True)

class RealtimeChart(QWidget):
    """실시간 차트 위젯"""

    def __init__(self, title="실시간 데이터", max_points=1000):
        super().__init__()
        self.title = title
        self.max_points = max_points
        self.setup_ui()
        self.setup_data_buffers()

    def setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)

        # 제목
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)

        # 그래프 위젯
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)

        # 축 라벨 설정
        self.plot_widget.setLabel('left', '값')
        self.plot_widget.setLabel('bottom', '시간 (초)')

        layout.addWidget(self.plot_widget)

        # 범례
        self.legend = self.plot_widget.addLegend()

    def setup_data_buffers(self):
        """데이터 버퍼 설정"""
        self.time_data = deque(maxlen=self.max_points)
        self.data_series = {}
        self.plot_lines = {}
        self.start_time = None

    def add_data_series(self, name, color='b', width=2):
        """데이터 시리즈 추가"""
        if name not in self.data_series:
            self.data_series[name] = deque(maxlen=self.max_points)

            # 플롯 라인 생성
            pen = pg.mkPen(color=color, width=width)
            self.plot_lines[name] = self.plot_widget.plot(
                [], [], name=name, pen=pen
            )

    def update_data(self, timestamp, **data_values):
        """데이터 업데이트"""
        if self.start_time is None:
            self.start_time = timestamp

        # 상대 시간 계산 (초)
        relative_time = (timestamp - self.start_time).total_seconds()
        self.time_data.append(relative_time)

        # 각 시리즈 데이터 업데이트
        for name, value in data_values.items():
            if name in self.data_series:
                self.data_series[name].append(value)

                # 플롯 업데이트
                if len(self.time_data) > 1:
                    self.plot_lines[name].setData(
                        list(self.time_data),
                        list(self.data_series[name])
                    )

    def clear_data(self):
        """데이터 클리어"""
        self.time_data.clear()
        for series in self.data_series.values():
            series.clear()
        for line in self.plot_lines.values():
            line.setData([], [])
        self.start_time = None

class MultiChannelRealtimeChart(QWidget):
    """다중 채널 실시간 차트"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_charts()

    def setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)

        # 차트 컨테이너
        self.chart_layout = QVBoxLayout()
        layout.addLayout(self.chart_layout)

        # 통계 정보 표시
        stats_layout = QHBoxLayout()
        self.stats_labels = {}

        stats_info = [
            ('온도 평균', 'avg_temp'),
            ('압력 평균', 'avg_pressure'),
            ('유량 평균', 'avg_flow'),
            ('데이터 포인트', 'data_points')
        ]

        for label_text, key in stats_info:
            label = QLabel(f"{label_text}: 0")
            label.setFont(QFont("Arial", 10))
            self.stats_labels[key] = label
            stats_layout.addWidget(label)

        layout.addLayout(stats_layout)

    def setup_charts(self):
        """차트 설정"""
        # 온도 차트
        self.temp_chart = RealtimeChart("챔버 온도 (°C)")
        self.temp_chart.add_data_series("온도", color='r', width=2)
        self.chart_layout.addWidget(self.temp_chart)

        # 압력 차트
        self.pressure_chart = RealtimeChart("챔버 압력 (Torr)")
        self.pressure_chart.add_data_series("압력", color='b', width=2)
        self.chart_layout.addWidget(self.pressure_chart)

        # 가스 유량 차트
        self.flow_chart = RealtimeChart("가스 유량 (sccm)")
        self.flow_chart.add_data_series("유량", color='g', width=2)
        self.chart_layout.addWidget(self.flow_chart)

        # 통계 계산용 데이터
        self.temp_buffer = deque(maxlen=100)
        self.pressure_buffer = deque(maxlen=100)
        self.flow_buffer = deque(maxlen=100)

    @Slot(dict)
    def update_charts(self, data):
        """차트 업데이트"""
        timestamp = data['timestamp']
        temp = data['chamber_temperature']
        pressure = data['chamber_pressure']
        flow = data['gas_flow_rate']

        # 차트 업데이트
        self.temp_chart.update_data(timestamp, 온도=temp)
        self.pressure_chart.update_data(timestamp, 압력=pressure)
        self.flow_chart.update_data(timestamp, 유량=flow)

        # 통계 버퍼 업데이트
        self.temp_buffer.append(temp)
        self.pressure_buffer.append(pressure)
        self.flow_buffer.append(flow)

        # 통계 정보 업데이트
        self.update_statistics()

    def update_statistics(self):
        """통계 정보 업데이트"""
        if len(self.temp_buffer) > 0:
            avg_temp = np.mean(self.temp_buffer)
            self.stats_labels['avg_temp'].setText(f"온도 평균: {avg_temp:.1f}°C")

        if len(self.pressure_buffer) > 0:
            avg_pressure = np.mean(self.pressure_buffer)
            self.stats_labels['avg_pressure'].setText(f"압력 평균: {avg_pressure:.2f}Torr")

        if len(self.flow_buffer) > 0:
            avg_flow = np.mean(self.flow_buffer)
            self.stats_labels['avg_flow'].setText(f"유량 평균: {avg_flow:.1f}sccm")

        total_points = len(self.temp_buffer)
        self.stats_labels['data_points'].setText(f"데이터 포인트: {total_points}")

    def clear_all_charts(self):
        """모든 차트 클리어"""
        self.temp_chart.clear_data()
        self.pressure_chart.clear_data()
        self.flow_chart.clear_data()

        self.temp_buffer.clear()
        self.pressure_buffer.clear()
        self.flow_buffer.clear()

        # 통계 라벨 리셋
        for label in self.stats_labels.values():
            label.setText(label.text().split(':')[0] + ": 0")
```

</div>

#### **3.3 고급 통신 구현**

##### **3.3.1 프로토콜 핸들러**

<div class="communication-section">

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import json
from enum import Enum
from PySide6.QtCore import QObject, Signal, Slot, QByteArray
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtNetwork import QTcpSocket

class MessageType(Enum):
    """메시지 타입 정의"""
    HEARTBEAT = 0x01
    DATA_REQUEST = 0x02
    DATA_RESPONSE = 0x03
    COMMAND = 0x04
    STATUS = 0x05
    ERROR = 0x06
    ALARM = 0x07

class ProtocolHandler(QObject):
    """통신 프로토콜 핸들러"""

    message_received = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.message_buffer = QByteArray()
        self.sequence_number = 0

    def create_message(self, msg_type: MessageType, data: dict):
        """메시지 생성"""
        try:
            # 헤더 구성
            header = struct.pack(
                '<BBH',  # little-endian, byte, byte, unsigned short
                0xAA,    # Start marker
                msg_type.value,
                self.sequence_number
            )

            # 데이터 직렬화
            payload = json.dumps(data).encode('utf-8')
            payload_length = len(payload)

            # 체크섬 계산
            checksum = sum(payload) & 0xFF

            # 전체 메시지 구성
            message = header + struct.pack('<HB', payload_length, checksum) + payload

            self.sequence_number = (self.sequence_number + 1) % 65536
            return message

        except Exception as e:
            self.error_occurred.emit(f"메시지 생성 실패: {str(e)}")
            return None

    def parse_message(self, data: bytes):
        """메시지 파싱"""
        self.message_buffer.append(data)

        while len(self.message_buffer) >= 6:  # 최소 헤더 크기
            # 시작 마커 찾기
            start_idx = self.message_buffer.indexOf(0xAA)
            if start_idx == -1:
                self.message_buffer.clear()
                break

            # 시작 마커 이전 데이터 제거
            if start_idx > 0:
                self.message_buffer = self.message_buffer.mid(start_idx)

            # 헤더 파싱
            if len(self.message_buffer) < 6:
                break

            header_data = bytes(self.message_buffer.data()[:6])
            start_marker, msg_type, seq_num, payload_length, checksum = struct.unpack('<BBHHB', header_data)

            # 전체 메시지 길이 확인
            total_length = 6 + payload_length
            if len(self.message_buffer) < total_length:
                break

            # 페이로드 추출
            payload_data = bytes(self.message_buffer.data()[6:total_length])

            # 체크섬 검증
            calculated_checksum = sum(payload_data) & 0xFF
            if calculated_checksum != checksum:
                self.error_occurred.emit(f"체크섬 오류: 예상={checksum}, 실제={calculated_checksum}")
                self.message_buffer = self.message_buffer.mid(1)
                continue

            try:
                # 페이로드 디코딩
                payload_str = payload_data.decode('utf-8')
                payload_dict = json.loads(payload_str)

                # 메시지 객체 생성
                message = {
                    'type': MessageType(msg_type),
                    'sequence': seq_num,
                    'data': payload_dict
                }

                self.message_received.emit(message)

            except Exception as e:
                self.error_occurred.emit(f"메시지 파싱 실패: {str(e)}")

            # 처리된 메시지 제거
            self.message_buffer = self.message_buffer.mid(total_length)

class EquipmentCommunicator(QObject):
    """장비 통신 관리자"""

    connected = Signal(bool)
    data_received = Signal(dict)
    status_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.protocol = ProtocolHandler()
        self.serial_port = None
        self.tcp_socket = None

        # 프로토콜 핸들러 연결
        self.protocol.message_received.connect(self.handle_message)
        self.protocol.error_occurred.connect(self.handle_protocol_error)

        # 하트비트 타이머
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.send_heartbeat)

    def connect_serial(self, port_name, baud_rate=9600):
        """시리얼 연결"""
        try:
            self.serial_port = QSerialPort()
            self.serial_port.setPortName(port_name)
            self.serial_port.setBaudRate(baud_rate)
            self.serial_port.setDataBits(QSerialPort.Data8)
            self.serial_port.setParity(QSerialPort.NoParity)
            self.serial_port.setStopBits(QSerialPort.OneStop)

            if self.serial_port.open(QSerialPort.ReadWrite):
                self.serial_port.readyRead.connect(self.read_serial_data)
                self.connected.emit(True)
                self.status_changed.emit(f"시리얼 연결됨: {port_name}")
                self.start_heartbeat()
                return True
            else:
                error = self.serial_port.errorString()
                self.status_changed.emit(f"시리얼 연결 실패: {error}")
                return False

        except Exception as e:
            self.status_changed.emit(f"시리얼 연결 오류: {str(e)}")
            return False

    def connect_tcp(self, host, port):
        """TCP 연결"""
        try:
            self.tcp_socket = QTcpSocket()
            self.tcp_socket.connected.connect(lambda: self.on_tcp_connected())
            self.tcp_socket.disconnected.connect(lambda: self.on_tcp_disconnected())
            self.tcp_socket.readyRead.connect(self.read_tcp_data)
            self.tcp_socket.error.connect(self.handle_tcp_error)

            self.tcp_socket.connectToHost(host, port)
            return True

        except Exception as e:
            self.status_changed.emit(f"TCP 연결 오류: {str(e)}")
            return False

    def read_serial_data(self):
        """시리얼 데이터 읽기"""
        if self.serial_port and self.serial_port.bytesAvailable():
            data = bytes(self.serial_port.readAll())
            self.protocol.parse_message(data)

    def read_tcp_data(self):
        """TCP 데이터 읽기"""
        if self.tcp_socket and self.tcp_socket.bytesAvailable():
            data = bytes(self.tcp_socket.readAll())
            self.protocol.parse_message(data)

    def send_command(self, command, parameters=None):
        """명령 전송"""
        data = {
            'command': command,
            'parameters': parameters or {},
            'timestamp': datetime.now().isoformat()
        }

        message = self.protocol.create_message(MessageType.COMMAND, data)
        if message:
            self.send_raw_data(message)

    def send_raw_data(self, data):
        """원시 데이터 전송"""
        if self.serial_port and self.serial_port.isOpen():
            self.serial_port.write(data)
        elif self.tcp_socket and self.tcp_socket.state() == QTcpSocket.ConnectedState:
            self.tcp_socket.write(data)

    def start_heartbeat(self):
        """하트비트 시작"""
        self.heartbeat_timer.start(5000)  # 5초 간격

    def send_heartbeat(self):
        """하트비트 전송"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'client_id': 'hmi_client'
        }
        message = self.protocol.create_message(MessageType.HEARTBEAT, data)
        if message:
            self.send_raw_data(message)

    @Slot(dict)
    def handle_message(self, message):
        """수신 메시지 처리"""
        msg_type = message['type']
        msg_data = message['data']

        if msg_type == MessageType.DATA_RESPONSE:
            self.data_received.emit(msg_data)
        elif msg_type == MessageType.STATUS:
            self.status_changed.emit(f"장비 상태: {msg_data.get('status', 'Unknown')}")
        elif msg_type == MessageType.ALARM:
            self.handle_alarm(msg_data)
        elif msg_type == MessageType.ERROR:
            self.status_changed.emit(f"장비 오류: {msg_data.get('message', 'Unknown error')}")

    def handle_alarm(self, alarm_data):
        """알람 처리"""
        severity = alarm_data.get('severity', 'Warning')
        message = alarm_data.get('message', 'Unknown alarm')
        self.status_changed.emit(f"⚠️ {severity}: {message}")

    def on_tcp_connected(self):
        """TCP 연결 완료"""
        self.connected.emit(True)
        self.status_changed.emit("TCP 연결됨")
        self.start_heartbeat()

    def on_tcp_disconnected(self):
        """TCP 연결 해제"""
        self.connected.emit(False)
        self.status_changed.emit("TCP 연결 해제됨")
        self.heartbeat_timer.stop()

    def handle_tcp_error(self, error):
        """TCP 오류 처리"""
        error_string = self.tcp_socket.errorString()
        self.status_changed.emit(f"TCP 오류: {error_string}")

    def handle_protocol_error(self, error):
        """프로토콜 오류 처리"""
        self.status_changed.emit(f"프로토콜 오류: {error}")

    def disconnect(self):
        """연결 해제"""
        self.heartbeat_timer.stop()

        if self.serial_port and self.serial_port.isOpen():
            self.serial_port.close()
        if self.tcp_socket:
            self.tcp_socket.disconnectFromHost()

        self.connected.emit(False)
        self.status_changed.emit("연결 해제됨")
```

</div>

---

## 4️⃣ Hands-on 실습 (45분)
### 🚀 **통합 실시간 모니터링 시스템 구현**

#### **4.1 프로젝트 개요**

<div class="project-overview">

**🎯 목표**: 실제 반도체 장비와 유사한 수준의 실시간 데이터 수집, 처리, 저장, 시각화가 가능한 통합 HMI 시스템 구현

**📋 주요 기능**:
- 멀티스레드 기반 실시간 데이터 수집
- SQLite 데이터베이스 자동 저장
- PyQtGraph 실시간 차트 시각화
- 시리얼/네트워크 통신 지원
- 알람 및 이벤트 로깅
- 성능 모니터링 및 통계

</div>

#### **4.2 통합 애플리케이션 구현**

##### **4.2.1 메인 애플리케이션 (main.py)**

<div class="integration-code">

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import math
import random
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QHBoxLayout, QWidget, QPushButton, QLabel,
                               QTabWidget, QTextEdit, QGroupBox, QGridLayout,
                               QSpinBox, QComboBox, QCheckBox, QSplitter,
                               QMenuBar, QStatusBar, QProgressBar)
from PySide6.QtCore import QObject, QThread, Signal, Slot, QTimer, Qt
from PySide6.QtGui import QFont, QAction, QIcon

# 이전에 구현한 클래스들 import
from database_manager import DatabaseManager
from multi_channel_chart import MultiChannelRealtimeChart
from equipment_communicator import EquipmentCommunicator

class IntegratedEquipmentMonitor(QMainWindow):
    """통합 장비 모니터링 시스템"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_components()
        self.setup_connections()

        # 성능 통계
        self.performance_stats = {
            'data_points_collected': 0,
            'database_writes': 0,
            'chart_updates': 0,
            'start_time': datetime.now()
        }

    def setup_ui(self):
        """UI 설정"""
        self.setWindowTitle("반도체 장비 실시간 모니터링 시스템 v2.0")
        self.setGeometry(100, 100, 1400, 900)

        # 메뉴바 설정
        self.setup_menubar()

        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 메인 스플리터
        main_splitter = QSplitter(Qt.Horizontal)
        central_widget_layout = QVBoxLayout(central_widget)
        central_widget_layout.addWidget(main_splitter)

        # 왼쪽 패널 (제어 및 상태)
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)

        # 오른쪽 패널 (차트 및 데이터)
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)

        # 스플리터 비율 설정
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)

        # 상태바 설정
        self.setup_statusbar()

    def setup_menubar(self):
        """메뉴바 설정"""
        menubar = self.menuBar()

        # 파일 메뉴
        file_menu = menubar.addMenu('파일')

        export_action = QAction('데이터 내보내기', self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction('종료', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 도구 메뉴
        tools_menu = menubar.addMenu('도구')

        db_stats_action = QAction('데이터베이스 통계', self)
        db_stats_action.triggered.connect(self.show_database_stats)
        tools_menu.addAction(db_stats_action)

        clear_data_action = QAction('차트 데이터 클리어', self)
        clear_data_action.triggered.connect(self.clear_chart_data)
        tools_menu.addAction(clear_data_action)

    def create_left_panel(self):
        """왼쪽 제어 패널 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 데이터 수집 제어
        collection_group = QGroupBox("데이터 수집 제어")
        collection_layout = QVBoxLayout(collection_group)

        # 제어 버튼들
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("수집 시작")
        self.stop_button = QPushButton("수집 중지")
        self.stop_button.setEnabled(False)

        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        collection_layout.addLayout(button_layout)

        # 수집 설정
        settings_layout = QGridLayout()

        settings_layout.addWidget(QLabel("수집 간격 (ms):"), 0, 0)
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(10, 10000)
        self.interval_spinbox.setValue(100)
        settings_layout.addWidget(self.interval_spinbox, 0, 1)

        settings_layout.addWidget(QLabel("데이터베이스 저장:"), 1, 0)
        self.db_save_checkbox = QCheckBox()
        self.db_save_checkbox.setChecked(True)
        settings_layout.addWidget(self.db_save_checkbox, 1, 1)

        collection_layout.addLayout(settings_layout)
        layout.addWidget(collection_group)

        # 통신 설정
        comm_group = QGroupBox("통신 설정")
        comm_layout = QVBoxLayout(comm_group)

        comm_type_layout = QHBoxLayout()
        comm_type_layout.addWidget(QLabel("통신 방식:"))
        self.comm_type_combo = QComboBox()
        self.comm_type_combo.addItems(["시뮬레이션", "시리얼", "TCP/IP"])
        comm_type_layout.addWidget(self.comm_type_combo)
        comm_layout.addLayout(comm_type_layout)

        self.connect_button = QPushButton("연결")
        self.connect_button.clicked.connect(self.toggle_connection)
        comm_layout.addWidget(self.connect_button)

        layout.addWidget(comm_group)

        # 상태 정보
        status_group = QGroupBox("시스템 상태")
        status_layout = QVBoxLayout(status_group)

        self.status_labels = {}
        status_items = [
            ('연결 상태', 'connection'),
            ('수집 상태', 'collection'),
            ('데이터 포인트', 'data_points'),
            ('DB 저장 횟수', 'db_writes'),
            ('차트 업데이트', 'chart_updates')
        ]

        for label_text, key in status_items:
            label = QLabel(f"{label_text}: 대기")
            label.setFont(QFont("Arial", 9))
            self.status_labels[key] = label
            status_layout.addWidget(label)

        layout.addWidget(status_group)

        # 로그 영역
        log_group = QGroupBox("시스템 로그")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setFont(QFont("Consolas", 8))
        log_layout.addWidget(self.log_text)

        clear_log_button = QPushButton("로그 클리어")
        clear_log_button.clicked.connect(self.log_text.clear)
        log_layout.addWidget(clear_log_button)

        layout.addWidget(log_group)

        layout.addStretch()
        return widget

    def create_right_panel(self):
        """오른쪽 차트 패널 생성"""
        # 탭 위젯 생성
        tab_widget = QTabWidget()

        # 실시간 차트 탭
        self.chart_widget = MultiChannelRealtimeChart()
        tab_widget.addTab(self.chart_widget, "실시간 차트")

        # 데이터 테이블 탭 (추후 구현)
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        data_layout.addWidget(QLabel("데이터 테이블 (구현 예정)"))
        tab_widget.addTab(data_tab, "데이터 테이블")

        # 통계 탭 (추후 구현)
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        stats_layout.addWidget(QLabel("통계 정보 (구현 예정)"))
        tab_widget.addTab(stats_tab, "통계")

        return tab_widget

    def setup_statusbar(self):
        """상태바 설정"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # 진행률 표시
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusbar.addPermanentWidget(self.progress_bar)

        # 시간 표시
        self.time_label = QLabel()
        self.statusbar.addPermanentWidget(self.time_label)

        # 시간 업데이트 타이머
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)

        self.statusbar.showMessage("준비됨")

    def setup_components(self):
        """구성 요소 설정"""
        # 데이터베이스 관리자
        self.db_manager = DatabaseManager()

        # 데이터 수집 워커
        self.data_collector = EnhancedDataCollector()
        self.collector_thread = QThread()
        self.data_collector.moveToThread(self.collector_thread)

        # 통신 관리자
        self.communicator = EquipmentCommunicator()

        # 성능 모니터링 타이머
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance_stats)
        self.performance_timer.start(5000)  # 5초마다 업데이트

    def setup_connections(self):
        """시그널-슬롯 연결"""
        # 데이터 수집기 연결
        self.data_collector.data_collected.connect(self.handle_new_data)
        self.data_collector.status_changed.connect(self.update_collection_status)

        # 데이터베이스 연결
        self.db_manager.data_saved.connect(self.on_data_saved)
        self.db_manager.error_occurred.connect(self.on_db_error)

        # 통신 관리자 연결
        self.communicator.connected.connect(self.on_connection_changed)
        self.communicator.data_received.connect(self.handle_communication_data)
        self.communicator.status_changed.connect(self.log_message)

        # 스레드 시작
        self.collector_thread.start()

    def start_monitoring(self):
        """모니터링 시작"""
        try:
            interval = self.interval_spinbox.value()

            # UI 상태 업데이트
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.progress_bar.setVisible(True)

            # 데이터 수집 시작
            self.data_collector.set_interval(interval)
            self.data_collector.start_collection()

            # 성능 통계 리셋
            self.performance_stats = {
                'data_points_collected': 0,
                'database_writes': 0,
                'chart_updates': 0,
                'start_time': datetime.now()
            }

            self.log_message("모니터링 시작됨")
            self.statusbar.showMessage("모니터링 중...")

        except Exception as e:
            self.log_message(f"시작 오류: {str(e)}")

    def stop_monitoring(self):
        """모니터링 중지"""
        try:
            # UI 상태 업데이트
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.progress_bar.setVisible(False)

            # 데이터 수집 중지
            self.data_collector.stop_collection()

            self.log_message("모니터링 중지됨")
            self.statusbar.showMessage("준비됨")

        except Exception as e:
            self.log_message(f"중지 오류: {str(e)}")

    @Slot(dict)
    def handle_new_data(self, data):
        """새 데이터 처리"""
        try:
            # 차트 업데이트
            self.chart_widget.update_charts(data)
            self.performance_stats['chart_updates'] += 1

            # 데이터베이스 저장
            if self.db_save_checkbox.isChecked():
                self.db_manager.save_equipment_data(data)

            # 통계 업데이트
            self.performance_stats['data_points_collected'] += 1

        except Exception as e:
            self.log_message(f"데이터 처리 오류: {str(e)}")

    @Slot(bool)
    def on_data_saved(self, success):
        """데이터 저장 완료"""
        if success:
            self.performance_stats['database_writes'] += 1

    @Slot(str)
    def on_db_error(self, error):
        """데이터베이스 오류"""
        self.log_message(f"DB 오류: {error}")

    def update_performance_stats(self):
        """성능 통계 업데이트"""
        stats = self.performance_stats
        runtime = (datetime.now() - stats['start_time']).total_seconds()

        if runtime > 0:
            data_rate = stats['data_points_collected'] / runtime

            self.status_labels['data_points'].setText(
                f"데이터 포인트: {stats['data_points_collected']} ({data_rate:.1f}/초)")
            self.status_labels['db_writes'].setText(
                f"DB 저장 횟수: {stats['database_writes']}")
            self.status_labels['chart_updates'].setText(
                f"차트 업데이트: {stats['chart_updates']}")

    def update_time(self):
        """시간 업데이트"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)

    def log_message(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

        # 자동 스크롤
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def toggle_connection(self):
        """연결 토글"""
        comm_type = self.comm_type_combo.currentText()

        if comm_type == "시뮬레이션":
            self.log_message("시뮬레이션 모드 활성화")
            self.status_labels['connection'].setText("연결 상태: 시뮬레이션")
        elif comm_type == "시리얼":
            # 시리얼 연결 구현
            self.log_message("시리얼 연결 시도...")
        elif comm_type == "TCP/IP":
            # TCP 연결 구현
            self.log_message("TCP/IP 연결 시도...")

    def on_connection_changed(self, connected):
        """연결 상태 변경"""
        status = "연결됨" if connected else "연결 해제됨"
        self.status_labels['connection'].setText(f"연결 상태: {status}")

    def update_collection_status(self, status):
        """수집 상태 업데이트"""
        self.status_labels['collection'].setText(f"수집 상태: {status}")

    def handle_communication_data(self, data):
        """통신 데이터 처리"""
        self.log_message(f"통신 데이터 수신: {data}")

    def export_data(self):
        """데이터 내보내기"""
        self.log_message("데이터 내보내기 기능 (구현 예정)")

    def show_database_stats(self):
        """데이터베이스 통계 표시"""
        stats = self.db_manager.get_statistics()
        self.log_message(f"DB 통계: {stats}")

    def clear_chart_data(self):
        """차트 데이터 클리어"""
        self.chart_widget.clear_all_charts()
        self.log_message("차트 데이터 클리어됨")

    def closeEvent(self, event):
        """애플리케이션 종료"""
        self.stop_monitoring()

        # 스레드 정리
        self.collector_thread.quit()
        self.collector_thread.wait()

        # 데이터베이스 연결 종료
        self.db_manager.close()

        event.accept()

class EnhancedDataCollector(QObject):
    """향상된 데이터 수집기"""

    data_collected = Signal(dict)
    status_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.is_collecting = False
        self.interval_ms = 100
        self.collection_timer = QTimer()
        self.collection_timer.timeout.connect(self.collect_data)
        self.sequence = 0

    def set_interval(self, interval_ms):
        """수집 간격 설정"""
        self.interval_ms = interval_ms
        if self.collection_timer.isActive():
            self.collection_timer.setInterval(interval_ms)

    @Slot()
    def start_collection(self):
        """수집 시작"""
        self.is_collecting = True
        self.sequence = 0
        self.collection_timer.start(self.interval_ms)
        self.status_changed.emit("수집 중")

    @Slot()
    def stop_collection(self):
        """수집 중지"""
        self.is_collecting = False
        self.collection_timer.stop()
        self.status_changed.emit("중지됨")

    def collect_data(self):
        """데이터 수집"""
        if not self.is_collecting:
            return

        # 고급 시뮬레이션 데이터 생성
        now = datetime.now()
        time_factor = time.time() % 120  # 2분 주기

        # 복잡한 패턴 시뮬레이션
        base_temp = 350 + 30 * math.sin(time_factor / 20) + 10 * math.sin(time_factor / 5)
        temperature = base_temp + random.gauss(0, 2)

        base_pressure = 5.0 + 3 * math.cos(time_factor / 15) + math.sin(time_factor / 3)
        pressure = max(0.1, base_pressure + random.gauss(0, 0.3))

        base_flow = 100 + 50 * math.sin(time_factor / 25)
        gas_flow = max(0, base_flow + random.gauss(0, 5))

        # 단계별 RF 파워
        step = int(time_factor / 30) % 4
        rf_base = [200, 300, 400, 250][step]
        rf_power = rf_base + random.gauss(0, 15)

        data = {
            'timestamp': now,
            'chamber_temperature': round(temperature, 2),
            'chamber_pressure': round(pressure, 3),
            'gas_flow_rate': round(gas_flow, 1),
            'rf_power': round(rf_power, 1),
            'recipe_step': step + 1,
            'status': 'Running',
            'sequence': self.sequence
        }

        self.sequence += 1
        self.data_collected.emit(data)

# 메인 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 애플리케이션 스타일 설정
    app.setStyle('Fusion')

    window = IntegratedEquipmentMonitor()
    window.show()

    sys.exit(app.exec())
```

</div>

#### **4.3 실습 과제 및 평가**

##### **🎯 실습 과제**

<div class="assignments">

**Phase 1: 기본 통합 (15분)**
1. **애플리케이션 실행**: 통합 모니터링 시스템 실행 및 기본 기능 확인
2. **데이터 수집**: 실시간 데이터 수집 시작 및 차트 업데이트 확인
3. **데이터베이스 저장**: SQLite 데이터베이스 저장 기능 테스트

**Phase 2: 고급 기능 (15분)**
1. **성능 최적화**: 수집 간격 조정 및 성능 모니터링
2. **통신 구현**: 시리얼 또는 TCP 통신 기능 추가
3. **알람 시스템**: 임계값 기반 알람 기능 구현

**Phase 3: 커스터마이징 (15분)**
1. **UI 개선**: 사용자 정의 차트 설정 및 레이아웃 조정
2. **데이터 분석**: 통계 정보 표시 및 트렌드 분석
3. **보고서 기능**: 데이터 내보내기 및 보고서 생성

</div>

##### **📊 평가 기준**

<div class="evaluation">

**💯 평가 항목**:
- **기능 완성도 (40%)**: 요구사항 구현 수준
- **성능 (25%)**: 실시간 처리 성능 및 안정성
- **코드 품질 (20%)**: 구조화, 주석, 오류 처리
- **사용성 (15%)**: UI/UX, 직관성, 편의성

**🏆 우수 기준**:
- 1000+ 데이터포인트/초 처리 가능
- 메모리 누수 없는 24시간 연속 운영
- 실제 장비 수준의 정확한 데이터 시뮬레이션
- 직관적이고 전문적인 산업용 UI

</div>

---

## 📝 **학습 정리 및 다음 주차 예고**

### **🎓 오늘 학습한 핵심 내용**
1. **QThread 멀티스레딩**: UI 블록킹 방지 및 백그라운드 처리
2. **실시간 데이터베이스**: SQLite 기반 고성능 데이터 저장
3. **고급 통신**: 시리얼/네트워크 프로토콜 구현
4. **실시간 차트**: PyQtGraph를 활용한 고성능 시각화
5. **성능 최적화**: 메모리 관리 및 처리 성능 향상

### **🔄 Python vs C# 실시간 처리 비교**
| 항목 | C# (Task/async) | Python (QThread) |
|------|----------------|------------------|
| **스레딩 모델** | Task Parallel Library | QThread + QObject |
| **UI 업데이트** | Dispatcher.Invoke | 시그널-슬롯 |
| **성능** | 네이티브 성능 | 해석형 언어 제약 |
| **메모리 관리** | GC 자동 관리 | 수동 + GC |
| **데이터베이스** | Entity Framework | SQLite3 직접 |

### **📅 다음 주차 예고: Python PySide6 고급 기능 및 배포**
- **고급 UI 컴포넌트**: 커스텀 위젯 및 3D 시각화
- **플러그인 아키텍처**: 모듈화 및 확장성 설계
- **국제화(i18n)**: 다국어 지원 및 지역화
- **패키징 및 배포**: PyInstaller, cx_Freeze 활용
- **크로스 플랫폼 최적화**: Windows/Linux/macOS 호환성