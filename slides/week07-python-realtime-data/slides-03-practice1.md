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
