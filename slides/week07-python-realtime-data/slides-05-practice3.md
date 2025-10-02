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

**Phase 1: 기본 통합**
1. **애플리케이션 실행**: 통합 모니터링 시스템 실행 및 기본 기능 확인
2. **데이터 수집**: 실시간 데이터 수집 시작 및 차트 업데이트 확인
3. **데이터베이스 저장**: SQLite 데이터베이스 저장 기능 테스트

**Phase 2: 고급 기능**
1. **성능 최적화**: 수집 간격 조정 및 성능 모니터링
2. **통신 구현**: 시리얼 또는 TCP 통신 기능 추가
3. **알람 시스템**: 임계값 기반 알람 기능 구현

**Phase 3: 커스터마이징**
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
