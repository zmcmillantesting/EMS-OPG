# Deployment

## Development

```bash
uv sync --extra dev        # or: pip install -e ".[dev]"
python -m ems_opg.database.init_db   # first-time schema creation
python app.py                        # opens the app in a native window
```

`python app.py` no longer opens a browser tab -- it starts a waitress WSGI
server on a background thread and opens a native window (PyWebView)
pointing at it, sized/maximized per `config.json`'s `"window"` section.
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
production-grade server) on a background thread, then opens a **PyWebView** 
native window pointing at it. The app is a desktop application, not something
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
exposed to the network. The PyWebView window is the only way it's meant to be 
reached.

**Not yet verified on an actual machine with a display** -- the server and 
window-close/shutdown wiring were tested headlessly (server binding, serving
real requests, event subscription), but the native window itself requires a 
real GUI environment (WinForms/EdgeChromium on Windows, GTK/Qt on linux, Cocoa
on macOS) that isn't available in the sandbox this was built in. Confirm the window
actually opens and renders the frontend correctly, and that the shutdown closing it triggers the shutdown
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
2. Close the app window (this triggers the shutdown backup automatically if
`backup_on_shutdown` is enabled -- startup backup, the default, also fires the
next time it's launched regardless)
3. Re-run `python -m ems_opg.database.init_db` only if the schema changed —
   it detects an outdated schema and recreates it automatically otherwise.
4. Restart.

## Installer / Portable Version

**Windowing: PyWebView** (`webview.create_window()` + `webview.start()`,
wrapping a waitress-served Flask backend — see `core/application.py`).
**Freezing: PyInstaller, `--onedir` (not `--onefile`)** — `EMS-OPG.spec` at
the project root, with `pyinstaller` in the `dev` extras of `pyproject.toml`.

Build on Windows (PyInstaller cannot cross-compile) with the venv active,
from the project root:

```powershell
uv sync --extra dev
uv run pyinstaller EMS-OPG.spec
```

This produces `dist\EMS-OPG\` — the whole folder is the app (the exe plus
the Python runtime, `frontend/`, `config/`, `assets/`, and PyWebView's
Windows backend DLLs, all bundled flat next to the exe via
`contents_directory="."` on `EXE()` in the spec — PyInstaller 6+ otherwise
nests all of this under an `_internal\` subfolder, which
`PathManager.root`'s `sys.frozen` resolution doesn't look inside).
`database/`, `logs/`, `cache/`, `exports/`, and `backup/` are deliberately
*not* bundled — those get created fresh on first run, wherever `data_root`
in the bundled `config.json` points.

`dist\EMS-OPG\` itself isn't meant to be handed to an operator directly.
Run the installer script afterward to move it to a clean per-user location
and drop a single shortcut on the Desktop, rather than leaving the whole
runtime folder there:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_windows.ps1
```

This moves the build to `%LOCALAPPDATA%\Programs\EMS-OPG\` and creates
`EMS-OPG.lnk` on the Desktop pointing at the exe inside it. Re-running the
script replaces a previous install cleanly.

**Before compiling**, double-check `config/config.json`'s `data_root`
points at the real production UNC path (e.g.
`\\emsfs01\production\EMS_TR_PATH\OpenGear\`) — it gets baked into the
build as-is, and a UNC path is required specifically because mapped drive
letters (`P:\`) are per-user-session and may not be visible to a process
launched under a different context.

**Before compiling**, double-check `config/config.json`'s `data_root`
points at the real production UNC path (e.g.
`\\emsfs01\production\EMS_TR_PATH\OpenGear\`) — it gets baked into the
build as-is, and a UNC path is required specifically because mapped drive
letters (`P:\`) are per-user-session and may not be visible to a process
launched under a different context.

## USB Deployment to Shop-Floor Machines

Windows disabled AutoRun for USB/removable drives back in Windows 7 (it
was one of the most common malware infection vectors), so a drive that
installs itself the instant it's plugged in isn't something to build or
re-enable. `install.bat` at the project root is the practical equivalent:
double-click it and it runs the installer for you, no typed commands.

To build a USB drive that installs with one double-click:

1. Build once: `uv run pyinstaller EMS-OPG.spec` (produces `dist\EMS-OPG\`).
2. Copy these three things onto the USB drive, keeping them in the same
   relative layout as the project root:
   ```
   USB:\
     install.bat
     scripts\
       install_windows.ps1
     dist\
       EMS-OPG\        (the full build output)
   ```
3. On the target machine: plug in the drive, open it, double-click
   `install.bat`. It installs to `%LOCALAPPDATA%\Programs\EMS-OPG\` and
   creates the Desktop shortcut, same as running the PowerShell script
   directly — `install.bat` just wraps that same script (with
   `-ExecutionPolicy Bypass` baked in) so nobody has to type PowerShell
   commands or fight execution-policy prompts on each machine.

Re-running `install.bat` on a machine that already has EMS-OPG installed
cleanly replaces the previous install (same behavior as the underlying
script). Nothing about this requires internet access or admin rights on
the target machine — it's a plain per-user file copy plus a shortcut.
