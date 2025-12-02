---
description: Figma 디자인을 반응형 코드로 자동 변환
---

# 🛑 코드 작성 전 필수 체크 - STOP!

**이미지/아이콘을 코드에 추가하려고 하나요?**

```
질문: <Image>, <Svg>, <Path>, <Circle> 등의 코드를 작성하려고 하나요?

→ YES이면 STOP! 아래 확인:

[ ] Bash로 Figma API 호출해서 이미지 URL 받았나요?
[ ] curl -o assets/icons/xxx.svg "URL" 실행했나요?
[ ] ls -la assets/icons/ 로 파일 존재 확인했나요?
[ ] 파일 크기가 0바이트 이상인가요?

4개 모두 체크되어야 코드 작성 가능!
하나라도 안 되면 → 이미지 다운로드부터 다시 시작
```

**절대 금지 - 이거 하나만 기억하세요:**
```
❌ SVG 코드 직접 작성 (<svg><path d="..."/>, <Path d="..."/>)
❌ 도형 조합 (<Circle>, <Rect>, <Line>)
❌ placeholder 이미지 (require('./placeholder.png'))
❌ "이미지 없어요" 하고 넘어가기

✅ Figma API → curl 다운로드 → import 사용 (이것만 허용!)
```

---

# 실행 순서

## Step 0: 환경변수 로드 (가장 먼저!)

```typescript
// Read 도구 사용:
// file_path: ".env"
```

.env 파일에서 다음 값 추출 후 메모리에 저장:
- `FIGMA_API_TOKEN=figd_xxx...`
- `GEMINI_API_KEY=AIza...`

**환경변수 없으면 작업 중단!**

---

## Step 1: 버전 선택

AskUserQuestion으로 다음 질문:

1. **버전 선택 (multiSelect: true)**
   - Mobile (0~430px)
   - Tablet (431~834px)
   - PC (835px~)

2. **px 범위 설정**
   - 기본값 사용
   - 직접 입력 (선택 시 추가 질문)

---

## Step 2: Figma 링크 입력

AskUserQuestion으로 링크 입력 받기:
- 여러 개는 줄바꿈/콤마로 구분
- 파싱하여 `{fileKey, nodeId}` 추출

---

## Step 3: 플랫폼 감지

package.json 읽어서 자동 감지:
- react-native / expo-mobile / expo-universal / nextjs / react-web

---

## Step 4: 설정 파일 생성

`figma-responsive.config.json` 생성 (버전, 플랫폼, 경로)

---

## Step 5: 반응형 유틸리티 생성

플랫폼별 `src/utils/responsive.ts` 생성
- RN/Expo: `references/responsive-utils-rn.md` 참조
- Web/Next: `references/responsive-utils-web.md` 참조

---

## Step 6: 페이지 변환 (서브에이전트)

**⚠️ 중요: 서브에이전트에 환경변수 전달 필수!**

각 링크마다 Task 도구로 병렬 실행:

```markdown
### 서브에이전트 프롬프트 템플릿 (아래 그대로 사용):

---
[환경변수]
FIGMA_API_TOKEN={Step 0에서 로드한 값}
GEMINI_API_KEY={Step 0에서 로드한 값}

[작업 정보]
- Figma URL: {url}
- File Key: {fileKey}
- Node ID: {nodeId}
- 플랫폼: {platform}
- 버전: {versions}

---

# 🛑 절대 규칙 - 위반 시 작업 실패

**이미지/아이콘 처리 규칙:**

1. SVG/PNG 코드를 직접 작성하면 안 됩니다
2. <Svg>, <Path>, <Circle>, <Rect> 등 직접 그리기 금지
3. placeholder나 임의 이미지 사용 금지
4. 반드시 Figma API로 다운로드 후 import 사용

**강제 실행 순서 (건너뛰기 불가):**

Step A. 이미지 노드 ID 수집
Step B. Bash로 Figma API 호출 → 이미지 URL 받기
Step C. Bash로 curl 다운로드 → 실제 파일 저장
Step D. ls로 파일 확인 → 0바이트 아닌지 체크
Step E. 그 다음에야 코드 작성 (import 사용)

---

# 실행

## Step A: Figma 노드 데이터 가져오기

`mcp__figma__get_file` 또는 Figma MCP 도구 사용

노드 분석하여 다음 수집:
- 이미지 노드 (type: VECTOR, IMAGE, FRAME)
- 각 노드의 ID, name, type

## Step B: 이미지 URL 요청 (Bash 필수!)

**반드시 Bash 도구로 실행:**

```bash
TOKEN="{환경변수에서 받은 FIGMA_API_TOKEN}"
FILE_KEY="{fileKey}"
NODE_IDS="1:234,5:678,9:012"  # 콤마로 구분

# API 호출
RESPONSE=$(curl -s -H "X-Figma-Token: $TOKEN" \
  "https://api.figma.com/v1/images/${FILE_KEY}?ids=${NODE_IDS}&format=svg")

echo "$RESPONSE"
# 응답: {"images": {"1:234": "https://...", ...}}
```

## Step C: 파일 다운로드 (Bash 필수!)

**반드시 Bash 도구로 실행:**

```bash
mkdir -p assets/icons assets/images

# 각 이미지 URL로 파일 다운로드
curl -s -o "assets/icons/icon-check.svg" "https://figma-alpha-api.s3..."
curl -s -o "assets/icons/icon-star.svg" "https://figma-alpha-api.s3..."

# 파일 확인
ls -la assets/icons/
find assets -type f -size 0  # 0바이트 파일 있으면 안 됨!
```

## Step D: 다운로드 검증

```bash
# 다운로드된 파일 개수 확인
echo "아이콘: $(ls -1 assets/icons/ 2>/dev/null | wc -l)개"
echo "이미지: $(ls -1 assets/images/ 2>/dev/null | wc -l)개"
```

**검증 실패 시:**
- 0바이트 파일 → Step B부터 재실행
- 파일 없음 → Step B부터 재실행
- 재시도 3번까지 허용

## Step E: 컴포넌트 코드 생성

**이제 코드 작성 가능! (Write/Edit 도구 사용)**

`references/figma-mapping.md` 참조하여 변환:
- iOS 시스템 UI 제거
- 노드 → React 컴포넌트 변환
- 반응형 유틸리티 적용 (`scaleFont`, `scaleWidth`, `scaleHeight`)

**이미지 import:**
```typescript
// ✅ 올바른 방법
import IconCheck from '../assets/icons/icon-check.svg';
import IconStar from '../assets/icons/icon-star.svg';

<Image source={IconCheck} style={{ width: 24, height: 24 }} />
```

**스케일링 함수 규칙 (`references/figma-mapping.md` 필수 참조):**
- fontSize: `scaleFont(figmaValue + 2)`
- marginHorizontal: `scaleWidth(figmaValue + 5)`
- marginVertical: `scaleHeight(figmaValue + 5)`
- width: `scaleWidth(figmaValue)`
- height: `scaleHeight(figmaValue)`
- gap (가로): `scaleWidth(figmaValue + 5)`
- gap (세로): `scaleHeight(figmaValue + 5)`

## 결과 반환

다음 정보 반환:
- 생성된 파일 경로들
- 다운로드된 아이콘/이미지 목록
- 제거된 iOS UI 요소
- 변환 로그

---
[서브에이전트 프롬프트 끝]
```

---

## Step 7: 결과 취합

모든 서브에이전트 완료 후:
- 생성된 컴포넌트 파일 정리
- 중복 아이콘 제거
- 공통 컴포넌트 식별

---

## Step 8: Gemini 검증 (필수!)

**절대 건너뛰지 않기! API 키 없으면 사용자에게 요청**

### 8-1. Figma 디자인 이미지 가져오기

```bash
TOKEN="{Step 0에서 로드한 FIGMA_API_TOKEN}"
FILE_KEY="{fileKey}"
NODE_ID="{nodeId}"

RESPONSE=$(curl -s -H "X-Figma-Token: $TOKEN" \
  "https://api.figma.com/v1/images/${FILE_KEY}?ids=${NODE_ID}&format=png&scale=2")

IMAGE_URL=$(echo "$RESPONSE" | grep -o 'https://[^"]*\.png[^"]*' | head -1)
curl -s -o /tmp/figma-design.png "$IMAGE_URL"
```

### 8-2. 앱 스크린샷 캡처

플랫폼별 명령:
```bash
# iOS 시뮬레이터
xcrun simctl io booted screenshot /tmp/app-screenshot.png

# Android 에뮬레이터
adb exec-out screencap -p > /tmp/app-screenshot.png

# Web (Puppeteer)
npx puppeteer screenshot http://localhost:3000 \
  --viewport {선택한_버전_maxWidth}x932 \
  --output /tmp/app-screenshot.png
```

**앱 미실행 시:**
- `npm start` / `expo start` 자동 시도
- 30초 대기 후 재시도 (최대 3회)
- 실패하면 Gemini 비교 건너뛰고 계속 진행

### 8-3. Gemini 비교 (Bash 필수!)

```bash
GEMINI_KEY="{Step 0에서 로드한 GEMINI_API_KEY}"

curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${GEMINI_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"text": "두 이미지를 비교하세요.\n\n검증:\n1. 이미지: 마스코트/아이콘 동일?\n2. 레이아웃: 위치 동일?\n3. 크기: 비율 동일?\n\nJSON 응답:\n{\"matchPercentage\": 85, \"imageIssues\": [...], \"layoutIssues\": [...], \"sizeIssues\": [...]}"},
        {"inline_data": {"mime_type": "image/png", "data": "'$(base64 -i /tmp/figma-design.png)'"}},
        {"inline_data": {"mime_type": "image/png", "data": "'$(base64 -i /tmp/app-screenshot.png)'"}}
      ]
    }]
  }'
```

**에러 처리:**
- API 키 오류 → Step 0으로 돌아가 환경변수 재로드
- 이미지 인식 실패 → 스크린샷 재캡처 (최대 3회)
- 네트워크 오류 → 5초 대기 후 재시도 (최대 3회)

### 8-4. 자동 수정

Gemini 결과에 따라:
- `imageIssues` → 이미지 재다운로드 또는 경로 수정
- `layoutIssues` → 정렬 속성 수정 (justifyContent, alignItems)
- `sizeIssues` → width/height 값 수정

### 8-5. 반복

```
if (matchPercentage >= 95 || 반복 >= 5):
  종료
else:
  앱 재빌드
  Step 8-2로 돌아가기
```

---

## Step 9: 최종 리포트

```markdown
# Figma → Code 변환 완료

## 설정
- 플랫폼: {platform}
- 버전: {versions}

## 변환된 페이지
| 페이지 | 파일 | 아이콘 |
|--------|------|--------|
| ... | ... | ...개 |

## 생성된 파일
- src/utils/responsive.ts
- src/screens/*.tsx
- assets/icons/ (N개)

## Gemini 비교
- 평균 일치율: X%
- 자동 수정: N건

## 다음 단계
1. npm start 또는 expo start
2. 각 버전에서 확인
```

---

# 참조 문서

- `references/figma-mapping.md` - Figma → 코드 변환 규칙 **(스케일링 필수 참조!)**
- `references/responsive-utils-rn.md` - React Native 유틸리티
- `references/responsive-utils-web.md` - Web 유틸리티
- `references/gemini-compare.md` - Gemini 비교 상세

---

# 핵심 원칙 (다시 강조)

1. **이미지는 100% Figma API 다운로드만 허용**
   - SVG 코드 직접 작성 절대 금지
   - Bash로 curl 실행 필수

2. **Gemini 검증은 무조건 실행**
   - API 키 없으면 사용자에게 요청
   - 5차까지 반복하며 95% 달성

3. **서브에이전트에 환경변수 전달 필수**
   - prompt에 FIGMA_API_TOKEN, GEMINI_API_KEY 직접 포함

4. **스케일링 함수 정확히 사용**
   - `scaleWidth` vs `scaleHeight` 구분
   - +2px (폰트), +5px (간격) 규칙 준수
