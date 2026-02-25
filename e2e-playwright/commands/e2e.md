---
description: E2E 테스트를 프런트+백엔드 코드 기반으로 작성하고 실행합니다
---

# E2E 테스트 작성

$ARGUMENTS

## 기본 전략

1. **프런트 + 백엔드 같이 읽기**: 반드시 해당 페이지의 프런트 코드와 백엔드(API Route / Server Action)를 **함께** 읽는다. 프런트에서 UI 구조/셀렉터를, 백엔드에서 필요한 데이터 구조를 파악한다.
2. **rules 참고**: `.claude/rules/e2e-testing.md`의 폴더 전략, MUI 셀렉터 규칙, 대기 전략을 따른다.
3. **로그인 fixture 사용**: `auth.fixture.ts`의 fixture를 import하여 로그인 코드를 직접 작성하지 않는다.
4. **MUI 헬퍼 활용**: `common.fixture.ts`의 `navigateTo`, `waitForDataGrid`, `selectOption` 등을 적극 활용한다.
5. **패턴 메모리 참조**: 테스트 작성 전 메모리의 `e2e-patterns.md`가 있다면 읽고, 기존 오류 패턴을 숙지한 상태에서 작성한다.

## 데이터 네이밍

테스트 데이터는 `helpers/test-data.ts`의 생성 함수를 사용하며, 아래 패턴을 따른다:

```
E2E_C_{도메인}_{timestamp}  -> 생성(Create) 테스트
E2E_U_{도메인}_{timestamp}  -> 수정(Update) 테스트
E2E_D_{도메인}_{timestamp}  -> 삭제(Delete) 테스트
```

cleanup 시 `E2E` 접두사로 테스트 데이터를 식별하여 정리한다. 프로젝트에 맞는 cleanup 방식(DB 직접 삭제, API 호출 등)을 `helpers/cleanup.ts`에 구현한다.

## 타겟 데이터 전략

- **생성 테스트**: 타겟 없음. 새로 만들고 검증.
- **수정/삭제/조회 테스트**: `beforeEach`에서 데이터 생성 -> 테스트에서 수정/삭제 -> `afterEach`에서 정리 (독립적 테스트 추천)
- **연결성이 중요한 작업** (예: 주문 -> 결제 -> 배송 연쇄): 타겟 데이터를 사용자에게 확인받고 진행

## 스크린샷

주요 데이터 시점에 스크린샷을 캡처한다:

| 시점 | 이유 |
|------|------|
| 데이터 등록 직후 | 등록 결과 확인 증거 |
| 데이터 수정 직후 | 변경 전/후 비교 |
| 목록에 데이터 표시될 때 | 실제 반영 확인 |
| 실패 시 (자동) | playwright.config.ts에 이미 설정됨 |

```typescript
await page.screenshot({ path: `screenshots/${testName}/after-create.png` });
```

## 파일 업로드

테스트용 파일은 `e2e/fixtures/files/`에 준비한다:
- `test-document.pdf` (PDF)
- `test-spreadsheet.xlsx` (엑셀)
- `test-image.png` (이미지)

```typescript
const filePath = path.resolve(__dirname, '../fixtures/files/test-document.pdf');
await page.setInputFiles('input[type="file"]', filePath);
```

## 디버깅 전략

오류 발생 시 **실제 코드(로직) 문제 vs E2E 테스트 문제**를 구분한다:
- **실제 코드 문제**: 사용자에게 컨펌 받고 코드 수정
- **E2E 테스트 문제**: 셀렉터/대기/타이밍 수정 후 재실행

로그/네트워크 모니터링은 오류 발생 시에만 추가한다.

## 실행 단계

1. 대상 페이지의 프런트 코드 + 백엔드(API/Server Action)를 함께 읽는다
2. 도메인 폴더 아래 `*.spec.ts` 생성
3. 로그인 fixture + common 헬퍼 import
4. 테스트 데이터는 `helpers/test-data.ts` 함수 사용
5. 각 단계마다 대기 포인트 추가 (7단계 대기 전략)
6. 저장/등록 후 **에러 스낵바 검증 필수** (거짓 통과 방지 — `rules/e2e-testing.md` 섹션 7 참고)
7. headless 모드로 실행: `npx playwright test e2e/{도메인}/{파일}.spec.ts`
8. 실패 시 디버깅 전략에 따라 원인 분석 후 수정 & 재실행
9. 테스트 완료 후 결과 보고서를 `docs/e2e-reports/`에 작성한다 (`.claude/rules/e2e-report.md` 규칙 참고)
