# Project Structure

This describes the actual current layout. Earlier drafts of this document
described a `views/`/`workers/`-style desktop (PyQt) structure — that was
never built; the app is a Flask backend serving a plain HTML/CSS/JS
frontend.

```
EMS-OPG/
├── app.py                      Entry point — python app.py
├── pyproject.toml              Dependencies, pytest config
├── config/
│   └── config.json             All runtime settings (see 07_Config_System_Design.md)
├── src/ems_opg/
│   ├── core/                   App bootstrap, paths, constants, exceptions
│   │   ├── application.py      Application class — starts waitress + the PyWebView window, owns shutdown flow
│   │   ├── paths_manager.py    Resolves every data directory from config.json's data_root
│   │   ├── shutdown.py         Runs on app exit — triggers the shutdown DB backup
│   │   ├── backup.py           Shared trigger for startup/shutdown DB backups (config-gated)
│   │   ├── webview_api.py      Methods exposed to the frontend as window.pywebview.api.* (native save dialog)
│   │   ├── constants.py        App-wide constants (version string, status labels, etc.)
│   │   ├── validators.py       Order/serial number format validation
│   │   ├── environment.py      APP_ENV → Environment enum
│   │   └── exceptions.py       Custom exception hierarchy
│   │
│   ├── api/                    Flask app and HTTP layer
│   │   ├── server.py           create_app() — Flask app, static frontend serving, log-file endpoint
│   │   └── routes.py           Every /api/* route: orders, devices, workflow, backup/restore, exports
│   │
│   ├── database/               SQLAlchemy setup
│   │   ├── base.py             Declarative Base
│   │   ├── models.py           Order, Device, MACAddressPool, AuditLog
│   │   ├── engine.py           SQLite engine, resolves the DB file path via PathManager
│   │   ├── session.py          Session factory
│   │   ├── database.py         DatabaseManager — session context manager, health_check(), backup()
│   │   └── init_db.py          CLI: create/recreate the schema
│   │
│   ├── repositories/           Direct DB access, one per model — no business rules here
│   │   ├── order_repository.py
│   │   ├── device_repository.py
│   │   ├── mac_address_repository.py
│   │   └── audit_repository.py
│   │
│   ├── services/                Business logic, built on repositories
│   │   ├── order_service.py     Order provisioning (creates placeholder devices, allocates MACs)
│   │   ├── device_service.py    Device reservation (finalizing a tested device)
│   │   └── qr_service.py        Builds/validates the QR command for each workflow step
│   │                            (no audit_service.py — audit logging is direct AuditRepository
│   │                            calls from routes.py; see 29_Known_Issues.md)
│   │
│   ├── workflow/                In-memory operator workflow state (not persisted)
│   │   ├── workflow_engine.py   Step sequencing, PASS/FAIL result capture
│   │   ├── workflow_session.py  Per-session state (operator, order, MACs, current step)
│   │   └── workflow_state.py    WorkflowState enum
│   │
│   ├── QR_Codes/                QR command generation and validation
│   │   ├── qr_generator.py      Renders a command string to a PNG (segno)
│   │   ├── qr_validator.py      Per-step command validation before a QR is generated
│   │   ├── qr_result.py         QRResult dataclass
│   │   └── qr_templates.py      (currently unused — see qr_service.py's commented-out import)
│   │
│   ├── config/
│   │   └── config_manager.py    ConfigurationManager — see 07_Config_System_Design.md
│   │
│   └── app_logging/
│       └── logger.py             LoggerManager (RotatingFileHandler setup) + Logger wrapper
│
├── frontend/                    Static site served directly by Flask (no build step)
│   ├── index.html, testing.html, history.html, settings.html
│   ├── components/              HTML fragments (panels for MAC, QR, results, etc.)
│   ├── css/
│   └── js/                      Plain JS, one file per page + api.js/common.js
│
├── scripts/                      Standalone admin scripts (run outside the Flask app)
│   ├── load_database.py          One-time/repeatable MAC pool CSV import
│   └── health_report.py          Weekly health report (OS-scheduled, writes to exports/)
│
├── tests/
│   ├── unit/
│   └── integration/
│
└── docs/                         This directory
```

## Data directories (not checked into source layout above)

`database/`, `logs/`, `database/backups/`, `exports/`, `cache/` are created
at runtime by `PathManager.create_directories()`, rooted at `config.json`'s
`data_root` (blank = next to the app install, the default in this repo).
See `docs/09_Backup_and_Recovery.md` and `docs/33_Pathing_updates_pre_prod_push.md`.

## Layer responsibilities, briefly

- **repositories/** — raw queries only, no business rules, no validation.
- **services/** — business rules, built on top of one or more repositories.
  Routes should call services (or repositories directly for simple reads),
  not raw SQLAlchemy.
- **api/routes.py** — HTTP concerns (request parsing, status codes, JSON
  shaping) plus a growing amount of orchestration that arguably belongs in
  a service (e.g. the order-completion CSV export lives here directly
  rather than in a service — see 29_Known_Issues.md).
- **workflow/** — purely in-memory per-operator-session state; nothing here
  is persisted to the database until `session_finish` calls into
  `services/device_service.py`.
