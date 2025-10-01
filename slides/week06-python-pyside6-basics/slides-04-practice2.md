# Python 가상환경 생성 (Python 3.9+ 권장)
python -m venv hmi_development
cd hmi_development

# Windows에서 가상환경 활성화
Scripts\activate

# Linux/macOS에서 가상환경 활성화
source bin/activate

# PySide6 및 개발 도구 설치
pip install PySide6[all]  # Qt Designer, qmltools 포함
pip install numpy pandas matplotlib  # 데이터 분석 라이브러리
pip install pyserial  # 시리얼 통신
pip install sqlite3  # 데이터베이스 (Python 3.x 기본 포함)
pip install pytest pytest-qt  # 테스트 프레임워크
pip install black flake8  # 코드 포맷팅 및 린터

# 개발용 추가 라이브러리
pip install memory_profiler  # 메모리 프로파일링
pip install line_profiler  # 라인별 성능 분석
pip install psutil  # 시스템 모니터링

# requirements.txt 생성
pip freeze > requirements.txt
```

#### 2. Visual Studio Code 설정
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./hmi_development/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "files.associations": {
        "*.ui": "xml",
        "*.qml": "qml",
        "*.qss": "css"
    },
    "emmet.includeLanguages": {
        "qml": "javascript"
    }
}

// .vscode/launch.json (디버깅 설정)
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {
                "QT_DEBUG_PLUGINS": "1",
                "QT_LOGGING_RULES": "*.debug=true"
            }
        },
        {
            "name": "Python: HMI Application",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "args": ["--debug"]
        }
    ]
}
```

#### 3. 프로젝트 구조 설정
```python
# project_structure.py - 자동으로 프로젝트 구조 생성
import os
from pathlib import Path

def create_project_structure():
    """표준화된 PySide6 HMI 프로젝트 구조 생성"""

    project_structure = {
        'src': {
            'models': ['__init__.py', 'sensor_data.py', 'equipment_model.py'],
            'views': ['__init__.py', 'main_window.py', 'dialogs.py'],
            'controllers': ['__init__.py', 'main_controller.py', 'data_controller.py'],
            'utils': ['__init__.py', 'logger.py', 'config.py', 'validators.py'],
            'resources': ['__init__.py']
        },
        'ui': ['main_window.ui', 'settings_dialog.ui'],
        'resources': ['icons', 'stylesheets', 'data'],
        'tests': ['__init__.py', 'test_models.py', 'test_views.py', 'test_controllers.py'],
        'docs': ['README.md', 'API.md', 'DEPLOYMENT.md'],
        'config': ['settings.json', 'logging.conf'],
        'scripts': ['build.py', 'deploy.py', 'test_runner.py']
    }

    def create_directory_structure(base_path: Path, structure: dict):
        for key, value in structure.items():
            current_path = base_path / key
            current_path.mkdir(exist_ok=True)

            if isinstance(value, dict):
                create_directory_structure(current_path, value)
            elif isinstance(value, list):
                for item in value:
                    if item.endswith('.py'):
                        (current_path / item).touch()
                    elif item.endswith(('.ui', '.json', '.conf', '.md')):
                        (current_path / item).touch()
                    else:
                        (current_path / item).mkdir(exist_ok=True)

    project_root = Path.cwd() / 'hmi_project'
    project_root.mkdir(exist_ok=True)
    create_directory_structure(project_root, project_structure)

    # 기본 파일들 생성
    create_basic_files(project_root)
    print(f"프로젝트 구조가 생성되었습니다: {project_root}")

def create_basic_files(project_root: Path):
    """기본적인 설정 파일들 생성"""

    # main.py
    main_py_content = '''#!/usr/bin/env python3
"""
반도체 HMI 시스템 메인 엔트리 포인트
"""
import sys
import argparse
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLoggingCategory, qmlRegisterType

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

from controllers.main_controller import MainController
from utils.logger import setup_logging
from utils.config import Config


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='반도체 HMI 시스템')
    parser.add_argument('--debug', action='store_true', help='디버그 모드 활성화')
    parser.add_argument('--config', type=str, help='설정 파일 경로')
    args = parser.parse_args()

    # 로깅 설정
    setup_logging(debug=args.debug)

    # Qt 애플리케이션 생성
    app = QApplication(sys.argv)
    app.setApplicationName("반도체 HMI 시스템")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("HMI Solutions")

    # 설정 로드
    config = Config(args.config)

    # 메인 컨트롤러 생성 및 실행
    controller = MainController(config)
    controller.show()

    # 이벤트 루프 시작
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
'''

    with open(project_root / 'main.py', 'w', encoding='utf-8') as f:
        f.write(main_py_content)

    # config/settings.json
    settings_json_content = '''{
    "application": {
        "name": "반도체 HMI 시스템",
        "version": "1.0.0",
        "window": {
            "width": 1920,
            "height": 1080,
            "fullscreen": false
        }
    },
    "data": {
        "update_interval_ms": 100,
        "buffer_size": 10000,
        "data_retention_days": 30
    },
    "communication": {
        "serial": {
            "port": "COM1",
            "baudrate": 9600,
            "timeout": 1.0
        },
        "tcp": {
            "host": "localhost",
            "port": 8080,
            "timeout": 5.0
        }
    },
    "logging": {
        "level": "INFO",
        "file": "logs/hmi.log",
        "max_size_mb": 10,
        "backup_count": 5
    }
}'''

    (project_root / 'config').mkdir(exist_ok=True)
    with open(project_root / 'config' / 'settings.json', 'w', encoding='utf-8') as f:
        f.write(settings_json_content)

if __name__ == '__main__':
    create_project_structure()
```

### Qt Designer 활용 및 .ui 파일 생성

#### 1. Qt Designer 실행 및 기본 설정
```python
# qt_designer_helper.py - Qt Designer 보조 도구
import subprocess
import sys
from pathlib import Path
from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QMessageBox

class QtDesignerHelper:
    """Qt Designer 보조 클래스"""

    def __init__(self):
        self.designer_path = self.find_designer_executable()

    def find_designer_executable(self) -> Path:
        """시스템에서 Qt Designer 실행 파일 찾기"""
        possible_paths = [
            Path(sys.executable).parent / 'Scripts' / 'pyside6-designer.exe',  # Windows
            Path(sys.executable).parent / 'pyside6-designer',  # Linux/macOS
            Path('/usr/bin/designer'),  # Linux 시스템 설치
            Path('/opt/Qt/Tools/QtCreator/bin/designer'),  # Qt Creator 설치
        ]

        for path in possible_paths:
            if path.exists():
                return path

        raise FileNotFoundError("Qt Designer를 찾을 수 없습니다. PySide6[all]이 설치되었는지 확인하세요.")

    def launch_designer(self, ui_file: Path = None):
        """Qt Designer 실행"""
        args = [str(self.designer_path)]
        if ui_file and ui_file.exists():
            args.append(str(ui_file))

        process = QProcess()
        success = process.startDetached(args[0], args[1:])

        if not success:
            QMessageBox.critical(None, "오류", f"Qt Designer 실행에 실패했습니다: {self.designer_path}")

        return success

    def compile_ui_to_py(self, ui_file: Path, output_file: Path = None):
        """UI 파일을 Python 코드로 변환"""
        if not ui_file.exists():
            raise FileNotFoundError(f"UI 파일을 찾을 수 없습니다: {ui_file}")

        if output_file is None:
            output_file = ui_file.with_suffix('.py')

        # pyside6-uic를 사용하여 변환
        uic_path = Path(sys.executable).parent / 'Scripts' / 'pyside6-uic.exe'
        if not uic_path.exists():
            uic_path = Path(sys.executable).parent / 'pyside6-uic'

        result = subprocess.run(
            [str(uic_path), str(ui_file), '-o', str(output_file)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"UI 컴파일 실패: {result.stderr}")

        print(f"UI 파일이 컴파일되었습니다: {output_file}")
        return output_file

# 사용 예제
if __name__ == '__main__':
    helper = QtDesignerHelper()

    # Qt Designer 실행
    helper.launch_designer()

    # UI 파일 컴파일 (예제)
    # helper.compile_ui_to_py(Path('ui/main_window.ui'))
```

#### 2. 기본 메인 윈도우 UI 설계
```xml
<!-- ui/main_window.ui - Qt Designer에서 생성할 기본 UI -->
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1200</width>
    <height>800</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>반도체 HMI 시스템</string>
  </property>
  <property name="styleSheet">
   <string notr="true">
/* 기본 스타일 시트 */
QMainWindow {
    background-color: #f5f5f5;
}

QToolBar {
    background-color: #2c3e50;
    border: none;
    spacing: 3px;
    color: white;
}

QStatusBar {
    background-color: #34495e;
    color: white;
}

QMenuBar {
    background-color: #2c3e50;
    color: white;
}

QMenuBar::item:selected {
    background-color: #3498db;
}
   </string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <layout class="QGridLayout" name="gridLayout">
    <item row="0" column="0">
     <widget class="QTabWidget" name="tabWidget">
      <property name="currentIndex">
       <number>0</number>
      </property>
      <widget class="QWidget" name="tab_overview">
       <attribute name="title">
        <string>시스템 개요</string>
       </attribute>
       <layout class="QVBoxLayout" name="verticalLayout">
        <item>
         <widget class="QGroupBox" name="groupBox_status">
          <property name="title">
           <string>장비 상태</string>
          </property>
          <layout class="QGridLayout" name="gridLayout_2">
           <item row="0" column="0">
            <widget class="QLabel" name="label_temp">
             <property name="text">
              <string>온도:</string>
             </property>
            </widget>
           </item>
           <item row="0" column="1">
            <widget class="QLCDNumber" name="lcd_temperature">
             <property name="digitCount">
              <number>5</number>
             </property>
             <property name="segmentStyle">
              <enum>QLCDNumber::Flat</enum>
             </property>
            </widget>
           </item>
           <item row="1" column="0">
            <widget class="QLabel" name="label_pressure">
             <property name="text">
              <string>압력:</string>
             </property>
            </widget>
           </item>
           <item row="1" column="1">
            <widget class="QLCDNumber" name="lcd_pressure">
             <property name="digitCount">
              <number>5</number>
             </property>
             <property name="segmentStyle">
              <enum>QLCDNumber::Flat</enum>
             </property>
            </widget>
           </item>
          </layout>
         </widget>
        </item>
        <item>
         <widget class="QGroupBox" name="groupBox_control">
          <property name="title">
           <string>제어</string>
          </property>
          <layout class="QHBoxLayout" name="horizontalLayout">
           <item>
            <widget class="QPushButton" name="btn_start">
             <property name="text">
              <string>시작</string>
             </property>
             <property name="styleSheet">
              <string notr="true">
QPushButton {
    background-color: #27ae60;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 5px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2ecc71;
}

QPushButton:pressed {
    background-color: #219a52;
}
              </string>
             </property>
            </widget>
           </item>
           <item>
            <widget class="QPushButton" name="btn_stop">
             <property name="text">
              <string>정지</string>
             </property>
             <property name="styleSheet">
              <string notr="true">
QPushButton {
    background-color: #e74c3c;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 5px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #c0392b;
}

QPushButton:pressed {
    background-color: #a93226;
}
              </string>
             </property>
            </widget>
           </item>
           <item>
            <spacer name="horizontalSpacer">
             <property name="orientation">
              <enum>Qt::Horizontal</enum>
             </property>
             <property name="sizeHint" stdset="0">
              <size>
               <width>40</width>
               <height>20</height>
              </size>
             </property>
            </spacer>
           </item>
          </layout>
         </widget>
        </item>
       </layout>
      </widget>
      <widget class="QWidget" name="tab_data">
       <attribute name="title">
        <string>데이터</string>
       </attribute>
       <layout class="QVBoxLayout" name="verticalLayout_2">
        <item>
         <widget class="QTableWidget" name="table_data">
          <property name="alternatingRowColors">
           <bool>true</bool>
          </property>
          <property name="sortingEnabled">
           <bool>true</bool>
          </property>
          <column>
           <property name="text">
            <string>시간</string>
           </property>
          </column>
          <column>
           <property name="text">
            <string>온도</string>
           </property>
          </column>
          <column>
           <property name="text">
            <string>압력</string>
           </property>
          </column>
          <column>
           <property name="text">
            <string>상태</string>
           </property>
          </column>
         </widget>
        </item>
       </layout>
      </widget>
     </widget>
    </item>
   </layout>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>1200</width>
     <height>22</height>
    </rect>
   </property>
   <widget class="QMenu" name="menu_file">
    <property name="title">
     <string>파일</string>
    </property>
    <addaction name="action_new"/>
    <addaction name="action_open"/>
    <addaction name="action_save"/>
    <addaction name="separator"/>
    <addaction name="action_exit"/>
   </widget>
   <widget class="QMenu" name="menu_tools">
    <property name="title">
     <string>도구</string>
    </property>
    <addaction name="action_settings"/>
    <addaction name="action_calibration"/>
   </widget>
   <addaction name="menu_file"/>
   <addaction name="menu_tools"/>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
  <widget class="QToolBar" name="toolBar">
   <property name="windowTitle">
    <string>toolBar</string>
   </property>
   <attribute name="toolBarArea">
    <enum>TopToolBarArea</enum>
   </attribute>
   <attribute name="toolBarBreak">
    <bool>false</bool>
   </attribute>
   <addaction name="action_start"/>
   <addaction name="action_stop"/>
   <addaction name="separator"/>
   <addaction name="action_settings"/>
  </widget>
  <action name="action_new">
   <property name="text">
    <string>새로 만들기</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+N</string>
   </property>
  </action>
  <action name="action_open">
   <property name="text">
    <string>열기</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+O</string>
   </property>
  </action>
  <action name="action_save">
   <property name="text">
    <string>저장</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+S</string>
   </property>
  </action>
  <action name="action_exit">
   <property name="text">
    <string>종료</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+Q</string>
   </property>
  </action>
  <action name="action_settings">
   <property name="text">
    <string>설정</string>
   </property>
  </action>
  <action name="action_calibration">
   <property name="text">
    <string>캘리브레이션</string>
   </property>
  </action>
  <action name="action_start">
   <property name="text">
    <string>시작</string>
   </property>
   <property name="toolTip">
    <string>시스템 시작</string>
   </property>
  </action>
  <action name="action_stop">
   <property name="text">
    <string>정지</string>
   </property>
   <property name="toolTip">
    <string>시스템 정지</string>
   </property>
  </action>
 </widget>
 <resources/>
 <connections/>
</ui>
```

---

## 실습 2: MVC 아키텍처 및 시그널-슬롯 시스템

### 실습 목표
- MVC (Model-View-Controller) 패턴 구현
- 시그널-슬롯 메커니즘을 활용한 이벤트 처리
- 데이터 모델과 뷰의 분리
- 커스텀 시그널 생성 및 활용

### Model 계층 구현

#### 1. 센서 데이터 모델
```python
