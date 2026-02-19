#!/bin/bash
# Auto-QA Setup Script
# Creates state file and initializes QA session
# Auto-detects app URL from running dev servers or project config

set -euo pipefail

# Parse arguments
PROMPT_PARTS=()
MAX_ISSUES=5
MAX_ITERATIONS=0
APP_URL=""
TESTER=""
LINEAR_TEAM="Purple-edu"
LINEAR_PROJECT=""
COMPLETION_PROMISE="null"

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      cat << 'HELP_EOF'
Auto-QA - Automated black-box QA testing with issue tracking

USAGE:
  /auto-qa [OPTIONS] PROMPT...

ARGUMENTS:
  PROMPT...    Description of what to test (app areas, test focus, etc.)

OPTIONS:
  --app-url <url>              Target app URL (auto-detected if omitted)
  --tester <name>              Tester/assignee name for Linear issues
  --max-issues <n>             Stop after finding N issues (default: 5)
  --max-iterations <n>         Max loop iterations (default: unlimited)
  --linear-team <team-key>     Linear team key (e.g., "ENG")
  --linear-project <name>      Linear project name
  --completion-promise <text>  Promise phrase to stop loop
  -h, --help                   Show this help

EXAMPLES:
  /auto-qa --tester "QA Bot" --max-issues 10 Test admin app study management menus
  /auto-qa --max-iterations 20 --linear-team ENG Random test all menus
  /auto-qa --app-url http://localhost:3300 Specific URL test

APP URL AUTO-DETECTION:
  1. Checks running dev servers on common ports (3000-3999, 4000-4999, 5173, 8080, etc.)
  2. Reads package.json scripts for port configuration
  3. If multiple found, lists them for user to choose
  4. If none found, prompts user to start the dev server

REQUIRES:
  - playwright-cli or agent-browser skill installed
  - Linear MCP server connected (linear-server or linear plugin)
HELP_EOF
      exit 0
      ;;
    --app-url)
      APP_URL="$2"; shift 2 ;;
    --tester)
      TESTER="$2"; shift 2 ;;
    --max-issues)
      MAX_ISSUES="$2"; shift 2 ;;
    --max-iterations)
      MAX_ITERATIONS="$2"; shift 2 ;;
    --linear-team)
      LINEAR_TEAM="$2"; shift 2 ;;
    --linear-project)
      LINEAR_PROJECT="$2"; shift 2 ;;
    --completion-promise)
      COMPLETION_PROMISE="$2"; shift 2 ;;
    *)
      PROMPT_PARTS+=("$1"); shift ;;
  esac
done

PROMPT="${PROMPT_PARTS[*]}"

if [[ -z "$PROMPT" ]]; then
  echo "❌ Error: No test description provided" >&2
  exit 1
fi

# ── Auto-detect app URL if not provided ──
if [[ -z "$APP_URL" ]]; then
  echo "🔍 Auto-detecting running dev servers..."

  DETECTED_URLS=()

  # Scan common dev server ports
  PORTS=(3000 3001 3300 3301 4000 4200 5173 5174 8000 8080 8888)

  for PORT in "${PORTS[@]}"; do
    if lsof -iTCP:"$PORT" -sTCP:LISTEN -P -n >/dev/null 2>&1; then
      # Verify it responds to HTTP
      if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 1 "http://localhost:$PORT" 2>/dev/null | grep -qE "^[23]"; then
        DETECTED_URLS+=("http://localhost:$PORT")
      fi
    fi
  done

  if [[ ${#DETECTED_URLS[@]} -eq 0 ]]; then
    echo ""
    echo "⚠️  No running dev servers detected."
    echo ""
    echo "   Please start your app first, then re-run this command."
    echo "   Or specify --app-url manually:"
    echo "     /auto-qa --app-url http://localhost:3000 $PROMPT"
    echo ""

    # Try to suggest a start command from package.json
    if [[ -f "package.json" ]]; then
      echo "   Detected package.json. Common start commands:"
      # Extract dev/start scripts
      DEV_SCRIPT=$(python3 -c "import json; d=json.load(open('package.json')); s=d.get('scripts',{}); print(s.get('dev',''))" 2>/dev/null || echo "")
      START_SCRIPT=$(python3 -c "import json; d=json.load(open('package.json')); s=d.get('scripts',{}); print(s.get('start',''))" 2>/dev/null || echo "")
      [[ -n "$DEV_SCRIPT" ]] && echo "     pnpm dev    → $DEV_SCRIPT"
      [[ -n "$START_SCRIPT" ]] && echo "     pnpm start  → $START_SCRIPT"

      # Check for filter-able workspaces (monorepo)
      if command -v pnpm &>/dev/null && [[ -f "pnpm-workspace.yaml" ]]; then
        echo ""
        echo "   Monorepo detected. Example:"
        echo "     pnpm dev --filter=@repo/admin"
      fi
    fi

    exit 1

  elif [[ ${#DETECTED_URLS[@]} -eq 1 ]]; then
    APP_URL="${DETECTED_URLS[0]}"
    echo "   ✅ Found: $APP_URL"

  else
    echo ""
    echo "   Found multiple dev servers:"
    for i in "${!DETECTED_URLS[@]}"; do
      PORT=$(echo "${DETECTED_URLS[$i]}" | grep -oE '[0-9]+$')
      PROC_NAME=$(lsof -iTCP:"$PORT" -sTCP:LISTEN -P -n 2>/dev/null | tail -1 | awk '{print $1}' || echo "unknown")
      echo "     [$((i+1))] ${DETECTED_URLS[$i]}  ($PROC_NAME)"
    done
    echo ""

    # ── Smart port selection from project config ──
    # 1. Check CLAUDE.md for port definitions (e.g., "admin (port 3300)")
    CONFIG_PORT=""
    if [[ -f "CLAUDE.md" ]]; then
      # Extract port numbers associated with "admin" keyword
      ADMIN_PORT=$(grep -iE '(admin|admin-app|admin dashboard).*port\s*[0-9]+' CLAUDE.md 2>/dev/null | grep -oE 'port\s*[0-9]+' | head -1 | grep -oE '[0-9]+' || echo "")
      if [[ -n "$ADMIN_PORT" ]]; then
        for url in "${DETECTED_URLS[@]}"; do
          if echo "$url" | grep -qE ":${ADMIN_PORT}$"; then
            CONFIG_PORT="$ADMIN_PORT"
            APP_URL="$url"
            break
          fi
        done
      fi
    fi

    # 2. Check package.json scripts for port hints (e.g., "next dev -p 3300")
    if [[ -z "$CONFIG_PORT" ]]; then
      # Look for admin app's package.json in monorepo
      for pkg in apps/admin/package.json apps/web/package.json; do
        if [[ -f "$pkg" ]]; then
          PKG_PORT=$(python3 -c "
import json, re
d=json.load(open('$pkg'))
scripts=d.get('scripts',{})
for k,v in scripts.items():
    if 'dev' in k or 'start' in k:
        m=re.search(r'-p\s*(\d+)|--port\s*(\d+)|PORT=(\d+)', v)
        if m:
            print(m.group(1) or m.group(2) or m.group(3))
            break
" 2>/dev/null || echo "")
          if [[ -n "$PKG_PORT" ]]; then
            for url in "${DETECTED_URLS[@]}"; do
              if echo "$url" | grep -qE ":${PKG_PORT}$"; then
                CONFIG_PORT="$PKG_PORT"
                APP_URL="$url"
                echo "   📋 Detected port $PKG_PORT from $pkg"
                break 2
              fi
            done
          fi
        fi
      done
    fi

    # 3. Fallback: prefer non-API frontend ports, excluding common API ports
    if [[ -z "$CONFIG_PORT" ]]; then
      API_PORTS="3001 3301 8000"
      for url in "${DETECTED_URLS[@]}"; do
        PORT=$(echo "$url" | grep -oE '[0-9]+$')
        if ! echo "$API_PORTS" | grep -qw "$PORT"; then
          APP_URL="$url"
          break
        fi
      done
    fi

    # 4. Ultimate fallback to first detected
    if [[ -z "$APP_URL" ]]; then
      APP_URL="${DETECTED_URLS[0]}"
    fi

    if [[ -n "$CONFIG_PORT" ]]; then
      echo "   ✅ Auto-selected: $APP_URL (from project config)"
    else
      echo "   ✅ Auto-selected: $APP_URL (frontend port)"
    fi
    echo "   (Override with --app-url if needed)"
  fi
fi

# Create state directory
mkdir -p .claude/auto-qa

# Quote values for YAML
if [[ -n "$COMPLETION_PROMISE" ]] && [[ "$COMPLETION_PROMISE" != "null" ]]; then
  CP_YAML="\"$COMPLETION_PROMISE\""
else
  CP_YAML="null"
fi

# Create state file
cat > .claude/auto-qa/state.local.md <<EOF
---
active: true
iteration: 1
max_iterations: $MAX_ITERATIONS
max_issues: $MAX_ISSUES
issues_found: 0
issues_fixed: 0
issues_skipped: 0
app_url: "$APP_URL"
tester: "$TESTER"
linear_team: "$LINEAR_TEAM"
linear_project: "$LINEAR_PROJECT"
completion_promise: $CP_YAML
started_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
---

$PROMPT
EOF

# Create empty issues file
echo "[]" > .claude/auto-qa/issues.json

cat <<EOF
🔍 Auto-QA session activated!

  App URL:        $APP_URL
  Tester:         ${TESTER:-"(not set)"}
  Max issues:     $MAX_ISSUES
  Max iterations: $(if [[ $MAX_ITERATIONS -gt 0 ]]; then echo $MAX_ITERATIONS; else echo "unlimited"; fi)
  Linear team:    ${LINEAR_TEAM:-"(not set)"}
  Linear project: ${LINEAR_PROJECT:-"(not set)"}

  State: .claude/auto-qa/state.local.md
  Issues: .claude/auto-qa/issues.json

🔄
EOF

echo ""
echo "$PROMPT"
