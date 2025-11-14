---
description: Automatically generate and run tests with detailed reports
---

# Test Generator

테스트 코드를 자동으로 생성하고 실행한 뒤, 상세한 결과 리포트를 제공합니다.

## Steps to follow:

### 1. 테스트 대상 파일 선택

사용자에게 테스트할 파일을 물어보세요:
- IDE에서 현재 열려있는 파일이 있다면 제안
- 또는 파일 경로를 직접 입력받기
- 예: `src/utils/calculator.js`, `components/Button.tsx`

**파일이 선택되면 Read 도구로 파일 내용을 읽으세요.**

### 2. 테스트 유형 선택

사용자에게 다음 중 선택하도록 안내:

#### A. 단위 테스트 (Unit Test)
- 개별 함수, 메서드, 유틸리티 테스트
- 외부 의존성 없이 독립적으로 동작
- 가장 빠르고 간단한 테스트

#### B. 통합 테스트 (Integration Test)
- 여러 모듈/컴포넌트 간 상호작용 테스트
- API + Database, Service + Repository 등
- 실제 의존성과 함께 테스트

#### C. E2E 테스트 (End-to-End)
- 실제 사용자 시나리오 테스트
- 브라우저 자동화, 전체 플로우 검증
- 가장 현실적이지만 느림

사용자의 선택을 기록하세요.

### 3. 테스트 프레임워크 감지

프로젝트의 `package.json`을 읽고 설치된 테스트 도구를 확인:

**유닛/통합 테스트 프레임워크:**
- `jest`: Jest
- `vitest`: Vitest
- `mocha` + `chai`: Mocha
- `@testing-library/react`: React Testing Library
- `@testing-library/vue`: Vue Testing Library

**E2E 테스트 프레임워크:**
- `cypress`: Cypress
- `@playwright/test`: Playwright
- `puppeteer`: Puppeteer

**프레임워크가 없는 경우:**
- 사용자에게 추천 (Jest/Vitest for unit, Playwright for E2E)
- 설치 여부 물어보기
- 설치한다면: `npm install -D [프레임워크]`

### 4. 코드 분석

읽은 파일 내용을 분석하여 다음을 추출:

#### JavaScript/TypeScript 파일:
- **함수 목록**: export된 함수들
- **클래스 및 메서드**: class 정의와 메서드들
- **입력 파라미터**: 각 함수의 매개변수
- **반환 타입**: TypeScript의 경우 타입 정보
- **의존성**: import 문

**예시 분석 결과:**
```
파일: src/utils/math.js
함수:
  1. add(a, b) - 두 수를 더함
  2. subtract(a, b) - 두 수를 뺌
  3. multiply(a, b) - 두 수를 곱함
  4. divide(a, b) - 나눗셈 (0으로 나누기 체크 필요)
```

#### React/Vue 컴포넌트:
- **컴포넌트 이름**
- **Props**: 받는 props와 타입
- **이벤트 핸들러**: onClick, onChange 등
- **상태**: useState, data() 등

#### API/백엔드 코드:
- **라우트/엔드포인트**: GET, POST 등
- **요청/응답 스키마**
- **에러 핸들링**

### 5. 테스트 코드 자동 생성

선택한 테스트 유형과 프레임워크에 맞는 테스트 코드를 생성:

---

#### A. 단위 테스트 생성 예시

**대상 파일: `src/utils/math.js`**
```javascript
export function add(a, b) {
  return a + b;
}

export function divide(a, b) {
  if (b === 0) throw new Error('Division by zero');
  return a / b;
}
```

**생성할 테스트: `src/utils/math.test.js` (Jest/Vitest)**
```javascript
import { describe, test, expect } from '@jest/globals';
import { add, divide } from './math';

describe('Math Utils', () => {
  describe('add()', () => {
    test('두 양수를 더한다', () => {
      expect(add(2, 3)).toBe(5);
    });

    test('음수를 처리한다', () => {
      expect(add(-5, 3)).toBe(-2);
    });

    test('0을 처리한다', () => {
      expect(add(0, 0)).toBe(0);
    });

    test('소수점을 처리한다', () => {
      expect(add(0.1, 0.2)).toBeCloseTo(0.3);
    });

    test('매우 큰 수를 처리한다', () => {
      expect(add(1e10, 1e10)).toBe(2e10);
    });
  });

  describe('divide()', () => {
    test('정상적인 나눗셈을 수행한다', () => {
      expect(divide(10, 2)).toBe(5);
    });

    test('소수 결과를 반환한다', () => {
      expect(divide(7, 2)).toBe(3.5);
    });

    test('0으로 나누면 에러를 던진다', () => {
      expect(() => divide(10, 0)).toThrow('Division by zero');
    });

    test('음수 나눗셈을 처리한다', () => {
      expect(divide(-10, 2)).toBe(-5);
    });

    test('0을 나누면 0을 반환한다', () => {
      expect(divide(0, 5)).toBe(0);
    });
  });
});
```

---

#### B. 통합 테스트 생성 예시

**대상: API + Database 통합**
```javascript
// src/services/userService.integration.test.js
import { describe, test, expect, beforeAll, afterAll } from '@jest/globals';
import { UserService } from './userService';
import { setupTestDatabase, cleanupTestDatabase } from '../test-utils/db';

describe('UserService Integration Tests', () => {
  let userService;
  let testDb;

  beforeAll(async () => {
    testDb = await setupTestDatabase();
    userService = new UserService(testDb);
  });

  afterAll(async () => {
    await cleanupTestDatabase(testDb);
  });

  describe('사용자 생성 및 조회', () => {
    test('새 사용자를 생성하고 조회할 수 있다', async () => {
      const userData = {
        name: '홍길동',
        email: 'hong@test.com'
      };

      const created = await userService.createUser(userData);
      expect(created).toHaveProperty('id');
      expect(created.name).toBe(userData.name);

      const found = await userService.findById(created.id);
      expect(found).toEqual(created);
    });

    test('중복 이메일은 거부된다', async () => {
      await userService.createUser({ name: 'A', email: 'dup@test.com' });

      await expect(
        userService.createUser({ name: 'B', email: 'dup@test.com' })
      ).rejects.toThrow('Email already exists');
    });
  });

  describe('사용자 업데이트', () => {
    test('사용자 정보를 수정할 수 있다', async () => {
      const user = await userService.createUser({
        name: '김철수',
        email: 'kim@test.com'
      });

      const updated = await userService.updateUser(user.id, {
        name: '김영희'
      });

      expect(updated.name).toBe('김영희');
      expect(updated.email).toBe('kim@test.com');
    });
  });
});
```

---

#### C. E2E 테스트 생성 예시 (Playwright)

**대상: 로그인 플로우**
```javascript
// e2e/login.spec.js
import { test, expect } from '@playwright/test';

test.describe('로그인 플로우', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('성공적인 로그인', async ({ page }) => {
    // 로그인 페이지로 이동
    await page.click('text=로그인');
    await expect(page).toHaveURL(/.*login/);

    // 폼 작성
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');

    // 제출
    await page.click('button[type="submit"]');

    // 대시보드로 리다이렉트 확인
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('h1')).toContainText('환영합니다');
  });

  test('잘못된 비밀번호 에러 처리', async ({ page }) => {
    await page.click('text=로그인');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // 에러 메시지 확인
    await expect(page.locator('.error-message'))
      .toContainText('비밀번호가 올바르지 않습니다');
  });

  test('이메일 유효성 검사', async ({ page }) => {
    await page.click('text=로그인');
    await page.fill('input[name="email"]', 'invalid-email');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // HTML5 validation 또는 커스텀 에러
    const emailInput = page.locator('input[name="email"]');
    await expect(emailInput).toHaveAttribute('aria-invalid', 'true');
  });
});
```

---

#### React 컴포넌트 테스트 예시

```javascript
// components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, test, expect, vi } from 'vitest';
import Button from './Button';

describe('Button 컴포넌트', () => {
  test('텍스트를 올바르게 렌더링한다', () => {
    render(<Button>클릭</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('클릭');
  });

  test('클릭 이벤트를 처리한다', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>클릭</Button>);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('disabled 상태를 처리한다', () => {
    render(<Button disabled>클릭</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  test('variant prop에 따라 올바른 클래스를 적용한다', () => {
    const { rerender } = render(<Button variant="primary">클릭</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn-primary');

    rerender(<Button variant="secondary">클릭</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn-secondary');
  });
});
```

---

### 6. 테스트 파일 위치 결정

프로젝트 구조에 맞게 테스트 파일 저장 위치 결정:

**옵션 1: 같은 폴더** (권장)
```
src/utils/
  ├── math.js
  └── math.test.js
```

**옵션 2: __tests__ 폴더**
```
src/utils/
  ├── math.js
  └── __tests__/
      └── math.test.js
```

**옵션 3: 별도 tests 폴더**
```
src/utils/math.js
tests/unit/utils/math.test.js
```

**E2E 테스트:**
```
e2e/
  ├── login.spec.js
  └── signup.spec.js
```

사용자에게 선호하는 위치를 물어보거나, 기존 프로젝트 패턴을 따르세요.

### 7. 테스트 파일 생성

Write 도구를 사용하여 생성된 테스트 코드를 파일로 저장:
- 적절한 경로에 `.test.js`, `.spec.js` 등의 확장자로 저장
- 파일 생성 완료를 사용자에게 알리기

### 8. 테스트 실행

생성한 테스트를 자동으로 실행:

#### A. 테스트 명령어 결정

`package.json`의 scripts 확인:
```json
{
  "scripts": {
    "test": "jest",
    "test:unit": "vitest run",
    "test:e2e": "playwright test"
  }
}
```

#### B. 적절한 명령어 실행

**단위/통합 테스트:**
```bash
npm test -- [테스트파일경로]
# 또는
npx jest src/utils/math.test.js
# 또는
npx vitest run src/utils/math.test.js
```

**E2E 테스트:**
```bash
npm run test:e2e
# 또는
npx playwright test e2e/login.spec.js
```

**커버리지 포함:**
```bash
npm test -- --coverage
```

Bash 도구를 사용하여 테스트 실행하고 결과를 캡처하세요.

### 9. 결과 상세 리포트 생성

테스트 실행 결과를 분석하여 사용자에게 상세한 리포트를 제공:

---

#### 리포트 형식:

```markdown
# 🧪 테스트 결과 리포트

## 📋 테스트 정보

- **대상 파일**: src/utils/math.js
- **테스트 파일**: src/utils/math.test.js
- **테스트 유형**: 단위 테스트 (Unit Test)
- **프레임워크**: Jest 29.5.0
- **실행 시간**: 2024-11-14 14:30:25

---

## 📊 전체 결과

✅ **통과**: 9개
❌ **실패**: 1개
⏭️  **스킵**: 0개

**성공률**: 90% (9/10)

---

## 🔍 상세 테스트 케이스

### ✅ add() 함수 (5/5 통과)

#### [PASS] 두 양수를 더한다
- **입력**: add(2, 3)
- **예상**: 5
- **결과**: 5 ✓
- **테스트 항목**: 기본 덧셈 연산

#### [PASS] 음수를 처리한다
- **입력**: add(-5, 3)
- **예상**: -2
- **결과**: -2 ✓
- **테스트 항목**: 음수 처리

#### [PASS] 0을 처리한다
- **입력**: add(0, 0)
- **예상**: 0
- **결과**: 0 ✓
- **테스트 항목**: 경계값 (0)

#### [PASS] 소수점을 처리한다
- **입력**: add(0.1, 0.2)
- **예상**: ~0.3 (부동소수점 오차 허용)
- **결과**: 0.30000000000000004 ✓
- **테스트 항목**: 부동소수점 연산

#### [PASS] 매우 큰 수를 처리한다
- **입력**: add(1e10, 1e10)
- **예상**: 2e10
- **결과**: 20000000000 ✓
- **테스트 항목**: 큰 수 처리

---

### ⚠️ divide() 함수 (4/5 통과, 1개 실패)

#### [PASS] 정상적인 나눗셈을 수행한다
- **입력**: divide(10, 2)
- **예상**: 5
- **결과**: 5 ✓
- **테스트 항목**: 기본 나눗셈

#### [PASS] 소수 결과를 반환한다
- **입력**: divide(7, 2)
- **예상**: 3.5
- **결과**: 3.5 ✓
- **테스트 항목**: 소수 결과

#### [FAIL] 0으로 나누면 에러를 던진다 ❌
- **입력**: divide(10, 0)
- **예상**: Error('Division by zero')
- **실제 결과**: Infinity
- **테스트 항목**: 에러 핸들링 (0으로 나누기)
- **실패 원인**: 함수가 에러를 던지지 않고 Infinity를 반환함

**스택 트레이스:**
```
Error: Expected function to throw an error, but it returned Infinity
  at Object.<anonymous> (src/utils/math.test.js:32:7)
```

**수정 제안:**
```javascript
export function divide(a, b) {
  if (b === 0) {
    throw new Error('Division by zero');
  }
  return a / b;
}
```

#### [PASS] 음수 나눗셈을 처리한다
- **입력**: divide(-10, 2)
- **예상**: -5
- **결과**: -5 ✓
- **테스트 항목**: 음수 처리

#### [PASS] 0을 나누면 0을 반환한다
- **입력**: divide(0, 5)
- **예상**: 0
- **결과**: 0 ✓
- **테스트 항목**: 0을 피제수로 사용

---

## 📈 커버리지 리포트

| 항목 | 비율 | 커버된 라인/전체 라인 |
|------|------|----------------------|
| **Statements** | 95% | 19/20 |
| **Branches** | 87.5% | 7/8 |
| **Functions** | 100% | 2/2 |
| **Lines** | 95% | 19/20 |

### 커버되지 않은 코드:

**라인 15**: `throw new Error('Division by zero')`
- 이 라인이 실행되지 않음 (테스트 실패와 연관)

---

## ✅ 테스트한 주요 시나리오

### 1. 정상 입력값 처리
- ✅ 양수 연산
- ✅ 기본 계산

### 2. 경계값 테스트
- ✅ 0 처리
- ✅ 음수 처리
- ✅ 매우 큰 수 (1e10)
- ✅ 소수점 (0.1, 0.2)

### 3. 에러 핸들링
- ❌ 0으로 나누기 (수정 필요!)

### 4. 특수 케이스
- ✅ 부동소수점 정밀도
- ✅ 음수 결과

---

## 💡 권장 사항

### 🔴 즉시 수정 필요

1. **divide() 함수의 0으로 나누기 처리**
   - 현재: Infinity 반환
   - 기대: Error 발생
   - 우선순위: 높음

### 🟡 개선 권장

1. **추가 테스트 케이스**
   - `add()`: NaN, null, undefined 입력 처리
   - `divide()`: Infinity 입력 처리
   - 타입 검증 (문자열 입력 등)

2. **성능 테스트**
   - 대량 연산 테스트 추가
   - 메모리 사용량 확인

3. **문서화**
   - JSDoc 주석 추가
   - 사용 예시 추가

---

## ⏱️ 성능 정보

- **총 실행 시간**: 1.234초
- **평균 테스트 시간**: 0.123초
- **가장 느린 테스트**: divide() 음수 나눗셈 (0.245초)

---

## 🎯 다음 단계

1. ❌ **실패한 테스트 수정**
   ```bash
   # divide 함수 수정 후 재실행:
   npm test src/utils/math.test.js
   ```

2. 📝 **추가 테스트 작성**
   - 엣지 케이스 커버리지 향상
   - 타입 검증 테스트 추가

3. 🚀 **CI/CD 통합**
   - GitHub Actions에 테스트 추가
   - PR 시 자동 테스트 실행

---

모든 테스트가 통과하도록 코드를 수정해주세요! 💪
```

---

### 10. 추가 기능 (선택적)

#### A. 자동 수정 제안
실패한 테스트에 대해 코드 수정 제안:
- 문제 원인 분석
- 수정 코드 예시
- 사용자가 원하면 자동 수정

#### B. 테스트 커버리지 개선
```
📊 커버리지 개선 제안:

현재: 87.5%
목표: 95%+

추가가 필요한 테스트:
1. validateEmail() - 특수문자 이메일 (@, +, . 포함)
2. parseJSON() - 잘못된 JSON 형식 처리
3. formatDate() - 타임존 처리
```

#### C. 스냅샷 테스트 (React/Vue)
```javascript
test('컴포넌트 렌더링 스냅샷', () => {
  const { container } = render(<Button>클릭</Button>);
  expect(container.firstChild).toMatchSnapshot();
});
```

## Important Notes:

### 테스트 작성 원칙
- **AAA 패턴**: Arrange (준비), Act (실행), Assert (검증)
- **한 테스트는 한 가지만**: 테스트당 하나의 검증 항목
- **명확한 테스트 이름**: 무엇을 테스트하는지 한국어로 명확히
- **독립성**: 테스트 간 의존성 없이 독립 실행 가능

### 커버리지 목표
- **Statements**: 80% 이상
- **Branches**: 75% 이상
- **Functions**: 100% (모든 함수 테스트)

### 사용자 경험
- 한국어로 친절하게 설명
- 실패 원인과 해결 방법 명확히 제시
- 시각적으로 보기 좋은 리포트 (이모지, 테이블 활용)
- 테스트 결과를 상세히 분석하여 제공

### 에러 처리
- 테스트 프레임워크 없으면 설치 가이드
- 테스트 실행 실패 시 원인 분석
- 권한 문제, 환경 문제 등 친절히 안내
