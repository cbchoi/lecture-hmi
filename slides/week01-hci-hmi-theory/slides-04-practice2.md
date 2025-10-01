## 실습 2: 반도체 FAB 환경 시뮬레이션

### 가상 클린룸 체험

#### VR 환경 구축
**플랫폼**: Unity 3D + Oculus Integration
**시나리오**:
- 300mm 웨이퍼 FAB 재현
- Class 1 클린룸 환경
- 실제 장비 배치 모델링

#### 환경 구성 요소
1. **물리적 환경**
   - 천장높이: 4.5m
   - HEPA 필터: 2×2m 간격
   - 작업대 높이: 850mm
   - 통로 폭: 2.5m

2. **조명 환경**
   - 황색광 (585nm) 시뮬레이션
   - 조도 400 lux 균등 분포
   - 그림자 최소화 설계

3. **소음 환경**
   - 배경소음: 65dB
   - HVAC 시스템: 연속 저주파
   - 장비 동작음: 간헐적 고주파

#### Unity C# 코드 예제 - Part 1

<div class="grid grid-cols-2 gap-8">
<div>

```csharp [1-25]
using UnityEngine;
using UnityEngine.XR;
public class CleanroomSimulation : MonoBehaviour
{
[Header("Environmental Settings")]
public Light yellowLight;
public AudioSource hvacSound;
public ParticleSystem airFlow;
[Header("Equipment Models")]
public GameObject[] equipmentPrefabs;
public Transform[] equipmentPositions;
private float currentNoiseLevel = 65f;
private float ambientTemperature = 22.5f;
private float relativeHumidity = 45f;
void Start()
{
SetupCleanroomEnvironment();
InitializeEquipment();
StartEnvironmentalMonitoring();
}
```

</div>
<div>

**클래스 선언 및 초기화**
- **Line 1-2**: Unity 3D와 XR(VR/AR) 네임스페이스 import
- **Line 4**: MonoBehaviour 상속으로 Unity 컴포넌트 생성
- **Line 6-9**: 환경 설정 관련 public 변수
  - **yellowLight**: 클린룸 황색광 조명
  - **hvacSound**: HVAC 시스템 소음 재생
  - **airFlow**: 층류 공기흐름 파티클 시스템

- **Line 11-13**: 장비 모델 관련 변수
  - **equipmentPrefabs**: 반도체 장비 프리팹 배열
  - **equipmentPositions**: 장비 배치 위치 배열

- **Line 15-17**: 환경 모니터링 변수 (소음, 온도, 습도)
- **Line 19-24**: Start() 메서드로 시뮬레이션 초기화 순서 정의

</div>
</div>

---

#### Unity C# 코드 예제 - Part 2

<div class="grid grid-cols-2 gap-8">
<div>

```csharp [26-50]
void SetupCleanroomEnvironment()
{
// 황색광 설정 (585nm 근사)
yellowLight.color = new Color(1f, 0.8f, 0.3f, 1f);
yellowLight.intensity = 1.2f;
yellowLight.shadows = LightShadows.Soft;
// HVAC 시스템 소음
hvacSound.clip = Resources.Load<AudioClip>("HVACSound");
hvacSound.volume = 0.3f;
hvacSound.loop = true;
hvacSound.Play();
// 층류 공기흐름 시뮬레이션
var main = airFlow.main;
main.startLifetime = 5f;
main.startSpeed = 0.5f;
main.maxParticles = 1000;
var shape = airFlow.shape;
shape.shapeType = ParticleSystemShapeType.Box;
shape.scale = new Vector3(20f, 0.1f, 15f);
var velocityOverLifetime = airFlow.velocityOverLifetime;
velocityOverLifetime.enabled = true;
```

</div>
<div>

**클린룸 환경 설정 메서드**
- **Line 26**: 클린룸 환경 구성 메서드 시작
- **Line 28-31**: 황색광 조명 설정
  - **Line 29**: RGB(1.0, 0.8, 0.3)로 585nm 황색광 근사
  - **Line 30**: 조명 강도 1.2로 설정 (400 lux 달성)
  - **Line 31**: 소프트 그림자로 시각적 피로 최소화

- **Line 33-37**: HVAC 시스템 소음 설정
  - **Line 34**: Resources 폴더에서 HVAC 소음 파일 로드
  - **Line 35-36**: 볼륨 0.3, 반복 재생 설정
  - **Line 37**: 배경 소음 재생 시작

- **Line 39-50**: 층류 공기흐름 파티클 시스템
  - **Line 41-43**: 파티클 수명 5초, 속도 0.5m/s, 최대 1000개
  - **Line 46-47**: Box 형태로 20×0.1×15m 영역 설정

</div>
</div>

---

#### Unity C# 코드 예제 - Part 3

<div class="grid grid-cols-2 gap-8">
<div>

```csharp [51-75]
velocityOverLifetime.space = ParticleSystemSimulationSpace.World;
velocityOverLifetime.y = new ParticleSystem.MinMaxCurve(-0.5f);
}
void InitializeEquipment()
{
for(int i = 0; i < equipmentPrefabs.Length; i++)
{
if(i < equipmentPositions.Length)
{
GameObject equipment = Instantiate(equipmentPrefabs[i],
equipmentPositions[i].position,
equipmentPositions[i].rotation);
// HMI 패널 설정
HMIPanel hmiPanel = equipment.GetComponentInChildren<HMIPanel>();
if(hmiPanel != null)
{
hmiPanel.Initialize(GetEquipmentParameters(i));
}
}
}
}
EquipmentParameters GetEquipmentParameters(int equipmentIndex)
```

</div>
<div>

**장비 초기화 및 파라미터 설정**
- **Line 51-52**: 파티클 속도 설정 완료
  - World 좌표계에서 Y축 -0.5m/s로 하향 기류 모사

- **Line 55-73**: 장비 초기화 메서드
  - **Line 57**: 모든 장비 프리팹에 대해 반복 처리
  - **Line 59**: 배치 위치가 유효한지 확인
  - **Line 61-63**: 지정된 위치와 회전으로 장비 인스턴스 생성
  - **Line 66**: 하위 컴포넌트에서 HMI 패널 검색
  - **Line 67-70**: HMI 패널이 존재하면 장비별 파라미터로 초기화

- **Line 75**: 장비별 파라미터 반환 메서드 선언
  - 각 장비 타입에 맞는 운영 파라미터 제공
  - 리소그래피, CVD 등 장비별 특성 반영

</div>
</div>

---

#### Unity C# 코드 예제 - Part 4

<div class="grid grid-cols-2 gap-8">
<div>

```csharp [76-100]
{
switch(equipmentIndex)
{
case 0: // Stepper
return new EquipmentParameters
{
name = "ASML PAS 5500",
throughput = 150, // WPH
overlayAccuracy = 2.0f, // nm
cdUniformity = 1.5f // nm
};
case 1: // CVD
return new EquipmentParameters
{
name = "AMAT Centura",
temperature = 450f, // Celsius
pressure = 10f, // Torr
gasFlow = 100f // sccm
};
default:
return new EquipmentParameters();
}
}
```

</div>
<div>

**장비별 파라미터 설정**
- **Line 77**: switch문으로 장비 인덱스별 분기 처리
- **Line 79-86**: 리소그래피 장비 (ASML PAS 5500) 설정
  - **throughput**: 150 WPH (Wafers Per Hour)
  - **overlayAccuracy**: 2.0nm 오버레이 정확도
  - **cdUniformity**: 1.5nm CD(Critical Dimension) 균일성

- **Line 88-95**: CVD 장비 (Applied Materials Centura) 설정
  - **temperature**: 450°C 챔버 온도
  - **pressure**: 10 Torr 공정 압력
  - **gasFlow**: 100 sccm 가스 유량

- **Line 97-98**: 기본값 반환 (정의되지 않은 장비)
- **Line 100**: 메서드 종료

실제 반도체 장비의 운영 사양을 반영한 정확한 수치

</div>
</div>

---

#### Unity C# 코드 예제 - Part 5

<div class="grid grid-cols-2 gap-8">
<div>

```csharp [101-125]
void StartEnvironmentalMonitoring()
{
InvokeRepeating("UpdateEnvironmentalData", 1f, 1f);
}
void UpdateEnvironmentalData()
{
// 환경 데이터 시뮬레이션 (정규분포 노이즈 추가)
ambientTemperature = 22.5f + Random.Range(-0.05f, 0.05f);
relativeHumidity = 45f + Random.Range(-0.5f, 0.5f);
currentNoiseLevel = 65f + Random.Range(-2f, 2f);
// UI 업데이트
UpdateEnvironmentalDisplay();
// 임계값 체크
CheckEnvironmentalAlarms();
}
void CheckEnvironmentalAlarms()
{
if(ambientTemperature < 22.4f || ambientTemperature > 22.6f)
{
TriggerAlarm("Temperature out of range: " + ambientTemperature.ToString("F2") + "°C");
}
```

</div>
<div>

**환경 모니터링 시스템**
- **Line 101-104**: 환경 모니터링 시작
  - **Line 103**: 1초 간격으로 환경 데이터 업데이트 반복 실행

- **Line 106-118**: 환경 데이터 업데이트 메서드
  - **Line 109**: 온도 22.5±0.05°C 범위에서 랜덤 변동
  - **Line 110**: 습도 45±0.5% 범위에서 변동
  - **Line 111**: 소음 65±2dB 범위에서 변동
  - **Line 114**: UI 디스플레이 업데이트 호출
  - **Line 117**: 알람 조건 확인 메서드 호출

- **Line 120-125**: 환경 알람 체크
  - **Line 122**: 온도가 22.4-22.6°C 범위를 벗어나면 알람
  - **Line 124**: 온도 이상 알람 메시지 생성 및 트리거

정밀한 환경 제어가 필요한 클린룸 특성 반영

</div>
</div>

---

#### Unity C# 코드 예제 - Part 6

<div class="grid grid-cols-2 gap-8">
<div>

```csharp [126-140]
if(relativeHumidity < 44f || relativeHumidity > 46f)
{
TriggerAlarm("Humidity out of range: " + relativeHumidity.ToString("F1") + "%");
}
}
void TriggerAlarm(string message)
{
AlarmManager.Instance.ShowAlarm(message, AlarmPriority.Medium);
}
}
[System.Serializable]
public class EquipmentParameters
{
public string name;
public float throughput;
public float overlayAccuracy;
public float cdUniformity;
public float temperature;
public float pressure;
public float gasFlow;
}
```

</div>
<div>

**알람 시스템 및 데이터 구조**
- **Line 127-130**: 습도 알람 체크
  - 44-46% 범위를 벗어나면 습도 이상 알람 발생
  - 소수점 1자리까지 표시하는 포맷 사용

- **Line 133-136**: 알람 트리거 메서드
  - **Line 135**: 싱글톤 패턴의 AlarmManager를 통해 알람 표시
  - Medium 우선순위로 알람 분류 (Critical, High, Medium, Low)

- **Line 139-149**: 장비 파라미터 데이터 클래스
  - **[System.Serializable]**: Unity Inspector에서 편집 가능
  - **Line 142-148**: 다양한 장비 타입의 파라미터 수용
    - 범용적 구조로 확장성 확보
    - 반도체 장비별 특성 파라미터 포함

클린룸 환경 시뮬레이션의 완성된 구조

</div>
</div>

---

### 체험 시나리오
1. **진입 절차**
   - 에어샤워 체험
   - 클린슈트 착용 시뮬레이션
   - 안전 교육 인터랙션

2. **장비 조작**
   - 리소그래피 장비 HMI
   - CVD 장비 모니터링
   - 검사 장비 데이터 분석

3. **비상 상황**
   - 가스 누출 경보
   - 전원 차단 절차
   - 비상 대피 훈련