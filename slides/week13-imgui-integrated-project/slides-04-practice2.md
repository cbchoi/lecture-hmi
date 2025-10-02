                                    -v ${WORKSPACE}/test-results:/app/test-results \
                                    ${IMAGE_NAME}:test \
                                    ctest --output-on-failure --output-junit test-results/junit.xml
                            '''
                        }
                    }
                    post {
                        always {
                            junit 'test-results/junit.xml'
                        }
                    }
                }

                stage('Integration Tests') {
                    steps {
                        container('docker') {
                            sh '''
                                # Docker Compose로 통합 테스트 환경 구성
                                docker-compose -f docker-compose.test.yml up -d

                                # 통합 테스트 실행
                                docker-compose -f docker-compose.test.yml exec -T hmi-app \
                                    ./run_integration_tests.sh
                            '''
                        }
                    }
                    post {
                        always {
                            sh 'docker-compose -f docker-compose.test.yml down -v'
                        }
                    }
                }
            }
        }

        stage('Build Production Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'release/*'
                }
            }
            steps {
                container('docker') {
                    sh '''
                        echo ${DOCKER_CREDENTIALS_PSW} | docker login -u ${DOCKER_CREDENTIALS_USR} --password-stdin ${DOCKER_REGISTRY}

                        # 프로덕션 이미지 빌드
                        docker build \
                            -f Dockerfile.production \
                            -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_VERSION} \
                            -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest \
                            .

                        # 이미지 보안 스캔
                        docker run --rm \
                            -v /var/run/docker.sock:/var/run/docker.sock \
                            aquasec/trivy image \
                            --exit-code 1 \
                            --severity HIGH,CRITICAL \
                            ${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_VERSION}

                        # 이미지 푸시
                        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_VERSION}
                        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest
                    '''
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                container('helm') {
                    sh '''
                        # Helm 차트로 스테이징 환경 배포
                        helm upgrade --install hmi-staging ./helm/semiconductor-hmi \
                            --namespace staging \
                            --create-namespace \
                            --set image.tag=${BUILD_VERSION} \
                            --set environment=staging \
                            --set replicaCount=1 \
                            --values helm/values-staging.yaml \
                            --wait --timeout=300s
                    '''
                }
            }
        }

        stage('Performance Tests') {
            when {
                branch 'main'
            }
            steps {
                container('docker') {
                    sh '''
                        # K6 성능 테스트 실행
                        docker run --rm \
                            -v ${WORKSPACE}/performance-tests:/tests \
                            -v ${WORKSPACE}/performance-results:/results \
                            loadimpact/k6 run \
                            --out junit=/results/performance-junit.xml \
                            --out json=/results/performance-results.json \
                            /tests/load-test.js
                    '''
                }
            }
            post {
                always {
                    junit 'performance-results/performance-junit.xml'
                    archiveArtifacts artifacts: 'performance-results/*', fingerprint: true
                }
            }
        }

        stage('Deploy to Production') {
            when {
                anyOf {
                    branch 'release/*'
                    tag 'v*'
                }
            }
            steps {
                script {
                    def deploy = input(
                        message: 'Deploy to production?',
                        parameters: [
                            choice(
                                name: 'DEPLOYMENT_STRATEGY',
                                choices: ['rolling', 'blue-green', 'canary'],
                                description: 'Deployment strategy'
                            )
                        ]
                    )

                    container('helm') {
                        sh """
                            helm upgrade --install hmi-production ./helm/semiconductor-hmi \
                                --namespace production \
                                --create-namespace \
                                --set image.tag=${BUILD_VERSION} \
                                --set environment=production \
                                --set deployment.strategy=${deploy} \
                                --values helm/values-production.yaml \
                                --wait --timeout=600s
                        """
                    }
                }
            }
        }

        stage('Smoke Tests') {
            when {
                anyOf {
                    branch 'main'
                    branch 'release/*'
                    tag 'v*'
                }
            }
            steps {
                container('docker') {
                    sh '''
                        # 배포 후 스모크 테스트
                        docker run --rm \
                            -v ${WORKSPACE}/smoke-tests:/tests \
                            postman/newman \
                            run /tests/smoke-tests.postman_collection.json \
                            --environment /tests/production.postman_environment.json \
                            --reporters junit \
                            --reporter-junit-export /tests/smoke-test-results.xml
                    '''
                }
            }
            post {
                always {
                    junit 'smoke-tests/smoke-test-results.xml'
                }
            }
        }
    }

    post {
        always {
            // 빌드 결과 알림
            script {
                def status = currentBuild.result ?: 'SUCCESS'
                def color = status == 'SUCCESS' ? 'good' : 'danger'

                slackSend(
                    channel: '#hmi-deployments',
                    color: color,
                    message: """
                        Build ${status}: ${env.JOB_NAME} - ${env.BUILD_NUMBER}
                        Branch: ${env.BRANCH_NAME}
                        Commit: ${env.GIT_COMMIT_SHORT}
                        Duration: ${currentBuild.durationString}
                        Build URL: ${env.BUILD_URL}
                    """
                )
            }
        }

        failure {
            // 실패시 추가 알림
            emailext(
                to: '${DEFAULT_RECIPIENTS}',
                subject: 'Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}',
                body: '''
                    Build failed for ${env.JOB_NAME} - ${env.BUILD_NUMBER}

                    Check the build logs: ${env.BUILD_URL}

                    Recent commits:
                    ${env.CHANGE_LOG}
                '''
            )
        }

        cleanup {
            // 정리 작업
            sh '''
                docker system prune -f
                kubectl delete pods --field-selector=status.phase=Succeeded -n semiconductor-hmi || true
            '''
        }
    }
}
```

---

## 🧪 테스트 및 시뮬레이션: 팹 환경 시뮬레이션 및 성능 검증

### 1. 실제 반도체 팹 환경 시뮬레이터

#### 1.1 디지털 트윈 팹 시뮬레이터

```cpp
// FabSimulator.cpp
#include "MasterSystemArchitecture.h"
#include <random>
#include <thread>
#include <chrono>

namespace SemiconductorHMI::Simulation {

// 반도체 공정 단계
enum class ProcessStep {
    WAFER_INCOMING,
    CLEANING,
    LITHOGRAPHY,
    ETCHING,
    DEPOSITION_CVD,
    DEPOSITION_PVD,
    ION_IMPLANTATION,
    CMP,
    METROLOGY,
    FINAL_TEST,
    OUTGOING
};

// 장비 상태
enum class EquipmentState {
    IDLE,
    RUNNING,
    MAINTENANCE,
    ERROR,
    CLEANING_MODE
};

// 웨이퍼 정보
struct Wafer {
    std::string wafer_id;
    std::string lot_id;
    ProcessStep current_step;
    std::vector<ProcessStep> completed_steps;
    std::chrono::system_clock::time_point start_time;
    std::unordered_map<std::string, double> measurements;
    bool has_defects = false;
    int priority = 0;
};

// 장비 정보
struct Equipment {
    std::string equipment_id;
    std::string equipment_type;  // CVD, PVD, ETCH, CMP, etc.
    ProcessStep process_step;
    EquipmentState state;
    Wafer* current_wafer = nullptr;

    // 성능 지표
    double throughput_wafers_per_hour = 0.0;
    double uptime_percentage = 0.0;
    double yield_percentage = 0.0;
    std::chrono::system_clock::time_point last_maintenance;

    // 실시간 파라미터
    std::unordered_map<std::string, double> process_parameters;
    std::unordered_map<std::string, double> parameter_limits;
};

class FabSimulator {
private:
    // 팹 구성
    std::vector<Equipment> equipment_list_;
    std::queue<Wafer> wafer_queue_;
    std::vector<Wafer> completed_wafers_;

    // 시뮬레이션 제어
    std::atomic<bool> simulation_running_{false};
    std::thread simulation_thread_;
    std::thread equipment_thread_;
    std::thread wafer_generator_thread_;

    // 시뮬레이션 통계
    struct FabStatistics {
        std::atomic<int> total_wafers_processed{0};
        std::atomic<int> wafers_in_process{0};
        std::atomic<double> overall_yield{0.0};
        std::atomic<double> average_cycle_time_hours{0.0};
        std::atomic<int> equipment_downtime_minutes{0};
    } statistics_;

    // 현실적인 데이터 생성을 위한 랜덤 생성기
    mutable std::mutex random_mutex_;
    std::mt19937 random_generator_;

public:
    FabSimulator() : random_generator_(std::random_device{}()) {
        InitializeFabLayout();
    }

    ~FabSimulator() {
        StopSimulation();
    }

    bool StartSimulation() {
        if (simulation_running_) return false;

        simulation_running_ = true;

        // 시뮬레이션 스레드들 시작
        simulation_thread_ = std::thread([this]() { SimulationLoop(); });
        equipment_thread_ = std::thread([this]() { EquipmentSimulationLoop(); });
        wafer_generator_thread_ = std::thread([this]() { WaferGeneratorLoop(); });

        return true;
    }

    void StopSimulation() {
        if (simulation_running_) {
            simulation_running_ = false;

            if (simulation_thread_.joinable()) simulation_thread_.join();
            if (equipment_thread_.joinable()) equipment_thread_.join();
            if (wafer_generator_thread_.joinable()) wafer_generator_thread_.join();
        }
    }

    // 실시간 데이터 접근
    std::vector<Equipment> GetEquipmentStatus() const {
        return equipment_list_;
    }

    FabStatistics GetFabStatistics() const {
        return statistics_;
    }

    // 장비 제어 시뮬레이션
    bool StartEquipment(const std::string& equipment_id) {
        auto it = std::find_if(equipment_list_.begin(), equipment_list_.end(),
                              [&](const Equipment& eq) { return eq.equipment_id == equipment_id; });

        if (it != equipment_list_.end() && it->state == EquipmentState::IDLE) {
            it->state = EquipmentState::RUNNING;
            return true;
        }
        return false;
    }

    bool StopEquipment(const std::string& equipment_id) {
        auto it = std::find_if(equipment_list_.begin(), equipment_list_.end(),
                              [&](const Equipment& eq) { return eq.equipment_id == equipment_id; });

        if (it != equipment_list_.end() && it->state == EquipmentState::RUNNING) {
            it->state = EquipmentState::IDLE;
            return true;
        }
        return false;
    }

    bool TriggerMaintenance(const std::string& equipment_id) {
        auto it = std::find_if(equipment_list_.begin(), equipment_list_.end(),
                              [&](const Equipment& eq) { return eq.equipment_id == equipment_id; });

        if (it != equipment_list_.end()) {
            it->state = EquipmentState::MAINTENANCE;
            it->last_maintenance = std::chrono::system_clock::now();
            return true;
        }
        return false;
    }

private:
    void InitializeFabLayout() {
        // CVD 장비들
        for (int i = 1; i <= 4; ++i) {
            Equipment cvd;
            cvd.equipment_id = "CVD_" + std::to_string(i);
            cvd.equipment_type = "CVD";
            cvd.process_step = ProcessStep::DEPOSITION_CVD;
            cvd.state = EquipmentState::IDLE;
            cvd.throughput_wafers_per_hour = 25.0;
            cvd.uptime_percentage = 95.0;
            cvd.yield_percentage = 98.5;

            // 프로세스 파라미터 설정
            cvd.process_parameters["temperature"] = 250.0;
            cvd.process_parameters["pressure"] = 0.1;
            cvd.process_parameters["flow_rate"] = 50.0;
            cvd.process_parameters["power"] = 1500.0;

            cvd.parameter_limits["temperature"] = 280.0;  // 최대값
            cvd.parameter_limits["pressure"] = 0.15;
            cvd.parameter_limits["flow_rate"] = 60.0;
            cvd.parameter_limits["power"] = 2000.0;

            equipment_list_.push_back(cvd);
        }

        // PVD 장비들
        for (int i = 1; i <= 3; ++i) {
            Equipment pvd;
            pvd.equipment_id = "PVD_" + std::to_string(i);
            pvd.equipment_type = "PVD";
            pvd.process_step = ProcessStep::DEPOSITION_PVD;
            pvd.state = EquipmentState::IDLE;
            pvd.throughput_wafers_per_hour = 20.0;
            pvd.uptime_percentage = 92.0;
            pvd.yield_percentage = 97.8;

            pvd.process_parameters["temperature"] = 200.0;
            pvd.process_parameters["pressure"] = 0.05;
            pvd.process_parameters["power"] = 2000.0;
            pvd.process_parameters["voltage"] = 380.0;

            equipment_list_.push_back(pvd);
        }

        // ETCH 장비들
        for (int i = 1; i <= 5; ++i) {
            Equipment etch;
            etch.equipment_id = "ETCH_" + std::to_string(i);
            etch.equipment_type = "ETCH";
            etch.process_step = ProcessStep::ETCHING;
            etch.state = EquipmentState::IDLE;
            etch.throughput_wafers_per_hour = 30.0;
            etch.uptime_percentage = 90.0;
            etch.yield_percentage = 96.5;

            etch.process_parameters["pressure"] = 0.02;
            etch.process_parameters["flow_rate"] = 100.0;
            etch.process_parameters["power"] = 2500.0;
            etch.process_parameters["bias_voltage"] = 150.0;

            equipment_list_.push_back(etch);
        }

        // CMP 장비들
        for (int i = 1; i <= 2; ++i) {
            Equipment cmp;
            cmp.equipment_id = "CMP_" + std::to_string(i);
            cmp.equipment_type = "CMP";
            cmp.process_step = ProcessStep::CMP;
            cmp.state = EquipmentState::IDLE;
            cmp.throughput_wafers_per_hour = 15.0;
            cmp.uptime_percentage = 88.0;
            cmp.yield_percentage = 99.2;

            cmp.process_parameters["pressure"] = 5.0;  // psi
            cmp.process_parameters["rotation_speed"] = 120.0;  // rpm
            cmp.process_parameters["slurry_flow"] = 200.0;  // ml/min

            equipment_list_.push_back(cmp);
        }

        // 리소그래피 장비들
        for (int i = 1; i <= 3; ++i) {
            Equipment litho;
            litho.equipment_id = "LITHO_" + std::to_string(i);
            litho.equipment_type = "LITHOGRAPHY";
            litho.process_step = ProcessStep::LITHOGRAPHY;
            litho.state = EquipmentState::IDLE;
            litho.throughput_wafers_per_hour = 40.0;
            litho.uptime_percentage = 85.0;
            litho.yield_percentage = 94.0;

            equipment_list_.push_back(litho);
        }
    }

    void SimulationLoop() {
        while (simulation_running_) {
            // 웨이퍼 라우팅 및 스케줄링
            ProcessWaferQueue();

            // 통계 업데이트
            UpdateStatistics();

            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }

    void EquipmentSimulationLoop() {
        while (simulation_running_) {
            for (auto& equipment : equipment_list_) {
                SimulateEquipmentBehavior(equipment);
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }

    void WaferGeneratorLoop() {
        int wafer_counter = 1;

        while (simulation_running_) {
            // 새 웨이퍼 생성 (현실적인 간격)
            std::this_thread::sleep_for(std::chrono::minutes(2));

            Wafer new_wafer;
            new_wafer.wafer_id = "W" + std::to_string(wafer_counter++);
            new_wafer.lot_id = "LOT" + std::to_string((wafer_counter - 1) / 25 + 1);
            new_wafer.current_step = ProcessStep::WAFER_INCOMING;
            new_wafer.start_time = std::chrono::system_clock::now();
            new_wafer.priority = GenerateRandomInt(1, 5);

            wafer_queue_.push(new_wafer);
            statistics_.wafers_in_process++;
        }
    }

    void ProcessWaferQueue() {
        if (wafer_queue_.empty()) return;

        Wafer& wafer = wafer_queue_.front();

        // 다음 프로세스 단계에 맞는 장비 찾기
        auto available_equipment = FindAvailableEquipment(wafer.current_step);

        if (available_equipment) {
            // 웨이퍼를 장비에 할당
            available_equipment->current_wafer = &wafer;
            available_equipment->state = EquipmentState::RUNNING;

            wafer_queue_.pop();

            // 프로세스 완료 시뮬레이션 (별도 스레드에서 처리)
            std::thread([this, available_equipment]() {
                ProcessWaferOnEquipment(available_equipment);
            }).detach();
        }
    }

    Equipment* FindAvailableEquipment(ProcessStep step) {
        for (auto& equipment : equipment_list_) {
            if (equipment.process_step == step && equipment.state == EquipmentState::IDLE) {
                return &equipment;
            }
        }
        return nullptr;
    }

    void ProcessWaferOnEquipment(Equipment* equipment) {
        if (!equipment || !equipment->current_wafer) return;

        // 프로세스 시간 시뮬레이션
        double process_time_hours = 3600.0 / equipment->throughput_wafers_per_hour;
        int process_time_seconds = static_cast<int>(process_time_hours * 3600);

        std::this_thread::sleep_for(std::chrono::seconds(process_time_seconds));

        // 프로세스 완료 처리
        Wafer* wafer = equipment->current_wafer;
        wafer->completed_steps.push_back(wafer->current_step);

        // 다음 단계로 이동
        wafer->current_step = GetNextProcessStep(wafer->current_step);

        // 수율 시뮬레이션
        if (GenerateRandomDouble(0.0, 100.0) > equipment->yield_percentage) {
            wafer->has_defects = true;
        }

        // 장비에서 웨이퍼 제거
        equipment->current_wafer = nullptr;
        equipment->state = EquipmentState::IDLE;

        // 웨이퍼가 완료되었으면 완료 목록에 추가
        if (wafer->current_step == ProcessStep::OUTGOING) {
            completed_wafers_.push_back(*wafer);
            statistics_.total_wafers_processed++;
            statistics_.wafers_in_process--;
        } else {
            // 다음 단계를 위해 큐에 다시 추가
            wafer_queue_.push(*wafer);
        }
    }

    ProcessStep GetNextProcessStep(ProcessStep current) {
        switch (current) {
            case ProcessStep::WAFER_INCOMING: return ProcessStep::CLEANING;
            case ProcessStep::CLEANING: return ProcessStep::LITHOGRAPHY;
            case ProcessStep::LITHOGRAPHY: return ProcessStep::ETCHING;
            case ProcessStep::ETCHING: return ProcessStep::DEPOSITION_CVD;
            case ProcessStep::DEPOSITION_CVD: return ProcessStep::DEPOSITION_PVD;
            case ProcessStep::DEPOSITION_PVD: return ProcessStep::ION_IMPLANTATION;
            case ProcessStep::ION_IMPLANTATION: return ProcessStep::CMP;
            case ProcessStep::CMP: return ProcessStep::METROLOGY;
            case ProcessStep::METROLOGY: return ProcessStep::FINAL_TEST;
            case ProcessStep::FINAL_TEST: return ProcessStep::OUTGOING;
            default: return ProcessStep::OUTGOING;
        }
    }

    void SimulateEquipmentBehavior(Equipment& equipment) {
        // 프로세스 파라미터 변동 시뮬레이션
        for (auto& [param_name, value] : equipment.process_parameters) {
            double variation = GenerateRandomDouble(-2.0, 2.0);  // ±2% 변동
            double new_value = value * (1.0 + variation / 100.0);

            // 한계값 체크
            if (equipment.parameter_limits.count(param_name)) {
                double limit = equipment.parameter_limits[param_name];
                if (new_value > limit) {
                    // 알람 발생 시뮬레이션
                    equipment.state = EquipmentState::ERROR;
                    continue;
                }
            }

            equipment.process_parameters[param_name] = new_value;
        }

        // 장비 고장 시뮬레이션 (매우 낮은 확률)
        if (equipment.state == EquipmentState::RUNNING && GenerateRandomDouble(0.0, 1.0) < 0.0001) {
            equipment.state = EquipmentState::ERROR;
        }

        // 정기 유지보수 시뮬레이션
        auto now = std::chrono::system_clock::now();
        auto hours_since_maintenance = std::chrono::duration_cast<std::chrono::hours>(
            now - equipment.last_maintenance).count();

        if (hours_since_maintenance > 168) {  // 1주일마다 유지보수
            equipment.state = EquipmentState::MAINTENANCE;
        }
    }

    void UpdateStatistics() {
        // 전체 수율 계산
        if (!completed_wafers_.empty()) {
            int good_wafers = 0;
            for (const auto& wafer : completed_wafers_) {
                if (!wafer.has_defects) good_wafers++;
            }
            statistics_.overall_yield = (static_cast<double>(good_wafers) / completed_wafers_.size()) * 100.0;
        }

        // 평균 사이클 타임 계산
        if (!completed_wafers_.empty()) {
            double total_cycle_time = 0.0;
            auto now = std::chrono::system_clock::now();

            for (const auto& wafer : completed_wafers_) {
                auto cycle_time = std::chrono::duration_cast<std::chrono::hours>(
                    now - wafer.start_time).count();
                total_cycle_time += cycle_time;
            }

            statistics_.average_cycle_time_hours = total_cycle_time / completed_wafers_.size();
        }
    }

    double GenerateRandomDouble(double min, double max) {
        std::lock_guard<std::mutex> lock(random_mutex_);
        std::uniform_real_distribution<double> dist(min, max);
        return dist(random_generator_);
    }

    int GenerateRandomInt(int min, int max) {
        std::lock_guard<std::mutex> lock(random_mutex_);
        std::uniform_int_distribution<int> dist(min, max);
        return dist(random_generator_);
    }
};

} // namespace SemiconductorHMI::Simulation
```

### 2. 통합 성능 테스트

#### 2.1 종합 성능 벤치마크

