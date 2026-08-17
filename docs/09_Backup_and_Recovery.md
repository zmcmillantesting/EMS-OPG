# Backup & Recovery

This document describes how EMS-OPG protects the SQLite database, where backups
live, how they get cleaned up, and how to recover from a bad state.

---

## Where backups live

All data — the database, its backups, logs, and exports — lives under a single
configurable root so it can sit on a shared network drive instead of the local
machine. `PathManager` resolves this from `config.json`'s `data_root` key:

- If `data_root` is set to an absolute path (e.g. a `P:\` network share), all
  data directories are created under it.
- If `data_root` is blank (the default in this repo), everything lives next to
  the application install.

Given a `data_root`, the layout is:

```
<data_root>/
├── database/
│   ├── ems_opg.db
│   └── backups/          ← automatic and manual backups land here
├── logs/
│   └── application.log   (+ up to backup_count rotated files)
└── exports/
    ├── health_report_<timestamp>.txt
    └── <order_number>_<timestamp>.csv
```

See `docs/33_Pathing_updates_pre_prod_push.md` for what to check before
deploying to a shared drive.

---

## Automatic backups

The application backs up the database **on shutdown**. This is wired into
`Application.run()`'s `finally` block via `core/shutdown.py`, so it fires both
on a clean exit and on the realistic shutdown path — an operator hitting
Ctrl+C. It does **not** fire if the server never actually started (e.g. the
port was already in use).

This is controlled entirely by `config.json`'s `"backup"` section:

```json
"backup": {
    "enabled": true,
    "directory": "database/backups",
    "max_backups": 5,
    "backup_on_startup": false,
    "backup_on_shutdown": true
}
```

- `enabled` — master switch. If `false`, no automatic backup happens
  regardless of the other flags.
- `backup_on_shutdown` — if `true`, a backup is created every time the
  application shuts down.
- `backup_on_startup` — present in config for a future startup-backup
  feature. **Not implemented yet** — see `docs/29_Known_Issues.md`.
- `max_backups` — how many timestamped backups to retain (see Cleanup below).
- `directory` — informational only right now; the actual location is always
  `PathManager.backup_dir` (`database/backups` under `data_root`), not read
  from this key.

A failed backup (e.g. the network drive is briefly unreachable) is caught and
logged — it does not crash the shutdown sequence.

---

## Manual backups

`POST /api/database/backup` triggers the same backup logic on demand, from
the running application. Both the automatic and manual paths go through the
same `DatabaseManager.backup()` method, so they share one retention policy —
there's no separate "manual backups pile up forever" behavior.

---

## Cleanup (retention)

Every time a backup is created — automatic or manual — `DatabaseManager`
prunes the `database/backups/` directory down to the newest `max_backups`
files (by modification time), deleting anything older. Backup filenames are
`ems_opg_<YYYYMMDD_HHMMSS>.db`.

Log files are rotated separately by `LoggerManager`'s `RotatingFileHandler`,
governed by `config.json`'s `logging.max_log_size_mb` and
`logging.backup_count` (currently 10) — `application.log` rotates once it
hits the size limit, and only the newest `backup_count` rotated files are
kept.

CSV exports (order-completion exports and weekly health reports, written to
`exports/`) are **never automatically deleted** — these are traceability
records and are kept indefinitely by design.

---

## Restore

`POST /api/database/restore` copies the most recent file in
`database/backups/` (by modification time) over the live database file. The
response reminds the operator to restart the server afterward, since the
running process may already have the old database open.

There is currently no way to restore a *specific* backup other than the
latest one through the API — to restore an older backup, copy it over the
live `ems_opg.db` file manually and restart the app.

---

## Verification

`POST /api/database/verify` runs `DatabaseManager.health_check()` — a plain
`SELECT 1` against the database — and reports whether the database is
reachable. The same check backs the `databaseConnected` field on
`GET /api/status` and the weekly health report (see below).

---

## Scheduling

Weekly, standalone, outside the running app: `scripts/health_report.py`.
Run it via an OS-level scheduler (Windows Task Scheduler / cron) — it does
not require the Flask server to be running, only the same Python
environment and `config.json`.

It reports:

- database reachability
- MAC address pool used/available counts
- open orders (devices completed vs. quantity)
- audit log flags from the last 7 days (`Test Failed`, `Manual Correction`,
  `MAC Reset`)
- free disk space on the `data_root` drive

and writes a plain-text report to `exports/health_report_<timestamp>.txt`.

---

## Disaster recovery

If the database file is lost or corrupted:

1. Stop the application if it's running.
2. Find the newest good backup in `database/backups/` (sorted by filename
   timestamp).
3. Copy it over `database/ems_opg.db` (or use `POST /api/database/restore`
   if the app is still reachable and the corruption doesn't prevent it from
   serving requests).
4. Restart the application.
5. Verify with `POST /api/database/verify` or `GET /api/status`.

If `database/backups/` itself is unreachable (e.g. the network share is
down), CSV exports in `exports/` still hold per-order traceability records
that were written at order-completion time, though they aren't a substitute
for a full database restore.
