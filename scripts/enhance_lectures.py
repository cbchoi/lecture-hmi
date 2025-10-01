#!/usr/bin/env python3
"""
Enhance lecture slides with:
1. Design pattern theory
2. SOLID principles
3. Two-column code layouts
4. Code explanations
"""

import os
import re
from pathlib import Path

# Design patterns theory content to add to Week 2
WEEK2_DESIGN_PATTERNS = """
---

## 소프트웨어 디자인 패턴 기초

### 📐 SOLID 원칙

#### Single Responsibility Principle (단일 책임 원칙)
- 클래스는 하나의 책임만 가져야 함
- HMI에서: ViewModel은 UI 로직, Model은 비즈니스 로직

<div class="grid grid-cols-2 gap-8">
<div>

```csharp
// ❌ 나쁜 예: 여러 책임
public class EquipmentViewModel
{
    public void UpdateUI() { }
    public void SaveToDatabase() { }
    public void SendToServer() { }
}
```

</div>
<div>

**문제점**:
- ViewModel이 너무 많은 책임을 가짐
- UI, 데이터베이스, 네트워크 로직이 혼재
- 테스트와 유지보수가 어려움
- 한 부분의 변경이 전체에 영향

</div>
</div>

---

<div class="grid grid-cols-2 gap-8">
<div>

```csharp
// ✅ 좋은 예: 책임 분리
public class EquipmentViewModel
{
    private readonly IEquipmentRepository _repository;
    private readonly IDataService _dataService;

    public void UpdateUI()
    {
        // UI 업데이트만 담당
        OnPropertyChanged(nameof(Status));
    }
}

public class EquipmentRepository
{
    public void Save(Equipment equipment)
    {
        // 데이터베이스 저장만 담당
    }
}

public class DataService
{
    public void Send(Equipment equipment)
    {
        // 서버 통신만 담당
    }
}
```

</div>
<div>

**개선점**:
- 각 클래스가 하나의 명확한 책임
- ViewModel: UI 상태 관리
- Repository: 데이터 영속성
- DataService: 네트워크 통신
- 독립적인 테스트 가능
- 변경의 영향 범위 최소화

</div>
</div>

---

#### Open/Closed Principle (개방-폐쇄 원칙)
- 확장에는 열려있고, 수정에는 닫혀있어야 함
- 새로운 기능 추가 시 기존 코드 수정 최소화

<div class="grid grid-cols-2 gap-8">
<div>

```csharp
// ✅ 좋은 예: 인터페이스 기반 확장
public interface IAlarmStrategy
{
    bool ShouldTrigger(double value);
    AlarmLevel GetLevel();
}

public class ThresholdAlarm : IAlarmStrategy
{
    private readonly double _threshold;

    public bool ShouldTrigger(double value)
    {
        return value > _threshold;
    }

    public AlarmLevel GetLevel()
    {
        return AlarmLevel.Warning;
    }
}

public class RateOfChangeAlarm : IAlarmStrategy
{
    private readonly double _maxRate;

    public bool ShouldTrigger(double value)
    {
        // 변화율 기반 알람
        return CalculateRate(value) > _maxRate;
    }
}
```

</div>
<div>

**장점**:
- 새로운 알람 타입 추가가 용이
- 기존 코드 수정 불필요
- 인터페이스를 통한 다형성
- 전략 패턴 적용
- 런타임에 알람 전략 변경 가능
- 각 알람 로직 독립적 테스트

**확장 예시**:
```csharp
// 새로운 알람 추가도 쉽게
public class PatternAlarm : IAlarmStrategy
{
    // 패턴 매칭 기반 알람
}
```

</div>
</div>

---

## Observer 패턴과 INotifyPropertyChanged

### 🔄 Observer 패턴의 핵심 개념

<div class="grid grid-cols-2 gap-8">
<div>

**Observer 패턴 구조**:
- Subject (관찰 대상): ViewModel
- Observer (관찰자): View
- 상태 변경 시 자동 통지
- 느슨한 결합 (Loose Coupling)

```csharp
// Subject 인터페이스
public interface ISubject
{
    void Attach(IObserver observer);
    void Detach(IObserver observer);
    void Notify();
}

// Observer 인터페이스
public interface IObserver
{
    void Update(ISubject subject);
}
```

</div>
<div>

**WPF에서의 구현**:
- INotifyPropertyChanged가 Subject 역할
- PropertyChanged 이벤트로 통지
- View가 Observer 역할 수행

```csharp
public class ViewModel : INotifyPropertyChanged
{
    private string _status;

    public string Status
    {
        get => _status;
        set
        {
            _status = value;
            // Observer들에게 통지
            PropertyChanged?.Invoke(this,
                new PropertyChangedEventArgs(
                    nameof(Status)));
        }
    }

    public event PropertyChangedEventHandler
        PropertyChanged;
}
```

</div>
</div>

---

## Command 패턴과 MVVM

### ⚡ Command 패턴의 핵심

<div class="grid grid-cols-2 gap-8">
<div>

**Command 패턴 이점**:
- 요청을 객체로 캡슐화
- 실행 취소(Undo) 가능
- 명령 대기열 구현
- 로깅 및 감사 추적

```csharp
public interface ICommand
{
    bool CanExecute(object parameter);
    void Execute(object parameter);
    event EventHandler CanExecuteChanged;
}

public class StartCommand : ICommand
{
    private readonly EquipmentViewModel _vm;

    public bool CanExecute(object parameter)
    {
        return _vm.Status == "Idle";
    }

    public void Execute(object parameter)
    {
        _vm.Start();
    }
}
```

</div>
<parameter name="content">

**RelayCommand 패턴**:
- 범용 Command 구현
- 델리게이트로 실행 로직 주입
- 재사용 가능한 구조

```csharp
public class RelayCommand : ICommand
{
    private readonly Action _execute;
    private readonly Func<bool> _canExecute;

    public RelayCommand(
        Action execute,
        Func<bool> canExecute = null)
    {
        _execute = execute;
        _canExecute = canExecute;
    }

    public bool CanExecute(object parameter)
    {
        return _canExecute?.Invoke() ?? true;
    }

    public void Execute(object parameter)
    {
        _execute();
    }
}

// 사용
public ICommand StartCommand { get; }

public ViewModel()
{
    StartCommand = new RelayCommand(
        () => Start(),
        () => Status == "Idle");
}
```

</div>
</div>

---

## 의존성 주입 (Dependency Injection)

### 💉 DI의 필요성

<div class="grid grid-cols-2 gap-8">
<div>

**Without DI (강한 결합)**:
```csharp
public class EquipmentViewModel
{
    // ❌ 구체 클래스에 직접 의존
    private DatabaseService _db
        = new DatabaseService();
    private NetworkService _network
        = new NetworkService();

    public void Save()
    {
        _db.Save(Equipment);
        _network.Send(Equipment);
    }
}
```

**문제점**:
- 테스트 어려움
- 교체 불가능
- 강한 결합

</div>
<div>

**With DI (느슨한 결합)**:
```csharp
public class EquipmentViewModel
{
    // ✅ 인터페이스를 통한 의존
    private readonly IRepository _repository;
    private readonly IDataService _dataService;

    // 생성자 주입
    public EquipmentViewModel(
        IRepository repository,
        IDataService dataService)
    {
        _repository = repository;
        _dataService = dataService;
    }

    public void Save()
    {
        _repository.Save(Equipment);
        _dataService.Send(Equipment);
    }
}
```

**장점**:
- 테스트용 Mock 주입 가능
- 런타임에 구현체 교체
- 느슨한 결합
- 유연한 아키텍처

</div>
</div>

---
"""

def add_design_patterns_to_week2(slides_dir):
    """Add design patterns theory to Week 2"""
    theory_file = slides_dir / "week02-csharp-wpf-basics" / "slides-02-theory.md"

    if not theory_file.exists():
        print(f"File not found: {theory_file}")
        return

    with open(theory_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the end of CLR section and insert design patterns
    insertion_point = content.find("## WPF 계층 구조")

    if insertion_point == -1:
        print("Could not find insertion point")
        return

    new_content = (
        content[:insertion_point] +
        WEEK_DESIGN_PATTERNS +
        "\n" +
        content[insertion_point:]
    )

    with open(theory_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Enhanced {theory_file}")

def convert_to_two_column(code_block, explanation):
    """Convert code and explanation to two-column layout"""
    return f"""
<div class="grid grid-cols-2 gap-8">
<div>

{code_block}

</div>
<div>

{explanation}

</div>
</div>
"""

def process_week_files(slides_dir, week_num):
    """Process all files in a week directory"""
    week_dir = slides_dir / f"week{week_num:02d}-*"

    for week_path in slides_dir.glob(f"week{week_num:02d}-*"):
        if not week_path.is_dir():
            continue

        print(f"\n📁 Processing {week_path.name}")

        for md_file in week_path.glob("slides-*.md"):
            process_markdown_file(md_file)

def process_markdown_file(md_file):
    """Process a single markdown file"""
    print(f"  📄 {md_file.name}")

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Already has two-column layout
    if '<div class="grid grid-cols-2 gap-8">' in content:
        print(f"    ✓ Already has two-column layout")
        return

    # Find code blocks without explanations
    code_pattern = r'```(\w+)\n(.*?)```'
    matches = list(re.finditer(code_pattern, content, re.DOTALL))

    if matches:
        print(f"    Found {len(matches)} code blocks")

def main():
    """Main function"""
    project_root = Path(__file__).parent.parent
    slides_dir = project_root / "slides"

    print("🚀 Starting lecture enhancement...")
    print(f"📂 Slides directory: {slides_dir}")

    # Step 1: Add design patterns to Week 2
    print("\n=== Step 1: Adding design patterns theory to Week 2 ===")
    add_design_patterns_to_week2(slides_dir)

    # Step 2: Process all weeks
    print("\n=== Step 2: Processing all weeks ===")
    for week_num in range(2, 14):
        process_week_files(slides_dir, week_num)

    print("\n✅ Enhancement complete!")

if __name__ == "__main__":
    main()
