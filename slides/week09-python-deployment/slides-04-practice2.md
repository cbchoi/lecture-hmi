# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream hmi_backend {
        server hmi-app:8080;
    }

    # HTTP to HTTPS 리다이렉션
    server {
        listen 80;
        server_name semiconductor-hmi.local;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS 서버
    server {
        listen 443 ssl http2;
        server_name semiconductor-hmi.local;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # 보안 헤더
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        location / {
            proxy_pass http://hmi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket 지원
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # 타임아웃 설정
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # 정적 파일 캐싱
        location /static/ {
            alias /app/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # 헬스체크 엔드포인트
        location /health {
            proxy_pass http://hmi_backend/health;
            access_log off;
        }
    }
}
```

---

## 🚀 **심화 실습 (45분) - 자동 업데이트 및 모니터링**

### 실습 3: 자동 업데이트 시스템 구현

#### 3.1 업데이트 서버 구현
```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import hashlib
import aiofiles
from pathlib import Path
from typing import Optional, Dict, List
import asyncio
import logging

app = FastAPI(title="HMI Update Server", version="1.0.0")
security = HTTPBearer()

class UpdateRequest(BaseModel):
    current_version: str
    client_id: str
    platform: str
    arch: str

class UpdateResponse(BaseModel):
    update_available: bool
    new_version: Optional[str] = None
    patch_url: Optional[str] = None
    full_package_url: Optional[str] = None
    checksum: Optional[str] = None
    changes: Optional[List[Dict]] = None
    rollback_supported: bool = True

class UpdateManager:
    """업데이트 관리자"""

    def __init__(self):
        self.updates_dir = Path("./updates")
        self.versions = self.load_version_manifest()

    def load_version_manifest(self) -> Dict:
        """버전 매니페스트 로드"""
        manifest_file = self.updates_dir / "manifest.json"
        if manifest_file.exists():
            import json
            with open(manifest_file) as f:
                return json.load(f)
        return {}

    async def check_update(self, request: UpdateRequest) -> UpdateResponse:
        """업데이트 확인"""
        platform_key = f"{request.platform}-{request.arch}"

        if platform_key not in self.versions:
            raise HTTPException(404, "지원하지 않는 플랫폼")

        latest_version = self.versions[platform_key]["latest"]

        if self.compare_versions(request.current_version, latest_version) < 0:
            # 업데이트 필요
            patch_info = await self.generate_patch_info(
                request.current_version,
                latest_version,
                platform_key
            )

            return UpdateResponse(
                update_available=True,
                new_version=latest_version,
                **patch_info
            )

        return UpdateResponse(update_available=False)

    async def generate_patch_info(self, current: str, target: str, platform: str) -> Dict:
        """패치 정보 생성"""
        patch_file = self.updates_dir / platform / f"{current}_to_{target}.patch"

        if patch_file.exists():
            # 델타 패치 사용
            checksum = await self.calculate_file_checksum(patch_file)
            return {
                "patch_url": f"/download/patch/{platform}/{current}_to_{target}.patch",
                "checksum": checksum,
                "changes": self.get_change_list(current, target)
            }
        else:
            # 전체 패키지 다운로드
            full_package = self.updates_dir / platform / f"{target}.zip"
            checksum = await self.calculate_file_checksum(full_package)
            return {
                "full_package_url": f"/download/full/{platform}/{target}.zip",
                "checksum": checksum,
                "changes": []
            }

@app.post("/api/check-update", response_model=UpdateResponse)
async def check_update(request: UpdateRequest, credentials: HTTPAuthorizationCredentials = security):
    """업데이트 확인 API"""
    try:
        update_manager = UpdateManager()
        return await update_manager.check_update(request)
    except Exception as e:
        logging.error(f"업데이트 확인 오류: {e}")
        raise HTTPException(500, "내부 서버 오류")

@app.get("/download/patch/{platform}/{filename}")
async def download_patch(platform: str, filename: str):
    """패치 파일 다운로드"""
    file_path = Path(f"./updates/{platform}/{filename}")

    if not file_path.exists():
        raise HTTPException(404, "파일을 찾을 수 없음")

    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()

    return Response(
        content=content,
        media_type='application/octet-stream',
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

#### 3.2 클라이언트 업데이트 매니저
```python
import asyncio
import aiohttp
import hashlib
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QProgressDialog, QMessageBox
import logging

class UpdateClient(QObject):
    """클라이언트 업데이트 관리자"""

    update_available = Signal(dict)
    update_progress = Signal(int)
    update_completed = Signal(bool)

    def __init__(self, update_server_url: str, current_version: str):
        super().__init__()
        self.server_url = update_server_url
        self.current_version = current_version
        self.client_id = self.get_client_id()

        # 자동 업데이트 확인 타이머 (1시간마다)
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_for_updates)
        self.check_timer.start(3600000)  # 1시간

    def get_client_id(self) -> str:
        """고유 클라이언트 ID 생성"""
        import uuid
        import platform

        machine_info = f"{platform.node()}-{platform.machine()}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, machine_info))

    async def check_for_updates(self):
        """업데이트 확인"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.server_url}/api/check-update",
                    json={
                        "current_version": self.current_version,
                        "client_id": self.client_id,
                        "platform": platform.system().lower(),
                        "arch": platform.machine().lower()
                    },
                    headers={"Authorization": f"Bearer {self.get_auth_token()}"}
                ) as response:

                    if response.status == 200:
                        update_info = await response.json()
                        if update_info["update_available"]:
                            self.update_available.emit(update_info)
                    else:
                        logging.error(f"업데이트 확인 실패: {response.status}")

        except Exception as e:
            logging.error(f"업데이트 확인 중 오류: {e}")

    async def download_and_apply_update(self, update_info: dict):
        """업데이트 다운로드 및 적용"""
        try:
            # 진행률 다이얼로그 표시
            progress_dialog = QProgressDialog(
                "업데이트를 다운로드하고 있습니다...",
                "취소",
                0, 100
            )
            progress_dialog.show()

            # 백업 생성
            backup_dir = Path("./backup")
            await self.create_backup(backup_dir)

            # 업데이트 다운로드
            if "patch_url" in update_info:
                success = await self.download_and_apply_patch(
                    update_info, progress_dialog
                )
            else:
                success = await self.download_full_update(
                    update_info, progress_dialog
                )

            progress_dialog.close()

            if success:
                # 업데이트 완료 메시지
                QMessageBox.information(
                    None,
                    "업데이트 완료",
                    f"버전 {update_info['new_version']}로 업데이트가 완료되었습니다.\n"
                    "애플리케이션을 재시작해주세요."
                )
                self.update_completed.emit(True)
            else:
                # 롤백 수행
                await self.rollback(backup_dir)
                QMessageBox.warning(
                    None,
                    "업데이트 실패",
                    "업데이트 중 오류가 발생하여 이전 버전으로 복원되었습니다."
                )
                self.update_completed.emit(False)

        except Exception as e:
            logging.error(f"업데이트 적용 중 오류: {e}")
            await self.rollback(backup_dir)
            self.update_completed.emit(False)

    async def create_backup(self, backup_dir: Path):
        """현재 버전 백업"""
        if backup_dir.exists():
            shutil.rmtree(backup_dir)

        backup_dir.mkdir(parents=True)

        # 중요 파일들 백업
        important_files = [
            "main.exe", "config.json", "database.db"
        ]

        for file_name in important_files:
            src_file = Path(file_name)
            if src_file.exists():
                shutil.copy2(src_file, backup_dir / file_name)

    async def verify_update(self, expected_checksum: str) -> bool:
        """업데이트 검증"""
        # 주요 파일들의 체크섬 확인
        current_checksum = await self.calculate_app_checksum()
        return current_checksum == expected_checksum

    async def rollback(self, backup_dir: Path):
        """이전 버전으로 롤백"""
        if not backup_dir.exists():
            return

        for backup_file in backup_dir.glob("*"):
            if backup_file.is_file():
                target_file = Path(backup_file.name)
                shutil.copy2(backup_file, target_file)
```

### 실습 4: 종합 모니터링 시스템

#### 4.1 메트릭 수집 시스템
```python
import psutil
import time
from dataclasses import dataclass
from typing import Dict, List
from PySide6.QtCore import QObject, QTimer, Signal
import sqlite3
from datetime import datetime, timedelta

@dataclass
class SystemMetrics:
    """시스템 메트릭 데이터 클래스"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, int]
    process_count: int
    uptime: float

class MetricsCollector(QObject):
    """시스템 메트릭 수집기"""

    metrics_collected = Signal(SystemMetrics)

    def __init__(self, collection_interval: int = 30):
        super().__init__()
        self.collection_interval = collection_interval
        self.db_path = "metrics.db"
        self.init_database()

        # 메트릭 수집 타이머
        self.timer = QTimer()
        self.timer.timeout.connect(self.collect_metrics)
        self.timer.start(collection_interval * 1000)

    def init_database(self):
        """메트릭 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                cpu_percent REAL,
                memory_percent REAL,
                disk_usage REAL,
                network_bytes_sent INTEGER,
                network_bytes_recv INTEGER,
                process_count INTEGER,
                uptime REAL
            )
        """)

        # 인덱스 생성
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON system_metrics(timestamp)
        """)

        conn.commit()
        conn.close()

    def collect_metrics(self):
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)

            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100

            # 네트워크 I/O
            network_io = psutil.net_io_counters()
            network_data = {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv
            }

            # 프로세스 수
            process_count = len(psutil.pids())

            # 시스템 업타임
            uptime = time.time() - psutil.boot_time()

            # 메트릭 객체 생성
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage=disk_usage,
                network_io=network_data,
                process_count=process_count,
                uptime=uptime
            )

            # 데이터베이스에 저장
            self.save_metrics(metrics)

            # 시그널 발송
            self.metrics_collected.emit(metrics)

        except Exception as e:
            logging.error(f"메트릭 수집 오류: {e}")

    def save_metrics(self, metrics: SystemMetrics):
        """메트릭을 데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO system_metrics
            (timestamp, cpu_percent, memory_percent, disk_usage,
             network_bytes_sent, network_bytes_recv, process_count, uptime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics.timestamp,
            metrics.cpu_percent,
            metrics.memory_percent,
            metrics.disk_usage,
            metrics.network_io["bytes_sent"],
            metrics.network_io["bytes_recv"],
            metrics.process_count,
            metrics.uptime
        ))

        conn.commit()
        conn.close()

        # 오래된 데이터 정리 (7일 이상)
        self.cleanup_old_metrics()

    def cleanup_old_metrics(self, days: int = 7):
        """오래된 메트릭 데이터 정리"""
        cutoff_date = datetime.now() - timedelta(days=days)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM system_metrics WHERE timestamp < ?",
            (cutoff_date,)
        )

        conn.commit()
        conn.close()
```

#### 4.2 알림 시스템
```python
from enum import Enum
from typing import Callable, Dict, List
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests

class AlertLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Alert:
    """알림 데이터 클래스"""
    def __init__(self, level: AlertLevel, title: str, message: str, component: str = "system"):
        self.level = level
        self.title = title
        self.message = message
        self.component = component
        self.timestamp = datetime.now()

class AlertManager(QObject):
    """알림 관리자"""

    alert_triggered = Signal(Alert)

    def __init__(self):
        super().__init__()
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_usage": 90.0,
            "response_time": 5.0  # 초
        }

        self.notification_channels = {
            "email": self.send_email_notification,
            "slack": self.send_slack_notification,
            "webhook": self.send_webhook_notification
        }

        self.alert_history = []

    def check_thresholds(self, metrics: SystemMetrics):
        """임계값 확인 및 알림 발송"""
        alerts = []

        # CPU 사용률 확인
        if metrics.cpu_percent > self.thresholds["cpu_percent"]:
            alerts.append(Alert(
                AlertLevel.WARNING,
                "High CPU Usage",
                f"CPU 사용률이 {metrics.cpu_percent:.1f}%로 임계값을 초과했습니다.",
                "cpu"
            ))

        # 메모리 사용률 확인
        if metrics.memory_percent > self.thresholds["memory_percent"]:
            alerts.append(Alert(
                AlertLevel.WARNING,
                "High Memory Usage",
                f"메모리 사용률이 {metrics.memory_percent:.1f}%로 임계값을 초과했습니다.",
                "memory"
            ))

        # 디스크 사용률 확인
        if metrics.disk_usage > self.thresholds["disk_usage"]:
            alerts.append(Alert(
                AlertLevel.ERROR,
                "High Disk Usage",
                f"디스크 사용률이 {metrics.disk_usage:.1f}%로 임계값을 초과했습니다.",
                "disk"
            ))

        # 알림 발송
        for alert in alerts:
            self.send_alert(alert)

    def send_alert(self, alert: Alert):
        """알림 발송"""
        # 중복 알림 방지 (5분 내 동일 컴포넌트 알림)
        if self.is_duplicate_alert(alert):
            return

        # 알림 이력에 추가
        self.alert_history.append(alert)

        # 시그널 발송
        self.alert_triggered.emit(alert)

        # 외부 채널로 알림 발송
        for channel_name, send_func in self.notification_channels.items():
            try:
                send_func(alert)
            except Exception as e:
                logging.error(f"{channel_name} 알림 발송 실패: {e}")

    def send_email_notification(self, alert: Alert):
        """이메일 알림 발송"""
        smtp_server = "smtp.company.com"
        smtp_port = 587
        username = "alert@company.com"
        password = "password"
        recipients = ["admin@company.com", "ops@company.com"]

        msg = MimeMultipart()
        msg['From'] = username
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"[{alert.level.value}] {alert.title}"

        body = f"""
        알림 레벨: {alert.level.value}
        컴포넌트: {alert.component}
        시간: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

        메시지:
        {alert.message}

        --
        Semiconductor HMI 모니터링 시스템
        """

        msg.attach(MimeText(body, 'plain', 'utf-8'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()

    def send_slack_notification(self, alert: Alert):
        """Slack 알림 발송"""
        webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

        color_map = {
            AlertLevel.INFO: "good",
            AlertLevel.WARNING: "warning",
            AlertLevel.ERROR: "danger",
            AlertLevel.CRITICAL: "danger"
        }

        payload = {
            "attachments": [{
                "color": color_map.get(alert.level, "warning"),
                "title": alert.title,
                "text": alert.message,
                "fields": [
                    {"title": "Level", "value": alert.level.value, "short": True},
                    {"title": "Component", "value": alert.component, "short": True},
                    {"title": "Time", "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'), "short": False}
                ],
                "footer": "Semiconductor HMI Monitoring",
                "ts": int(alert.timestamp.timestamp())
            }]
        }

        requests.post(webhook_url, json=payload)

# 사용 예제
if __name__ == "__main__":
    # 메트릭 수집기 초기화
    metrics_collector = MetricsCollector(30)

    # 알림 관리자 초기화
    alert_manager = AlertManager()

    # 메트릭과 알림 연결
    metrics_collector.metrics_collected.connect(alert_manager.check_thresholds)

    print("모니터링 시스템이 시작되었습니다...")
```

---

## 💼 **Hands-on 프로젝트 (45분) - 완전 자동화된 배포 파이프라인**

### 최종 프로젝트: 엔드투엔드 배포 파이프라인 구축

#### 4.1 GitHub Actions CI/CD 파이프라인
```yaml
