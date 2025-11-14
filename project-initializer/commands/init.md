---
description: Interactive project initialization for various tech stacks
---

# Project Initializer

프로젝트 타입과 기술 스택에 맞는 초기 세팅을 자동으로 수행합니다.

## Steps to follow:

### 1. Gather Project Information
사용자에게 다음 정보를 질문하세요:

#### 프로젝트 타입
다음 중 하나를 선택하도록 안내:
- **웹 프론트엔드**: React, Next.js, Vue, Svelte 등
- **웹 백엔드**: Express, NestJS, FastAPI, Spring Boot 등
- **모바일 앱**: React Native, Flutter 등
- **풀스택**: Next.js, MERN, T3 Stack 등

#### 기술 스택 세부 사항
프로젝트 타입에 따라 구체적인 기술 스택을 질문:

**프론트엔드의 경우:**
- 프레임워크: React, Next.js, Vue.js, Svelte, Vite 등
- 언어: TypeScript, JavaScript
- 스타일링: Tailwind CSS, styled-components, CSS Modules, Emotion 등
- 상태관리: Zustand, Redux, Recoil, Jotai (필요시)
- 추가 도구: ESLint, Prettier 포함 여부

**백엔드의 경우:**
- 프레임워크: Express, NestJS, Fastify, Koa (Node.js) / FastAPI, Django (Python) / Spring Boot (Java)
- 언어: TypeScript, JavaScript, Python, Java
- 데이터베이스: PostgreSQL, MySQL, MongoDB, Redis (필요시)
- ORM/ODM: Prisma, TypeORM, Mongoose 등
- 추가 도구: ESLint, Prettier 포함 여부

**모바일의 경우:**
- 프레임워크: React Native, Flutter
- 언어: TypeScript, JavaScript, Dart
- 상태관리: Zustand, Redux Toolkit 등
- 네비게이션: React Navigation, Expo Router 등

**풀스택의 경우:**
- 스택: Next.js Full Stack, MERN, T3 Stack, SvelteKit 등
- 데이터베이스: PostgreSQL, MongoDB 등
- ORM: Prisma, Drizzle 등

#### 프로젝트 이름
- 프로젝트 폴더명 (kebab-case 권장)

### 2. Execute Project Setup

수집한 정보를 바탕으로 다음 작업을 순서대로 수행:

#### A. 프로젝트 생성
선택한 스택에 맞는 CLI 도구 사용:

**프론트엔드:**
- Next.js: `npx create-next-app@latest [프로젝트명] --typescript --tailwind --app --eslint`
- Vite + React: `npm create vite@latest [프로젝트명] -- --template react-ts`
- Vue: `npm create vue@latest [프로젝트명]`
- Svelte: `npm create svelte@latest [프로젝트명]`

**백엔드:**
- Express: 수동 설정 (package.json 생성 후 필요 패키지 설치)
- NestJS: `npx @nestjs/cli new [프로젝트명]`
- FastAPI: 수동 설정 (venv 생성, requirements.txt)

**모바일:**
- React Native: `npx react-native init [프로젝트명]` 또는 `npx create-expo-app [프로젝트명]`
- Flutter: `flutter create [프로젝트명]`

#### B. 기본 설정 파일 생성

**모든 프로젝트 공통:**
1. `.gitignore` (아직 없다면 생성)
2. `.env.example` 파일 생성 (환경변수 템플릿)
3. `README.md` 업데이트 또는 생성:
   - 프로젝트 이름
   - 기술 스택 목록
   - 설치 및 실행 방법
   - 폴더 구조 설명

**TypeScript 프로젝트:**
- `tsconfig.json` (프레임워크에서 제공하지 않는 경우)

**Node.js 프로젝트:**
- `.eslintrc` (ESLint 선택 시)
- `.prettierrc` (Prettier 선택 시)

#### C. 폴더 구조 생성

프로젝트 타입에 맞는 기본 폴더 구조:

**프론트엔드:**
```
src/
├── components/      # 재사용 가능한 컴포넌트
├── pages/ or app/   # 페이지 (프레임워크에 따라)
├── styles/          # 전역 스타일
├── utils/           # 유틸리티 함수
├── hooks/           # 커스텀 훅 (React)
├── types/           # TypeScript 타입 정의
└── constants/       # 상수
```

**백엔드:**
```
src/
├── controllers/     # 컨트롤러
├── services/        # 비즈니스 로직
├── models/          # 데이터 모델
├── routes/          # 라우트 정의
├── middleware/      # 미들웨어
├── config/          # 설정 파일
├── utils/           # 유틸리티
└── types/           # TypeScript 타입
```

#### D. 초기 패키지 설치

**선택된 추가 도구 설치:**
- Tailwind CSS: `npm install -D tailwindcss postcss autoprefixer`
- ESLint + Prettier: `npm install -D eslint prettier eslint-config-prettier`
- 상태관리 라이브러리 (선택 시)
- 기타 필수 의존성

#### E. Git 초기화
```bash
cd [프로젝트명]
git init
git add .
git commit -m "Initial commit: Setup [기술스택] project"
```

### 3. 완료 메시지

프로젝트 세팅이 완료되면 한국어로 요약 메시지 출력:

```
✅ 프로젝트 초기 세팅이 완료되었습니다!

📦 프로젝트: [프로젝트명]
🛠️  기술 스택:
   - [선택한 기술 스택 목록]

📁 생성된 구조:
   [폴더 구조 요약]

🚀 다음 단계:
   1. cd [프로젝트명]
   2. npm install (아직 안했다면)
   3. npm run dev (또는 해당 프레임워크의 dev 명령어)

💡 .env.example을 참고해서 .env 파일을 생성하세요!

화이팅! 🔥
```

## Important Notes:
- 사용자가 선택한 옵션을 정확히 반영하여 프로젝트를 생성하세요
- 모든 명령어 실행 전에 현재 디렉토리를 확인하세요
- 이미 존재하는 폴더/파일이 있다면 덮어쓰기 전에 사용자에게 확인받으세요
- 한국어로 친절하게 안내하세요
- 각 단계마다 진행 상황을 알려주세요
