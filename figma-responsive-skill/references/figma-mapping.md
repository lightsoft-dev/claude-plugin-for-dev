# Figma → 코드 매핑 규칙

Figma 디자인 요소를 React Native / Web 코드로 변환하는 규칙입니다.

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

## 크기 변환

### 기본 규칙

```typescript
// Figma 값
width: 300
height: 200

// React Native (반응형)
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

// React Native
gap: scaleSpacing(16),

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

// React Native
paddingHorizontal: scaleSpacing(24),
paddingVertical: scaleSpacing(16),

// Web
padding: `${fluidSpacing(16)} ${fluidSpacing(24)}`,
```

## 텍스트 스타일 변환

### 폰트 크기

```typescript
// Figma
fontSize: 16

// React Native (태블릿/PC에서 +2px)
fontSize: scaleFont(16),

// Web
fontSize: fluidFont(16),
```

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
