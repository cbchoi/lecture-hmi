# C# 고급 UI/UX 및 사용자 정의 컨트롤
> 반도체 장비 전용 고성능 사용자 인터페이스 개발

---

## 📋 오늘의 학습 목표

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #007bff; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #1a365d;">사용자 정의 컨트롤:</strong> 반도체 장비용 특화 컨트롤 개발</li>
        <li><strong style="color: #1a365d;">고급 레이아웃:</strong> 가상화와 성능 최적화 기법</li>
        <li><strong style="color: #1a365d;">3D 시각화:</strong> 장비 상태의 직관적 3차원 표현</li>
        <li><strong style="color: #1a365d;">접근성 향상:</strong> 산업용 환경을 위한 UX 개선</li>
    </ul>
</div>

---

## 🗺️ 강의 진행 순서

<div style="display: flex; flex-direction: column; gap: 1rem; margin: 1.5rem 0;">
    <div style="display: flex; align-items: center; background: #e8f5e8; padding: 1rem; border-radius: 8px;">
        <div style="background: #28a745; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">1</div>
        <span style="color: #155724;"><strong>이론 (45분):</strong> 고급 레이아웃 시스템과 컨트롤 개발</span>
    </div>
    <div style="display: flex; align-items: center; background: #e3f2fd; padding: 1rem; border-radius: 8px;">
        <div style="background: #2196f3; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">2</div>
        <span style="color: #0d47a1;"><strong>기초 실습 (45분):</strong> 사용자 정의 컨트롤 개발</span>
    </div>
    <div style="display: flex; align-items: center; background: #f3e5f5; padding: 1rem; border-radius: 8px;">
        <div style="background: #9c27b0; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">3</div>
        <span style="color: #4a148c;"><strong>심화 실습 (45분):</strong> 3D 시각화 및 애니메이션</span>
    </div>
    <div style="display: flex; align-items: center; background: #fff3cd; padding: 1rem; border-radius: 8px;">
        <div style="background: #f39c12; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">4</div>
        <span style="color: #856404;"><strong>Hands-on (45분):</strong> 종합 대시보드 시스템</span>
    </div>
</div>

---

# 📖 이론 강의 (45분)

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

# 💻 기초 실습 (45분)

---

## 실습 1: 반도체 장비 제어 패널 구현

<div style="margin: 2rem 0;">

### 🎛️ 종합 제어 패널 UserControl

```csharp
// EquipmentControlPanel.xaml
<UserControl x:Class="SemiconductorHMI.Controls.EquipmentControlPanel"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:local="clr-namespace:SemiconductorHMI.Controls">

    <UserControl.Resources>
        <!-- 제어 버튼 스타일 -->
        <Style x:Key="ControlButtonStyle" TargetType="Button">
            <Setter Property="Width" Value="120"/>
            <Setter Property="Height" Value="40"/>
            <Setter Property="Margin" Value="5"/>
            <Setter Property="FontWeight" Value="Medium"/>
            <Setter Property="BorderThickness" Value="0"/>
            <Setter Property="CornerRadius" Value="5"/>
            <Setter Property="Cursor" Value="Hand"/>
            <Style.Triggers>
                <Trigger Property="IsMouseOver" Value="True">
                    <Setter Property="Transform">
                        <Setter.Value>
                            <ScaleTransform ScaleX="1.05" ScaleY="1.05"/>
                        </Setter.Value>
                    </Setter>
                </Trigger>
            </Style.Triggers>
        </Style>

        <!-- 슬라이더 스타일 -->
        <Style x:Key="ParameterSliderStyle" TargetType="Slider">
            <Setter Property="Width" Value="200"/>
            <Setter Property="Height" Value="30"/>
            <Setter Property="Margin" Value="10,5"/>
            <Setter Property="IsSnapToTickEnabled" Value="True"/>
            <Setter Property="TickFrequency" Value="1"/>
            <Setter Property="TickPlacement" Value="BottomRight"/>
        </Style>
    </UserControl.Resources>

    <Border Background="White" CornerRadius="10" Padding="20"
            BorderBrush="#E0E0E0" BorderThickness="1">
        <Grid>
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="*"/>
                <RowDefinition Height="Auto"/>
            </Grid.RowDefinitions>

            <!-- 헤더 -->
            <Border Grid.Row="0" Background="#2C3E50" CornerRadius="5" Padding="15,10" Margin="0,0,0,15">
                <Grid>
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="Auto"/>
                    </Grid.ColumnDefinitions>

                    <StackPanel Grid.Column="0" Orientation="Horizontal">
                        <local:StatusLED Status="{Binding EquipmentStatus}"
                                       IsBlinking="{Binding IsAlarmActive}"
                                       Width="20" Height="20" Margin="0,0,10,0"/>
                        <TextBlock Text="{Binding EquipmentId}"
                                 FontSize="18" FontWeight="Bold" Foreground="White"/>
                    </StackPanel>

                    <TextBlock Grid.Column="1"
                             Text="{Binding LastUpdate, StringFormat='yyyy-MM-dd HH:mm:ss'}"
                             FontSize="12" Foreground="#BDC3C7" VerticalAlignment="Center"/>
                </Grid>
            </Border>

            <!-- 메인 제어 영역 -->
            <Grid Grid.Row="1">
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="*"/>
                </Grid.ColumnDefinitions>

                <!-- 왼쪽: 파라미터 제어 -->
                <StackPanel Grid.Column="0" Margin="0,0,10,0">
                    <TextBlock Text="공정 파라미터" FontSize="16" FontWeight="Bold" Margin="0,0,0,15"/>

                    <!-- 온도 제어 -->
                    <Border Background="#F8F9FA" CornerRadius="5" Padding="15" Margin="0,0,0,10">
                        <StackPanel>
                            <Grid>
                                <Grid.ColumnDefinitions>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="Auto"/>
                                </Grid.ColumnDefinitions>
                                <TextBlock Grid.Column="0" Text="온도 설정" FontWeight="Medium"/>
                                <TextBlock Grid.Column="1"
                                         Text="{Binding TargetTemperature, StringFormat='{}{0:F1}°C'}"
                                         FontWeight="Bold" Foreground="#E67E22"/>
                            </Grid>

                            <Slider Style="{StaticResource ParameterSliderStyle}"
                                  Minimum="0" Maximum="300"
                                  Value="{Binding TargetTemperature}"
                                  TickFrequency="25"/>

                            <Grid Margin="0,5,0,0">
                                <Grid.ColumnDefinitions>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="*"/>
                                </Grid.ColumnDefinitions>
                                <TextBlock Grid.Column="0" Text="현재:" FontSize="12" Foreground="#666"/>
                                <TextBlock Grid.Column="1"
                                         Text="{Binding CurrentTemperature, StringFormat='{}{0:F1}°C'}"
                                         FontSize="12" HorizontalAlignment="Right"/>
                            </Grid>
                        </StackPanel>
                    </Border>

                    <!-- 압력 제어 -->
                    <Border Background="#F8F9FA" CornerRadius="5" Padding="15" Margin="0,0,0,10">
                        <StackPanel>
                            <Grid>
                                <Grid.ColumnDefinitions>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="Auto"/>
                                </Grid.ColumnDefinitions>
                                <TextBlock Grid.Column="0" Text="압력 설정" FontWeight="Medium"/>
                                <TextBlock Grid.Column="1"
                                         Text="{Binding TargetPressure, StringFormat='{}{0:F3} Torr'}"
                                         FontWeight="Bold" Foreground="#3498DB"/>
                            </Grid>

                            <Slider Style="{StaticResource ParameterSliderStyle}"
                                  Minimum="0.001" Maximum="2.0"
                                  Value="{Binding TargetPressure}"
                                  TickFrequency="0.1"/>

                            <Grid Margin="0,5,0,0">
                                <Grid.ColumnDefinitions>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="*"/>
                                </Grid.ColumnDefinitions>
                                <TextBlock Grid.Column="0" Text="현재:" FontSize="12" Foreground="#666"/>
                                <TextBlock Grid.Column="1"
                                         Text="{Binding CurrentPressure, StringFormat='{}{0:F3} Torr'}"
                                         FontSize="12" HorizontalAlignment="Right"/>
                            </Grid>
                        </StackPanel>
                    </Border>

                    <!-- 유량 제어 -->
                    <Border Background="#F8F9FA" CornerRadius="5" Padding="15">
                        <StackPanel>
                            <Grid>
                                <Grid.ColumnDefinitions>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="Auto"/>
                                </Grid.ColumnDefinitions>
                                <TextBlock Grid.Column="0" Text="가스 유량" FontWeight="Medium"/>
                                <TextBlock Grid.Column="1"
                                         Text="{Binding TargetFlowRate, StringFormat='{}{0:F1} sccm'}"
                                         FontWeight="Bold" Foreground="#27AE60"/>
                            </Grid>

                            <Slider Style="{StaticResource ParameterSliderStyle}"
                                  Minimum="0" Maximum="500"
                                  Value="{Binding TargetFlowRate}"
                                  TickFrequency="50"/>

                            <Grid Margin="0,5,0,0">
                                <Grid.ColumnDefinitions>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="*"/>
                                </Grid.ColumnDefinitions>
                                <TextBlock Grid.Column="0" Text="현재:" FontSize="12" Foreground="#666"/>
                                <TextBlock Grid.Column="1"
                                         Text="{Binding CurrentFlowRate, StringFormat='{}{0:F1} sccm'}"
                                         FontSize="12" HorizontalAlignment="Right"/>
                            </Grid>
                        </StackPanel>
                    </Border>
                </StackPanel>

                <!-- 오른쪽: 상태 모니터링 -->
                <StackPanel Grid.Column="1" Margin="10,0,0,0">
                    <TextBlock Text="상태 모니터링" FontSize="16" FontWeight="Bold" Margin="0,0,0,15"/>

                    <!-- 원형 게이지들 -->
                    <Grid>
                        <Grid.RowDefinitions>
                            <RowDefinition Height="*"/>
                            <RowDefinition Height="*"/>
                        </Grid.RowDefinitions>
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition Width="*"/>
                            <ColumnDefinition Width="*"/>
                        </Grid.ColumnDefinitions>

                        <!-- 온도 게이지 -->
                        <local:CircularGauge Grid.Row="0" Grid.Column="0"
                                           Value="{Binding CurrentTemperature}"
                                           Minimum="0" Maximum="300"
                                           Unit="°C"
                                           Foreground="#E67E22"
                                           Width="120" Height="120"
                                           Margin="5"/>

                        <!-- 압력 게이지 -->
                        <local:CircularGauge Grid.Row="0" Grid.Column="1"
                                           Value="{Binding CurrentPressure}"
                                           Minimum="0" Maximum="2"
                                           Unit="Torr"
                                           Foreground="#3498DB"
                                           Width="120" Height="120"
                                           Margin="5"/>

                        <!-- 유량 게이지 -->
                        <local:CircularGauge Grid.Row="1" Grid.Column="0"
                                           Value="{Binding CurrentFlowRate}"
                                           Minimum="0" Maximum="500"
                                           Unit="sccm"
                                           Foreground="#27AE60"
                                           Width="120" Height="120"
                                           Margin="5"/>

                        <!-- 파워 게이지 -->
                        <local:CircularGauge Grid.Row="1" Grid.Column="1"
                                           Value="{Binding CurrentPower}"
                                           Minimum="0" Maximum="5000"
                                           Unit="W"
                                           Foreground="#9B59B6"
                                           Width="120" Height="120"
                                           Margin="5"/>
                    </Grid>
                </StackPanel>
            </Grid>

            <!-- 하단: 제어 버튼 -->
            <Border Grid.Row="2" Background="#ECF0F1" CornerRadius="5" Padding="15" Margin="0,15,0,0">
                <Grid>
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="*"/>
                    </Grid.ColumnDefinitions>

                    <Button Grid.Column="0" Style="{StaticResource ControlButtonStyle}"
                            Command="{Binding StartProcessCommand}"
                            Background="#27AE60" Foreground="White">
                        <StackPanel Orientation="Horizontal">
                            <TextBlock Text="▶" FontSize="14" Margin="0,0,5,0"/>
                            <TextBlock Text="공정 시작"/>
                        </StackPanel>
                    </Button>

                    <Button Grid.Column="1" Style="{StaticResource ControlButtonStyle}"
                            Command="{Binding StopProcessCommand}"
                            Background="#E74C3C" Foreground="White">
                        <StackPanel Orientation="Horizontal">
                            <TextBlock Text="⏹" FontSize="14" Margin="0,0,5,0"/>
                            <TextBlock Text="공정 정지"/>
                        </StackPanel>
                    </Button>

                    <Button Grid.Column="2" Style="{StaticResource ControlButtonStyle}"
                            Command="{Binding PauseProcessCommand}"
                            Background="#F39C12" Foreground="White">
                        <StackPanel Orientation="Horizontal">
                            <TextBlock Text="⏸" FontSize="14" Margin="0,0,5,0"/>
                            <TextBlock Text="일시정지"/>
                        </StackPanel>
                    </Button>

                    <Button Grid.Column="3" Style="{StaticResource ControlButtonStyle}"
                            Command="{Binding MaintenanceCommand}"
                            Background="#9B59B6" Foreground="White">
                        <StackPanel Orientation="Horizontal">
                            <TextBlock Text="🔧" FontSize="14" Margin="0,0,5,0"/>
                            <TextBlock Text="정비모드"/>
                        </StackPanel>
                    </Button>
                </Grid>
            </Border>
        </Grid>
    </Border>
</UserControl>
```

### 🎯 제어 패널 ViewModel

```csharp
// EquipmentControlPanelViewModel.cs
public class EquipmentControlPanelViewModel : BaseViewModel
{
    private string _equipmentId;
    private EquipmentStatus _equipmentStatus;
    private bool _isAlarmActive;
    private DateTime _lastUpdate;

    // 현재 값들
    private double _currentTemperature;
    private double _currentPressure;
    private double _currentFlowRate;
    private double _currentPower;

    // 목표 값들
    private double _targetTemperature;
    private double _targetPressure;
    private double _targetFlowRate;

    // Properties
    public string EquipmentId
    {
        get => _equipmentId;
        set => SetProperty(ref _equipmentId, value);
    }

    public EquipmentStatus EquipmentStatus
    {
        get => _equipmentStatus;
        set => SetProperty(ref _equipmentStatus, value);
    }

    public bool IsAlarmActive
    {
        get => _isAlarmActive;
        set => SetProperty(ref _isAlarmActive, value);
    }

    public DateTime LastUpdate
    {
        get => _lastUpdate;
        set => SetProperty(ref _lastUpdate, value);
    }

    public double CurrentTemperature
    {
        get => _currentTemperature;
        set => SetProperty(ref _currentTemperature, value);
    }

    public double CurrentPressure
    {
        get => _currentPressure;
        set => SetProperty(ref _currentPressure, value);
    }

    public double CurrentFlowRate
    {
        get => _currentFlowRate;
        set => SetProperty(ref _currentFlowRate, value);
    }

    public double CurrentPower
    {
        get => _currentPower;
        set => SetProperty(ref _currentPower, value);
    }

    public double TargetTemperature
    {
        get => _targetTemperature;
        set
        {
            if (SetProperty(ref _targetTemperature, value))
            {
                SendParameterUpdate("Temperature", value);
            }
        }
    }

    public double TargetPressure
    {
        get => _targetPressure;
        set
        {
            if (SetProperty(ref _targetPressure, value))
            {
                SendParameterUpdate("Pressure", value);
            }
        }
    }

    public double TargetFlowRate
    {
        get => _targetFlowRate;
        set
        {
            if (SetProperty(ref _targetFlowRate, value))
            {
                SendParameterUpdate("FlowRate", value);
            }
        }
    }

    // Commands
    public ICommand StartProcessCommand { get; }
    public ICommand StopProcessCommand { get; }
    public ICommand PauseProcessCommand { get; }
    public ICommand MaintenanceCommand { get; }

    public EquipmentControlPanelViewModel(string equipmentId)
    {
        EquipmentId = equipmentId;
        EquipmentStatus = EquipmentStatus.Idle;
        LastUpdate = DateTime.Now;

        // 초기값 설정
        TargetTemperature = 200.0;
        TargetPressure = 0.8;
        TargetFlowRate = 150.0;

        CurrentTemperature = 25.0;
        CurrentPressure = 0.001;
        CurrentFlowRate = 0.0;
        CurrentPower = 0.0;

        InitializeCommands();
        StartDataSimulation();
    }

    private void InitializeCommands()
    {
        StartProcessCommand = new RelayCommand(ExecuteStartProcess, CanStartProcess);
        StopProcessCommand = new RelayCommand(ExecuteStopProcess, CanStopProcess);
        PauseProcessCommand = new RelayCommand(ExecutePauseProcess, CanPauseProcess);
        MaintenanceCommand = new RelayCommand(ExecuteMaintenance, CanEnterMaintenance);
    }

    private bool CanStartProcess()
    {
        return EquipmentStatus == EquipmentStatus.Idle ||
               EquipmentStatus == EquipmentStatus.Maintenance;
    }

    private void ExecuteStartProcess()
    {
        EquipmentStatus = EquipmentStatus.Running;
        IsAlarmActive = false;

        // 공정 시작 로직
        StartProcessSimulation();
    }

    private bool CanStopProcess()
    {
        return EquipmentStatus != EquipmentStatus.Idle;
    }

    private void ExecuteStopProcess()
    {
        EquipmentStatus = EquipmentStatus.Idle;
        IsAlarmActive = false;

        // 공정 정지 로직
        StopProcessSimulation();
    }

    private bool CanPauseProcess()
    {
        return EquipmentStatus == EquipmentStatus.Running;
    }

    private void ExecutePauseProcess()
    {
        // 일시정지 구현
        MessageBox.Show("공정이 일시정지되었습니다.", "정보",
            MessageBoxButton.OK, MessageBoxImage.Information);
    }

    private bool CanEnterMaintenance()
    {
        return EquipmentStatus == EquipmentStatus.Idle ||
               EquipmentStatus == EquipmentStatus.Error;
    }

    private void ExecuteMaintenance()
    {
        EquipmentStatus = EquipmentStatus.Maintenance;
        IsAlarmActive = false;

        // 정비 모드 진입
        EnterMaintenanceMode();
    }

    private void SendParameterUpdate(string parameterName, double value)
    {
        // 실제로는 장비로 파라미터 전송
        Console.WriteLine($"{EquipmentId}: {parameterName} = {value}");
        LastUpdate = DateTime.Now;
    }

    private void StartDataSimulation()
    {
        var timer = new Timer(UpdateSimulationData, null,
            TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1));
    }

    private void UpdateSimulationData(object state)
    {
        Application.Current.Dispatcher.InvokeAsync(() =>
        {
            if (EquipmentStatus == EquipmentStatus.Running)
            {
                // 목표값으로 서서히 수렴
                CurrentTemperature = ApproachTarget(CurrentTemperature, TargetTemperature, 2.0);
                CurrentPressure = ApproachTarget(CurrentPressure, TargetPressure, 0.02);
                CurrentFlowRate = ApproachTarget(CurrentFlowRate, TargetFlowRate, 5.0);
                CurrentPower = CalculatePower();

                // 알람 조건 체크
                CheckAlarmConditions();
            }
            else if (EquipmentStatus == EquipmentStatus.Idle)
            {
                // 대기 상태로 복귀
                CurrentTemperature = ApproachTarget(CurrentTemperature, 25.0, 1.0);
                CurrentPressure = ApproachTarget(CurrentPressure, 0.001, 0.01);
                CurrentFlowRate = ApproachTarget(CurrentFlowRate, 0.0, 3.0);
                CurrentPower = 0.0;
            }

            LastUpdate = DateTime.Now;
        });
    }

    private double ApproachTarget(double current, double target, double step)
    {
        var difference = target - current;
        if (Math.Abs(difference) < step)
            return target;

        return current + Math.Sign(difference) * step +
               (Random.Shared.NextDouble() - 0.5) * step * 0.1;
    }

    private double CalculatePower()
    {
        // 파워는 온도와 압력의 함수로 계산
        return (CurrentTemperature - 25) * 10 + CurrentPressure * 1000 +
               (Random.Shared.NextDouble() - 0.5) * 100;
    }

    private void CheckAlarmConditions()
    {
        var hasAlarm = false;

        // 온도 알람
        if (CurrentTemperature > TargetTemperature * 1.1)
        {
            hasAlarm = true;
        }

        // 압력 알람
        if (CurrentPressure > TargetPressure * 1.2)
        {
            hasAlarm = true;
        }

        if (hasAlarm && !IsAlarmActive)
        {
            IsAlarmActive = true;
            EquipmentStatus = EquipmentStatus.Warning;
        }
        else if (!hasAlarm && IsAlarmActive)
        {
            IsAlarmActive = false;
            EquipmentStatus = EquipmentStatus.Running;
        }
    }

    private void StartProcessSimulation()
    {
        // 공정 시작 시뮬레이션
        Task.Run(async () =>
        {
            await Task.Delay(2000); // 2초 예열 시간

            Application.Current.Dispatcher.Invoke(() =>
            {
                if (EquipmentStatus == EquipmentStatus.Running)
                {
                    // 공정 안정화 완료
                    Console.WriteLine($"{EquipmentId} 공정이 안정화되었습니다.");
                }
            });
        });
    }

    private void StopProcessSimulation()
    {
        // 공정 정지 시뮬레이션
        Task.Run(async () =>
        {
            await Task.Delay(1000); // 1초 정지 시간

            Application.Current.Dispatcher.Invoke(() =>
            {
                Console.WriteLine($"{EquipmentId} 공정이 정지되었습니다.");
            });
        });
    }

    private void EnterMaintenanceMode()
    {
        // 정비 모드 진입 로직
        var maintenanceWindow = new MaintenanceWindow(this);
        maintenanceWindow.Show();
    }
}
```

</div>

---

## 실습 2: 고급 데이터 템플릿 및 스타일링

<div style="margin: 2rem 0;">

### 🎨 동적 스타일 시스템

```csharp
// DynamicStyleManager.cs - 런타임 스타일 변경
public class DynamicStyleManager : INotifyPropertyChanged
{
    private static DynamicStyleManager _instance;
    public static DynamicStyleManager Instance => _instance ??= new DynamicStyleManager();

    private ThemeType _currentTheme;
    private Dictionary<string, ResourceDictionary> _themes;

    public event PropertyChangedEventHandler PropertyChanged;

    public ThemeType CurrentTheme
    {
        get => _currentTheme;
        set
        {
            if (SetProperty(ref _currentTheme, value))
            {
                ApplyTheme(value);
            }
        }
    }

    private DynamicStyleManager()
    {
        _themes = new Dictionary<string, ResourceDictionary>();
        LoadThemes();
        CurrentTheme = ThemeType.Light;
    }

    private void LoadThemes()
    {
        // 라이트 테마
        var lightTheme = new ResourceDictionary();
        lightTheme.Add("PrimaryColor", new SolidColorBrush(Color.FromRgb(52, 152, 219)));
        lightTheme.Add("SecondaryColor", new SolidColorBrush(Color.FromRgb(46, 204, 113)));
        lightTheme.Add("BackgroundColor", new SolidColorBrush(Colors.White));
        lightTheme.Add("TextColor", new SolidColorBrush(Color.FromRgb(44, 62, 80)));
        lightTheme.Add("BorderColor", new SolidColorBrush(Color.FromRgb(224, 224, 224)));

        // 다크 테마
        var darkTheme = new ResourceDictionary();
        darkTheme.Add("PrimaryColor", new SolidColorBrush(Color.FromRgb(155, 89, 182)));
        darkTheme.Add("SecondaryColor", new SolidColorBrush(Color.FromRgb(230, 126, 34)));
        darkTheme.Add("BackgroundColor", new SolidColorBrush(Color.FromRgb(44, 62, 80)));
        darkTheme.Add("TextColor", new SolidColorBrush(Colors.White));
        darkTheme.Add("BorderColor", new SolidColorBrush(Color.FromRgb(127, 140, 141)));

        // 산업용 테마 (고대비)
        var industrialTheme = new ResourceDictionary();
        industrialTheme.Add("PrimaryColor", new SolidColorBrush(Color.FromRgb(255, 193, 7)));
        industrialTheme.Add("SecondaryColor", new SolidColorBrush(Color.FromRgb(255, 87, 34)));
        industrialTheme.Add("BackgroundColor", new SolidColorBrush(Color.FromRgb(33, 37, 41)));
        industrialTheme.Add("TextColor", new SolidColorBrush(Colors.White));
        industrialTheme.Add("BorderColor", new SolidColorBrush(Color.FromRgb(108, 117, 125)));

        _themes["Light"] = lightTheme;
        _themes["Dark"] = darkTheme;
        _themes["Industrial"] = industrialTheme;
    }

    private void ApplyTheme(ThemeType theme)
    {
        var app = Application.Current;
        if (app?.Resources == null) return;

        var themeName = theme.ToString();
        if (!_themes.ContainsKey(themeName)) return;

        var themeResources = _themes[themeName];

        // 기존 테마 리소스 제거
        var keysToRemove = new List<object>();
        foreach (var key in app.Resources.Keys)
        {
            if (key.ToString().EndsWith("Color"))
            {
                keysToRemove.Add(key);
            }
        }

        foreach (var key in keysToRemove)
        {
            app.Resources.Remove(key);
        }

        // 새 테마 적용
        foreach (var kvp in themeResources)
        {
            app.Resources[kvp.Key] = kvp.Value;
        }

        // 테마 변경 이벤트 발생
        ThemeChanged?.Invoke(this, new ThemeChangedEventArgs(theme));
    }

    public event EventHandler<ThemeChangedEventArgs> ThemeChanged;

    private bool SetProperty<T>(ref T backingStore, T value, [CallerMemberName] string propertyName = "")
    {
        if (EqualityComparer<T>.Default.Equals(backingStore, value))
            return false;

        backingStore = value;
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        return true;
    }
}

public enum ThemeType
{
    Light,
    Dark,
    Industrial
}

public class ThemeChangedEventArgs : EventArgs
{
    public ThemeType NewTheme { get; }

    public ThemeChangedEventArgs(ThemeType newTheme)
    {
        NewTheme = newTheme;
    }
}
```

### 🎯 조건부 데이터 템플릿

```csharp
// ConditionalDataTemplateSelector.cs
public class EquipmentStatusTemplateSelector : DataTemplateSelector
{
    public DataTemplate RunningTemplate { get; set; }
    public DataTemplate WarningTemplate { get; set; }
    public DataTemplate ErrorTemplate { get; set; }
    public DataTemplate IdleTemplate { get; set; }
    public DataTemplate MaintenanceTemplate { get; set; }

    public override DataTemplate SelectTemplate(object item, DependencyObject container)
    {
        if (item is EquipmentViewModel equipment)
        {
            return equipment.Status switch
            {
                EquipmentStatus.Running => RunningTemplate,
                EquipmentStatus.Warning => WarningTemplate,
                EquipmentStatus.Error => ErrorTemplate,
                EquipmentStatus.Maintenance => MaintenanceTemplate,
                _ => IdleTemplate
            };
        }

        return base.SelectTemplate(item, container);
    }
}
```

```xml
<!-- EquipmentStatusTemplates.xaml -->
<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                    xmlns:local="clr-namespace:SemiconductorHMI.Controls">

    <!-- Running 상태 템플릿 -->
    <DataTemplate x:Key="RunningTemplate">
        <Border Background="#E8F5E8" BorderBrush="#27AE60" BorderThickness="2"
                CornerRadius="8" Padding="15">
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="Auto"/>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="Auto"/>
                </Grid.ColumnDefinitions>

                <!-- 상태 아이콘 -->
                <Ellipse Grid.Column="0" Width="24" Height="24"
                         Fill="#27AE60" Margin="0,0,10,0">
                    <Ellipse.Effect>
                        <DropShadowEffect Color="#27AE60" BlurRadius="8" Opacity="0.6"/>
                    </Ellipse.Effect>
                </Ellipse>

                <!-- 장비 정보 -->
                <StackPanel Grid.Column="1">
                    <TextBlock Text="{Binding EquipmentId}" FontWeight="Bold" FontSize="16"/>
                    <TextBlock Text="정상 운전 중" Foreground="#27AE60" FontWeight="Medium"/>
                    <StackPanel Orientation="Horizontal" Margin="0,5,0,0">
                        <TextBlock Text="온도: " FontSize="12"/>
                        <TextBlock Text="{Binding TemperatureText}" FontSize="12" FontWeight="Medium"/>
                        <TextBlock Text=" | 압력: " FontSize="12" Margin="10,0,0,0"/>
                        <TextBlock Text="{Binding PressureText}" FontSize="12" FontWeight="Medium"/>
                    </StackPanel>
                </StackPanel>

                <!-- 진행률 표시 -->
                <StackPanel Grid.Column="2">
                    <TextBlock Text="가동률" FontSize="10" Foreground="#666" HorizontalAlignment="Center"/>
                    <TextBlock Text="98%" FontSize="16" FontWeight="Bold"
                               Foreground="#27AE60" HorizontalAlignment="Center"/>
                </StackPanel>
            </Grid>
        </Border>
    </DataTemplate>

    <!-- Warning 상태 템플릿 -->
    <DataTemplate x:Key="WarningTemplate">
        <Border Background="#FFF3CD" BorderBrush="#F39C12" BorderThickness="2"
                CornerRadius="8" Padding="15">
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="Auto"/>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="Auto"/>
                </Grid.ColumnDefinitions>

                <!-- 경고 아이콘 (깜빡임) -->
                <Grid Grid.Column="0" Width="24" Height="24" Margin="0,0,10,0">
                    <Ellipse Fill="#F39C12"/>
                    <TextBlock Text="⚠" FontSize="14" Foreground="White"
                               HorizontalAlignment="Center" VerticalAlignment="Center"/>
                    <Grid.Triggers>
                        <EventTrigger RoutedEvent="Loaded">
                            <BeginStoryboard>
                                <Storyboard RepeatBehavior="Forever">
                                    <DoubleAnimation Storyboard.TargetProperty="Opacity"
                                                   From="1" To="0.3" Duration="0:0:0.8"
                                                   AutoReverse="True"/>
                                </Storyboard>
                            </BeginStoryboard>
                        </EventTrigger>
                    </Grid.Triggers>
                </Grid>

                <StackPanel Grid.Column="1">
                    <TextBlock Text="{Binding EquipmentId}" FontWeight="Bold" FontSize="16"/>
                    <TextBlock Text="주의 필요" Foreground="#F39C12" FontWeight="Medium"/>
                    <TextBlock Text="파라미터 확인 필요" FontSize="12" Foreground="#E67E22"/>
                </StackPanel>

                <Button Grid.Column="2" Content="확인" Background="#F39C12" Foreground="White"
                        Padding="10,5" BorderThickness="0" CornerRadius="3"/>
            </Grid>
        </Border>
    </DataTemplate>

    <!-- Error 상태 템플릿 -->
    <DataTemplate x:Key="ErrorTemplate">
        <Border Background="#F8D7DA" BorderBrush="#E74C3C" BorderThickness="2"
                CornerRadius="8" Padding="15">
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="Auto"/>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="Auto"/>
                </Grid.ColumnDefinitions>

                <!-- 오류 아이콘 -->
                <Grid Grid.Column="0" Width="24" Height="24" Margin="0,0,10,0">
                    <Ellipse Fill="#E74C3C"/>
                    <TextBlock Text="✕" FontSize="14" Foreground="White"
                               HorizontalAlignment="Center" VerticalAlignment="Center"/>
                </Grid>

                <StackPanel Grid.Column="1">
                    <TextBlock Text="{Binding EquipmentId}" FontWeight="Bold" FontSize="16"/>
                    <TextBlock Text="오류 발생" Foreground="#E74C3C" FontWeight="Medium"/>
                    <TextBlock Text="즉시 조치 필요" FontSize="12" Foreground="#C0392B"/>
                </StackPanel>

                <StackPanel Grid.Column="2">
                    <Button Content="진단" Background="#E74C3C" Foreground="White"
                            Padding="10,5" BorderThickness="0" CornerRadius="3" Margin="0,0,0,5"/>
                    <Button Content="리셋" Background="#95A5A6" Foreground="White"
                            Padding="10,5" BorderThickness="0" CornerRadius="3"/>
                </StackPanel>
            </Grid>
        </Border>
    </DataTemplate>

    <!-- 템플릿 셀렉터 -->
    <local:EquipmentStatusTemplateSelector x:Key="StatusTemplateSelector"
                                         RunningTemplate="{StaticResource RunningTemplate}"
                                         WarningTemplate="{StaticResource WarningTemplate}"
                                         ErrorTemplate="{StaticResource ErrorTemplate}"
                                         IdleTemplate="{StaticResource IdleTemplate}"
                                         MaintenanceTemplate="{StaticResource MaintenanceTemplate}"/>
</ResourceDictionary>
```

</div>

---

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

# Hands-on: 종합 대시보드 및 테마 시스템 (45분)

## 최종 통합 대시보드 구현

### 메인 대시보드 레이아웃

<div class="code-section">

**MainDashboard.xaml - 전체 레이아웃**

```xml
<Window x:Class="SemiconductorHMI.Views.MainDashboard"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:controls="clr-namespace:SemiconductorHMI.Controls"
        xmlns:helix="http://helix-toolkit.org/wpf"
        Title="반도체 장비 통합 모니터링 시스템"
        Height="1080" Width="1920"
        WindowState="Maximized"
        WindowStartupLocation="CenterScreen">

    <Window.Resources>
        <ResourceDictionary>
            <ResourceDictionary.MergedDictionaries>
                <ResourceDictionary Source="/Themes/DarkTheme.xaml"/>
                <ResourceDictionary Source="/Themes/LightTheme.xaml"/>
                <ResourceDictionary Source="/Controls/ControlTemplates.xaml"/>
            </ResourceDictionary.MergedDictionaries>
        </ResourceDictionary>
    </Window.Resources>

    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="60"/>      <!-- 헤더 -->
            <RowDefinition Height="*"/>       <!-- 메인 컨텐츠 -->
            <RowDefinition Height="40"/>      <!-- 상태바 -->
        </Grid.RowDefinitions>

        <!-- 헤더 영역 -->
        <Border Grid.Row="0" Background="{DynamicResource HeaderBackgroundBrush}">
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="200"/>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="300"/>
                </Grid.ColumnDefinitions>

                <!-- 로고 및 타이틀 -->
                <StackPanel Grid.Column="0" Orientation="Horizontal" VerticalAlignment="Center" Margin="10,0">
                    <Image Source="/Assets/CompanyLogo.png" Width="40" Height="40" Margin="0,0,10,0"/>
                    <TextBlock Text="SemiHMI Pro" FontSize="18" FontWeight="Bold"
                              Foreground="{DynamicResource PrimaryTextBrush}" VerticalAlignment="Center"/>
                </StackPanel>

                <!-- 중앙 검색 및 네비게이션 -->
                <StackPanel Grid.Column="1" Orientation="Horizontal" HorizontalAlignment="Center" VerticalAlignment="Center">
                    <Button Content="개요" Style="{DynamicResource NavigationButtonStyle}" Command="{Binding ShowOverviewCommand}"/>
                    <Button Content="공정 모니터링" Style="{DynamicResource NavigationButtonStyle}" Command="{Binding ShowProcessCommand}"/>
                    <Button Content="알람" Style="{DynamicResource NavigationButtonStyle}" Command="{Binding ShowAlarmsCommand}"/>
                    <Button Content="보고서" Style="{DynamicResource NavigationButtonStyle}" Command="{Binding ShowReportsCommand}"/>
                    <Button Content="설정" Style="{DynamicResource NavigationButtonStyle}" Command="{Binding ShowSettingsCommand}"/>
                </StackPanel>

                <!-- 사용자 정보 및 시스템 상태 -->
                <StackPanel Grid.Column="2" Orientation="Horizontal" HorizontalAlignment="Right" VerticalAlignment="Center" Margin="10,0">
                    <!-- 테마 전환 버튼 -->
                    <ToggleButton x:Name="ThemeToggle" Style="{DynamicResource ThemeToggleStyle}"
                                 IsChecked="{Binding IsDarkTheme, Mode=TwoWay}"
                                 ToolTip="테마 전환"/>

                    <!-- 알림 버튼 -->
                    <Button Style="{DynamicResource IconButtonStyle}" Command="{Binding ShowNotificationsCommand}">
                        <Grid>
                            <Path Data="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"
                                  Fill="{DynamicResource IconBrush}"/>
                            <Ellipse Width="8" Height="8" Fill="Red" HorizontalAlignment="Right" VerticalAlignment="Top"
                                    Visibility="{Binding HasNewNotifications, Converter={StaticResource BoolToVisibilityConverter}}"/>
                        </Grid>
                    </Button>

                    <!-- 사용자 정보 -->
                    <StackPanel Orientation="Horizontal" Margin="10,0,0,0">
                        <Ellipse Width="30" Height="30" Fill="{DynamicResource UserAvatarBrush}"/>
                        <TextBlock Text="{Binding CurrentUser.Name}" Margin="8,0,0,0" VerticalAlignment="Center"
                                  Foreground="{DynamicResource PrimaryTextBrush}"/>
                    </StackPanel>
                </StackPanel>
            </Grid>
        </Border>

        <!-- 메인 컨텐츠 영역 -->
        <Grid Grid.Row="1">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="300"/>   <!-- 왼쪽 패널 -->
                <ColumnDefinition Width="5"/>     <!-- 스플리터 -->
                <ColumnDefinition Width="*"/>     <!-- 중앙 컨텐츠 -->
                <ColumnDefinition Width="5"/>     <!-- 스플리터 -->
                <ColumnDefinition Width="300"/>   <!-- 오른쪽 패널 -->
            </Grid.ColumnDefinitions>

            <!-- 왼쪽 장비 리스트 패널 -->
            <Border Grid.Column="0" Background="{DynamicResource SidePanelBackgroundBrush}" BorderBrush="{DynamicResource BorderBrush}" BorderThickness="0,0,1,0">
                <ScrollViewer>
                    <StackPanel Margin="10">
                        <TextBlock Text="장비 목록" FontSize="16" FontWeight="Bold" Margin="0,0,0,10"
                                  Foreground="{DynamicResource PrimaryTextBrush}"/>

                        <ItemsControl ItemsSource="{Binding EquipmentList}">
                            <ItemsControl.ItemTemplate>
                                <DataTemplate>
                                    <controls:EquipmentListItem Equipment="{Binding}" Margin="0,2"/>
                                </DataTemplate>
                            </ItemsControl.ItemTemplate>
                        </ItemsControl>
                    </StackPanel>
                </ScrollViewer>
            </Border>

            <!-- 스플리터 -->
            <GridSplitter Grid.Column="1" HorizontalAlignment="Stretch" Background="{DynamicResource SplitterBrush}"/>

            <!-- 중앙 메인 컨텐츠 -->
            <Grid Grid.Column="2">
                <Grid.RowDefinitions>
                    <RowDefinition Height="2*"/>    <!-- 3D 뷰 -->
                    <RowDefinition Height="5"/>     <!-- 스플리터 -->
                    <RowDefinition Height="1*"/>    <!-- 차트 영역 -->
                </Grid.RowDefinitions>

                <!-- 3D 장비 시각화 영역 -->
                <Border Grid.Row="0" Background="{DynamicResource MainContentBackgroundBrush}"
                       BorderBrush="{DynamicResource BorderBrush}" BorderThickness="1" Margin="5">
                    <Grid>
                        <Grid.RowDefinitions>
                            <RowDefinition Height="Auto"/>
                            <RowDefinition Height="*"/>
                        </Grid.RowDefinitions>

                        <!-- 3D 뷰 헤더 -->
                        <Border Grid.Row="0" Background="{DynamicResource CardHeaderBackgroundBrush}" Padding="10,5">
                            <Grid>
                                <Grid.ColumnDefinitions>
                                    <ColumnDefinition Width="*"/>
                                    <ColumnDefinition Width="Auto"/>
                                </Grid.ColumnDefinitions>

                                <TextBlock Grid.Column="0" Text="장비 3D 모니터링" FontWeight="Bold"
                                          Foreground="{DynamicResource PrimaryTextBrush}"/>

                                <StackPanel Grid.Column="1" Orientation="Horizontal">
                                    <Button Content="리셋 뷰" Style="{DynamicResource SecondaryButtonStyle}" Margin="5,0"/>
                                    <Button Content="전체화면" Style="{DynamicResource SecondaryButtonStyle}" Margin="5,0"/>
                                </StackPanel>
                            </Grid>
                        </Border>

                        <!-- 3D 뷰포트 -->
                        <controls:Equipment3DVisualizer Grid.Row="1" x:Name="Equipment3DView"
                                                       SelectedEquipment="{Binding SelectedEquipment}"/>
                    </Grid>
                </Border>

                <!-- 스플리터 -->
                <GridSplitter Grid.Row="1" HorizontalAlignment="Stretch" Background="{DynamicResource SplitterBrush}"/>

                <!-- 실시간 차트 영역 -->
                <Border Grid.Row="2" Background="{DynamicResource MainContentBackgroundBrush}"
                       BorderBrush="{DynamicResource BorderBrush}" BorderThickness="1" Margin="5">
                    <TabControl Style="{DynamicResource DynamicTabControlStyle}">
                        <TabItem Header="온도 트렌드">
                            <controls:RealTimeChart ChartType="Temperature" DataSource="{Binding TemperatureData}"/>
                        </TabItem>
                        <TabItem Header="압력 트렌드">
                            <controls:RealTimeChart ChartType="Pressure" DataSource="{Binding PressureData}"/>
                        </TabItem>
                        <TabItem Header="가스 흐름">
                            <controls:RealTimeChart ChartType="GasFlow" DataSource="{Binding GasFlowData}"/>
                        </TabItem>
                        <TabItem Header="전력 소비">
                            <controls:RealTimeChart ChartType="Power" DataSource="{Binding PowerData}"/>
                        </TabItem>
                    </TabControl>
                </Border>
            </Grid>

            <!-- 스플리터 -->
            <GridSplitter Grid.Column="3" HorizontalAlignment="Stretch" Background="{DynamicResource SplitterBrush}"/>

            <!-- 오른쪽 상태 패널 -->
            <Border Grid.Column="4" Background="{DynamicResource SidePanelBackgroundBrush}" BorderBrush="{DynamicResource BorderBrush}" BorderThickness="1,0,0,0">
                <ScrollViewer>
                    <StackPanel Margin="10">
                        <!-- 시스템 상태 -->
                        <controls:SystemStatusPanel Margin="0,0,0,20"/>

                        <!-- 최근 알람 -->
                        <controls:RecentAlarmsPanel Margin="0,0,0,20"/>

                        <!-- 주요 지표 -->
                        <controls:KeyMetricsPanel/>
                    </StackPanel>
                </ScrollViewer>
            </Border>
        </Grid>

        <!-- 하단 상태바 -->
        <Border Grid.Row="2" Background="{DynamicResource StatusBarBackgroundBrush}" BorderBrush="{DynamicResource BorderBrush}" BorderThickness="0,1,0,0">
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="Auto"/>
                    <ColumnDefinition Width="Auto"/>
                    <ColumnDefinition Width="Auto"/>
                </Grid.ColumnDefinitions>

                <TextBlock Grid.Column="0" Text="{Binding StatusMessage}" VerticalAlignment="Center" Margin="10,0"
                          Foreground="{DynamicResource SecondaryTextBrush}"/>

                <TextBlock Grid.Column="1" Text="{Binding ConnectionStatus}" VerticalAlignment="Center" Margin="10,0"
                          Foreground="{DynamicResource SecondaryTextBrush}"/>

                <TextBlock Grid.Column="2" Text="{Binding CurrentTime, StringFormat='yyyy-MM-dd HH:mm:ss'}"
                          VerticalAlignment="Center" Margin="10,0"
                          Foreground="{DynamicResource SecondaryTextBrush}"/>

                <ProgressBar Grid.Column="3" Width="100" Height="16" Margin="10,0"
                           Value="{Binding SystemLoad}" Maximum="100"
                           Style="{DynamicResource ModernProgressBarStyle}"/>
            </Grid>
        </Border>
    </Grid>
</Window>
```

</div>

## 동적 테마 시스템

### 테마 관리자 구현

<div class="code-section">

**DynamicThemeManager.cs**

```csharp
public class DynamicThemeManager : INotifyPropertyChanged
{
    private static readonly Lazy<DynamicThemeManager> _instance = new(() => new DynamicThemeManager());
    public static DynamicThemeManager Instance => _instance.Value;

    private ThemeType currentTheme = ThemeType.Dark;
    private readonly Dictionary<string, ResourceDictionary> themeResources;

    public event PropertyChangedEventHandler PropertyChanged;

    public ThemeType CurrentTheme
    {
        get => currentTheme;
        set
        {
            if (currentTheme != value)
            {
                currentTheme = value;
                ApplyTheme(value);
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(CurrentTheme)));
            }
        }
    }

    private DynamicThemeManager()
    {
        themeResources = new Dictionary<string, ResourceDictionary>();
        LoadThemeResources();
    }

    private void LoadThemeResources()
    {
        // 다크 테마 리소스
        var darkTheme = new ResourceDictionary
        {
            Source = new Uri("/Themes/DarkTheme.xaml", UriKind.Relative)
        };
        themeResources["Dark"] = darkTheme;

        // 라이트 테마 리소스
        var lightTheme = new ResourceDictionary
        {
            Source = new Uri("/Themes/LightTheme.xaml", UriKind.Relative)
        };
        themeResources["Light"] = lightTheme;

        // 고대비 테마 (접근성)
        var highContrastTheme = new ResourceDictionary
        {
            Source = new Uri("/Themes/HighContrastTheme.xaml", UriKind.Relative)
        };
        themeResources["HighContrast"] = highContrastTheme;

        // 사용자 정의 테마들
        LoadCustomThemes();
    }

    private void LoadCustomThemes()
    {
        var customThemesPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "CustomThemes");
        if (Directory.Exists(customThemesPath))
        {
            foreach (var xamlFile in Directory.GetFiles(customThemesPath, "*.xaml"))
            {
                try
                {
                    var themeName = Path.GetFileNameWithoutExtension(xamlFile);
                    var themeDict = new ResourceDictionary
                    {
                        Source = new Uri(xamlFile, UriKind.Absolute)
                    };
                    themeResources[themeName] = themeDict;
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"사용자 정의 테마 로드 실패: {ex.Message}");
                }
            }
        }
    }

    public void ApplyTheme(ThemeType theme)
    {
        var app = Application.Current;
        if (app?.Resources == null) return;

        // 기존 테마 리소스 제거
        var resourcesToRemove = app.Resources.MergedDictionaries
            .Where(rd => IsThemeResource(rd))
            .ToList();

        foreach (var resource in resourcesToRemove)
        {
            app.Resources.MergedDictionaries.Remove(resource);
        }

        // 새 테마 적용
        if (themeResources.TryGetValue(theme.ToString(), out var newTheme))
        {
            app.Resources.MergedDictionaries.Add(newTheme);

            // 테마 변경 애니메이션
            AnimateThemeTransition();

            // 설정 저장
            SaveThemePreference(theme);
        }
    }

    private bool IsThemeResource(ResourceDictionary resource)
    {
        // 테마 리소스인지 확인하는 로직
        return resource.Source?.OriginalString.Contains("/Themes/") == true;
    }

    private void AnimateThemeTransition()
    {
        // 부드러운 테마 전환 효과
        foreach (Window window in Application.Current.Windows)
        {
            var fadeOut = new DoubleAnimation(1.0, 0.8, TimeSpan.FromMilliseconds(150));
            var fadeIn = new DoubleAnimation(0.8, 1.0, TimeSpan.FromMilliseconds(150))
            {
                BeginTime = TimeSpan.FromMilliseconds(150)
            };

            fadeOut.Completed += (s, e) => window.BeginAnimation(UIElement.OpacityProperty, fadeIn);
            window.BeginAnimation(UIElement.OpacityProperty, fadeOut);
        }
    }

    // 실시간 색상 조정
    public void AdjustThemeColors(ColorAdjustment adjustment)
    {
        var app = Application.Current;

        // 기본 색상들 조정
        if (app.Resources.Contains("PrimaryBrush"))
        {
            var primaryBrush = (SolidColorBrush)app.Resources["PrimaryBrush"];
            var adjustedColor = AdjustColor(primaryBrush.Color, adjustment);
            app.Resources["PrimaryBrush"] = new SolidColorBrush(adjustedColor);
        }

        // 기타 주요 색상들도 동일하게 조정
        AdjustResourceColor("SecondaryBrush", adjustment);
        AdjustResourceColor("AccentBrush", adjustment);
        AdjustResourceColor("BackgroundBrush", adjustment);
    }

    private void AdjustResourceColor(string resourceKey, ColorAdjustment adjustment)
    {
        var app = Application.Current;
        if (app.Resources.Contains(resourceKey) && app.Resources[resourceKey] is SolidColorBrush brush)
        {
            var adjustedColor = AdjustColor(brush.Color, adjustment);
            app.Resources[resourceKey] = new SolidColorBrush(adjustedColor);
        }
    }

    private Color AdjustColor(Color original, ColorAdjustment adjustment)
    {
        // HSV 색공간에서 조정
        var hsv = ColorHelper.RgbToHsv(original);

        hsv.H = (hsv.H + adjustment.HueShift) % 360;
        hsv.S = Math.Max(0, Math.Min(1, hsv.S + adjustment.SaturationDelta));
        hsv.V = Math.Max(0, Math.Min(1, hsv.V + adjustment.BrightnessDelta));

        return ColorHelper.HsvToRgb(hsv);
    }

    // 접근성 지원
    public void ApplyAccessibilityTheme(AccessibilityRequirements requirements)
    {
        var app = Application.Current;

        if (requirements.HighContrast)
        {
            ApplyTheme(ThemeType.HighContrast);
        }

        if (requirements.LargeFonts)
        {
            app.Resources["BaseFontSize"] = 16.0;
            app.Resources["HeaderFontSize"] = 24.0;
        }

        if (requirements.ReducedMotion)
        {
            // 애니메이션 지속시간 단축
            app.Resources["StandardAnimationDuration"] = TimeSpan.FromMilliseconds(100);
        }
    }
}

public enum ThemeType
{
    Light,
    Dark,
    HighContrast,
    Custom
}

public class ColorAdjustment
{
    public double HueShift { get; set; }
    public double SaturationDelta { get; set; }
    public double BrightnessDelta { get; set; }
}

public class AccessibilityRequirements
{
    public bool HighContrast { get; set; }
    public bool LargeFonts { get; set; }
    public bool ReducedMotion { get; set; }
}
```

</div>

### 스타일 템플릿 정의

<div class="code-section">

**DarkTheme.xaml**

```xml
<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

    <!-- 기본 색상 팔레트 -->
    <Color x:Key="PrimaryColor">#FF2D2D30</Color>
    <Color x:Key="SecondaryColor">#FF3E3E42</Color>
    <Color x:Key="AccentColor">#FF007ACC</Color>
    <Color x:Key="BackgroundColor">#FF1E1E1E</Color>
    <Color x:Key="SurfaceColor">#FF252526</Color>
    <Color x:Key="PrimaryTextColor">#FFFFFFFF</Color>
    <Color x:Key="SecondaryTextColor">#FFCCCCCC</Color>
    <Color x:Key="BorderColor">#FF3F3F46</Color>

    <!-- 상태별 색상 -->
    <Color x:Key="SuccessColor">#FF4CAF50</Color>
    <Color x:Key="WarningColor">#FFFF9800</Color>
    <Color x:Key="ErrorColor">#FFF44336</Color>
    <Color x:Key="InfoColor">#FF2196F3</Color>

    <!-- 브러시 리소스 -->
    <SolidColorBrush x:Key="PrimaryBrush" Color="{StaticResource PrimaryColor}"/>
    <SolidColorBrush x:Key="SecondaryBrush" Color="{StaticResource SecondaryColor}"/>
    <SolidColorBrush x:Key="AccentBrush" Color="{StaticResource AccentColor}"/>
    <SolidColorBrush x:Key="BackgroundBrush" Color="{StaticResource BackgroundColor}"/>
    <SolidColorBrush x:Key="SurfaceBrush" Color="{StaticResource SurfaceColor}"/>
    <SolidColorBrush x:Key="PrimaryTextBrush" Color="{StaticResource PrimaryTextColor}"/>
    <SolidColorBrush x:Key="SecondaryTextBrush" Color="{StaticResource SecondaryTextColor}"/>
    <SolidColorBrush x:Key="BorderBrush" Color="{StaticResource BorderColor}"/>

    <!-- 특수 용도 브러시 -->
    <SolidColorBrush x:Key="HeaderBackgroundBrush" Color="{StaticResource SecondaryColor}"/>
    <SolidColorBrush x:Key="SidePanelBackgroundBrush" Color="{StaticResource PrimaryColor}"/>
    <SolidColorBrush x:Key="MainContentBackgroundBrush" Color="{StaticResource BackgroundColor}"/>
    <SolidColorBrush x:Key="CardHeaderBackgroundBrush" Color="{StaticResource SurfaceColor}"/>
    <SolidColorBrush x:Key="StatusBarBackgroundBrush" Color="{StaticResource SecondaryColor}"/>
    <SolidColorBrush x:Key="SplitterBrush" Color="{StaticResource BorderColor}"/>

    <!-- 그라데이션 브러시 -->
    <LinearGradientBrush x:Key="HeaderGradientBrush" StartPoint="0,0" EndPoint="0,1">
        <GradientStop Color="{StaticResource SecondaryColor}" Offset="0"/>
        <GradientStop Color="{StaticResource PrimaryColor}" Offset="1"/>
    </LinearGradientBrush>

    <!-- 컨트롤 스타일 -->
    <Style x:Key="NavigationButtonStyle" TargetType="Button">
        <Setter Property="Background" Value="Transparent"/>
        <Setter Property="Foreground" Value="{StaticResource PrimaryTextBrush}"/>
        <Setter Property="BorderThickness" Value="0"/>
        <Setter Property="Padding" Value="15,8"/>
        <Setter Property="Margin" Value="5,0"/>
        <Setter Property="FontWeight" Value="Medium"/>
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="Button">
                    <Border Background="{TemplateBinding Background}"
                           CornerRadius="4"
                           Padding="{TemplateBinding Padding}">
                        <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
                    </Border>
                    <ControlTemplate.Triggers>
                        <Trigger Property="IsMouseOver" Value="True">
                            <Setter Property="Background" Value="{StaticResource AccentBrush}"/>
                        </Trigger>
                        <Trigger Property="IsPressed" Value="True">
                            <Setter Property="Background" Value="{StaticResource SurfaceBrush}"/>
                        </Trigger>
                    </ControlTemplate.Triggers>
                </ControlTemplate>
            </Setter.Value>
        </Setter>
    </Style>

    <!-- 기타 스타일들... -->

</ResourceDictionary>
```

</div>

## 성능 최적화 및 마무리

### 가상화 및 메모리 관리

<div class="code-section">

**성능 최적화 구현**

```csharp
public class PerformanceOptimizations
{
    // UI 가상화 구현
    public static void EnableVirtualization(ItemsControl control)
    {
        VirtualizingPanel.SetIsVirtualizing(control, true);
        VirtualizingPanel.SetVirtualizationMode(control, VirtualizationMode.Recycling);
        VirtualizingPanel.SetScrollUnit(control, ScrollUnit.Item);
    }

    // 메모리 사용량 모니터링
    public class MemoryMonitor : IDisposable
    {
        private readonly Timer memoryTimer;
        private readonly Action<long> onMemoryUpdate;

        public MemoryMonitor(Action<long> onMemoryUpdate)
        {
            this.onMemoryUpdate = onMemoryUpdate;
            memoryTimer = new Timer(CheckMemoryUsage, null, TimeSpan.Zero, TimeSpan.FromSeconds(5));
        }

        private void CheckMemoryUsage(object state)
        {
            var memoryUsage = GC.GetTotalMemory(false);
            onMemoryUpdate?.Invoke(memoryUsage);

            // 메모리 사용량이 임계치를 초과하면 가비지 컬렉션 요청
            if (memoryUsage > 500 * 1024 * 1024) // 500MB
            {
                GC.Collect();
                GC.WaitForPendingFinalizers();
                GC.Collect();
            }
        }

        public void Dispose()
        {
            memoryTimer?.Dispose();
        }
    }
}
```

</div>

---