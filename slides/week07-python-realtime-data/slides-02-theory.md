# 🔄 이론 강의: Python 비동기 프로그래밍

---

## asyncio 기반 비동기 프로그래밍

### 🚀 Async/Await 패턴

**코루틴과 이벤트 루프**

<div class="grid grid-cols-2 gap-8">
<div>

```python
import asyncio
import aiohttp
from typing import List

# Coroutine 정의
async def fetch_sensor_data(sensor_id: str) -> dict:
    """비동기 센서 데이터 조회"""
    print(f"Fetching data from sensor {sensor_id}...")

    # 비동기 HTTP 요청 (aiohttp 사용)
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"http://sensors/{sensor_id}"
        ) as response:
            data = await response.json()
            print(f"Sensor {sensor_id}: {data['value']}")
            return data

async def process_equipment_data(equipment_id: str):
    """장비 데이터 병렬 처리"""
    sensor_ids = ["T001", "P001", "V001"]

    # 병렬 실행 (asyncio.gather)
    results = await asyncio.gather(
        fetch_sensor_data(sensor_ids[0]),
        fetch_sensor_data(sensor_ids[1]),
        fetch_sensor_data(sensor_ids[2]),
        return_exceptions=True  # 예외 무시
    )

    # 결과 처리
    temperature = results[0]['value']
    pressure = results[1]['value']
    voltage = results[2]['value']

    print(f"Equipment {equipment_id}:")
    print(f"  Temperature: {temperature}°C")
    print(f"  Pressure: {pressure} Pa")
    print(f"  Voltage: {voltage} V")

    return {
        'temperature': temperature,
        'pressure': pressure,
        'voltage': voltage
    }

# 실행
async def main():
    start = asyncio.get_event_loop().time()

    # 여러 장비 병렬 처리
    equipment_tasks = [
        process_equipment_data("E001"),
        process_equipment_data("E002"),
        process_equipment_data("E003"),
    ]

    results = await asyncio.gather(*equipment_tasks)

    elapsed = asyncio.get_event_loop().time() - start
    print(f"All equipment processed in {elapsed:.2f}s")

# 이벤트 루프 실행
if __name__ == "__main__":
    asyncio.run(main())
```

</div>
<div>

**Async/Await 핵심 개념**:

**async def**:
- 코루틴 함수 정의
- 항상 코루틴 객체 반환
- `await` 키워드 사용 가능

**await**:
- 다른 코루틴의 완료 대기
- I/O 작업 완료까지 양보
- 이벤트 루프로 제어 반환

**asyncio.gather()**:
- 여러 코루틴 병렬 실행
- 모든 결과를 리스트로 반환
- `return_exceptions=True`: 예외를 결과로 포함

**장점**:
- **높은 동시성**: 수천 개 작업 동시 처리
- **낮은 오버헤드**: 스레드보다 가벼움
- **I/O 바운드 최적**: 네트워크, 파일 I/O

**실행 시간 비교**:
```
# 동기 방식 (순차 실행)
센서 3개 × 1초 = 3초

# 비동기 방식 (병렬 실행)
센서 3개 동시 = 1초
```

**반도체 HMI 적용**:
- 여러 장비 동시 모니터링
- 센서 데이터 병렬 수집
- 웹 API 호출 병렬 처리
- 데이터베이스 비동기 쿼리

**주의사항**:
- CPU-bound 작업에는 부적합
- 모든 I/O가 비동기여야 효과적
- 디버깅이 어려움 (스택 트레이스 복잡)

</div>
</div>

---

### ⏰ asyncio 고급 패턴

**Timeout, Task, Queue**

<div class="grid grid-cols-2 gap-8">
<div>

```python
import asyncio
from asyncio import Queue, Task
from typing import Optional

# 1. Timeout 처리
async def read_sensor_with_timeout(
    sensor_id: str,
    timeout: float = 5.0
) -> Optional[float]:
    """타임아웃이 있는 센서 읽기"""
    try:
        async with asyncio.timeout(timeout):
            # 센서 읽기 시뮬레이션
            await asyncio.sleep(1)
            return 125.5
    except asyncio.TimeoutError:
        print(f"Sensor {sensor_id} timeout!")
        return None

# 2. Task 관리
class EquipmentMonitor:
    def __init__(self):
        self.tasks: List[Task] = []

    async def start_monitoring(self, equipment_id: str):
        """모니터링 시작"""
        task = asyncio.create_task(
            self._monitor_loop(equipment_id),
            name=f"monitor_{equipment_id}"
        )
        self.tasks.append(task)
        return task

    async def _monitor_loop(self, equipment_id: str):
        """모니터링 루프"""
        while True:
            try:
                data = await self.read_equipment_data(
                    equipment_id)
                self.process_data(data)
                await asyncio.sleep(0.1)  # 100ms 주기
            except asyncio.CancelledError:
                print(f"Monitoring {equipment_id} cancelled")
                break

    async def stop_monitoring(self):
        """모든 모니터링 중단"""
        for task in self.tasks:
            task.cancel()

        # 모든 작업 종료 대기
        await asyncio.gather(
            *self.tasks,
            return_exceptions=True
        )

# 3. asyncio.Queue (Producer-Consumer)
async def sensor_producer(queue: Queue):
    """센서 데이터 생산자"""
    sensor_id = 0
    while True:
        data = {
            'id': sensor_id,
            'value': random.uniform(20, 30),
            'timestamp': time.time()
        }
        await queue.put(data)
        sensor_id += 1
        await asyncio.sleep(0.1)

async def data_consumer(queue: Queue, consumer_id: int):
    """데이터 소비자"""
    while True:
        data = await queue.get()
        print(f"Consumer {consumer_id} processing: {data}")
        await asyncio.sleep(0.5)  # 처리 시간
        queue.task_done()

async def main():
    queue = Queue(maxsize=100)

    # 생산자 1개, 소비자 3개
    producer = asyncio.create_task(sensor_producer(queue))
    consumers = [
        asyncio.create_task(data_consumer(queue, i))
        for i in range(3)
    ]

    # 10초 실행 후 종료
    await asyncio.sleep(10)

    producer.cancel()
    for consumer in consumers:
        consumer.cancel()

    await asyncio.gather(
        producer, *consumers,
        return_exceptions=True
    )
```

</div>
<div>

**asyncio.timeout()**:
- Python 3.11+ 타임아웃 컨텍스트
- 지정 시간 초과 시 `TimeoutError`
- 이전 버전: `asyncio.wait_for()`

```python
# Python 3.10 이하
result = await asyncio.wait_for(
    coro(), timeout=5.0)
```

**asyncio.create_task()**:
- 코루틴을 Task로 예약
- 백그라운드 실행
- 취소 가능 (`task.cancel()`)
- 이름 지정 가능 (디버깅 용이)

**Task 상태 확인**:
```python
task = asyncio.create_task(coro())

print(task.done())       # 완료 여부
print(task.cancelled())  # 취소 여부

try:
    result = await task
except asyncio.CancelledError:
    print("Task was cancelled")
```

**asyncio.Queue**:
- 비동기 안전 큐
- `await queue.put(item)`: 항목 추가
- `await queue.get()`: 항목 가져오기
- `queue.task_done()`: 완료 표시
- `await queue.join()`: 모든 작업 완료 대기

**Queue 크기 제한**:
```python
queue = Queue(maxsize=10)

# Queue 가득 차면 대기
await queue.put(item)  # 블로킹

# 즉시 반환 (예외 발생)
queue.put_nowait(item)  # Full 시 QueueFull
```

**실무 패턴**:
```python
async def equipment_controller():
    """장비 제어 루프"""
    command_queue = Queue()

    # 명령 처리 태스크
    processor = asyncio.create_task(
        process_commands(command_queue))

    # 명령 수신 태스크
    receiver = asyncio.create_task(
        receive_commands(command_queue))

    try:
        await asyncio.gather(
            processor, receiver)
    except KeyboardInterrupt:
        processor.cancel()
        receiver.cancel()
```

</div>
</div>

---

## concurrent.futures 기반 병렬 처리

### 🔀 ThreadPoolExecutor / ProcessPoolExecutor

**스레드 vs 프로세스 병렬 실행**

<div class="grid grid-cols-2 gap-8">
<div>

```python
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    as_completed
)
import time

# I/O-bound 작업 (스레드 적합)
def download_sensor_data(sensor_id: str) -> dict:
    """센서 데이터 다운로드"""
    print(f"Downloading from {sensor_id}...")
    time.sleep(1)  # 네트워크 I/O 시뮬레이션
    return {
        'sensor_id': sensor_id,
        'value': 125.5,
        'timestamp': time.time()
    }

# CPU-bound 작업 (프로세스 적합)
def calculate_statistics(data: List[float]) -> dict:
    """통계 계산 (CPU 집약적)"""
    return {
        'mean': sum(data) / len(data),
        'min': min(data),
        'max': max(data),
        'std': statistics.stdev(data)
    }

# ThreadPoolExecutor 사용
def fetch_all_sensors_threaded(sensor_ids: List[str]):
    """스레드 풀로 센서 데이터 수집"""
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Future 객체 생성
        future_to_sensor = {
            executor.submit(download_sensor_data, sid): sid
            for sid in sensor_ids
        }

        results = []
        # 완료된 순서대로 처리
        for future in as_completed(future_to_sensor):
            sensor_id = future_to_sensor[future]
            try:
                data = future.result()
                results.append(data)
            except Exception as e:
                print(f"Sensor {sensor_id} failed: {e}")

        return results

# ProcessPoolExecutor 사용
def analyze_data_parallel(datasets: List[List[float]]):
    """프로세스 풀로 병렬 분석"""
    with ProcessPoolExecutor(max_workers=4) as executor:
        # map으로 병렬 실행
        results = executor.map(
            calculate_statistics,
            datasets
        )
        return list(results)

# 사용 예시
if __name__ == "__main__":
    # I/O-bound: 스레드 풀
    sensor_ids = [f"S{i:03d}" for i in range(50)]
    start = time.time()
    sensor_data = fetch_all_sensors_threaded(sensor_ids)
    print(f"Fetched {len(sensor_data)} sensors "
          f"in {time.time() - start:.2f}s")

    # CPU-bound: 프로세스 풀
    datasets = [
        [random.uniform(0, 100) for _ in range(10000)]
        for _ in range(10)
    ]
    start = time.time()
    stats = analyze_data_parallel(datasets)
    print(f"Analyzed {len(stats)} datasets "
          f"in {time.time() - start:.2f}s")
```

</div>
<div>

**ThreadPoolExecutor**:
- **I/O-bound 작업에 적합**
  - 네트워크 요청
  - 파일 읽기/쓰기
  - 데이터베이스 쿼리

- **GIL 영향 받음**
  - CPU 작업에는 부적합
  - 동시에 1개 스레드만 Python 코드 실행

- **메모리 공유**
  - 같은 메모리 공간 사용
  - 데이터 복사 불필요

**ProcessPoolExecutor**:
- **CPU-bound 작업에 적합**
  - 계산 집약적 작업
  - 데이터 분석
  - 이미지/비디오 처리

- **GIL 우회**
  - 각 프로세스가 독립적 인터프리터
  - 진짜 병렬 실행

- **독립 메모리**
  - 프로세스 간 데이터 복사
  - 오버헤드 존재

**선택 가이드**:
```python
# I/O-bound → ThreadPoolExecutor
- 네트워크 요청
- 파일 I/O
- 데이터베이스

# CPU-bound → ProcessPoolExecutor
- 수학 계산
- 데이터 처리
- 암호화

# Mixed → asyncio + ThreadPoolExecutor
```

**Future 객체**:
```python
future = executor.submit(func, arg)

# 블로킹
result = future.result(timeout=5)

# 논블로킹
if future.done():
    result = future.result()

# 취소
future.cancel()
```

**asyncio와 통합**:
```python
import asyncio

async def async_wrapper():
    loop = asyncio.get_event_loop()

    # ThreadPoolExecutor를 asyncio에서 사용
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor,
            blocking_io_operation,
            arg
        )

    return result
```

**반도체 HMI 적용**:
```python
# 센서 데이터 수집 (I/O)
with ThreadPoolExecutor(max_workers=20) as executor:
    sensor_futures = [
        executor.submit(read_sensor, sid)
        for sid in all_sensors
    ]

# 데이터 분석 (CPU)
with ProcessPoolExecutor(max_workers=8) as executor:
    analysis_results = executor.map(
        analyze_wafer_data,
        wafer_datasets
    )
```

</div>
</div>

---

## QThread와의 통합

### 🔗 Qt 이벤트 루프와 Python 비동기

**PySide6에서 asyncio 사용**

<div class="grid grid-cols-2 gap-8">
<div>

```python
import asyncio
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

# qasync를 사용한 asyncio + Qt 통합
class AsyncEquipmentMonitor(QObject):
    data_updated = Signal(dict)

    def __init__(self):
        super().__init__()
        self.running = False

    async def start_monitoring(self, equipment_id: str):
        """비동기 모니터링 시작"""
        self.running = True

        while self.running:
            try:
                # 비동기 데이터 수집
                data = await self.fetch_equipment_data(
                    equipment_id)

                # Qt Signal로 UI 업데이트
                self.data_updated.emit(data)

                await asyncio.sleep(0.1)  # 100ms 주기

            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(1)

    async def fetch_equipment_data(
        self, equipment_id: str
    ) -> dict:
        """비동기 데이터 조회"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://api/equipment/{equipment_id}"
            ) as response:
                return await response.json()

    def stop_monitoring(self):
        """모니터링 중지"""
        self.running = False

# Qt 애플리케이션에서 사용
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.monitor = AsyncEquipmentMonitor()
        self.monitor.data_updated.connect(
            self.on_data_updated)

    def start_monitoring(self):
        """모니터링 시작"""
        # asyncio Task 생성
        asyncio.create_task(
            self.monitor.start_monitoring("E001"))

    def on_data_updated(self, data: dict):
        """데이터 업데이트 핸들러"""
        self.temperature_label.setText(
            f"{data['temperature']}°C")

# 메인 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # qasync 이벤트 루프 설정
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()
```

</div>
<div>

**qasync 라이브러리**:
```bash
pip install qasync
```

**핵심 개념**:
- Qt 이벤트 루프를 asyncio와 통합
- Signal/Slot을 async/await와 함께 사용
- UI 업데이트를 안전하게 처리

**장점**:
- asyncio의 강력함 + Qt의 안정성
- 비동기 I/O + GUI 응답성
- 네트워크 요청 병렬 처리

**일반적인 QThread 방식**:
```python
class DataWorker(QThread):
    data_ready = Signal(str)

    def run(self):
        # 동기 방식
        result = self.process_data()
        self.data_ready.emit(result)
```

**asyncio 방식**:
```python
class AsyncWorker(QObject):
    data_ready = Signal(str)

    async def process(self):
        # 비동기 방식
        result = await async_process_data()
        self.data_ready.emit(result)

# 사용
worker = AsyncWorker()
asyncio.create_task(worker.process())
```

**실무 패턴**:
```python
class EquipmentController:
    def __init__(self):
        self.tasks = []

    async def start_all_equipment(
        self, equipment_ids: List[str]
    ):
        """모든 장비 병렬 시작"""
        tasks = [
            self.start_equipment(eid)
            for eid in equipment_ids
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

        for eid, result in zip(
            equipment_ids, results
        ):
            if isinstance(result, Exception):
                print(f"{eid} failed: {result}")
            else:
                print(f"{eid} started successfully")
```

**주의사항**:
- Qt Signal은 스레드 안전
- asyncio Task는 취소 가능
- 예외 처리 필수
- 리소스 정리 중요 (finally, context manager)

</div>
</div>

---

## Qt Threading 패턴

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

## 2️⃣ 기초 실습
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

