# 심화 실습: 3D 시각화 및 고급 애니메이션 (45분)

## 3D 장비 시각화

### WPF 3D 기초 개념

<div class="code-section">

**3D 좌표계 및 카메라 설정**

```xml
<!-- 3D 뷰포트 기본 구조 -->
<Viewport3D>
    <Viewport3D.Camera>
        <PerspectiveCamera Position="5,3,4"
                          LookDirection="-5,-3,-4"
                          UpDirection="0,1,0"
                          FieldOfView="45"/>
    </Viewport3D.Camera>

    <!-- 조명 설정 -->
    <ModelVisual3D>
        <ModelVisual3D.Content>
            <Model3DGroup>
                <AmbientLight Color="#404040"/>
                <DirectionalLight Color="#C0C0C0" Direction="-1,-1,-1"/>
                <PointLight Color="#FFFFFF" Position="3,3,3" Range="10"/>
            </Model3DGroup>
        </ModelVisual3D.Content>
    </ModelVisual3D>

    <!-- 3D 모델 컨텐츠 -->
    <ModelVisual3D x:Name="EquipmentModel">
        <!-- 장비 모델이 여기에 추가됨 -->
    </ModelVisual3D>
</Viewport3D>
```

</div>

### 산업용 장비 3D 모델링

<div class="code-section">

**CVD 장비 3D 구현**

```csharp
public class Equipment3DVisualizer : UserControl
{
    private Viewport3D viewport3D;
    private ModelVisual3D equipmentModel;
    private readonly RotateTransform3D rotateTransform;
    private readonly TranslateTransform3D translateTransform;
    private readonly ScaleTransform3D scaleTransform;

    public Equipment3DVisualizer()
    {
        InitializeComponent();
        SetupTransforms();
        CreateEquipmentGeometry();
        SetupInteractivity();
    }

    private void SetupTransforms()
    {
        rotateTransform = new RotateTransform3D(new AxisAngleRotation3D(new Vector3D(0, 1, 0), 0));
        translateTransform = new TranslateTransform3D();
        scaleTransform = new ScaleTransform3D();

        var transformGroup = new Transform3DGroup();
        transformGroup.Children.Add(scaleTransform);
        transformGroup.Children.Add(rotateTransform);
        transformGroup.Children.Add(translateTransform);

        equipmentModel.Transform = transformGroup;
    }

    private void CreateEquipmentGeometry()
    {
        var model3DGroup = new Model3DGroup();

        // CVD 챔버 (원통형)
        model3DGroup.Children.Add(CreateChamber());

        // 웨이퍼 스테이지
        model3DGroup.Children.Add(CreateWaferStage());

        // 가스 주입구들
        model3DGroup.Children.Add(CreateGasInlets());

        // 온도 센서
        model3DGroup.Children.Add(CreateTemperatureSensors());

        // 압력 게이지
        model3DGroup.Children.Add(CreatePressureGauges());

        equipmentModel.Content = model3DGroup;
    }

    private GeometryModel3D CreateChamber()
    {
        var mesh = new MeshGeometry3D();

        // 원통형 챔버 메시 생성
        CreateCylinderMesh(mesh, new Point3D(0, 0, 0), 2.0, 3.0, 32);

        var material = new MaterialGroup();
        material.Children.Add(new DiffuseMaterial(new SolidColorBrush(Colors.LightGray)));
        material.Children.Add(new SpecularMaterial(new SolidColorBrush(Colors.White), 50));

        return new GeometryModel3D(mesh, material);
    }

    private void CreateCylinderMesh(MeshGeometry3D mesh, Point3D center, double radius, double height, int segments)
    {
        double angleStep = 2 * Math.PI / segments;

        // 하단 원
        for (int i = 0; i < segments; i++)
        {
            double angle = i * angleStep;
            var point = new Point3D(
                center.X + radius * Math.Cos(angle),
                center.Y - height / 2,
                center.Z + radius * Math.Sin(angle)
            );
            mesh.Positions.Add(point);
        }

        // 상단 원
        for (int i = 0; i < segments; i++)
        {
            double angle = i * angleStep;
            var point = new Point3D(
                center.X + radius * Math.Cos(angle),
                center.Y + height / 2,
                center.Z + radius * Math.Sin(angle)
            );
            mesh.Positions.Add(point);
        }

        // 측면 삼각형들 생성
        for (int i = 0; i < segments; i++)
        {
            int next = (i + 1) % segments;

            // 첫 번째 삼각형
            mesh.TriangleIndices.Add(i);
            mesh.TriangleIndices.Add(segments + i);
            mesh.TriangleIndices.Add(next);

            // 두 번째 삼각형
            mesh.TriangleIndices.Add(next);
            mesh.TriangleIndices.Add(segments + i);
            mesh.TriangleIndices.Add(segments + next);
        }
    }

    // 센서 위치에 따른 색상 변경
    public void UpdateSensorVisualization(string sensorId, double value, double minValue, double maxValue)
    {
        var normalizedValue = (value - minValue) / (maxValue - minValue);
        var color = GetTemperatureColor(normalizedValue);

        // 해당 센서 모델 찾기 및 색상 업데이트
        if (sensorModels.TryGetValue(sensorId, out var sensorModel))
        {
            var material = new DiffuseMaterial(new SolidColorBrush(color));
            sensorModel.Material = material;
        }
    }

    private Color GetTemperatureColor(double normalizedValue)
    {
        // 온도에 따른 색상 그라데이션 (파란색 → 녹색 → 노란색 → 빨간색)
        if (normalizedValue < 0.33)
            return Color.FromRgb(0, (byte)(255 * normalizedValue * 3), 255);
        else if (normalizedValue < 0.66)
            return Color.FromRgb((byte)(255 * (normalizedValue - 0.33) * 3), 255, (byte)(255 * (1 - (normalizedValue - 0.33) * 3)));
        else
            return Color.FromRgb(255, (byte)(255 * (1 - (normalizedValue - 0.66) * 3)), 0);
    }
}
```

</div>

### HelixToolkit 활용 고급 3D

<div class="code-section">

**HelixToolkit을 활용한 고성능 3D 렌더링**

```csharp
// NuGet: HelixToolkit.Wpf 설치 필요
using HelixToolkit.Wpf;

public class AdvancedEquipment3DView : UserControl
{
    private HelixViewport3D helixViewport;
    private readonly Dictionary<string, ModelVisual3D> equipmentParts;

    public AdvancedEquipment3DView()
    {
        equipmentParts = new Dictionary<string, ModelVisual3D>();
        InitializeHelixViewport();
        LoadEquipmentModel();
    }

    private void InitializeHelixViewport()
    {
        helixViewport = new HelixViewport3D
        {
            Background = new SolidColorBrush(Color.FromRgb(20, 20, 30)),
            DefaultCamera = new PerspectiveCamera(new Point3D(8, 6, 8), new Vector3D(-8, -6, -8), new Vector3D(0, 1, 0), 45),
            ShowCoordinateSystem = true,
            ShowFrameRate = true,
            IsHeadLightEnabled = true
        };

        // 그리드 추가
        var gridLines = new GridLinesVisual3D
        {
            Width = 10,
            Length = 10,
            MinorDistance = 0.5,
            MajorDistance = 1,
            Thickness = 0.01
        };
        helixViewport.Children.Add(gridLines);

        Content = helixViewport;
    }

    private void LoadEquipmentModel()
    {
        // 3D 모델 파일에서 로드 (예: .3ds, .obj 파일)
        var importer = new ModelImporter();

        try
        {
            var equipmentModel = importer.Load("Assets/CVD_Equipment.3ds");
            var visual = new ModelVisual3D { Content = equipmentModel };

            helixViewport.Children.Add(visual);
            equipmentParts["MainChamber"] = visual;
        }
        catch (Exception ex)
        {
            // 모델 파일이 없는 경우 프로그래매틱 생성
            CreateParametricEquipment();
        }
    }

    private void CreateParametricEquipment()
    {
        // 파라미터 기반 장비 모델 생성
        var builder = new MeshBuilder();

        // CVD 반응기 챔버
        builder.AddCylinder(new Point3D(0, 0, 0), new Point3D(0, 3, 0), 1.5, 64);

        // 가스 주입구
        for (int i = 0; i < 4; i++)
        {
            double angle = i * Math.PI / 2;
            var position = new Point3D(1.8 * Math.Cos(angle), 1.5, 1.8 * Math.Sin(angle));
            var direction = new Point3D(position.X + 0.5 * Math.Cos(angle), position.Y, position.Z + 0.5 * Math.Sin(angle));
            builder.AddCylinder(position, direction, 0.1, 16);
        }

        // 웨이퍼 스테이지
        builder.AddCylinder(new Point3D(0, 0.2, 0), new Point3D(0, 0.3, 0), 0.8, 32);

        var mesh = builder.ToMesh();
        var material = MaterialHelper.CreateMaterial(Colors.Silver, 0.3, 100);

        var model = new GeometryModel3D(mesh, material);
        var visual = new ModelVisual3D { Content = model };

        helixViewport.Children.Add(visual);
        equipmentParts["ParametricChamber"] = visual;
    }

    // 실시간 데이터에 따른 시각적 피드백
    public void UpdateEquipmentStatus(EquipmentStatus status)
    {
        Dispatcher.Invoke(() =>
        {
            // 온도에 따른 색상 변화
            var temperatureColor = GetTemperatureColor(status.Temperature);
            UpdatePartColor("MainChamber", temperatureColor);

            // 압력에 따른 크기 변화 (시각적 효과)
            var pressureScale = 1.0 + (status.Pressure - 1.0) * 0.1;
            UpdatePartScale("MainChamber", pressureScale);

            // 가스 흐름 애니메이션
            if (status.GasFlow > 0)
            {
                StartGasFlowAnimation(status.GasFlow);
            }
        });
    }

    private void StartGasFlowAnimation(double flowRate)
    {
        // 파티클 시스템으로 가스 흐름 시각화
        var particleSystem = new ParticleSystemVisual3D
        {
            ParticleSize = 0.05,
            ParticleCount = (int)(flowRate * 100),
            EmissionRate = flowRate * 10,
            ParticleLife = TimeSpan.FromSeconds(2)
        };

        helixViewport.Children.Add(particleSystem);

        // 2초 후 제거
        var timer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(2) };
        timer.Tick += (s, e) =>
        {
            helixViewport.Children.Remove(particleSystem);
            timer.Stop();
        };
        timer.Start();
    }
}
```

</div>

## 고급 애니메이션 시스템

### 복합 애니메이션 관리

<div class="code-section">

**산업용 HMI 애니메이션 매니저**

```csharp
public class EquipmentAnimationManager
{
    private readonly Dictionary<string, Storyboard> activeAnimations;
    private readonly Dictionary<string, AnimationClock> animationClocks;

    public EquipmentAnimationManager()
    {
        activeAnimations = new Dictionary<string, Storyboard>();
        animationClocks = new Dictionary<string, AnimationClock>();
    }

    // 장비 상태 전환 애니메이션
    public void AnimateStatusTransition(FrameworkElement target, EquipmentStatus fromStatus, EquipmentStatus toStatus)
    {
        var storyboard = new Storyboard();

        // 색상 전환 애니메이션
        var colorAnimation = CreateColorAnimation(
            GetStatusColor(fromStatus),
            GetStatusColor(toStatus),
            TimeSpan.FromMilliseconds(800)
        );

        Storyboard.SetTarget(colorAnimation, target);
        Storyboard.SetTargetProperty(colorAnimation, new PropertyPath("(Border.Background).(SolidColorBrush.Color)"));
        storyboard.Children.Add(colorAnimation);

        // 크기 변화 애니메이션 (pulse 효과)
        if (toStatus == EquipmentStatus.Warning || toStatus == EquipmentStatus.Error)
        {
            var scaleAnimation = CreatePulseAnimation();
            Storyboard.SetTarget(scaleAnimation, target);
            Storyboard.SetTargetProperty(scaleAnimation, new PropertyPath("(UIElement.RenderTransform).(ScaleTransform.ScaleX)"));
            storyboard.Children.Add(scaleAnimation);
        }

        // 투명도 애니메이션
        var opacityAnimation = new DoubleAnimation
        {
            From = 0.7,
            To = 1.0,
            Duration = TimeSpan.FromMilliseconds(400),
            EasingFunction = new QuadraticEase { EasingMode = EasingMode.EaseOut }
        };

        Storyboard.SetTarget(opacityAnimation, target);
        Storyboard.SetTargetProperty(opacityAnimation, new PropertyPath("Opacity"));
        storyboard.Children.Add(opacityAnimation);

        // 애니메이션 시작
        storyboard.Begin();
        activeAnimations[$"StatusTransition_{target.Name}"] = storyboard;
    }

    private ColorAnimation CreateColorAnimation(Color from, Color to, TimeSpan duration)
    {
        return new ColorAnimation
        {
            From = from,
            To = to,
            Duration = duration,
            EasingFunction = new QuadraticEase { EasingMode = EasingMode.EaseInOut }
        };
    }

    private DoubleAnimationUsingKeyFrames CreatePulseAnimation()
    {
        var animation = new DoubleAnimationUsingKeyFrames
        {
            RepeatBehavior = RepeatBehavior.Forever,
            AutoReverse = true
        };

        animation.KeyFrames.Add(new EasingDoubleKeyFrame(1.0, KeyTime.FromTimeSpan(TimeSpan.Zero)));
        animation.KeyFrames.Add(new EasingDoubleKeyFrame(1.1, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(500)))
        {
            EasingFunction = new SineEase { EasingMode = EasingMode.EaseInOut }
        });
        animation.KeyFrames.Add(new EasingDoubleKeyFrame(1.0, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(1000)))
        {
            EasingFunction = new SineEase { EasingMode = EasingMode.EaseInOut }
        });

        return animation;
    }

    // 데이터 변화 애니메이션
    public void AnimateValueChange(FrameworkElement gauge, double fromValue, double toValue, TimeSpan duration)
    {
        var animation = new DoubleAnimation
        {
            From = fromValue,
            To = toValue,
            Duration = duration,
            EasingFunction = new QuadraticEase { EasingMode = EasingMode.EaseOut }
        };

        // 값 변화 과정에서 시각적 피드백
        animation.CurrentTimeInvalidated += (s, e) =>
        {
            var clock = (AnimationClock)s;
            var currentValue = fromValue + (toValue - fromValue) * clock.CurrentProgress.Value;

            // 급격한 변화 시 경고 효과
            if (Math.Abs(toValue - fromValue) > (toValue * 0.1))
            {
                AddWarningEffect(gauge);
            }
        };

        gauge.BeginAnimation(CircularGauge.ValueProperty, animation);
    }

    private void AddWarningEffect(FrameworkElement element)
    {
        var glowEffect = new DropShadowEffect
        {
            Color = Colors.Orange,
            BlurRadius = 20,
            ShadowDepth = 0,
            Opacity = 0.7
        };

        element.Effect = glowEffect;

        // 3초 후 효과 제거
        var timer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(3) };
        timer.Tick += (s, e) =>
        {
            element.Effect = null;
            timer.Stop();
        };
        timer.Start();
    }

    // 복합 장비 동작 시퀀스 애니메이션
    public async Task AnimateProcessSequence(IEnumerable<FrameworkElement> equipmentParts, ProcessSequence sequence)
    {
        foreach (var step in sequence.Steps)
        {
            var targetPart = equipmentParts.FirstOrDefault(p => p.Name == step.EquipmentPart);
            if (targetPart != null)
            {
                // 각 단계별 애니메이션 실행
                await AnimateProcessStep(targetPart, step);

                // 다음 단계로 진행하기 전 대기
                await Task.Delay(step.Duration);
            }
        }
    }

    private async Task AnimateProcessStep(FrameworkElement part, ProcessStep step)
    {
        switch (step.Action)
        {
            case ProcessAction.Heat:
                await AnimateHeating(part, step.TargetValue);
                break;
            case ProcessAction.Evacuate:
                await AnimateEvacuation(part);
                break;
            case ProcessAction.InjectGas:
                await AnimateGasInjection(part, step.GasType);
                break;
            case ProcessAction.Rotate:
                await AnimateRotation(part, step.RotationSpeed);
                break;
        }
    }

    private async Task AnimateHeating(FrameworkElement part, double targetTemperature)
    {
        // 온도 상승에 따른 색상 변화
        var colorAnimation = new ColorAnimation
        {
            From = Colors.Blue,
            To = Colors.Red,
            Duration = TimeSpan.FromSeconds(2),
            EasingFunction = new QuadraticEase()
        };

        var brush = new SolidColorBrush();
        part.SetValue(Control.BackgroundProperty, brush);
        brush.BeginAnimation(SolidColorBrush.ColorProperty, colorAnimation);

        await Task.Delay(2000);
    }
}
```

</div>

### 성능 최적화된 애니메이션

<div class="code-section">

**하드웨어 가속 애니메이션**

```csharp
public class PerformanceOptimizedAnimations
{
    // Composition API를 활용한 고성능 애니메이션
    public static void ApplyCompositionAnimation(FrameworkElement element, string propertyName, double from, double to)
    {
        // WPF Composition API 활용 (Windows 10 이상)
        var compositor = ElementCompositionPreview.GetElementVisual(element)?.Compositor;
        if (compositor != null)
        {
            var animation = compositor.CreateScalarKeyFrameAnimation();
            animation.InsertKeyFrame(0f, (float)from);
            animation.InsertKeyFrame(1f, (float)to);
            animation.Duration = TimeSpan.FromMilliseconds(500);

            var visual = ElementCompositionPreview.GetElementVisual(element);
            visual.StartAnimation(propertyName, animation);
        }
    }

    // GPU 최적화된 Transform 애니메이션
    public static void AnimateTransformGPU(FrameworkElement element, Transform newTransform)
    {
        element.RenderTransform = newTransform;
        element.CacheMode = new BitmapCache(); // GPU 캐싱 활성화

        // Transform은 자동으로 GPU에서 처리됨
        var animation = new DoubleAnimation
        {
            From = 0,
            To = 1,
            Duration = TimeSpan.FromMilliseconds(300)
        };

        newTransform.BeginAnimation(Transform.ValueProperty, animation);
    }
}
```

</div>

---

