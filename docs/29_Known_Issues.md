# Known Issues

Tracked here rather than fixed immediately because each needs a judgment
call, isn't urgent, or is explicitly deferred. Update this list as items get
resolved or new ones are found.

## Configuration / versioning

- **Version number is inconsistent across the codebase.** `pyproject.toml`
  and `core/constants.py` both say `0.1.0`; `core/version.py`'s (unused)
  `Version` dataclass and `config.json`'s `application.version` both say
  `1.0.0`. Needs consolidating onto one source of truth before
  `docs/15_Release_Process.md`'s versioning section means anything.
- **`backup_on_startup` config flag exists but isn't implemented.**
  `config.json`'s `backup.backup_on_startup` is read nowhere in code —
  only `backup_on_shutdown` is wired up (`core/shutdown.py`). Either build
  a startup-backup feature to match it, or remove the flag so it doesn't
  imply behavior that doesn't exist.
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
- **Production `data_root` is unset.** The app currently defaults to
  storing everything next to the local install; nothing has been run
  end-to-end against the real shared-drive path yet. See
  `docs/33_Pathing_updates_pre_prod_push.md`.
- **Packaging/installer process is undecided** — see
  `docs/11_Deployment.md`.

## Minor

- **`config/config.json` must stay strictly valid JSON** (no comments, no
  trailing commas) — this has broken the app on startup at least once in
  practice. No format guard currently catches this before it reaches
  `Application.__init__`. Worth a pre-commit or CI check if this recurs.
- **Log rotation covers `application.log` only.** Ad hoc log files written
  by test scripts (`logs/qr_generation_test.log`,
  `logs/mac_database_initialization.log`, `logs/database_flow_test.log`)
  aren't on a rotating handler and can grow unbounded, though they're
  test/dev artifacts rather than production logs.
