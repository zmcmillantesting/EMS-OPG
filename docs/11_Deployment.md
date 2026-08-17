# Deployment

## Development

```bash
uv sync --extra dev        # or: pip install -e ".[dev]"
python -m ems_opg.database.init_db   # first-time schema creation
python app.py                        # starts the Flask dev server on :5000
```

`config.json`'s `data_root` is left blank in the repo, so in development
everything (database, logs, backups, exports) lives under the project root.
Override the port with `EMS_OPG_PORT` if 5000 is taken.

## Testing

```bash
uv run pytest
```

See `docs/10_Testing_Strategy.md`. The suite uses an in-memory SQLite
database per test (`tests/integration/conftest.py`) — it never touches the
real `database/ems_opg.db`.

## Production

Production runs the same `python app.py` entry point — there is currently
no separate production server (no gunicorn/waitress in front of it; Flask's
built-in dev server is what's used). Before pointing it at real data:

1. Set `config.json`'s `data_root` to the shared network path (see
   `docs/33_Pathing_updates_pre_prod_push.md`).
2. Confirm the account running the app has write access to that share.
3. Run `python -m ems_opg.database.init_db` once against the production
   `data_root` if `database/ems_opg.db` doesn't already exist there.
4. Run `scripts/load_database.py` to import the client's MAC address pool
   if it isn't already loaded (see `docs/30_Database_Initialization.md`).
5. Start the app. Confirm `GET /api/status` reports `databaseConnected: true`.

The app binds to `127.0.0.1` only (`core/application.py`) — it is not
exposed to the network by default. How operators actually reach it (local
kiosk browser, internal reverse proxy, etc.) is a deployment decision not
yet documented here.

## Configuration

All environment-specific values live in `config/config.json` — see
`docs/07_Config_System_Design.md`. The one setting that matters most across
environments is `data_root`; everything else has reasonable defaults
already checked into the repo.

## Updates

There's no automated update mechanism. Updating means:

1. `git pull` (or deploy a new build — see Installer, below) on the machine
   running the app.
2. Stop the running instance (Ctrl+C — this triggers the shutdown backup
   automatically if `backup_on_shutdown` is enabled).
3. Re-run `python -m ems_opg.database.init_db` only if the schema changed —
   it detects an outdated schema and recreates it automatically otherwise.
4. Restart.

## Installer / Portable Version

**Not decided yet.** There is no PyInstaller spec, no build script, and no
packaging config anywhere in `pyproject.toml` — "compiling" this into a
standalone executable is not currently a defined process. Options to
evaluate:

- Bundle with PyInstaller/Nuitka into a single executable so operators
  don't need a Python install on shop-floor machines.
- Ship as a portable Python environment + the source tree.
- Require Python 3.12+ to already be present and distribute source only.

Whichever direction is chosen, this section needs to be filled in with the
actual build command and any environment-specific gotchas (e.g. the
`data_root` P: drive dependency) before it's usable as a real deployment
guide.
