# Week 8: Python PySide6 고급 기능 및 커스텀 UI 컴포넌트

## 🎯 **학습 목표**
- **커스텀 위젯**: 전문적인 반도체 HMI를 위한 고급 UI 컴포넌트 개발
- **3D 시각화**: OpenGL 기반 실시간 3D 렌더링 및 장비 모델링
- **고급 아키텍처**: Model-View 패턴 고도화 및 플러그인 시스템 구축
- **UI/UX 최적화**: 현대적 스타일링 및 국제화 지원

---

## 커스텀 위젯 개발

### 🎨 커스텀 위젯의 필요성
- **표준 위젯 한계**: 산업용 HMI 요구사항에 부족한 기본 컴포넌트
- **브랜딩 일관성**: 회사/제품 고유의 디자인 언어 구현
- **특수 기능**: 반도체 장비 특화 인터페이스 요소
- **성능 최적화**: 특정 용도에 최적화된 렌더링

### 🏗️ 위젯 개발 패턴
1. **Composition Pattern**: 기존 위젯 조합
2. **Inheritance Pattern**: QWidget 직접 상속
3. **Custom Painting**: QPainter 활용 완전 커스텀
4. **Hybrid Approach**: 혼합 방식

---

## QPainter 기반 산업용 게이지

### 핵심 구현 예제

```python
class IndustrialGauge(QWidget):
    """산업용 계기판 위젯"""

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 배경, 눈금, 바늘 순서로 그리기
        self.draw_background(painter)
        self.draw_scale(painter)
        self.draw_needle(painter)
```

### 주요 기능
- **실시간 데이터 반영**: 센서값에 따른 바늘 위치 변경
- **임계값 표시**: 경고/위험 영역 색상 구분
- **부드러운 애니메이션**: QPropertyAnimation 활용

---

## 3D 시각화 및 OpenGL 통합
        if self.value >= self.critical_threshold:
            needle_color = self.colors['critical']
        elif self.value >= self.warning_threshold:
            needle_color = self.colors['warning']
        else:
            needle_color = self.colors['normal']

        painter.setPen(QPen(needle_color, 4))

        # 바늘 그리기
        needle_length = radius - 30
        needle_x = center.x() + needle_length * math.cos(math.radians(current_angle))
        needle_y = center.y() + needle_length * math.sin(math.radians(current_angle))

        painter.drawLine(center, QPoint(int(needle_x), int(needle_y)))

        # 중심점 그리기
        painter.setBrush(QBrush(needle_color))
        painter.drawEllipse(center, 8, 8)

        painter.restore()

    def draw_text(self, painter, rect):
        """텍스트 그리기"""
        painter.setPen(QPen(Qt.white))
        painter.setFont(painter.font())

        # 현재 값 표시
        text_rect = QRect(rect.x(), rect.bottom() - 40, rect.width(), 30)
        painter.drawText(text_rect, Qt.AlignCenter, f"{self.value:.1f}")

        # 단위 표시
        unit_rect = QRect(rect.x(), rect.bottom() - 20, rect.width(), 20)
        painter.drawText(unit_rect, Qt.AlignCenter, "°C")

    def setValue(self, value):
        """값 설정"""
        self.value = max(self.min_value, min(self.max_value, value))
        self.update()

    def setRange(self, min_val, max_val):
        """범위 설정"""
        self.min_value = min_val
        self.max_value = max_val
        self.update()

    def setThresholds(self, warning, critical):
        """임계값 설정"""
        self.warning_threshold = warning
        self.critical_threshold = critical
        self.update()
```

##### **1.1.2 상태 인디케이터 위젯**

<div class="code-block">

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QPainter, QBrush, QPen, QFont
from PySide6.QtCore import Qt, QRect, QTimer, Signal
from enum import Enum

class EquipmentStatus(Enum):
    """장비 상태 열거형"""
    OFFLINE = "offline"
    IDLE = "idle"
    RUNNING = "running"
    WARNING = "warning"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class StatusIndicator(QWidget):
    """상태 인디케이터 위젯"""

    status_changed = Signal(EquipmentStatus)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 60)

        self.status = EquipmentStatus.OFFLINE
        self.is_blinking = False
        self.blink_state = True

        # 상태별 색상 매핑
        self.status_colors = {
            EquipmentStatus.OFFLINE: Qt.gray,
            EquipmentStatus.IDLE: Qt.blue,
            EquipmentStatus.RUNNING: Qt.green,
            EquipmentStatus.WARNING: Qt.yellow,
            EquipmentStatus.ERROR: Qt.red,
            EquipmentStatus.MAINTENANCE: Qt.magenta
        }

        # 깜빡임 타이머
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_blink)

        # 상태별 깜빡임 설정
        self.blinking_statuses = {EquipmentStatus.WARNING, EquipmentStatus.ERROR}

    def paintEvent(self, event):
        """커스텀 페인팅"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        # 배경 그리기
        painter.setPen(QPen(Qt.darkGray, 2))
        painter.setBrush(QBrush(Qt.black))
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 8, 8)

        # 상태 LED 그리기
        led_rect = QRect(10, 10, 30, 30)
        self.draw_led(painter, led_rect)

        # 텍스트 그리기
        text_rect = QRect(50, 10, 60, 40)
        self.draw_status_text(painter, text_rect)

    def draw_led(self, painter, rect):
        """LED 그리기"""
        color = self.status_colors[self.status]

        # 깜빡임 처리
        if self.is_blinking and not self.blink_state:
            color = Qt.darkGray

        # LED 외곽
        painter.setPen(QPen(Qt.white, 1))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(rect)

        # LED 하이라이트
        highlight_rect = QRect(rect.x() + 3, rect.y() + 3, 8, 8)
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(highlight_rect)

    def draw_status_text(self, painter, rect):
        """상태 텍스트 그리기"""
        painter.setPen(QPen(Qt.white))
        painter.setFont(QFont("Arial", 9, QFont.Bold))

        status_text = self.status.value.upper()
        painter.drawText(rect, Qt.AlignCenter, status_text)

    def set_status(self, status: EquipmentStatus):
        """상태 설정"""
        if self.status != status:
            self.status = status

            # 깜빡임 제어
            if status in self.blinking_statuses:
                self.start_blinking()
            else:
                self.stop_blinking()

            self.status_changed.emit(status)
            self.update()

    def start_blinking(self):
        """깜빡임 시작"""
        self.is_blinking = True
        self.blink_timer.start(500)  # 500ms 간격

    def stop_blinking(self):
        """깜빡임 중지"""
        self.is_blinking = False
        self.blink_timer.stop()
        self.blink_state = True
        self.update()

    def toggle_blink(self):
        """깜빡임 토글"""
        self.blink_state = not self.blink_state
        self.update()

class EquipmentPanel(QWidget):
    """장비 패널 위젯"""

    def __init__(self, equipment_name, parent=None):
        super().__init__(parent)
        self.equipment_name = equipment_name
        self.setup_ui()

    def setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)

        # 제목
        title_label = QLabel(self.equipment_name)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 상태 인디케이터들
        indicators_layout = QHBoxLayout()

        self.power_indicator = StatusIndicator()
        self.process_indicator = StatusIndicator()
        self.alarm_indicator = StatusIndicator()

        indicators_layout.addWidget(self.create_labeled_indicator("전원", self.power_indicator))
        indicators_layout.addWidget(self.create_labeled_indicator("프로세스", self.process_indicator))
        indicators_layout.addWidget(self.create_labeled_indicator("알람", self.alarm_indicator))

        layout.addLayout(indicators_layout)

        # 초기 상태 설정
        self.power_indicator.set_status(EquipmentStatus.IDLE)
        self.process_indicator.set_status(EquipmentStatus.OFFLINE)
        self.alarm_indicator.set_status(EquipmentStatus.OFFLINE)

    def create_labeled_indicator(self, label_text, indicator):
        """라벨이 있는 인디케이터 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 8))

        layout.addWidget(label)
        layout.addWidget(indicator)

        return widget

    def update_equipment_status(self, power_on, process_running, has_alarm):
        """장비 상태 업데이트"""
        # 전원 상태
        if power_on:
            self.power_indicator.set_status(EquipmentStatus.RUNNING)
        else:
            self.power_indicator.set_status(EquipmentStatus.OFFLINE)

        # 프로세스 상태
        if power_on and process_running:
            self.process_indicator.set_status(EquipmentStatus.RUNNING)
        elif power_on:
            self.process_indicator.set_status(EquipmentStatus.IDLE)
        else:
            self.process_indicator.set_status(EquipmentStatus.OFFLINE)

        # 알람 상태
        if has_alarm:
            self.alarm_indicator.set_status(EquipmentStatus.ERROR)
        else:
            self.alarm_indicator.set_status(EquipmentStatus.OFFLINE)
```

</div>

#### **1.2 Model-View 아키텍처 고도화**

##### **1.2.1 고성능 데이터 모델**

<div class="architecture-section">

**🏗️ 대용량 데이터 처리를 위한 Model-View 최적화**:

```python
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant, Signal
from PySide6.QtGui import QColor, QFont
from datetime import datetime
import numpy as np
from typing import List, Any, Optional

class HighPerformanceDataModel(QAbstractTableModel):
    """고성능 데이터 테이블 모델"""

    data_changed_signal = Signal(int, int)  # row, column

    def __init__(self, parent=None):
        super().__init__(parent)

        # 데이터 저장소 (NumPy 배열 사용으로 성능 최적화)
        self.data_buffer = np.empty((0, 8), dtype=object)  # 초기 빈 배열
        self.max_rows = 10000  # 최대 행 수
        self.current_row_count = 0

        # 헤더 정의
        self.headers = [
            "Timestamp", "Temperature", "Pressure", "Flow Rate",
            "RF Power", "Recipe Step", "Status", "Alarms"
        ]

        # 컬럼별 데이터 타입
        self.column_types = [
            datetime, float, float, float, float, int, str, str
        ]

        # 시각적 포맷팅을 위한 설정
        self.warning_thresholds = {
            1: (300, 400),  # Temperature
            2: (1.0, 10.0), # Pressure
            3: (50, 200),   # Flow Rate
            4: (200, 500)   # RF Power
        }

    def rowCount(self, parent=QModelIndex()):
        """행 수 반환"""
        return self.current_row_count

    def columnCount(self, parent=QModelIndex()):
        """열 수 반환"""
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        """데이터 반환"""
        if not index.isValid():
            return QVariant()

        row = index.row()
        col = index.column()

        if row >= self.current_row_count or col >= len(self.headers):
            return QVariant()

        value = self.data_buffer[row, col]

        if role == Qt.DisplayRole:
            return self.format_display_value(value, col)
        elif role == Qt.BackgroundRole:
            return self.get_background_color(value, col)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter if col > 0 else Qt.AlignLeft
        elif role == Qt.FontRole:
            if col == 6:  # Status column
                font = QFont()
                font.setBold(True)
                return font

        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """헤더 데이터 반환"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(section + 1)

        return QVariant()

    def format_display_value(self, value, column):
        """표시값 포맷팅"""
        if value is None:
            return ""

        if column == 0:  # Timestamp
            if isinstance(value, datetime):
                return value.strftime("%H:%M:%S.%f")[:-3]
        elif column in [1, 2, 3, 4]:  # Numeric columns
            if isinstance(value, (int, float)):
                if column == 1:  # Temperature
                    return f"{value:.1f}°C"
                elif column == 2:  # Pressure
                    return f"{value:.2f}Torr"
                elif column == 3:  # Flow Rate
                    return f"{value:.1f}sccm"
                elif column == 4:  # RF Power
                    return f"{value:.0f}W"
        elif column == 5:  # Recipe Step
            return f"Step {value}" if value else "N/A"

        return str(value)

    def get_background_color(self, value, column):
        """배경색 결정"""
        if column in self.warning_thresholds and isinstance(value, (int, float)):
            min_val, max_val = self.warning_thresholds[column]

            if value < min_val or value > max_val:
                return QColor(255, 200, 200)  # 연한 빨강
            elif abs(value - min_val) < (max_val - min_val) * 0.1 or \
                 abs(value - max_val) < (max_val - min_val) * 0.1:
                return QColor(255, 255, 200)  # 연한 노랑

        return QVariant()

    def add_data_point(self, data_point: dict):
        """데이터 포인트 추가 (최적화된 배치 삽입)"""
        # 배열 크기 확장 필요 시
        if self.current_row_count >= self.data_buffer.shape[0]:
            self.expand_buffer()

        # 최대 행 수 제한
        if self.current_row_count >= self.max_rows:
            self.remove_oldest_rows(1000)  # 1000개 행 제거

        # 데이터 변환 및 삽입
        row_data = [
            data_point.get('timestamp', datetime.now()),
            data_point.get('chamber_temperature', 0.0),
            data_point.get('chamber_pressure', 0.0),
            data_point.get('gas_flow_rate', 0.0),
            data_point.get('rf_power', 0.0),
            data_point.get('recipe_step', 0),
            data_point.get('status', 'Unknown'),
            data_point.get('alarms', '')
        ]

        # 행 삽입 시작
        self.beginInsertRows(QModelIndex(), self.current_row_count, self.current_row_count)

        # 데이터 저장
        self.data_buffer[self.current_row_count] = row_data
        self.current_row_count += 1

        # 행 삽입 완료
        self.endInsertRows()

        # 시그널 발송
        self.data_changed_signal.emit(self.current_row_count - 1, -1)

    def add_data_batch(self, data_points: List[dict]):
        """배치 데이터 추가 (성능 최적화)"""
        if not data_points:
            return

        batch_size = len(data_points)

        # 필요한 공간 확보
        while self.current_row_count + batch_size > self.data_buffer.shape[0]:
            self.expand_buffer()

        # 최대 행 수 제한
        if self.current_row_count + batch_size > self.max_rows:
            remove_count = (self.current_row_count + batch_size) - self.max_rows + 1000
            self.remove_oldest_rows(remove_count)

        # 배치 삽입 시작
        start_row = self.current_row_count
        end_row = start_row + batch_size - 1

        self.beginInsertRows(QModelIndex(), start_row, end_row)

        # 배치 데이터 변환 및 저장
        for i, data_point in enumerate(data_points):
            row_data = [
                data_point.get('timestamp', datetime.now()),
                data_point.get('chamber_temperature', 0.0),
                data_point.get('chamber_pressure', 0.0),
                data_point.get('gas_flow_rate', 0.0),
                data_point.get('rf_power', 0.0),
                data_point.get('recipe_step', 0),
                data_point.get('status', 'Unknown'),
                data_point.get('alarms', '')
            ]
            self.data_buffer[self.current_row_count + i] = row_data

        self.current_row_count += batch_size

        # 배치 삽입 완료
        self.endInsertRows()

    def expand_buffer(self):
        """버퍼 크기 확장"""
        current_size = self.data_buffer.shape[0]
        new_size = max(1000, current_size * 2)  # 최소 1000, 또는 2배로 확장

        new_buffer = np.empty((new_size, self.data_buffer.shape[1]), dtype=object)
        new_buffer[:current_size] = self.data_buffer
        self.data_buffer = new_buffer

    def remove_oldest_rows(self, count):
        """오래된 행 제거"""
        if count >= self.current_row_count:
            self.clear_data()
            return

        # 행 제거 시작
        self.beginRemoveRows(QModelIndex(), 0, count - 1)

        # 데이터 이동
        remaining_count = self.current_row_count - count
        self.data_buffer[:remaining_count] = self.data_buffer[count:self.current_row_count]
        self.current_row_count = remaining_count

        # 행 제거 완료
        self.endRemoveRows()

    def clear_data(self):
        """모든 데이터 클리어"""
        if self.current_row_count == 0:
            return

        self.beginRemoveRows(QModelIndex(), 0, self.current_row_count - 1)
        self.current_row_count = 0
        self.endRemoveRows()

    def get_data_range(self, start_row, end_row):
        """데이터 범위 반환"""
        if start_row < 0 or end_row >= self.current_row_count:
            return []

        return self.data_buffer[start_row:end_row + 1].tolist()

    def export_to_dict_list(self):
        """딕셔너리 리스트로 내보내기"""
        result = []
        for row in range(self.current_row_count):
            row_dict = {}
            for col, header in enumerate(self.headers):
                row_dict[header] = self.data_buffer[row, col]
            result.append(row_dict)
        return result
```

</div>

#### **1.3 3D 시각화 및 그래픽스**

##### **1.3.1 OpenGL 기반 3D 렌더링**

<div class="graphics-section">

**🎮 3D 시각화의 장점**:
- **직관적 표현**: 복잡한 장비 구조의 3차원적 이해
- **실시간 모니터링**: 장비 상태의 시각적 피드백
- **공간적 관계**: 센서 위치 및 프로세스 흐름 표현
- **몰입감**: 사용자 경험 향상

```python
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtOpenGL import QOpenGLShaderProgram, QOpenGLBuffer
from PySide6.QtGui import QMatrix4x4, QVector3D, QQuaternion
from PySide6.QtCore import QTimer, Signal
import numpy as np
from OpenGL.GL import *
import math

class Equipment3DView(QOpenGLWidget):
    """3D 장비 시각화 위젯"""

    equipment_clicked = Signal(str)  # 장비 부품 클릭 시그널

    def __init__(self, parent=None):
        super().__init__(parent)

        # 3D 속성
        self.rotation_x = 15.0
        self.rotation_y = 45.0
        self.zoom = 1.0

        # 마우스 상호작용
        self.last_mouse_pos = None
        self.mouse_buttons = 0

        # 3D 모델 데이터
        self.equipment_models = {}
        self.load_equipment_models()

        # 애니메이션 타이머
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate)
        self.animation_timer.start(16)  # 60 FPS

        # 센서 데이터 시각화
        self.sensor_data = {}
        self.temperature_color_map = {
            'cold': (0.0, 0.0, 1.0),   # 파랑
            'normal': (0.0, 1.0, 0.0), # 녹색
            'hot': (1.0, 1.0, 0.0),    # 노랑
            'critical': (1.0, 0.0, 0.0) # 빨강
        }

    def initializeGL(self):
        """OpenGL 초기화"""
        # 깊이 테스트 활성화
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        # 뒷면 제거
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        # 조명 설정
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        # 조명 속성 설정
        light_position = [2.0, 2.0, 2.0, 1.0]
        light_ambient = [0.2, 0.2, 0.2, 1.0]
        light_diffuse = [0.8, 0.8, 0.8, 1.0]
        light_specular = [1.0, 1.0, 1.0, 1.0]

        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

        # 배경색 설정
        glClearColor(0.1, 0.1, 0.2, 1.0)

    def resizeGL(self, width, height):
        """뷰포트 크기 변경"""
        glViewport(0, 0, width, height)

        # 투영 행렬 설정
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect_ratio = width / height if height != 0 else 1
        fov = 45.0
        near_plane = 0.1
        far_plane = 100.0

        # 원근 투영
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        glFrustum(-aspect_ratio / f, aspect_ratio / f, -1.0 / f, 1.0 / f, near_plane, far_plane)

    def paintGL(self):
        """3D 렌더링"""
        # 화면 클리어
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 모델뷰 행렬 설정
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # 카메라 위치 설정
        glTranslatef(0.0, 0.0, -5.0 * self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        # 3D 모델 렌더링
        self.render_equipment()

        # 센서 데이터 시각화
        self.render_sensors()

        # 좌표축 표시
        self.render_axes()

    def render_equipment(self):
        """장비 모델 렌더링"""
        # 챔버 렌더링
        self.render_chamber()

        # 가스 라인 렌더링
        self.render_gas_lines()

        # 센서 위치 렌더링
        self.render_sensor_positions()

    def render_chamber(self):
        """반응 챔버 렌더링"""
        glPushMatrix()

        # 재질 속성 설정
        material_ambient = [0.2, 0.2, 0.3, 1.0]
        material_diffuse = [0.3, 0.3, 0.5, 1.0]
        material_specular = [0.8, 0.8, 0.8, 1.0]
        material_shininess = [50.0]

        glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

        # 원통형 챔버 (쿼드릭 사용)
        from OpenGL.GLU import gluNewQuadric, gluCylinder, gluSphere

        quadric = gluNewQuadric()

        # 외벽
        glColor3f(0.7, 0.7, 0.8)
        gluCylinder(quadric, 1.5, 1.5, 2.0, 32, 16)

        # 상단
        glPushMatrix()
        glTranslatef(0.0, 0.0, 2.0)
        gluSphere(quadric, 1.5, 32, 16)
        glPopMatrix()

        # 하단
        gluSphere(quadric, 1.5, 32, 16)

        glPopMatrix()

    def render_gas_lines(self):
        """가스 라인 렌더링"""
        glPushMatrix()

        # 가스 입구 파이프들
        gas_inlets = [
            (2.0, 0.0, 1.0),   # 가스 1
            (1.4, 1.4, 1.0),   # 가스 2
            (0.0, 2.0, 1.0),   # 가스 3
            (-1.4, 1.4, 1.0),  # 가스 4
        ]

        glColor3f(0.8, 0.8, 0.9)
        for x, y, z in gas_inlets:
            glPushMatrix()
            glTranslatef(x, y, z)

            # 파이프 렌더링 (간단한 원통)
            from OpenGL.GLU import gluNewQuadric, gluCylinder
            quadric = gluNewQuadric()
            glRotatef(90, 0, 1, 0)
            gluCylinder(quadric, 0.1, 0.1, 0.5, 8, 4)

            glPopMatrix()

        glPopMatrix()

    def render_sensor_positions(self):
        """센서 위치 렌더링"""
        glPushMatrix()

        # 온도 센서들
        temp_sensors = [
            ('T1', 1.3, 0.0, 0.5),
            ('T2', 0.0, 1.3, 1.0),
            ('T3', -1.3, 0.0, 1.5),
            ('T4', 0.0, -1.3, 1.0),
        ]

        for sensor_id, x, y, z in temp_sensors:
            glPushMatrix()
            glTranslatef(x, y, z)

            # 센서 데이터에 따른 색상 결정
            temp_value = self.sensor_data.get(sensor_id, 25.0)
            color = self.get_temperature_color(temp_value)
            glColor3f(*color)

            # 센서 표시 (작은 구)
            from OpenGL.GLU import gluNewQuadric, gluSphere
            quadric = gluNewQuadric()
            gluSphere(quadric, 0.1, 16, 8)

            glPopMatrix()

        glPopMatrix()

    def render_sensors(self):
        """센서 데이터 시각화"""
        # 온도 분포 시각화 (열화상 효과)
        self.render_temperature_distribution()

        # 압력 게이지 3D 표시
        self.render_pressure_indicators()

    def render_temperature_distribution(self):
        """온도 분포 시각화"""
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # 반투명 온도 층 렌더링
        for i in range(10):
            height = i * 0.2
            alpha = 0.1

            # 현재 높이에서의 평균 온도 계산
            avg_temp = self.calculate_average_temperature_at_height(height)
            color = self.get_temperature_color(avg_temp)

            glColor4f(color[0], color[1], color[2], alpha)

            # 원형 온도 분포 렌더링
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0.0, 0.0, height)

            for angle in range(0, 361, 10):
                rad = math.radians(angle)
                x = 1.4 * math.cos(rad)
                y = 1.4 * math.sin(rad)
                glVertex3f(x, y, height)

            glEnd()

        glDisable(GL_BLEND)
        glPopMatrix()

    def render_pressure_indicators(self):
        """압력 인디케이터 렌더링"""
        glPushMatrix()

        # 압력 값에 따른 3D 바 그래프
        pressure_value = self.sensor_data.get('pressure', 5.0)
        bar_height = pressure_value / 10.0  # 정규화

        glTranslatef(2.5, 0.0, 0.0)
        glColor3f(0.0, 0.8, 1.0)

        # 압력 바 렌더링
        glBegin(GL_QUADS)
        # 앞면
        glVertex3f(-0.1, -0.1, 0.0)
        glVertex3f(0.1, -0.1, 0.0)
        glVertex3f(0.1, 0.1, 0.0)
        glVertex3f(-0.1, 0.1, 0.0)

        # 윗면
        glVertex3f(-0.1, -0.1, bar_height)
        glVertex3f(0.1, -0.1, bar_height)
        glVertex3f(0.1, 0.1, bar_height)
        glVertex3f(-0.1, 0.1, bar_height)
        glEnd()

        glPopMatrix()

    def render_axes(self):
        """좌표축 렌더링"""
        glPushMatrix()
        glDisable(GL_LIGHTING)

        glLineWidth(3.0)
        glBegin(GL_LINES)

        # X축 (빨강)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(1.0, 0.0, 0.0)

        # Y축 (녹색)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 1.0, 0.0)

        # Z축 (파랑)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 1.0)

        glEnd()
        glLineWidth(1.0)

        glEnable(GL_LIGHTING)
        glPopMatrix()

    def get_temperature_color(self, temperature):
        """온도에 따른 색상 반환"""
        if temperature < 100:
            return self.temperature_color_map['cold']
        elif temperature < 200:
            return self.temperature_color_map['normal']
        elif temperature < 300:
            return self.temperature_color_map['hot']
        else:
            return self.temperature_color_map['critical']

    def calculate_average_temperature_at_height(self, height):
        """특정 높이에서의 평균 온도 계산"""
        # 실제로는 센서 데이터를 기반으로 보간 계산
        base_temp = 25.0
        height_factor = height * 50  # 높이에 따른 온도 증가
        return base_temp + height_factor

    def update_sensor_data(self, sensor_data):
        """센서 데이터 업데이트"""
        self.sensor_data.update(sensor_data)
        self.update()

    def mousePressEvent(self, event):
        """마우스 클릭 이벤트"""
        self.last_mouse_pos = event.position()
        self.mouse_buttons = event.buttons()

    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트"""
        if self.last_mouse_pos is None:
            return

        dx = event.position().x() - self.last_mouse_pos.x()
        dy = event.position().y() - self.last_mouse_pos.y()

        if self.mouse_buttons & Qt.LeftButton:
            # 회전
            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5

            # 회전 제한
            self.rotation_x = max(-90, min(90, self.rotation_x))

            self.update()

        self.last_mouse_pos = event.position()

    def wheelEvent(self, event):
        """마우스 휠 이벤트 (줌)"""
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9

        self.zoom *= zoom_factor
        self.zoom = max(0.1, min(5.0, self.zoom))

        self.update()

    def animate(self):
        """애니메이션 업데이트"""
        # 시간에 따른 자동 회전 (옵션)
        # self.rotation_y += 0.5
        self.update()

    def load_equipment_models(self):
        """장비 모델 로드"""
        # 실제로는 3D 모델 파일(.obj, .stl 등)을 로드
        # 여기서는 기본 형태로 구현
        pass

---

## 2️⃣ 기초 실습
### 🛠️ **커스텀 위젯 및 고급 UI 컴포넌트 개발**

#### **2.1 플로우 다이어그램 위젯**

<div class="practice-section">

```python
#!/usr/bin/env python3
