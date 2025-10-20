---
description: Start a new feature and create Notion tracker
---

# Feature Start

You are starting a new feature development workflow with Notion tracking.

## Steps to follow:

### 1. Gather Information
Ask the user for:
- **Feature name**: What feature are you building?
- **Description**: Brief description of the feature

**Note**: The Notion Database ID is read from `.mcp.json` configuration file (`featureTracker.defaultDatabaseId`).
- If the database ID is not configured or is "YOUR_DATABASE_ID_HERE", ask the user to provide it and inform them they can set it in `.mcp.json` to avoid entering it every time.
- If configured, use the default database ID without asking the user.

### 2. Create Git Branch
- Create a new branch with format: `feature/[feature-name-kebab-case]`
- Switch to that branch
- Example: `git checkout -b feature/user-authentication`

### 3. Create Notion Tracker Entry
Use the Notion MCP tools to:
- Create a new page in the Feature Tracker database
- Set the following properties:
  - **Feature Name**: [user provided name]
  - **Status**: "작업중" (In Progress)
  - **Start Time**: Current timestamp in ISO 8601 format (e.g., "2025-10-20T17:30:00+09:00" or use JavaScript `new Date().toISOString()`)
  - **Branch**: The git branch name you created
  - **Description**: [user provided description]
- Save the page ID for later reference

**Important**: For the Start Time property, you must use the proper format for Notion date properties:
- Use `date:Start Time:start` for the property name
- Use `date:Start Time:is_datetime` and set it to 1 for datetime
- Provide the current timestamp in ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ)

### 4. Initialize Todo List
Use the TodoWrite tool to create an initial task breakdown:
- Break down the feature into logical steps
- Add at least 3-5 actionable tasks
- Mark the first task as pending

### 5. Confirmation Message
Display a summary in Korean:
```
✅ 작업을 시작합니다!

📝 Feature: [feature name]
🌿 Branch: [branch name]
📊 Notion: [link to Notion page]

할 일 목록이 생성되었습니다. 화이팅!
```

## Important Notes:
- Always create the Notion entry BEFORE starting actual development
- Store the Notion page ID in a temporary way if needed for feature-end
- Be encouraging and supportive in your messages
- Use Korean for user-facing messages
