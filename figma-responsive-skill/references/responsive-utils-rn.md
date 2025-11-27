# React Native / Expo 반응형 유틸리티

## 생성할 파일

`src/utils/responsive.ts`

## 전체 코드

```typescript
import { Dimensions, Platform } from 'react-native';

// ===== 타입 정의 =====
type VersionType = 'mobile' | 'tablet' | 'pc';

interface VersionConfig {
  enabled: boolean;
  minWidth: number;
  maxWidth: number | null;
}

// ===== 설정 (figma-responsive.config.json에서 주입) =====
// 이 값들은 커맨드 실행 시 사용자 입력에 따라 동적으로 설정됩니다
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

// ===== 화면 정보 =====
const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

// ===== 현재 버전 감지 =====
export const getCurrentVersion = (): VersionType => {
  // 활성화된 버전 중에서 현재 화면 너비에 맞는 버전 찾기
  for (const [version, config] of Object.entries(VERSION_CONFIGS)) {
    if (!config.enabled) continue;

    const { minWidth, maxWidth } = config;
    if (SCREEN_WIDTH >= minWidth && (maxWidth === null || SCREEN_WIDTH <= maxWidth)) {
      return version as VersionType;
    }
  }
  return 'mobile'; // 기본값
};

// ===== 기준 크기 가져오기 =====
const getBaseWidth = (): number => {
  const version = getCurrentVersion();
  const config = VERSION_CONFIGS[version];
  // maxWidth가 있으면 그 값을, 없으면 minWidth + 적당한 값 사용
  return config.maxWidth ?? config.minWidth + 200;
};

// ===== 유틸리티 함수들 =====

/**
 * 너비 비율 계산
 * @param size - Figma에서의 너비 값
 * @returns 현재 화면에 맞게 스케일된 너비
 */
export const scaleWidth = (size: number): number => {
  const baseWidth = getBaseWidth();
  return (SCREEN_WIDTH / baseWidth) * size;
};

/**
 * 높이 비율 계산
 * @param size - Figma에서의 높이 값
 * @returns 현재 화면에 맞게 스케일된 높이
 */
export const scaleHeight = (size: number): number => {
  const baseWidth = getBaseWidth();
  // 높이도 너비 기준으로 계산 (비율 유지)
  return (SCREEN_WIDTH / baseWidth) * size;
};

/**
 * 폰트 크기 계산
 * 태블릿/PC에서는 textSizeIncrease만큼 추가
 * @param size - Figma에서의 폰트 크기
 * @returns 현재 버전에 맞게 조정된 폰트 크기
 */
export const scaleFont = (size: number): number => {
  const version = getCurrentVersion();

  // mobile이 아니면 textSizeIncrease 추가
  const increase = version === 'mobile' ? 0 : SCALING.textSizeIncrease;
  const adjustedSize = size + increase;

  // 작은 화면에서 추가 축소
  if (SCREEN_WIDTH < 350) {
    return (SCREEN_WIDTH / 400) * adjustedSize;
  }

  return adjustedSize;
};

/**
 * 간격(마진/패딩) 계산
 * 태블릿/PC에서는 spacingIncrease만큼 추가
 * @param size - Figma에서의 간격 값
 * @returns 현재 버전에 맞게 조정된 간격
 */
export const scaleSpacing = (size: number): number => {
  const version = getCurrentVersion();

  // mobile이 아니면 spacingIncrease 추가
  const increase = version === 'mobile' ? 0 : SCALING.spacingIncrease;

  return scaleWidth(size + increase);
};

/**
 * 균등 비율 계산 (너비/높이 중 작은 비율 사용)
 * @param size - 원본 크기
 * @returns 비율 유지하며 스케일된 크기
 */
export const scale = (size: number): number => {
  const baseWidth = getBaseWidth();
  return (SCREEN_WIDTH / baseWidth) * size;
};

// ===== 화면 정보 객체 =====
export const screenInfo = {
  width: SCREEN_WIDTH,
  height: SCREEN_HEIGHT,
  version: getCurrentVersion(),
  isWeb: Platform.OS === 'web',
  isMobile: getCurrentVersion() === 'mobile',
  isTablet: getCurrentVersion() === 'tablet',
  isPc: getCurrentVersion() === 'pc',
};

// ===== 조건부 값 반환 =====
/**
 * 버전별 다른 값 반환
 * @example
 * const padding = responsive({ mobile: 16, tablet: 24, pc: 32 });
 */
export const responsive = <T>(values: Partial<Record<VersionType, T>>): T => {
  const version = getCurrentVersion();
  return (values[version] ?? values.mobile ?? values.tablet ?? values.pc) as T;
};

// ===== 이미지 크기 계산 =====
/**
 * 이미지 크기 계산 (가로세로 비율 유지)
 * @param width - Figma에서의 너비
 * @param height - Figma에서의 높이
 */
export const scaleImage = (width: number, height: number) => ({
  width: scaleWidth(width),
  height: scaleWidth(height), // 비율 유지를 위해 width 기준
});
```

## 사용 예시

```typescript
import {
  scaleWidth,
  scaleHeight,
  scaleFont,
  scaleSpacing,
  responsive,
  screenInfo
} from '@/utils/responsive';
import { StyleSheet, View, Text } from 'react-native';

const MyComponent = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Hello</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: scaleWidth(300),
    height: scaleHeight(200),
    padding: scaleSpacing(16), // 태블릿/PC에서 +5px
    marginTop: scaleSpacing(24),
  },
  title: {
    fontSize: scaleFont(24), // 태블릿/PC에서 +2px
    fontWeight: '600',
  },
});
```

## 버전별 조건부 스타일

```typescript
const styles = StyleSheet.create({
  container: {
    flexDirection: responsive({
      mobile: 'column',
      tablet: 'row',
      pc: 'row'
    }),
    padding: responsive({
      mobile: scaleSpacing(16),
      tablet: scaleSpacing(24),
      pc: scaleSpacing(32)
    }),
  },
});
```

## 플레이스홀더 치환 규칙

커맨드 실행 시 다음 플레이스홀더를 사용자 입력값으로 치환:

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
