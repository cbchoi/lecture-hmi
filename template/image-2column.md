## 🖼️ 그림 설명 - 2단 구성

<div class="two-column">
<div class="column-left">

### 📋 프로세스 생성 과정

<div style="margin: 1.5rem 0;">

<div style="display: flex; align-items: center; background: #e8f5e8; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
    <div style="background: #28a745; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">1</div>
    <div>
        <h4 style="margin: 0; color: #155724;">🚀 프로세스 초기화</h4>
        <ul style="margin: 0.5rem 0 0 0; color: #155724; font-size: 0.9em;">
            <li>메모리 공간 할당</li>
            <li>프로세스 제어 블록(PCB) 생성</li>
            <li>초기 스택 및 힙 설정</li>
        </ul>
    </div>
</div>

<div style="display: flex; align-items: center; background: #e3f2fd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
    <div style="background: #2196f3; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">2</div>
    <div>
        <h4 style="margin: 0; color: #0d47a1;">📁 실행 파일 로딩</h4>
        <ul style="margin: 0.5rem 0 0 0; color: #0d47a1; font-size: 0.9em;">
            <li>PE 파일 형식 분석</li>
            <li>코드 및 데이터 섹션 로딩</li>
            <li>DLL 의존성 해결</li>
        </ul>
    </div>
</div>

<div style="display: flex; align-items: center; background: #f3e5f5; padding: 1rem; border-radius: 8px;">
    <div style="background: #9c27b0; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">3</div>
    <div>
        <h4 style="margin: 0; color: #4a148c;">⚡ 프로세스 시작</h4>
        <ul style="margin: 0.5rem 0 0 0; color: #4a148c; font-size: 0.9em;">
            <li>초기 스레드 생성</li>
            <li>실행 권한 부여</li>
            <li>스케줄링 큐에 등록</li>
        </ul>
    </div>
</div>

</div>

<div style="background: #fff3cd; padding: 1rem; border-radius: 8px; border: 1px solid #f39c12; margin-top: 1.5rem;">
    <h4 style="color: #856404; margin-top: 0;">💡 핵심 포인트</h4>
    <p style="margin-bottom: 0; color: #856404; font-size: 0.95em;">
        각 단계는 순차적으로 실행되며, 어느 한 단계라도 실패하면 프로세스 생성이 중단됩니다.
    </p>
</div>

</div>
<div class="column-right">

### 🎯 시각적 설명

<div style="text-align: center; background: #f8f9fa; padding: 1.5rem; border-radius: 12px; border: 2px solid #dee2e6;">
    <img src="slides/weekXX/images/process-creation.png" alt="프로세스 생성 다이어그램" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <p style="margin: 1rem 0 0 0; color: #6c757d; font-size: 0.9em; font-style: italic;">
        📊 프로세스 생성 과정의 단계별 흐름도
    </p>
</div>

<div style="margin-top: 1.5rem; background: #e8f4f8; padding: 1rem; border-radius: 8px; border-left: 4px solid #17a2b8;">
    <h4 style="color: #0c5460; margin-top: 0;">🔍 주요 관찰 포인트</h4>
    <ul style="color: #0c5460; margin-bottom: 0; font-size: 0.9em;">
        <li>각 단계의 의존성 관계</li>
        <li>메모리 할당 시점과 크기</li>
        <li>오류 발생 시 롤백 과정</li>
        <li>시스템 리소스 사용량</li>
    </ul>
</div>

</div>
</div>

---

Note:
**그림 2단 구성 템플릿 사용법:**

1. **왼쪽 설명**: 단계별 프로세스를 시각적으로 구성
2. **오른쪽 이미지**: `slides/weekXX/images/` 폴더의 이미지 참조
3. **상호 연관성**: 설명과 그림이 서로 보완하도록 구성
4. **시각적 강화**: 이모지와 색상으로 내용 구분

**디자인 특징:**
- 단계별 원형 번호로 순서 표현
- 색상별 배경으로 각 단계 구분
- 이미지 캡션과 관찰 포인트 제공
- 양쪽 콘텐츠의 균형잡힌 배치