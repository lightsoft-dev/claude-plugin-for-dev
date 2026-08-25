# Spring MVC + JSP 프로젝트에서 화면 분석하기

레거시 Spring(JSP/MyBatis) 어드민 화면을 분석할 때의 구체적 방법. `globalinsu_admin` 기준으로 검증됐으나 유사 구조에 그대로 적용된다.

## 진입점 → 뷰 파일 찾기

```bash
# URL → 컨트롤러
grep -rn "@RequestMapping\|@PostMapping\|@GetMapping" src/main/java --include=*.java | grep "<경로 일부>"

# 컨트롤러가 new ModelAndView("/a/b/c") 를 반환 → src/main/webapp/WEB-INF/jsp/a/b/c.jsp
```

**주의: 뷰가 다시 include로 갈리는 경우가 많다.**
```jsp
<c:choose>
  <c:when test="${sessionScope.IS_PHONE}">
    <%@ include file="...MainM.jsp" %>   <!-- 모바일 -->
  </c:when>
  <c:otherwise>
    <%@ include file="...MainW.jsp" %>   <!-- 웹 ← 보통 이쪽을 문서화 -->
  </c:otherwise>
</c:choose>
```
`XxxMain.jsp`는 껍데기이고 실제 내용은 `XxxMainW.jsp`에 있을 수 있다. 반드시 확인할 것.

## 드롭다운 값 출처 판별

### 패턴 1 — DB 코드값 (가장 흔함)
```jsp
<c:forEach items="${tu:codeList('CONSULT_REF_GROUP')}" var="vo">
  <option value="${vo.CODE}">${vo.CODE_NM}</option>
</c:forEach>
```
→ `GI_CODE` 테이블의 `GROUP_CD='CONSULT_REF_GROUP'` 행들.

**관리 화면 경로 찾기** — `CodeGroup` enum에서 해당 그룹을 찾는다.
```java
// CodeGroup.java  ("그룹코드", "라벨", "구분", "path")
CONSULT_REF_GROUP("CONSULT_REF_GROUP@...", "상담유입", "CONSULT_REF", "consultDbRef"),
```
마지막 필드가 path면 관리 화면은 **`/globalinsu/codeManager/{path}/main.do`**.
path가 빈 문자열이면 전용 관리 화면이 없다는 뜻 → 문서에 "별도 관리 화면 없음(다른 메뉴에서 함께 관리)"로 적는다.

실제 값 확인:
```bash
mysql ... -e "SELECT CODE, CODE_NM FROM GI_CODE WHERE GROUP_CD='XXX' AND DATA_STS='Y' ORDER BY CD_NO"
```

### 패턴 2 — 하드코딩
```jsp
<option value="ORDER_TYPE1">광고</option>
<option value="ORDER_TYPE2">운영</option>
```
→ "코드에 고정. 항목 추가/변경은 개발 수정 필요"라고 명시.

⚠️ **관리 화면이 따로 있는데도 화면은 하드코딩을 쓰는 경우**가 있다(연동 누락 버그). 관리 화면의 코드그룹과 실제 화면이 참조하는 코드그룹이 **다른 그룹**이면 의심할 것. 발견하면 문서 "알아두면 좋은 것"에 적고 사용자에게 보고한다.

### 패턴 3 — 컨트롤러 조회값
```jsp
<c:forEach items="${salesTeamList}" var="st">
```
→ 컨트롤러에서 `mav.addObject("salesTeamList", ...)` 를 찾아 어떤 서비스/쿼리인지 추적. 조건(활성만/내 팀만 등)을 문서에 적는다.

## 권한별 노출 분기

```jsp
<c:if test="${fn:contains('P1,P6,P7', sessionScope.GI_SESSION.POSITION_CD)}">
  <th>연락처</th>
</c:if>
```
→ 이 컬럼은 P1·P6·P7만 본다. **컬럼/버튼마다 이런 조건이 붙으므로 전수 확인**한다.

```bash
grep -nE "fn:contains\('P|MANAGER_TEAM_CD|isSiteAuth" <뷰파일>
```

직급 코드↔이름은 DB 코드테이블에 있다(예: `POSITION_GROUP`). 하드코딩 주석에 의존하지 말고 실제 값을 조회해 확인할 것.

URL 단위 접근권한은 별도 enum/테이블에 있을 수 있다(예: `Site.java`의 `"P1@P7"`).

## 저장 검증 순서

```bash
grep -nA30 "function fn_save" <뷰파일> | grep -E "alert\(|return"
```
alert 문구를 **순서대로** 뽑으면 그대로 "저장이 안 될 때" 섹션이 된다.

## 상태 코드

목록의 상태 탭/배지는 대개 코드테이블 기반이다.
```bash
mysql ... -e "SELECT CODE, CODE_NM FROM GI_CODE WHERE GROUP_CD='XXX_STS_GROUP' ORDER BY CD_NO"
```
⚠️ **기본 필터가 일부 상태를 제외**하는 경우가 흔하다. 컨트롤러에서 기본값을 확인할 것.
```java
if (StringUtils.isEmpty(vo.getDATA_STS())) vo.setDATA_STS(Code.X_CONSULT_DB_NOT_SETTING.getCODE());
```
"전체보기인데 특정 상태가 안 보인다"는 문의의 원인이므로 반드시 문서화한다.

## 로컬 캡처 환경 만들기 (계정이 없을 때)

레거시 앱은 로그인에 계정 외 **권한 행**이 별도로 필요한 경우가 많다.

1. 계정 삽입 (비밀번호가 평문 저장이면 그대로 넣으면 된다)
2. 로그인 시도 → 실패하면 응답의 에러코드로 원인 추적
   ```bash
   grep -rn "CE0041" src/main/java   # → EMPTY_AUTH_LIST "권한이 존재하지않습니다"
   ```
3. 권한 테이블(예: `GI_AUTH`)에 행 추가. 운영에서 형태를 먼저 확인하면 정확하다.
   ```sql
   SELECT GROUP_CD, AUTH_CD FROM GI_AUTH GROUP BY GROUP_CD, AUTH_CD LIMIT 5;
   ```
4. 조직 테이블(HQ/BRANCH/TEAM)에 NOT NULL 참조가 걸려 있으면 함께 채운다.

권한별 비교 캡처를 위해 **직급이 다른 계정 2개**를 만들어 두면 좋다.
