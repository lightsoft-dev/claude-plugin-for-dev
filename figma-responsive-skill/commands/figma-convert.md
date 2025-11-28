---
description: Figma 디자인을 반응형 코드로 자동 변환
---

# Figma Convert

Figma MCP를 활용하여 디자인을 반응형 코드로 자동 변환합니다.

---

## 🚨🚨🚨 절대 금지 사항 - 위반 시 작업 실패 🚨🚨🚨

### 1. 🔴🔴🔴 이미지/아이콘 직접 생성 절대 금지 🔴🔴🔴
```
❌ 절대 금지: SVG 코드를 직접 작성하는 것 (path d="..." 등)
❌ 절대 금지: 아이콘을 코드로 그리는 것 (Circle, Rect 등 조합)
❌ 절대 금지: 임의의 placeholder 이미지 사용
❌ 절대 금지: 다른 페이지/다른 노드의 이미지 사용
❌ 절대 금지: 비슷한 이미지로 대체하는 것

✅ 무조건 필수: Figma REST API로 해당 노드 ID의 이미지를 다운로드!
✅ 무조건 필수: curl로 실제 이미지 파일(.svg, .png)을 저장!
✅ 무조건 필수: 저장된 파일을 import해서 사용!
```

**이미지 다운로드 과정 (반드시 따라야 함):**
1. Figma 노드에서 이미지/아이콘 노드 ID 수집
2. `curl -H "X-Figma-Token: $TOKEN" "https://api.figma.com/v1/images/{fileKey}?ids={nodeId}&format=svg"`
3. 응답에서 이미지 URL 추출
4. `curl -o assets/icons/xxx.svg "{이미지URL}"` 로 다운로드
5. 코드에서 `import Icon from '../assets/icons/xxx.svg'` 사용

### 2. Gemini 검증 건너뛰기 절대 금지
```
❌ 금지: "API 키가 없다"며 건너뛰는 것
❌ 금지: "설정되지 않았다"며 건너뛰는 것
✅ 필수: Step 0에서 .env 로드 확인 후 진행
✅ 필수: 환경변수 없으면 Step 0 다시 실행
```

### 3. 서브에이전트 환경변수 전달 필수
```
❌ 금지: Task에 환경변수 없이 실행하는 것
✅ 필수: prompt에 FIGMA_API_TOKEN, GEMINI_API_KEY 값을 직접 포함
✅ 필수: "환경변수: FIGMA_API_TOKEN=xxx, GEMINI_API_KEY=yyy" 형태로 전달
```

---

## Steps to follow:

### 0. 환경 변수 로드 및 저장 (필수 - 가장 먼저 실행!)

**⚠️ 이 단계를 건너뛰면 Gemini 비교와 이미지 다운로드가 작동하지 않습니다!**

**⚠️ 반드시 .env 파일을 직접 Read 도구로 읽어서 값을 추출하세요!**

**Step 0-1. .env 파일 읽기 (Read 도구 사용):**
```
Read 도구로 프로젝트 루트의 .env 파일 읽기
```

**Step 0-2. 값 추출 및 저장:**
.env 파일 내용에서 다음 값들을 추출하여 **메모리에 저장**:
- `FIGMA_API_TOKEN` 값 → 이후 Step 6, 8에서 사용
- `GEMINI_API_KEY` 값 → 이후 Step 6, 8에서 사용

**Step 0-3. 확인 출력:**
```
✅ 환경변수 로드 완료
- FIGMA_API_TOKEN: figd_xxxx... (설정됨)
- GEMINI_API_KEY: AIza... (설정됨)
```

**환경변수가 없으면** 사용자에게 `.env` 파일 생성 요청:
```
GEMINI_API_KEY="your-gemini-api-key"
FIGMA_API_TOKEN="your-figma-token"
```

**중요: 이 값들을 Step 6 서브에이전트와 Step 8 Gemini 검증에서 직접 사용합니다!**

### 1. 버전 선택 및 px 범위 설정

AskUserQuestion 도구로 한 번에 버전 선택과 px 범위를 설정받으세요.

**첫 번째 질문 - 버전 선택:**
```
question: "구현할 버전을 선택하세요"
header: "버전"
multiSelect: true
options:
  - label: "Mobile"
    description: "모바일 (기본: 0~430px)"
  - label: "Tablet"
    description: "태블릿 (기본: 431~834px)"
  - label: "PC"
    description: "PC (기본: 835px~)"
```

**두 번째 질문 - px 범위 설정 (선택한 버전에 대해):**
```
question: "px 범위를 어떻게 설정하시겠습니까?"
header: "범위설정"
options:
  - label: "기본값 사용"
    description: "Mobile: 0~430px, Tablet: 431~834px, PC: 835px~"
  - label: "직접 입력"
    description: "각 버전의 범위를 직접 지정합니다"
```

**"직접 입력" 선택 시에만** 추가 질문:
- 선택한 각 버전에 대해 "Mobile min~max px 입력 (예: 0~430):" 형식으로 질문

**기본값:**
- Mobile: `{ minWidth: 0, maxWidth: 430 }`
- Tablet: `{ minWidth: 431, maxWidth: 834 }`
- PC: `{ minWidth: 835, maxWidth: null }`

### 2. Figma 링크 입력

AskUserQuestion 도구로 Figma 링크를 입력받으세요.

```
question: "변환할 Figma 링크를 입력하세요 (여러 개는 줄바꿈으로 구분)"
header: "Figma"
options:
  - label: "링크 입력"
    description: "Figma 디자인 URL을 입력합니다"
```

사용자가 "Other"를 선택하면 텍스트 입력창이 나타납니다.

**링크 파싱 규칙:**
- 줄바꿈(`\n`), 공백, 콤마(`,`)로 구분된 여러 링크 허용
- 각 링크에서 `file_key`와 `node-id` 추출
- URL 형식 예시:
  - `https://www.figma.com/file/{file_key}?node-id={node_id}`
  - `https://www.figma.com/design/{file_key}/...?node-id={node_id}`

**링크 파싱 함수:**
```javascript
const parseFigmaLinks = (input) => {
  // 줄바꿈, 콤마, 공백으로 분리
  const links = input.split(/[\n,\s]+/).filter(s => s.includes('figma.com'));

  return links.map(url => {
    const fileKeyMatch = url.match(/(?:file|design)\/([^\/\?]+)/);
    const nodeIdMatch = url.match(/node-id=([^&\s]+)/);

    return {
      url,
      fileKey: fileKeyMatch?.[1],
      nodeId: nodeIdMatch?.[1]?.replace(/%3A/g, ':').replace(/-/g, ':')
    };
  }).filter(link => link.fileKey && link.nodeId);
};
```

**입력 예시:**
```
https://figma.com/design/ABC123/Project?node-id=1-234
https://figma.com/design/ABC123/Project?node-id=5-678
https://figma.com/design/XYZ789/Other?node-id=10-20
```

### 3. 플랫폼 자동 감지

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

### 4. 설정 파일 생성

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

### 5. 반응형 유틸리티 생성

플랫폼에 맞는 반응형 유틸리티 파일을 생성하세요.

**React Native / Expo의 경우:**
`references/responsive-utils-rn.md` 참조하여 `src/utils/responsive.ts` 생성

**Web / Next.js의 경우:**
`references/responsive-utils-web.md` 참조하여 `src/utils/responsive.ts` 생성

### 6. 페이지 변환 (멀티 에이전트 병렬 처리)

**⚠️ 서브에이전트에 환경변수 반드시 전달!**

각 Figma 링크에 대해 Task 도구로 서브에이전트 병렬 실행:

**서브에이전트 프롬프트 필수 포함 사항:**
```
[환경변수]
FIGMA_API_TOKEN={Step 0에서 로드한 값}
GEMINI_API_KEY={Step 0에서 로드한 값}

[작업]
Figma URL: {url}
File Key: {fileKey}
Node ID: {nodeId}
플랫폼: {platform}
버전 설정: {versions}

위 환경변수를 사용하여 다음 작업을 수행하세요:
1. Figma MCP로 노드 데이터 가져오기
2. iOS 시스템 UI 제거
3. 컴포넌트 코드 생성
4. 이미지/아이콘 다운로드 (FIGMA_API_TOKEN 사용)
```

각 서브에이전트가 수행할 작업:

#### Step 6-1. Figma MCP로 노드 데이터 가져오기
- `mcp__figma__get_file` 또는 관련 MCP 도구 사용

#### Step 6-2. iOS 시스템 UI 요소 자동 제거
- `references/figma-mapping.md`의 "iOS 시스템 UI 요소 제거" 섹션 참조
- 상태바, 홈 인디케이터 감지 및 제거
- React Native: `SafeAreaView`로 자동 래핑

#### Step 6-3. 노드 분석 및 컴포넌트 생성
- `references/figma-mapping.md` 참조하여 Figma 요소 → React 컴포넌트 변환
- 반응형 유틸리티 적용

#### Step 6-4. 🔴🔴🔴 이미지/아이콘 다운로드 (무조건 다운로드! 절대 코드로 그리지 마!) 🔴🔴🔴

   **🚨🚨🚨 경고: 이미지를 코드로 그리면 작업 실패입니다! 🚨🚨🚨**

   **절대 하지 마:**
   - `<svg><path d="M10 10..."/></svg>` ← 이런 식으로 SVG 코드 작성 금지!
   - `<Circle cx={} cy={} r={} />` ← 이런 식으로 도형 조합 금지!
   - `require('./placeholder.png')` ← 임의 이미지 사용 금지!

   **무조건 해야 하는 것:**
   - Figma API 호출 → 이미지 URL 받기 → curl로 다운로드 → 저장된 파일 import

   **Step 6-4-1. Figma에서 이미지 노드 ID 수집:**
   - VECTOR, IMAGE, FRAME(아이콘/이미지 포함) 노드의 ID 수집
   - 마스코트, 캐릭터, 일러스트, 아이콘 등 모든 그래픽 요소 포함
   - **모든 이미지/아이콘 노드를 빠짐없이 수집!**

   **Step 6-4-2. Figma API로 이미지 URL 요청:**
   ```bash
   # 프롬프트에서 전달받은 FIGMA_API_TOKEN 값을 직접 사용!
   TOKEN="전달받은_FIGMA_API_TOKEN_값"
   FILE_KEY="파일키"
   NODE_IDS="1:234,5:678,9:012"

   # SVG export (아이콘/벡터용)
   RESPONSE=$(curl -s -H "X-Figma-Token: $TOKEN" \
     "https://api.figma.com/v1/images/${FILE_KEY}?ids=${NODE_IDS}&format=svg")

   echo "$RESPONSE"  # 응답 확인

   # PNG export (마스코트/이미지용, 2배 해상도)
   RESPONSE=$(curl -s -H "X-Figma-Token: $TOKEN" \
     "https://api.figma.com/v1/images/${FILE_KEY}?ids=${NODE_IDS}&format=png&scale=2")

   echo "$RESPONSE"  # 응답 확인
   ```

   **Step 6-4-3. 실제 이미지 파일 다운로드:**
   ```bash
   # 응답에서 받은 URL로 실제 이미지 다운로드 (무조건!)
   mkdir -p assets/images assets/icons

   # 예시: 응답에서 받은 URL 사용
   curl -s -o "assets/images/mascot.png" "https://figma-alpha-api.s3.us-west-2.amazonaws.com/images/..."
   curl -s -o "assets/icons/check.svg" "https://figma-alpha-api.s3.us-west-2.amazonaws.com/images/..."

   # 다운로드 확인
   ls -la assets/images/
   ls -la assets/icons/
   ```

   **Step 6-4-4. 다운로드한 파일 사용:**
   ```typescript
   // ✅ 올바른 사용법: 다운로드한 파일 import
   import MascotImage from '../assets/images/mascot.png';
   import CheckIcon from '../assets/icons/check.svg';

   // ❌ 잘못된 사용법: 코드로 직접 그리기
   // const CheckIcon = () => <Svg><Path d="..."/></Svg>  // 절대 금지!
   ```

   **저장 위치:**
   - 아이콘 (SVG) → `assets/icons/`
   - 마스코트/캐릭터/이미지 (PNG) → `assets/images/`
   - 100% 동일 파일만 중복 제외, 나머지는 모두 저장
   - `assets/icons/index.ts` 및 `assets/images/index.ts` 생성

**Step 6-5. 서브에이전트 결과 반환:**
   - 생성된 파일 경로들
   - 추출된 아이콘 목록
   - 추출된 이미지/마스코트 목록
   - 제거된 iOS 시스템 UI 요소 목록
   - 변환 로그

### 7. 결과 취합

모든 서브에이전트 완료 후:

1. 생성된 모든 컴포넌트 파일 목록 정리
2. 중복 아이콘 제거 및 통합
3. 공통 컴포넌트 식별

### 8. Gemini 검증 (필수!) - 이미지 & 레이아웃 확인

**⚠️ 이 단계는 반드시 실행해야 합니다!**
**⚠️ Step 0에서 로드한 GEMINI_API_KEY를 사용하세요!**
**⚠️ 환경변수가 없다고 건너뛰지 말고, Step 0에서 로드한 값을 직접 사용!**

**Gemini의 역할 (UI 생성 X, 검증만 O):**
- Claude Code가 UI 코드는 이미 잘 생성함
- Gemini는 **검증만** 담당:
  1. **이미지 검증**: Figma의 마스코트/아이콘이 앱에 제대로 들어갔는지
  2. **레이아웃 검증**: 요소들이 Figma와 동일한 위치에 있는지

**비교 대상:**
- Figma 디자인 이미지 (원본)
- 실행 중인 앱 스크린샷 (결과물)

**비교 프로세스 (최대 5차 반복):**

```
반복 1~5차:
  1. Figma 디자인 이미지 가져오기
  2. 앱 실행 및 스크린샷 캡처
  3. Gemini로 두 이미지 비교 분석
  4. 차이점을 코드로 자동 수정
  5. 일치율 95% 이상이면 종료, 아니면 다음 차수로
```

#### Step 8-1. Figma 디자인 이미지 가져오기

`references/gemini-compare.md`의 "Figma REST API 직접 호출" 참조:

```bash
# FIGMA_API_TOKEN으로 이미지 URL 요청
FILE_KEY="파일키"
NODE_ID="노드아이디"

RESPONSE=$(curl -s -H "X-Figma-Token: $FIGMA_API_TOKEN" \
  "https://api.figma.com/v1/images/${FILE_KEY}?ids=${NODE_ID}&format=png&scale=2")

IMAGE_URL=$(echo "$RESPONSE" | grep -o 'https://[^"]*\.png[^"]*' | head -1)
curl -s -o /tmp/figma-design.png "$IMAGE_URL"
```

#### Step 8-2. 앱 스크린샷 캡처

**플랫폼별 캡처 명령:**

```bash
# iOS 시뮬레이터
xcrun simctl io booted screenshot /tmp/app-screenshot.png

# Android 에뮬레이터
adb exec-out screencap -p > /tmp/app-screenshot.png

# Web (Puppeteer) - 선택한 버전의 뷰포트 사용
npx puppeteer screenshot http://localhost:3000 \
  --viewport {선택한_버전_maxWidth}x932 \
  --output /tmp/app-screenshot.png
```

**앱이 실행 중이 아닌 경우:**
1. 자동으로 `npm start` 또는 `expo start` 실행 시도
2. 시뮬레이터/에뮬레이터 자동 실행 시도
3. 30초 대기 후 재시도 (최대 3회)
4. 그래도 실패하면 Gemini 비교 건너뛰고 계속 진행 (사용자에게 물어보지 않음)

#### Step 8-3. Gemini 검증 분석

```bash
GEMINI_API_KEY="$GEMINI_API_KEY" gemini -m gemini-2.5-flash \
  --image /tmp/figma-design.png \
  --image /tmp/app-screenshot.png \
  "두 이미지를 비교 검증하세요. 첫 번째는 Figma 원본, 두 번째는 개발된 앱입니다.

   검증 항목:
   1. 이미지 검증: 마스코트, 아이콘, 일러스트가 동일하게 들어갔는지
   2. 레이아웃 검증: 요소들의 위치가 Figma와 동일한지 (상/하/좌/우 위치)
   3. 크기 검증: 요소들의 크기 비율이 맞는지

   JSON 형식으로 응답:
   {
     \"matchPercentage\": 85,
     \"imageIssues\": [
       {\"element\": \"마스코트\", \"issue\": \"이미지가 없거나 다름\", \"expected\": \"사과모자 캐릭터\"}
     ],
     \"layoutIssues\": [
       {\"element\": \"코인 아이콘\", \"issue\": \"위치가 다름\", \"expected\": \"중앙 정렬\", \"actual\": \"왼쪽 정렬\"}
     ],
     \"sizeIssues\": [
       {\"element\": \"체크 아이콘\", \"issue\": \"크기가 작음\", \"expected\": \"24px\", \"actual\": \"16px\"}
     ]
   }"
```

**Gemini 에러 처리:**
- API 키 오류 → Step 0으로 돌아가서 환경변수 다시 로드 후 재시도
- 이미지 인식 실패 → 이미지 재캡처 후 재시도
- 네트워크 오류 → 5초 대기 후 재시도 (최대 3회)

#### Step 8-4. Claude Code가 자동 수정

Gemini 검증 결과에 따라:

**이미지 이슈 (imageIssues):**
- 이미지가 없거나 다름 → Figma API로 해당 이미지 다시 다운로드
- 이미지 경로 오류 → 코드에서 import 경로 수정

**레이아웃 이슈 (layoutIssues):**
- 위치가 다름 → 정렬 속성 수정 (justifyContent, alignItems 등)
- 마진/패딩 수정 → scaleWidth/scaleHeight 값 조정

**크기 이슈 (sizeIssues):**
- 크기가 다름 → width/height 값 수정

수정 로그 출력:
```
[수정 1/3] 마스코트 이미지 재다운로드
[수정 2/3] 코인 아이콘: alignItems: 'flex-start' → 'center'
[수정 3/3] 체크 아이콘: width: 16 → 24
```

#### Step 8-5. 반복 판단

```
if (matchPercentage >= 95 || 반복횟수 >= 5):
  종료
else:
  앱 재빌드/리로드
  Step 8-2로 돌아가기
```

**반복 로그:**
```
[Gemini 비교 1차] 일치율: 78% - 수정 3건 적용
[Gemini 비교 2차] 일치율: 89% - 수정 2건 적용
[Gemini 비교 3차] 일치율: 94% - 수정 1건 적용
[Gemini 비교 4차] 일치율: 97% - 완료!
```

### 9. 최종 리포트 출력

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

### 필수 참조 문서
- `references/figma-mapping.md` - Figma → 코드 변환 규칙 **(스케일링 함수 규칙 필독!)**
- `references/responsive-utils-rn.md` - React Native 반응형 유틸리티
- `references/responsive-utils-web.md` - Web 반응형 유틸리티
- `references/gemini-compare.md` - Gemini 비교 상세 방법

### 스케일링 함수 사용 규칙 (절대 준수)

| 속성 | 함수 | 추가값 |
|------|------|--------|
| 폰트 크기 | `scaleFont(n + 2)` | Figma 값 + 2~3px |
| 가로 마진/패딩 | `scaleWidth(n + 5)` | Figma 값 + 4~6px |
| 세로 마진/패딩 | `scaleHeight(n + 5)` | Figma 값 + 4~6px |
| 너비 | `scaleWidth(n)` | 그대로 |
| 높이 | `scaleHeight(n)` | 그대로 |
| 가로 gap | `scaleWidth(n + 5)` | Figma 값 + 5px |
| 세로 gap | `scaleHeight(n + 5)` | Figma 값 + 5px |

**잘못된 사용 금지:**
- `scaleSpacing()` 사용 금지 → 가로/세로 구분하여 `scaleWidth`/`scaleHeight` 사용
- 세로 속성에 `scaleWidth` 사용 금지
- 가로 속성에 `scaleHeight` 사용 금지

### 반응형 버전별 대응

사용자가 선택한 버전(Mobile/Tablet/PC)과 px 범위에 따라:

1. **config 파일 생성 시** 선택한 버전만 `enabled: true`로 설정
2. **반응형 유틸리티 생성 시** 선택한 px 범위를 정확히 반영
3. **컴포넌트 생성 시** 선택한 버전에 맞는 조건부 스타일 적용:

```typescript
// 예: Mobile + Tablet 선택, PC 미선택 시
const styles = StyleSheet.create({
  container: {
    // Mobile (0~430px)과 Tablet (431~834px)에서만 대응
    width: screenInfo.isTablet ? scaleWidth(400) : scaleWidth(300),
    padding: screenInfo.isTablet ? scaleWidth(24 + 5) : scaleWidth(16 + 5),
  },
});
```

### Gemini 비교 동작 원칙

1. **절대 멈추지 않음** - 에러 시 자동 재시도/디버깅 후 진행
2. **5차까지 반복** - 95% 일치율 달성 또는 5차 완료까지
3. **구체적인 수정 지시** - Gemini가 파일명, 위치, 현재값→목표값 명시
4. **Claude Code가 직접 수정** - Gemini 결과를 받아 자동으로 코드 수정

### 기타 규칙
- Figma MCP가 연결되어 있어야 합니다
- 아이콘은 항상 SVG로 추출하여 `assets/icons/`에 저장합니다
- iOS 상태바/홈 인디케이터는 자동 제거됩니다
