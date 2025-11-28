# Gemini 디자인 비교

Gemini AI를 사용하여 Figma 원본 디자인과 개발된 화면을 비교하고 자동 수정합니다.

## 환경 설정

### 환경 변수

```bash
export GEMINI_API_KEY="your-api-key"
```

### 확인 방법

```bash
echo $GEMINI_API_KEY
```

## 스크린샷 캡처

### 1. iOS 시뮬레이터

```bash
xcrun simctl io booted screenshot /tmp/ios-screenshot.png
```

### 2. Android 에뮬레이터

```bash
adb exec-out screencap -p > /tmp/android-screenshot.png
```

### 3. Web (Puppeteer)

```bash
# Puppeteer가 설치되어 있어야 함
npx puppeteer screenshot http://localhost:3000 \
  --viewport 430x932 \
  --output /tmp/web-mobile.png
```

### 4. 여러 뷰포트 캡처

```bash
# Mobile
npx puppeteer screenshot http://localhost:3000 \
  --viewport 430x932 \
  --output /tmp/web-mobile.png

# Tablet
npx puppeteer screenshot http://localhost:3000 \
  --viewport 834x1194 \
  --output /tmp/web-tablet.png

# PC
npx puppeteer screenshot http://localhost:3000 \
  --viewport 1440x900 \
  --output /tmp/web-pc.png
```

## Figma 디자인 이미지 가져오기

### 방법 1: Figma REST API 직접 호출 (권장)

MCP 한계로 이미지를 가져오지 못할 경우, `.env`의 `FIGMA_API_TOKEN`을 사용하여 직접 API 호출:

```bash
# .env에서 토큰 로드
source .env 2>/dev/null || export FIGMA_API_TOKEN="${FIGMA_API_TOKEN}"

# Figma URL에서 file_key와 node_id 추출
# URL 형식: https://www.figma.com/file/{file_key}?node-id={node_id}
# 또는: https://www.figma.com/design/{file_key}/...?node-id={node_id}

FILE_KEY="파일키"
NODE_ID="노드아이디"  # URL 인코딩 필요 (예: 123-456 또는 123:456)

# 이미지 URL 가져오기
IMAGE_RESPONSE=$(curl -s -H "X-Figma-Token: $FIGMA_API_TOKEN" \
  "https://api.figma.com/v1/images/${FILE_KEY}?ids=${NODE_ID}&format=png&scale=2")

# 응답에서 이미지 URL 추출
IMAGE_URL=$(echo $IMAGE_RESPONSE | grep -o '"[^"]*\.png[^"]*"' | head -1 | tr -d '"')

# 이미지 다운로드
curl -s -o /tmp/figma-design.png "$IMAGE_URL"
```

### Figma URL 파싱 함수

```bash
# Figma URL에서 file_key와 node_id 추출하는 함수
parse_figma_url() {
  local url="$1"

  # file_key 추출 (file/ 또는 design/ 뒤의 값)
  FILE_KEY=$(echo "$url" | grep -oE '(file|design)/[^/\?]+' | cut -d'/' -f2)

  # node-id 추출 및 URL 디코딩
  NODE_ID=$(echo "$url" | grep -oE 'node-id=[^&]+' | cut -d'=' -f2)

  # %3A를 :로, -를 :로 변환 (Figma API 형식)
  NODE_ID_ENCODED=$(echo "$NODE_ID" | sed 's/%3A/:/g' | sed 's/-/:/g')

  echo "FILE_KEY=$FILE_KEY"
  echo "NODE_ID=$NODE_ID_ENCODED"
}

# 사용 예시
parse_figma_url "https://www.figma.com/design/ABC123/Project?node-id=1-234"
```

### 전체 이미지 다운로드 스크립트

```bash
#!/bin/bash
# figma-image-download.sh

download_figma_image() {
  local FIGMA_URL="$1"
  local OUTPUT_PATH="${2:-/tmp/figma-design.png}"

  # .env 파일에서 토큰 로드
  if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
  fi

  if [ -z "$FIGMA_API_TOKEN" ]; then
    echo "Error: FIGMA_API_TOKEN not found in .env"
    return 1
  fi

  # URL 파싱
  FILE_KEY=$(echo "$FIGMA_URL" | grep -oE '(file|design)/[^/\?]+' | cut -d'/' -f2)
  NODE_ID=$(echo "$FIGMA_URL" | grep -oE 'node-id=[^&]+' | cut -d'=' -f2 | sed 's/%3A/:/g' | sed 's/-/:/g')

  echo "Fetching image for: $FILE_KEY / $NODE_ID"

  # 이미지 URL 요청
  RESPONSE=$(curl -s -H "X-Figma-Token: $FIGMA_API_TOKEN" \
    "https://api.figma.com/v1/images/${FILE_KEY}?ids=${NODE_ID}&format=png&scale=2")

  # 에러 체크
  if echo "$RESPONSE" | grep -q '"err"'; then
    echo "Error: $(echo $RESPONSE | grep -o '"err":"[^"]*"')"
    return 1
  fi

  # 이미지 URL 추출 및 다운로드
  IMAGE_URL=$(echo "$RESPONSE" | grep -o 'https://[^"]*\.png[^"]*' | head -1)

  if [ -z "$IMAGE_URL" ]; then
    echo "Error: Could not extract image URL"
    echo "Response: $RESPONSE"
    return 1
  fi

  curl -s -o "$OUTPUT_PATH" "$IMAGE_URL"
  echo "Image saved to: $OUTPUT_PATH"
}

# 사용 예시
# download_figma_image "https://www.figma.com/design/ABC/Project?node-id=1-234" "/tmp/design.png"
```

### 방법 2: Figma MCP 사용

Figma MCP가 정상 동작하는 경우:

```
mcp__figma 관련 도구를 사용하여 PNG 이미지 가져오기
```

### 환경 변수 확인

```bash
# .env 파일 확인
cat .env | grep FIGMA_API_TOKEN

# 토큰 유효성 테스트
curl -s -H "X-Figma-Token: $FIGMA_API_TOKEN" \
  "https://api.figma.com/v1/me" | head -c 200
```

저장 위치: `/tmp/figma-design.png`

## Gemini API 비교 호출

### 방법 1: Gemini CLI 사용 (권장)

```bash
# .env에서 API 키 로드
export GEMINI_API_KEY=$(grep GEMINI_API_KEY .env | cut -d'=' -f2 | tr -d '"')

# 이미지 비교 실행
GEMINI_API_KEY="$GEMINI_API_KEY" gemini -m gemini-2.5-flash \
  --image /tmp/figma-design.png \
  --image /tmp/dev-screenshot.png \
  "두 이미지를 비교해서 UI 차이점을 JSON으로 알려줘"
```

### 방법 2: Gemini REST API 직접 호출 (대안)

Gemini CLI가 설치되지 않은 경우, curl로 직접 API 호출:

```bash
#!/bin/bash
# gemini-compare.sh

compare_designs() {
  local FIGMA_IMAGE="$1"
  local DEV_IMAGE="$2"

  # .env 파일에서 API 키 로드
  if [ -f ".env" ]; then
    export GEMINI_API_KEY=$(grep GEMINI_API_KEY .env | cut -d'=' -f2 | tr -d '"')
    export GEMINI_MODEL=$(grep GEMINI_MODEL .env | cut -d'=' -f2 | tr -d '"')
  fi

  GEMINI_MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"

  if [ -z "$GEMINI_API_KEY" ]; then
    echo "Error: GEMINI_API_KEY not found"
    return 1
  fi

  # 이미지를 base64로 인코딩
  FIGMA_BASE64=$(base64 -i "$FIGMA_IMAGE" | tr -d '\n')
  DEV_BASE64=$(base64 -i "$DEV_IMAGE" | tr -d '\n')

  # API 요청 JSON 생성
  REQUEST_JSON=$(cat <<JSONEOF
{
  "contents": [{
    "parts": [
      {
        "inline_data": {
          "mime_type": "image/png",
          "data": "$FIGMA_BASE64"
        }
      },
      {
        "inline_data": {
          "mime_type": "image/png",
          "data": "$DEV_BASE64"
        }
      },
      {
        "text": "당신은 UI/UX 디자인 검수 전문가입니다.\n\n두 이미지를 비교 분석해주세요:\n- 첫 번째 이미지: Figma 원본 디자인\n- 두 번째 이미지: 개발된 실제 화면\n\n## 비교 항목\n\n1. **레이아웃**: 요소 위치, 정렬, 간격, 크기\n2. **타이포그래피**: 폰트 크기, 굵기, 행간\n3. **색상**: 배경색, 텍스트 색상, 버튼 색상\n4. **아이콘/이미지**: 크기, 위치\n\n## 출력 형식\n\n반드시 다음 JSON 형식으로만 출력해주세요:\n\n{\"overallMatchPercentage\": 87, \"summary\": \"전체적인 요약\", \"issues\": [{\"id\": 1, \"category\": \"spacing\", \"element\": \"Header\", \"description\": \"설명\", \"currentValue\": \"16px\", \"expectedValue\": \"24px\", \"priority\": \"high\", \"suggestedFix\": \"수정 제안\"}], \"passed\": [\"통과 항목\"]}"
      }
    ]
  }],
  "generationConfig": {
    "temperature": 0.1,
    "maxOutputTokens": 2048
  }
}
JSONEOF
)

  # Gemini API 호출
  RESPONSE=$(curl -s \
    "https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$REQUEST_JSON")

  echo "$RESPONSE"
}

# 사용 예시
# compare_designs "/tmp/figma-design.png" "/tmp/dev-screenshot.png"
```

### Gemini API 키 테스트

```bash
# .env에서 키 로드 및 테스트
GEMINI_API_KEY=$(grep GEMINI_API_KEY .env | cut -d'=' -f2 | tr -d '"')

curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=${GEMINI_API_KEY}" | head -c 500
```

### Gemini CLI 상세 프롬프트 예시

더 정밀한 비교가 필요한 경우:

```bash
export GEMINI_API_KEY=$(grep GEMINI_API_KEY .env | cut -d'=' -f2 | tr -d '"')

GEMINI_API_KEY="$GEMINI_API_KEY" gemini -m gemini-2.5-flash \
  --image /tmp/figma-design.png \
  --image /tmp/dev-screenshot.png \
  "당신은 UI/UX 디자인 검수 전문가입니다. 두 이미지를 비교하세요. 첫 번째: Figma 원본, 두 번째: 개발 화면. 비교 항목: 1) 레이아웃(위치, 정렬, 간격, 크기) 2) 타이포그래피(폰트 크기, 굵기, 행간) 3) 색상(배경, 텍스트, 버튼) 4) 아이콘 크기/위치. 결과를 JSON으로 출력: {overallMatchPercentage, summary, issues: [{id, category, element, description, currentValue, expectedValue, priority, suggestedFix}], passed: []}"
```

## 응답 처리

### JSON 파싱

```typescript
interface GeminiResponse {
  overallMatchPercentage: number;
  summary: string;
  issues: Issue[];
  passed: string[];
}

interface Issue {
  id: number;
  category: 'spacing' | 'typography' | 'color' | 'layout' | 'icon';
  element: string;
  description: string;
  currentValue: string;
  expectedValue: string;
  priority: 'high' | 'medium' | 'low';
  suggestedFix: string;
}
```

### 우선순위별 분류

```typescript
const highPriority = issues.filter(i => i.priority === 'high');
const mediumPriority = issues.filter(i => i.priority === 'medium');
const lowPriority = issues.filter(i => i.priority === 'low');
```

## 자동 수정 로직

### 1. 파일 찾기

`element` 이름으로 해당 컴포넌트 파일 찾기:

```
Grep 도구로 "Header" 등의 컴포넌트 검색
```

### 2. 수정 적용

`suggestedFix`를 해당 파일에 적용:

```typescript
// 예: paddingTop: scaleSpacing(24)
// 해당 스타일 속성을 찾아서 수정
```

### 3. 카테고리별 수정 패턴

| 카테고리 | 수정 방법 |
|---------|----------|
| `spacing` | margin/padding 값 수정 |
| `typography` | fontSize, fontWeight, lineHeight 수정 |
| `color` | color, backgroundColor 수정 |
| `layout` | flexDirection, alignItems, justifyContent 수정 |
| `icon` | width, height 수정 |

## 반복 비교

```
최대 3회 반복:

1. 스크린샷 캡처
2. Gemini 비교
3. 일치율 확인
   - 95% 이상: 완료
   - 95% 미만: 자동 수정 후 재비교

3회 후에도 95% 미만이면:
- 남은 이슈 목록 표시
- 수동 확인 권장
```

## 에러 처리

### API 키 없음

```
GEMINI_API_KEY가 설정되지 않았습니다.

다음 중 선택하세요:
1. 비교 건너뛰고 진행
2. API 키 설정 후 재시도
```

### 스크린샷 캡처 실패

```
스크린샷 캡처에 실패했습니다.

가능한 원인:
- 시뮬레이터/에뮬레이터가 실행 중이지 않음
- 앱이 실행 중이지 않음
- 권한 문제

다음 중 선택하세요:
1. 비교 건너뛰고 진행
2. 다시 시도
```

### Gemini API 실패

```
Gemini API 호출에 실패했습니다.

가능한 원인:
- API 키가 잘못됨
- 할당량 초과
- 네트워크 오류

다음 중 선택하세요:
1. 비교 건너뛰고 진행
2. 다시 시도
```

## 결과 리포트 형식

```markdown
## Gemini 디자인 비교 결과

### 일치율: 87%

### 수정된 이슈 (3건)

| # | 카테고리 | 요소 | 수정 내용 |
|---|---------|------|----------|
| 1 | spacing | Header | paddingTop: 16 → 24 |
| 2 | typography | Title | fontSize: 20 → 24 |
| 3 | color | Button | backgroundColor: #333 → #1A1A1A |

### 확인 필요 (1건)

| # | 카테고리 | 요소 | 설명 |
|---|---------|------|------|
| 1 | icon | Logo | 커스텀 아이콘 확인 필요 |

### 통과 항목

- 배경색 일치
- 버튼 스타일 일치
- 레이아웃 구조 일치
```
