# -*- coding: utf-8 -*-

import sys
import math
import numpy as np
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer, Signal, QPoint
from PySide6.QtGui import QMatrix4x4, QVector3D, QQuaternion
from OpenGL.GL import *
from OpenGL.GLU import *
import random

class Interactive3DEquipment(QOpenGLWidget):
    """인터랙티브 3D 장비 시각화"""

    component_selected = Signal(str)
    sensor_data_updated = Signal(str, float)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 카메라 제어
        self.camera_distance = 10.0
        self.camera_rotation_x = 15.0
        self.camera_rotation_y = 45.0

        # 마우스 상호작용
        self.last_mouse_pos = None
        self.mouse_sensitivity = 0.5

        # 3D 모델 구성요소
        self.equipment_components = {
            'chamber': {
                'position': [0.0, 0.0, 0.0],
                'rotation': [0.0, 0.0, 0.0],
                'scale': [1.0, 1.0, 1.0],
                'color': [0.7, 0.7, 0.8, 1.0],
                'selected': False,
                'temperature': 25.0
            },
            'gas_inlet_1': {
                'position': [2.0, 0.0, 1.0],
                'rotation': [0.0, 0.0, 90.0],
                'scale': [0.3, 0.3, 1.0],
                'color': [0.2, 0.8, 0.2, 1.0],
                'selected': False,
                'flow_rate': 0.0
            },
            'gas_inlet_2': {
                'position': [0.0, 2.0, 1.0],
                'rotation': [0.0, 0.0, 0.0],
                'scale': [0.3, 0.3, 1.0],
                'color': [0.2, 0.2, 0.8, 1.0],
                'selected': False,
                'flow_rate': 0.0
            },
            'exhaust_port': {
                'position': [0.0, 0.0, -2.0],
                'rotation': [0.0, 0.0, 0.0],
                'scale': [0.5, 0.5, 0.8],
                'color': [0.8, 0.2, 0.2, 1.0],
                'selected': False,
                'pressure': 1.0
            },
            'heater': {
                'position': [0.0, 0.0, 2.5],
                'rotation': [0.0, 0.0, 0.0],
                'scale': [1.2, 1.2, 0.2],
                'color': [1.0, 0.5, 0.0, 1.0],
                'selected': False,
                'power': 0.0
            }
        }

        # 애니메이션
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate)
        self.animation_timer.start(33)  # 30 FPS

        # 파티클 시스템 (가스 플로우 시각화)
        self.particles = []
        self.max_particles = 200

        # 센서 데이터 시뮬레이션
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.update_sensor_data)
        self.sensor_timer.start(1000)  # 1초마다 센서 데이터 업데이트

    def initializeGL(self):
        """OpenGL 초기화"""
        # 깊이 테스트
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        # 조명 설정
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)

        # 메인 조명
        light0_pos = [5.0, 5.0, 5.0, 1.0]
        light0_ambient = [0.3, 0.3, 0.3, 1.0]
        light0_diffuse = [0.8, 0.8, 0.8, 1.0]
        light0_specular = [1.0, 1.0, 1.0, 1.0]

        glLightfv(GL_LIGHT0, GL_POSITION, light0_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light0_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light0_specular)

        # 보조 조명
        light1_pos = [-3.0, -3.0, 3.0, 1.0]
        light1_ambient = [0.1, 0.1, 0.1, 1.0]
        light1_diffuse = [0.4, 0.4, 0.4, 1.0]

        glLightfv(GL_LIGHT1, GL_POSITION, light1_pos)
        glLightfv(GL_LIGHT1, GL_AMBIENT, light1_ambient)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)

        # 블렌딩 (투명도)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # 배경색
        glClearColor(0.05, 0.05, 0.1, 1.0)

    def resizeGL(self, width, height):
        """뷰포트 크기 변경"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect_ratio = width / height if height != 0 else 1.0
        gluPerspective(45.0, aspect_ratio, 0.1, 100.0)

    def paintGL(self):
        """3D 렌더링"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # 카메라 설정
        glTranslatef(0.0, 0.0, -self.camera_distance)
        glRotatef(self.camera_rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.camera_rotation_y, 0.0, 1.0, 0.0)

        # 좌표축 렌더링
        self.render_axes()

        # 장비 컴포넌트 렌더링
        self.render_equipment_components()

        # 파티클 시스템 렌더링 (가스 플로우)
        self.render_particles()

        # 센서 데이터 시각화
        self.render_sensor_overlays()

    def render_axes(self):
        """좌표축 렌더링"""
        glDisable(GL_LIGHTING)
        glLineWidth(3.0)

        glBegin(GL_LINES)
        # X축 (빨강)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(2.0, 0.0, 0.0)

        # Y축 (녹색)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 2.0, 0.0)

        # Z축 (파랑)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 2.0)
        glEnd()

        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    def render_equipment_components(self):
        """장비 컴포넌트 렌더링"""
        for comp_name, comp_data in self.equipment_components.items():
            glPushMatrix()

            # 변환 적용
            pos = comp_data['position']
            rot = comp_data['rotation']
            scale = comp_data['scale']

            glTranslatef(pos[0], pos[1], pos[2])
            glRotatef(rot[0], 1.0, 0.0, 0.0)
            glRotatef(rot[1], 0.0, 1.0, 0.0)
            glRotatef(rot[2], 0.0, 0.0, 1.0)
            glScalef(scale[0], scale[1], scale[2])

            # 재질 설정
            self.set_material(comp_data)

            # 컴포넌트별 렌더링
            if comp_name == 'chamber':
                self.render_chamber(comp_data)
            elif comp_name.startswith('gas_inlet'):
                self.render_gas_inlet(comp_data)
            elif comp_name == 'exhaust_port':
                self.render_exhaust_port(comp_data)
            elif comp_name == 'heater':
                self.render_heater(comp_data)

            glPopMatrix()

    def set_material(self, comp_data):
        """재질 속성 설정"""
        color = comp_data['color']
        selected = comp_data['selected']

        # 선택된 컴포넌트는 밝게 표시
        if selected:
            ambient = [color[0] * 0.5, color[1] * 0.5, color[2] * 0.5, color[3]]
            diffuse = [min(1.0, color[0] * 1.5), min(1.0, color[1] * 1.5),
                      min(1.0, color[2] * 1.5), color[3]]
        else:
            ambient = [color[0] * 0.3, color[1] * 0.3, color[2] * 0.3, color[3]]
            diffuse = color

        specular = [0.8, 0.8, 0.8, 1.0]
        shininess = [50.0]

        glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, shininess)

    def render_chamber(self, comp_data):
        """반응 챔버 렌더링"""
        # 외부 챔버 (원통)
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)

        # 원통 몸체
        gluCylinder(quadric, 1.5, 1.5, 2.0, 32, 16)

        # 상단
        glPushMatrix()
        glTranslatef(0.0, 0.0, 2.0)
        gluDisk(quadric, 0.0, 1.5, 32, 16)
        glPopMatrix()

        # 하단
        gluDisk(quadric, 0.0, 1.5, 32, 16)

        # 온도에 따른 내부 글로우 효과
        temperature = comp_data.get('temperature', 25.0)
        if temperature > 100.0:
            glDisable(GL_LIGHTING)
            glow_intensity = min(1.0, (temperature - 100.0) / 300.0)
            glColor4f(1.0, 0.5 * glow_intensity, 0.0, 0.3 * glow_intensity)

            # 내부 구
            glPushMatrix()
            glTranslatef(0.0, 0.0, 1.0)
            gluSphere(quadric, 1.3, 16, 16)
            glPopMatrix()

            glEnable(GL_LIGHTING)

    def render_gas_inlet(self, comp_data):
        """가스 입구 렌더링"""
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)

        # 파이프
        gluCylinder(quadric, 0.15, 0.15, 1.0, 16, 8)

        # 밸브 (구)
        glPushMatrix()
        glTranslatef(0.0, 0.0, 0.5)
        gluSphere(quadric, 0.2, 16, 16)
        glPopMatrix()

        # 가스 플로우 표시
        flow_rate = comp_data.get('flow_rate', 0.0)
        if flow_rate > 0:
            self.generate_gas_particles(comp_data['position'], flow_rate)

    def render_exhaust_port(self, comp_data):
        """배기구 렌더링"""
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)

        # 배기 파이프
        gluCylinder(quadric, 0.3, 0.5, 1.0, 16, 8)

        # 플랜지
        glPushMatrix()
        glTranslatef(0.0, 0.0, 1.0)
        gluDisk(quadric, 0.3, 0.7, 24, 4)
        glPopMatrix()

    def render_heater(self, comp_data):
        """히터 렌더링"""
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)

        # 히터 플레이트
        gluCylinder(quadric, 1.0, 1.0, 0.1, 32, 4)

        # 히터 코일 (스프링 형태)
        power = comp_data.get('power', 0.0)
        if power > 0:
            glDisable(GL_LIGHTING)
            heat_intensity = min(1.0, power / 1000.0)
            glColor4f(1.0, heat_intensity * 0.5, 0.0, 0.8)

            glBegin(GL_LINE_STRIP)
            for i in range(0, 360 * 3, 10):  # 3회전
                angle = math.radians(i)
                radius = 0.8 - (i / (360 * 3)) * 0.2
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                z = 0.05 + (i / (360 * 3)) * 0.1

                glVertex3f(x, y, z)
            glEnd()

            glEnable(GL_LIGHTING)

    def generate_gas_particles(self, inlet_pos, flow_rate):
        """가스 파티클 생성"""
        particle_count = int(flow_rate / 10.0)  # 유량에 비례한 파티클 수

        for _ in range(particle_count):
            if len(self.particles) < self.max_particles:
                particle = {
                    'position': list(inlet_pos),
                    'velocity': [
                        random.uniform(-0.1, 0.1),
                        random.uniform(-0.1, 0.1),
                        random.uniform(-0.5, -0.2)
                    ],
                    'life': random.uniform(1.0, 3.0),
                    'size': random.uniform(0.02, 0.05),
                    'color': [0.8, 0.8, 1.0, 0.6]
                }
                self.particles.append(particle)

    def render_particles(self):
        """파티클 렌더링"""
        glDisable(GL_LIGHTING)
        glEnable(GL_POINT_SMOOTH)

        for particle in self.particles:
            alpha = particle['life'] / 3.0  # 생명력에 따른 투명도
            glColor4f(particle['color'][0], particle['color'][1],
                     particle['color'][2], alpha)

            glPointSize(particle['size'] * 100)
            glBegin(GL_POINTS)
            glVertex3f(particle['position'][0], particle['position'][1], particle['position'][2])
            glEnd()

        glDisable(GL_POINT_SMOOTH)
        glEnable(GL_LIGHTING)

    def render_sensor_overlays(self):
        """센서 데이터 오버레이 렌더링"""
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)

        # 온도 센서 위치에 텍스트 표시
        chamber_data = self.equipment_components['chamber']
        temp = chamber_data.get('temperature', 25.0)

        # 3D 위치를 2D 스크린 좌표로 변환 (간단한 구현)
        glColor3f(1.0, 1.0, 0.0)
        self.render_text_3d([0.0, 2.5, 0.0], f"T: {temp:.1f}°C")

        # 압력 센서
        exhaust_data = self.equipment_components['exhaust_port']
        pressure = exhaust_data.get('pressure', 1.0)
        self.render_text_3d([0.0, -2.5, -2.0], f"P: {pressure:.2f}T")

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

    def render_text_3d(self, position, text):
        """3D 공간에 텍스트 렌더링 (간단한 구현)"""
        # 실제로는 QOpenGLWidget에서 텍스트 렌더링은 복잡함
        # 여기서는 간단한 라인으로 대체
        glPushMatrix()
        glTranslatef(position[0], position[1], position[2])

        # 텍스트 배경 (사각형)
        glBegin(GL_QUADS)
        glVertex3f(-0.5, -0.1, 0.0)
        glVertex3f(0.5, -0.1, 0.0)
        glVertex3f(0.5, 0.1, 0.0)
        glVertex3f(-0.5, 0.1, 0.0)
        glEnd()

        glPopMatrix()

    def animate(self):
        """애니메이션 업데이트"""
        # 파티클 업데이트
        dt = 0.033  # 33ms

        for particle in self.particles[:]:
            # 위치 업데이트
            particle['position'][0] += particle['velocity'][0] * dt
            particle['position'][1] += particle['velocity'][1] * dt
            particle['position'][2] += particle['velocity'][2] * dt

            # 생명력 감소
            particle['life'] -= dt

            # 중력 효과
            particle['velocity'][2] -= 0.1 * dt

            # 생명력이 다한 파티클 제거
            if particle['life'] <= 0:
                self.particles.remove(particle)

        self.update()

    def update_sensor_data(self):
        """센서 데이터 업데이트 (시뮬레이션)"""
        # 온도 시뮬레이션
        heater_power = self.equipment_components['heater'].get('power', 0.0)
        current_temp = self.equipment_components['chamber']['temperature']

        # 히터 파워에 따른 온도 변화
        target_temp = 25.0 + (heater_power / 1000.0) * 400.0  # 최대 425°C
        temp_change = (target_temp - current_temp) * 0.1  # 느린 온도 변화

        new_temp = current_temp + temp_change + random.uniform(-2.0, 2.0)
        new_temp = max(20.0, min(500.0, new_temp))  # 온도 제한

        self.equipment_components['chamber']['temperature'] = new_temp
        self.sensor_data_updated.emit('chamber_temperature', new_temp)

        # 압력 시뮬레이션
        gas_flow_total = sum([
            comp.get('flow_rate', 0.0) for comp in self.equipment_components.values()
            if 'flow_rate' in comp
        ])

        base_pressure = 0.1 + (gas_flow_total / 1000.0) * 10.0
        new_pressure = base_pressure + random.uniform(-0.1, 0.1)
        new_pressure = max(0.01, min(20.0, new_pressure))

        self.equipment_components['exhaust_port']['pressure'] = new_pressure
        self.sensor_data_updated.emit('chamber_pressure', new_pressure)

    def mousePressEvent(self, event):
        """마우스 클릭 이벤트"""
        self.last_mouse_pos = event.position()

        # 레이캐스팅을 통한 컴포넌트 선택 (간단한 구현)
        # 실제로는 더 복잡한 3D 피킹 알고리즘 필요
        if event.button() == Qt.LeftButton:
            self.select_component_at_mouse(event.position())

    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트"""
        if self.last_mouse_pos is None:
            return

        dx = event.position().x() - self.last_mouse_pos.x()
        dy = event.position().y() - self.last_mouse_pos.y()

        if event.buttons() & Qt.LeftButton:
            # 카메라 회전
            self.camera_rotation_y += dx * self.mouse_sensitivity
            self.camera_rotation_x += dy * self.mouse_sensitivity

            # 회전 제한
            self.camera_rotation_x = max(-90, min(90, self.camera_rotation_x))

        self.last_mouse_pos = event.position()
        self.update()

    def wheelEvent(self, event):
        """마우스 휠 이벤트 (줌)"""
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9

        self.camera_distance *= zoom_factor
        self.camera_distance = max(3.0, min(20.0, self.camera_distance))

        self.update()

    def select_component_at_mouse(self, mouse_pos):
        """마우스 위치의 컴포넌트 선택"""
        # 간단한 거리 기반 선택 (실제로는 레이캐스팅 사용)
        # 모든 컴포넌트 선택 해제
        for comp_data in self.equipment_components.values():
            comp_data['selected'] = False

        # 첫 번째 컴포넌트 선택 (데모용)
        component_names = list(self.equipment_components.keys())
        if component_names:
            selected_comp = component_names[0]
            self.equipment_components[selected_comp]['selected'] = True
            self.component_selected.emit(selected_comp)

    def set_component_parameter(self, component_name, parameter, value):
        """컴포넌트 파라미터 설정"""
        if component_name in self.equipment_components:
            self.equipment_components[component_name][parameter] = value

class Equipment3DController(QWidget):
    """3D 장비 제어 패널"""

    def __init__(self, equipment_3d, parent=None):
        super().__init__(parent)
        self.equipment_3d = equipment_3d
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)

        # 히터 제어
        heater_group = QVBoxLayout()
        heater_group.addWidget(QLabel("히터 제어"))

        self.heater_slider = QSlider(Qt.Horizontal)
        self.heater_slider.setRange(0, 1000)
        self.heater_slider.setValue(0)
        self.heater_label = QLabel("Power: 0W")

        heater_group.addWidget(self.heater_label)
        heater_group.addWidget(self.heater_slider)

        layout.addLayout(heater_group)

        # 가스 유량 제어
        gas_group = QVBoxLayout()
        gas_group.addWidget(QLabel("가스 유량 제어"))

        self.gas1_slider = QSlider(Qt.Horizontal)
        self.gas1_slider.setRange(0, 200)
        self.gas1_label = QLabel("Gas 1: 0 sccm")

        self.gas2_slider = QSlider(Qt.Horizontal)
        self.gas2_slider.setRange(0, 200)
        self.gas2_label = QLabel("Gas 2: 0 sccm")

        gas_group.addWidget(self.gas1_label)
        gas_group.addWidget(self.gas1_slider)
        gas_group.addWidget(self.gas2_label)
        gas_group.addWidget(self.gas2_slider)

        layout.addLayout(gas_group)

        # 센서 데이터 표시
        sensor_group = QVBoxLayout()
        sensor_group.addWidget(QLabel("센서 데이터"))

        self.temp_label = QLabel("Temperature: --°C")
        self.pressure_label = QLabel("Pressure: --T")

        sensor_group.addWidget(self.temp_label)
        sensor_group.addWidget(self.pressure_label)

        layout.addLayout(sensor_group)

    def setup_connections(self):
        """시그널 연결"""
        self.heater_slider.valueChanged.connect(self.on_heater_changed)
        self.gas1_slider.valueChanged.connect(self.on_gas1_changed)
        self.gas2_slider.valueChanged.connect(self.on_gas2_changed)

        self.equipment_3d.component_selected.connect(self.on_component_selected)
        self.equipment_3d.sensor_data_updated.connect(self.on_sensor_data_updated)

    def on_heater_changed(self, value):
        """히터 파워 변경"""
        self.heater_label.setText(f"Power: {value}W")
        self.equipment_3d.set_component_parameter('heater', 'power', value)

    def on_gas1_changed(self, value):
        """가스1 유량 변경"""
        self.gas1_label.setText(f"Gas 1: {value} sccm")
        self.equipment_3d.set_component_parameter('gas_inlet_1', 'flow_rate', value)

    def on_gas2_changed(self, value):
        """가스2 유량 변경"""
        self.gas2_label.setText(f"Gas 2: {value} sccm")
        self.equipment_3d.set_component_parameter('gas_inlet_2', 'flow_rate', value)

    def on_component_selected(self, component_name):
        """컴포넌트 선택 시"""
        print(f"Selected component: {component_name}")

    def on_sensor_data_updated(self, sensor_name, value):
        """센서 데이터 업데이트"""
        if sensor_name == 'chamber_temperature':
            self.temp_label.setText(f"Temperature: {value:.1f}°C")
        elif sensor_name == 'chamber_pressure':
            self.pressure_label.setText(f"Pressure: {value:.2f}T")

class Equipment3DViewer(QMainWindow):
    """3D 장비 뷰어 메인 윈도우"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Equipment Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 레이아웃
        layout = QHBoxLayout(central_widget)

        # 3D 뷰
        self.equipment_3d = Interactive3DEquipment()

        # 제어 패널
        self.controller = Equipment3DController(self.equipment_3d)
        self.controller.setMaximumWidth(300)

        layout.addWidget(self.equipment_3d, 3)
        layout.addWidget(self.controller, 1)

# 메인 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Equipment3DViewer()
    window.show()

    sys.exit(app.exec())
```

</div>

#### **3.2 플러그인 아키텍처 시스템**

##### **3.2.1 동적 모듈 로딩 시스템**

<div class="plugin-architecture">

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import importlib
import importlib.util
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QWidget, QListWidget, QPushButton, QLabel, QTextEdit,
                               QSplitter, QGroupBox, QComboBox, QTabWidget)
from PySide6.QtCore import Qt, Signal, QObject, QThread
import json

class PluginInterface(ABC):
    """플러그인 인터페이스 기본 클래스"""

    @abstractmethod
    def get_name(self) -> str:
        """플러그인 이름 반환"""
        pass

    @abstractmethod
    def get_version(self) -> str:
        """플러그인 버전 반환"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """플러그인 설명 반환"""
        pass

    @abstractmethod
    def initialize(self, context: Dict[str, Any]) -> bool:
        """플러그인 초기화"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """플러그인 정리"""
        pass

    @abstractmethod
    def get_widget(self) -> Optional[QWidget]:
        """플러그인 UI 위젯 반환"""
        pass

class DataProcessorPlugin(PluginInterface):
    """데이터 처리 플러그인 인터페이스"""

    @abstractmethod
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 처리"""
        pass

    @abstractmethod
    def get_supported_data_types(self) -> List[str]:
        """지원하는 데이터 타입 목록"""
        pass

class VisualizationPlugin(PluginInterface):
    """시각화 플러그인 인터페이스"""

    @abstractmethod
    def create_visualization(self, data: Dict[str, Any]) -> QWidget:
        """시각화 위젯 생성"""
        pass

    @abstractmethod
    def update_visualization(self, data: Dict[str, Any]) -> None:
        """시각화 업데이트"""
        pass

class CommunicationPlugin(PluginInterface):
    """통신 플러그인 인터페이스"""

    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> bool:
        """연결 설정"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """연결 해제"""
        pass

    @abstractmethod
    def send_data(self, data: Dict[str, Any]) -> bool:
        """데이터 전송"""
        pass

    @abstractmethod
    def receive_data(self) -> Optional[Dict[str, Any]]:
        """데이터 수신"""
        pass

class PluginManager(QObject):
    """플러그인 관리자"""

    plugin_loaded = Signal(str)
    plugin_unloaded = Signal(str)
    plugin_error = Signal(str, str)

    def __init__(self):
        super().__init__()

        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_configs: Dict[str, Dict] = {}
        self.plugin_paths: List[str] = ["plugins/"]

        # 플러그인 카테고리별 관리
        self.data_processors: Dict[str, DataProcessorPlugin] = {}
        self.visualizers: Dict[str, VisualizationPlugin] = {}
        self.communicators: Dict[str, CommunicationPlugin] = {}

    def add_plugin_path(self, path: str):
        """플러그인 경로 추가"""
        if path not in self.plugin_paths:
            self.plugin_paths.append(path)

    def discover_plugins(self) -> List[str]:
        """플러그인 발견"""
        discovered = []

        for plugin_path in self.plugin_paths:
            if not os.path.exists(plugin_path):
                continue

            for item in os.listdir(plugin_path):
                item_path = os.path.join(plugin_path, item)

                if os.path.isdir(item_path):
                    # 디렉토리 형태 플러그인
                    plugin_file = os.path.join(item_path, "plugin.py")
                    if os.path.exists(plugin_file):
                        discovered.append(plugin_file)

                elif item.endswith(".py") and item != "__init__.py":
                    # 단일 파일 플러그인
                    discovered.append(item_path)

        return discovered

    def load_plugin(self, plugin_path: str) -> bool:
        """플러그인 로드"""
        try:
            # 모듈 이름 생성
            module_name = os.path.splitext(os.path.basename(plugin_path))[0]

            # 모듈 스펙 생성
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load plugin spec from {plugin_path}")

            # 모듈 생성 및 실행
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 플러그인 클래스 찾기
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, PluginInterface) and
                    attr != PluginInterface):
                    plugin_class = attr
                    break

            if plugin_class is None:
                raise ImportError("No valid plugin class found")

            # 플러그인 인스턴스 생성
            plugin_instance = plugin_class()

            # 플러그인 초기화
            context = {
                'plugin_manager': self,
                'config': self.plugin_configs.get(plugin_instance.get_name(), {})
            }

            if not plugin_instance.initialize(context):
                raise RuntimeError("Plugin initialization failed")

            # 플러그인 등록
            plugin_name = plugin_instance.get_name()
            self.plugins[plugin_name] = plugin_instance

            # 카테고리별 등록
            if isinstance(plugin_instance, DataProcessorPlugin):
                self.data_processors[plugin_name] = plugin_instance
            elif isinstance(plugin_instance, VisualizationPlugin):
                self.visualizers[plugin_name] = plugin_instance
            elif isinstance(plugin_instance, CommunicationPlugin):
                self.communicators[plugin_name] = plugin_instance

            self.plugin_loaded.emit(plugin_name)
            return True

        except Exception as e:
            error_msg = f"Failed to load plugin {plugin_path}: {str(e)}"
            self.plugin_error.emit(plugin_path, error_msg)
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """플러그인 언로드"""
        try:
            if plugin_name not in self.plugins:
                return False

            plugin = self.plugins[plugin_name]

            # 플러그인 정리
            plugin.cleanup()

            # 카테고리별 제거
            if plugin_name in self.data_processors:
                del self.data_processors[plugin_name]
            elif plugin_name in self.visualizers:
                del self.visualizers[plugin_name]
            elif plugin_name in self.communicators:
                del self.communicators[plugin_name]

            # 메인 목록에서 제거
            del self.plugins[plugin_name]

            self.plugin_unloaded.emit(plugin_name)
            return True

        except Exception as e:
            error_msg = f"Failed to unload plugin {plugin_name}: {str(e)}"
            self.plugin_error.emit(plugin_name, error_msg)
            return False

    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """플러그인 인스턴스 반환"""
        return self.plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: type) -> Dict[str, PluginInterface]:
        """타입별 플러그인 목록 반환"""
        result = {}
        for name, plugin in self.plugins.items():
            if isinstance(plugin, plugin_type):
                result[name] = plugin
        return result

    def load_plugin_config(self, config_path: str):
        """플러그인 설정 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.plugin_configs = json.load(f)
        except Exception as e:
            print(f"Failed to load plugin config: {e}")

    def save_plugin_config(self, config_path: str):
        """플러그인 설정 저장"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.plugin_configs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save plugin config: {e}")

    def process_data_with_plugins(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """데이터 처리 플러그인들로 데이터 처리"""
        result = data.copy()

        for processor in self.data_processors.values():
            if data_type in processor.get_supported_data_types():
                try:
                    result = processor.process_data(result)
                except Exception as e:
                    error_msg = f"Data processing error in {processor.get_name()}: {str(e)}"
                    self.plugin_error.emit(processor.get_name(), error_msg)

        return result

class PluginManagerWidget(QWidget):
    """플러그인 관리자 UI"""

    def __init__(self, plugin_manager: PluginManager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)

        # 플러그인 발견 및 로드
        discovery_layout = QHBoxLayout()

        self.discover_button = QPushButton("플러그인 검색")
        self.load_button = QPushButton("선택된 플러그인 로드")
        self.unload_button = QPushButton("선택된 플러그인 언로드")

        discovery_layout.addWidget(self.discover_button)
        discovery_layout.addWidget(self.load_button)
        discovery_layout.addWidget(self.unload_button)
        discovery_layout.addStretch()

        layout.addLayout(discovery_layout)

        # 플러그인 목록
        splitter = QSplitter(Qt.Horizontal)

        # 발견된 플러그인 목록
        discovered_group = QGroupBox("발견된 플러그인")
        discovered_layout = QVBoxLayout(discovered_group)

        self.discovered_list = QListWidget()
        discovered_layout.addWidget(self.discovered_list)

        splitter.addWidget(discovered_group)

        # 로드된 플러그인 목록
        loaded_group = QGroupBox("로드된 플러그인")
        loaded_layout = QVBoxLayout(loaded_group)

        self.loaded_list = QListWidget()
        loaded_layout.addWidget(self.loaded_list)

        # 플러그인 상세 정보
        self.plugin_info = QTextEdit()
        self.plugin_info.setMaximumHeight(100)
        loaded_layout.addWidget(QLabel("플러그인 정보:"))
        loaded_layout.addWidget(self.plugin_info)

        splitter.addWidget(loaded_group)

        layout.addWidget(splitter)

        # 플러그인 카테고리별 탭
        self.plugin_tabs = QTabWidget()

        # 데이터 처리 탭
        self.data_processor_tab = QWidget()
        data_processor_layout = QVBoxLayout(self.data_processor_tab)
        self.data_processor_list = QListWidget()
        data_processor_layout.addWidget(self.data_processor_list)
        self.plugin_tabs.addTab(self.data_processor_tab, "데이터 처리")

        # 시각화 탭
        self.visualization_tab = QWidget()
        visualization_layout = QVBoxLayout(self.visualization_tab)
        self.visualization_list = QListWidget()
        visualization_layout.addWidget(self.visualization_list)
        self.plugin_tabs.addTab(self.visualization_tab, "시각화")

        # 통신 탭
        self.communication_tab = QWidget()
        communication_layout = QVBoxLayout(self.communication_tab)
        self.communication_list = QListWidget()
        communication_layout.addWidget(self.communication_list)
        self.plugin_tabs.addTab(self.communication_tab, "통신")

        layout.addWidget(self.plugin_tabs)

    def setup_connections(self):
        """시그널 연결"""
        self.discover_button.clicked.connect(self.discover_plugins)
        self.load_button.clicked.connect(self.load_selected_plugin)
        self.unload_button.clicked.connect(self.unload_selected_plugin)

        self.loaded_list.currentItemChanged.connect(self.on_plugin_selected)

        self.plugin_manager.plugin_loaded.connect(self.on_plugin_loaded)
        self.plugin_manager.plugin_unloaded.connect(self.on_plugin_unloaded)
        self.plugin_manager.plugin_error.connect(self.on_plugin_error)

    def discover_plugins(self):
        """플러그인 검색"""
        self.discovered_list.clear()

        plugins = self.plugin_manager.discover_plugins()
        for plugin_path in plugins:
            plugin_name = os.path.basename(plugin_path)
            self.discovered_list.addItem(f"{plugin_name} ({plugin_path})")

    def load_selected_plugin(self):
        """선택된 플러그인 로드"""
        current_item = self.discovered_list.currentItem()
        if current_item:
            # 경로 추출
            text = current_item.text()
            plugin_path = text.split(" (")[1].rstrip(")")

            self.plugin_manager.load_plugin(plugin_path)

    def unload_selected_plugin(self):
        """선택된 플러그인 언로드"""
        current_item = self.loaded_list.currentItem()
        if current_item:
            plugin_name = current_item.text().split(" - ")[0]
            self.plugin_manager.unload_plugin(plugin_name)

    def on_plugin_loaded(self, plugin_name):
        """플러그인 로드됨"""
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if plugin:
            item_text = f"{plugin_name} - {plugin.get_version()}"
            self.loaded_list.addItem(item_text)

            # 카테고리별 목록 업데이트
            if isinstance(plugin, DataProcessorPlugin):
                self.data_processor_list.addItem(plugin_name)
            elif isinstance(plugin, VisualizationPlugin):
                self.visualization_list.addItem(plugin_name)
            elif isinstance(plugin, CommunicationPlugin):
                self.communication_list.addItem(plugin_name)

    def on_plugin_unloaded(self, plugin_name):
        """플러그인 언로드됨"""
        # 로드된 목록에서 제거
        for i in range(self.loaded_list.count()):
            item = self.loaded_list.item(i)
            if item.text().startswith(plugin_name):
                self.loaded_list.takeItem(i)
                break

        # 카테고리별 목록에서 제거
        for list_widget in [self.data_processor_list, self.visualization_list, self.communication_list]:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                if item.text() == plugin_name:
                    list_widget.takeItem(i)
                    break

    def on_plugin_error(self, plugin_name, error_message):
        """플러그인 오류"""
        print(f"Plugin Error [{plugin_name}]: {error_message}")

    def on_plugin_selected(self, current, previous):
        """플러그인 선택됨"""
        if current:
            plugin_name = current.text().split(" - ")[0]
            plugin = self.plugin_manager.get_plugin(plugin_name)

            if plugin:
                info_text = f"""
이름: {plugin.get_name()}
버전: {plugin.get_version()}
설명: {plugin.get_description()}
타입: {type(plugin).__name__}
"""
                self.plugin_info.setText(info_text)

class ModularHMISystem(QMainWindow):
    """모듈형 HMI 시스템"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("모듈형 HMI 시스템")
        self.setGeometry(100, 100, 1400, 900)

        # 플러그인 매니저 초기화
        self.plugin_manager = PluginManager()

        # 플러그인 디렉토리 생성
        self.create_plugin_directories()

        # 샘플 플러그인 생성
        self.create_sample_plugins()

        self.setup_ui()

    def create_plugin_directories(self):
        """플러그인 디렉토리 생성"""
        os.makedirs("plugins", exist_ok=True)

    def create_sample_plugins(self):
        """샘플 플러그인 생성"""
        # 간단한 데이터 필터 플러그인
        sample_plugin_code = '''
from plugin_interfaces import DataProcessorPlugin
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class SimpleFilterPlugin(DataProcessorPlugin):
    def get_name(self):
        return "Simple Data Filter"

    def get_version(self):
        return "1.0.0"

    def get_description(self):
        return "간단한 데이터 필터링 플러그인"

    def initialize(self, context):
        return True

    def cleanup(self):
        pass

    def get_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Simple Filter Plugin"))
        return widget

    def process_data(self, data):
        # 간단한 필터링 로직
        filtered_data = data.copy()
        for key, value in data.items():
            if isinstance(value, (int, float)):
                # 이상치 제거 (간단한 예)
                if abs(value) > 1000:
                    filtered_data[key] = 0
        return filtered_data

    def get_supported_data_types(self):
        return ["sensor_data", "process_data"]
'''

        # 플러그인 파일 생성
        with open("plugins/simple_filter.py", "w", encoding="utf-8") as f:
            f.write(sample_plugin_code)

    def setup_ui(self):
        """UI 설정"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        # 플러그인 관리자 UI
        plugin_manager_widget = PluginManagerWidget(self.plugin_manager)
        plugin_manager_widget.setMaximumWidth(600)

        # 메인 작업 영역
        work_area = QWidget()
        work_layout = QVBoxLayout(work_area)
        work_layout.addWidget(QLabel("메인 작업 영역"))
        work_layout.addWidget(QLabel("여기에 플러그인들이 통합됩니다"))

        layout.addWidget(plugin_manager_widget, 1)
        layout.addWidget(work_area, 2)

# 메인 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ModularHMISystem()
    window.show()

    sys.exit(app.exec())
```

</div>

---

## 4️⃣ Hands-on 실습
### 🚀 **통합 모듈형 HMI 플랫폼 구축**

#### **4.1 최종 프로젝트 개요**

<div class="final-project">

**🎯 목표**: 모든 고급 기능을 통합한 완전한 모듈형 HMI 플랫폼 구축

**📋 핵심 구성요소**:
- 커스텀 위젯 기반 전문적 UI
- 3D 시각화를 통한 직관적 장비 모니터링
- 플러그인 시스템을 통한 확장 가능성
- 국제화 및 테마 지원
- 고성능 실시간 데이터 처리

</div>

#### **4.2 통합 플랫폼 구현**

##### **4.2.1 메인 플랫폼 클래스**

<div class="integrated-platform">

```python
#!/usr/bin/env python3
