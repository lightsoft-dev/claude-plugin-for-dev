---
name: screen-doc-notion
description: "웹 앱 화면(관리자/어드민 페이지 등)을 분석해 스크린샷이 포함된 사용 안내 문서를 Notion에 작성한다. 화면 구조·필터·권한별 차이·드롭다운 값의 출처(하드코딩 vs 코드관리 메뉴)까지 코드로 확인해 정리하고, 사용자 시나리오와 화면 바로가기 링크를 포함한다. 사용 시점 - (1) '이 페이지 설명하는 문서 만들어줘', (2) '화면 안내/매뉴얼 노션에 작성', (3) '어드민 페이지 문서화', (4) 'screen-doc', (5) 특정 URL을 주며 기능 설명 문서를 요청할 때."
---

# 화면 안내 문서 → Notion

특정 화면(들)을 **코드로 분석 + 실제 캡처**해서, 처음 보는 사람도 이해할 수 있는 안내 문서를 Notion에 작성한다.

## 이 스킬이 만드는 문서의 필수 구성

아래 6개는 **반드시** 포함한다. 특히 ①②③은 이 스킬의 핵심 차별점이다.

1. **화면별 바로가기 링크** — 각 화면 섹션 제목 바로 아래에 실제 접속 URL(https)을 넣는다. 읽는 사람이 문서를 보다가 바로 그 화면으로 갈 수 있어야 한다.
2. **사용자 시나리오** — "이럴 때 이렇게 쓴다"를 단계로 서술. 기능 나열이 아니라 **실제 업무 흐름**으로 쓴다.
3. **드롭다운/옵션 값의 출처** — 각 선택 항목이 **하드코딩인지, DB 코드값인지, 별도 관리 메뉴에서 생성되는지** 밝힌다. 관리 메뉴가 있으면 그 경로까지 적는다.
4. 화면별 스크린샷 (Notion에 업로드)
5. 권한/역할별로 보이는 것이 다르면 그 차이를 표로
6. 알아두면 좋은 것 (헷갈리기 쉬운 동작, 알려진 이슈)

---

## 워크플로

### 1단계 — 대상 확정 및 URL 수집

사용자가 준 URL에서 시작한다. 같은 메뉴의 형제 화면(서브탭)도 함께 문서화할지 확인한다.

각 화면의 **접속 URL을 정확히 기록**해 둔다(피드백①). 나중에 문서 각 섹션 제목 아래에 넣는다.

```
상담      https://<host>/globalinsu/consult/info/main.do
상담입력   https://<host>/globalinsu/consult/db/self/main.do
```

### 2단계 — 코드 분석 (문서의 실체)

캡처만으로는 알 수 없는 것을 코드에서 확인한다. **추측하지 말고 근거를 찾는다.**

**(a) 화면 진입점 → 뷰 파일**
```bash
grep -rn "@RequestMapping\|@GetMapping" src/main/java --include=*.java | grep "<경로>"
```
컨트롤러가 반환하는 뷰 이름 → JSP/템플릿 파일을 찾는다. W/M(웹/모바일) 분기나 include 구조가 있는지 확인한다.

**(b) 필터·검색 항목**
JSP에서 `<select>`, `<input name=...>`을 훑어 검색 조건을 목록화한다.

**(c) 목록 컬럼 + 권한 분기**
```bash
grep -nE "<th|fn:contains\(|c:if" <뷰파일>
```
`fn:contains('P1,P7', 직급)` 같은 조건이 붙은 컬럼은 **권한별로 숨겨지는 항목**이다. 반드시 표로 정리한다 — "내 화면엔 그 컬럼이 없다"는 문의의 대부분이 이것이다.

**(d) 드롭다운 값의 출처 판별 (피드백③ — 중요)**

각 select의 옵션이 어디서 오는지 3가지로 분류한다.

| 코드 형태 | 판정 | 문서에 쓸 내용 |
| --- | --- | --- |
| `<option value="A">고정값</option>` 나열 | **하드코딩** | "코드에 고정. 변경하려면 개발 수정 필요" |
| `${tu:codeList('XXX_GROUP')}` / `${XXX_GROUP.items}` | **DB 코드값** | 해당 코드그룹을 관리하는 **화면 경로**까지 명시 |
| `${someList}` (컨트롤러가 넣어준 값) | **조회 결과** | 컨트롤러 추적 → 어떤 테이블/조건인지 |

DB 코드값이면 **관리 화면 경로를 반드시 찾아 적는다.** 사용자가 "이 목록에 항목을 추가하려면 어디로 가야 하나"를 알 수 있어야 한다.

```bash
# 코드그룹 → 관리화면 경로 매핑 (Spring/JSP 프로젝트 예)
grep -rn "XXX_GROUP" src/main/java --include=*.java | grep -i "codegroup\|enum"
# CodeGroup enum 의 마지막 필드가 path 면 → /codeManager/{path}/main.do 가 관리화면
```

DB가 붙어 있으면 실제 값도 확인해 문서에 예시로 넣으면 좋다.
```bash
mysql ... -e "SELECT CODE, CODE_NM FROM GI_CODE WHERE GROUP_CD='XXX_GROUP' AND DATA_STS='Y' ORDER BY CD_NO"
```

**(e) 저장/검증 로직**
등록·수정 화면이면 JS의 `fn_save()` 등에서 **검증 순서**를 읽어 그대로 문서화한다. 안내창 문구가 곧 실패 원인이므로 사용자에게 매우 유용하다.

### 3단계 — 캡처 환경 선택 ⚠️ 개인정보 주의

**운영/개발 서버의 실데이터 화면을 그대로 캡처해 문서에 넣지 않는다.** 목록 화면에는 대개 고객 이름·연락처가 그대로 보이며, 문서에 올리면 개인정보가 유출된다.

우선순위:
1. **로컬 환경 + 더미 데이터** (최선) — 운영과 같은 화면이면서 안전
2. 개발 서버 — 실데이터가 없거나 이미 더미인 경우만
3. 운영 — 원칙적으로 금지. 불가피하면 마스킹 후 사용

로컬을 쓸 때는 문서 상단에 **"더미 데이터"임을 명시**한다.

로컬에 계정이 없으면 만들어야 할 수 있다(권한 행까지 필요한 경우가 많음). 로그인 실패 시 응답 메시지·에러코드를 grep해 원인을 찾는다.

### 4단계 — 스크린샷 촬영 (aside 브라우저)

`aside` CLI를 쓴다. **주의점 3가지:**

- **openTab 으로 연 탭은 repl 세션이 끝나면 닫힌다.** 따라서 `openTab → 이동 → screenshot`을 **한 번의 repl 호출 안에서** 끝내야 한다.
- **screenshot 경로는 aside 세션 디렉터리로 제한**된다. 절대경로를 주면 "escapes the session directory" 에러. **상대 파일명**으로 저장한 뒤 회수한다.
- **요소 단위 screenshot은 미지원**("Invalid parameters"). `fullPage: true` 또는 viewport 전체를 쓴다. fullPage는 sticky 헤더 때문에 하단이 중복될 수 있으니, 깔끔한 컷이 필요하면 viewport(옵션 없이)로 찍는다.

```bash
aside repl "
const p = await openTab('<URL>');
await p.waitForLoadState('domcontentloaded'); await sleep(2500);
await p.screenshot({ path: 'shot_01.png', fullPage: true });   // 상대경로
// 화면 구조도 함께 뽑아두면 문서 작성이 정확해진다
const info = await p.evaluate(()=>({
  headers: [...document.querySelectorAll('table thead th')].map(t=>t.textContent.trim()),
  tabs: [...document.querySelectorAll('.nav-link')].map(a=>a.textContent.trim())
}));
console.log(JSON.stringify(info,null,2));
"
# 회수
cp ~/.aside/u/0/sessions/*/shot_*.png <작업폴더>/
```

로그인이 필요하면 **사용자에게 직접 로그인을 요청**한다(비밀번호를 대신 입력하지 않는다). 단, 로컬 테스트 계정처럼 사용자가 만들어준/합의된 계정은 직접 입력해도 된다.

**권한별 차이가 있으면 각 권한으로 로그인해 2장을 찍어 비교**한다. 문서의 설득력이 크게 올라간다.

### 5단계 — 문서 작성

`templates/doc-template.md` 구조를 따른다. 원칙:

- **기능 나열이 아니라 "왜/언제 쓰는지"부터** 쓴다.
- 화면을 "위에서 아래로 ①②③ 덩어리"로 나눠 읽는 법을 알려준다.
- 표를 적극 활용하되, 표 안에는 짧은 사실만 넣고 설명은 표 밖 문장으로.
- 헷갈리기 쉬운 동작은 인용(>)으로 강조한다. (예: "전체보기가 미배정을 제외한다")

### 6단계 — Notion 업로드

**이미지 업로드는 3단계**다.

```
1) notion-create-file-upload(filename)  → upload_url, upload_headers, file_upload_id 획득
2) curl -X POST "<upload_url>" -H "authorization: <upload_headers.authorization>" \
        -F "file=@<로컬파일>;type=image/png"
   → 응답의 markdown_source = file-upload://<id>
3) 문서 마크다운에 <image src="file-upload://<id>"></image> 로 삽입
```

업로드 URL은 **수 분 내 만료**되므로 발급 후 바로 올린다. 여러 장이면 create-file-upload를 병렬 호출한 뒤 curl로 순차 업로드하면 빠르다.

문서 작성은 `notion-update-page`의 `replace_content`(전체 교체) 또는 `insert_content`(추가)를 쓴다. 표는 Notion 마크다운 표 문법이 그대로 렌더링된다.

작성 후 **반드시 `notion-fetch`로 검증**한다 — 이미지가 S3 URL로 치환됐는지, 표가 `<table>`로 렌더링됐는지 확인.

마지막에 페이지 아이콘(이모지)을 지정하면 완성도가 올라간다.

---

## 문서 품질 체크리스트

작성 후 아래를 자문한다.

- [ ] 각 화면 섹션에 **접속 URL 링크**가 있는가
- [ ] **사용자 시나리오**가 업무 흐름으로 서술됐는가 (기능 나열 아님)
- [ ] 모든 드롭다운에 대해 **값의 출처**(하드코딩/코드관리/조회)를 밝혔는가, 관리 화면 경로를 적었는가
- [ ] 스크린샷에 **실제 개인정보가 없는가**
- [ ] 권한별 차이가 있다면 표 + 비교 캡처가 있는가
- [ ] 저장 실패 등 **자주 겪는 문제의 원인**을 적었는가
- [ ] 처음 보는 사람이 읽고 그 화면을 쓸 수 있는가

## 참고

- 프로젝트별 상세(코드그룹→관리화면 매핑 등)는 `references/` 참고
- 문서 뼈대는 `templates/doc-template.md`
