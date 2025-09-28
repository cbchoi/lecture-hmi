## 💻 코드 설명 - 전체 구성

### 📄 예제 코드

```c
#include <stdio.h>
#include <windows.h>

// 파일 정보를 출력하는 함수
void PrintFileInfo(const wchar_t* fileName) {
    WIN32_FIND_DATA findData;
    HANDLE hFind;

    // 파일 검색 시작
    hFind = FindFirstFile(fileName, &findData);

    if (hFind == INVALID_HANDLE_VALUE) {
        wprintf(L"❌ 파일을 찾을 수 없습니다: %s\n", fileName);
        return;
    }

    // 파일 정보 출력
    wprintf(L"📁 파일명: %s\n", findData.cFileName);
    wprintf(L"📏 파일 크기: %ld bytes\n", findData.nFileSizeLow);
    wprintf(L"📅 생성 시간: %08x-%08x\n",
            findData.ftCreationTime.dwHighDateTime,
            findData.ftCreationTime.dwLowDateTime);

    FindClose(hFind);  // 핸들 정리
}

int main() {
    wprintf(L"🚀 파일 정보 조회 프로그램\n");
    PrintFileInfo(L"test.txt");
    return 0;
}
```

### 📝 코드 분석

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin: 1.5rem 0;">

<div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745;">
    <h4 style="color: #155724; margin-top: 0;">🔍 핵심 함수들</h4>
    <ul style="color: #155724; margin-bottom: 0;">
        <li><code>FindFirstFile()</code>: 파일 검색 시작</li>
        <li><code>FindClose()</code>: 검색 핸들 해제</li>
        <li><code>wprintf()</code>: 유니코드 출력</li>
    </ul>
</div>

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3;">
    <h4 style="color: #0d47a1; margin-top: 0;">📊 WIN32_FIND_DATA 구조체</h4>
    <ul style="color: #0d47a1; margin-bottom: 0;">
        <li><code>cFileName</code>: 파일명</li>
        <li><code>nFileSizeLow</code>: 파일 크기</li>
        <li><code>ftCreationTime</code>: 생성 시간</li>
    </ul>
</div>

</div>

<div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #f39c12; margin: 1rem 0;">
    <h4 style="color: #856404; margin-top: 0;">⚠️ 주의사항</h4>
    <ul style="color: #856404; margin-bottom: 0;">
        <li>반드시 <code>FindClose()</code>로 핸들을 정리해야 합니다</li>
        <li>유니코드 문자열은 <code>L</code> 접두사를 사용합니다</li>
        <li>에러 처리를 위해 <code>INVALID_HANDLE_VALUE</code> 확인이 필요합니다</li>
    </ul>
</div>

### 🚀 실행 결과 예시

```
🚀 파일 정보 조회 프로그램
📁 파일명: test.txt
📏 파일 크기: 1024 bytes
📅 생성 시간: 01d8a2f3-4b5c6d7e
```

---

Note:
코드 설명 1단 구성 템플릿입니다.
- 위에 코드, 아래에 설명을 배치합니다
- slides/weekXX/code/ 폴더의 코드 파일을 참조할 수 있습니다
- 코드와 설명이 한 화면에 모두 표시됩니다