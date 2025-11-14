---
description: Smart cleanup for deployment - removes unused backups, temp files, and packages
---

# Project Cleaner

배포 전 프로젝트를 정리합니다. 백업 파일, 임시 파일, 사용하지 않는 패키지를 스마트하게 탐지하고 제거합니다.

## Steps to follow:

### 1. 백업 및 임시 파일 탐지

다음 패턴의 파일들을 프로젝트 전체에서 찾으세요:

**백업 파일:**
- `*.bak`
- `*.backup`
- `*.old`
- `*~` (vim 백업)
- `*.swp`, `*.swo` (vim swap)

**OS 임시 파일:**
- `.DS_Store` (macOS)
- `Thumbs.db`, `desktop.ini` (Windows)

**개발 임시 파일:**
- `*.tmp`
- `*.temp`
- `*.log` (선택적 - 사용자에게 물어보기)

**제외할 폴더:**
- `node_modules/`
- `.git/`
- `dist/`, `build/`, `out/`
- `.next/`, `.nuxt/`
- `coverage/`

Glob 또는 Grep 도구를 사용하여 파일 목록을 수집하세요.

### 2. 의존성 분석 (핵심 로직)

찾은 각 백업/임시 파일에 대해 다음을 수행:

#### A. 파일 참조 검색

각 백업 파일이 **어디서 import/require 되는지** Grep으로 검색:

**검색 패턴 (JavaScript/TypeScript):**
```regex
import.*from.*['"].*파일명.*['"]
require\(['"].*파일명.*['"]\)
```

**검색 패턴 (Python):**
```regex
import.*파일명
from.*파일명.*import
```

**검색 패턴 (일반):**
- 파일명을 그대로 검색 (확장자 포함)

**예시:**
- `utils.js.bak` 찾았다면
- 프로젝트 전체에서 `utils.js.bak`를 검색
- import 또는 require 하는 파일이 있는지 확인

#### B. 참조 파일 분류

검색 결과를 분석하여:

1. **실제 코드에서 참조** (`.bak`/`.old` 없는 일반 파일에서 import)
   - → **삭제 불가** (경고 표시)
   - 예: `main.js`가 `api.js.bak`를 import

2. **백업 파일끼리만 참조** (`.bak` → `.bak`)
   - → **삭제 가능** (미사용 그룹)
   - 예: `a.js.bak` ← `b.js.bak` ← `c.js.bak` (순환)

3. **아무도 참조 안 함**
   - → **삭제 가능** (안전)

#### C. 그룹화

백업 파일끼리만 참조하는 경우 그룹으로 묶어서 표시:
```
미사용 백업 파일 그룹:
  - old/utils.js.bak
  - old/api.js.bak
  - old/helpers.js.bak
  (서로만 참조하고 실제 코드와 무관)
```

### 3. 사용하지 않는 패키지 분석

`package.json` 파일이 있는지 확인:

#### A. package.json 읽기
- `dependencies`와 `devDependencies` 목록 추출

#### B. 각 패키지 사용 여부 검색

각 패키지에 대해 Grep으로 검색:

**검색 패턴:**
```regex
import.*from.*['"]패키지명['"]
require\(['"]패키지명['"]\)
```

**주의사항:**
- `@types/` 패키지는 TypeScript에서 자동 사용 (스킵)
- `eslint-`, `prettier-` 등 설정 패키지는 config 파일에서 사용 확인
- peer dependencies는 체크하지 않음

#### C. 미사용 패키지 목록 생성

실제 코드에서 import/require 되지 않는 패키지를 리스트업

**선택적:** `depcheck` 도구 설치 및 실행
```bash
npx depcheck
```

### 4. 삭제 목록 표시

사용자에게 한국어로 보기 좋게 정리된 목록을 보여주세요:

```markdown
# 🗑️ 프로젝트 정리 결과

## ✅ 안전하게 삭제 가능한 파일

### 백업 파일 (12개)
- src/utils.js.bak (어디서도 사용 안 됨)
- src/api/old.js~ (어디서도 사용 안 됨)
- components/Button.jsx.old (어디서도 사용 안 됨)
...

### 미사용 백업 파일 그룹 (3개 파일)
- old/legacy-api.js.bak
- old/legacy-utils.js.bak
- old/legacy-helpers.js.bak
(서로만 참조, 실제 코드와 무관)

### OS 임시 파일 (5개)
- .DS_Store
- src/.DS_Store
- public/Thumbs.db
...

### 개발 임시 파일 (3개)
- debug.log
- test.tmp
- .swp
...

## 📦 사용하지 않는 패키지

### npm 패키지 (4개)
- lodash (코드에서 import 없음)
- moment (코드에서 import 없음)
- axios (코드에서 import 없음)
- chalk (코드에서 import 없음)

예상 절약 용량: ~2.3MB (파일) + ~15MB (패키지)

---

## ⚠️ 주의 필요

### 여전히 사용 중인 백업 파일
- config/database.js.bak (src/main.js에서 참조 중!)
  → 삭제하면 안 됩니다. 실제 코드를 먼저 수정하세요.

---

계속 진행하시겠습니까?
```

### 5. 사용자 확인

다음 옵션을 제공:
1. **모두 삭제** - 안전한 항목 전부 삭제
2. **파일만 삭제** - 백업/임시 파일만 삭제 (패키지 유지)
3. **패키지만 제거** - npm 패키지만 제거
4. **취소** - 아무것도 안 함

사용자의 선택을 기다리세요.

### 6. 삭제 실행

사용자가 승인하면:

#### A. 파일 삭제
```bash
rm -f [파일 목록]
```

각 파일을 삭제하면서 진행 상황 표시:
```
🗑️ 삭제 중...
✓ src/utils.js.bak 삭제됨
✓ .DS_Store 삭제됨
...
```

#### B. 패키지 제거
```bash
npm uninstall [패키지1] [패키지2] ...
```

#### C. 최종 정리 (선택적)
```bash
npm prune
```

### 7. 완료 메시지

작업 완료 후 요약:

```markdown
✅ 프로젝트 정리 완료!

🗑️ 삭제된 항목:
   - 백업 파일: 12개
   - 임시 파일: 8개
   - npm 패키지: 4개

💾 절약된 용량: ~17.3MB

📦 다음 단계:
   1. git status로 변경사항 확인
   2. 프로젝트가 정상 작동하는지 테스트
   3. 문제없으면 커밋

깔끔하게 정리되었습니다! 🎉
```

## Important Notes:

### 안전 장치
- **절대 삭제하면 안 되는 것:**
  - `node_modules/` 내부 파일 (전체 폴더는 괜찮음)
  - `.git/` 관련 파일
  - 실제 코드에서 참조 중인 파일
  - `package.json`, `package-lock.json`

### 검색 최적화
- Grep 도구로 빠르게 검색
- 파일 확장자별로 적절한 패턴 사용
- 대소문자 구분 주의 (운영체제별)

### 사용자 경험
- 삭제 전 **반드시** 목록을 보여주고 확인
- 위험한 작업은 경고 표시
- 한국어로 친절하게 안내
- 각 단계마다 진행 상황 표시

### 에러 처리
- 파일 삭제 실패 시 계속 진행하고 마지막에 실패 목록 표시
- npm 패키지 제거 실패 시 원인 설명
- 권한 문제 등 예상 가능한 에러 안내
