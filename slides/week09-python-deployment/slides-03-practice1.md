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
