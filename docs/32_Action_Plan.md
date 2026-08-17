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

1. **Production `data_root` is not yet set.** The app currently defaults to
   storing everything next to the local install. Before real deployment,
   `config.json`'s `data_root` needs to point at the actual shared drive
   path. See `docs/33_Pathing_updates_pre_prod_push.md`.

2. **Packaging/installer process is undecided.** There is no PyInstaller
   spec, build script, or other packaging config anywhere in the repo —
   `docs/11_Deployment.md` and `docs/15_Release_Process.md` previously had
   no real content either. A decision is needed on how this actually gets
   onto shop-floor machines (bundled executable vs. requiring a Python
   install vs. something else) before "compiling" is a well-defined step.

3. **Frontend hasn't been re-verified against the latest API changes.**
   This cycle's backend changes (automation endpoints, response shapes)
   were not cross-checked against `frontend/js/*.js` — the API surface for
   existing endpoints didn't change, but this hasn't been confirmed by
   actually exercising the UI.

4. **Order/device cleanup (deleting old closed orders) was explicitly
   descoped.** Discussed and deliberately deferred — no age threshold or
   approval workflow has been designed yet.

5. **A few smaller inconsistencies remain** — see `docs/29_Known_Issues.md`
   for the current list (duplicate/dead version constants, unimplemented
   `backup_on_startup` flag, empty `audit_service.py`, etc.).

## Suggested priority order

1. Set and verify `data_root` against the real shared-drive path; confirm
   the app boots and writes to it correctly end-to-end.
2. Manually exercise the full operator workflow through the running app
   (not just `pytest`) — provision an order, complete a device, confirm the
   backup/export automation actually fires as expected.
3. Decide the packaging/installer approach and write it up in
   `docs/11_Deployment.md` / `docs/15_Release_Process.md`.
4. Work through `docs/29_Known_Issues.md` as time allows.
5. Revisit order/device cleanup (item 5 from the original automation
   request) once there's a concrete retention policy to build against.
