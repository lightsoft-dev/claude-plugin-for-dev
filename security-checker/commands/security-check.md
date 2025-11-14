---
description: Comprehensive security scanning for secrets, vulnerabilities, and code issues
---

# Security Checker

프로젝트의 보안 취약점을 포괄적으로 검사합니다. 환경 변수 노출, 하드코딩된 시크릿, 의존성 취약점, 코드 보안 이슈 등을 자동으로 탐지합니다.

## Steps to follow:

### 1. 민감 정보 노출 검사 (최우선 순위)

보안에서 가장 중요한 부분입니다. 철저하게 검사하세요.

#### A. .gitignore 검증

**1단계: .gitignore 파일 읽기**
- Read 도구로 `.gitignore` 파일 내용 확인
- 파일이 없으면 경고

**2단계: 필수 항목 확인**
다음 항목이 포함되어 있는지 체크:
```
.env
.env.local
.env.development
.env.production
.env.*.local
node_modules/
.DS_Store
Thumbs.db
*.log
*.key
*.pem
credentials.json
secrets.json
config/secrets.*
.aws/
.gcloud/
```

**누락된 항목은 경고로 표시**

#### B. 환경 변수 파일 검사

**검색할 파일들:**
```
.env
.env.local
.env.development
.env.production
.env.test
.env.staging
```

**Glob 도구로 검색:**
```
**/.env*
```

**각 파일에 대해:**
1. 파일이 존재하는지 확인
2. .gitignore에 포함되어 있는지 확인
3. **매우 중요**: Git 히스토리에 커밋된 적이 있는지 확인
   ```bash
   git log --all --full-history -- .env
   ```

   결과가 있으면 **심각한 보안 문제**:
   - 언제 커밋되었는지
   - 어떤 커밋 해시인지
   - 조치 방법 안내 (git filter-branch)

#### C. 하드코딩된 시크릿 탐지

**Grep 도구로 전체 프로젝트 검색** (node_modules, .git 제외)

다음 패턴들을 검색:

**1. API 키 패턴:**
```regex
(api[_-]?key|apikey|api[_-]?secret)\s*[:=]\s*['""][^'""]{20,}['""]
```

**2. AWS 키:**
```regex
AKIA[0-9A-Z]{16}
```

**3. Private 키:**
```regex
-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----
```

**4. 데이터베이스 연결 문자열 (비밀번호 포함):**
```regex
(mongodb|postgresql|mysql):\/\/[^:]+:[^@]+@
```

**5. 패스워드 하드코딩:**
```regex
(password|passwd|pwd)\s*[:=]\s*['""][^'""]+['""]
```

**6. 토큰:**
```regex
(token|bearer|jwt)\s*[:=]\s*['""][^'""]{20,}['""]
```

**7. GitHub 토큰:**
```regex
gh[pousr]_[A-Za-z0-9_]{36,}
```

**8. Stripe 키:**
```regex
(sk|pk)_(test|live)_[A-Za-z0-9]{24,}
```

**9. Google API 키:**
```regex
AIza[0-9A-Za-z_-]{35}
```

**10. Slack 토큰:**
```regex
xox[baprs]-[0-9]{10,12}-[0-9]{10,12}-[A-Za-z0-9]{24,}
```

**각 매칭에 대해:**
- 파일 경로와 라인 번호 기록
- 매칭된 내용 (일부 마스킹)
- 심각도: 매우 높음

**예외 처리:**
- 주석 내용은 낮은 우선순위
- 테스트 파일 (`*.test.js`, `*.spec.js`)은 표시하되 우선순위 낮춤
- `example`, `placeholder`, `your-key-here` 같은 명확한 예시는 제외

#### D. Git 히스토리 검사

**민감한 키워드가 과거 커밋에 있는지 검사:**

```bash
git log -p | grep -iE "(password|api.key|secret|token|bearer|private.key)" | head -50
```

**발견되면:**
- 어떤 커밋에서 발견되었는지
- 파일명
- **경고**: 이미 Git 히스토리에 기록되었으므로 단순 삭제로는 부족
- 조치 방법:
  ```bash
  # BFG Repo-Cleaner 사용 권장
  bfg --delete-files .env
  git reflog expire --expire=now --all
  git gc --prune=now --aggressive
  ```

### 2. 의존성 보안 검사

#### A. package.json 확인

**1단계: package.json 읽기**
- Read 도구로 `package.json` 파일 읽기
- dependencies와 devDependencies 확인

**2단계: npm audit 실행**

```bash
npm audit --json
```

**결과 분석:**
- **Critical**: 즉시 수정 필요
- **High**: 빠른 시일 내 수정
- **Moderate**: 수정 권장
- **Low**: 주시 필요

**각 취약점에 대해:**
- 패키지 이름
- 현재 버전
- 취약점 설명
- 권장 버전
- 수정 방법

**3단계: 오래된 패키지 확인**

```bash
npm outdated
```

**Major 버전이 뒤쳐진 패키지 표시**

#### B. 의존성 라이선스 확인 (선택적)

위험한 라이선스 (GPL 등) 체크

### 3. 코드 보안 취약점 검사

#### A. SQL Injection 위험

**위험한 패턴 검색 (Grep):**

```regex
(query|execute)\s*\(\s*['""`].*\$\{.*\}.*['""`]
(query|execute)\s*\(\s*['""].*\+.*['""]
```

**구체적 예시:**
```javascript
// 위험
db.query("SELECT * FROM users WHERE id = " + userId)
db.query(`DELETE FROM ${table} WHERE id = ${id}`)

// 안전
db.query("SELECT * FROM users WHERE id = ?", [userId])
db.query("SELECT * FROM users WHERE id = $1", [userId])
```

**발견된 각 케이스:**
- 파일 및 라인 번호
- 위험한 코드
- 안전한 대체 코드 제안
- 심각도: 높음

#### B. XSS (Cross-Site Scripting) 취약점

**위험한 패턴 검색:**

```regex
\.innerHTML\s*=
dangerouslySetInnerHTML
document\.write\(
eval\(
```

**구체적 예시:**
```javascript
// 위험
element.innerHTML = userInput
<div dangerouslySetInnerHTML={{ __html: userData }} />
document.write(input)

// 안전
element.textContent = userInput
DOMPurify.sanitize(userInput)
```

**심각도: 중간-높음**

#### C. Command Injection

**위험한 패턴:**

```regex
exec\([^)]*\$\{
spawn\([^)]*\+
child_process.*\$\{
```

**구체적 예시:**
```javascript
// 위험
exec(`rm -rf ${userInput}`)
spawn('sh', ['-c', command + userInput])

// 안전
execFile('rm', ['-rf', userInput])  // 인자를 배열로
```

**심각도: 매우 높음**

#### D. Path Traversal

**위험한 패턴:**

```regex
(readFile|writeFile|sendFile)\([^)]*\+
(readFile|writeFile|sendFile)\([^)]*\$\{
```

**구체적 예시:**
```javascript
// 위험
fs.readFile(req.query.file)
res.sendFile(userPath)

// 안전
const safePath = path.join(__dirname, 'uploads', path.basename(filename))
fs.readFile(safePath)
```

**심각도: 높음**

#### E. 정규식 ReDoS (Regular Expression Denial of Service)

**위험한 패턴:**
- 중첩된 반복: `(a+)+`
- 백트래킹이 과도한 패턴

```regex
\(\.\*\)\+
\(\.\+\)\+
```

**심각도: 중간**

### 4. 설정 보안 검사

#### A. CORS 설정

**파일 검색:**
- Express: `cors()`
- 다른 프레임워크의 CORS 설정

**위험한 설정 검색:**
```regex
cors\(\s*\{\s*origin:\s*['"]\*['""]
Access-Control-Allow-Origin:\s*\*
```

**발견 시:**
- 파일 및 위치
- 현재 설정
- 권장 설정:
  ```javascript
  // 안전한 설정
  cors({
    origin: ['https://yourdomain.com', 'https://app.yourdomain.com']
  })
  ```

**심각도: 중간**

#### B. 보안 헤더 확인

**검색할 헤더:**
- `helmet` 패키지 사용 여부
- 수동 헤더 설정 여부

**확인할 헤더:**
1. **X-Frame-Options**: Clickjacking 방지
2. **Content-Security-Policy**: XSS 방지
3. **X-Content-Type-Options**: MIME 스니핑 방지
4. **Strict-Transport-Security**: HTTPS 강제
5. **X-XSS-Protection**: XSS 필터

**package.json에서 helmet 검색:**
- 없으면 권장

**서버 파일에서 헤더 설정 검색:**
```regex
setHeader\(['""]X-Frame-Options
setHeader\(['""]Content-Security-Policy
helmet\(\)
```

**없으면 경고**

#### C. HTTPS 강제 여부

**검색:**
```regex
(app\.use\(|middleware.*)(https|ssl|secure)
```

**Production에서 HTTPS 강제하는지 확인**

### 5. 인증/인가 보안

#### A. JWT 검증

**위험한 패턴:**
```regex
jwt\.decode\(
```

**안전한 패턴:**
```regex
jwt\.verify\(
```

**decode만 사용하고 verify 안 하면 경고**

**예시:**
```javascript
// 위험
const decoded = jwt.decode(token)  // 검증 없음!

// 안전
const decoded = jwt.verify(token, SECRET_KEY)
```

#### B. 비밀번호 해싱

**검색:**
- bcrypt, argon2, scrypt 사용 여부
- 평문 비밀번호 저장 여부

**위험한 패턴:**
```regex
password\s*[:=]\s*req\.(body|params|query)\.password
INSERT.*password.*VALUES.*\$\{
```

**안전한 패턴:**
```regex
bcrypt\.(hash|compare)
argon2\.(hash|verify)
```

#### C. 세션 보안

**검색:**
- `express-session` 설정
- `httpOnly`, `secure`, `sameSite` 쿠키 옵션

```javascript
// 안전한 설정
session({
  cookie: {
    httpOnly: true,
    secure: true,  // HTTPS only
    sameSite: 'strict'
  }
})
```

### 6. 프론트엔드 보안 (React/Vue/등)

#### A. 외부 스크립트 로딩

**위험한 패턴:**
```regex
<script\s+src=['""]http://
eval\(
```

**CDN은 HTTPS 사용 권장**

#### B. localStorage에 민감 정보

**검색:**
```regex
localStorage\.setItem\([^)]*token
localStorage\.setItem\([^)]*password
sessionStorage\.setItem\([^)]*token
```

**권장: httpOnly 쿠키 또는 메모리에만 저장**

### 7. Docker/컨테이너 보안 (선택적)

**Dockerfile이 있으면:**

#### A. Root 사용자 회피
```dockerfile
# 위험
RUN apt-get install

# 안전
USER node
RUN apt-get install
```

#### B. 시크릿을 이미지에 복사하지 않음
```dockerfile
# 위험
COPY .env /app/.env

# 안전: 환경 변수로 주입
```

### 8. 상세 보안 리포트 생성

모든 검사를 완료한 후, 다음 형식으로 종합 리포트를 생성하세요:

---

```markdown
# 🔒 보안 검사 리포트

생성 일시: 2024-11-14 15:30:00
프로젝트: [프로젝트명]

---

## 📊 전체 요약

| 심각도 | 개수 |
|--------|------|
| 🚨 심각 (Critical) | 3 |
| ⚠️ 경고 (High) | 5 |
| 💡 주의 (Medium) | 8 |
| ℹ️ 정보 (Low) | 2 |

**전체 보안 점수: 68/100** (개선 필요)

---

## 🚨 심각 (즉시 수정 필요)

### 1. .env 파일이 .gitignore에 없음 ❌

**위치**: 루트 디렉토리
**발견 내용**: `.env` 파일이 존재하지만 `.gitignore`에 포함되지 않음
**위험도**: 매우 높음
**영향**: 환경 변수가 Git에 커밋되어 GitHub에 노출될 위험

**즉시 조치:**
```bash
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
```

**추가 확인**: Git 히스토리에 이미 커밋되었는지 확인
```bash
git log --all --full-history -- .env
```

---

### 2. 하드코딩된 API 키 발견 ❌

**파일**: [src/config/api.js:15](src/config/api.js#L15)
**발견 내용**:
```javascript
const API_KEY = "your_actual_api_key_here_redacted";
```

**위험도**: 매우 높음
**영향**: API 키가 소스 코드에 노출되어 누구나 확인 가능

**즉시 조치:**
1. `.env` 파일로 이동:
   ```bash
   # .env
   API_KEY=your_actual_api_key_here
   ```

2. 코드 수정:
   ```javascript
   const API_KEY = process.env.API_KEY;
   ```

3. **중요**: 노출된 키는 즉시 폐기하고 새로 발급
   - Stripe 대시보드에서 해당 키 삭제
   - 새 키 발급 후 `.env`에만 저장

---

### 3. Git 히스토리에 .env 파일 커밋 발견 ❌

**커밋**: [a1b2c3d](commit/a1b2c3d) (2024-10-15)
**파일**: `.env`
**위험도**: 매우 높음
**영향**: GitHub에 이미 푸시되었다면 환경 변수가 공개 이력에 남음

**즉시 조치:**
```bash
# 1. BFG Repo-Cleaner 설치 (권장)
brew install bfg  # macOS
# 또는 https://rtyley.github.io/bfg-repo-cleaner/

# 2. .env 파일을 히스토리에서 완전 제거
bfg --delete-files .env

# 3. 히스토리 정리
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Force push (주의: 팀원과 조율 필요)
git push origin --force --all
```

**주의**: Force push는 팀 전체에 영향을 미치므로 반드시 팀원들과 조율

**노출된 모든 시크릿 교체 필요**

---

## ⚠️ 경고 (빠른 수정 권장)

### 1. npm audit에서 5개의 취약점 발견

**세부 내용**:

#### Critical (1개)
- **lodash** 4.17.15
  - 취약점: Prototype Pollution
  - CVSS: 9.8
  - 수정 버전: 4.17.21
  - 조치: `npm install lodash@latest`

#### High (2개)
- **axios** 0.21.0
  - 취약점: SSRF (Server-Side Request Forgery)
  - CVSS: 8.1
  - 수정 버전: 0.21.4

- **minimist** 1.2.5
  - 취약점: Prototype Pollution
  - 수정 버전: 1.2.8

#### Moderate (2개)
- **url-parse** 1.5.3
- **ws** 7.4.5

**즉시 조치:**
```bash
npm audit fix
# 또는 수동으로
npm install lodash@latest axios@latest minimist@latest
```

---

### 2. SQL Injection 위험 코드 발견 (3곳)

#### 위치 1: [src/db/users.js:42](src/db/users.js#L42)

**위험한 코드**:
```javascript
const query = "SELECT * FROM users WHERE id = " + req.params.id;
db.query(query);
```

**위험도**: 높음
**공격 시나리오**: `id=1 OR 1=1; DROP TABLE users;--`

**수정 방법**:
```javascript
// Parameterized Query 사용
const query = "SELECT * FROM users WHERE id = ?";
db.query(query, [req.params.id]);

// 또는 ORM 사용 (Sequelize, TypeORM 등)
const user = await User.findByPk(req.params.id);
```

#### 위치 2: [src/api/products.js:58](src/api/products.js#L58)

**위험한 코드**:
```javascript
db.query(`DELETE FROM products WHERE category = '${category}'`);
```

**수정 방법**:
```javascript
db.query("DELETE FROM products WHERE category = ?", [category]);
```

#### 위치 3: [src/services/search.js:23](src/services/search.js#L23)

**위험한 코드**:
```javascript
const sql = `SELECT * FROM items WHERE name LIKE '%${searchTerm}%'`;
```

**수정 방법**:
```javascript
const sql = "SELECT * FROM items WHERE name LIKE ?";
db.query(sql, [`%${searchTerm}%`]);
```

---

### 3. XSS 취약점 발견 (2곳)

#### 위치 1: [src/components/Profile.jsx:28](src/components/Profile.jsx#L28)

**위험한 코드**:
```javascript
profileDiv.innerHTML = userData.bio;
```

**위험도**: 중간-높음
**공격 시나리오**: bio에 `<script>alert('XSS')</script>` 삽입

**수정 방법**:
```javascript
// 방법 1: textContent 사용
profileDiv.textContent = userData.bio;

// 방법 2: sanitize 라이브러리
import DOMPurify from 'dompurify';
profileDiv.innerHTML = DOMPurify.sanitize(userData.bio);
```

#### 위치 2: [src/pages/Comments.tsx:45](src/pages/Comments.tsx#L45)

**위험한 코드**:
```tsx
<div dangerouslySetInnerHTML={{ __html: comment.text }} />
```

**수정 방법**:
```tsx
// sanitize 후 사용
<div dangerouslySetInnerHTML={{
  __html: DOMPurify.sanitize(comment.text)
}} />

// 또는 일반 텍스트로
<div>{comment.text}</div>
```

---

### 4. CORS 설정이 너무 관대함

**파일**: [server.js:10](server.js#L10)
**현재 설정**:
```javascript
app.use(cors({ origin: '*' }));
```

**위험도**: 중간
**영향**: 모든 도메인에서 API 접근 가능 (CSRF 공격 위험)

**수정 방법**:
```javascript
// 특정 도메인만 허용
app.use(cors({
  origin: [
    'https://yourdomain.com',
    'https://app.yourdomain.com'
  ],
  credentials: true
}));

// 또는 환경 변수로
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS.split(','),
  credentials: true
}));
```

---

### 5. 보안 헤더 미설정

**발견 내용**: Express 서버에 보안 헤더가 설정되지 않음

**누락된 헤더**:
- X-Frame-Options (Clickjacking 방지)
- Content-Security-Policy (XSS 방지)
- X-Content-Type-Options (MIME 스니핑 방지)
- Strict-Transport-Security (HTTPS 강제)

**수정 방법**:
```bash
npm install helmet
```

```javascript
// server.js
const helmet = require('helmet');
app.use(helmet());

// 또는 세밀한 설정
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"]
    }
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));
```

---

## 💡 주의 (개선 권장)

### 1. JWT 검증 누락 가능성

**파일**: [src/middleware/auth.js:18](src/middleware/auth.js#L18)
**발견 내용**:
```javascript
const decoded = jwt.decode(token);
```

**권장**: `verify` 사용
```javascript
const decoded = jwt.verify(token, process.env.JWT_SECRET);
```

---

### 2. 오래된 패키지

다음 패키지들의 Major 버전이 크게 뒤쳐져 있습니다:

| 패키지 | 현재 | 최신 | 업데이트 |
|--------|------|------|----------|
| react | 16.14.0 | 18.2.0 | Major |
| express | 4.17.1 | 4.18.2 | Minor |
| webpack | 4.46.0 | 5.88.2 | Major |

**조치**: 점진적 업데이트 권장 (Breaking changes 확인 필요)

---

### 3. localStorage에 토큰 저장

**파일**: [src/utils/auth.js:12](src/utils/auth.js#L12)
```javascript
localStorage.setItem('authToken', token);
```

**권장**: httpOnly 쿠키 사용 (XSS로부터 보호)

---

## ✅ 양호

### .gitignore 설정
✅ `node_modules/` 포함됨
✅ `*.log` 포함됨
✅ `.DS_Store` 포함됨

### 비밀번호 해싱
✅ bcrypt 사용 확인 ([src/auth/password.js:25](src/auth/password.js#L25))

### HTTPS 사용
✅ Production에서 HTTPS 강제 ([server.js:45](server.js#L45))

---

## 📈 상세 점수

| 카테고리 | 점수 | 상태 |
|---------|------|------|
| 민감 정보 관리 | 25/40 | 🚨 심각 |
| 의존성 보안 | 15/20 | ⚠️ 경고 |
| 코드 보안 | 18/30 | ⚠️ 경고 |
| 설정 보안 | 10/20 | 💡 주의 |
| 인증/인가 | 8/10 | ✅ 양호 |

**전체 점수: 76/120 → 63/100**

---

## 🎯 즉시 조치 항목 (우선순위)

### 오늘 반드시 수정:
1. ❌ `.env`를 `.gitignore`에 추가
2. ❌ `src/config/api.js`의 하드코딩된 API 키 제거
3. ❌ 노출된 API 키 폐기 및 재발급

### 이번 주 내 수정:
4. ⚠️ Git 히스토리에서 `.env` 제거
5. ⚠️ SQL Injection 코드 수정 (3곳)
6. ⚠️ npm audit fix 실행
7. ⚠️ XSS 취약점 수정 (2곳)

### 이번 달 내 개선:
8. 💡 helmet.js 설치 및 설정
9. 💡 CORS 설정 강화
10. 💡 주요 패키지 업데이트

---

## 📚 보안 개선 권장 사항

### 단기 (1주)
- [ ] 모든 심각/경고 항목 수정
- [ ] pre-commit hook 설정 (시크릿 검사)
- [ ] 팀 보안 가이드라인 작성

### 중기 (1개월)
- [ ] 정기적 보안 스캔 CI/CD 통합
- [ ] 의존성 자동 업데이트 (Dependabot)
- [ ] 보안 교육 실시

### 장기 (분기)
- [ ] 침투 테스트 수행
- [ ] 보안 감사 (Security Audit)
- [ ] Bug Bounty 프로그램 고려

---

## 🔧 자동 수정 가능 항목

다음 항목은 자동으로 수정할 수 있습니다. 진행할까요?

1. `.gitignore`에 `.env` 추가
2. `npm audit fix` 실행
3. `helmet` 설치 및 기본 설정
4. 오래된 패키지 업데이트 (Minor 버전만)

---

## 🔐 보안 체크리스트

다음 보안 검사를 통과했습니다:

- [ ] 환경 변수 관리
  - [ ] .env가 .gitignore에 있음
  - [ ] Git 히스토리에 시크릿 없음
  - [ ] 하드코딩된 키 없음

- [ ] 의존성 보안
  - [ ] 알려진 취약점 없음
  - [ ] 최신 버전 사용

- [ ] 코드 보안
  - [ ] SQL Injection 방지
  - [ ] XSS 방지
  - [ ] CSRF 방지

- [ ] 서버 설정
  - [ ] 보안 헤더 설정
  - [ ] HTTPS 사용
  - [ ] CORS 적절히 설정

**전체 체크리스트: 8/16 완료 (50%)**

---

## ⏭️ 다음 단계

1. **즉시**: 심각 항목 3개 수정
2. **오늘 중**: npm audit fix 실행
3. **내일**: SQL Injection 및 XSS 코드 수정
4. **이번 주**: 보안 헤더 설정 및 CORS 강화
5. **정기적**: 매주 보안 스캔 실행 (`/security-check`)

---

보안은 지속적인 프로세스입니다. 정기적으로 점검하세요! 🔒
```

---

### 9. 자동 수정 제안 (선택적)

사용자에게 물어본 후, 안전하게 자동 수정 가능한 항목 처리:

#### A. .gitignore 업데이트
```bash
cat >> .gitignore << EOF
# Environment variables
.env
.env.local
.env.*.local

# Secrets
*.key
*.pem
credentials.json
secrets.json
EOF
```

#### B. npm audit fix
```bash
npm audit fix
```

#### C. helmet 설치
```bash
npm install helmet
```

**사용자에게 확인 후 실행**

### 10. CI/CD 통합 제안

**.github/workflows/security-check.yml** 생성 제안:
```yaml
name: Security Check

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run npm audit
        run: npm audit
      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
```

## Important Notes:

### 우선순위
1. **민감 정보 노출** - 가장 높음
2. **의존성 취약점** - 높음
3. **코드 취약점** - 중간-높음
4. **설정 문제** - 중간

### False Positive 최소화
- 테스트 파일은 우선순위 낮춤
- 주석은 별도 표시
- `example`, `placeholder` 같은 명확한 예시는 제외

### 사용자 경험
- 한국어로 명확하게 설명
- 각 문제에 대한 **구체적인 수정 방법** 제시
- 위험도와 영향을 명확히 설명
- 즉시 조치 항목과 장기 개선 항목 구분

### 에러 처리
- Git이 없는 프로젝트도 처리
- package.json이 없으면 해당 섹션 스킵
- 권한 문제 등 예외 상황 안내

### 보안
- 리포트에 실제 시크릿 전문을 노출하지 말 것 (마스킹)
- 민감한 정보는 일부만 표시 (예: `api_key_abc...xyz`)
