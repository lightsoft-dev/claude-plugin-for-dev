---
description: Figma 디자인을 반응형 코드로 자동 변환
---

# Figma Convert

Figma MCP를 활용하여 디자인을 반응형 코드로 자동 변환합니다.

## Steps to follow:

### 0. 환경 변수 로드 (필수)

Bash 도구로 아래 명령을 실행하여 환경 변수를 설정하세요:

```bash
# .env 파일 자동 탐색 및 로드
for env_path in ".env" "../.env" "../../.env" "$HOME/.claude/.env"; do
  if [ -f "$env_path" ]; then
    set -a && source "$env_path" && set +a
    echo "Loaded: $env_path"
    break
  fi
done

# 환경 변수 확인
echo "GEMINI_API_KEY: ${GEMINI_API_KEY:0:10}..."
echo "FIGMA_API_TOKEN: ${FIGMA_API_TOKEN:0:10}..."
```

**필요한 환경 변수:**
- `GEMINI_API_KEY` - Gemini 디자인 비교용
- `FIGMA_API_TOKEN` - Figma 이미지 export용 (MCP 대안)

환경 변수가 출력되지 않으면 프로젝트 루트에 `.env` 파일을 생성하세요.

### 1. 버전 선택 (다중 선택 가능)

AskUserQuestion 도구를 사용하여 사용자에게 구현할 버전을 질문하세요:

```
어떤 버전을 구현하시겠습니까? (다중 선택 가능)
[ ] Mobile
[ ] Tablet
[ ] PC
```

- `multiSelect: true`로 설정하여 여러 버전 선택 가능하게 합니다.
- 최소 1개 이상 선택되어야 합니다.

### 2. 각 버전의 px 범위 입력

선택한 각 버전에 대해 px 범위를 질문하세요:

**Mobile 선택 시:**
```
Mobile 범위를 입력하세요
기본값: 0 ~ 430px
>
```

**Tablet 선택 시:**
```
Tablet 범위를 입력하세요
기본값: 431 ~ 834px
>
```

**PC 선택 시:**
```
PC 범위를 입력하세요
기본값: 835px ~
>
```

기본값을 제시하고, 사용자가 Enter만 누르면 기본값 사용.

### 3. Figma 링크 입력 (여러 개 가능)

사용자에게 변환할 Figma 페이지 링크들을 입력받으세요:

```
변환할 Figma 페이지 링크들을 입력하세요 (여러 개 가능):
> https://figma.com/file/xxx?node-id=123
> https://figma.com/file/xxx?node-id=456
> (빈 줄 입력 시 완료)
```

모든 링크를 배열로 저장합니다.

### 4. 플랫폼 자동 감지

프로젝트의 `package.json`을 Read 도구로 읽어서 플랫폼을 감지하세요:

```javascript
const deps = { ...dependencies, ...devDependencies };

if (deps["react-native"] && !deps["expo"]) {
  platform = "react-native";
} else if (deps["expo"] && !deps["react-dom"]) {
  platform = "expo-mobile";
} else if (deps["expo"] && deps["react-dom"]) {
  platform = "expo-universal";
} else if (deps["next"]) {
  platform = "nextjs";
} else if (deps["react-dom"]) {
  platform = "react-web";
}
```

감지된 플랫폼을 사용자에게 표시:
```
플랫폼 감지: Expo Universal (웹 + 모바일)
```

### 5. 설정 파일 생성

`figma-responsive.config.json` 파일을 프로젝트 루트에 생성:

```json
{
  "versions": {
    "mobile": {
      "enabled": true/false,
      "minWidth": 사용자입력,
      "maxWidth": 사용자입력
    },
    "tablet": {
      "enabled": true/false,
      "minWidth": 사용자입력,
      "maxWidth": 사용자입력
    },
    "pc": {
      "enabled": true/false,
      "minWidth": 사용자입력,
      "maxWidth": null
    }
  },
  "scaling": {
    "textSizeIncrease": 2,
    "spacingIncrease": 5
  },
  "platform": "감지된플랫폼",
  "paths": {
    "utils": "src/utils/responsive.ts",
    "icons": "assets/icons"
  }
}
```

### 6. 반응형 유틸리티 생성

플랫폼에 맞는 반응형 유틸리티 파일을 생성하세요.

**React Native / Expo의 경우:**
`references/responsive-utils-rn.md` 참조하여 `src/utils/responsive.ts` 생성

**Web / Next.js의 경우:**
`references/responsive-utils-web.md` 참조하여 `src/utils/responsive.ts` 생성

### 7. 페이지별 병렬 변환 (멀티 에이전트)

각 Figma 링크에 대해 Task 도구를 사용하여 서브 에이전트를 **병렬로** 실행하세요:

```
각 Figma 링크마다 Task 도구를 병렬로 호출:

Task 1:
- prompt: "Figma 페이지 변환: [링크1]
  - Figma MCP로 노드 데이터 가져오기
  - 컴포넌트 코드 생성 (반응형 유틸 적용)
  - SVG 아이콘 추출
  - 결과 반환"
- subagent_type: "general-purpose"

Task 2:
- prompt: "Figma 페이지 변환: [링크2] ..."
- subagent_type: "general-purpose"

(모든 링크에 대해 병렬 실행)
```

**서브 에이전트가 수행할 작업:**

1. Figma MCP 호출하여 노드 데이터 가져오기:
   - `mcp__figma__get_file` 또는 관련 MCP 도구 사용

2. **iOS 시스템 UI 요소 자동 제거**:
   - `references/figma-mapping.md`의 "iOS 시스템 UI 요소 제거" 섹션 참조
   - 상단 상태바 (Status Bar) 감지 및 제거:
     - 키워드: `status bar`, `battery`, `signal`, `time`, `notch`, `dynamic island`
     - 위치: y < 60, 높이 20~59px
   - 하단 홈 인디케이터 (Home Indicator) 감지 및 제거:
     - 키워드: `home indicator`, `home bar`, `bottom indicator`
     - 위치: 화면 하단 40px 이내
   - 제거된 요소 로그 출력:
     ```
     [iOS System UI] 제거됨: "Status Bar" (44px, 상단)
     [iOS System UI] 제거됨: "Home Indicator" (34px, 하단)
     ```
   - React Native: `SafeAreaView`로 자동 래핑

3. 노드 분석 및 컴포넌트 생성:
   - `references/figma-mapping.md` 참조하여 Figma 요소 → React 컴포넌트 변환
   - 반응형 유틸리티 적용 (scaleWidth, scaleFont, scaleSpacing 등)

4. SVG 아이콘 추출:
   - 아이콘 노드 탐지 (이름에 "icon", "Icon", "svg" 포함)
   - `assets/icons/` 폴더에 SVG 파일 저장
   - `assets/icons/index.ts` 생성

5. 결과 반환:
   - 생성된 파일 경로들
   - 추출된 아이콘 목록
   - 제거된 iOS 시스템 UI 요소 목록
   - 변환 로그

### 8. 결과 취합

모든 서브 에이전트 완료 후:

1. 생성된 모든 컴포넌트 파일 목록 정리
2. 중복 아이콘 제거 및 통합
3. 공통 컴포넌트 식별

### 9. Gemini 디자인 비교 (선택적)

`GEMINI_API_KEY` 환경 변수가 설정되어 있는 경우에만 실행:

```bash
echo $GEMINI_API_KEY
```

**설정되어 있으면:**

1. Figma 디자인 이미지 가져오기 (Figma MCP 이미지 export)
2. 개발 화면 스크린샷 캡처:
   - iOS: `xcrun simctl io booted screenshot`
   - Android: `adb exec-out screencap -p`
   - Web: Puppeteer 사용
3. `references/gemini-compare.md` 참조하여 Gemini CLI로 비교
4. 차이점 발견 시 자동 수정
5. 95% 일치율까지 반복 (최대 3회)

**설정 안 되어 있거나 실패 시:**
사용자에게 진행 여부 확인:
```
Gemini 비교를 건너뛰시겠습니까?
1. 예, 건너뛰기
2. API 키 설정 후 재시도
```

### 10. 최종 리포트 출력

변환 완료 후 결과 요약 표시:

```markdown
# Figma → Code 변환 완료

## 설정
- 플랫폼: Expo Universal
- 버전: Mobile (0~430px), Tablet (431~834px)

## 변환된 페이지
| 페이지 | 파일 경로 | 아이콘 수 |
|--------|----------|----------|
| HomePage | src/screens/HomePage.tsx | 5개 |
| LoginPage | src/screens/LoginPage.tsx | 2개 |

## 생성된 파일
- src/utils/responsive.ts
- src/screens/HomePage.tsx
- src/screens/LoginPage.tsx
- assets/icons/ (7개 SVG)

## Gemini 비교 결과
- 평균 일치율: 96%
- 자동 수정: 3건

## 다음 단계
1. npm start 또는 expo start로 앱 실행
2. 각 버전(Mobile/Tablet)에서 확인
```

## Important Notes:

- Figma MCP가 연결되어 있어야 합니다
- 반응형 유틸리티는 `references/` 폴더의 레퍼런스 문서를 참조하세요
- 아이콘은 항상 SVG로 추출하여 `assets/icons/`에 저장합니다
- 텍스트 크기는 태블릿/PC에서 +2px 적용
- 마진/패딩은 태블릿/PC에서 +5px 적용
