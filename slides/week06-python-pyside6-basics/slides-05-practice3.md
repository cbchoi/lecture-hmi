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

