# -*- coding: utf-8 -*-

import sys
import math
import time
from datetime import datetime, timedelta
from collections import deque
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPainter, QPen, QBrush, QFont, QColor, QLinearGradient
from PySide6.QtCore import Qt, QRect, QPoint, QTimer, Signal
import random

class AdvancedTrendChart(QWidget):
    """고급 트렌드 차트 위젯"""

    point_hovered = Signal(str, float, datetime)
    threshold_exceeded = Signal(str, float, float)

    def __init__(self, title="Trend Chart", parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)

        # 차트 속성
        self.title = title
        self.data_series = {}  # {series_name: {'data': deque, 'color': QColor, 'visible': bool}}
        self.time_range = timedelta(minutes=10)  # 10분 범위
        self.max_points = 1000

        # 축 설정
        self.y_min = 0
        self.y_max = 100
        self.auto_scale = True
        self.grid_enabled = True

        # 임계값 설정
        self.thresholds = {}  # {series_name: {'warning': float, 'critical': float}}

        # 마우스 상호작용
        self.mouse_pos = QPoint()
        self.show_crosshair = True
        self.show_values = True

        # 확대/축소
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)

        # 색상 팔레트
        self.default_colors = [
            QColor(255, 0, 0),    # 빨강
            QColor(0, 255, 0),    # 녹색
            QColor(0, 0, 255),    # 파랑
            QColor(255, 165, 0),  # 주황
            QColor(128, 0, 128),  # 보라
            QColor(255, 192, 203), # 분홍
            QColor(0, 255, 255),  # 시안
            QColor(255, 255, 0),  # 노랑
        ]
        self.color_index = 0

    def add_series(self, series_name, color=None, warning_threshold=None, critical_threshold=None):
        """데이터 시리즈 추가"""
        if color is None:
            color = self.default_colors[self.color_index % len(self.default_colors)]
            self.color_index += 1

        self.data_series[series_name] = {
            'data': deque(maxlen=self.max_points),
            'color': color,
            'visible': True
        }

        if warning_threshold is not None or critical_threshold is not None:
            self.thresholds[series_name] = {
                'warning': warning_threshold,
                'critical': critical_threshold
            }

    def add_data_point(self, series_name, value, timestamp=None):
        """데이터 포인트 추가"""
        if series_name not in self.data_series:
            self.add_series(series_name)

        if timestamp is None:
            timestamp = datetime.now()

        # 데이터 추가
        self.data_series[series_name]['data'].append((timestamp, value))

        # 자동 스케일링
        if self.auto_scale:
            self.update_y_range()

        # 임계값 체크
        self.check_thresholds(series_name, value)

        self.update()

    def update_y_range(self):
        """Y축 범위 자동 업데이트"""
        all_values = []

        for series_data in self.data_series.values():
            for timestamp, value in series_data['data']:
                all_values.append(value)

        if all_values:
            min_val = min(all_values)
            max_val = max(all_values)

            # 여백 추가 (10%)
            margin = (max_val - min_val) * 0.1
            self.y_min = min_val - margin
            self.y_max = max_val + margin

    def check_thresholds(self, series_name, value):
        """임계값 체크"""
        if series_name in self.thresholds:
            thresholds = self.thresholds[series_name]

            if thresholds.get('critical') and value > thresholds['critical']:
                self.threshold_exceeded.emit(series_name, value, thresholds['critical'])
            elif thresholds.get('warning') and value > thresholds['warning']:
                self.threshold_exceeded.emit(series_name, value, thresholds['warning'])

    def paintEvent(self, event):
        """페인팅 이벤트"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 배경
        self.draw_background(painter)

        # 차트 영역 계산
        chart_rect = self.get_chart_rect()

        # 그리드
        if self.grid_enabled:
            self.draw_grid(painter, chart_rect)

        # 임계값 라인
        self.draw_threshold_lines(painter, chart_rect)

        # 데이터 시리즈
        self.draw_data_series(painter, chart_rect)

        # 축 라벨
        self.draw_axes(painter, chart_rect)

        # 제목
        self.draw_title(painter)

        # 범례
        self.draw_legend(painter)

        # 크로스헤어
        if self.show_crosshair:
            self.draw_crosshair(painter, chart_rect)

    def draw_background(self, painter):
        """배경 그리기"""
        # 그라디언트 배경
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(250, 250, 250))
        gradient.setColorAt(1.0, QColor(220, 220, 220))

        painter.fillRect(self.rect(), QBrush(gradient))

    def get_chart_rect(self):
        """차트 영역 계산"""
        margin = 60
        return QRect(
            margin,
            margin + 30,  # 제목 공간
            self.width() - 2 * margin - 150,  # 범례 공간
            self.height() - 2 * margin - 30
        )

    def draw_grid(self, painter, chart_rect):
        """그리드 그리기"""
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.DotLine))

        # 수직선 (시간축)
        for i in range(10):
            x = chart_rect.x() + (i * chart_rect.width() / 9)
            painter.drawLine(x, chart_rect.y(), x, chart_rect.bottom())

        # 수평선 (값축)
        for i in range(6):
            y = chart_rect.y() + (i * chart_rect.height() / 5)
            painter.drawLine(chart_rect.x(), y, chart_rect.right(), y)

    def draw_threshold_lines(self, painter, chart_rect):
        """임계값 라인 그리기"""
        for series_name, thresholds in self.thresholds.items():
            # 경고 임계값
            if thresholds.get('warning'):
                y = self.value_to_y(thresholds['warning'], chart_rect)
                painter.setPen(QPen(QColor(255, 165, 0), 2, Qt.DashLine))
                painter.drawLine(chart_rect.x(), y, chart_rect.right(), y)

                # 라벨
                painter.setPen(QPen(QColor(255, 165, 0)))
                painter.drawText(chart_rect.right() + 5, y, f"Warning: {thresholds['warning']}")

            # 위험 임계값
            if thresholds.get('critical'):
                y = self.value_to_y(thresholds['critical'], chart_rect)
                painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.DashLine))
                painter.drawLine(chart_rect.x(), y, chart_rect.right(), y)

                # 라벨
                painter.setPen(QPen(QColor(255, 0, 0)))
                painter.drawText(chart_rect.right() + 5, y, f"Critical: {thresholds['critical']}")

    def draw_data_series(self, painter, chart_rect):
        """데이터 시리즈 그리기"""
        current_time = datetime.now()
        time_start = current_time - self.time_range

        for series_name, series_data in self.data_series.items():
            if not series_data['visible'] or not series_data['data']:
                continue

            # 시간 범위 내 데이터 필터링
            filtered_data = [
                (timestamp, value) for timestamp, value in series_data['data']
                if timestamp >= time_start
            ]

            if len(filtered_data) < 2:
                continue

            # 라인 그리기
            painter.setPen(QPen(series_data['color'], 2))

            points = []
            for timestamp, value in filtered_data:
                x = self.timestamp_to_x(timestamp, chart_rect, current_time)
                y = self.value_to_y(value, chart_rect)
                points.append(QPoint(int(x), int(y)))

            # 연결된 라인 그리기
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])

            # 데이터 포인트 마커
            painter.setBrush(QBrush(series_data['color']))
            for point in points[-10:]:  # 최근 10개만 표시
                painter.drawEllipse(point, 3, 3)

    def timestamp_to_x(self, timestamp, chart_rect, current_time):
        """타임스탬프를 X 좌표로 변환"""
        time_diff = (current_time - timestamp).total_seconds()
        time_range_seconds = self.time_range.total_seconds()

        ratio = 1.0 - (time_diff / time_range_seconds)
        return chart_rect.x() + ratio * chart_rect.width()

    def value_to_y(self, value, chart_rect):
        """값을 Y 좌표로 변환"""
        if self.y_max == self.y_min:
            return chart_rect.center().y()

        ratio = (value - self.y_min) / (self.y_max - self.y_min)
        return chart_rect.bottom() - ratio * chart_rect.height()

    def draw_axes(self, painter, chart_rect):
        """축 라벨 그리기"""
        painter.setPen(QPen(Qt.black))
        painter.setFont(QFont("Arial", 9))

        # Y축 라벨
        for i in range(6):
            y = chart_rect.y() + (i * chart_rect.height() / 5)
            value = self.y_max - (i * (self.y_max - self.y_min) / 5)
            text = f"{value:.1f}"
            painter.drawText(chart_rect.x() - 30, y + 5, text)

        # X축 라벨 (시간)
        current_time = datetime.now()
        for i in range(6):
            x = chart_rect.x() + (i * chart_rect.width() / 5)
            time_offset = timedelta(seconds=(5-i) * self.time_range.total_seconds() / 5)
            timestamp = current_time - time_offset
            text = timestamp.strftime("%H:%M")
            painter.drawText(x - 20, chart_rect.bottom() + 20, text)

    def draw_title(self, painter):
        """제목 그리기"""
        painter.setPen(QPen(Qt.black))
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        title_rect = QRect(0, 10, self.width(), 30)
        painter.drawText(title_rect, Qt.AlignCenter, self.title)

    def draw_legend(self, painter):
        """범례 그리기"""
        legend_x = self.width() - 140
        legend_y = 60

        painter.setPen(QPen(Qt.black))
        painter.setFont(QFont("Arial", 9))

        y_offset = 0
        for series_name, series_data in self.data_series.items():
            if not series_data['visible']:
                continue

            # 색상 박스
            color_rect = QRect(legend_x, legend_y + y_offset, 15, 15)
            painter.fillRect(color_rect, series_data['color'])
            painter.drawRect(color_rect)

            # 시리즈 이름
            painter.drawText(legend_x + 20, legend_y + y_offset + 12, series_name)

            # 현재 값
            if series_data['data']:
                current_value = series_data['data'][-1][1]
                painter.drawText(legend_x + 20, legend_y + y_offset + 25, f"{current_value:.2f}")

            y_offset += 40

    def draw_crosshair(self, painter, chart_rect):
        """크로스헤어 그리기"""
        if not chart_rect.contains(self.mouse_pos):
            return

        painter.setPen(QPen(QColor(100, 100, 100), 1, Qt.DashLine))

        # 수직선
        painter.drawLine(self.mouse_pos.x(), chart_rect.y(),
                        self.mouse_pos.x(), chart_rect.bottom())

        # 수평선
        painter.drawLine(chart_rect.x(), self.mouse_pos.y(),
                        chart_rect.right(), self.mouse_pos.y())

        # 값 표시
        if self.show_values:
            value = self.y_to_value(self.mouse_pos.y(), chart_rect)
            painter.setPen(QPen(Qt.black))
            painter.drawText(self.mouse_pos.x() + 10, self.mouse_pos.y() - 10,
                           f"Value: {value:.2f}")

    def y_to_value(self, y, chart_rect):
        """Y 좌표를 값으로 변환"""
        if chart_rect.height() == 0:
            return 0

        ratio = (chart_rect.bottom() - y) / chart_rect.height()
        return self.y_min + ratio * (self.y_max - self.y_min)

    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트"""
        self.mouse_pos = event.position().toPoint()
        self.update()

    def wheelEvent(self, event):
        """마우스 휠 이벤트 (줌)"""
        delta = event.angleDelta().y()
        zoom_in = delta > 0

        if zoom_in:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1

        self.zoom_factor = max(0.1, min(10.0, self.zoom_factor))
        self.update()

    def set_time_range(self, minutes):
        """시간 범위 설정"""
        self.time_range = timedelta(minutes=minutes)
        self.update()

    def set_y_range(self, y_min, y_max):
        """Y축 범위 설정"""
        self.y_min = y_min
        self.y_max = y_max
        self.auto_scale = False
        self.update()

    def toggle_series_visibility(self, series_name):
        """시리즈 표시/숨김 토글"""
        if series_name in self.data_series:
            self.data_series[series_name]['visible'] = not self.data_series[series_name]['visible']
            self.update()

    def clear_data(self):
        """모든 데이터 클리어"""
        for series_data in self.data_series.values():
            series_data['data'].clear()
        self.update()

    def export_data(self):
        """데이터 내보내기"""
        data = {}
        for series_name, series_data in self.data_series.items():
            data[series_name] = list(series_data['data'])
        return data
```

</div>

---

## 3️⃣ 심화 실습
### ⚡ **3D 시각화 및 플러그인 아키텍처**

#### **3.1 고급 3D 시각화 구현**

##### **3.1.1 인터랙티브 3D 장비 모델**

<div class="advanced-3d">

```python
#!/usr/bin/env python3
