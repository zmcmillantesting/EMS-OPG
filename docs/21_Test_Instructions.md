# Test Instructions

## Purpose

This document explains how to run EMS-OPG tests and how to verify that the test environment is configured correctly.

These instructions are intended for developers and QA engineers who need to run the project test suite and understand the test workflow.

---

## How the tests work briefly

* `tests/integration/` verifies how major components work together, such as database access, configuration loading, logging, and filesystem paths.
* `tests/unit/` exercises individual functions and classes in isolation to catch logic bugs quickly.
* `tests/performance/` measures behavior under load or generates artifacts like barcodes, and may skip when optional dependencies are not installed.
* `tests/ui/` covers user interface behavior and workflow steps when UI tests are present.
* `tests/conftest.py` provides shared pytest setup, import path configuration, and fixtures used across tests.

---

## 1. Prerequisites

Before running tests, make sure the following are installed:

* Python 3.12 or newer
* pip
* A supported terminal environment
* Git

The project uses the `src` layout and a local Python virtual environment.

---

## 2. Set up the Python environment

### 2.1 Create a virtual environment

From the project root (`/home/zmcmillan/EMS-OPG`):

Linux / WSL:

```bash
python3 -m venv .venv
```

Windows PowerShell:

```powershell
python -m venv .venv
```

### 2.2 Activate the virtual environment

Linux / WSL:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

When activation succeeds, the prompt will show `(.venv)`.

### 2.3 Install dependencies

Install the project and dev dependencies from `pyproject.toml`:

```bash
pip install -e ".[dev]"
```

This installs:

* Application dependencies: `qrcode`, `pillow`, `SQLAlchemy`
* Development dependencies: `pytest`, `pytest-cov`, `black`, `ruff`

---

## 3. Run the tests

### 3.1 Run a single test file

To run a single integration test file:

```bash
pytest tests/integration/test_database.py -q
```

### 3.2 Run the full test suite

To run all tests in the repository:

```bash
pytest -q
```

### 3.3 Run tests with coverage

If `pytest-cov` is installed:

```bash
pytest --cov=src -q
```

### 3.4 Run a single test function

Use the `-k` option to select a specific test by keyword:

```bash
pytest -q -k "test_database_script"
```

---

## 4. Environment notes

* Always activate the local `.venv` before running tests.
* The repository includes a WSL-friendly layout, so using WSL is recommended on Windows.
* If the tests cannot import `src.ems_opg`, verify that the test run is started from the project root and the virtual environment is active.

---

## 5. Common test files

The main test folders are:

* `tests/integration/` — integration tests for database, configuration, logging, and paths
* `tests/unit/` — unit tests for isolated code paths
* `tests/performance/` — performance-oriented tests
* `tests/ui/` — UI tests (if present)

Key integration test files include:

* `tests/integration/test_database.py`
* `tests/integration/test_config.py`
* `tests/integration/test_paths.py`
* `tests/integration/test_logging.py`

---

## 6. Handling failures

If a test run fails:

1. Read the pytest output for the failing module and stack trace.
2. Confirm the virtual environment is active.
3. Confirm you are running pytest from the project root.
4. If a dependency is missing, install it from `pyproject.toml` or use:

```bash
pip install -e ".[dev]"
```

Common errors:

* `ModuleNotFoundError: No module named 'src'` — usually caused by running tests outside the project root or without the virtual environment.
* Missing optional dependencies like `segno` for barcode tests — these tests may be skipped if the package is not installed.

---

## 7. Recommended workflow

1. Activate the `.venv`.
2. Run `pytest -q` to confirm the full suite.
3. If there are failures, run the specific failing file or function.
4. Fix the issue.
5. Re-run the full suite.

---

## 8. Notes for reviewers

* The project uses `tests/conftest.py` to configure test import paths and shared fixtures.
* Running tests in WSL is generally the most reliable option on Windows.
* If a test uses database objects, verify that the in-memory database session fixture is configured correctly.

---

## 9. Useful commands

```bash
source .venv/bin/activate
pytest -q
pytest tests/integration/test_database.py -q
pytest --cov=src -q
```