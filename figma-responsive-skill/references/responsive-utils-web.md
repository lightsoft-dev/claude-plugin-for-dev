# Web / Next.js 반응형 유틸리티

## 생성할 파일

`src/utils/responsive.ts`

## 전체 코드

```typescript
'use client'; // Next.js App Router 사용 시

import { useState, useEffect } from 'react';

// ===== 타입 정의 =====
type VersionType = 'mobile' | 'tablet' | 'pc';

interface VersionConfig {
  enabled: boolean;
  minWidth: number;
  maxWidth: number | null;
}

// ===== 설정 (figma-responsive.config.json에서 주입) =====
const VERSION_CONFIGS: Record<VersionType, VersionConfig> = {
  mobile: {
    enabled: {{MOBILE_ENABLED}},
    minWidth: {{MOBILE_MIN}},
    maxWidth: {{MOBILE_MAX}}
  },
  tablet: {
    enabled: {{TABLET_ENABLED}},
    minWidth: {{TABLET_MIN}},
    maxWidth: {{TABLET_MAX}}
  },
  pc: {
    enabled: {{PC_ENABLED}},
    minWidth: {{PC_MIN}},
    maxWidth: {{PC_MAX}}
  }
};

// 스케일링 설정
const SCALING = {
  textSizeIncrease: {{TEXT_INCREASE}},  // 기본: 2
  spacingIncrease: {{SPACING_INCREASE}} // 기본: 5
};

// ===== 브레이크포인트 추출 =====
export const breakpoints = {
  mobile: VERSION_CONFIGS.mobile.maxWidth ?? 430,
  tablet: VERSION_CONFIGS.tablet.maxWidth ?? 834,
  pc: VERSION_CONFIGS.pc.minWidth ?? 835,
};

// ===== 미디어 쿼리 =====
export const media = {
  mobile: `@media (max-width: ${breakpoints.mobile}px)`,
  tablet: `@media (min-width: ${breakpoints.mobile + 1}px) and (max-width: ${breakpoints.tablet}px)`,
  pc: `@media (min-width: ${breakpoints.pc}px)`,
};

// ===== CSS 변수 =====
export const cssVariables = `
:root {
  --breakpoint-mobile: ${breakpoints.mobile}px;
  --breakpoint-tablet: ${breakpoints.tablet}px;
  --breakpoint-pc: ${breakpoints.pc}px;

  --text-increase: ${SCALING.textSizeIncrease}px;
  --spacing-increase: ${SCALING.spacingIncrease}px;
}
`;

// ===== React Hook: useResponsive =====
interface UseResponsiveResult {
  version: VersionType;
  isMobile: boolean;
  isTablet: boolean;
  isPc: boolean;
  width: number;
  height: number;
}

export const useResponsive = (): UseResponsiveResult => {
  const [state, setState] = useState<UseResponsiveResult>({
    version: 'pc',
    isMobile: false,
    isTablet: false,
    isPc: true,
    width: typeof window !== 'undefined' ? window.innerWidth : breakpoints.pc,
    height: typeof window !== 'undefined' ? window.innerHeight : 900,
  });

  useEffect(() => {
    const updateState = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;

      let version: VersionType = 'pc';
      if (width <= breakpoints.mobile) {
        version = 'mobile';
      } else if (width <= breakpoints.tablet) {
        version = 'tablet';
      }

      setState({
        version,
        isMobile: version === 'mobile',
        isTablet: version === 'tablet',
        isPc: version === 'pc',
        width,
        height,
      });
    };

    updateState();
    window.addEventListener('resize', updateState);
    return () => window.removeEventListener('resize', updateState);
  }, []);

  return state;
};

// ===== Fluid Typography (clamp 기반) =====
/**
 * 유동적 폰트 크기 (뷰포트에 따라 자동 조절)
 * @param minSize - 최소 폰트 크기 (mobile)
 * @param maxSize - 최대 폰트 크기 (pc) - 자동으로 textSizeIncrease 적용
 */
export const fluidFont = (minSize: number, maxSize?: number): string => {
  const actualMaxSize = (maxSize ?? minSize) + SCALING.textSizeIncrease;
  const minVw = breakpoints.mobile;
  const maxVw = breakpoints.pc;

  const slope = (actualMaxSize - minSize) / (maxVw - minVw);
  const intercept = minSize - slope * minVw;

  return `clamp(${minSize}px, ${intercept.toFixed(4)}px + ${(slope * 100).toFixed(4)}vw, ${actualMaxSize}px)`;
};

// ===== Fluid Spacing =====
/**
 * 유동적 간격 (뷰포트에 따라 자동 조절)
 * @param minSpacing - 최소 간격 (mobile)
 * @param maxSpacing - 최대 간격 (pc) - 자동으로 spacingIncrease 적용
 */
export const fluidSpacing = (minSpacing: number, maxSpacing?: number): string => {
  const actualMaxSpacing = (maxSpacing ?? minSpacing) + SCALING.spacingIncrease;
  return fluidFont(minSpacing, actualMaxSpacing);
};

// ===== 조건부 값 반환 =====
/**
 * 버전별 다른 값 반환
 * @example
 * const padding = responsive({ mobile: '16px', tablet: '24px', pc: '32px' });
 */
export const responsive = <T>(values: Partial<Record<VersionType, T>>): Record<VersionType, T> => {
  const defaultValue = values.pc ?? values.tablet ?? values.mobile;
  return {
    mobile: values.mobile ?? defaultValue as T,
    tablet: values.tablet ?? values.mobile ?? defaultValue as T,
    pc: values.pc ?? values.tablet ?? values.mobile ?? defaultValue as T,
  };
};

// ===== Tailwind CSS 클래스 생성 (선택적) =====
/**
 * Tailwind 반응형 클래스 생성
 * @example
 * tw({ mobile: 'p-4', tablet: 'p-6', pc: 'p-8' })
 * // => "p-4 md:p-6 lg:p-8"
 */
export const tw = (classes: Partial<Record<VersionType, string>>): string => {
  const result: string[] = [];

  if (classes.mobile) {
    result.push(classes.mobile);
  }
  if (classes.tablet) {
    result.push(classes.tablet.split(' ').map(c => `md:${c}`).join(' '));
  }
  if (classes.pc) {
    result.push(classes.pc.split(' ').map(c => `lg:${c}`).join(' '));
  }

  return result.join(' ');
};
```

## Tailwind CSS 설정 (tailwind.config.js)

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    screens: {
      'sm': '{{MOBILE_MAX}}px',   // Mobile max
      'md': '{{TABLET_MIN}}px',   // Tablet min
      'lg': '{{PC_MIN}}px',       // PC min
    },
  },
};
```

## 사용 예시

### 1. useResponsive 훅 사용

```tsx
import { useResponsive, fluidFont, fluidSpacing } from '@/utils/responsive';

const MyComponent = () => {
  const { version, isMobile, isTablet, isPc } = useResponsive();

  return (
    <div
      style={{
        fontSize: fluidFont(16, 18),      // 16px ~ 20px (18+2)
        padding: fluidSpacing(16, 24),    // 16px ~ 29px (24+5)
      }}
    >
      현재 버전: {version}
      {isMobile && <MobileLayout />}
      {isTablet && <TabletLayout />}
      {isPc && <PcLayout />}
    </div>
  );
};
```

### 2. CSS-in-JS 스타일

```tsx
const styles = {
  container: {
    fontSize: fluidFont(24),        // 24px ~ 26px
    padding: fluidSpacing(16),      // 16px ~ 21px
    marginBottom: fluidSpacing(24), // 24px ~ 29px
  },
};
```

### 3. Tailwind CSS 사용

```tsx
import { tw } from '@/utils/responsive';

const MyComponent = () => {
  return (
    <div className={tw({
      mobile: 'p-4 text-base',
      tablet: 'p-6 text-lg',
      pc: 'p-8 text-xl'
    })}>
      반응형 컨텐츠
    </div>
  );
};

// 결과: "p-4 text-base md:p-6 md:text-lg lg:p-8 lg:text-xl"
```

### 4. 미디어 쿼리 사용 (styled-components 등)

```tsx
import styled from 'styled-components';
import { media, fluidFont } from '@/utils/responsive';

const Title = styled.h1`
  font-size: ${fluidFont(24)};

  ${media.mobile} {
    text-align: center;
  }

  ${media.tablet} {
    text-align: left;
  }

  ${media.pc} {
    text-align: left;
    max-width: 800px;
  }
`;
```

## 플레이스홀더 치환 규칙

| 플레이스홀더 | 설명 | 예시 |
|-------------|------|------|
| `{{MOBILE_ENABLED}}` | Mobile 활성화 여부 | `true` |
| `{{MOBILE_MIN}}` | Mobile 최소 너비 | `0` |
| `{{MOBILE_MAX}}` | Mobile 최대 너비 | `430` |
| `{{TABLET_ENABLED}}` | Tablet 활성화 여부 | `true` |
| `{{TABLET_MIN}}` | Tablet 최소 너비 | `431` |
| `{{TABLET_MAX}}` | Tablet 최대 너비 | `834` |
| `{{PC_ENABLED}}` | PC 활성화 여부 | `false` |
| `{{PC_MIN}}` | PC 최소 너비 | `835` |
| `{{PC_MAX}}` | PC 최대 너비 | `null` |
| `{{TEXT_INCREASE}}` | 텍스트 크기 증가 | `2` |
| `{{SPACING_INCREASE}}` | 간격 증가 | `5` |
