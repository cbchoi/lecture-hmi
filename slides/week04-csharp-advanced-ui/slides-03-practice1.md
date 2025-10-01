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

