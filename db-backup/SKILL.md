---
name: db-backup
description: Set up an automated daily DB backup (GitHub Actions → rclone → team Google Drive) for the current project, adapting the dump/restore commands to the project's DB type (Postgres, MySQL, ...). Use when the user says "db-backup", "DB 백업 붙여줘", "백업 워크플로 만들어줘", "이 프로젝트 DB 백업 설정", or asks to add scheduled database backups to Google Drive / NAS. Always invoke when the user wants to wire up automated DB backups.
---

# DB Backup

Add a **daily automated database backup** to the current project: a GitHub Actions workflow that dumps the DB and uploads it to the team's Google Drive via `rclone`. The DB dump/restore commands adapt to whatever database the project actually uses.

## Fixed conventions (do not change per project)

- **Transport = `rclone`, remote name = `gdrive`.** The workflow references `gdrive:` and nothing else. This is the migration seam: to move backups from Google Drive to a NAS/S3/SFTP later, only the `RCLONE_CONF` secret changes (a new remote still named `gdrive`) — the workflow is never touched.
- **Destination folder = `gdrive:<repo>-backup/`** where `<repo>` is the project's repo/dir name. Keeps every project separated inside the shared team drive.
- **Retention = 30 days** (`rclone delete --min-age 30d`). Drive has no lifecycle rules, so rclone prunes.
- **Schedule = 03:00 KST daily** (`cron: "0 18 * * *"` UTC) + `workflow_dispatch` for manual runs.

## Steps

### 1. Detect the DB type

Figure out which database the project uses — **do not ask if you can detect it.** Look, in order:

1. `DATABASE_URL` / `DIRECT_URL` scheme in `.env`, `.env.example`, or deploy config → `postgres://` / `postgresql://` → Postgres; `mysql://` → MySQL.
2. ORM config: Prisma `datasource.provider` (`schema.prisma`), Drizzle/TypeORM/Sequelize dialect, Django `ENGINE`, Rails `adapter` in `database.yml`.
3. Dependencies: `pg` / `postgres` / `@supabase/*` → Postgres; `mysql2` / `mysql` → MySQL.

Read `reference.md` for the per-DB command matrix. If the type isn't Postgres or MySQL, follow the same template pattern using that DB's native dump/restore tool and tell the user it's an untested addition.

### 2. Pick the connection secret

The workflow needs a **direct connection string** (not a pooled/pgbouncer one — dumps need a real session).

- Supabase/Postgres: use the `DIRECT_URL` value (port 5432), not the pooled `DATABASE_URL` (port 6543).
- Otherwise: the project's `DATABASE_URL`.

This goes into GitHub Secret **`DB_URL`**.

### 3. Generate the workflow + docs

Write two files, filling the template in `reference.md` with the detected DB's install/dump block and `<repo>` folder name:

- `.github/workflows/db-backup.yml`
- `docs/db-backup.md`

Keep the Korean comments — they explain the non-obvious bits (client version match, PATH order, retention). Match the existing repo's comment language if it differs.

### 4. Guide the one-time setup

Tell the user exactly what they must do by hand (the skill can't do these — they need their Google account + repo settings):

1. **rclone → team Google Drive token** (once per machine, reusable across projects):
   ```bash
   brew install rclone   # if not installed
   rclone config
   ```
   New remote, name **`gdrive`** (exactly), Storage `drive`, scope Full access, auto-config → log in with the **team** Google account, not a Shared Drive. Then:
   ```bash
   cat ~/.config/rclone/rclone.conf
   ```
   Copy the whole `[gdrive]` block (includes the token).

2. **GitHub Secrets** (repo → Settings → Secrets and variables → Actions):

   | Secret | Value |
   |---|---|
   | `DB_URL` | direct DB connection string from step 2 |
   | `RCLONE_CONF` | full `rclone.conf` contents |

3. **Verify**: Actions tab → DB Backup → Run workflow → check `gdrive:<repo>-backup/` for a fresh dump.

### 5. Confirm, don't commit

Show the generated files. **Do not commit or push** unless the user asks — creating the workflow and setting secrets is theirs to trigger.

## Migration note (Google Drive → NAS later)

When the team moves off Google Drive: regenerate `rclone.conf` with the new backend (`sftp`, `s3`, `local`, ...) but **keep the remote named `gdrive`**, update the `RCLONE_CONF` secret. Zero workflow edits. Optionally rename the remote everywhere later if the `gdrive` name becomes confusing — that's the only reason to touch the yml.
