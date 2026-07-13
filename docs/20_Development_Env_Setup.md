# EMS-OPG Development Environment Setup

## Overview

This document describes how to configure a development environment for the EMS-OPG project.

The goal is to ensure every developer has the same:

* Python version
* Virtual environment configuration
* Project dependencies
* Testing tools
* Development utilities
* Environment variables

Developers should **not install individual Python packages manually**. All dependencies are managed through the project's `pyproject.toml` file.

---

# 1. System Requirements

## Required Software

Before starting, install:

* Git
* Python 3.12+
* pip
* A code editor (recommended: VS Code, PyCharm, or equivalent)

Verify installations:

```bash
git --version
```

```bash
python --version
```

```bash
pip --version
```

Expected:

```text
Python 3.12.x or newer
pip 24.x or newer
```

---

# 2. Clone the Repository

Clone the EMS-OPG repository:

```bash
git clone <repository-url>
```

Navigate into the project:

```bash
cd EMS-OPG
```

The project root should contain:

```text
EMS-OPG/
├── pyproject.toml
├── src/
├── tests/
├── docs/
└── README.md
```

---

# 3. Create a Python Virtual Environment

A virtual environment isolates project dependencies from the developer's global Python installation.

## Linux / WSL

Create the environment:

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

---

## Windows PowerShell

Create the environment:

```powershell
python -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

Successful activation should show:

```text
(.venv)
```

at the beginning of the terminal prompt.

Example:

```text
(.venv) PS C:\EMS-OPG>
```

---

# 4. Upgrade pip

Before installing dependencies:

```bash
python -m pip install --upgrade pip
```

Verify:

```bash
pip --version
```

---

# 5. Install EMS-OPG Dependencies

EMS-OPG uses `pyproject.toml` to manage dependencies.

Install the project and development tools:

```bash
pip install -e ".[dev]"
```

This installs:

## Application Dependencies

* qrcode
* pillow

## Development Dependencies

* pytest
* pytest-cov
* black
* ruff

The `-e` flag installs the project in editable mode.

This means changes made inside:

```text
src/ems_opg/
```

are immediately available without reinstalling.

---

# 6. Verify Installation

Confirm the package is installed:

```bash
pip list | grep ems
```

Expected:

```text
ems-opg    0.1.0
```

Verify pytest:

```bash
pytest --version
```

Expected:

```text
pytest x.x.x
```

---

# 7. Verify Python Package Imports

EMS-OPG uses a `src` package layout.

The correct import format is:

```python
from ems_opg.app_logging.logger import Logger
```

Do not use:

```python
from src.ems_opg.app_logging.logger import Logger
```

or:

```python
from logging.logger import Logger
```

The package name is:

```text
ems_opg
```

not:

```text
src
```

---

# 8. Running Tests

All tests should be executed from the project root:

```bash
pytest
```

Verbose output:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest tests/integration/logging_verification.py
```

Run a specific test:

```bash
pytest tests/integration/logging_verification.py::test_logger_creation
```

---

# 9. Code Quality Tools

## Formatting

EMS-OPG uses Black for consistent formatting.

Run:

```bash
black .
```

---

## Static Analysis

EMS-OPG uses Ruff for linting.

Run:

```bash
ruff check .
```

---

# 10. Environment Variables

Environment-specific settings should not be committed into source control.

Create a local environment file:

```text
.env
```

Example:

```env
EMS_OPG_ENV=development
DATABASE_URL=sqlite:///development.db
LOG_LEVEL=DEBUG
```

Each developer should maintain their own `.env` file.

Never commit:

```text
.env
```

to Git.

---

# 11. Project Configuration Files

The following files control the development environment:

| File                                | Purpose                                       |
| ----------------------------------- | --------------------------------------------- |
| `pyproject.toml`                    | Python package configuration and dependencies |
| `.gitignore`                        | Files excluded from Git                       |
| `.env`                              | Developer-specific environment variables      |
| `pytest.ini` / pytest configuration | Test execution settings                       |
| `docs/`                             | Development documentation                     |

---

# 12. Troubleshooting

## Import Error

Example:

```text
ModuleNotFoundError: No module named 'ems_opg'
```

Solution:

Verify the virtual environment is active:

```bash
which python
```

Then reinstall:

```bash
pip install -e ".[dev]"
```

---

## pytest Cannot Find Tests

Make sure you are running from the project root:

Correct:

```bash
cd EMS-OPG
pytest
```

Incorrect:

```bash
cd tests
pytest
```

---

## Dependency Problems

If dependencies become corrupted:

Deactivate:

```bash
deactivate
```

Remove the environment:

Linux / WSL:

```bash
rm -rf .venv
```

PowerShell:

```powershell
Remove-Item -Recurse -Force .venv
```

Recreate:

```bash
python -m venv .venv
```

Activate and reinstall:

```bash
pip install -e ".[dev]"
```

---

# 13. Developer Setup Checklist

Before beginning development, verify:

* [ ] Repository cloned
* [ ] Python 3.12+ installed
* [ ] Virtual environment created
* [ ] Virtual environment activated
* [ ] pip upgraded
* [ ] Dependencies installed with `pip install -e ".[dev]"`
* [ ] EMS-OPG package import works
* [ ] pytest executes successfully
* [ ] Environment variables configured
* [ ] Code formatting tools available

---

# Summary

A new developer should only need to run:

```bash
git clone <repository-url>

cd EMS-OPG

python -m venv .venv

source .venv/bin/activate     # Linux/WSL
# OR
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

pip install --upgrade pip

pip install -e ".[dev]"

pytest
```

After completing these steps, the developer environment should match the EMS-OPG development standard.
