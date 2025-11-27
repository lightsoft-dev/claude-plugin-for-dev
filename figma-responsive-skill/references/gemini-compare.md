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

Figma MCP를 사용하여 디자인 이미지 export:

```
mcp__figma 관련 도구를 사용하여 PNG 이미지 가져오기
```

저장 위치: `/tmp/figma-design.png`

## Gemini CLI 비교 호출

```bash
gemini -m gemini-2.0-flash \
  --image /tmp/figma-design.png \
  --image /tmp/dev-screenshot.png \
  --prompt "$(cat <<'EOF'
당신은 UI/UX 디자인 검수 전문가입니다.

두 이미지를 비교 분석해주세요:
- 첫 번째 이미지: Figma 원본 디자인
- 두 번째 이미지: 개발된 실제 화면

## 비교 항목

1. **레이아웃**
   - 요소 위치
   - 정렬 (좌/중앙/우)
   - 간격 (margin, padding)
   - 요소 크기

2. **타이포그래피**
   - 폰트 크기
   - 폰트 굵기
   - 행간 (line-height)
   - 자간 (letter-spacing)

3. **색상**
   - 배경색
   - 텍스트 색상
   - 버튼/요소 색상

4. **아이콘/이미지**
   - 크기
   - 위치

## 출력 형식

반드시 다음 JSON 형식으로만 출력해주세요:

{
  "overallMatchPercentage": 87,
  "summary": "전체적인 레이아웃은 일치하나 일부 간격과 폰트 크기에 차이가 있습니다.",
  "issues": [
    {
      "id": 1,
      "category": "spacing",
      "element": "Header",
      "description": "상단 패딩이 부족합니다",
      "currentValue": "16px",
      "expectedValue": "24px",
      "priority": "high",
      "suggestedFix": "paddingTop: scaleSpacing(24)"
    }
  ],
  "passed": [
    "배경색 일치",
    "버튼 스타일 일치"
  ]
}
EOF
)"
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
