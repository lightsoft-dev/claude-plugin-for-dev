# Feature Tracker Plugin

Notion과 연동하여 작업 시작과 종료를 자동으로 추적하는 Claude Code 플러그인입니다.

## 기능

- `/feature-start`: 새로운 작업 시작
  - Git 브랜치 자동 생성
  - Notion에 작업 트래커 생성
  - 시작 시간 자동 기록
  - Todo 리스트 초기화

- `/feature-end`: 작업 완료
  - 변경사항 커밋
  - Pull Request 생성
  - Notion 트래커 업데이트 (완료 상태, 종료 시간)
  - 작업 시간 자동 계산

## 설치 방법

### 1. Notion Integration 설정

1. https://www.notion.so/my-integrations 접속
2. "New integration" 클릭
3. Integration 이름: "Claude Feature Tracker"
4. **Internal Integration Token** 복사

### 2. Notion Database 생성

Notion에 다음 구조의 데이터베이스를 생성하세요:

**데이터베이스 이름**: Feature Tracker

**속성 (Properties)**:
- `Feature Name` (Title) - 작업 이름
- `Status` (Select) - 작업중, 완료됨, 대기중
- `Start Time` (Date) - 시작 시간
- `End Time` (Date) - 종료 시간
- `Duration` (Formula) - `dateBetween(prop("End Time"), prop("Start Time"), "hours")`
- `Branch` (Text) - Git 브랜치명
- `Description` (Text) - 작업 설명
- `PR URL` (URL) - Pull Request 링크

데이터베이스에 Integration 연결:
- 페이지 우측 상단 `...` → `Connections` → 생성한 integration 추가

### 3. Notion MCP 서버 설치

```bash
# Notion MCP 서버 클론
git clone https://github.com/makenotion/notion-mcp-server
cd notion-mcp-server
npm install
npm run build
```

### 4. Claude Desktop 설정

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "notion": {
      "command": "node",
      "args": ["/절대/경로/notion-mcp-server/build/index.js"],
      "env": {
        "NOTION_API_TOKEN": "your_notion_integration_token_here"
      }
    }
  }
}
```

### 5. Claude Desktop 재시작

Claude Desktop을 완전히 종료하고 다시 실행합니다.

## 사용 방법

### 작업 시작

```
/feature-start
```

Claude가 다음 정보를 물어봅니다:
- Feature 이름
- 설명
- Notion Database ID

### 작업 완료

```
/feature-end
```

Claude가 다음을 자동으로 수행합니다:
- 변경사항 리뷰
- 커밋 생성
- PR 생성
- Notion 업데이트

## 주의사항

- Notion MCP가 제대로 설정되어 있어야 합니다
- Git repository에서 실행해야 합니다
- GitHub CLI (`gh`)가 설치되어 있어야 PR 생성이 가능합니다

## 문제 해결

### Notion MCP가 연결되지 않을 때
- Claude Desktop을 완전히 재시작했는지 확인
- `claude_desktop_config.json` 경로가 올바른지 확인
- Notion API Token이 유효한지 확인

### Database에 접근할 수 없을 때
- Integration이 해당 데이터베이스에 연결되어 있는지 확인
- Database ID가 올바른지 확인
