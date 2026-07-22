---
description: 이 프로젝트에 매일 DB 백업(→ 팀 Google Drive) 워크플로 셋업
---

`db-backup` 스킬을 실행해, 현재 프로젝트에 자동 DB 백업 워크플로를 붙인다.

수행 순서 (스킬의 `SKILL.md` + `reference.md` 를 따른다):

1. 프로젝트의 DB 타입 감지 (`.env`/ORM 설정/의존성 → Postgres/MySQL/...)
2. `.github/workflows/db-backup.yml` + `docs/db-backup.md` 생성 (감지된 DB에 맞는 덤프/복원 블록 주입)
3. GitHub Secrets(`DB_URL`, `RCLONE_CONF`) 및 rclone `gdrive` remote 셋업 안내
4. 생성 파일만 보여주고, 커밋/푸시는 사용자 요청 시에만

전송 remote 이름은 항상 `gdrive` 로 고정 — 추후 NAS 이관은 `RCLONE_CONF` 시크릿만 교체.
