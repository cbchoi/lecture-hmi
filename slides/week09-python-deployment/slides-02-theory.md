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
