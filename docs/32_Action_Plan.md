# EMS-OPG Action Plan

## Current status summary

- Core application skeleton exists, but the main app entrypoint is not fully implemented.
- Configuration, path management, logging, and database initialization are present.
- Database models exist for orders, devices, MAC pool, and audit log.
- Repository and service layers are partially implemented; several files are empty or inconsistent.
- Workflow code is only a state machine skeleton; no real step generation or UI connection.
- Tests exist for configuration and database initialization, but coverage is limited.

## Key gaps to fix first

1. Align the database model and repository fields.
   - Fix the `Device` model field names to match actual business concepts.
   - Confirm whether the device should store `mac_address`, `ethaddr1_id`, or two MAC fields.
   - Ensure `Order` and `Device` relationships are correct and queryable.

2. Correct repository implementations.
   - `DeviceRepository` has invalid queries and inconsistent field names.
   - `OrderRepository` needs list/search methods, not just create and delete.
   - `AuditRepository` is empty and must support audit log creation.
   - `MacAddressRepository` is mostly good but should be verified with the final model shape.

3. Fill in service layer behavior.
   - Implement `OrderService`, `AuditService`, and complete `DeviceService`.
   - Add transactional safety and meaningful error handling.
   - Implement `QRService` fully so it generates commands and QR payloads.

4. Implement the application startup and workflow integration.
   - Build `core/application.py` to load config, paths, logger, DB, and startup logic.
   - Connect `startup.py` to the real application lifecycle.
   - Use `WorkflowEngine` and `WorkflowSession` to manage selected order/device state and step progress.

5. Implement the user-facing workflow/UI layer.
   - Decide whether the final interface is PyQt or CLI, then implement the main screens.
   - Add order selection, device assignment, MAC assignment, QR display, and completion flow.
   - Add operator capture and audit logging for each important action.

## Recommended next steps

### Step 1: Stabilize the data layer
- Review and fix the `src/ems_opg/database/models.py` device schema.
- Update repositories so they use the actual model fields.
- Add missing methods for search, list, and availability.
- Add audit repository methods.

### Step 2: Complete services and core application wiring
- Implement `src/ems_opg/services/order_service.py`, `audit_service.py`, and `device_service.py`.
- Complete `src/ems_opg/services/qr_service.py` with QR payload generation.
- Build `src/ems_opg/core/application.py` with config, paths, logger, and database manager.
- Use `WorkflowEngine` for actual workflow state transitions.

### Step 3: Implement the workflow and UI flow
- Add operator login / identity capture.
- Add order search and selection.
- Add device selection and MAC allocation.
- Display QR codes for each test step and save traceability data.
- Ensure the app records audit events on save, update, and backup.

### Step 4: Add tests and validation
- Add unit tests for repository search/list methods.
- Add service tests for device reservation and order creation.
- Add integration tests for workflow flows and database state.
- Continue using `python -m pytest tests/...`.

### Step 5: Polish documentation and release readiness
- Update `docs/04_Project_Structure.md` with actual module responsibilities.
- Update `docs/06_UI_UX_Guidelines.md` and `docs/22_User_Manual.md` to match the implemented workflow.
- Add a short release checklist: config verification, DB schema, audit logging, backup, test run.

## Suggested priority order

1. Fix data model and repository issues.
2. Implement core services and app initialization.
3. Build workflow state handling and QR generation.
4. Add the user interface or interaction layer.
5. Add tests, logging, backup, and final documentation updates.

## Useful immediate actions

- Open `src/ems_opg/database/models.py` and resolve the MAC field naming.
- Open `src/ems_opg/repositories/device_repository.py` and correct query logic.
- Open `src/ems_opg/core/application.py` and implement app bootstrap steps.
- Add at least one repository/service unit test before adding UI code.

## Long-term completion checklist

- [ ] Database schema matches traceability model.
- [ ] Repositories are stable and tested.
- [ ] Services encapsulate business rules correctly.
- [ ] Workflow engine drives the app state.
- [ ] QR generation works and is testable.
- [ ] Application UI or interaction flow is complete.
- [ ] Backup and audit logging are implemented.
- [ ] Documentation reflects actual behavior.
- [ ] End-to-end tests verify the operator workflow.
