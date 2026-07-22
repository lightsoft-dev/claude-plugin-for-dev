# DB command matrix + workflow template

Fill the template with the block matching the detected DB. Everything else is identical across DB types (that's the point — only dump/restore + client install vary).

## Command matrix

| DB | Client install | Dump | Restore |
|---|---|---|---|
| Postgres | `postgresql-client-17` (match server major ≥ client) | `pg_dump -Fc --no-owner --no-privileges` | `pg_restore --no-owner --no-privileges --clean --if-exists` |
| MySQL | `mysql-client` | `mysqldump --single-transaction --routines --triggers` | `mysql < dump.sql` |

Postgres uses the compressed custom format (`.dump`, restore with `pg_restore`). MySQL dumps plain SQL (`.sql`, restore by piping into `mysql`). Adjust file extension accordingly.

## Workflow template — `.github/workflows/db-backup.yml`

Replace `{{REPO}}`, `{{INSTALL_BLOCK}}`, `{{DUMP_BLOCK}}`.

```yaml
name: DB Backup

# 매일 03:00 KST(18:00 UTC) DB를 덤프 후 팀 Google Drive로 업로드.
# 수동 실행: Actions 탭 > DB Backup > Run workflow
on:
  schedule:
    - cron: "0 18 * * *"
  workflow_dispatch:

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
{{INSTALL_BLOCK}}

      - name: Install rclone
        run: curl -fsSL https://rclone.org/install.sh | sudo bash

      - name: Dump & upload to Google Drive
        env:
          DB_URL: ${{ secrets.DB_URL }}
          RCLONE_CONF: ${{ secrets.RCLONE_CONF }}
        run: |
          set -euo pipefail
          # rclone 설정 복원 (remote 이름은 gdrive 로 고정 — 나중에 NAS 이관해도 이 이름 유지)
          mkdir -p ~/.config/rclone
          printf '%s' "$RCLONE_CONF" > ~/.config/rclone/rclone.conf

{{DUMP_BLOCK}}
          echo "dump size: $(du -h "$FILE" | cut -f1)"

          rclone copy "$FILE" "gdrive:{{REPO}}-backup/"
          echo "✅ uploaded $FILE"

          # 보관 30일: Drive엔 수명주기 규칙이 없어 rclone으로 처리
          rclone delete "gdrive:{{REPO}}-backup/" --min-age 30d
```

### Postgres — `{{INSTALL_BLOCK}}`

```yaml
      - name: Install pg_dump 17 (서버 >= 클라이언트 버전 요구)
        run: |
          sudo sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
          curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/pgdg.gpg
          sudo apt-get update
          sudo apt-get install -y postgresql-client-17
```

### Postgres — `{{DUMP_BLOCK}}`

```bash
          # 러너 기본 pg_dump(16)가 아닌 방금 설치한 17을 PATH 우선
          export PATH="/usr/lib/postgresql/17/bin:$PATH"
          FILE="{{REPO}}-$(date +%Y%m%d-%H%M%S).dump"
          # -Fc: 압축 커스텀 포맷(pg_restore로 복원), 소유자/권한 제외로 이식성 확보
          pg_dump "$DB_URL" -Fc --no-owner --no-privileges -f "$FILE"
```

### MySQL — `{{INSTALL_BLOCK}}`

```yaml
      - name: Install mysql client
        run: sudo apt-get update && sudo apt-get install -y mysql-client
```

### MySQL — `{{DUMP_BLOCK}}`

```bash
          # mysql:// URL 파싱 (mysqldump는 URL을 직접 받지 못함)
          proto_removed="${DB_URL#mysql://}"
          creds="${proto_removed%%@*}"; hostpart="${proto_removed#*@}"
          DB_USER="${creds%%:*}"; DB_PASS="${creds#*:}"
          hostport="${hostpart%%/*}"; DB_NAME="${hostpart#*/}"; DB_NAME="${DB_NAME%%\?*}"
          DB_HOST="${hostport%%:*}"; DB_PORT="${hostport#*:}"; [ "$DB_PORT" = "$DB_HOST" ] && DB_PORT=3306
          FILE="{{REPO}}-$(date +%Y%m%d-%H%M%S).sql"
          mysqldump --single-transaction --routines --triggers \
            -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$FILE"
```

## Restore section for `docs/db-backup.md`

### Postgres
```bash
rclone copy "gdrive:{{REPO}}-backup/{{REPO}}-YYYYMMDD-HHMMSS.dump" ./
pg_restore --no-owner --no-privileges --clean --if-exists \
  -d "<복원_대상_DB_URL>" ./{{REPO}}-YYYYMMDD-HHMMSS.dump
```

### MySQL
```bash
rclone copy "gdrive:{{REPO}}-backup/{{REPO}}-YYYYMMDD-HHMMSS.sql" ./
mysql -h <host> -P <port> -u <user> -p <dbname> < ./{{REPO}}-YYYYMMDD-HHMMSS.sql
```
