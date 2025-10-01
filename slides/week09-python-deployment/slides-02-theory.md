---
layout: cover
---

# Week 09 - Python 배포 및 패키징
## 이론 강의 (120분)

반도체 HMI 애플리케이션의 프로젝트 구조, 설정 관리, 배포 전략

---

# 1. Python 패키지 구조 패턴

## 1.1 패키지 구조 기본

<div class="grid grid-cols-2 gap-8">
<div>

```python
# 반도체 HMI 프로젝트 구조
semiconductor_hmi/
├── setup.py              # 패키지 설정 (레거시)
├── pyproject.toml        # 현대적 패키지 설정
├── README.md
├── requirements.txt      # 운영 의존성
├── requirements-dev.txt  # 개발 의존성
├── src/
│   └── semiconductor_hmi/
│       ├── __init__.py
│       ├── __main__.py   # python -m 진입점
│       ├── core/
│       │   ├── __init__.py
│       │   ├── equipment.py
│       │   └── recipe.py
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py
│       │   └── widgets/
│       ├── data/
│       │   └── __init__.py
│       └── utils/
│           └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── test_equipment.py
│   └── test_recipe.py
└── docs/
    └── conf.py
```

</div>
<div>

**패키지 구조 설계 원칙**:

1. **src/ 레이아웃** (권장)
   - 패키지를 `src/` 디렉토리 아래 배치
   - 테스트가 설치된 패키지만 사용하도록 강제
   - Import 문제 방지

2. **__init__.py 역할**
   - 디렉토리를 Python 패키지로 인식
   - 패키지 레벨 import 정의
   - 버전 정보, 공개 API 선언

3. **__main__.py 용도**
   - `python -m package_name` 실행 지원
   - CLI 애플리케이션의 진입점
   - 스크립트와 모듈 분리

**반도체 HMI 적용**:
- 장비 제어, UI, 데이터 처리를 모듈로 분리
- 테스트 격리 및 독립 실행 보장
- 배포 시 소스와 테스트 분리

</div>
</div>

---

## 1.2 pyproject.toml 현대적 패키지 설정

<div class="grid grid-cols-2 gap-8">
<div>

```toml
# pyproject.toml - PEP 517/518 표준
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "semiconductor-hmi"
version = "1.0.0"
description = "Semiconductor Equipment HMI System"
authors = [
    {name = "Your Name", email = "you@company.com"}
]
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Manufacturing",
    "Topic :: Scientific/Engineering",
    "Programming Language :: Python :: 3.9",
]

dependencies = [
    "PySide6>=6.5.0",
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "pyserial>=3.5",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-qt>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
]
docs = [
    "sphinx>=5.0",
    "sphinx-rtd-theme>=1.0",
]

[project.scripts]
semiconductor-hmi = "semiconductor_hmi.__main__:main"
hmi-config = "semiconductor_hmi.cli:config_command"

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 88
target-version = ['py39']

[tool.ruff]
line-length = 88
select = ["E", "F", "W", "I"]
ignore = ["E501"]
```

</div>
<div>

**pyproject.toml 구조 설명**:

1. **[build-system]**
   - 빌드 도구 지정 (setuptools, poetry, flit 등)
   - 빌드 의존성 정의
   - PEP 517 표준 준수

2. **[project]**
   - 패키지 메타데이터 (이름, 버전, 설명)
   - 의존성 관리 (dependencies)
   - 선택적 의존성 (optional-dependencies)
   - Python 버전 요구사항

3. **[project.scripts]**
   - CLI 명령어 등록
   - Entry point 정의
   - 설치 후 `semiconductor-hmi` 명령 사용 가능

4. **[tool.*]**
   - 도구별 설정 (black, ruff, pytest 등)
   - 프로젝트 전체에 일관된 설정 적용

**setup.py vs pyproject.toml**:
- `setup.py`: 레거시, 동적 설정, 복잡한 빌드
- `pyproject.toml`: 현대적, 선언적 설정, 표준화 (권장)

**반도체 HMI 적용**:
- 운영 환경: `pip install semiconductor-hmi`
- 개발 환경: `pip install -e ".[dev]"`
- CLI 명령: `semiconductor-hmi --config config.yaml`

</div>
</div>

---

## 1.3 __init__.py 패키지 초기화

<div class="grid grid-cols-2 gap-8">
<div>

```python
# src/semiconductor_hmi/__init__.py
"""
Semiconductor Equipment HMI System

공개 API를 정의하고 패키지 버전 관리
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = [
    # Core 모듈
    "Equipment",
    "Recipe",
    "ProcessData",

    # UI 컴포넌트
    "MainWindow",
    "EquipmentWidget",

    # 유틸리티
    "logger",
    "config",
]

# 공개 API import
from .core.equipment import Equipment
from .core.recipe import Recipe
from .data.process_data import ProcessData
from .ui.main_window import MainWindow
from .ui.widgets.equipment_widget import EquipmentWidget
from .utils.logger import logger
from .utils.config import config

# 패키지 레벨 초기화
def init_application(config_path: str = None):
    """
    애플리케이션 초기화

    Args:
        config_path: 설정 파일 경로
    """
    if config_path:
        config.load(config_path)

    logger.info(f"Semiconductor HMI v{__version__} initialized")
```

```python
# src/semiconductor_hmi/__main__.py
"""
CLI 진입점: python -m semiconductor_hmi
"""
import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
```

```python
# src/semiconductor_hmi/cli.py
"""CLI 명령어 구현"""
import argparse
from . import init_application, __version__
from .ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication

def main():
    """메인 CLI 진입점"""
    parser = argparse.ArgumentParser(
        description="Semiconductor Equipment HMI"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--config",
        help="Configuration file path",
        default="config.yaml"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    args = parser.parse_args()

    # 초기화
    init_application(args.config)

    # GUI 실행
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
```

</div>
<div>

**__init__.py 패턴 설명**:

1. **__all__ 변수**
   - 공개 API 명시적 선언
   - `from package import *` 동작 제어
   - 사용자에게 노출할 인터페이스 정의

2. **버전 정보**
   - `__version__`: 패키지 버전
   - Single source of truth (한 곳에서 관리)
   - 런타임에서 버전 확인 가능

3. **공개 API import**
   - 사용자 편의를 위한 import 단순화
   - `from semiconductor_hmi import Equipment` 가능
   - 내부 모듈 구조 감춤 (캡슐화)

**__main__.py 패턴**:
- `python -m semiconductor_hmi` 실행 지원
- 모듈을 스크립트처럼 실행
- CLI 진입점 제공

**CLI 설계 패턴**:
```bash
# 다양한 실행 방법
python -m semiconductor_hmi --config prod.yaml
semiconductor-hmi --debug
hmi-config --show
```

**반도체 HMI 적용**:
- 사용자는 내부 구조를 몰라도 됨
- `import semiconductor_hmi` 한 줄로 모든 기능 접근
- 버전 관리 및 호환성 검증 용이

</div>
</div>

---

# 2. 설정 관리 (Configuration Management)

## 2.1 설정 파일 형식 비교

<div class="grid grid-cols-2 gap-8">
<div>

```python
# 1. INI 형식 (configparser) - 단순 설정
# config.ini
[Equipment]
name = Chamber-A
port = COM3
baudrate = 9600

[Database]
host = localhost
port = 5432
database = semiconductor_db

[Logging]
level = INFO
file = logs/hmi.log
```

```python
# 2. YAML 형식 - 복잡한 계층 구조
# config.yaml
equipment:
  name: Chamber-A
  port: COM3
  baudrate: 9600
  parameters:
    temperature:
      min: 20
      max: 300
      unit: celsius
    pressure:
      min: 0.1
      max: 10.0
      unit: torr

database:
  host: localhost
  port: 5432
  database: semiconductor_db
  pool_size: 10

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  handlers:
    - type: file
      filename: logs/hmi.log
      max_bytes: 10485760
      backup_count: 5
    - type: console
      level: DEBUG
```

```python
# 3. TOML 형식 - pyproject.toml과 일관성
# config.toml
[equipment]
name = "Chamber-A"
port = "COM3"
baudrate = 9600

[equipment.parameters.temperature]
min = 20
max = 300
unit = "celsius"

[database]
host = "localhost"
port = 5432
database = "semiconductor_db"
pool_size = 10

[[logging.handlers]]
type = "file"
filename = "logs/hmi.log"
max_bytes = 10485760

[[logging.handlers]]
type = "console"
level = "DEBUG"
```

</div>
<div>

**설정 형식 비교**:

| 형식 | 장점 | 단점 | 사용 시나리오 |
|------|------|------|---------------|
| **INI** | 단순, 읽기 쉬움, 표준 라이브러리 | 중첩 구조 제한, 타입 제한 | 간단한 키-값 설정 |
| **YAML** | 계층 구조, 가독성 우수, 주석 지원 | 문법 민감 (들여쓰기), 파싱 느림 | 복잡한 설정, DevOps |
| **TOML** | 타입 안전, 명확한 문법, Python 친화적 | 상대적으로 덜 보편적 | pyproject.toml과 일관성 |
| **JSON** | 표준, 언어 중립적, 빠른 파싱 | 주석 없음, 가독성 낮음 | API 데이터, 웹 통신 |

**선택 가이드**:
1. **단순한 키-값**: INI (`configparser`)
2. **복잡한 계층 구조**: YAML (`PyYAML`)
3. **Python 프로젝트**: TOML (`tomli/tomllib`)
4. **API/웹**: JSON (`json`)

**반도체 HMI 권장**:
- 주 설정: **YAML** (복잡한 장비 파라미터)
- 프로젝트 설정: **TOML** (pyproject.toml 일관성)
- 레거시 지원: **INI** (기존 시스템 호환)

</div>
</div>

---

## 2.2 설정 관리 클래스 구현

<div class="grid grid-cols-2 gap-8">
<div>

```python
# config.py - 설정 관리 클래스
import yaml
import os
from pathlib import Path
from typing import Any, Dict
from dataclasses import dataclass

@dataclass
class EquipmentConfig:
    """장비 설정"""
    name: str
    port: str
    baudrate: int
    timeout: float = 1.0

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)

@dataclass
class DatabaseConfig:
    """데이터베이스 설정"""
    host: str
    port: int
    database: str
    username: str = ""
    password: str = ""
    pool_size: int = 5

class ConfigManager:
    """
    설정 관리 싱글톤 클래스

    우선순위:
    1. 환경 변수
    2. 사용자 설정 파일
    3. 기본 설정 파일
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._config: Dict[str, Any] = {}
        self._config_file: Path = None
        self._initialized = True

    def load(self, config_path: str = None):
        """
        설정 파일 로드 (우선순위 적용)
        """
        # 1. 기본 설정 로드
        default_config = self._load_default_config()

        # 2. 파일 설정 로드 (우선순위)
        file_configs = []

        # 시스템 설정
        system_config = Path("/etc/semiconductor-hmi/config.yaml")
        if system_config.exists():
            file_configs.append(self._load_yaml(system_config))

        # 사용자 설정
        user_config = Path.home() / ".config" / "semiconductor-hmi" / "config.yaml"
        if user_config.exists():
            file_configs.append(self._load_yaml(user_config))

        # 명시적 설정 파일
        if config_path:
            file_configs.append(self._load_yaml(config_path))

        # 설정 병합 (우선순위: 나중 것이 우선)
        self._config = default_config
        for config in file_configs:
            self._deep_merge(self._config, config)

        # 3. 환경 변수 오버라이드
        self._apply_env_overrides()

    def _load_yaml(self, path: Path) -> Dict:
        """YAML 파일 로드"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def _deep_merge(self, base: Dict, override: Dict):
        """딕셔너리 깊은 병합"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _apply_env_overrides(self):
        """환경 변수로 설정 오버라이드"""
        # HMI_DATABASE_HOST=localhost
        # HMI_EQUIPMENT_PORT=COM4
        prefix = "HMI_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # HMI_DATABASE_HOST -> database.host
                path = key[len(prefix):].lower().split('_')
                self._set_nested(self._config, path, value)

    def _set_nested(self, config: Dict, path: list, value: Any):
        """중첩 딕셔너리 값 설정"""
        for key in path[:-1]:
            config = config.setdefault(key, {})
        config[path[-1]] = value

    def get(self, key: str, default=None) -> Any:
        """
        설정 값 조회 (점 표기법 지원)

        Example:
            config.get('database.host')
            config.get('equipment.parameters.temperature.max')
        """
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    def get_equipment_config(self) -> EquipmentConfig:
        """장비 설정 객체 반환"""
        return EquipmentConfig.from_dict(self._config['equipment'])

    def get_database_config(self) -> DatabaseConfig:
        """데이터베이스 설정 객체 반환"""
        return DatabaseConfig(**self._config['database'])

# 전역 설정 인스턴스
config = ConfigManager()
```

</div>
<div>

**설정 관리 패턴 설명**:

1. **싱글톤 패턴**
   - 애플리케이션 전체에서 하나의 설정 인스턴스
   - `config = ConfigManager()` 여러 번 호출해도 같은 객체
   - 설정 일관성 보장

2. **우선순위 시스템**
   ```
   환경 변수 (최우선)
      ↓
   명시적 파일 (--config)
      ↓
   사용자 설정 (~/.config/)
      ↓
   시스템 설정 (/etc/)
      ↓
   기본 설정 (내장)
   ```

3. **환경 변수 오버라이드**
   - `HMI_DATABASE_HOST=localhost` → `config['database']['host']`
   - 컨테이너/클라우드 환경에서 중요
   - 설정 파일 수정 없이 배포 환경별 설정 가능

4. **타입 안전 설정 객체**
   - `dataclass`로 설정 구조 정의
   - IDE 자동완성 지원
   - 런타임 타입 검증

**사용 예시**:
```python
from semiconductor_hmi.utils.config import config

# 초기화
config.load('config.yaml')

# 값 조회 (점 표기법)
db_host = config.get('database.host', 'localhost')

# 타입 안전 객체
eq_config = config.get_equipment_config()
print(eq_config.baudrate)  # IDE 자동완성
```

**반도체 HMI 적용**:
- 개발/스테이징/운영 환경별 설정 관리
- 민감 정보는 환경 변수로 주입
- 설정 변경 시 재빌드 불필요

</div>
</div>

---

## 2.3 환경 변수 및 시크릿 관리

<div class="grid grid-cols-2 gap-8">
<div>

```python
# secrets.py - 시크릿 관리
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

class SecretManager:
    """
    시크릿 관리 클래스

    우선순위:
    1. 환경 변수
    2. .env 파일
    3. 시크릿 파일 (/run/secrets/)
    """

    def __init__(self, env_file: str = ".env"):
        # .env 파일 로드 (있으면)
        if Path(env_file).exists():
            load_dotenv(env_file)

        # Docker secrets 디렉토리
        self.secrets_dir = Path("/run/secrets")

    def get_secret(self, key: str, default: Optional[str] = None) -> str:
        """
        시크릿 조회 (우선순위 적용)

        Args:
            key: 시크릿 키 (예: DATABASE_PASSWORD)
            default: 기본값

        Returns:
            시크릿 값
        """
        # 1. 환경 변수 확인
        value = os.getenv(key)
        if value:
            return value

        # 2. Docker secrets 파일 확인
        secret_file = self.secrets_dir / key.lower()
        if secret_file.exists():
            return secret_file.read_text().strip()

        # 3. 기본값 반환
        if default is not None:
            return default

        raise ValueError(f"Secret '{key}' not found")

    def get_database_url(self) -> str:
        """데이터베이스 연결 문자열 생성"""
        host = self.get_secret("DATABASE_HOST", "localhost")
        port = self.get_secret("DATABASE_PORT", "5432")
        database = self.get_secret("DATABASE_NAME", "semiconductor_db")
        username = self.get_secret("DATABASE_USER")
        password = self.get_secret("DATABASE_PASSWORD")

        return f"postgresql://{username}:{password}@{host}:{port}/{database}"

# 전역 시크릿 매니저
secrets = SecretManager()
```

```python
# .env 파일 예시 (개발 환경용)
# .env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=semiconductor_db
DATABASE_USER=dev_user
DATABASE_PASSWORD=dev_password

LDAP_SERVER=ldap://localhost:389
LDAP_BASE_DN=dc=company,dc=com

LOG_LEVEL=DEBUG
```

```bash
# 운영 환경: 환경 변수로 주입
export DATABASE_HOST=prod-db.company.com
export DATABASE_PASSWORD=$(vault read -field=password secret/db)

# Docker: secrets로 주입
docker run \
  -e DATABASE_HOST=prod-db.company.com \
  --secret DATABASE_PASSWORD \
  semiconductor-hmi:latest

# Kubernetes: Secret으로 주입
kubectl create secret generic db-credentials \
  --from-literal=password='prod-password'
```

</div>
<div>

**시크릿 관리 모범 사례**:

1. **절대 하지 말아야 할 것**
   - ❌ 코드에 하드코딩
   - ❌ Git에 시크릿 커밋 (.env 파일 주의!)
   - ❌ 로그에 시크릿 출력

2. **개발 환경**
   - `.env` 파일 사용 (python-dotenv)
   - `.gitignore`에 `.env` 추가
   - `.env.example` 제공 (값 없이 구조만)

3. **운영 환경**
   - 환경 변수로 주입
   - Vault/Secret Manager 사용
   - Docker/Kubernetes secrets
   - 암호화된 설정 파일

**python-dotenv 사용**:
```python
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수처럼 사용
db_password = os.getenv('DATABASE_PASSWORD')
```

**.env.example 제공**:
```bash
# .env.example (Git에 커밋)
DATABASE_HOST=
DATABASE_PORT=5432
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=

# .gitignore
.env
*.secret
```

**반도체 HMI 적용**:
- 장비 인증 정보 보호
- LDAP/DB 비밀번호 관리
- 환경별 설정 분리 (dev/staging/prod)
- 보안 감사 추적

**우선순위 예시**:
```python
# 1. 환경 변수 (최우선)
$ export DATABASE_PASSWORD=from_env

# 2. Docker secrets
$ echo "from_docker_secret" > /run/secrets/database_password

# 3. .env 파일
DATABASE_PASSWORD=from_dotenv

# 결과: "from_env" (환경 변수가 최우선)
```

</div>
</div>

---

# 3. CLI 애플리케이션 패턴

## 3.1 argparse 기본 패턴

<div class="grid grid-cols-2 gap-8">
<div>

```python
# cli.py - argparse 기반 CLI
import argparse
import sys
from pathlib import Path
from typing import List
from . import __version__
from .core.equipment import Equipment
from .utils.config import config
from .utils.logger import logger

def create_parser() -> argparse.ArgumentParser:
    """CLI 파서 생성"""
    parser = argparse.ArgumentParser(
        prog="semiconductor-hmi",
        description="Semiconductor Equipment HMI System",
        epilog="For more information, visit https://docs.example.com"
    )

    # 버전 정보
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    # 설정 파일
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default="config.yaml",
        help="Configuration file path (default: config.yaml)"
    )

    # 로그 레벨
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    # 서브커맨드
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands"
    )

    # 1. run 명령
    run_parser = subparsers.add_parser(
        "run",
        help="Run HMI application"
    )
    run_parser.add_argument(
        "--equipment",
        required=True,
        help="Equipment name"
    )
    run_parser.add_argument(
        "--fullscreen",
        action="store_true",
        help="Run in fullscreen mode"
    )

    # 2. config 명령
    config_parser = subparsers.add_parser(
        "config",
        help="Manage configuration"
    )
    config_subparsers = config_parser.add_subparsers(dest="config_action")

    config_subparsers.add_parser("show", help="Show current configuration")
    config_subparsers.add_parser("validate", help="Validate configuration file")

    init_parser = config_subparsers.add_parser("init", help="Initialize configuration")
    init_parser.add_argument("--output", default="config.yaml", help="Output file")

    # 3. recipe 명령
    recipe_parser = subparsers.add_parser(
        "recipe",
        help="Manage recipes"
    )
    recipe_parser.add_argument(
        "action",
        choices=["list", "show", "import", "export"],
        help="Recipe action"
    )
    recipe_parser.add_argument(
        "--recipe-id",
        help="Recipe ID (for show/export)"
    )
    recipe_parser.add_argument(
        "--file",
        type=Path,
        help="File path (for import/export)"
    )

    return parser

def cmd_run(args):
    """HMI 실행 명령"""
    logger.info(f"Starting HMI for equipment: {args.equipment}")

    # 설정 로드
    config.load(args.config)

    # GUI 실행
    from PySide6.QtWidgets import QApplication
    from .ui.main_window import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow(equipment_name=args.equipment)

    if args.fullscreen:
        window.showFullScreen()
    else:
        window.show()

    return app.exec()

def cmd_config_show(args):
    """설정 표시 명령"""
    import yaml
    config.load(args.config)
    print(yaml.dump(config._config, default_flow_style=False))

def cmd_config_validate(args):
    """설정 검증 명령"""
    try:
        config.load(args.config)
        logger.info(f"✓ Configuration file '{args.config}' is valid")
        return 0
    except Exception as e:
        logger.error(f"✗ Configuration validation failed: {e}")
        return 1

def cmd_recipe_list(args):
    """레시피 목록 명령"""
    from .core.recipe import RecipeManager

    config.load(args.config)
    manager = RecipeManager()
    recipes = manager.list_recipes()

    print(f"{'ID':<20} {'Name':<30} {'Version':<10}")
    print("-" * 60)
    for recipe in recipes:
        print(f"{recipe.id:<20} {recipe.name:<30} {recipe.version:<10}")

def main(argv: List[str] = None):
    """CLI 메인 진입점"""
    parser = create_parser()
    args = parser.parse_args(argv)

    # 로거 설정
    logger.setLevel(args.log_level)

    # 명령 라우팅
    if args.command == "run":
        return cmd_run(args)
    elif args.command == "config":
        if args.config_action == "show":
            return cmd_config_show(args)
        elif args.config_action == "validate":
            return cmd_config_validate(args)
    elif args.command == "recipe":
        if args.action == "list":
            return cmd_recipe_list(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

</div>
<div>

**argparse 패턴 설명**:

1. **파서 구조**
   - `ArgumentParser`: 메인 파서 생성
   - `add_argument()`: 옵션/인자 추가
   - `subparsers`: 서브커맨드 지원

2. **인자 유형**
   - **위치 인자** (Positional): `parser.add_argument('name')`
   - **선택 인자** (Optional): `parser.add_argument('--config')`
   - **플래그**: `action="store_true"` (스위치)
   - **선택지**: `choices=['A', 'B']` (제한된 값)

3. **서브커맨드 패턴**
   ```bash
   semiconductor-hmi run --equipment Chamber-A
   semiconductor-hmi config show
   semiconductor-hmi recipe list
   ```
   - Git/Docker 스타일 명령 구조
   - 명령별로 다른 옵션 제공

4. **타입 검증**
   - `type=Path`: 자동 타입 변환
   - `type=int`, `type=float`
   - 커스텀 타입: `type=lambda x: ...`

**명령 라우팅 패턴**:
```python
# 서브커맨드별로 함수 분리
commands = {
    'run': cmd_run,
    'config': cmd_config,
    'recipe': cmd_recipe,
}
return commands[args.command](args)
```

**사용 예시**:
```bash
# 도움말
semiconductor-hmi --help
semiconductor-hmi config --help

# 실행
semiconductor-hmi run --equipment Chamber-A --fullscreen

# 설정 검증
semiconductor-hmi config validate -c config.yaml

# 레시피 관리
semiconductor-hmi recipe list
semiconductor-hmi recipe export --recipe-id RCP001 --file recipe.json
```

**반도체 HMI 적용**:
- 운영자 CLI 도구 제공
- 배포 스크립트 자동화
- 시스템 관리 명령 (status, restart 등)

</div>
</div>

---

## 3.2 Click 프레임워크 (고급 CLI)

<div class="grid grid-cols-2 gap-8">
<div>

```python
# cli_click.py - Click 기반 CLI
import click
from pathlib import Path
from . import __version__
from .utils.config import config
from .utils.logger import logger

# 컨텍스트 객체 (명령 간 공유 데이터)
class Context:
    def __init__(self):
        self.config_file = None
        self.verbose = False

@click.group()
@click.option(
    '--config', '-c',
    type=click.Path(exists=True, path_type=Path),
    default='config.yaml',
    help='Configuration file path'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose output'
)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, config_file, verbose):
    """Semiconductor Equipment HMI System"""
    # 컨텍스트 객체 생성
    ctx.obj = Context()
    ctx.obj.config_file = config_file
    ctx.obj.verbose = verbose

    # 설정 로드
    config.load(config_file)

    if verbose:
        logger.setLevel('DEBUG')

@cli.command()
@click.option('--equipment', required=True, help='Equipment name')
@click.option('--fullscreen', is_flag=True, help='Run in fullscreen mode')
@click.pass_context
def run(ctx, equipment, fullscreen):
    """Run HMI application"""
    click.echo(f"Starting HMI for: {equipment}")

    from PySide6.QtWidgets import QApplication
    from .ui.main_window import MainWindow
    import sys

    app = QApplication(sys.argv)
    window = MainWindow(equipment_name=equipment)

    if fullscreen:
        window.showFullScreen()
    else:
        window.show()

    sys.exit(app.exec())

@cli.group()
def config_cmd():
    """Manage configuration"""
    pass

@config_cmd.command('show')
@click.pass_context
def config_show(ctx):
    """Show current configuration"""
    import yaml
    output = yaml.dump(config._config, default_flow_style=False)
    click.echo(output)

@config_cmd.command('validate')
@click.pass_context
def config_validate(ctx):
    """Validate configuration file"""
    try:
        click.echo(f"✓ Configuration file '{ctx.obj.config_file}' is valid")
    except Exception as e:
        click.echo(f"✗ Validation failed: {e}", err=True)
        raise click.Abort()

@config_cmd.command('init')
@click.option('--output', default='config.yaml', help='Output file path')
@click.confirmation_option(
    prompt='This will create a new configuration file. Continue?'
)
def config_init(output):
    """Initialize configuration file"""
    from .utils.config import create_default_config

    config_data = create_default_config()

    with open(output, 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False)

    click.echo(f"✓ Created configuration file: {output}")

@cli.group()
def recipe():
    """Manage recipes"""
    pass

@recipe.command('list')
def recipe_list():
    """List all recipes"""
    from .core.recipe import RecipeManager

    manager = RecipeManager()
    recipes = manager.list_recipes()

    # Click 테이블 출력
    click.echo(f"{'ID':<20} {'Name':<30} {'Version':<10}")
    click.echo("-" * 60)
    for r in recipes:
        click.echo(f"{r.id:<20} {r.name:<30} {r.version:<10}")

@recipe.command('import')
@click.argument('file', type=click.Path(exists=True, path_type=Path))
@click.option('--validate-only', is_flag=True, help='Only validate, do not import')
def recipe_import(file, validate_only):
    """Import recipe from file"""
    from .core.recipe import RecipeManager

    with click.progressbar(
        length=100,
        label='Importing recipe'
    ) as bar:
        manager = RecipeManager()

        # 검증
        bar.update(30)
        if not manager.validate_recipe_file(file):
            click.echo("✗ Recipe validation failed", err=True)
            raise click.Abort()

        bar.update(30)

        if validate_only:
            click.echo("✓ Recipe is valid")
            return

        # Import
        recipe_id = manager.import_recipe(file)
        bar.update(40)

        click.echo(f"✓ Imported recipe: {recipe_id}")

@recipe.command('export')
@click.argument('recipe_id')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', type=click.Choice(['json', 'yaml']), default='json')
def recipe_export(recipe_id, output, format):
    """Export recipe to file"""
    from .core.recipe import RecipeManager

    manager = RecipeManager()
    recipe_data = manager.get_recipe(recipe_id)

    if not output:
        output = f"{recipe_id}.{format}"

    manager.export_recipe(recipe_id, output, format=format)
    click.echo(f"✓ Exported to: {output}")

if __name__ == '__main__':
    cli()
```

</div>
<div>

**Click vs argparse 비교**:

| 기능 | argparse | Click | 비고 |
|------|----------|-------|------|
| **학습 곡선** | 완만 | 완만 | 둘 다 쉬움 |
| **데코레이터** | ❌ | ✅ | Click이 더 Pythonic |
| **자동 도움말** | ✅ | ✅ | 둘 다 자동 생성 |
| **진행 표시줄** | ❌ | ✅ | Click 내장 |
| **색상 출력** | ❌ | ✅ | Click 내장 |
| **확인 프롬프트** | ❌ | ✅ | `@confirmation_option` |
| **파일 처리** | 수동 | 자동 | Click이 편리 |
| **컨텍스트** | ❌ | ✅ | `@click.pass_context` |
| **표준 라이브러리** | ✅ | ❌ | argparse는 내장 |

**Click 주요 기능**:

1. **데코레이터 스타일**
   ```python
   @click.command()
   @click.option('--name')
   def greet(name):
       click.echo(f'Hello {name}')
   ```

2. **진행 표시줄**
   ```python
   with click.progressbar(items) as bar:
       for item in bar:
           process(item)
   ```

3. **색상 출력**
   ```python
   click.echo(click.style('Success!', fg='green'))
   click.echo(click.style('Error!', fg='red'))
   ```

4. **확인 프롬프트**
   ```python
   @click.confirmation_option(
       prompt='Are you sure?'
   )
   def dangerous_action():
       ...
   ```

5. **파일 입출력**
   ```python
   @click.command()
   @click.argument('input', type=click.File('r'))
   @click.argument('output', type=click.File('w'))
   def convert(input, output):
       data = input.read()
       output.write(transform(data))
   ```

**선택 가이드**:
- **argparse**: 표준 라이브러리 선호, 간단한 CLI
- **Click**: 복잡한 CLI, 사용자 경험 중시, 고급 기능 필요

**반도체 HMI 적용**:
- 레시피 import/export 시 진행 표시줄
- 위험 작업 확인 프롬프트 (삭제 등)
- 색상으로 성공/실패 구분
- 계층적 명령 구조 (config/recipe/equipment 그룹)

</div>
</div>

---

# 4. 로깅 (Logging) 모범 사례

## 4.1 로깅 기본 설정

<div class="grid grid-cols-2 gap-8">
<div>

```python
# logger.py - 로깅 설정
import logging
import sys
from pathlib import Path
from logging.handlers import (
    RotatingFileHandler,
    TimedRotatingFileHandler
)

def setup_logger(
    name: str = __name__,
    level: str = "INFO",
    log_dir: Path = Path("logs"),
    console: bool = True,
    file: bool = True
) -> logging.Logger:
    """
    로거 설정

    Args:
        name: 로거 이름
        level: 로그 레벨 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        log_dir: 로그 파일 디렉토리
        console: 콘솔 출력 여부
        file: 파일 출력 여부

    Returns:
        설정된 로거
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # 기존 핸들러 제거 (중복 방지)
    logger.handlers.clear()

    # 포맷터 정의
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # 1. 콘솔 핸들러
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)

    # 2. 파일 핸들러 (일반 로그)
    if file:
        log_dir.mkdir(parents=True, exist_ok=True)

        # 크기 기반 로테이션 (10MB, 5개 백업)
        file_handler = RotatingFileHandler(
            log_dir / "hmi.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

        # 3. 에러 전용 파일 핸들러
        error_handler = RotatingFileHandler(
            log_dir / "error.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)

        # 4. 시간 기반 로테이션 (일별)
        daily_handler = TimedRotatingFileHandler(
            log_dir / "daily.log",
            when='midnight',
            interval=1,
            backupCount=30,  # 30일 보관
            encoding='utf-8'
        )
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(detailed_formatter)
        daily_handler.suffix = "%Y%m%d"
        logger.addHandler(daily_handler)

    return logger

# 전역 로거
logger = setup_logger('semiconductor_hmi')
```

```python
# 사용 예시
from .utils.logger import logger

# 다양한 로그 레벨
logger.debug("디버깅 정보: 변수 x = 10")
logger.info("프로세스 시작")
logger.warning("메모리 사용량 80% 초과")
logger.error("장비 통신 실패")
logger.critical("시스템 중단")

# 예외 로깅
try:
    result = risky_operation()
except Exception as e:
    logger.exception("작업 실패")  # 스택 트레이스 자동 포함

# 구조화된 로깅 (extra 파라미터)
logger.info(
    "Recipe started",
    extra={
        'recipe_id': 'RCP001',
        'equipment': 'Chamber-A',
        'operator': 'user123'
    }
)
```

</div>
<div>

**로깅 레벨 가이드**:

| 레벨 | 사용 시나리오 | 예시 |
|------|---------------|------|
| **DEBUG** | 개발 중 상세 정보 | 변수 값, 함수 호출 순서 |
| **INFO** | 정상 작동 확인 | 프로세스 시작/완료, 연결 성공 |
| **WARNING** | 주의 필요한 상황 | 재시도, 성능 저하, 설정 누락 |
| **ERROR** | 오류 발생 (복구 가능) | 통신 실패, 파일 없음, 검증 실패 |
| **CRITICAL** | 치명적 오류 (복구 불가) | 시스템 다운, 데이터 손실 |

**핸들러 유형**:

1. **StreamHandler**
   - 콘솔 출력 (stdout/stderr)
   - 개발 및 디버깅용

2. **RotatingFileHandler**
   - 파일 크기 기반 로테이션
   - `maxBytes`: 최대 파일 크기
   - `backupCount`: 백업 파일 개수
   - 예: `hmi.log`, `hmi.log.1`, `hmi.log.2`

3. **TimedRotatingFileHandler**
   - 시간 기반 로테이션
   - `when='midnight'`: 매일 자정
   - `when='H'`: 매 시간
   - `when='W0'`: 매주 월요일

4. **기타 핸들러**
   - `SMTPHandler`: 이메일 전송
   - `SysLogHandler`: syslog 서버
   - `HTTPHandler`: HTTP endpoint

**포맷터 패턴**:
```python
# 상세 로그 (파일용)
'%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
# 출력: 2024-10-02 14:30:00 - semiconductor_hmi - ERROR - equipment.py:123 - Connection failed

# 간단한 로그 (콘솔용)
'%(asctime)s - %(levelname)s - %(message)s'
# 출력: 14:30:00 - ERROR - Connection failed
```

**반도체 HMI 적용**:
- 일반 로그: `hmi.log` (크기 로테이션)
- 에러 로그: `error.log` (분석용)
- 일별 로그: `daily.20241002.log` (감사 추적)
- 장비별 로거: `logger = logging.getLogger('hmi.chamber_a')`

</div>
</div>

---

## 4.2 구조화된 로깅 (Structured Logging)

<div class="grid grid-cols-2 gap-8">
<div>

```python
# structured_logger.py - 구조화된 로깅
import logging
import json
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """JSON 형식 로그 포맷터"""

    def format(self, record: logging.LogRecord) -> str:
        """
        로그를 JSON으로 변환

        ELK Stack, CloudWatch 등과 호환
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # extra 필드 추가
        if hasattr(record, 'equipment_id'):
            log_data['equipment_id'] = record.equipment_id
        if hasattr(record, 'recipe_id'):
            log_data['recipe_id'] = record.recipe_id
        if hasattr(record, 'operator'):
            log_data['operator'] = record.operator

        # 예외 정보
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)

def setup_structured_logger(
    name: str,
    json_file: str = "logs/structured.log"
) -> logging.Logger:
    """구조화된 로거 설정"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # JSON 파일 핸들러
    json_handler = RotatingFileHandler(
        json_file,
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=10
    )
    json_handler.setFormatter(JSONFormatter())
    logger.addHandler(json_handler)

    return logger

# 전역 구조화 로거
structured_logger = setup_structured_logger('semiconductor_hmi.structured')
```

```python
# 사용 예시: 구조화된 로깅
from .utils.structured_logger import structured_logger

# 장비 이벤트 로깅
structured_logger.info(
    "Equipment state changed",
    extra={
        'equipment_id': 'CHAMBER-A-001',
        'old_state': 'IDLE',
        'new_state': 'PROCESSING',
        'operator': 'user123',
        'recipe_id': 'RCP001',
        'wafer_id': 'W12345'
    }
)

# 출력 (JSON):
# {
#   "timestamp": "2024-10-02T06:30:00.123456",
#   "level": "INFO",
#   "logger": "semiconductor_hmi.structured",
#   "message": "Equipment state changed",
#   "module": "equipment",
#   "function": "set_state",
#   "line": 145,
#   "equipment_id": "CHAMBER-A-001",
#   "old_state": "IDLE",
#   "new_state": "PROCESSING",
#   "operator": "user123",
#   "recipe_id": "RCP001",
#   "wafer_id": "W12345"
# }

# 성능 메트릭 로깅
structured_logger.info(
    "Process completed",
    extra={
        'equipment_id': 'CHAMBER-A-001',
        'recipe_id': 'RCP001',
        'duration_seconds': 3600,
        'wafers_processed': 25,
        'yield_rate': 98.5,
        'defect_count': 3
    }
)
```

```python
# Context Manager로 로그 컨텍스트 관리
import logging
from contextlib import contextmanager

@contextmanager
def log_context(**kwargs):
    """
    로그 컨텍스트 임시 설정

    with log_context(equipment_id='CHAMBER-A'):
        logger.info("Processing")  # equipment_id 자동 포함
    """
    # 기존 필터 저장
    old_filter = logging.getLogger().filters.copy()

    # 컨텍스트 필터 추가
    class ContextFilter(logging.Filter):
        def filter(self, record):
            for key, value in kwargs.items():
                setattr(record, key, value)
            return True

    context_filter = ContextFilter()
    logging.getLogger().addFilter(context_filter)

    try:
        yield
    finally:
        # 필터 복원
        logging.getLogger().removeFilter(context_filter)

# 사용 예시
with log_context(equipment_id='CHAMBER-A', operator='user123'):
    logger.info("Recipe started")  # equipment_id, operator 자동 포함
    process_recipe()
    logger.info("Recipe completed")
```

</div>
<div>

**구조화된 로깅의 장점**:

1. **검색 및 분석 용이**
   - JSON 필드로 정확한 검색
   - 집계 및 통계 생성 용이
   - ELK/Splunk 등 로그 분석 도구와 호환

2. **컨텍스트 정보 풍부**
   - 장비 ID, 레시피 ID, 작업자 자동 포함
   - 관련 로그 그룹화 가능
   - 디버깅 시간 단축

3. **자동화 친화적**
   - 기계 판독 가능 (JSON)
   - 알람/모니터링 시스템과 통합
   - 대시보드 자동 생성

**ELK Stack 통합 예시**:
```python
# Elasticsearch에 직접 전송
from elasticsearch import Elasticsearch

class ElasticsearchHandler(logging.Handler):
    def __init__(self, es_client, index_name):
        super().__init__()
        self.es = es_client
        self.index = index_name

    def emit(self, record):
        log_data = JSONFormatter().format(record)
        self.es.index(
            index=self.index,
            document=json.loads(log_data)
        )

# 사용
es = Elasticsearch(['http://localhost:9200'])
logger.addHandler(
    ElasticsearchHandler(es, 'hmi-logs-2024')
)
```

**로그 쿼리 예시** (Elasticsearch):
```json
// 특정 장비의 에러 로그 검색
{
  "query": {
    "bool": {
      "must": [
        {"match": {"equipment_id": "CHAMBER-A-001"}},
        {"match": {"level": "ERROR"}}
      ]
    }
  }
}

// 레시피 평균 처리 시간
{
  "aggs": {
    "avg_duration": {
      "avg": {"field": "duration_seconds"}
    }
  },
  "query": {
    "match": {"recipe_id": "RCP001"}
  }
}
```

**로그 컨텍스트 패턴**:
```python
# 방법 1: extra 파라미터
logger.info("Message", extra={'key': 'value'})

# 방법 2: Context Manager
with log_context(key='value'):
    logger.info("Message")  # key 자동 포함

# 방법 3: Adapter
adapter = logging.LoggerAdapter(logger, {'key': 'value'})
adapter.info("Message")  # key 자동 포함
```

**반도체 HMI 적용**:
- 장비 가동률 분석 (로그 기반)
- 에러 패턴 자동 탐지
- 실시간 모니터링 대시보드
- 감사 추적 (누가, 언제, 무엇을)

</div>
</div>

---

# 5. 배포 최적화된 Python PySide6 Docker 이미지
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

## 🔧 **기초 실습 - 패키징 및 기본 배포**

### 실습 1: PyInstaller를 활용한 실행 파일 생성

#### 1.1 PyInstaller 설정 파일 작성
```python
