## 🔄 비교 분석 - 이중 이미지 구성

### 📊 프로세스 vs 스레드 완전 분석

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #007bff; margin: 1.5rem 0;">
    <p style="margin: 0; font-size: 1.1em; color: #2d3748;">
        🎯 <strong>핵심 개념:</strong> 프로세스는 독립적인 메모리 공간을 가지며, 스레드는 프로세스 내에서 메모리 공간을 공유하는 실행 단위입니다.
    </p>
</div>

<div class="two-column">
<div class="column-left">

<div style="text-align: center; background: #e8f5e8; padding: 1.5rem; border-radius: 12px; border: 2px solid #28a745; margin-bottom: 1rem;">
    <img src="slides/weekXX/images/process-memory.png" alt="프로세스 메모리 구조" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <h3 style="color: #155724; margin: 1rem 0 0.5rem 0;">🏠 프로세스 (Process)</h3>
</div>

<div style="background: #d4edda; padding: 1rem; border-radius: 8px; border: 1px solid #c3e6cb;">
    <h4 style="color: #155724; margin-top: 0;">✅ 장점</h4>
    <ul style="color: #155724; margin-bottom: 0; font-size: 0.9em;">
        <li>🔒 <strong>독립적인 주소 공간</strong></li>
        <li>🛡️ <strong>높은 보안성과 안정성</strong></li>
        <li>💪 <strong>오류 격리 (한 프로세스 오류가 다른 프로세스에 영향 없음)</strong></li>
    </ul>
</div>

<div style="background: #f8d7da; padding: 1rem; border-radius: 8px; border: 1px solid #f5c6cb; margin-top: 0.5rem;">
    <h4 style="color: #721c24; margin-top: 0;">❌ 단점</h4>
    <ul style="color: #721c24; margin-bottom: 0; font-size: 0.9em;">
        <li>⏱️ <strong>높은 컨텍스트 스위칭 비용</strong></li>
        <li>💰 <strong>많은 메모리 사용량</strong></li>
        <li>📡 <strong>복잡한 IPC 통신</strong></li>
    </ul>
</div>

</div>
<div class="column-right">

<div style="text-align: center; background: #e3f2fd; padding: 1.5rem; border-radius: 12px; border: 2px solid #2196f3; margin-bottom: 1rem;">
    <img src="slides/weekXX/images/thread-memory.png" alt="스레드 메모리 구조" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <h3 style="color: #0d47a1; margin: 1rem 0 0.5rem 0;">🧵 스레드 (Thread)</h3>
</div>

<div style="background: #cce5ff; padding: 1rem; border-radius: 8px; border: 1px solid #99ccff;">
    <h4 style="color: #0d47a1; margin-top: 0;">✅ 장점</h4>
    <ul style="color: #0d47a1; margin-bottom: 0; font-size: 0.9em;">
        <li>🤝 <strong>공유 주소 공간</strong></li>
        <li>⚡ <strong>빠른 생성과 전환</strong></li>
        <li>💬 <strong>효율적인 데이터 공유</strong></li>
    </ul>
</div>

<div style="background: #fff3cd; padding: 1rem; border-radius: 8px; border: 1px solid #ffeaa7; margin-top: 0.5rem;">
    <h4 style="color: #856404; margin-top: 0;">⚠️ 주의사항</h4>
    <ul style="color: #856404; margin-bottom: 0; font-size: 0.9em;">
        <li>🔄 <strong>동기화 문제 (Race Condition)</strong></li>
        <li>🎯 <strong>디버깅의 복잡성</strong></li>
        <li>💥 <strong>하나의 스레드 오류가 전체 프로세스에 영향</strong></li>
    </ul>
</div>

</div>
</div>

### 📋 핵심 차이점 요약

<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin: 1.5rem 0;">

<div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #6f42c1; text-align: center;">
    <h4 style="color: #6f42c1; margin-top: 0;">💾 메모리</h4>
    <p style="margin: 0; font-size: 0.9em;">프로세스: <strong>독립</strong><br>스레드: <strong>공유</strong></p>
</div>

<div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #e91e63; text-align: center;">
    <h4 style="color: #e91e63; margin-top: 0;">⚡ 생성 비용</h4>
    <p style="margin: 0; font-size: 0.9em;">프로세스: <strong>높음</strong><br>스레드: <strong>낮음</strong></p>
</div>

<div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #ff9800; text-align: center;">
    <h4 style="color: #ff9800; margin-top: 0;">📡 통신</h4>
    <p style="margin: 0; font-size: 0.9em;">프로세스: <strong>IPC</strong><br>스레드: <strong>메모리 공유</strong></p>
</div>

</div>

---

Note:
**이중 이미지 템플릿 사용법:**

1. **상단 설명**: 비교할 개념의 전체적인 개요 설명
2. **이미지 배치**: 양쪽에 비교 대상 이미지 배치
3. **장단점 분석**: 각각의 특징을 색상별로 구분 표시
4. **요약**: 하단에 핵심 차이점 그리드로 정리

**활용 시나리오:**
- 두 기술이나 개념의 비교
- Before/After 상황 설명
- 장단점 분석
- 대안 제시 상황