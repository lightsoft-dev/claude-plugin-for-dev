# Figma Responsive Skill

Figma MCP를 활용하여 디자인을 반응형 코드로 자동 변환하는 스킬입니다.

## 핵심 기능

- **단일 커맨드**: `/figma-convert` 하나로 모든 과정 자동 완료
- **버전 선택**: Mobile / Tablet / PC 중복 선택 + px 범위 직접 지정
- **멀티 페이지**: 여러 Figma 링크 한 번에 입력하여 병렬 변환
- **SVG 아이콘**: 자동 추출하여 `assets/icons/` 저장
- **Gemini 비교**: 개발 결과 vs Figma 디자인 비교 후 자동 수정

## 워크플로우

```
/figma-convert 실행
    │
    ├─ 1. 버전 선택 (다중 선택)
    │     └─ Mobile / Tablet / PC
    │
    ├─ 2. 각 버전 px 범위 입력
    │     ├─ Mobile: 0 ~ 430px
    │     ├─ Tablet: 431 ~ 834px
    │     └─ PC: 835px ~
    │
    ├─ 3. Figma 링크들 입력
    │
    ├─ 4. 플랫폼 자동 감지
    │     └─ package.json 분석
    │
    ├─ 5. Figma MCP로 디자인 가져오기
    │
    ├─ 6. 페이지별 병렬 변환 (멀티 에이전트)
    │     └─ 각 링크마다 Task 도구로 서브 에이전트 실행
    │
    ├─ 7. SVG 아이콘 추출
    │
    ├─ 8. 반응형 유틸리티 생성
    │     └─ src/utils/responsive.ts
    │
    ├─ 9. Gemini 비교 & 자동 수정
    │     └─ 95% 일치까지 반복
    │
    └─ 10. 최종 리포트
```

## 플랫폼 자동 감지

package.json 분석하여 플랫폼 결정:

```javascript
// React Native (순수)
if (dependencies["react-native"] && !dependencies["expo"]) => "react-native"

// Expo (모바일)
if (dependencies["expo"] && !dependencies["react-dom"]) => "expo-mobile"

// Expo Universal (웹 + 모바일)
if (dependencies["expo"] && dependencies["react-dom"]) => "expo-universal"

// Next.js
if (dependencies["next"]) => "nextjs"

// React Web
if (dependencies["react-dom"] && !dependencies["next"]) => "react-web"
```

## 반응형 유틸리티

### React Native / Expo

`src/utils/responsive.ts` 생성:

- `scaleWidth(size)` - 너비 비율 계산
- `scaleHeight(size)` - 높이 비율 계산
- `scaleFont(size)` - 폰트 크기 (태블릿/PC에서 +2px)
- `scaleSpacing(size)` - 마진/패딩 (태블릿/PC에서 +5px)
- `getCurrentVersion()` - 현재 버전 감지 (mobile/tablet/pc)

### Web / Next.js

- CSS 미디어 쿼리 기반
- `useResponsive()` 훅 제공
- `fluidFont()`, `fluidSpacing()` 유틸리티

## 멀티 에이전트 아키텍처

### 메인 에이전트 (Coordinator)

1. 사용자 입력 수집 (버전, 범위, 링크들)
2. 각 Figma 링크에 대해 Task 도구로 서브 에이전트 실행 (병렬)
3. 모든 결과 취합
4. 공통 컴포넌트 추출
5. 최종 리포트 생성

### 서브 에이전트 (Page Converter)

1. 할당된 Figma 링크 분석
2. Figma MCP로 노드 데이터 가져오기
3. 컴포넌트 코드 생성 (반응형 유틸 적용)
4. SVG 아이콘 추출
5. 결과 반환

## Gemini 디자인 비교

### 스크린샷 캡처 (플랫폼별)

| 플랫폼 | iOS | Android | Web |
|--------|-----|---------|-----|
| React Native | `xcrun simctl io booted screenshot` | `adb screencap` | - |
| Expo Universal | 위와 동일 | 위와 동일 | Puppeteer |
| Web | - | - | Puppeteer |

### 비교 프로세스

1. Figma 디자인 이미지 export (Figma MCP)
2. 개발 화면 스크린샷 캡처
3. Gemini CLI로 두 이미지 비교
4. 차이점 JSON으로 반환
5. 자동 수정 적용
6. 95% 일치율 달성까지 반복 (최대 3회)

## 설정 파일

### figma-responsive.config.json

```json
{
  "versions": {
    "mobile": { "enabled": true, "minWidth": 0, "maxWidth": 430 },
    "tablet": { "enabled": true, "minWidth": 431, "maxWidth": 834 },
    "pc": { "enabled": false, "minWidth": 835, "maxWidth": null }
  },
  "scaling": {
    "textSizeIncrease": 2,
    "spacingIncrease": 5
  },
  "paths": {
    "utils": "src/utils/responsive.ts",
    "icons": "assets/icons"
  }
}
```

## 환경 변수

| 변수 | 필수 | 용도 |
|------|------|------|
| `GEMINI_API_KEY` | 선택 | 디자인 비교 기능 |

> Figma MCP 서버 사용으로 별도 Figma API 토큰 설정 불필요

## 레퍼런스

- `references/responsive-utils-rn.md` - React Native 반응형 유틸 상세
- `references/responsive-utils-web.md` - Web 반응형 유틸 상세
- `references/gemini-compare.md` - Gemini 비교 방법 상세
- `references/figma-mapping.md` - Figma에서 코드 매핑 규칙
