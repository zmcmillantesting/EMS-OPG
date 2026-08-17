# Deployment

## Development

```bash
uv sync --extra dev        # or: pip install -e ".[dev]"
python -m ems_opg.database.init_db   # first-time schema creation
python app.py                        # starts the Flask dev server on window
```

`python app.py` no longer opens a browser tab - it starts a waitress WSGI
server on a background thread and opens a native window (PyWebView)
pointing at it, sized/maximized per `config.json`'s `"window"` section
Closing the window is the shutdown trigger (see Production, below).

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

Production runs the same `python app.py` entry point. `core/application.py`
starts a **waitress** WSGI server (not Flask's dev server 00 waitress is a 
production-graed server) on a background thread, then opens a **PyWebView** 
native window pointing at it. The app is a desktop application, not somthing
operators reach through a browser. Before pointing it at read data:
1. Set `config.json`'s `data_root` to the shared network path (see
   `docs/33_Pathing_updates_pre_prod_push.md`).
2. Confirm the account running the app has write access to that share.
3. Run `python -m ems_opg.database.init_db` once against the production
   `data_root` if `database/ems_opg.db` doesn't already exist there.
4. Run `scripts/load_database.py` to import the client's MAC address pool
   if it isn't already loaded (see `docs/30_Database_Initialization.md`).
5. Start the app. Confirm `GET /api/status` reports `databaseConnected: true`.

The app still binds to `127.0.0.1` only (`core/application.py`) -- it is not
exposed to the network. The PyWebView window is the only way it's ment to be 
reached.

**Not yet verified on an actual machine with a display** -- the server and 
window-close/shutdown wiring were tested headlessly (server binding, serving
real requests, event subscription), but the native window itself requires a 
real GUI environment (WINForms/EdgeChromium on Windows, GTK/Qt on linux, Cocoa
on macOS) that isn't available in the sandbox this was built in. Confirm the window
actually opens and renders the fronend correctly, and closing it triggers the shutdown
backup, before relying on this in production.

## Configuration

All environment-specific values live in `config/config.json` — see
`docs/07_Config_System_Design.md`. The one setting that matters most across
environments is `data_root`; everything else has reasonable defaults
already checked into the repo.

## Updates

There's no automated update mechanism. Updating means:

1. `git pull` (or deploy a new build — see Installer, below) on the machine
   running the app.
2. Close the app window (This triggers the shutdown backup automatically if
`backup_on_shutdown` is enabled --startup backup, the defualt, also files the
next time it's launched regardlessf)
3. Re-run `python -m ems_opg.database.init_db` only if the schema changed —
   it detects an outdated schema and recreates it automatically otherwise.
4. Restart.

## Installer / Portable Version

**Windowing decided: PyWebView** (`webview.create_window()` +
`webview.start()`, wrapping a waitress-served Flask backend — see
`core/application.py`). **Freezing into a standalone executable is still
not decided.** PyWebView gives the native window; it doesn't bundle Python
itself into an executable. There is still no PyInstaller spec, no build
script, and no packaging config anywhere in `pyproject.toml`. Options to
evaluate for that remaining piece:

- Bundle with PyInstaller/Nuitka into a single executable so operators
 don't need a Python install on shop-floor machines. (PyWebView is
  commonly packaged this way — its own docs have guidance on bundling
  with PyInstaller specifically.)
- Ship as a portable Python environment + the source tree.
- Require Python 3.12+ to already be present and distribute source only.

Whichever direction is chosen, this section needs to be filled in with the
actual build command and any environment-specific gotchas (e.g. the
`data_root` P: drive dependency) before it's usable as a real deployment
guide.
