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
