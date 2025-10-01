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
