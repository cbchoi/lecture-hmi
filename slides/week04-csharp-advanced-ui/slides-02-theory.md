# 📖 이론 강의

---

## UI 디자인 패턴

### 🎨 Template Method 패턴

**WPF 컨트롤 생명주기와 Template Method**

<div class="grid grid-cols-2 gap-8">
<div>

```csharp
// Template Method 패턴 기반 컨트롤
public abstract class BaseEquipmentControl : Control
{
    // 템플릿 메서드: 고정된 알고리즘
    public override void OnApplyTemplate()
    {
        base.OnApplyTemplate();

        // 1단계: 템플릿 파트 로드
        LoadTemplateParts();

        // 2단계: 이벤트 핸들러 연결
        AttachEventHandlers();

        // 3단계: 초기 상태 설정
        InitializeState();

        // 4단계: 서브클래스 초기화
        OnControlInitialized();
    }

    // 하위 클래스가 구현해야 하는 추상 메서드
    protected abstract void LoadTemplateParts();
    protected abstract void InitializeState();

    // 선택적으로 오버라이드 가능한 훅 메서드
    protected virtual void AttachEventHandlers() { }
    protected virtual void OnControlInitialized() { }
}
```

</div>
<div>

**Template Method 패턴 핵심**:
- **고정된 알고리즘**: `OnApplyTemplate()`이 실행 순서 정의
- **추상 메서드**: 하위 클래스가 반드시 구현
- **훅 메서드**: 선택적 커스터마이징 포인트

**WPF에서의 활용**:
- 컨트롤 초기화 프로세스 표준화
- 일관된 생명주기 관리
- 확장 가능한 구조

**장점**:
- 코드 중복 제거
- 일관된 동작 보장
- 유지보수성 향상

</div>
</div>

---

<div class="grid grid-cols-2 gap-8">
<div>

```csharp
// 구체적인 구현: 온도 게이지
public class TemperatureGaugeControl
    : BaseEquipmentControl
{
    private TextBlock _valueText;
    private Path _indicatorPath;
    private Border _alarmBorder;

    protected override void LoadTemplateParts()
    {
        _valueText = GetTemplateChild("PART_ValueText")
            as TextBlock;
        _indicatorPath = GetTemplateChild("PART_Indicator")
            as Path;
        _alarmBorder = GetTemplateChild("PART_AlarmBorder")
            as Border;

        if (_valueText == null || _indicatorPath == null)
        {
            throw new InvalidOperationException(
                "Required template parts not found");
        }
    }

    protected override void InitializeState()
    {
        UpdateValueDisplay(CurrentTemperature);
        UpdateIndicatorPosition(CurrentTemperature);
        UpdateAlarmState(AlarmStatus.Normal);
    }

    protected override void AttachEventHandlers()
    {
        this.MouseEnter += OnMouseEnter;
        this.MouseLeave += OnMouseLeave;
    }

    protected override void OnControlInitialized()
    {
        // 온도 센서 연결
        StartTemperatureMonitoring();
    }

    // 컨트롤 고유 로직
    private void UpdateValueDisplay(double temperature)
    {
        if (_valueText != null)
        {
            _valueText.Text = $"{temperature:F1}°C";
        }
    }
}
```

</div>
<div>

**구현 클래스의 책임**:

**LoadTemplateParts()**:
- XAML 템플릿에서 필수 요소 찾기
- null 체크 및 예외 처리
- 타입 캐스팅

**InitializeState()**:
- 초기 값 설정
- UI 요소 상태 초기화
- 기본 스타일 적용

**AttachEventHandlers()**:
- 마우스/키보드 이벤트 연결
- 데이터 바인딩 이벤트 처리
- 리소스 정리 이벤트 등록

**OnControlInitialized()**:
- 외부 시스템 연결 (센서, 네트워크)
- 타이머 시작
- 백그라운드 작업 초기화

**사용 시나리오**:
```xml
<local:TemperatureGaugeControl
    CurrentTemperature="125.5"
    MinValue="0"
    MaxValue="300"
    AlarmThreshold="250"/>
```

</div>
</div>

---

### ⚙️ Strategy 패턴

**레이아웃 및 렌더링 전략**

<div class="grid grid-cols-2 gap-8">
<div>

```csharp
// Strategy 인터페이스: 렌더링 전략
public interface IRenderStrategy
{
    void Render(DrawingContext dc,
        EquipmentData data, Size size);
    bool CanRender(EquipmentData data);
}

// 전략 1: 그래프 렌더링
public class GraphRenderStrategy : IRenderStrategy
{
    public void Render(DrawingContext dc,
        EquipmentData data, Size size)
    {
        var points = ConvertToPoints(
            data.TimeSeries, size);

        var geometry = new StreamGeometry();
        using (var ctx = geometry.Open())
        {
            ctx.BeginFigure(points[0], false, false);
            ctx.PolyLineTo(points, true, true);
        }

        var pen = new Pen(Brushes.Blue, 2);
        dc.DrawGeometry(null, pen, geometry);
    }

    public bool CanRender(EquipmentData data)
    {
        return data.TimeSeries != null &&
               data.TimeSeries.Count > 1;
    }

    private List<Point> ConvertToPoints(
        List<DataPoint> timeSeries, Size size)
    {
        var points = new List<Point>();
        var maxValue = timeSeries.Max(p => p.Value);
        var minValue = timeSeries.Min(p => p.Value);
        var range = maxValue - minValue;

        for (int i = 0; i < timeSeries.Count; i++)
        {
            var x = (double)i / (timeSeries.Count - 1)
                * size.Width;
            var normalized = (timeSeries[i].Value - minValue)
                / range;
            var y = size.Height * (1 - normalized);
            points.Add(new Point(x, y));
        }

        return points;
    }
}
```

</div>
<div>

**Strategy 패턴 핵심**:
- 알고리즘을 캡슐화
- 런타임에 전략 교체 가능
- 클라이언트 코드 변경 없이 확장

**IRenderStrategy 인터페이스**:
- `Render()`: 실제 렌더링 수행
- `CanRender()`: 해당 전략 사용 가능 여부

**GraphRenderStrategy 구현**:
- 시계열 데이터를 그래프로 렌더링
- Point 리스트로 변환
- StreamGeometry로 효율적인 드로잉
- 정규화를 통한 스케일 조정

**사용 예시**:
```csharp
var data = new EquipmentData
{
    TimeSeries = GetRecentData(),
    Type = DataType.Temperature
};

if (strategy.CanRender(data))
{
    strategy.Render(dc, data, controlSize);
}
```

</div>
</div>

---

<div class="grid grid-cols-2 gap-8">
<div>

```csharp
// 전략 2: 바 차트 렌더링
public class BarChartRenderStrategy : IRenderStrategy
{
    private readonly Brush fillBrush = Brushes.LightBlue;
    private readonly Brush strokeBrush = Brushes.DarkBlue;

    public void Render(DrawingContext dc,
        EquipmentData data, Size size)
    {
        var barWidth = size.Width / data.Values.Count;
        var maxValue = data.Values.Max();

        for (int i = 0; i < data.Values.Count; i++)
        {
            var value = data.Values[i];
            var barHeight = (value / maxValue)
                * size.Height * 0.8;

            var rect = new Rect(
                x: i * barWidth + barWidth * 0.1,
                y: size.Height - barHeight,
                width: barWidth * 0.8,
                height: barHeight);

            dc.DrawRectangle(fillBrush,
                new Pen(strokeBrush, 1), rect);

            // 값 레이블 그리기
            var text = new FormattedText(
                value.ToString("F1"),
                CultureInfo.CurrentCulture,
                FlowDirection.LeftToRight,
                new Typeface("Segoe UI"),
                10, strokeBrush,
                VisualTreeHelper.GetDpi(this).PixelsPerDip);

            dc.DrawText(text, new Point(
                rect.X + rect.Width / 2 - text.Width / 2,
                rect.Y - text.Height - 2));
        }
    }

    public bool CanRender(EquipmentData data)
    {
        return data.Values != null &&
               data.Values.Count > 0 &&
               data.Values.Count <= 20;
    }
}

// 전략 3: 히트맵 렌더링
public class HeatmapRenderStrategy : IRenderStrategy
{
    public void Render(DrawingContext dc,
        EquipmentData data, Size size)
    {
        var rows = data.Matrix.GetLength(0);
        var cols = data.Matrix.GetLength(1);

        var cellWidth = size.Width / cols;
        var cellHeight = size.Height / rows;

        var maxValue = data.Matrix.Cast<double>().Max();

        for (int r = 0; r < rows; r++)
        {
            for (int c = 0; c < cols; c++)
            {
                var value = data.Matrix[r, c];
                var intensity = value / maxValue;

                var color = GetHeatColor(intensity);
                var brush = new SolidColorBrush(color);

                var rect = new Rect(
                    c * cellWidth, r * cellHeight,
                    cellWidth, cellHeight);

                dc.DrawRectangle(brush,
                    new Pen(Brushes.White, 0.5), rect);
            }
        }
    }

    public bool CanRender(EquipmentData data)
    {
        return data.Matrix != null;
    }

    private Color GetHeatColor(double intensity)
    {
        // 파란색 -> 녹색 -> 빨간색 그라데이션
        if (intensity < 0.5)
        {
            var t = intensity * 2;
            return Color.FromRgb(
                0,
                (byte)(255 * t),
                (byte)(255 * (1 - t)));
        }
        else
        {
            var t = (intensity - 0.5) * 2;
            return Color.FromRgb(
                (byte)(255 * t),
                (byte)(255 * (1 - t)),
                0);
        }
    }
}
```

</div>
<div>

**BarChartRenderStrategy**:
- 막대 그래프 방식 렌더링
- 최대 20개 데이터 포인트 지원
- 값 레이블 자동 표시
- 막대 간격 및 여백 자동 계산

**HeatmapRenderStrategy**:
- 2차원 행렬 데이터 시각화
- 색상 그라데이션으로 값 표현
- 웨이퍼 맵, 센서 배열 표시에 적합
- 파란색(낮음) → 빨간색(높음) 스케일

**Context 클래스로 전략 관리**:
```csharp
public class DataVisualizationControl : Control
{
    private IRenderStrategy _renderStrategy;

    public void SetRenderStrategy(
        VisualizationType type)
    {
        _renderStrategy = type switch
        {
            VisualizationType.Graph
                => new GraphRenderStrategy(),
            VisualizationType.BarChart
                => new BarChartRenderStrategy(),
            VisualizationType.Heatmap
                => new HeatmapRenderStrategy(),
            _ => throw new ArgumentException()
        };

        InvalidateVisual();
    }

    protected override void OnRender(
        DrawingContext dc)
    {
        base.OnRender(dc);

        if (_renderStrategy?.CanRender(_data)
            == true)
        {
            _renderStrategy.Render(
                dc, _data, RenderSize);
        }
    }
}
```

**런타임 전략 변경**:
```csharp
// 사용자 선택에 따라 전략 변경
visualControl.SetRenderStrategy(
    VisualizationType.Heatmap);
```

</div>
</div>

---

### 🏗️ Composite 패턴

**UI 계층 구조 관리**

<div class="grid grid-cols-2 gap-8">
<div>

```csharp
// Component: 공통 인터페이스
public interface IEquipmentComponent
{
    string Name { get; }
    EquipmentStatus Status { get; }

    void Start();
    void Stop();
    void UpdateStatus();

    // 계층 구조 탐색
    IEquipmentComponent Parent { get; set; }
    IEnumerable<IEquipmentComponent> GetChildren();
}

// Leaf: 단일 장비 (자식 없음)
public class EquipmentModule : IEquipmentComponent
{
    public string Name { get; set; }
    public EquipmentStatus Status { get; private set; }
    public IEquipmentComponent Parent { get; set; }

    private readonly IEquipmentController _controller;

    public EquipmentModule(
        string name,
        IEquipmentController controller)
    {
        Name = name;
        _controller = controller;
        Status = EquipmentStatus.Idle;
    }

    public void Start()
    {
        Console.WriteLine($"Starting {Name}");
        _controller.PowerOn();
        Status = EquipmentStatus.Running;
    }

    public void Stop()
    {
        Console.WriteLine($"Stopping {Name}");
        _controller.PowerOff();
        Status = EquipmentStatus.Idle;
    }

    public void UpdateStatus()
    {
        Status = _controller.GetCurrentStatus();
    }

    public IEnumerable<IEquipmentComponent> GetChildren()
    {
        // Leaf는 자식이 없음
        return Enumerable.Empty<IEquipmentComponent>();
    }
}
```

</div>
<div>

**Composite 패턴 핵심**:
- 개별 객체와 복합 객체를 동일하게 처리
- 트리 구조로 부품-전체 계층 표현
- 재귀적 구조

**IEquipmentComponent 인터페이스**:
- 모든 장비 컴포넌트의 공통 동작 정의
- `Start()`, `Stop()`: 생명주기 관리
- `UpdateStatus()`: 상태 동기화
- `GetChildren()`: 계층 탐색

**Leaf (EquipmentModule)**:
- 계층의 말단 노드
- 실제 장비 제어 로직 포함
- 자식 컴포넌트 없음
- `GetChildren()` → 빈 컬렉션 반환

**반도체 환경 적용**:
```
Fab Line (Composite)
├── Wet Station (Composite)
│   ├── Chemical Supply Module (Leaf)
│   ├── Wafer Handler (Leaf)
│   └── Dryer Module (Leaf)
└── Etcher (Composite)
    ├── Plasma Source (Leaf)
    ├── Vacuum Pump (Leaf)
    └── Gas Supply (Leaf)
```

</div>
</div>

---

<div class="grid grid-cols-2 gap-8">
<div>

```csharp
// Composite: 복합 장비 (자식 포함)
public class EquipmentGroup : IEquipmentComponent
{
    private readonly List<IEquipmentComponent> _children
        = new List<IEquipmentComponent>();

    public string Name { get; set; }
    public EquipmentStatus Status { get; private set; }
    public IEquipmentComponent Parent { get; set; }

    public EquipmentGroup(string name)
    {
        Name = name;
        Status = EquipmentStatus.Idle;
    }

    // 자식 관리 메서드
    public void Add(IEquipmentComponent component)
    {
        component.Parent = this;
        _children.Add(component);
    }

    public void Remove(IEquipmentComponent component)
    {
        component.Parent = null;
        _children.Remove(component);
    }

    // 재귀적으로 모든 자식에게 전파
    public void Start()
    {
        Console.WriteLine(
            $"Starting group: {Name}");

        foreach (var child in _children)
        {
            child.Start(); // 재귀 호출
        }

        Status = EquipmentStatus.Running;
    }

    public void Stop()
    {
        Console.WriteLine(
            $"Stopping group: {Name}");

        // 역순으로 정지 (안전성)
        for (int i = _children.Count - 1; i >= 0; i--)
        {
            _children[i].Stop();
        }

        Status = EquipmentStatus.Idle;
    }

    public void UpdateStatus()
    {
        foreach (var child in _children)
        {
            child.UpdateStatus();
        }

        // 자식들의 상태로부터 그룹 상태 결정
        Status = DetermineGroupStatus();
    }

    public IEnumerable<IEquipmentComponent> GetChildren()
    {
        return _children;
    }

    private EquipmentStatus DetermineGroupStatus()
    {
        if (_children.All(c =>
            c.Status == EquipmentStatus.Running))
            return EquipmentStatus.Running;

        if (_children.Any(c =>
            c.Status == EquipmentStatus.Error))
            return EquipmentStatus.Error;

        if (_children.Any(c =>
            c.Status == EquipmentStatus.Running))
            return EquipmentStatus.PartiallyRunning;

        return EquipmentStatus.Idle;
    }
}
```

</div>
<div>

**Composite (EquipmentGroup)**:
- 여러 자식 컴포넌트를 포함
- 동작을 자식들에게 재귀적으로 전파
- 그룹 전체를 하나의 단위로 제어

**Add/Remove 메서드**:
- 동적으로 계층 구조 변경
- 부모-자식 관계 자동 설정
- Parent 속성 관리

**재귀적 동작**:
- `Start()`: 모든 자식을 순차적으로 시작
- `Stop()`: 역순으로 정지 (의존성 고려)
- `UpdateStatus()`: 전체 트리 상태 갱신

**그룹 상태 집계**:
- 모든 자식이 Running → Running
- 하나라도 Error → Error
- 일부만 Running → PartiallyRunning
- 모두 Idle → Idle

**사용 예시**:
```csharp
// 계층 구조 구축
var fabLine = new EquipmentGroup("Fab Line 1");

var wetStation = new EquipmentGroup("Wet Station");
wetStation.Add(new EquipmentModule(
    "Chemical Supply", chemController));
wetStation.Add(new EquipmentModule(
    "Wafer Handler", handlerController));

var etcher = new EquipmentGroup("Etcher");
etcher.Add(new EquipmentModule(
    "Plasma Source", plasmaController));
etcher.Add(new EquipmentModule(
    "Vacuum Pump", pumpController));

fabLine.Add(wetStation);
fabLine.Add(etcher);

// 전체 라인 시작 (모든 장비 자동 시작)
fabLine.Start();

// 특정 그룹만 정지
wetStation.Stop();
```

**UI TreeView 바인딩**:
```xml
<TreeView ItemsSource="{Binding RootEquipment}">
  <TreeView.ItemTemplate>
    <HierarchicalDataTemplate
      ItemsSource="{Binding GetChildren}">
      <TextBlock Text="{Binding Name}"/>
    </HierarchicalDataTemplate>
  </TreeView.ItemTemplate>
</TreeView>
```

</div>
</div>

---

### 🎭 Decorator 패턴

**컨트롤 동작 확장**

<div class="grid grid-cols-2 gap-8">
<div>

```csharp
// Component: 기본 인터페이스
public interface IDataDisplay
{
    void Display(EquipmentData data);
    Size GetRequiredSize();
}

// ConcreteComponent: 기본 구현
public class BasicDataDisplay : IDataDisplay
{
    private readonly TextBlock _textBlock;

    public BasicDataDisplay(TextBlock textBlock)
    {
        _textBlock = textBlock;
    }

    public void Display(EquipmentData data)
    {
        _textBlock.Text =
            $"{data.Name}: {data.Value:F2} {data.Unit}";
    }

    public Size GetRequiredSize()
    {
        return new Size(200, 30);
    }
}

// Decorator 기본 클래스
public abstract class DataDisplayDecorator
    : IDataDisplay
{
    protected readonly IDataDisplay _innerDisplay;

    protected DataDisplayDecorator(
        IDataDisplay innerDisplay)
    {
        _innerDisplay = innerDisplay;
    }

    public virtual void Display(EquipmentData data)
    {
        _innerDisplay.Display(data);
    }

    public virtual Size GetRequiredSize()
    {
        return _innerDisplay.GetRequiredSize();
    }
}

// Concrete Decorator 1: 임계값 강조
public class ThresholdHighlightDecorator
    : DataDisplayDecorator
{
    private readonly double _warningThreshold;
    private readonly double _errorThreshold;
    private readonly Border _border;

    public ThresholdHighlightDecorator(
        IDataDisplay innerDisplay,
        Border border,
        double warningThreshold,
        double errorThreshold)
        : base(innerDisplay)
    {
        _border = border;
        _warningThreshold = warningThreshold;
        _errorThreshold = errorThreshold;
    }

    public override void Display(EquipmentData data)
    {
        // 기본 표시 먼저 수행
        _innerDisplay.Display(data);

        // 임계값에 따라 배경색 변경
        if (data.Value >= _errorThreshold)
        {
            _border.Background = Brushes.Red;
            _border.BorderBrush = Brushes.DarkRed;
            _border.BorderThickness = new Thickness(3);
        }
        else if (data.Value >= _warningThreshold)
        {
            _border.Background = Brushes.Orange;
            _border.BorderBrush = Brushes.DarkOrange;
            _border.BorderThickness = new Thickness(2);
        }
        else
        {
            _border.Background = Brushes.Transparent;
            _border.BorderBrush = Brushes.Gray;
            _border.BorderThickness = new Thickness(1);
        }
    }
}
```

</div>
<div>

**Decorator 패턴 핵심**:
- 객체에 동적으로 책임 추가
- 상속 없이 기능 확장
- 여러 Decorator 중첩 가능

**IDataDisplay 인터페이스**:
- 데이터 표시의 기본 계약
- `Display()`: 데이터 렌더링
- `GetRequiredSize()`: 필요한 크기 계산

**BasicDataDisplay**:
- 최소한의 텍스트 표시
- 데코레이터로 감쌀 핵심 컴포넌트

**DataDisplayDecorator 추상 클래스**:
- 모든 데코레이터의 기본 클래스
- `_innerDisplay`로 내부 컴포넌트 참조
- 기본 동작은 내부 컴포넌트에 위임

**ThresholdHighlightDecorator**:
- 임계값 초과 시 시각적 경고
- 원래 표시 동작은 그대로 유지
- 배경색과 테두리로 상태 표시
- Error (빨강) / Warning (주황) / Normal (투명)

**사용 시나리오**:
```csharp
var basicDisplay = new BasicDataDisplay(textBlock);
var withHighlight = new ThresholdHighlightDecorator(
    basicDisplay, border, 80.0, 95.0);
var withLogging = new LoggingDecorator(
    withHighlight, logger);

// 모든 데코레이터 기능이 적용됨
withLogging.Display(sensorData);
```

</div>
</div>

---

<div class="grid grid-cols-2 gap-8">
<div>

```csharp
// Concrete Decorator 2: 로깅 추가
public class LoggingDecorator : DataDisplayDecorator
{
    private readonly ILogger _logger;

    public LoggingDecorator(
        IDataDisplay innerDisplay,
        ILogger logger)
        : base(innerDisplay)
    {
        _logger = logger;
    }

    public override void Display(EquipmentData data)
    {
        _logger.LogInformation(
            "Displaying data: {Name} = {Value} {Unit}",
            data.Name, data.Value, data.Unit);

        var startTime = DateTime.UtcNow;

        try
        {
            _innerDisplay.Display(data);

            var elapsed = DateTime.UtcNow - startTime;
            _logger.LogDebug(
                "Display completed in {Elapsed}ms",
                elapsed.TotalMilliseconds);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex,
                "Failed to display data: {Name}",
                data.Name);
            throw;
        }
    }
}

// Concrete Decorator 3: 애니메이션 추가
public class AnimatedDisplayDecorator
    : DataDisplayDecorator
{
    private readonly FrameworkElement _element;
    private double _previousValue;

    public AnimatedDisplayDecorator(
        IDataDisplay innerDisplay,
        FrameworkElement element)
        : base(innerDisplay)
    {
        _element = element;
        _previousValue = 0;
    }

    public override void Display(EquipmentData data)
    {
        // 값이 크게 변경된 경우 애니메이션 효과
        var valueDiff = Math.Abs(
            data.Value - _previousValue);

        if (valueDiff > 10)
        {
            // 깜빡임 애니메이션
            var animation = new DoubleAnimation
            {
                From = 1.0,
                To = 0.3,
                Duration = TimeSpan.FromMilliseconds(200),
                AutoReverse = true,
                RepeatBehavior = new RepeatBehavior(2)
            };

            _element.BeginAnimation(
                UIElement.OpacityProperty,
                animation);
        }

        // 기본 표시 수행
        _innerDisplay.Display(data);

        _previousValue = data.Value;
    }
}

// Concrete Decorator 4: 단위 변환
public class UnitConversionDecorator
    : DataDisplayDecorator
{
    private readonly Func<double, double> _converter;
    private readonly string _targetUnit;

    public UnitConversionDecorator(
        IDataDisplay innerDisplay,
        Func<double, double> converter,
        string targetUnit)
        : base(innerDisplay)
    {
        _converter = converter;
        _targetUnit = targetUnit;
    }

    public override void Display(EquipmentData data)
    {
        // 값 변환
        var convertedData = new EquipmentData
        {
            Name = data.Name,
            Value = _converter(data.Value),
            Unit = _targetUnit,
            Timestamp = data.Timestamp
        };

        _innerDisplay.Display(convertedData);
    }
}
```

</div>
<div>

**LoggingDecorator**:
- 데이터 표시 전/후 로깅
- 성능 측정 (표시 시간)
- 예외 발생 시 상세 로그

**AnimatedDisplayDecorator**:
- 값 변화가 클 때 시각적 효과
- 이전 값과 비교하여 애니메이션 결정
- Opacity 애니메이션으로 주목도 향상
- 데이터 급변 시 사용자 주의 환기

**UnitConversionDecorator**:
- 단위 변환 로직 추가
- 원본 데이터는 변경하지 않음
- Celsius ↔ Fahrenheit
- Pa ↔ Torr ↔ mbar

**데코레이터 체인 구성**:
```csharp
// 기본 표시
IDataDisplay display = new BasicDataDisplay(
    textBlock);

// 임계값 강조 추가
display = new ThresholdHighlightDecorator(
    display, border, 80, 95);

// 애니메이션 추가
display = new AnimatedDisplayDecorator(
    display, container);

// 로깅 추가
display = new LoggingDecorator(
    display, logger);

// 섭씨를 화씨로 변환하여 표시
display = new UnitConversionDecorator(
    display,
    celsius => celsius * 9/5 + 32,
    "°F");

// 최종 사용
display.Display(temperatureData);
```

**실행 순서**:
1. UnitConversionDecorator: 섭씨 → 화씨
2. LoggingDecorator: 로그 기록
3. AnimatedDisplayDecorator: 애니메이션 체크
4. ThresholdHighlightDecorator: 임계값 강조
5. BasicDataDisplay: 실제 텍스트 표시

**장점**:
- 기능 조합의 유연성
- 런타임에 동적으로 추가/제거
- 단일 책임 원칙 준수
- 각 데코레이터는 하나의 기능만 담당

</div>
</div>

---

## WPF 고급 레이아웃 시스템

<div style="margin: 2rem 0;">

### 🏗️ 레이아웃 프로세스 심화

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #0d47a1;">Measure Pass:</strong> 각 요소가 필요한 공간 계산</li>
        <li><strong style="color: #0d47a1;">Arrange Pass:</strong> 실제 위치와 크기 할당</li>
        <li><strong style="color: #0d47a1;">Render Pass:</strong> 화면에 실제 그리기</li>
        <li><strong style="color: #0d47a1;">Hit Test Pass:</strong> 마우스/터치 입력 처리</li>
    </ul>
</div>

### 📊 성능 최적화 전략

<div style="background: #f3e5f5; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #9c27b0; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #4a148c;">가상화(Virtualization):</strong> 보이는 항목만 렌더링</li>
        <li><strong style="color: #4a148c;">캐싱:</strong> 레이아웃 결과 캐시하여 재계산 방지</li>
        <li><strong style="color: #4a148c;">지연 로딩:</strong> 필요할 때만 UI 요소 생성</li>
        <li><strong style="color: #4a148c;">렌더 변환:</strong> GPU 가속 변환 활용</li>
    </ul>
</div>

### 💡 반도체 환경에서의 고려사항

<div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #f39c12; margin: 1.5rem 0;">
    <p style="margin: 0; color: #856404; font-weight: 500; font-size: 1.1em;">
        ⚠️ 대량의 센서 데이터를 실시간 표시해야 하므로 UI 가상화와 효율적인 데이터 바인딩이 필수입니다.
    </p>
</div>

### 🔧 VirtualizingStackPanel 활용

```csharp
// 가상화 패널을 활용한 대용량 데이터 표시
public class EquipmentDataVirtualizingPanel : VirtualizingPanel, IScrollInfo
{
    private Size _extentSize;
    private Size _viewportSize;
    private Point _offset;
    private ScrollViewer _scrollOwner;

    // 아이템 크기 (고정)
    private readonly double _itemHeight = 50;
    private readonly double _itemWidth = 200;

    // 보이는 범위의 아이템만 생성
    protected override Size MeasureOverride(Size availableSize)
    {
        var itemsControl = ItemsControl.GetItemsOwner(this);
        if (itemsControl == null) return new Size();

        var itemCount = itemsControl.Items.Count;

        // 뷰포트 크기 계산
        _viewportSize = availableSize;

        // 전체 크기 계산
        _extentSize = new Size(_itemWidth, _itemHeight * itemCount);

        // 보이는 범위 계산
        var firstVisibleIndex = Math.Max(0, (int)Math.Floor(_offset.Y / _itemHeight));
        var lastVisibleIndex = Math.Min(itemCount - 1,
            (int)Math.Ceiling((_offset.Y + _viewportSize.Height) / _itemHeight));

        // 기존 컨테이너 정리
        var generator = ItemContainerGenerator;
        var startPos = generator.GeneratorPositionFromIndex(firstVisibleIndex);

        using (generator.StartAt(startPos, GeneratorDirection.Forward))
        {
            for (int i = firstVisibleIndex; i <= lastVisibleIndex; i++)
            {
                var container = generator.GenerateNext() as UIElement;
                if (container != null)
                {
                    if (!Children.Contains(container))
                    {
                        AddInternalChild(container);
                    }

                    // 아이템 측정
                    container.Measure(new Size(_itemWidth, _itemHeight));
                }
            }
        }

        // 보이지 않는 컨테이너 제거
        CleanupContainers(firstVisibleIndex, lastVisibleIndex);

        return availableSize;
    }

    protected override Size ArrangeOverride(Size finalSize)
    {
        var firstVisibleIndex = Math.Max(0, (int)Math.Floor(_offset.Y / _itemHeight));

        for (int i = 0; i < Children.Count; i++)
        {
            var child = Children[i];
            var itemIndex = firstVisibleIndex + i;

            // 아이템 위치 계산
            var rect = new Rect(
                0,
                itemIndex * _itemHeight - _offset.Y,
                _itemWidth,
                _itemHeight);

            child.Arrange(rect);
        }

        return finalSize;
    }

    private void CleanupContainers(int firstVisibleIndex, int lastVisibleIndex)
    {
        var generator = ItemContainerGenerator;

        for (int i = Children.Count - 1; i >= 0; i--)
        {
            var child = Children[i];
            var itemIndex = generator.IndexFromContainer(child);

            if (itemIndex < firstVisibleIndex || itemIndex > lastVisibleIndex)
            {
                RemoveInternalChildRange(i, 1);
                generator.Remove(GeneratorPosition.FromIndex(itemIndex), 1);
            }
        }
    }

    // IScrollInfo 구현
    public bool CanVerticallyScroll { get; set; }
    public bool CanHorizontallyScroll { get; set; }

    public double ExtentWidth => _extentSize.Width;
    public double ExtentHeight => _extentSize.Height;
    public double ViewportWidth => _viewportSize.Width;
    public double ViewportHeight => _viewportSize.Height;

    public double HorizontalOffset => _offset.X;
    public double VerticalOffset => _offset.Y;

    public ScrollViewer ScrollOwner
    {
        get => _scrollOwner;
        set => _scrollOwner = value;
    }

    public void SetVerticalOffset(double offset)
    {
        _offset.Y = Math.Max(0, Math.Min(offset, ExtentHeight - ViewportHeight));
        InvalidateMeasure();
        ScrollOwner?.InvalidateScrollInfo();
    }

    public void LineUp() => SetVerticalOffset(VerticalOffset - _itemHeight);
    public void LineDown() => SetVerticalOffset(VerticalOffset + _itemHeight);
    public void PageUp() => SetVerticalOffset(VerticalOffset - ViewportHeight);
    public void PageDown() => SetVerticalOffset(VerticalOffset + ViewportHeight);

    public void SetHorizontalOffset(double offset) { }
    public void LineLeft() { }
    public void LineRight() { }
    public void PageLeft() { }
    public void PageRight() { }

    public Rect MakeVisible(Visual visual, Rect rectangle) => rectangle;
}
```

</div>

---

## 사용자 정의 컨트롤 개발

<div style="margin: 2rem 0;">

### 🎨 컨트롤 개발 방식 비교

<div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #155724;">UserControl:</strong> 기존 컨트롤 조합, 빠른 개발</li>
        <li><strong style="color: #155724;">CustomControl:</strong> 완전한 재정의, 최대 유연성</li>
        <li><strong style="color: #155724;">Attached Property:</strong> 기존 컨트롤 확장</li>
        <li><strong style="color: #155724;">Behavior:</strong> 재사용 가능한 동작 정의</li>
    </ul>
</div>

### 💻 반도체 장비용 게이지 컨트롤

```csharp
// Themes/Generic.xaml
<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                    xmlns:local="clr-namespace:SemiconductorHMI.Controls">

    <Style TargetType="{x:Type local:CircularGauge}">
        <Setter Property="Width" Value="200"/>
        <Setter Property="Height" Value="200"/>
        <Setter Property="Background" Value="Transparent"/>
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="{x:Type local:CircularGauge}">
                    <Grid Background="{TemplateBinding Background}">
                        <Ellipse Stroke="#E0E0E0" StrokeThickness="8" Fill="Transparent"/>

                        <!-- 백그라운드 아크 -->
                        <Path x:Name="PART_BackgroundArc"
                              Stroke="#F5F5F5"
                              StrokeThickness="8"
                              StrokeLineCap="Round"
                              Fill="Transparent"/>

                        <!-- 값 아크 -->
                        <Path x:Name="PART_ValueArc"
                              Stroke="{TemplateBinding Foreground}"
                              StrokeThickness="8"
                              StrokeLineCap="Round"
                              Fill="Transparent"/>

                        <!-- 중앙 값 표시 -->
                        <StackPanel VerticalAlignment="Center" HorizontalAlignment="Center">
                            <TextBlock x:Name="PART_ValueText"
                                     Text="{TemplateBinding Value}"
                                     FontSize="24"
                                     FontWeight="Bold"
                                     HorizontalAlignment="Center"
                                     Foreground="{TemplateBinding Foreground}"/>
                            <TextBlock Text="{TemplateBinding Unit}"
                                     FontSize="12"
                                     HorizontalAlignment="Center"
                                     Foreground="#666666"/>
                        </StackPanel>

                        <!-- 최소/최대 레이블 -->
                        <TextBlock Text="{TemplateBinding Minimum}"
                                 FontSize="10"
                                 Foreground="#666666"
                                 HorizontalAlignment="Left"
                                 VerticalAlignment="Bottom"
                                 Margin="20,0,0,20"/>

                        <TextBlock Text="{TemplateBinding Maximum}"
                                 FontSize="10"
                                 Foreground="#666666"
                                 HorizontalAlignment="Right"
                                 VerticalAlignment="Bottom"
                                 Margin="0,0,20,20"/>
                    </Grid>
                </ControlTemplate>
            </Setter.Value>
        </Setter>
    </Style>
</ResourceDictionary>
```

```csharp
// CircularGauge.cs - 원형 게이지 커스텀 컨트롤
[TemplatePart(Name = "PART_ValueArc", Type = typeof(Path))]
[TemplatePart(Name = "PART_BackgroundArc", Type = typeof(Path))]
[TemplatePart(Name = "PART_ValueText", Type = typeof(TextBlock))]
public class CircularGauge : Control
{
    private Path _valueArc;
    private Path _backgroundArc;
    private TextBlock _valueText;

    static CircularGauge()
    {
        DefaultStyleKeyProperty.OverrideMetadata(typeof(CircularGauge),
            new FrameworkPropertyMetadata(typeof(CircularGauge)));
    }

    public override void OnApplyTemplate()
    {
        base.OnApplyTemplate();

        _valueArc = GetTemplateChild("PART_ValueArc") as Path;
        _backgroundArc = GetTemplateChild("PART_BackgroundArc") as Path;
        _valueText = GetTemplateChild("PART_ValueText") as TextBlock;

        UpdateGauge();
    }

    #region Dependency Properties

    public static readonly DependencyProperty ValueProperty =
        DependencyProperty.Register("Value", typeof(double), typeof(CircularGauge),
            new PropertyMetadata(0.0, OnValueChanged));

    public static readonly DependencyProperty MinimumProperty =
        DependencyProperty.Register("Minimum", typeof(double), typeof(CircularGauge),
            new PropertyMetadata(0.0, OnRangeChanged));

    public static readonly DependencyProperty MaximumProperty =
        DependencyProperty.Register("Maximum", typeof(double), typeof(CircularGauge),
            new PropertyMetadata(100.0, OnRangeChanged));

    public static readonly DependencyProperty UnitProperty =
        DependencyProperty.Register("Unit", typeof(string), typeof(CircularGauge),
            new PropertyMetadata(""));

    public static readonly DependencyProperty StartAngleProperty =
        DependencyProperty.Register("StartAngle", typeof(double), typeof(CircularGauge),
            new PropertyMetadata(-140.0, OnRangeChanged));

    public static readonly DependencyProperty EndAngleProperty =
        DependencyProperty.Register("EndAngle", typeof(double), typeof(CircularGauge),
            new PropertyMetadata(140.0, OnRangeChanged));

    public double Value
    {
        get => (double)GetValue(ValueProperty);
        set => SetValue(ValueProperty, value);
    }

    public double Minimum
    {
        get => (double)GetValue(MinimumProperty);
        set => SetValue(MinimumProperty, value);
    }

    public double Maximum
    {
        get => (double)GetValue(MaximumProperty);
        set => SetValue(MaximumProperty, value);
    }

    public string Unit
    {
        get => (string)GetValue(UnitProperty);
        set => SetValue(UnitProperty, value);
    }

    public double StartAngle
    {
        get => (double)GetValue(StartAngleProperty);
        set => SetValue(StartAngleProperty, value);
    }

    public double EndAngle
    {
        get => (double)GetValue(EndAngleProperty);
        set => SetValue(EndAngleProperty, value);
    }

    #endregion

    private static void OnValueChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is CircularGauge gauge)
        {
            gauge.UpdateGauge();
            gauge.AnimateToValue((double)e.NewValue);
        }
    }

    private static void OnRangeChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is CircularGauge gauge)
        {
            gauge.UpdateGauge();
        }
    }

    private void UpdateGauge()
    {
        if (_valueArc == null || _backgroundArc == null) return;

        var centerX = ActualWidth / 2;
        var centerY = ActualHeight / 2;
        var radius = Math.Min(centerX, centerY) - 20;

        // 백그라운드 아크 생성
        _backgroundArc.Data = CreateArcGeometry(centerX, centerY, radius, StartAngle, EndAngle);

        // 값 아크 생성
        var normalizedValue = (Value - Minimum) / (Maximum - Minimum);
        var valueAngle = StartAngle + (EndAngle - StartAngle) * normalizedValue;
        _valueArc.Data = CreateArcGeometry(centerX, centerY, radius, StartAngle, valueAngle);

        // 값 텍스트 업데이트
        if (_valueText != null)
        {
            _valueText.Text = Value.ToString("F1");
        }
    }

    private Geometry CreateArcGeometry(double centerX, double centerY, double radius,
        double startAngle, double endAngle)
    {
        var startAngleRad = startAngle * Math.PI / 180;
        var endAngleRad = endAngle * Math.PI / 180;

        var startPoint = new Point(
            centerX + radius * Math.Cos(startAngleRad),
            centerY + radius * Math.Sin(startAngleRad));

        var endPoint = new Point(
            centerX + radius * Math.Cos(endAngleRad),
            centerY + radius * Math.Sin(endAngleRad));

        var isLargeArc = Math.Abs(endAngle - startAngle) > 180;

        var pathGeometry = new PathGeometry();
        var pathFigure = new PathFigure { StartPoint = startPoint };

        var arcSegment = new ArcSegment
        {
            Point = endPoint,
            Size = new Size(radius, radius),
            IsLargeArc = isLargeArc,
            SweepDirection = SweepDirection.Clockwise
        };

        pathFigure.Segments.Add(arcSegment);
        pathGeometry.Figures.Add(pathFigure);

        return pathGeometry;
    }

    private void AnimateToValue(double newValue)
    {
        if (_valueArc == null) return;

        var currentAngle = GetCurrentValueAngle();
        var normalizedValue = (newValue - Minimum) / (Maximum - Minimum);
        var targetAngle = StartAngle + (EndAngle - StartAngle) * normalizedValue;

        var animation = new DoubleAnimation
        {
            From = currentAngle,
            To = targetAngle,
            Duration = TimeSpan.FromMilliseconds(500),
            EasingFunction = new QuadraticEase { EasingMode = EasingMode.EaseOut }
        };

        var storyboard = new Storyboard();
        storyboard.Children.Add(animation);

        Storyboard.SetTarget(animation, this);
        Storyboard.SetTargetProperty(animation, new PropertyPath("(local:CircularGauge.AnimatedAngle)"));

        storyboard.Begin();
    }

    private double GetCurrentValueAngle()
    {
        var normalizedValue = (Value - Minimum) / (Maximum - Minimum);
        return StartAngle + (EndAngle - StartAngle) * normalizedValue;
    }

    // 애니메이션을 위한 의존성 프로퍼티
    public static readonly DependencyProperty AnimatedAngleProperty =
        DependencyProperty.Register("AnimatedAngle", typeof(double), typeof(CircularGauge),
            new PropertyMetadata(0.0, OnAnimatedAngleChanged));

    public double AnimatedAngle
    {
        get => (double)GetValue(AnimatedAngleProperty);
        set => SetValue(AnimatedAngleProperty, value);
    }

    private static void OnAnimatedAngleChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is CircularGauge gauge && gauge._valueArc != null)
        {
            var centerX = gauge.ActualWidth / 2;
            var centerY = gauge.ActualHeight / 2;
            var radius = Math.Min(centerX, centerY) - 20;

            gauge._valueArc.Data = gauge.CreateArcGeometry(centerX, centerY, radius,
                gauge.StartAngle, (double)e.NewValue);
        }
    }
}
```

### 🔧 반도체 장비 상태 LED 컨트롤

```csharp
// StatusLED.cs - 상태 표시 LED 컨트롤
public class StatusLED : Control
{
    static StatusLED()
    {
        DefaultStyleKeyProperty.OverrideMetadata(typeof(StatusLED),
            new FrameworkPropertyMetadata(typeof(StatusLED)));
    }

    public static readonly DependencyProperty StatusProperty =
        DependencyProperty.Register("Status", typeof(EquipmentStatus), typeof(StatusLED),
            new PropertyMetadata(EquipmentStatus.Idle, OnStatusChanged));

    public static readonly DependencyProperty IsBlinkingProperty =
        DependencyProperty.Register("IsBlinking", typeof(bool), typeof(StatusLED),
            new PropertyMetadata(false, OnBlinkingChanged));

    public EquipmentStatus Status
    {
        get => (EquipmentStatus)GetValue(StatusProperty);
        set => SetValue(StatusProperty, value);
    }

    public bool IsBlinking
    {
        get => (bool)GetValue(IsBlinkingProperty);
        set => SetValue(IsBlinkingProperty, value);
    }

    private static void OnStatusChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is StatusLED led)
        {
            led.UpdateStatusColor();
            led.UpdateBlinkingBehavior();
        }
    }

    private static void OnBlinkingChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is StatusLED led)
        {
            led.UpdateBlinkingBehavior();
        }
    }

    private void UpdateStatusColor()
    {
        var color = Status switch
        {
            EquipmentStatus.Running => Colors.LimeGreen,
            EquipmentStatus.Warning => Colors.Orange,
            EquipmentStatus.Error => Colors.Red,
            EquipmentStatus.Maintenance => Colors.Blue,
            _ => Colors.Gray
        };

        SetValue(BackgroundProperty, new SolidColorBrush(color));
    }

    private void UpdateBlinkingBehavior()
    {
        if (IsBlinking && (Status == EquipmentStatus.Warning || Status == EquipmentStatus.Error))
        {
            StartBlinkingAnimation();
        }
        else
        {
            StopBlinkingAnimation();
        }
    }

    private void StartBlinkingAnimation()
    {
        var animation = new DoubleAnimation
        {
            From = 1.0,
            To = 0.3,
            Duration = TimeSpan.FromMilliseconds(500),
            AutoReverse = true,
            RepeatBehavior = RepeatBehavior.Forever
        };

        BeginAnimation(OpacityProperty, animation);
    }

    private void StopBlinkingAnimation()
    {
        BeginAnimation(OpacityProperty, null);
        Opacity = 1.0;
    }
}
```

</div>

---

## 디펜던시 프로퍼티 고급 활용

<div style="margin: 2rem 0;">

### ⚙️ 프로퍼티 메타데이터 고급 설정

<div style="background: #f3e5f5; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #9c27b0; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #4a148c;">Coercion:</strong> 값 범위 제한 및 유효성 검사</li>
        <li><strong style="color: #4a148c;">Value Inheritance:</strong> 부모에서 자식으로 값 전파</li>
        <li><strong style="color: #4a148c;">Animation:</strong> 값 변경 시 자동 애니메이션</li>
        <li><strong style="color: #4a148c;">Data Binding:</strong> 양방향 바인딩 지원</li>
    </ul>
</div>

### 💻 고급 디펜던시 프로퍼티 구현

```csharp
// 범위 제한 및 유효성 검사가 포함된 디펜던시 프로퍼티
public class TemperatureControl : Control
{
    public static readonly DependencyProperty TemperatureProperty =
        DependencyProperty.Register(
            "Temperature",
            typeof(double),
            typeof(TemperatureControl),
            new FrameworkPropertyMetadata(
                25.0,                              // 기본값
                FrameworkPropertyMetadataOptions.AffectsRender |
                FrameworkPropertyMetadataOptions.BindsTwoWayByDefault,
                OnTemperatureChanged,              // 변경 콜백
                CoerceTemperature),                // 값 강제 조정
            ValidateTemperature);                  // 유효성 검사

    public static readonly DependencyProperty MinTemperatureProperty =
        DependencyProperty.Register("MinTemperature", typeof(double), typeof(TemperatureControl),
            new PropertyMetadata(-50.0, OnRangeChanged));

    public static readonly DependencyProperty MaxTemperatureProperty =
        DependencyProperty.Register("MaxTemperature", typeof(double), typeof(TemperatureControl),
            new PropertyMetadata(300.0, OnRangeChanged));

    public double Temperature
    {
        get => (double)GetValue(TemperatureProperty);
        set => SetValue(TemperatureProperty, value);
    }

    public double MinTemperature
    {
        get => (double)GetValue(MinTemperatureProperty);
        set => SetValue(MinTemperatureProperty, value);
    }

    public double MaxTemperature
    {
        get => (double)GetValue(MaxTemperatureProperty);
        set => SetValue(MaxTemperatureProperty, value);
    }

    // 값 유효성 검사
    private static bool ValidateTemperature(object value)
    {
        if (value is double temp)
        {
            return !double.IsNaN(temp) && !double.IsInfinity(temp);
        }
        return false;
    }

    // 값 강제 조정 (범위 제한)
    private static object CoerceTemperature(DependencyObject d, object baseValue)
    {
        if (d is TemperatureControl control && baseValue is double temp)
        {
            var min = control.MinTemperature;
            var max = control.MaxTemperature;

            if (temp < min) return min;
            if (temp > max) return max;
            return temp;
        }
        return baseValue;
    }

    // 온도 변경 시 콜백
    private static void OnTemperatureChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is TemperatureControl control)
        {
            control.OnTemperatureChanged((double)e.OldValue, (double)e.NewValue);
        }
    }

    // 범위 변경 시 온도 값 재검증
    private static void OnRangeChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is TemperatureControl control)
        {
            // 현재 온도 값을 강제 조정
            control.CoerceValue(TemperatureProperty);
        }
    }

    private void OnTemperatureChanged(double oldValue, double newValue)
    {
        // 온도 변경에 따른 시각적 업데이트
        UpdateTemperatureVisuals(newValue);

        // 이벤트 발생
        TemperatureChanged?.Invoke(this, new TemperatureChangedEventArgs(oldValue, newValue));

        // 임계값 체크
        CheckTemperatureThresholds(newValue);
    }

    public event EventHandler<TemperatureChangedEventArgs> TemperatureChanged;

    private void UpdateTemperatureVisuals(double temperature)
    {
        // 온도에 따른 색상 변경
        var color = GetTemperatureColor(temperature);
        Background = new SolidColorBrush(color);

        // 온도 표시 텍스트 업데이트
        ToolTip = $"온도: {temperature:F1}°C";
    }

    private Color GetTemperatureColor(double temperature)
    {
        var normalizedTemp = (temperature - MinTemperature) / (MaxTemperature - MinTemperature);

        // 파란색(차가움) -> 빨간색(뜨거움) 그라데이션
        var red = (byte)(255 * normalizedTemp);
        var blue = (byte)(255 * (1 - normalizedTemp));
        var green = (byte)(128 * Math.Sin(normalizedTemp * Math.PI));

        return Color.FromRgb(red, green, blue);
    }

    private void CheckTemperatureThresholds(double temperature)
    {
        // 임계값에 따른 알람 발생
        if (temperature > MaxTemperature * 0.9)
        {
            TriggerWarningAlarm("온도가 위험 수준에 도달했습니다.");
        }
        else if (temperature < MinTemperature * 1.1)
        {
            TriggerWarningAlarm("온도가 너무 낮습니다.");
        }
    }

    private void TriggerWarningAlarm(string message)
    {
        // 알람 이벤트 발생 또는 시각적 경고 표시
        var animation = new ColorAnimation
        {
            To = Colors.Red,
            Duration = TimeSpan.FromMilliseconds(200),
            AutoReverse = true,
            RepeatBehavior = new RepeatBehavior(3)
        };

        var brush = Background as SolidColorBrush;
        brush?.BeginAnimation(SolidColorBrush.ColorProperty, animation);
    }
}

public class TemperatureChangedEventArgs : EventArgs
{
    public double OldValue { get; }
    public double NewValue { get; }

    public TemperatureChangedEventArgs(double oldValue, double newValue)
    {
        OldValue = oldValue;
        NewValue = newValue;
    }
}
```

</div>

