# Figma Responsive Skill

Figma MCP를 활용한 반응형 코드 자동 변환 플러그인.

단일 커맨드로 Figma 디자인을 멀티 디바이스 반응형 코드로 변환하고, Gemini AI로 디자인 비교 및 자동 수정까지 지원합니다.

## 사용법

```bash
/figma-convert
```

### Step 1: 버전 선택

```
어떤 버전을 구현하시겠습니까? (다중 선택 가능)
[x] Mobile
[x] Tablet
[ ] PC
```

### Step 2: px 범위 입력

```
Mobile 범위 (기본: 0 ~ 430px): 0 ~ 430
Tablet 범위 (기본: 431 ~ 834px): 431 ~ 834
```

### Step 3: Figma 링크 입력

```
변환할 Figma 페이지 링크들을 입력하세요:
> https://figma.com/file/xxx?node-id=123
> https://figma.com/file/xxx?node-id=456
> (완료)
```

**끝! 모든 과정이 자동으로 실행됩니다.**

## 자동 실행 과정

1. 플랫폼 자동 감지 (package.json 분석)
2. Figma MCP로 디자인 데이터 가져오기
3. 페이지별 병렬 변환 (멀티 에이전트)
4. SVG 아이콘 추출 → `assets/icons/`
5. 반응형 유틸리티 생성 → `src/utils/responsive.ts`
6. Gemini 비교 & 자동 수정 (선택적)
7. 최종 리포트 출력

## 반응형 유틸리티

### React Native / Expo

```typescript
import { scaleWidth, scaleFont, scaleSpacing } from '@/utils/responsive';

const styles = StyleSheet.create({
  container: {
    width: scaleWidth(300),
    padding: scaleSpacing(16),     // 태블릿/PC에서 +5px
  },
  title: {
    fontSize: scaleFont(24),       // 태블릿/PC에서 +2px
  },
});
```

### Web / Next.js

```typescript
import { fluidFont, fluidSpacing, useResponsive } from '@/utils/responsive';

const MyComponent = () => {
  const { isMobile, isTablet, isPc } = useResponsive();

  return (
    <div style={{
      fontSize: fluidFont(16),      // 16px ~ 18px
      padding: fluidSpacing(16),    // 16px ~ 21px
    }}>
      {isMobile && <MobileView />}
      {isTablet && <TabletView />}
      {isPc && <PcView />}
    </div>
  );
};
```

## 설정 파일

`figma-responsive.config.json`:

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
  }
}
```

## 환경 변수

| 변수 | 필수 | 용도 |
|------|------|------|
| `GEMINI_API_KEY` | 선택 | 디자인 비교 기능 |

> Figma MCP 서버 사용으로 별도 Figma API 토큰 설정 불필요

## 지원 플랫폼

| 플랫폼 | 감지 조건 |
|--------|----------|
| React Native | `react-native` 있고 `expo` 없음 |
| Expo Mobile | `expo` 있고 `react-dom` 없음 |
| Expo Universal | `expo` + `react-dom` |
| Next.js | `next` |
| React Web | `react-dom` (next 제외) |

## 폴더 구조

```
figma-responsive-skill/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── figma-convert.md
├── references/
│   ├── responsive-utils-rn.md
│   ├── responsive-utils-web.md
│   ├── gemini-compare.md
│   └── figma-mapping.md
├── SKILL.md
└── README.md
```

## 요구사항

- Figma MCP 서버 연결
- Claude Code

## 라이센스

MIT
