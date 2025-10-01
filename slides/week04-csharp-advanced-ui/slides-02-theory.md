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

