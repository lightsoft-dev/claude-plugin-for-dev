---
name: auto-qa
description: "Automated black-box QA testing with Linear issue tracking. Iteratively tests random parts of a web application using browser automation (playwright-cli or agent-browser), discovers bugs, checks Linear for duplicates via MCP, creates new issues with screenshots/recordings, fixes bugs, and generates an HTML report. Use when: (1) user says /auto-qa, (2) user wants automated QA testing of a web app, (3) user wants to find and fix bugs with Linear tracking, (4) user wants black-box testing with issue reports."
---

# Auto-QA

Iterative black-box QA testing loop: test a web app, find bugs, track in Linear, fix, generate HTML report.

## Prerequisites Check

Before starting, verify these are available:

1. **Browser automation**: One of these skills must be installed:
   - `playwright-cli` (preferred)
   - `agent-browser`
   - Or Playwright MCP tools (`mcp__playwright__*`)
   If none available, ask user to install: `/find-skills playwright`

2. **Linear MCP**: Search for Linear tools with `ToolSearch` query `"linear"`.
   Possible tool prefixes: `mcp__linear__*`, `mcp__linear-server__*`
   If no Linear MCP tools found, tell user:
   - Install Linear plugin: `claude plugins add linear`
   - Or add to `~/.claude.json` under `mcpServers`:
     ```json
     "linear-server": { "type": "sse", "url": "https://mcp.linear.app/sse" }
     ```

3. **Login credentials**: Ask user for login URL, credentials, or login method.

## Startup

Run the setup script (app URL is auto-detected from running dev servers):
```!
"${SKILL_DIR}/scripts/setup-auto-qa.sh" $ARGUMENTS
```

**App URL auto-detection**: The script scans common ports (3000-3301, 4200, 5173, 8080, etc.)
for running HTTP servers. If multiple found, it prefers frontend ports over API ports.
If none found, it suggests start commands from `package.json`.
User can still override with `--app-url <url>`.

## Iteration Workflow

Each iteration follows this cycle:

### 1. Pick a Random Test Target

Choose a random page/feature from the app. Vary across iterations:
- Navigate to different menu sections
- Test CRUD operations (create, read, update, delete)
- Test edge cases (empty forms, boundary values, special characters)
- Test UI state transitions (filters, pagination, modals, tabs)
- Check console for errors/warnings
- Check network requests for failures

### 2. Perform Black-Box Testing

Use browser automation to interact with the app:
- Take **before screenshots** of the page state
- Perform actions (click, type, navigate, filter, sort)
- Observe results: console errors, visual glitches, broken behavior
- Take **after screenshots** if an issue is found
- Record GIFs/videos if available for reproduction evidence

### 3. When an Issue is Found

#### 3a. Check Linear for Duplicates

Use Linear MCP tools to search for existing issues:
- Search by keywords from the issue title
- If a matching issue exists with the same problem → **skip** (mark as `skipped`)
- If no match → proceed to create

#### 3b. Create Linear Issue

Use Linear MCP tools to create a new issue:
- **Title**: Concise description of the bug (Korean preferred if project uses Korean)
- **Description**: Include:
  - Steps to reproduce
  - Expected vs actual behavior
  - Affected page/component path
  - Screenshot links (if uploaded)
- **Assignee**: Set to `--tester` name if provided
- **Labels**: Add "QA", "Bug" if available
- **State**: Set to appropriate state (e.g., "Todo", "In Progress")

#### 3c. Fix the Bug

- Identify the root cause in the codebase
- Apply the fix
- Verify the fix with browser automation
- Take **after-fix screenshots**

#### 3d. Commit the Fix (One Commit Per Issue)

**IMPORTANT**: Create a separate git commit for each issue fix. This allows the user to cherry-pick individual fixes.

```bash
git add <changed-files>
git commit -m "[admin] QA: <이슈 요약>"
```

After committing, capture the commit hash and store it in the issue record:
```bash
COMMIT_HASH=$(git rev-parse HEAD)
```

Record `commit_hash` and `commit_message` in the issue JSON (see step 4).

#### 3e. Update Linear Issue

- Update issue state to "Done" or "In Review"
- Add fix details to the issue description (cause, fix summary)

### 4. Record the Issue Locally

Append to `.claude/auto-qa/issues.json`:
```json
{
  "id": "QA-001",
  "title": "Issue title",
  "severity": "high|mid|low",
  "category": "crash|function|ux|security|performance",
  "location": "path/to/file.tsx",
  "description": "What went wrong",
  "cause": "Root cause analysis",
  "fix": "What was changed",
  "status": "fixed|open|skipped",
  "commit_hash": "full-40-char-git-hash",
  "commit_message": "[admin] QA: 이슈 요약",
  "linear_id": "TEAM-123",
  "linear_url": "https://linear.app/...",
  "screenshots_before": ["/path/to/before.png"],
  "screenshots_after": ["/path/to/after.png"],
  "recording_before": "/path/to/before.gif",
  "recording_after": "/path/to/after.gif"
}
```

### 5. Check Completion

Read `.claude/auto-qa/state.local.md` frontmatter:
- If `issues_found >= max_issues` → generate report and stop
- If `iteration >= max_iterations` (and max_iterations > 0) → generate report and stop
- Otherwise → update `iteration` count and continue

### 6. Generate HTML Report (ALWAYS)

**IMPORTANT**: Always generate an HTML report, not markdown. The HTML report is the primary deliverable.

Generate after **every issue is fixed** (not just at the end):
```bash
python3 "${SKILL_DIR}/scripts/generate_report.py" .claude/auto-qa/issues.json docs/qa-reports/QA_REPORT_$(date +%Y%m%d).html
```

The script:
- Reads `issues.json` and embeds screenshots as base64 (self-contained HTML)
- Creates expandable issue cards with severity badges, before/after screenshots
- Supports GIF/video recordings as evidence

After generation, open the report for the user:
```bash
open docs/qa-reports/QA_REPORT_$(date +%Y%m%d).html
```

**Do NOT generate markdown (.md) reports** - always use the HTML generator script for the final report.

## State File Format

`.claude/auto-qa/state.local.md`:
```yaml
---
active: true
iteration: 1
max_iterations: 20
max_issues: 10
issues_found: 3
issues_fixed: 2
issues_skipped: 1
app_url: "http://localhost:3300"
tester: "QA Bot"
linear_team: "ENG"
linear_project: "Admin QA"
---
Test description prompt here
```

## Issue Severity Guide

| Severity | Criteria |
|----------|----------|
| **high** | App crash, data loss, security vulnerability, core feature broken |
| **mid**  | Feature partially broken, incorrect data display, console errors, UX confusion |
| **low**  | Minor visual glitch, debug logs in console, typo, non-critical warning |

## Tips

- Vary test targets across iterations to maximize coverage
- Check browser console for errors after every navigation
- Test both happy path and edge cases
- For pagination bugs: change page, change filter, verify page resets
- For modal bugs: open, close, reopen - check state reset
- For form bugs: save, edit, draft save, delete - check state consistency
- Screenshots go to `.claude/auto-qa/screenshots/` directory
