# 🚀 심화 실습

---

## 실습 3: MVVM 패턴 완성

<div style="margin: 2rem 0;">

### ⚡ 커맨드 구현

```csharp
// MainWindowViewModel에 커맨드 추가
public class MainWindowViewModel : BaseViewModel
{
    // ... 기존 코드 ...

    public ICommand RefreshCommand { get; }
    public ICommand StartMaintenanceCommand { get; }
    public ICommand StopEquipmentCommand { get; }
    public ICommand ClearAlarmsCommand { get; }

    public MainWindowViewModel()
    {
        // ... 기존 초기화 코드 ...

        // 커맨드 초기화
        RefreshCommand = new RelayCommand(ExecuteRefresh);
        StartMaintenanceCommand = new RelayCommand(ExecuteStartMaintenance, CanStartMaintenance);
        StopEquipmentCommand = new RelayCommand(ExecuteStopEquipment, CanStopEquipment);
        ClearAlarmsCommand = new RelayCommand(ExecuteClearAlarms, CanClearAlarms);
    }

    // 새로고침 커맨드
    private void ExecuteRefresh()
    {
        StatusMessage = "데이터를 새로고침하는 중...";

        // 실제로는 서버에서 데이터를 가져오는 로직
        foreach (var equipment in EquipmentList)
        {
            equipment.LastUpdate = DateTime.Now;
            // 임의의 데이터 업데이트 시뮬레이션
            var random = new Random();
            equipment.Temperature += (random.NextDouble() - 0.5) * 2;
            equipment.Pressure += (random.NextDouble() - 0.5) * 0.1;
        }

        UpdateAlarmCount();
        StatusMessage = "새로고침 완료";
    }

    // 정비 시작 커맨드
    private void ExecuteStartMaintenance()
    {
        if (SelectedEquipment != null)
        {
            SelectedEquipment.Status = EquipmentStatus.Maintenance;
            StatusMessage = $"{SelectedEquipment.EquipmentId} 정비 모드로 전환";
            UpdateAlarmCount();
        }
    }

    private bool CanStartMaintenance()
    {
        return SelectedEquipment?.Status == EquipmentStatus.Idle ||
               SelectedEquipment?.Status == EquipmentStatus.Error;
    }

    // 장비 정지 커맨드
    private void ExecuteStopEquipment()
    {
        if (SelectedEquipment != null)
        {
            SelectedEquipment.Status = EquipmentStatus.Idle;
            StatusMessage = $"{SelectedEquipment.EquipmentId} 장비 정지";
            UpdateAlarmCount();
        }
    }

    private bool CanStopEquipment()
    {
        return SelectedEquipment?.Status == EquipmentStatus.Running ||
               SelectedEquipment?.Status == EquipmentStatus.Warning;
    }

    // 알람 초기화 커맨드
    private void ExecuteClearAlarms()
    {
        foreach (var equipment in EquipmentList)
        {
            if (equipment.Status == EquipmentStatus.Warning)
            {
                equipment.Status = EquipmentStatus.Running;
            }
        }
        UpdateAlarmCount();
        StatusMessage = "모든 경고 알람이 초기화되었습니다";
    }

    private bool CanClearAlarms()
    {
        return AlarmCount > 0;
    }
}
```

### 🎮 XAML에 커맨드 바인딩 추가

```xml
<!-- MainWindow.xaml의 메인 콘텐츠 영역에 버튼 추가 -->
<Grid Grid.Row="1">
    <!-- 기존 콘텐츠... -->

    <!-- 제어 버튼 패널 추가 -->
    <Grid Grid.Row="2" Margin="0,20,0,0">
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="*"/>
            <ColumnDefinition Width="*"/>
            <ColumnDefinition Width="*"/>
            <ColumnDefinition Width="*"/>
        </Grid.ColumnDefinitions>

        <!-- 새로고침 버튼 -->
        <Button Grid.Column="0"
                Command="{Binding RefreshCommand}"
                Background="#3498DB"
                Foreground="White"
                Padding="15,10"
                Margin="5"
                FontWeight="Medium"
                BorderThickness="0"
                CornerRadius="5">
            <StackPanel Orientation="Horizontal">
                <TextBlock Text="🔄" FontSize="16" Margin="0,0,5,0"/>
                <TextBlock Text="새로고침"/>
            </StackPanel>
        </Button>

        <!-- 정비 시작 버튼 -->
        <Button Grid.Column="1"
                Command="{Binding StartMaintenanceCommand}"
                Background="#9B59B6"
                Foreground="White"
                Padding="15,10"
                Margin="5"
                FontWeight="Medium"
                BorderThickness="0"
                CornerRadius="5">
            <StackPanel Orientation="Horizontal">
                <TextBlock Text="🔧" FontSize="16" Margin="0,0,5,0"/>
                <TextBlock Text="정비 시작"/>
            </StackPanel>
        </Button>

        <!-- 장비 정지 버튼 -->
        <Button Grid.Column="2"
                Command="{Binding StopEquipmentCommand}"
                Background="#E67E22"
                Foreground="White"
                Padding="15,10"
                Margin="5"
                FontWeight="Medium"
                BorderThickness="0"
                CornerRadius="5">
            <StackPanel Orientation="Horizontal">
                <TextBlock Text="⏹️" FontSize="16" Margin="0,0,5,0"/>
                <TextBlock Text="장비 정지"/>
            </StackPanel>
        </Button>

        <!-- 알람 초기화 버튼 -->
        <Button Grid.Column="3"
                Command="{Binding ClearAlarmsCommand}"
                Background="#E74C3C"
                Foreground="White"
                Padding="15,10"
                Margin="5"
                FontWeight="Medium"
                BorderThickness="0"
                CornerRadius="5">
            <StackPanel Orientation="Horizontal">
                <TextBlock Text="🚨" FontSize="16" Margin="0,0,5,0"/>
                <TextBlock Text="알람 초기화"/>
            </StackPanel>
        </Button>
    </Grid>
</Grid>
```

</div>

---

## 실습 4: 값 변환기 구현

<div style="margin: 2rem 0;">

### 🔄 상태별 색상 변환기

```csharp
// StatusToColorConverter.cs
using System;
using System.Globalization;
using System.Windows.Data;
using System.Windows.Media;

namespace SemiconductorHMI.Converters
{
    public class StatusToColorConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value is EquipmentStatus status)
            {
                return status switch
                {
                    EquipmentStatus.Running => new SolidColorBrush(Color.FromRgb(76, 175, 80)),     // 녹색
                    EquipmentStatus.Warning => new SolidColorBrush(Color.FromRgb(255, 152, 0)),     // 주황색
                    EquipmentStatus.Error => new SolidColorBrush(Color.FromRgb(244, 67, 54)),       // 빨간색
                    EquipmentStatus.Maintenance => new SolidColorBrush(Color.FromRgb(33, 150, 243)), // 파란색
                    _ => new SolidColorBrush(Color.FromRgb(158, 158, 158))                          // 회색
                };
            }
            return new SolidColorBrush(Colors.Gray);
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }

    // 온도 범위별 색상 변환기
    public class TemperatureToColorConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value is double temperature)
            {
                if (temperature < 50)
                    return new SolidColorBrush(Color.FromRgb(33, 150, 243));   // 파란색 (저온)
                else if (temperature < 150)
                    return new SolidColorBrush(Color.FromRgb(76, 175, 80));    // 녹색 (정상)
                else if (temperature < 250)
                    return new SolidColorBrush(Color.FromRgb(255, 193, 7));    // 노란색 (주의)
                else if (temperature < 300)
                    return new SolidColorBrush(Color.FromRgb(255, 152, 0));    // 주황색 (경고)
                else
                    return new SolidColorBrush(Color.FromRgb(244, 67, 54));    // 빨간색 (위험)
            }
            return new SolidColorBrush(Colors.Gray);
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }

    // 압력 단위 표시 변환기
    public class PressureToStringConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value is double pressure)
            {
                if (pressure < 0.001)
                    return $"{pressure * 1000000:F1} mTorr";
                else if (pressure < 1.0)
                    return $"{pressure * 1000:F1} mTorr";
                else
                    return $"{pressure:F3} Torr";
            }
            return "0 Torr";
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }
}
```

### 📄 XAML에서 변환기 사용

```xml
<Window x:Class="SemiconductorHMI.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:converters="clr-namespace:SemiconductorHMI.Converters"
        Title="반도체 장비 모니터링 시스템">

    <Window.Resources>
        <!-- 변환기 리소스 등록 -->
        <converters:StatusToColorConverter x:Key="StatusToColorConverter"/>
        <converters:TemperatureToColorConverter x:Key="TemperatureToColorConverter"/>
        <converters:PressureToStringConverter x:Key="PressureToStringConverter"/>
    </Window.Resources>

    <!-- 기존 내용... -->

    <!-- 장비 목록에서 색상 변환기 사용 -->
    <ListBox.ItemTemplate>
        <DataTemplate>
            <Border Background="{Binding Status, Converter={StaticResource StatusToColorConverter}}"
                    CornerRadius="3"
                    Padding="8,5"
                    Margin="0,2">
                <!-- 내용... -->
            </Border>
        </DataTemplate>
    </ListBox.ItemTemplate>

    <!-- 온도 표시에 색상 변환기 적용 -->
    <TextBlock Text="{Binding SelectedEquipment.TemperatureText}"
               FontSize="36" FontWeight="Bold"
               Foreground="{Binding SelectedEquipment.Temperature,
                          Converter={StaticResource TemperatureToColorConverter}}"/>

    <!-- 압력 표시에 단위 변환기 적용 -->
    <TextBlock Text="{Binding SelectedEquipment.Pressure,
                     Converter={StaticResource PressureToStringConverter}}"
               FontSize="36" FontWeight="Bold"
               Foreground="#3498DB"/>
</Window>
```

</div>

---

