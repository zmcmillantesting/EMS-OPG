# EMS-OPG Action Plan

This document previously described the project in an early skeleton state —
undecided PyQt-vs-CLI interface, empty service layer, workflow engine
unconnected to anything. None of that is current. Rewritten to reflect
actual status.

## Current status summary

- **Interface decided and built**: Flask backend (`src/ems_opg/api/`)
  serving a static HTML/CSS/vanilla-JS frontend (`frontend/`) — not PyQt,
  not CLI.
- **Data layer complete**: `Order`, `Device`, `MACAddressPool`, `AuditLog`
  models; repositories for all four; services for orders, devices, and QR
  generation.
- **Workflow engine implemented**: `WorkflowEngine`/`WorkflowSession` drive
  the operator through the 6-step QR-scan test sequence, in memory,
  finalized into the database via `DeviceService.reserve_device` at
  `session_finish`.
- **Operational automation implemented this cycle**: database backup on
  shutdown (with retention pruning), a weekly standalone health-report
  script, automatic CSV export when an order finishes 100% PASS, and
  size+count-based log rotation. See `docs/09_Backup_and_Recovery.md`.
- **Test suite**: unit + integration tests across config, paths, database
  health, device/order/MAC repositories and services, QR generation and
  validation, and full end-to-end device-reservation flows. All passing as
  of this writing.

## What's genuinely still open

## What's genuinely still open

1. **The PyWebView window hasn't been visually confirmed.** Windowing
   (PyWebView) and its server (waitress) are implemented in
   `core/application.py`, gated behind a real bind test and headless
   event-wiring tests — but no environment used to build this had a
   display server, so the window actually opening/rendering/closing
   cleanly on a real machine is still unverified.

2. **Freezing into a standalone executable is still undecided.** PyWebView
   solves the native-window piece; bundling Python itself (PyInstaller,
   Nuitka, or similar) for shop-floor machines without a Python install is
   a separate, still-open decision. See `docs/11_Deployment.md`.

3. **Frontend hasn't been re-verified against the latest API changes.**
   This cycle's backend changes (automation endpoints, response shapes)
   were not cross-checked against `frontend/js/*.js` — the API surface for
   existing endpoints didn't change, but this hasn't been confirmed by
   actually exercising the UI (now inside the PyWebView window rather than
   a browser tab).

4. **Order/device cleanup (deleting old closed orders) was explicitly
   descoped.** Discussed and deliberately deferred — no age threshold or
   approval workflow has been designed yet.

5. **A few smaller inconsistencies remain** — see `docs/29_Known_Issues.md`
   for the current list (`audit_service.py`'s empty file needs a decision,
   etc.).

## Suggested priority order

1. Run the app on an actual Windows machine with the production
   `data_root` — confirm the window opens, the frontend renders and
   functions inside it, and closing the window triggers the shutdown
   backup as expected.
2. Manually exercise the full operator workflow through the running app
   (not just `pytest`) — provision an order, complete a device, confirm the
   backup/export automation actually fires as expected.
3. Decide the executable-freezing approach and write it up in
   `docs/11_Deployment.md` / `docs/15_Release_Process.md`.
4. Work through `docs/29_Known_Issues.md` as time allows.
5. Revisit order/device cleanup (item 5 from the original automation
   request) once there's a concrete retention policy to build against.
