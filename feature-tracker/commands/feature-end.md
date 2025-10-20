---
description: Complete feature and update Notion tracker
---

# Feature End

You are completing a feature development workflow and updating Notion tracking.

## Steps to follow:

### 1. Review Current Work
- Run `git status` to see all changes
- Check if all todos are completed (if not, ask user if they want to proceed)
- Verify tests pass (if applicable)

### 2. Ask for Notion Page
Ask the user for:
- **Notion Page ID**: The ID of the tracker entry created in feature-start
  - If they don't have it, try to search for it by branch name or feature name

### 3. Commit Changes
- Stage all relevant files with `git add`
- Create a descriptive commit message following the project's convention
- Include the standard co-authored footer:
  ```
  🤖 Generated with [Claude Code](https://claude.com/claude-code)
  
  Co-Authored-By: Claude <noreply@anthropic.com>
  ```
- Commit the changes

### 4. Create Pull Request
- Push the branch to remote: `git push -u origin [branch-name]`
- Use `gh pr create` to create a pull request:
  - **Title**: Clear, descriptive title
  - **Body**: Include summary, changes made, and test plan
  - Include Claude Code footer
- Capture the PR URL

### 5. Update Notion Tracker
Use Notion MCP tools to update the tracker page:
- **Status**: Change to "완료됨" (Completed)
- **End Time**: Current timestamp in ISO 8601 format (use JavaScript `new Date().toISOString()`)
  - Use `date:End Time:start` for the property name
  - Use `date:End Time:is_datetime` and set it to 1 for datetime
  - Provide the current timestamp in ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ)
- **PR URL**: Add the pull request URL
- **Duration**: Will auto-calculate based on Start Time and End Time

### 6. Clean Up
- Clear the todo list using TodoWrite with empty array
- Switch back to main branch: `git checkout main`

### 7. Completion Message
Display a summary in Korean:
```
🎉 작업이 완료되었습니다!

📝 Feature: [feature name]
⏱️  작업 시간: [calculated duration] 시간
🔗 PR: [PR URL]
📊 Notion: [link to updated Notion page]

수고하셨습니다! 🙌
```

## Important Notes:
- Always update Notion AFTER creating the PR (so you have the URL)
- If the user can't provide the Notion page ID, try to find it by searching
- Be thorough in reviewing changes before committing
- Celebrate the completion with encouraging Korean messages
- If any step fails, inform the user clearly and ask how to proceed
