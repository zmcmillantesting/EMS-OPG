# Known Issues

Tracked here rather than fixed immediately because each needs a judgment
call, isn't urgent, or is explicitly deferred. Update this list as items get
resolved or new ones are found.

## Configuration / versioning

- ~~**Version number is inconsistent across the codebase.**~~ Resolved —
  `pyproject.toml`, `core/constants.py`, and `config.json` all say `1.0.0`
  now. `core/version.py`'s separate `Version` dataclass is still unused
  dead code (harmless, but worth deleting rather than leaving as a second
  version source someone could edit by mistake).
- ~~**`backup_on_startup` config flag exists but isn't implemented.**~~
  Resolved — startup and shutdown backups are both implemented via
  `core/backup.py`'s shared `run_backup_if_enabled()`, independently
  toggled by `config.json`. Startup is now the default; shutdown is
  available but off by default. See `docs/09_Backup_and_Recovery.md`.
- **`config.json`'s `"paths"` section is unused.** `PathManager` derives
  every directory from `data_root` directly; the `assets`/`exports`/
  `database`/`qr_cache` keys under `"paths"` in `config.json` are dead
  config, never read by anything.

## Dead / unused code

- **`core/startup.py` and `core/shutdown.py`'s original design both import
  `PyQt5`**, which isn't a project dependency (not in `pyproject.toml`).
  `startup.py` is fully dead — nothing imports it, and it would
  `ModuleNotFoundError` if it were. `shutdown.py` is now live (wired into
  `Application.run()`) but its `PyQt5`-flavored origins are gone; worth a
  pass to confirm nothing else in `core/` still assumes a desktop UI.
- **`core/version.py`'s `Version` dataclass is unused.** `constants.py`'s
  plain `APP_VERSION` string is what's actually imported (by
  `api/routes.py`'s `/api/status`). See versioning note above.
- **`services/audit_service.py` is an empty file.** Audit logging happens
  ad hoc via `AuditRepository` calls directly inside `api/routes.py`
  instead of going through a service layer, unlike `OrderService` and
  `DeviceService`.
- **`MacAddressRepository.get_first_available()` and
  `get_next_available()` are identical** — one is redundant.
- **`QR_Codes/qr_templates.py`** is imported nowhere live (`qr_service.py`
  has it commented out).

## API gaps

- **`PUT /devices/<serial>` (manual correction) can't change `test_result`.**
  It updates order/serial/operator/MAC fields but not the PASS/FAIL result
  itself — there's currently no way to correct a mis-recorded test result
  through the API.
- **No email delivery for the weekly health report** — it's written to
  `exports/health_report_<timestamp>.txt` only, by design for now (see
  `docs/09_Backup_and_Recovery.md`). Revisit once SMTP details are
  available.
- **Order/device cleanup was explicitly descoped.** Deleting old closed
  orders (with operator approval) was part of the original automation
  request and deliberately deferred — no age threshold or approval
  mechanism has been designed.

## Not yet verified

- **Frontend hasn't been re-exercised against this cycle's backend
  changes.** The API surface for existing endpoints didn't change shape,
  but the automation additions (backup/export/health-report) haven't been
  confirmed against the actual running UI, only via `pytest` and direct
  script/function calls.
- **Production `data_root` is unset.**~~ Resolved — `config.json`'s
  `data_root` now points at the real shared-drive path.
- **The PyWebView desktop window has not been visually verified.** Windowing
  (PyWebView) and the server behind it (waitress) are now implemented
  (`core/application.py`), and the server-binding/event-wiring logic was
  tested headlessly, but no sandbox here has a display server — the window
  actually opening, rendering the frontend, and closing cleanly needs to be
  confirmed on a real machine before relying on it.
- **Freezing into a standalone executable is still undecided.** PyWebView
  gives the native window; something like PyInstaller/Nuitka is still
  needed to bundle Python itself for shop-floor machines without a Python
  install. See `docs/11_Deployment.md`'s Installer section.

## Minor## Not yet verified

- ~~**Production `data_root` is unset.**~~ Resolved — `config.json`'s
  `data_root` points at the real UNC path (`\\emsfs01\production\...`) and
  has been confirmed working from a real launch.
- ~~**The PyWebView desktop window has not been visually verified.**~~
  Resolved — confirmed on real hardware: the window opens, a full
  provision → test → history workflow completed, and the shutdown-backup
  toggle behaved correctly (fired on startup, correctly skipped on
  shutdown since `backup_on_shutdown` is off by default).
- **Freezing into a standalone executable is still undecided.** PyWebView
  gives the native window; something like PyInstaller/Nuitka is still
  needed to bundle Python itself for shop-floor machines without a Python
  install. See `docs/11_Deployment.md`'s Installer section.
- **SQLite database lives directly on a network share
  (`\\emsfs01\production\...`).** SQLite's locking, which coordinates
  concurrent access, is well known to be unreliable over SMB/CIFS network
  filesystems — under concurrent writes from multiple operators this can
  cause spurious "database is locked" errors or, in the worst case,
  corruption. A single-operator smoke test won't surface this. **Decision:
  accept this risk for now** rather than splitting `data_root` (DB local,
  backups/exports on the share) or moving to a network-safe database.
  Revisit if "database is locked" errors actually show up, or once
  multiple simultaneous test stations are running.
- **Frontend hasn't been re-exercised against this cycle's backend
  changes beyond a single manual pass.** One full operator workflow
  (provision → board test → history) has now been confirmed working on
  real hardware, but the newer automation specifically (CSV
  auto-export on order completion, the health-report script) hasn't been
  independently checked against real output files yet.


- **`config/config.json` must stay strictly valid JSON** (no comments, no
  trailing commas) — this has broken the app on startup at least once in
  practice. No format guard currently catches this before it reaches
  `Application.__init__`. Worth a pre-commit or CI check if this recurs.
- **Log rotation covers `application.log` only.** Ad hoc log files written
  by test scripts (`logs/qr_generation_test.log`,
  `logs/mac_database_initialization.log`, `logs/database_flow_test.log`)
  aren't on a rotating handler and can grow unbounded, though they're
  test/dev artifacts rather than production logs.
