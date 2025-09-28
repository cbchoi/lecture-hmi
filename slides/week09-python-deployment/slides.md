# Week 9: Python PySide6 배포 및 운영 최적화

## 🎯 **이론 강의 (45분) - 배포 전략 및 운영 아키텍처**

### 1. 산업용 소프트웨어 배포 전략

#### 1.1 반도체 장비 환경의 특수성
```python
"""
반도체 장비 배포 환경 특성:
- 폐쇄형 네트워크 (에어갭 환경)
- 24/7 연속 운영 (다운타임 최소화)
- 엄격한 변경 관리 (CFR 21 Part 11 준수)
- 멀티 플랫폼 (Windows/Linux 혼재)
- 실시간 성능 요구사항
"""

# 배포 전략 설계 원칙
DEPLOYMENT_PRINCIPLES = {
    "reliability": "99.99% 가용성 보장",
    "security": "제로 트러스트 보안 모델",
    "maintainability": "원격 업데이트 지원",
    "scalability": "수백 대 동시 배포",
    "compliance": "규제 준수 추적성"
}
```

#### 1.2 패키징 전략 비교
```python
# PyInstaller vs cx_Freeze vs Nuitka 비교 분석
packaging_comparison = {
    "PyInstaller": {
        "pros": ["간편한 사용", "광범위한 라이브러리 지원", "크로스 플랫폼"],
        "cons": ["큰 실행 파일", "느린 시작 시간"],
        "use_case": "빠른 프로토타이핑, 일반적인 배포"
    },
    "cx_Freeze": {
        "pros": ["작은 실행 파일", "MSI 패키지 지원"],
        "cons": ["복잡한 설정", "제한적인 라이브러리 지원"],
        "use_case": "Windows 전용, 크기 최적화 필요"
    },
    "Nuitka": {
        "pros": ["최고 성능", "진정한 컴파일"],
        "cons": ["긴 빌드 시간", "복잡한 디버깅"],
        "use_case": "성능 크리티컬, 대규모 애플리케이션"
    }
}
```

### 2. 컨테이너 기반 배포 아키텍처

#### 2.1 Docker 멀티 스테이지 빌드
```dockerfile
# 최적화된 Python PySide6 Docker 이미지
FROM python:3.11-slim as builder

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    qt6-base-dev \
    libgl1-mesa-glx \
    libxcb-xinerama0 \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 빌드
COPY . /app
WORKDIR /app
RUN python -m PyInstaller --onefile --windowed main.py

# 런타임 이미지
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    libqt6core6 \
    libqt6gui6 \
    libqt6widgets6 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/dist/main /usr/local/bin/hmi-app
EXPOSE 8080
CMD ["/usr/local/bin/hmi-app"]
```

#### 2.2 Kubernetes 배포 매니페스트
```yaml
# HMI 애플리케이션 Kubernetes 배포
apiVersion: apps/v1
kind: Deployment
metadata:
  name: semiconductor-hmi
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: semiconductor-hmi
  template:
    metadata:
      labels:
        app: semiconductor-hmi
    spec:
      containers:
      - name: hmi-app
        image: semiconductor-hmi:v1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: semiconductor-hmi-service
spec:
  selector:
    app: semiconductor-hmi
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

### 3. 자동 업데이트 시스템 설계

#### 3.1 델타 패치 업데이트 아키텍처
```python
import hashlib
import requests
from pathlib import Path
from typing import Dict, List

class DeltaUpdateManager:
    """델타 패치 기반 자동 업데이트 시스템"""

    def __init__(self, update_server_url: str, app_version: str):
        self.update_server = update_server_url
        self.current_version = app_version
        self.backup_dir = Path("./backup")

    def check_for_updates(self) -> Dict:
        """서버에서 업데이트 확인"""
        response = requests.get(
            f"{self.update_server}/api/updates",
            params={"current_version": self.current_version}
        )
        return response.json()

    def calculate_file_hash(self, filepath: Path) -> str:
        """파일 해시 계산 (무결성 검증)"""
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def apply_delta_patch(self, patch_info: Dict) -> bool:
        """델타 패치 적용"""
        try:
            # 백업 생성
            self.create_backup()

            # 패치 다운로드
            patch_data = self.download_patch(patch_info['patch_url'])

            # 무결성 검증
            if not self.verify_patch_integrity(patch_data, patch_info['checksum']):
                raise ValueError("패치 무결성 검증 실패")

            # 패치 적용
            for file_change in patch_info['changes']:
                self.apply_file_change(file_change)

            # 검증
            if self.verify_update():
                self.cleanup_backup()
                return True
            else:
                self.rollback()
                return False

        except Exception as e:
            self.rollback()
            raise e

    def rollback(self):
        """업데이트 실패 시 롤백"""
        if self.backup_dir.exists():
            # 백업에서 복원
            for backup_file in self.backup_dir.glob("**/*"):
                if backup_file.is_file():
                    target = Path(str(backup_file).replace(str(self.backup_dir), "."))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    backup_file.replace(target)
```

### 4. 보안 및 인증 시스템

#### 4.1 RBAC 기반 접근 제어
```python
from enum import Enum
from typing import Set, Dict
import ldap3

class Permission(Enum):
    """권한 정의"""
    VIEW_EQUIPMENT = "view_equipment"
    CONTROL_EQUIPMENT = "control_equipment"
    MODIFY_SETTINGS = "modify_settings"
    VIEW_LOGS = "view_logs"
    ADMIN_ACCESS = "admin_access"

class Role:
    """역할 정의"""
    def __init__(self, name: str, permissions: Set[Permission]):
        self.name = name
        self.permissions = permissions

# 기본 역할 정의
ROLES = {
    "operator": Role("Operator", {
        Permission.VIEW_EQUIPMENT,
        Permission.VIEW_LOGS
    }),
    "engineer": Role("Engineer", {
        Permission.VIEW_EQUIPMENT,
        Permission.CONTROL_EQUIPMENT,
        Permission.VIEW_LOGS
    }),
    "admin": Role("Administrator", {
        Permission.VIEW_EQUIPMENT,
        Permission.CONTROL_EQUIPMENT,
        Permission.MODIFY_SETTINGS,
        Permission.VIEW_LOGS,
        Permission.ADMIN_ACCESS
    })
}

class LDAPAuthenticator:
    """LDAP 기반 인증 시스템"""

    def __init__(self, ldap_server: str, base_dn: str):
        self.server = ldap3.Server(ldap_server)
        self.base_dn = base_dn

    def authenticate(self, username: str, password: str) -> Dict:
        """사용자 인증 및 권한 조회"""
        try:
            user_dn = f"uid={username},{self.base_dn}"
            conn = ldap3.Connection(self.server, user_dn, password)

            if conn.bind():
                # 사용자 정보 조회
                conn.search(
                    user_dn,
                    '(objectClass=person)',
                    attributes=['cn', 'memberOf']
                )

                user_info = conn.entries[0]
                groups = [group.split(',')[0].split('=')[1]
                         for group in user_info.memberOf.values]

                # 그룹 기반 역할 매핑
                role = self.map_groups_to_role(groups)

                return {
                    "authenticated": True,
                    "username": username,
                    "display_name": str(user_info.cn),
                    "role": role,
                    "permissions": list(ROLES[role].permissions)
                }
            else:
                return {"authenticated": False}

        except Exception as e:
            return {"authenticated": False, "error": str(e)}
```

---

## 🔧 **기초 실습 (45분) - 패키징 및 기본 배포**

### 실습 1: PyInstaller를 활용한 실행 파일 생성

#### 1.1 PyInstaller 설정 파일 작성
```python
# build_config.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# 애플리케이션 경로 설정
app_path = Path.cwd()
src_path = app_path / "src"

a = Analysis(
    [str(src_path / "main.py")],
    pathex=[str(app_path)],
    binaries=[],
    datas=[
        (str(src_path / "ui" / "*.ui"), "ui"),
        (str(src_path / "resources" / "*"), "resources"),
        (str(src_path / "config" / "*.json"), "config"),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'PySide6.QtOpenGL',
        'PyQt5.sip',
        'numpy',
        'sqlite3'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'tkinter',
        'test',
        'unittest'
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SemiconductorHMI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # UPX 압축 사용
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 애플리케이션
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(src_path / "resources" / "icon.ico")
)
```

#### 1.2 빌드 자동화 스크립트
```python
#!/usr/bin/env python3
"""
빌드 자동화 스크립트
크로스 플랫폼 빌드 지원
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, List

class BuildManager:
    """빌드 관리자"""

    def __init__(self):
        self.platform = platform.system().lower()
        self.arch = platform.machine().lower()
        self.build_dir = Path("./build")
        self.dist_dir = Path("./dist")

    def clean_build(self):
        """이전 빌드 정리"""
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"정리됨: {dir_path}")

    def install_dependencies(self):
        """의존성 설치"""
        requirements = [
            "PySide6>=6.5.0",
            "PyInstaller>=5.10.0",
            "numpy>=1.24.0",
            "requests>=2.31.0",
            "cryptography>=3.4.8"
        ]

        for req in requirements:
            subprocess.run([sys.executable, "-m", "pip", "install", req])

    def build_executable(self, spec_file: str = "build_config.spec"):
        """실행 파일 빌드"""
        print(f"빌드 시작: {self.platform}-{self.arch}")

        # PyInstaller 실행
        cmd = [
            "pyinstaller",
            "--clean",
            "--noconfirm",
            spec_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("빌드 성공!")
            self.post_process()
        else:
            print(f"빌드 실패: {result.stderr}")
            sys.exit(1)

    def post_process(self):
        """빌드 후 처리"""
        # 실행 파일 이름 플랫폼별 수정
        exe_name = "SemiconductorHMI"
        if self.platform == "windows":
            exe_name += ".exe"

        exe_path = self.dist_dir / exe_name
        if exe_path.exists():
            # 플랫폼별 배포 디렉토리 생성
            deploy_dir = Path(f"./deploy/{self.platform}-{self.arch}")
            deploy_dir.mkdir(parents=True, exist_ok=True)

            # 실행 파일 복사
            shutil.copy2(exe_path, deploy_dir / exe_name)

            # 추가 파일 복사 (설정, 라이선스 등)
            for file_name in ["config.json", "LICENSE.txt", "README.md"]:
                src_file = Path(file_name)
                if src_file.exists():
                    shutil.copy2(src_file, deploy_dir / file_name)

            print(f"배포 패키지 생성: {deploy_dir}")

    def create_installer(self):
        """설치 패키지 생성"""
        if self.platform == "windows":
            self.create_msi_installer()
        elif self.platform == "linux":
            self.create_deb_package()
        elif self.platform == "darwin":
            self.create_dmg_package()

    def create_msi_installer(self):
        """Windows MSI 설치 패키지 생성"""
        wix_script = """
        <?xml version="1.0" encoding="UTF-8"?>
        <Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
          <Product Id="*" Name="Semiconductor HMI" Language="1033"
                   Version="1.0.0" Manufacturer="YourCompany"
                   UpgradeCode="12345678-1234-1234-1234-123456789012">
            <Package InstallerVersion="200" Compressed="yes" />

            <Directory Id="TARGETDIR" Name="SourceDir">
              <Directory Id="ProgramFilesFolder">
                <Directory Id="INSTALLFOLDER" Name="SemiconductorHMI" />
              </Directory>
            </Directory>

            <Component Id="MainExecutable" Guid="*">
              <File Id="MainExe" Source="dist/SemiconductorHMI.exe"
                    KeyPath="yes" Checksum="yes"/>
            </Component>

            <Feature Id="ProductFeature" Title="Main Feature" Level="1">
              <ComponentRef Id="MainExecutable" />
            </Feature>
          </Product>
        </Wix>
        """

        # WiX 스크립트 저장 및 컴파일
        with open("installer.wxs", "w") as f:
            f.write(wix_script)

        subprocess.run(["candle", "installer.wxs"])
        subprocess.run(["light", "-out", "SemiconductorHMI.msi", "installer.wixobj"])

if __name__ == "__main__":
    builder = BuildManager()

    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        builder.clean_build()
    else:
        builder.install_dependencies()
        builder.build_executable()
        builder.create_installer()
```

### 실습 2: Docker 컨테이너화

#### 2.1 Docker Compose 설정
```yaml
# docker-compose.yml
version: '3.8'

services:
  # HMI 애플리케이션
  hmi-app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://hmi_user:password@postgres:5432/hmi_db
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config:ro
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # PostgreSQL 데이터베이스
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: hmi_db
      POSTGRES_USER: hmi_user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  # Redis 캐시
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  # Nginx 로드 밸런서
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - hmi-app
    restart: unless-stopped

volumes:
  postgres_data:
```

#### 2.2 Nginx 설정 파일
```nginx
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
# .github/workflows/deploy.yml
name: Semiconductor HMI Deployment Pipeline

on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'

jobs:
  # 코드 품질 검사
  quality-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install flake8 black pylint mypy pytest

    - name: Code formatting check
      run: black --check .

    - name: Linting
      run: flake8 . --max-line-length=88 --extend-ignore=E203

    - name: Type checking
      run: mypy src/

    - name: Security scanning
      run: |
        pip install bandit
        bandit -r src/ -f json -o security-report.json

    - name: Upload security report
      uses: actions/upload-artifact@v3
      with:
        name: security-report
        path: security-report.json

  # 단위 테스트
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install system dependencies (Linux)
      if: matrix.os == 'ubuntu-latest'
      run: |
        sudo apt-get update
        sudo apt-get install -y qt6-base-dev libgl1-mesa-glx

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-qt pytest-cov

    - name: Run tests
      run: |
        pytest tests/ --cov=src/ --cov-report=xml --cov-report=html

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  # 빌드 및 패키징
  build:
    needs: [quality-check, test]
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller

    - name: Build application
      run: |
        python build_script.py

    - name: Create installer (Windows)
      if: matrix.os == 'windows-latest'
      run: |
        # WiX Toolset으로 MSI 생성
        choco install wixtoolset
        candle installer.wxs
        light -out SemiconductorHMI.msi installer.wixobj

    - name: Create installer (macOS)
      if: matrix.os == 'macos-latest'
      run: |
        # DMG 패키지 생성
        hdiutil create -volname "Semiconductor HMI" -srcfolder dist/ -ov -format UDZO SemiconductorHMI.dmg

    - name: Create installer (Linux)
      if: matrix.os == 'ubuntu-latest'
      run: |
        # DEB 패키지 생성
        python setup.py --command-packages=stdeb.command bdist_deb

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: installer-${{ matrix.os }}
        path: |
          *.msi
          *.dmg
          *.deb
          dist/

  # Docker 이미지 빌드
  docker-build:
    needs: [quality-check, test]
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ghcr.io/${{ github.repository }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        platforms: linux/amd64,linux/arm64
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  # 스테이징 배포
  deploy-staging:
    needs: [build, docker-build]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to Kubernetes
      run: |
        # kubectl 설정
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig

        # 네임스페이스 생성
        kubectl create namespace staging --dry-run=client -o yaml | kubectl apply -f -

        # 배포
        envsubst < k8s/deployment.yaml | kubectl apply -f - -n staging

        # 배포 상태 확인
        kubectl rollout status deployment/semiconductor-hmi -n staging --timeout=300s

  # 프로덕션 배포
  deploy-production:
    needs: [build, docker-build]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    environment: production

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to Production
      run: |
        # 프로덕션 배포는 수동 승인 후 진행
        echo "프로덕션 배포 시작..."

        # 블루-그린 배포 전략
        kubectl apply -f k8s/blue-green-deployment.yaml -n production

        # 헬스체크 대기
        kubectl wait --for=condition=available deployment/semiconductor-hmi-green -n production --timeout=600s

        # 트래픽 전환
        kubectl patch service semiconductor-hmi-service -n production -p '{"spec":{"selector":{"version":"green"}}}'

        # 이전 버전 정리 (5분 후)
        sleep 300
        kubectl delete deployment semiconductor-hmi-blue -n production --ignore-not-found

  # 릴리스 노트 생성
  release:
    needs: [deploy-production]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')

    steps:
    - uses: actions/checkout@v3

    - name: Generate Release Notes
      uses: actions/github-script@v6
      with:
        script: |
          const tag = context.ref.replace('refs/tags/', '');
          const release = await github.rest.repos.createRelease({
            owner: context.repo.owner,
            repo: context.repo.repo,
            tag_name: tag,
            name: `Release ${tag}`,
            generate_release_notes: true
          });

          // 빌드 아티팩트 첨부
          const artifacts = await github.rest.actions.listWorkflowRunArtifacts({
            owner: context.repo.owner,
            repo: context.repo.repo,
            run_id: context.runId
          });

          console.log(`Created release: ${release.data.html_url}`);
```

#### 4.2 배포 상태 모니터링 대시보드
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import json
from typing import List, Dict
import psutil
import subprocess
from datetime import datetime

app = FastAPI(title="Deployment Dashboard")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class DeploymentMonitor:
    """배포 상태 모니터링"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.deployment_status = {
            "staging": {"status": "running", "version": "v1.2.3", "instances": 3},
            "production": {"status": "running", "version": "v1.2.2", "instances": 5}
        }

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

        # 초기 상태 전송
        await websocket.send_text(json.dumps({
            "type": "status_update",
            "data": self.deployment_status
        }))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_update(self, message: Dict):
        """모든 연결된 클라이언트에게 업데이트 브로드캐스트"""
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # 연결이 끊어진 경우 제거
                self.active_connections.remove(connection)

    async def check_deployment_health(self):
        """배포 상태 헬스체크"""
        while True:
            try:
                # Kubernetes 클러스터 상태 확인
                result = subprocess.run(
                    ["kubectl", "get", "deployments", "-o", "json"],
                    capture_output=True, text=True
                )

                if result.returncode == 0:
                    deployments = json.loads(result.stdout)

                    for deployment in deployments.get("items", []):
                        name = deployment["metadata"]["name"]
                        namespace = deployment["metadata"]["namespace"]

                        if "semiconductor-hmi" in name:
                            ready_replicas = deployment["status"].get("readyReplicas", 0)
                            total_replicas = deployment["spec"]["replicas"]

                            status = "running" if ready_replicas == total_replicas else "degraded"

                            if namespace in self.deployment_status:
                                self.deployment_status[namespace].update({
                                    "status": status,
                                    "instances": ready_replicas,
                                    "last_updated": datetime.now().isoformat()
                                })

                    # 클라이언트들에게 업데이트 브로드캐스트
                    await self.broadcast_update({
                        "type": "health_update",
                        "data": self.deployment_status
                    })

            except Exception as e:
                print(f"헬스체크 오류: {e}")

            await asyncio.sleep(30)  # 30초마다 체크

monitor = DeploymentMonitor()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await monitor.connect(websocket)
    try:
        while True:
            # 클라이언트로부터 메시지 대기
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "trigger_deployment":
                # 배포 트리거 처리
                await handle_deployment_trigger(message["data"])
            elif message["type"] == "rollback_request":
                # 롤백 요청 처리
                await handle_rollback_request(message["data"])

    except WebSocketDisconnect:
        monitor.disconnect(websocket)

async def handle_deployment_trigger(deployment_data: Dict):
    """배포 트리거 처리"""
    environment = deployment_data["environment"]
    version = deployment_data["version"]

    # 배포 상태 업데이트
    monitor.deployment_status[environment]["status"] = "deploying"

    await monitor.broadcast_update({
        "type": "deployment_started",
        "data": {
            "environment": environment,
            "version": version,
            "timestamp": datetime.now().isoformat()
        }
    })

    # 실제 배포 실행 (백그라운드 태스크)
    asyncio.create_task(execute_deployment(environment, version))

async def execute_deployment(environment: str, version: str):
    """실제 배포 실행"""
    try:
        # Kubernetes 배포 업데이트
        result = subprocess.run([
            "kubectl", "set", "image",
            f"deployment/semiconductor-hmi",
            f"hmi-app=ghcr.io/company/semiconductor-hmi:{version}",
            "-n", environment
        ], capture_output=True, text=True)

        if result.returncode == 0:
            # 배포 완료 대기
            await asyncio.sleep(60)  # 실제로는 kubectl rollout status 사용

            monitor.deployment_status[environment].update({
                "status": "running",
                "version": version,
                "last_deployed": datetime.now().isoformat()
            })

            await monitor.broadcast_update({
                "type": "deployment_completed",
                "data": {
                    "environment": environment,
                    "version": version,
                    "status": "success"
                }
            })
        else:
            monitor.deployment_status[environment]["status"] = "failed"

            await monitor.broadcast_update({
                "type": "deployment_failed",
                "data": {
                    "environment": environment,
                    "error": result.stderr
                }
            })

    except Exception as e:
        await monitor.broadcast_update({
            "type": "deployment_error",
            "data": {"error": str(e)}
        })

# 대시보드 헬스체크 시작
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor.check_deployment_health())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 4.3 대시보드 웹 인터페이스
```html
<!-- templates/dashboard.html -->
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Semiconductor HMI Deployment Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }

        .dashboard {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        .environment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .environment-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }

        .environment-card:hover {
            transform: translateY(-2px);
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-running { background-color: #4CAF50; }
        .status-deploying { background-color: #FF9800; animation: pulse 1s infinite; }
        .status-failed { background-color: #F44336; }
        .status-degraded { background-color: #FF5722; }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .deploy-button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }

        .rollback-button {
            background: #FF5722;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }

        .metric-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .log-container {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
        }

        .log-entry {
            margin-bottom: 5px;
        }

        .log-timestamp {
            color: #608b4e;
        }

        .log-level-info { color: #4ec9b0; }
        .log-level-warning { color: #dcdcaa; }
        .log-level-error { color: #f44747; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🏭 Semiconductor HMI Deployment Dashboard</h1>
            <p>실시간 배포 상태 모니터링 및 관리</p>
        </div>

        <div class="environment-grid">
            <div class="environment-card" id="staging-card">
                <h2>🧪 Staging Environment</h2>
                <p><span class="status-indicator status-running" id="staging-indicator"></span>
                   <span id="staging-status">Loading...</span></p>
                <p><strong>Version:</strong> <span id="staging-version">-</span></p>
                <p><strong>Instances:</strong> <span id="staging-instances">-</span></p>
                <p><strong>Last Updated:</strong> <span id="staging-updated">-</span></p>
                <button class="deploy-button" onclick="triggerDeployment('staging')">Deploy to Staging</button>
                <button class="rollback-button" onclick="triggerRollback('staging')">Rollback</button>
            </div>

            <div class="environment-card" id="production-card">
                <h2>🚀 Production Environment</h2>
                <p><span class="status-indicator status-running" id="production-indicator"></span>
                   <span id="production-status">Loading...</span></p>
                <p><strong>Version:</strong> <span id="production-version">-</span></p>
                <p><strong>Instances:</strong> <span id="production-instances">-</span></p>
                <p><strong>Last Updated:</strong> <span id="production-updated">-</span></p>
                <button class="deploy-button" onclick="triggerDeployment('production')">Deploy to Production</button>
                <button class="rollback-button" onclick="triggerRollback('production')">Rollback</button>
            </div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <h3>📊 CPU Usage</h3>
                <div id="cpu-chart"></div>
            </div>
            <div class="metric-card">
                <h3>💾 Memory Usage</h3>
                <div id="memory-chart"></div>
            </div>
            <div class="metric-card">
                <h3>🌐 Network I/O</h3>
                <div id="network-chart"></div>
            </div>
            <div class="metric-card">
                <h3>⚡ Response Time</h3>
                <div id="response-chart"></div>
            </div>
        </div>

        <div class="log-container" id="log-container">
            <h3>📝 Deployment Logs</h3>
            <div id="logs"></div>
        </div>
    </div>

    <script>
        class DashboardClient {
            constructor() {
                this.ws = null;
                this.logs = [];
                this.connect();
            }

            connect() {
                this.ws = new WebSocket(`ws://${window.location.host}/ws`);

                this.ws.onopen = () => {
                    this.addLog('info', 'Dashboard connected');
                };

                this.ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                };

                this.ws.onclose = () => {
                    this.addLog('warning', 'Connection lost, reconnecting...');
                    setTimeout(() => this.connect(), 5000);
                };

                this.ws.onerror = (error) => {
                    this.addLog('error', `Connection error: ${error}`);
                };
            }

            handleMessage(message) {
                switch (message.type) {
                    case 'status_update':
                        this.updateEnvironmentStatus(message.data);
                        break;
                    case 'health_update':
                        this.updateEnvironmentStatus(message.data);
                        break;
                    case 'deployment_started':
                        this.addLog('info', `Deployment started: ${message.data.environment} -> ${message.data.version}`);
                        break;
                    case 'deployment_completed':
                        this.addLog('info', `Deployment completed: ${message.data.environment} -> ${message.data.version}`);
                        break;
                    case 'deployment_failed':
                        this.addLog('error', `Deployment failed: ${message.data.environment} - ${message.data.error}`);
                        break;
                }
            }

            updateEnvironmentStatus(data) {
                Object.keys(data).forEach(env => {
                    const envData = data[env];

                    document.getElementById(`${env}-status`).textContent = envData.status;
                    document.getElementById(`${env}-version`).textContent = envData.version;
                    document.getElementById(`${env}-instances`).textContent = envData.instances;
                    document.getElementById(`${env}-updated`).textContent =
                        envData.last_updated ? new Date(envData.last_updated).toLocaleString() : '-';

                    const indicator = document.getElementById(`${env}-indicator`);
                    indicator.className = `status-indicator status-${envData.status}`;
                });
            }

            addLog(level, message) {
                const timestamp = new Date().toLocaleTimeString();
                const logEntry = document.createElement('div');
                logEntry.className = 'log-entry';
                logEntry.innerHTML =
                    `<span class="log-timestamp">[${timestamp}]</span> ` +
                    `<span class="log-level-${level}">[${level.toUpperCase()}]</span> ${message}`;

                const logsContainer = document.getElementById('logs');
                logsContainer.appendChild(logEntry);
                logsContainer.scrollTop = logsContainer.scrollHeight;

                // 로그 제한 (최대 100개)
                while (logsContainer.children.length > 100) {
                    logsContainer.removeChild(logsContainer.firstChild);
                }
            }

            triggerDeployment(environment) {
                const version = prompt(`Enter version to deploy to ${environment}:`);
                if (version) {
                    this.ws.send(JSON.stringify({
                        type: 'trigger_deployment',
                        data: { environment, version }
                    }));
                }
            }

            triggerRollback(environment) {
                if (confirm(`Are you sure you want to rollback ${environment}?`)) {
                    this.ws.send(JSON.stringify({
                        type: 'rollback_request',
                        data: { environment }
                    }));
                }
            }
        }

        // 전역 함수들
        function triggerDeployment(environment) {
            dashboard.triggerDeployment(environment);
        }

        function triggerRollback(environment) {
            dashboard.triggerRollback(environment);
        }

        // 대시보드 초기화
        const dashboard = new DashboardClient();
    </script>
</body>
</html>
```

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "\uae30\uc874 \ud30c\uc77c \uad6c\uc870 \ubd84\uc11d", "status": "completed", "activeForm": "\uae30\uc874 \ud30c\uc77c \uad6c\uc870 \ubd84\uc11d \uc911"}, {"content": "1\uc8fc\ucc28 HCI/HMI \uc774\ub860 \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "1\uc8fc\ucc28 HCI/HMI \uc774\ub860 \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "2\uc8fc\ucc28 C# WPF \uae30\ucd08 \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "2\uc8fc\ucc28 C# WPF \uae30\ucd08 \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "3\uc8fc\ucc28 C# \uc2e4\uc2dc\uac04 \ub370\uc774\ud130 \ucc98\ub9ac \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "3\uc8fc\ucc28 C# \uc2e4\uc2dc\uac04 \ub370\uc774\ud130 \ucc98\ub9ac \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "4\uc8fc\ucc28 C# \uace0\uae09 UI/UX \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "4\uc8fc\ucc28 C# \uace0\uae09 UI/UX \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "5\uc8fc\ucc28 C# \ud14c\uc2a4\ud2b8/\ubc30\ud3ec \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "5\uc8fc\ucc28 C# \ud14c\uc2a4\ud2b8/\ubc30\ud3ec \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "6\uc8fc\ucc28 Python PySide6 \uae30\ucd08 \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "6\uc8fc\ucc28 Python PySide6 \uae30\ucd08 \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "7\uc8fc\ucc28 Python PySide6 \uc2e4\uc2dc\uac04 \ub370\uc774\ud130 \ucc98\ub9ac \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "7\uc8fc\ucc28 Python PySide6 \uc2e4\uc2dc\uac04 \ub370\uc774\ud130 \ucc98\ub9ac \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "8\uc8fc\ucc28 Python PySide6 \uace0\uae09 \uae30\ub2a5 \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "8\uc8fc\ucc28 Python PySide6 \uace0\uae09 \uae30\ub2a5 \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "9\uc8fc\ucc28 Python PySide6 \ubc30\ud3ec \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "completed", "activeForm": "9\uc8fc\ucc28 Python PySide6 \ubc30\ud3ec \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "10-13\uc8fc\ucc28 ImGUI C++ \uac15\uc758\uc790\ub8cc \uc81c\uc791", "status": "in_progress", "activeForm": "10-13\uc8fc\ucc28 ImGUI C++ \uac15\uc758\uc790\ub8cc \uc81c\uc791 \uc911"}, {"content": "acceptance \uae30\uc900\uc73c\ub85c revision \uc218\ud589", "status": "pending", "activeForm": "acceptance \uae30\uc900\uc73c\ub85c revision \uc218\ud589 \uc911"}]