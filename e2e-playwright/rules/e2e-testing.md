---
paths: "**/e2e/**"
---

# E2E 테스트 규칙 (Playwright + MUI)

## 폴더 전략

도메인 > 시나리오 구조를 권장한다. 역할 기반 접근 제어가 있는 프로젝트는 역할별 폴더를 상위에 둔다:

```
e2e/
├── fixtures/                    # 공통 fixture, 헬퍼
│   ├── auth.fixture.ts          # 로그인 fixture (역할별 분리 권장)
│   └── common.fixture.ts        # MUI 셀렉터 헬퍼 (DataGrid, Dialog, Select)
├── helpers/
│   ├── test-data.ts             # 테스트 데이터 생성 함수
│   └── cleanup.ts               # 테스트 데이터 정리 유틸
├── {도메인}/                     # 예: projects/, users/, orders/
│   ├── create.spec.ts
│   ├── edit.spec.ts
│   └── list-filter.spec.ts
└── access-control/              # 권한 경계 테스트 (횡단)
```

## 테스트 작성 규칙

### 1. 로그인 fixture 사용 (로그인 직접 작성 금지)

```typescript
// O - fixture import로 역할/계정 선택
import { adminTest as test, expect } from '../fixtures/auth.fixture';

// X - 각 테스트에서 로그인 코드 직접 작성
```

### 2. MUI 셀렉터 규칙

MUI 컴포넌트는 일반 셀렉터가 안 먹는 경우가 많다:

- **Select (드롭다운)**: `getByRole('combobox')` → `getByRole('listbox')` → 옵션 클릭
  - 주의: MUI Select의 listbox는 **dialog 밖 body에 렌더링**됨 → `dialog.getByRole('listbox')` (X) / `page.getByRole('listbox')` (O)
- **비밀번호 필드**: `getByPlaceholder()` 사용 (label이 아이콘 버튼에도 매칭됨)
- **페이지 제목**: `getByRole('heading')` 사용 (사이드바에 같은 텍스트 존재)
  - 주의: MUI Typography(`<p>` 태그)는 heading role이 없음 → `getByText('제목').first()` 사용
- **테이블 셀**: `getByRole('gridcell', { name: '텍스트' })`
- **텍스트가 여러 곳에 있으면**: `.first()` 또는 더 구체적인 role 사용
- `common.fixture.ts`의 헬퍼 함수 적극 활용

### 3. 대기 전략 — 각 단계마다 대기 포인트 필수

Playwright는 매우 빠르므로 **모든 단계 전환 시 대기**해야 한다. 빠르게 통과하면 의심하기.

```typescript
// [1] 페이지 이동 → networkidle 대기
await navigateTo(page, '/projects');              // 내부에서 waitUntil: 'networkidle'

// [2] DataGrid 렌더링 → 테이블 + 로딩 완료 대기
await waitForDataGrid(page);

// [3] 버튼 클릭 → Dialog/결과 나타날 때까지 대기
await page.getByRole('button', { name: '새 항목' }).click();
const dialog = await waitForDialog(page);         // dialog visible 대기
await expect(dialog.getByRole('textbox').first()).toBeVisible(); // 내부 폼 렌더링 대기

// [4] Select 드롭다운 → 옵션 로드 대기
await dialog.getByRole('combobox').first().click();
const listbox = page.getByRole('listbox');        // dialog 밖에서 찾기!
await expect(listbox).toBeVisible();
await expect(listbox.getByRole('option').first()).toBeVisible(); // 옵션 실제 로드 확인

// [5] 폼 입력 → 값이 실제로 들어갔는지 검증
await input.fill('텍스트');
await expect(input).toHaveValue('텍스트');

// [6] 등록/수정 버튼 → Dialog 닫힘 + 네트워크 완료 대기
await dialog.getByRole('button', { name: '등록' }).click();
await waitForDialogClose(page);                   // dialog hidden 대기
await page.waitForLoadState('networkidle');        // 목록 갱신 API 완료

// [7] 결과 확인 → gridcell로 정확히 검증 + 행 수 비교
await expect(page.getByRole('gridcell', { name: '항목명' })).toBeVisible({ timeout: 10000 });
const rowsAfter = await getRowCount(page);
expect(rowsAfter).toBeGreaterThan(rowsBefore);
```

### 4. 테스트 데이터

- `helpers/test-data.ts`의 생성 함수 사용
- 데이터 이름은 `E2E`로 시작 → cleanup 시 패턴 매칭으로 삭제 가능
- 시드 데이터 ID는 `test-data.ts`의 상수로 관리

### 5. 컨텍스트 확보 순서 (프론트 + 백엔드 같이 읽기)

테스트 작성 전 **프론트 코드와 백엔드(API/Server Action)를 반드시 함께 읽는다**:

1. **프론트 코드** (페이지 컴포넌트) → UI 구조, 셀렉터, 표시 텍스트 파악
2. **백엔드** (API Route / Server Action) → 어떤 테이블/컬럼 사용하는지, 데이터 구조 파악
3. 위 두 개로 부족하면 → DB 직접 조회 또는 사용자에게 확인

프론트 코드만 보면 "어떤 데이터를 넣어야 페이지가 정상 동작하는지" 판단이 어렵다. 백엔드의 쿼리를 보면 필요한 데이터 구조를 알 수 있다.

### 6. 시드 데이터 보호

테스트용 시드 계정(로그인, 기본 데이터)은 **READ ONLY**로 취급한다.

**E2E 테스트에서 절대 하지 않는 것:**
- 시드 계정 비밀번호 변경
- 시드 계정 삭제
- 시드 계정 역할(role) 변경
- 시드 계정 비활성화

위 작업이 필요한 경우 **반드시 사용자에게 컨펌**을 받고 진행한다. 시드 계정이 변경되면 global-setup의 로그인 체크부터 이후 전체 테스트가 연쇄 실패한다.

### 7. 에러 스낵바 검증 (거짓 통과 방지)

테스트가 "통과"해도 실제로는 서버 에러가 발생했을 수 있다. 저장/등록 후 **에러 스낵바가 없는지** 반드시 확인한다:

```typescript
// [패턴 1] 저장/등록 후 에러 스낵바 부재 확인
await dialog.getByRole('button', { name: '등록' }).click();
await waitForDialogClose(page);
await expect(
  page.locator('.MuiAlert-root').filter({ hasText: /오류|실패|error/i })
).toBeHidden({ timeout: 3000 });

// [패턴 2] 조건부 스킵 전 에러 상태 구분
// "데이터가 없어서 스킵"하기 전에, 에러 때문인지 확인
const errorAlert = page.locator('.MuiAlert-root').filter({ hasText: /오류|실패|error/i });
if (await errorAlert.isVisible().catch(() => false)) {
  throw new Error('페이지 로드 중 에러 발생: ' + await errorAlert.textContent());
}
// 에러가 아니면 → 정상적으로 데이터 없음 → 스킵 가능
```

**핵심**: "데이터가 없다"와 "서버 에러로 데이터를 못 가져왔다"는 다르다. 에러 스낵바 체크 없이 스킵하면 거짓 통과(false positive)가 된다.

### 8. 새 테스트 추가 시 체크리스트

1. 도메인 폴더 아래 `*.spec.ts` 생성
2. 로그인 fixture import
3. `common.fixture.ts` 헬퍼 활용
4. 테스트 데이터는 `helpers/test-data.ts`에서 생성
5. 저장/등록 후 **에러 스낵바 검증 추가** (섹션 7 참고 — 거짓 통과 방지)
6. 실행 확인: `npx playwright test e2e/{도메인}/{파일}.spec.ts`

## Global Setup (테스트 전 자동 검증)

`e2e/global-setup.ts`에서 테스트 실행 전 다음을 자동 체크하는 것을 권장한다:

1. **서버 상태**: dev 서버가 떠있는지, 500 에러 안 나는지
2. **로그인 검증**: 시드 계정으로 로그인이 정상 동작하는지

하나라도 실패하면 **테스트를 시작하지 않고 즉시 중단** + 원인 안내.

무한루프 위험 없음 — 모든 동작에 timeout이 걸려있다:
- 테스트 전체: 30초 (`playwright.config.ts → timeout`)
- 개별 액션(click, fill 등): 30초 (기본값)
- expect 검증: 5초 (기본값)

## headless 모드

- 기본적으로 **headless: true**로 실행 (브라우저 안 보임)
- 명시적으로 "headed로 해줘" 또는 "브라우저 보여줘" 요청 시에만 `--headed` 사용
- playwright.config.ts의 `headless` 설정은 `true` 유지

## 실행 방법

```bash
npx playwright test                          # 전체
npx playwright test e2e/{도메인}/            # 도메인별
npx playwright test e2e/access-control/      # 권한 테스트
npx playwright test --headed                 # 브라우저 보면서
npx playwright test --last-failed            # 직전 실패한 것만 재실행
```

### 실패 테스트 디버깅 워크플로우 (기본 워크플로우 — 사용자가 별도 요청하지 않으면 이 흐름으로 진행)

```
테스트 실행 → 실패 발생
    ↓
실패한 것만 모아서 확인 (--last-failed)
    ↓
분류: E2E 문제 vs 로직 문제
    ↓
┌─ E2E 문제 → 고치고 → 그 테스트만 다시 실행 → 통과하면 다음으로
│
└─ 로직 문제 → skip 처리하고 일단 빼놓기
    ↓
반복 (E2E 문제가 다 해결될 때까지)
    ↓
최종: 로직 문제로 skip된 테스트 목록만 사용자에게 보고
```

1. **실패한 것만 실행**: `--last-failed` 또는 개별 파일 지정
2. **원인 분류**:
   - **E2E 테스트 문제** (셀렉터/대기/타이밍) → 테스트 코드 수정 후 해당 테스트만 재실행
   - **로직 문제** (실제 기능 버그) → `test.skip()` 처리하고 목록에 추가
3. **반복**: E2E 문제가 모두 해결될 때까지 2번 반복
4. **최종 보고**: 로직 문제로 skip된 테스트 목록을 사용자에게 보고 (어떤 테스트에서 어떤 문제인지 정리)
5. 로직 수정은 사용자가 확인 후 한꺼번에 진행
6. **보고서 작성**: 테스트 결과를 `docs/e2e-reports/`에 기록 (`.claude/rules/e2e-report.md` 규칙 참고)

디버깅 시 trace/video/network 로그 분석에 시간 쓰지 않는다. 에러 메시지 + 스크린샷으로 우선 판단하고, 그래도 안 되면 사용자에게 확인.

**마지막에 전체 재실행 하지 않는다.** 통과한 테스트는 다시 실행하지 않는다. 깔때기 방식으로 실패한 것만 좁혀나간다.

## 테스트 실행 규칙

- **Playwright 테스트 실행(`npx playwright test`)은 반드시 메인 에이전트가 직접 수행**한다
- 서브에이전트(Task), 팀즈(TeamCreate) 등 위임된 에이전트에서 `npx playwright test`를 실행하지 않는다
- 서브에이전트/팀즈는 **테스트 코드 작성까지만** 담당하고, 실행과 디버깅은 메인 에이전트가 한다
- 단, 사용자가 명시적으로 병렬 실행을 요청하면 서브에이전트/팀즈에서도 실행 가능
- 이유: Playwright는 localhost 브라우저를 띄우므로 동시 실행 시 포트 충돌/세션 꼬임 발생

## 패턴 학습

- **테스트 작성 전**: 메모리의 `e2e-patterns.md`가 있다면 읽고, 기존 오류 패턴(MUI 셀렉터, Zustand hydration, Quill 에디터 등)을 숙지한다.
- **새 패턴 발견 시**: 기존에 없던 새로운 실패 패턴을 발견하면 `e2e-patterns.md`에 추가한다. 이미 있는 패턴으로 실패한 경우, 단순 오타, 일회성 문제는 추가하지 않는다.

## 트러블슈팅

- **패키지 추가 후 500 에러 (ENOENT vendor-chunks)**: `.next` 캐시가 깨진 것 → `rm -rf .next` 후 dev 서버 재시작
- **테스트가 2~3초 만에 통과**: 로딩 전에 넘어간 가능성 → `waitForDataGrid()`, `toHaveValue()`, 행 수 비교 추가
- **strict mode violation (N개 매칭)**: 셀렉터가 너무 넓음 → `getByRole()`, `.first()`, 또는 부모 스코프 좁히기

## 참고 파일

프로젝트에 맞게 아래 파일들을 구성한다:

- `playwright.config.ts` - Playwright 설정 (headless, video, trace 등)
- `e2e/fixtures/auth.fixture.ts` - 로그인 fixture (계정 정보)
- `e2e/fixtures/common.fixture.ts` - MUI 공통 헬퍼 함수 모음
- `e2e/helpers/test-data.ts` - 테스트 데이터 생성 함수 + 시드 데이터 상수
- `e2e/helpers/cleanup.ts` - 테스트 데이터 정리
- `e2e/global-setup.ts` - 테스트 전 서버/로그인 자동 검증
