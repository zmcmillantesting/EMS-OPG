# Configuration System Design Guide

**Document Version:** 1.0

---

# Purpose

This document explains how the application's configuration system is designed, how configuration data flows through the application, and the correct procedure for adding or modifying configuration values.

The goal of this design is to provide a **single source of truth** for application settings while keeping configuration data separate from application code.

---

# Design Philosophy

The configuration system is divided into two parts:

1. **Configuration Data**
2. **Configuration Manager**

These two components have different responsibilities.

| Component                      | Responsibility                                                                  |
| ------------------------------ | ------------------------------------------------------------------------------- |
| `config/config.json`           | Stores configuration values                                                     |
| `src/config/config_manager.py` | Reads, validates, manages, and provides configuration values to the application |

The configuration file contains **only data**.

The Configuration Manager contains **all configuration logic**.

---

# Directory Structure

```
Project/

├── config/
│   ├── config.default.json
│   ├── config.json
│   └── README.md
│
├── src/
│   └── config/
│       ├── __init__.py
│       ├── config_manager.py
│       ├── defaults.py
│       └── schema.py
```

---

# Responsibilities

## config/config.json

This file stores runtime settings.

Examples include:

* Database filename
* Logging level
* Backup settings
* Window size
* Workflow options

This file should never contain Python code.

---

## src/config/config_manager.py

The Configuration Manager is responsible for:

* Loading the configuration file
* Validating configuration values
* Providing default values
* Saving configuration changes
* Exposing configuration to the rest of the application

No other module should read the JSON file directly.

---

# Configuration Workflow

```
Application Starts
        │
        ▼
ConfigurationManager Created
        │
        ▼
Locate config/config.json
        │
        ▼
Does file exist?
        │
   ┌────┴────┐
   │         │
  Yes        No
   │         │
   ▼         ▼
Load JSON   Copy config.default.json
   │         │
   └────┬────┘
        ▼
Validate Configuration
        │
        ▼
Load Into Memory
        │
        ▼
Provide Configuration To
Logger
Database
Workflow Engine
UI
Services
```

The configuration file is read once during application startup.

After that, every component accesses configuration through the Configuration Manager.

---

# Correct Usage

## Correct

```
Logger

↓

ConfigurationManager

↓

config.logging.level
```

```
Database

↓

ConfigurationManager

↓

config.database.filename
```

Every subsystem requests configuration through the manager.

---

## Incorrect

```
Logger

↓

Open config.json
```

```
Database

↓

Open config.json
```

```
Workflow

↓

Open config.json
```

No module other than the Configuration Manager should read the configuration file.

---

# Why This Architecture?

Using a Configuration Manager provides several advantages.

## Single Source of Truth

Every component receives configuration from one location.

This prevents duplicate configuration logic throughout the application.

---

## Easier Maintenance

Changing the configuration file format only requires changes inside the Configuration Manager.

The remainder of the application remains unchanged.

---

## Validation

The Configuration Manager validates settings before the application begins running.

Invalid values can be corrected or replaced with defaults before they cause runtime failures.

---

## Testing

Tests can provide custom configurations without modifying production settings.

This allows unit and integration tests to run in isolated environments.

---

## Future Expansion

The application may eventually support:

* YAML
* TOML
* Environment Variables
* Encrypted Configuration
* Remote Configuration

Because the rest of the application communicates only with the Configuration Manager, these changes can be implemented without modifying business logic.

---

# How To Add A New Configuration Setting

Whenever a new configuration option is introduced, follow this process.

## Step 1

Add the new value to:

```
config.default.json
```

Example:

```json
"reports":
{
    "auto_export": true
}
```

---

## Step 2

Update the Configuration Manager.

Create or update the appropriate configuration model.

Example:

```
ReportsConfig
```

---

## Step 3

Expose the new configuration through the Configuration Manager.

Example:

```
config.reports.auto_export
```

---

## Step 4

Use the Configuration Manager inside the application.

Correct:

```python
report_service.initialize(config.reports)
```

Incorrect:

```python
with open("config/config.json") as file:
    ...
```

---

## Step 5

Update documentation.

If the configuration affects application behavior, update:

* Requirements Specification
* Configuration Guide
* User Documentation (if applicable)

---

# Rules For Developers

The following rules should always be followed.

### Rule 1

Never read `config.json` outside of the Configuration Manager.

---

### Rule 2

Never hardcode configurable values inside application code.

Incorrect:

```python
LOG_LEVEL = "INFO"
```

Correct:

```python
config.logging.level
```

---

### Rule 3

Every new configuration option must have a default value.

---

### Rule 4

Configuration validation belongs inside the Configuration Manager.

Validation should not be duplicated throughout the application.

---

### Rule 5

Application modules should only know about the settings they require.

For example:

* Logger receives logging configuration.
* Database receives database configuration.
* Workflow Engine receives workflow configuration.

This reduces coupling between modules.

---

# Summary

The Configuration Manager acts as the application's single interface to configuration.

```
config.json
      │
      ▼
ConfigurationManager
      │
      ├── Logger
      ├── Database
      ├── Backup Manager
      ├── Workflow Engine
      ├── UI
      └── Services
```

The configuration file stores data.

The Configuration Manager provides behavior.

Keeping these responsibilities separate results in a system that is easier to maintain, easier to test, and easier to extend as the application grows.
