# ImGUI C++ 심화 - 고급 렌더링 및 커스텀 시각화

## 🎯 학습 목표
- ImGUI 고급 렌더링 기법 및 커스텀 드로잉을 활용한 전문적인 반도체 HMI 개발
- 3D 시각화와 ImGUI의 통합을 통한 직관적인 장비 상태 표현 시스템 구축
- 고성능 실시간 데이터 처리 및 메모리 최적화를 통한 안정적인 산업용 HMI 구현
- 커스텀 위젯 개발과 고급 이벤트 처리를 통한 사용자 경험 극대화

## 📚 주요 내용
- ImGUI DrawList API를 활용한 고급 2D/3D 그래픽스 렌더링
- OpenGL/Vulkan과 ImGUI의 seamless 통합 및 성능 최적화
- 커스텀 위젯 라이브러리 개발 (복합 차트, 3D 뷰어, 애니메이션)
- 고급 이벤트 처리 시스템 및 멀티터치/제스처 지원
- 메모리 풀링 및 GPU 리소스 관리를 통한 성능 최적화
- 실시간 데이터 스트리밍 및 대용량 데이터 시각화 기법
- 반도체 장비별 특화 UI 컴포넌트 (웨이퍼 맵, 프로세스 플로우)
- 고급 애니메이션 시스템 및 상태 전환 효과

## ⏰ 예상 소요 시간
- **이론 강의**: 45분 (고급 렌더링 아키텍처, 3D 통합, 성능 최적화)
- **기초 실습**: 45분 (커스텀 드로잉 및 위젯 개발)
- **심화 실습**: 45분 (3D 시각화 통합 및 고급 이벤트 처리)
- **Hands-on**: 45분 (실시간 반도체 장비 3D 모니터링 시스템)
- **총합**: 180분

## 👥 대상 청중
- **수준**: 고급 (C++ 고급, OpenGL/3D 그래픽스 경험, ImGUI 기초 완료)
- **사전 지식**: 3D 수학, 셰이더 프로그래밍, 고급 C++ 템플릿, 멀티스레딩
- **도구 경험**: OpenGL/Vulkan, 3D 모델링 도구, 성능 프로파일링 도구

## 💻 실습 환경
- **운영체제**: Windows/Linux/macOS (크로스 플랫폼)
- **필수 소프트웨어**:
  - C++ 컴파일러 (GCC 10+, Clang 12+, MSVC 2022+)
  - OpenGL 4.5+ / Vulkan SDK
  - ImGUI 1.89+ (최신 docking branch)
  - GLM 수학 라이브러리
  - Assimp (3D 모델 로딩)
- **선택 소프트웨어**:
  - RenderDoc (그래픽스 디버깅)
  - Intel VTune / AMD CodeXL (성능 분석)
  - Blender (3D 모델 제작)

## 📖 사전 준비
- [ ] 10주차 ImGUI C++ 기초 과정 완료
- [ ] [OpenGL 고급 기법](https://learnopengl.com/Advanced-OpenGL/Framebuffers) 학습
- [ ] 3D 수학 및 행렬 변환 이해
- [ ] [ImGUI DrawList API](https://github.com/ocornut/imgui/blob/master/docs/FAQ.md#q-how-can-i-use-my-own-math-types-instead-of-imvec2imvec4) 숙지

## 🔗 참고 자료
- [ImGUI Advanced Usage](https://github.com/ocornut/imgui/blob/master/docs/BACKENDS.md)
- [OpenGL Programming Guide](https://www.khronos.org/opengl/wiki/Getting_Started)
- [Real-Time Rendering](http://www.realtimerendering.com/)
- [Game Engine Architecture](https://www.gameenginebook.com/)
- [Graphics Programming Weekly](https://www.jendrikillner.com/tags/weekly/)

## 📋 체크리스트
- [ ] 고급 2D/3D 그래픽스 렌더링 시스템 구현
- [ ] 커스텀 위젯 라이브러리 개발 및 반도체 장비 특화 컴포넌트 제작
- [ ] 3D 장비 모델 통합 및 실시간 상태 시각화 구현
- [ ] 고성능 메모리 관리 및 GPU 리소스 최적화 적용
- [ ] 멀티터치 및 고급 이벤트 처리 시스템 완성