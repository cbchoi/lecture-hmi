## 💻 코드 설명 - 2단 구성

<div class="two-column">
<div class="column-left">

### 📄 소스 코드

```c
#include <stdio.h>
#include <windows.h>

int main() {
    HANDLE hFile;

    // 파일 생성 (파일이 없을 때만)
    hFile = CreateFile(
        L"example.txt",        // 파일명
        GENERIC_WRITE,         // 쓰기 권한
        0,                     // 공유 금지
        NULL,                  // 기본 보안
        CREATE_NEW,            // 새 파일만 생성
        FILE_ATTRIBUTE_NORMAL, // 일반 파일
        NULL                   // 템플릿 없음
    );

    // 에러 처리
    if (hFile == INVALID_HANDLE_VALUE) {
        printf("❌ 파일 생성 실패\n");
        return 1;
    }

    printf("✅ 파일 생성 성공\n");
    CloseHandle(hFile);
    return 0;
}
```

</div>
<div class="column-right">

### 📝 상세 설명

<div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745; margin-bottom: 1rem;">
    <h4 style="color: #155724; margin-top: 0;">🎯 핵심 함수: CreateFile()</h4>
    <p style="margin-bottom: 0; color: #155724;">Windows API의 핵심 파일 생성/열기 함수</p>
</div>

**📋 매개변수 설명:**

<div style="font-size: 0.9em; line-height: 1.6;">

1. **`lpFileName`** 📁
   → 생성할 파일의 이름 (유니코드)

2. **`dwDesiredAccess`** 🔑
   → `GENERIC_READ`, `GENERIC_WRITE` 등

3. **`dwShareMode`** 🤝
   → 다른 프로세스와의 파일 공유 설정

4. **`dwCreationDisposition`** 🆕
   → `CREATE_NEW`: 새 파일만 생성
   → `CREATE_ALWAYS`: 항상 생성
   → `OPEN_EXISTING`: 기존 파일만 열기

</div>

<div style="background: #e8f5e8; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
    <h4 style="color: #28a745; margin-top: 0;">🔄 반환값</h4>
    <ul style="margin-bottom: 0; color: #155724;">
        <li><strong>성공:</strong> 유효한 파일 핸들</li>
        <li><strong>실패:</strong> <code>INVALID_HANDLE_VALUE</code></li>
    </ul>
</div>

</div>
</div>

---

Note:
**코드 2단 구성 템플릿 사용법:**

1. **소스 코드**: 실제 예제 코드로 교체
2. **한글 주석**: 코드 내 주석을 한글로 상세히 작성
3. **상세 설명**: 오른쪽에 함수별, 매개변수별 설명
4. **외부 파일**: `slides/weekXX/code/` 폴더의 파일 참조 가능

**디자인 특징:**
- 이모지로 각 섹션 구분
- 색상별 박스로 중요도 표현
- 매개변수별 상세 설명으로 학습 효과 극대화
- 한글 주석으로 이해도 향상