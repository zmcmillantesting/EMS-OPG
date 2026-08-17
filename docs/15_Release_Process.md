# Release Process

This is currently a lightweight process — there's no CI/CD pipeline, no
packaging step, and no code signing configured. Documented here as it
actually exists, with gaps called out rather than invented.

## Version Number

**Currently inconsistent — needs to be consolidated before this section
means anything.** As of this writing there are two different version
strings live in the codebase:

- `pyproject.toml` → `version = "0.1.0"`
- `src/ems_opg/core/constants.py` → `APP_VERSION = "0.1.0"` (this is the
  one actually served by `GET /api/status`)
- `src/ems_opg/core/version.py` → a separate, unused `Version(1, 0, 0)`
  dataclass
- `config/config.json` → `application.version = "1.0.0"`

Pick one source of truth (`pyproject.toml` is the conventional place) and
either delete the others or have them import from it. See
`docs/29_Known_Issues.md`.

## Testing

`uv run pytest` must pass before any release. There is no separate release
test suite — the same integration/unit tests that run in development are
the release gate.

## Packaging

Not yet defined — see `docs/11_Deployment.md`'s Installer section. No build
artifact is currently produced; releases today mean "the git history at
this commit," not a built package.

## Signing

Not applicable yet — no distributable binary exists to sign.

## Deployment

Manual — see `docs/11_Deployment.md`'s Updates section (`git pull`, stop,
re-init schema if needed, restart).

## Rollback

There is no automated rollback. In practice: `git checkout` the previous
commit/tag, and if the schema changed, restore the appropriate database
backup from `database/backups/` (see `docs/09_Backup_and_Recovery.md`) —
`init_db.py`'s automatic schema-recreation is destructive (`DROP` +
`CREATE`), so rolling back a schema change requires restoring data from a
backup taken before the change, not just reverting code.

## Release Notes

Not currently tracked anywhere (no CHANGELOG). Worth starting one once the
version-number inconsistency above is resolved.
