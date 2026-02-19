# Claude Code Plugins for Dev

Lightsoft 개발팀을 위한 Claude Code 플러그인/스킬 모음.

## Plugins

| 플러그인 | 커맨드 | 설명 |
|---------|--------|------|
| **voicemanager** | *(hook)* | 작업 완료 시 TTS 알림 (`say` 명령) |
| **project-initializer** | `/init` | 기술 스택별 프로젝트 초기 세팅 |
| **project-cleaner** | `/cleanup` | 배포 전 백업/임시 파일 및 미사용 패키지 정리 |
| **test-generator** | `/test` | 테스트 코드 자동 생성 및 실행, 리포트 출력 |
| **security-checker** | `/security-check` | 시크릿 노출, 의존성 취약점, 코드 보안 이슈 검사 |

## Skills

| 스킬 | 커맨드 | 설명 |
|------|--------|------|
| **figma-responsive-skill** | `/figma-convert` | Figma 디자인 → 멀티 디바이스 반응형 코드 변환 (Gemini AI 비교 검증) |
| **auto-qa** | `/auto-qa` | 브라우저 자동화 기반 블랙박스 QA + Linear 이슈 생성 + 버그 수정 + HTML 리포트 |

## 설치

```bash
claude plugins add github:lightsoft-dev/claude-plugin-for-dev
```

## 구조

```
.
├── .claude-plugin/
│   └── marketplace.json    # 플러그인 레지스트리
├── voicemanager/           # TTS 알림 (hooks)
├── project-initializer/    # 프로젝트 초기화
├── project-cleaner/        # 프로젝트 정리
├── test-generator/         # 테스트 자동 생성
├── security-checker/       # 보안 검사
├── figma-responsive-skill/ # Figma → 반응형 코드
└── auto-qa/                # 자동 QA 테스팅
```
