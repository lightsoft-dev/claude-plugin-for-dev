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
- **Notion Database ID**: The database ID where you want to track this (or use a default if configured)

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
  - **Start Time**: Current timestamp (use `now()`)
  - **Branch**: The git branch name you created
  - **Description**: [user provided description]
- Save the page ID for later reference

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
