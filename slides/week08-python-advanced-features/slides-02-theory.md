# -*- coding: utf-8 -*-

import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QScrollArea, QMainWindow)
from PySide6.QtGui import QPainter, QPen, QBrush, QPolygon, QFont, QColor
from PySide6.QtCore import Qt, QRect, QPoint, Signal, QPropertyAnimation, QEasingCurve
from enum import Enum
import math

class ProcessStage(Enum):
    """프로세스 단계"""
    IDLE = "idle"
    PREP = "preparation"
    PROCESS = "processing"
    PURGE = "purging"
    COMPLETE = "complete"
    ERROR = "error"

class FlowComponent:
    """플로우 컴포넌트 기본 클래스"""

    def __init__(self, x, y, width, height, component_id, name):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.component_id = component_id
        self.name = name
        self.status = ProcessStage.IDLE
        self.value = 0.0
        self.connections = []  # 연결된 컴포넌트들

    def get_rect(self):
        return QRect(self.x, self.y, self.width, self.height)

    def get_center(self):
        return QPoint(self.x + self.width // 2, self.y + self.height // 2)

    def add_connection(self, target_component):
        if target_component not in self.connections:
            self.connections.append(target_component)

class Chamber(FlowComponent):
    """반응 챔버 컴포넌트"""

    def __init__(self, x, y, component_id="chamber_1", name="Main Chamber"):
        super().__init__(x, y, 120, 80, component_id, name)
        self.temperature = 25.0
        self.pressure = 1.0

    def draw(self, painter):
        rect = self.get_rect()

        # 상태에 따른 색상
        color_map = {
            ProcessStage.IDLE: QColor(200, 200, 200),
            ProcessStage.PREP: QColor(255, 255, 0),
            ProcessStage.PROCESS: QColor(0, 255, 0),
            ProcessStage.PURGE: QColor(255, 165, 0),
            ProcessStage.COMPLETE: QColor(0, 0, 255),
            ProcessStage.ERROR: QColor(255, 0, 0)
        }

        # 챔버 외곽
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(color_map[self.status]))
        painter.drawRoundedRect(rect, 10, 10)

        # 내부 원 (반응 영역)
        inner_rect = rect.adjusted(15, 15, -15, -15)
        painter.setBrush(QBrush(Qt.darkBlue))
        painter.drawEllipse(inner_rect)

        # 텍스트 정보
        painter.setPen(QPen(Qt.white))
        painter.setFont(QFont("Arial", 9, QFont.Bold))

        text_rect = QRect(rect.x(), rect.y() - 20, rect.width(), 15)
        painter.drawText(text_rect, Qt.AlignCenter, self.name)

        # 온도/압력 표시
        painter.setFont(QFont("Arial", 8))
        temp_text = f"T: {self.temperature:.1f}°C"
        pressure_text = f"P: {self.pressure:.1f}T"

        painter.drawText(rect.x() + 5, rect.y() + rect.height() + 15, temp_text)
        painter.drawText(rect.x() + 5, rect.y() + rect.height() + 28, pressure_text)

class GasLine(FlowComponent):
    """가스 라인 컴포넌트"""

    def __init__(self, x, y, component_id="gas_1", name="N2"):
        super().__init__(x, y, 80, 40, component_id, name)
        self.flow_rate = 0.0
        self.valve_open = False

    def draw(self, painter):
        rect = self.get_rect()

        # 밸브 상태에 따른 색상
        valve_color = QColor(0, 255, 0) if self.valve_open else QColor(255, 0, 0)

        # 가스 라인 (사각형)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(QColor(220, 220, 220)))
        painter.drawRect(rect)

        # 밸브 표시 (작은 원)
        valve_rect = QRect(rect.x() + rect.width() - 15, rect.y() + 5, 10, 10)
        painter.setBrush(QBrush(valve_color))
        painter.drawEllipse(valve_rect)

        # 가스명 표시
        painter.setPen(QPen(Qt.black))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, self.name)

        # 유량 표시
        painter.setFont(QFont("Arial", 8))
        flow_text = f"{self.flow_rate:.1f} sccm"
        flow_rect = QRect(rect.x(), rect.y() + rect.height() + 5, rect.width(), 15)
        painter.drawText(flow_rect, Qt.AlignCenter, flow_text)

class Pump(FlowComponent):
    """진공 펌프 컴포넌트"""

    def __init__(self, x, y, component_id="pump_1", name="Turbo Pump"):
        super().__init__(x, y, 60, 60, component_id, name)
        self.pump_speed = 0.0
        self.is_running = False

    def draw(self, painter):
        rect = self.get_rect()
        center = self.get_center()

        # 펌프 상태에 따른 색상
        pump_color = QColor(0, 255, 0) if self.is_running else QColor(128, 128, 128)

        # 펌프 몸체 (원)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(pump_color))
        painter.drawEllipse(rect)

        # 회전 블레이드 표시
        if self.is_running:
            painter.setPen(QPen(Qt.black, 3))
            blade_length = 20

            for i in range(4):
                angle = (i * 90 + self.pump_speed * 10) % 360
                rad = math.radians(angle)

                end_x = center.x() + blade_length * math.cos(rad)
                end_y = center.y() + blade_length * math.sin(rad)

                painter.drawLine(center, QPoint(int(end_x), int(end_y)))

        # 이름 표시
        painter.setPen(QPen(Qt.white))
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, self.name)

class ProcessFlowDiagram(QWidget):
    """프로세스 플로우 다이어그램 위젯"""

    component_clicked = Signal(str)
    component_status_changed = Signal(str, ProcessStage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)

        # 컴포넌트들
        self.components = {}
        self.connections = []  # (from_component, to_component, flow_rate)

        # 마우스 상호작용
        self.selected_component = None
        self.mouse_pos = QPoint()

        # 애니메이션
        self.animation_phase = 0.0
        self.animation_timer = None

        self.setup_components()

    def setup_components(self):
        """컴포넌트 배치 설정"""
        # 가스 라인들 (상단)
        gas_lines = [
            ("N2", 50, 50),
            ("Ar", 200, 50),
            ("SiH4", 350, 50),
            ("NH3", 500, 50)
        ]

        for name, x, y in gas_lines:
            component = GasLine(x, y, f"gas_{name.lower()}", name)
            self.components[component.component_id] = component

        # 메인 챔버 (중앙)
        chamber = Chamber(300, 200, "main_chamber", "CVD Chamber")
        self.components[chamber.component_id] = chamber

        # 펌프들 (하단)
        pumps = [
            ("Roughing Pump", 150, 400),
            ("Turbo Pump", 350, 400),
            ("Dry Pump", 550, 400)
        ]

        for name, x, y in pumps:
            pump = Pump(x, y, f"pump_{name.lower().replace(' ', '_')}", name)
            self.components[pump.component_id] = pump

        # 연결 설정
        self.setup_connections()

    def setup_connections(self):
        """컴포넌트 간 연결 설정"""
        # 가스 라인 -> 챔버
        for comp_id, component in self.components.items():
            if comp_id.startswith("gas_"):
                chamber = self.components["main_chamber"]
                component.add_connection(chamber)
                self.connections.append((component, chamber, 0.0))

        # 챔버 -> 펌프들
        chamber = self.components["main_chamber"]
        for comp_id, component in self.components.items():
            if comp_id.startswith("pump_"):
                chamber.add_connection(component)
                self.connections.append((chamber, component, 0.0))

    def paintEvent(self, event):
        """페인팅 이벤트"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 배경
        painter.fillRect(self.rect(), QColor(240, 240, 240))

        # 연결선 그리기
        self.draw_connections(painter)

        # 컴포넌트들 그리기
        for component in self.components.values():
            component.draw(painter)

        # 선택된 컴포넌트 하이라이트
        if self.selected_component:
            self.highlight_component(painter, self.selected_component)

    def draw_connections(self, painter):
        """연결선 그리기"""
        painter.setPen(QPen(Qt.blue, 3))

        for from_comp, to_comp, flow_rate in self.connections:
            from_center = from_comp.get_center()
            to_center = to_comp.get_center()

            # 화살표 그리기
            self.draw_arrow(painter, from_center, to_center, flow_rate)

    def draw_arrow(self, painter, start, end, flow_rate):
        """화살표 그리기"""
        # 기본 라인
        painter.drawLine(start, end)

        # 화살표 머리
        angle = math.atan2(end.y() - start.y(), end.x() - start.x())
        arrow_length = 15
        arrow_angle = math.pi / 6  # 30도

        # 화살표 점들
        arrow_p1 = QPoint(
            int(end.x() - arrow_length * math.cos(angle - arrow_angle)),
            int(end.y() - arrow_length * math.sin(angle - arrow_angle))
        )
        arrow_p2 = QPoint(
            int(end.x() - arrow_length * math.cos(angle + arrow_angle)),
            int(end.y() - arrow_length * math.sin(angle + arrow_angle))
        )

        arrow = QPolygon([end, arrow_p1, arrow_p2])
        painter.setBrush(QBrush(Qt.blue))
        painter.drawPolygon(arrow)

        # 유량 표시
        if flow_rate > 0:
            mid_point = QPoint((start.x() + end.x()) // 2, (start.y() + end.y()) // 2)
            painter.setPen(QPen(Qt.red))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(mid_point, f"{flow_rate:.1f}")

    def highlight_component(self, painter, component):
        """선택된 컴포넌트 하이라이트"""
        rect = component.get_rect()
        painter.setPen(QPen(Qt.red, 3, Qt.DashLine))
        painter.setBrush(QBrush())  # 투명
        painter.drawRect(rect.adjusted(-5, -5, 5, 5))

    def mousePressEvent(self, event):
        """마우스 클릭 이벤트"""
        click_pos = event.position().toPoint()

        # 클릭된 컴포넌트 찾기
        for component in self.components.values():
            if component.get_rect().contains(click_pos):
                self.selected_component = component
                self.component_clicked.emit(component.component_id)
                self.update()
                break
        else:
            self.selected_component = None
            self.update()

    def update_component_status(self, component_id, status, **kwargs):
        """컴포넌트 상태 업데이트"""
        if component_id in self.components:
            component = self.components[component_id]
            component.status = status

            # 추가 속성 업데이트
            for key, value in kwargs.items():
                if hasattr(component, key):
                    setattr(component, key, value)

            self.component_status_changed.emit(component_id, status)
            self.update()

    def start_simulation(self):
        """시뮬레이션 애니메이션 시작"""
        if not self.animation_timer:
            from PySide6.QtCore import QTimer
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self.animate_flow)
            self.animation_timer.start(100)  # 100ms 간격

    def stop_simulation(self):
        """시뮬레이션 애니메이션 중지"""
        if self.animation_timer:
            self.animation_timer.stop()

    def animate_flow(self):
        """플로우 애니메이션"""
        self.animation_phase += 0.1

        # 펌프 회전 애니메이션
        for component in self.components.values():
            if isinstance(component, Pump) and component.is_running:
                component.pump_speed = self.animation_phase

        self.update()

class ProcessControlPanel(QWidget):
    """프로세스 제어 패널"""

    def __init__(self, flow_diagram, parent=None):
        super().__init__(parent)
        self.flow_diagram = flow_diagram
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)

        # 제어 버튼들
        control_layout = QHBoxLayout()

        self.start_button = QPushButton("프로세스 시작")
        self.stop_button = QPushButton("프로세스 중지")
        self.emergency_button = QPushButton("비상 정지")
        self.emergency_button.setStyleSheet("background-color: red; color: white;")

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.emergency_button)

        layout.addLayout(control_layout)

        # 상태 정보
        self.status_label = QLabel("시스템 대기 중")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.status_label)

        # 개별 컴포넌트 제어
        component_layout = QHBoxLayout()

        # 가스 밸브 제어
        gas_control = QVBoxLayout()
        gas_control.addWidget(QLabel("가스 제어"))

        self.gas_buttons = {}
        for gas_name in ["N2", "Ar", "SiH4", "NH3"]:
            button = QPushButton(f"{gas_name} ON/OFF")
            button.setCheckable(True)
            self.gas_buttons[gas_name] = button
            gas_control.addWidget(button)

        component_layout.addLayout(gas_control)

        # 펌프 제어
        pump_control = QVBoxLayout()
        pump_control.addWidget(QLabel("펌프 제어"))

        self.pump_buttons = {}
        for pump_name in ["Roughing Pump", "Turbo Pump", "Dry Pump"]:
            button = QPushButton(f"{pump_name} ON/OFF")
            button.setCheckable(True)
            self.pump_buttons[pump_name] = button
            pump_control.addWidget(button)

        component_layout.addLayout(pump_control)

        layout.addLayout(component_layout)

    def setup_connections(self):
        """시그널 연결"""
        self.start_button.clicked.connect(self.start_process)
        self.stop_button.clicked.connect(self.stop_process)
        self.emergency_button.clicked.connect(self.emergency_stop)

        # 가스 밸브 제어
        for gas_name, button in self.gas_buttons.items():
            button.toggled.connect(lambda checked, name=gas_name: self.toggle_gas(name, checked))

        # 펌프 제어
        for pump_name, button in self.pump_buttons.items():
            button.toggled.connect(lambda checked, name=pump_name: self.toggle_pump(name, checked))

        # 플로우 다이어그램 연결
        self.flow_diagram.component_clicked.connect(self.on_component_clicked)

    def start_process(self):
        """프로세스 시작"""
        self.status_label.setText("프로세스 실행 중")
        self.flow_diagram.start_simulation()

        # 챔버 상태 변경
        self.flow_diagram.update_component_status(
            "main_chamber",
            ProcessStage.PROCESS,
            temperature=350.0,
            pressure=5.0
        )

    def stop_process(self):
        """프로세스 중지"""
        self.status_label.setText("프로세스 중지됨")
        self.flow_diagram.stop_simulation()

        # 모든 컴포넌트 idle 상태로
        for comp_id in self.flow_diagram.components:
            self.flow_diagram.update_component_status(comp_id, ProcessStage.IDLE)

    def emergency_stop(self):
        """비상 정지"""
        self.status_label.setText("비상 정지 - 안전 점검 필요")
        self.flow_diagram.stop_simulation()

        # 모든 컴포넌트 에러 상태로
        for comp_id in self.flow_diagram.components:
            self.flow_diagram.update_component_status(comp_id, ProcessStage.ERROR)

    def toggle_gas(self, gas_name, checked):
        """가스 밸브 토글"""
        component_id = f"gas_{gas_name.lower()}"
        if component_id in self.flow_diagram.components:
            self.flow_diagram.update_component_status(
                component_id,
                ProcessStage.PROCESS if checked else ProcessStage.IDLE,
                valve_open=checked,
                flow_rate=100.0 if checked else 0.0
            )

    def toggle_pump(self, pump_name, checked):
        """펌프 토글"""
        component_id = f"pump_{pump_name.lower().replace(' ', '_')}"
        if component_id in self.flow_diagram.components:
            self.flow_diagram.update_component_status(
                component_id,
                ProcessStage.PROCESS if checked else ProcessStage.IDLE,
                is_running=checked,
                pump_speed=1000.0 if checked else 0.0
            )

    def on_component_clicked(self, component_id):
        """컴포넌트 클릭 처리"""
        component = self.flow_diagram.components.get(component_id)
        if component:
            self.status_label.setText(f"선택됨: {component.name} ({component_id})")

# 메인 애플리케이션
class ProcessMonitorApp(QMainWindow):
    """프로세스 모니터링 애플리케이션"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("반도체 프로세스 플로우 모니터링")
        self.setGeometry(100, 100, 1200, 800)

        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 레이아웃
        layout = QHBoxLayout(central_widget)

        # 플로우 다이어그램
        self.flow_diagram = ProcessFlowDiagram()
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.flow_diagram)
        scroll_area.setWidgetResizable(True)

        # 제어 패널
        self.control_panel = ProcessControlPanel(self.flow_diagram)
        self.control_panel.setMaximumWidth(300)

        layout.addWidget(scroll_area, 3)
        layout.addWidget(self.control_panel, 1)

# 메인 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ProcessMonitorApp()
    window.show()

    sys.exit(app.exec())
```

</div>

#### **2.2 고급 차트 위젯**

##### **2.2.1 실시간 트렌드 차트**

<div class="chart-widget">

```python
#!/usr/bin/env python3
