# Figma → 코드 매핑 규칙

Figma 디자인 요소를 React Native / Web 코드로 변환하는 규칙입니다.

## iOS 시스템 UI 요소 제거

앱 개발 시 불필요한 iOS 시스템 UI 요소를 자동으로 식별하고 제거합니다.

### 제거 대상 요소

#### 1. 상단 상태바 (Status Bar)

iPhone의 시간, 배터리, 신호 강도 등을 표시하는 영역.

**식별 기준:**
- 노드 이름에 다음 키워드 포함 (대소문자 무시):
  - `status bar`, `statusbar`, `status-bar`
  - `time`, `battery`, `signal`, `carrier`
  - `notch`, `dynamic island`
- 위치: 화면 최상단 (y = 0 또는 y < 60)
- 크기 범위:
  - 높이: 44px ~ 59px (노치/다이나믹 아일랜드 기기)
  - 높이: 20px ~ 24px (구형 기기)
  - 너비: 화면 전체 (90% 이상)

**일반적인 Figma 이름 패턴:**
```
Status Bar
Status bar
status-bar
iPhone Status Bar
iOS Status Bar
Time / Battery / Signal
Notch
Dynamic Island
```

#### 2. 하단 홈 인디케이터 (Home Indicator)

iPhone X 이후 기기의 하단 홈 바.

**식별 기준:**
- 노드 이름에 다음 키워드 포함 (대소문자 무시):
  - `home indicator`, `homeindicator`, `home-indicator`
  - `home bar`, `homebar`, `home-bar`
  - `bottom bar`, `swipe bar`
  - `indicator bar`
- 위치: 화면 최하단 (부모 높이 - y < 40)
- 크기 범위:
  - 높이: 5px ~ 8px
  - 너비: 130px ~ 140px (중앙 정렬)
  - 또는 영역 높이: 34px (Safe Area)

**일반적인 Figma 이름 패턴:**
```
Home Indicator
home indicator
Home Bar
Bottom Indicator
iPhone Home Indicator
Safe Area - Bottom
```

### 제거 로직

```typescript
interface FigmaNode {
  name: string;
  absoluteBoundingBox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  parent?: FigmaNode;
}

// iOS 시스템 UI 요소 감지
const isIOSSystemElement = (node: FigmaNode, screenHeight: number): boolean => {
  const name = node.name.toLowerCase();
  const { y, height, width } = node.absoluteBoundingBox;

  // 1. 상태바 키워드 검사
  const statusBarKeywords = [
    'status bar', 'statusbar', 'status-bar',
    'battery', 'signal', 'carrier', 'time',
    'notch', 'dynamic island'
  ];

  const isStatusBarByName = statusBarKeywords.some(kw => name.includes(kw));
  const isStatusBarByPosition = y < 60 && height >= 20 && height <= 59;

  if (isStatusBarByName || (isStatusBarByPosition && width > 350)) {
    return true;
  }

  // 2. 홈 인디케이터 키워드 검사
  const homeIndicatorKeywords = [
    'home indicator', 'homeindicator', 'home-indicator',
    'home bar', 'homebar', 'home-bar',
    'bottom indicator', 'swipe bar', 'indicator bar'
  ];

  const isHomeIndicatorByName = homeIndicatorKeywords.some(kw => name.includes(kw));
  const bottomPosition = screenHeight - (y + height);
  const isHomeIndicatorByPosition = bottomPosition < 40 && height <= 40;

  if (isHomeIndicatorByName || isHomeIndicatorByPosition) {
    // 홈 인디케이터 바 자체 (작은 바)
    if (height >= 5 && height <= 8 && width >= 100 && width <= 150) {
      return true;
    }
    // Safe Area 영역 (34px 높이)
    if (height >= 30 && height <= 40 && isHomeIndicatorByName) {
      return true;
    }
  }

  return false;
};

// 노드 필터링
const filterIOSSystemElements = (
  nodes: FigmaNode[],
  screenHeight: number
): FigmaNode[] => {
  return nodes.filter(node => !isIOSSystemElement(node, screenHeight));
};
```

### 변환 시 처리 방법

1. **완전 제거**: 상태바/홈 인디케이터 노드는 코드로 변환하지 않음
2. **SafeAreaView 사용**: React Native에서는 SafeAreaView로 자동 대체
3. **레이아웃 조정**: 제거된 영역만큼 레이아웃 위치 조정

```tsx
// React Native 변환 예시
import { SafeAreaView } from 'react-native-safe-area-context';

const Screen = () => {
  return (
    <SafeAreaView style={{ flex: 1 }}>
      {/* 변환된 콘텐츠 (상태바/홈 인디케이터 제외) */}
    </SafeAreaView>
  );
};
```

### 로그 출력

시스템 UI 요소 제거 시 로그 출력:

```
[iOS System UI] 제거됨: "Status Bar" (44px, 상단)
[iOS System UI] 제거됨: "Home Indicator" (34px, 하단)
```

## 노드 타입 매핑

### React Native

| Figma 타입 | React Native |
|-----------|--------------|
| FRAME | `<View>` |
| GROUP | `<View>` |
| TEXT | `<Text>` |
| RECTANGLE | `<View>` |
| ELLIPSE | `<View>` (borderRadius: 50%) |
| VECTOR | SVG 컴포넌트 |
| IMAGE | `<Image>` |
| COMPONENT | 커스텀 컴포넌트 |
| INSTANCE | 컴포넌트 사용 |

### Web / Next.js

| Figma 타입 | HTML/React |
|-----------|------------|
| FRAME | `<div>` |
| GROUP | `<div>` |
| TEXT | `<p>`, `<span>`, `<h1>`~`<h6>` |
| RECTANGLE | `<div>` |
| ELLIPSE | `<div>` (borderRadius: 50%) |
| VECTOR | `<svg>` |
| IMAGE | `<img>` 또는 `<Image>` (Next.js) |
| COMPONENT | 커스텀 컴포넌트 |
| INSTANCE | 컴포넌트 사용 |

## 스케일링 함수 사용 규칙 (중요!)

### 핵심 원칙

**Figma 디자인 값보다 항상 크게 적용:**
- **폰트 크기**: Figma 값 + 2~3px → `scaleFont(figmaValue + 2)` 또는 `scaleFont(figmaValue + 3)`
- **마진/패딩**: Figma 값 + 4~6px
  - 가로 여백 (left, right, horizontal) → `scaleWidth(figmaValue + 5)`
  - 세로 여백 (top, bottom, vertical) → `scaleHeight(figmaValue + 5)`
- **이미지/요소 크기**:
  - 너비 → `scaleWidth(figmaValue)`
  - 높이 → `scaleHeight(figmaValue)`

### 함수별 사용 용도

| 함수 | 용도 | 예시 |
|------|------|------|
| `scaleWidth(n)` | 너비, 가로 마진/패딩, 가로 간격 | `width`, `marginLeft`, `paddingRight`, `gap` (가로) |
| `scaleHeight(n)` | 높이, 세로 마진/패딩, 세로 간격 | `height`, `marginTop`, `paddingBottom`, `gap` (세로) |
| `scaleFont(n)` | 폰트 크기 전용 (항상 +2~3px 추가) | `fontSize` |

### 올바른 사용 예시

```typescript
// Figma 값: fontSize: 14, padding: 16, margin: 12, width: 200, height: 100

// ✅ 올바른 변환
const styles = StyleSheet.create({
  container: {
    width: scaleWidth(200),           // 너비 → scaleWidth
    height: scaleHeight(100),         // 높이 → scaleHeight
    paddingLeft: scaleWidth(16 + 5),  // 가로 패딩 → scaleWidth + 5px
    paddingRight: scaleWidth(16 + 5), // 가로 패딩 → scaleWidth + 5px
    paddingTop: scaleHeight(16 + 5),  // 세로 패딩 → scaleHeight + 5px
    paddingBottom: scaleHeight(16 + 5), // 세로 패딩 → scaleHeight + 5px
    marginLeft: scaleWidth(12 + 5),   // 가로 마진 → scaleWidth + 5px
    marginTop: scaleHeight(12 + 5),   // 세로 마진 → scaleHeight + 5px
  },
  text: {
    fontSize: scaleFont(14 + 2),      // 폰트 → scaleFont + 2~3px
  },
});

// ❌ 잘못된 변환 (하지 마세요)
const wrongStyles = {
  paddingHorizontal: scaleSpacing(16), // scaleSpacing 사용 금지
  marginTop: scaleWidth(12),           // 세로에 scaleWidth 사용 금지
  fontSize: scaleWidth(14),            // 폰트에 scaleWidth 사용 금지
};
```

### 간격(Gap) 방향별 적용

```typescript
// Figma: itemSpacing: 12 (flexDirection에 따라 다름)

// flexDirection: 'row' (가로 배치) → 가로 간격
gap: scaleWidth(12 + 5),

// flexDirection: 'column' (세로 배치) → 세로 간격
gap: scaleHeight(12 + 5),
```

## 크기 변환

### 기본 규칙

```typescript
// Figma 값
width: 300
height: 200

// React Native (반응형) - 각각 해당 함수 사용
width: scaleWidth(300),
height: scaleHeight(200),

// Web (반응형)
width: 'clamp(280px, 70vw, 300px)',
height: 'auto',
```

### 고정 크기 vs 유동 크기

```typescript
// Figma: Fill container (100%)
width: '100%',

// Figma: Hug contents
width: 'auto', // 또는 생략

// Figma: Fixed (300px)
width: scaleWidth(300),
```

## Auto Layout 변환

### Flex Direction

| Figma layoutMode | CSS/RN |
|-----------------|--------|
| VERTICAL | `flexDirection: 'column'` |
| HORIZONTAL | `flexDirection: 'row'` |

### Alignment

| Figma primaryAxisAlignItems | CSS justifyContent |
|----------------------------|-------------------|
| MIN | `flex-start` |
| CENTER | `center` |
| MAX | `flex-end` |
| SPACE_BETWEEN | `space-between` |

| Figma counterAxisAlignItems | CSS alignItems |
|----------------------------|----------------|
| MIN | `flex-start` |
| CENTER | `center` |
| MAX | `flex-end` |

### Gap (간격)

```typescript
// Figma
itemSpacing: 16

// React Native - flexDirection에 따라 다름
// flexDirection: 'row' (가로 배치)
gap: scaleWidth(16 + 5),  // 가로 간격 → scaleWidth + 5px

// flexDirection: 'column' (세로 배치)
gap: scaleHeight(16 + 5), // 세로 간격 → scaleHeight + 5px

// Web
gap: fluidSpacing(16),
```

### Padding

```typescript
// Figma
paddingLeft: 24
paddingRight: 24
paddingTop: 16
paddingBottom: 16

// React Native - 가로/세로 구분하여 적용 (+5px)
paddingLeft: scaleWidth(24 + 5),   // 가로 → scaleWidth
paddingRight: scaleWidth(24 + 5),  // 가로 → scaleWidth
paddingTop: scaleHeight(16 + 5),   // 세로 → scaleHeight
paddingBottom: scaleHeight(16 + 5), // 세로 → scaleHeight

// Web
padding: `${fluidSpacing(16)} ${fluidSpacing(24)}`,
```

## 텍스트 스타일 변환

### 폰트 크기

```typescript
// Figma
fontSize: 16

// React Native - 항상 Figma 값 + 2~3px 추가
fontSize: scaleFont(16 + 2),  // 16 → 18로 변환

// Web
fontSize: fluidFont(16 + 2),
```

**중요**: 폰트는 항상 Figma 원본보다 2~3px 크게 적용합니다.

### 폰트 굵기

| Figma fontWeight | CSS/RN fontWeight |
|-----------------|-------------------|
| Thin | '100' |
| Light | '300' |
| Regular | '400' |
| Medium | '500' |
| SemiBold | '600' |
| Bold | '700' |
| ExtraBold | '800' |
| Black | '900' |

### 줄 높이

```typescript
// Figma (lineHeightPx)
lineHeightPx: 24

// React Native
lineHeight: scaleFont(24),

// Web (비율)
lineHeight: 1.5, // 또는 '24px'
```

### 자간

```typescript
// Figma (letterSpacing)
letterSpacing: 0.5

// React Native / Web
letterSpacing: 0.5,
```

### 텍스트 정렬

| Figma textAlignHorizontal | CSS textAlign |
|--------------------------|---------------|
| LEFT | 'left' |
| CENTER | 'center' |
| RIGHT | 'right' |
| JUSTIFIED | 'justify' |

## 색상 변환

### RGB → Hex

```typescript
// Figma (0-1 범위)
{ r: 0.1, g: 0.2, b: 0.3, a: 1 }

// 변환 함수
const rgbToHex = (r: number, g: number, b: number): string => {
  const toHex = (n: number) => Math.round(n * 255).toString(16).padStart(2, '0');
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
};

// 결과
'#1A334D'
```

### RGBA (투명도 포함)

```typescript
// Figma
{ r: 0.1, g: 0.2, b: 0.3, a: 0.5 }

// 결과
'rgba(26, 51, 77, 0.5)'
```

## 그림자 (Effects)

### Drop Shadow

```typescript
// Figma effect
{
  type: 'DROP_SHADOW',
  color: { r: 0, g: 0, b: 0, a: 0.1 },
  offset: { x: 0, y: 4 },
  radius: 8,
  spread: 0
}

// React Native
shadowColor: '#000',
shadowOffset: { width: 0, height: 4 },
shadowOpacity: 0.1,
shadowRadius: 8,
elevation: 4, // Android

// Web
boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.1)',
```

## 모서리 둥글기

```typescript
// Figma
cornerRadius: 12

// React Native
borderRadius: scaleWidth(12),

// Web
borderRadius: '12px',
```

### 개별 모서리

```typescript
// Figma
topLeftRadius: 12
topRightRadius: 12
bottomLeftRadius: 0
bottomRightRadius: 0

// React Native
borderTopLeftRadius: scaleWidth(12),
borderTopRightRadius: scaleWidth(12),
borderBottomLeftRadius: 0,
borderBottomRightRadius: 0,

// Web
borderRadius: '12px 12px 0 0',
```

## 테두리 (Stroke)

```typescript
// Figma
strokeWeight: 1
strokes: [{ color: { r: 0.9, g: 0.9, b: 0.9, a: 1 } }]

// React Native / Web
borderWidth: 1,
borderColor: '#E5E5E5',
```

## 아이콘 추출

### 아이콘 식별 기준

다음 조건 중 하나라도 만족하면 아이콘으로 판단:

1. 노드 이름에 "icon", "Icon", "svg", "SVG" 포함
2. 노드 타입이 VECTOR 또는 BOOLEAN_OPERATION
3. 크기가 12~64px 범위

### SVG 저장

```
assets/icons/
├── home.svg
├── search.svg
├── notification.svg
├── profile.svg
└── index.ts
```

### index.ts 생성

```typescript
// React Native (react-native-svg)
export { default as HomeIcon } from './home.svg';
export { default as SearchIcon } from './search.svg';
export { default as NotificationIcon } from './notification.svg';
export { default as ProfileIcon } from './profile.svg';

// Web
export { ReactComponent as HomeIcon } from './home.svg';
export { ReactComponent as SearchIcon } from './search.svg';
```

### 아이콘 사용

```tsx
import { HomeIcon } from '@/assets/icons';

// React Native
<HomeIcon width={scaleWidth(24)} height={scaleWidth(24)} fill="#000" />

// Web
<HomeIcon width={24} height={24} fill="#000" />
```

## 이미지 처리

### React Native

```tsx
<Image
  source={{ uri: 'image-url' }}
  style={{
    width: scaleWidth(200),
    height: scaleWidth(150), // 비율 유지
  }}
  resizeMode="cover"
/>
```

### Web (Next.js)

```tsx
import Image from 'next/image';

<Image
  src="/images/photo.jpg"
  alt="Description"
  width={200}
  height={150}
  style={{ objectFit: 'cover' }}
/>
```

## 컴포넌트 명명 규칙

| Figma 이름 | 파일명 | 컴포넌트명 |
|-----------|--------|-----------|
| Header | Header.tsx | Header |
| Primary Button | PrimaryButton.tsx | PrimaryButton |
| user-avatar | UserAvatar.tsx | UserAvatar |
| Card/Large | CardLarge.tsx | CardLarge |

### 변환 규칙

1. 공백 → 제거
2. 하이픈(-) → PascalCase
3. 슬래시(/) → 제거하고 합침
4. 첫 글자 대문자
