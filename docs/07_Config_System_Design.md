# Configuration System Design Guide

**Document Version:** 2.0 — rewritten to describe the system as it actually
exists, not as originally planned. The previous version of this document
described a schema/validation/defaults layer that was never built; if you're
looking for that design, it doesn't exist in the current codebase.

---

# Purpose

This document explains how the application's configuration system actually
works today: where settings live, how they're loaded, and how to add a new
setting.

---

# What actually exists

Configuration is two pieces:

| Component | Responsibility |
|---|---|
| `config/config.json` | The single JSON file holding every runtime setting |
| `src/ems_opg/config/config_manager.py` (`ConfigurationManager`) | Loads, saves, and exposes that file's contents |

There is **no schema, no validation, no default-value fallback file, and no
per-section config model classes**. `ConfigurationManager` is a thin wrapper:

```python
class ConfigurationManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self._config = {}
        self.load()

    def load(self):
        with open(self.config_path, "r") as file:
            self._config = json.load(file)

    def save(self):
        with open(self.config_path, "w") as file:
            json.dump(self._config, file, indent=4)
```

Everything else on it is a `@property` returning a raw dict straight out of
`self._config` — `.application`, `.database`, `.logging`, `.backup`,
`.paths`, `.workflow`, `.window`, plus a couple of QR-command helper methods
(`get_qr_command`, `get_workflow`, `format_qr_command`) used by `QRService`.

**Consequences of this being unvalidated:**

- A missing key raises a plain `KeyError` wherever it's accessed, not a
  friendly config error.
- `config.json` must be syntactically valid JSON — no comments, no trailing
  commas. Standard `json.load()` is strict about this, and a broken file
  crashes `Application.__init__` immediately (this has happened in practice
  — see `docs/29_Known_Issues.md`).
- Code that reads a key with `.get("key", default)` (e.g. `Shutdown`,
  `backup_database()`) tolerates that key being absent; code that does
  `config.logging["level"]` does not.

---

# Where config is read

`Application.__init__` creates one `ConfigurationManager` for the process
and passes it (and `PathManager`) into `Logger`. Beyond that, individual
routes and `Shutdown` reach `application.config.<section>` directly — there
is no dependency-injection layer routing config to just the modules that
need it. In practice:

- `Logger`/`LoggerManager` reads `config.logging`.
- `Shutdown.backup_database()` reads `config.backup`.
- `api/routes.py`'s `/api/database/backup` route reads
  `application.config.backup.get("max_backups", 5)`.
- `QRService` reads `config.get_qr_command(...)` / `config.get_workflow(...)`.

---

# `data_root` — the one setting with real behavioral weight

`config.json`'s top-level `"data_root"` key is read once by
`PathManager._resolve_data_root()`. If set to an absolute path, every data
directory (`database/`, `logs/`, `database/backups/`, `exports/`, `cache/`)
is created under it instead of next to the app install — this is how the
app supports "app on C:, data on a shared P: drive" without any code
changes. See `docs/33_Pathing_updates_pre_prod_push.md`.

---

# How to add a new configuration setting

1. Add the key (with a sensible value) to `config/config.json`.
2. If it needs a fallback when absent, read it with
   `application.config.<section>.get("key", default)` rather than `[...]`.
3. If it belongs to a section that doesn't have a `ConfigurationManager`
   property yet, add one — a one-line `@property` returning
   `self._config["section"]`.
4. Use it via `application.config`, not by opening `config.json` directly
   from a new module.
5. Update this document and, if it changes visible behavior, whichever
   feature doc it affects (e.g. `09_Backup_and_Recovery.md`).

---

# Rules that still hold

- Don't read `config.json` outside `ConfigurationManager` — everything
  should go through `application.config`.
- Don't hardcode a value in source that's meant to vary by deployment
  (`data_root` is the existing example of getting this right).
- `config.json` must stay strictly valid JSON. If your editor's linter
  doesn't flag trailing commas or comments in `.json` files, double-check
  by hand before committing — `json.load()` will not forgive either.

# Future possibilities, not current behavior

The original version of this document described schema validation, a
`config.default.json` fallback, and typed config objects
(`ReportsConfig`-style). None of that exists today. It's a reasonable
direction if `config.json` grows enough sections that silent `KeyError`s
become a real problem — but until it's actually built, don't treat it as
documentation of current behavior.
