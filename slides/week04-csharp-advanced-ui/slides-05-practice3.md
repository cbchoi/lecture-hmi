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

