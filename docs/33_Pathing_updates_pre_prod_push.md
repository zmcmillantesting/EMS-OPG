# Pre-Deployment Checklist: Data Paths

This used to be a reminder to hardcode the production backup path directly
into `routes.py` before compiling. **That's no longer how this works — don't
do that.** Data paths (database, backups, logs, exports) are now fully
config-driven through `PathManager` and `config.json`'s `data_root`, so
nothing in the source needs to change between environments.

## What actually needs to happen before a production deploy

1. **Set `data_root` in `config.json`** on the target machine to the real
   shared-drive path, e.g.:

   ```json
   "data_root": "P:\\EMS_TR_PATH\\EMS_OPG"
   ```

   Leaving it blank (the repo default) keeps everything next to the local
   install, which is correct for development but not for production.

2. **Confirm the resulting layout** matches what's expected — with the
   `data_root` above, the app will create/use:

   ```
   P:\EMS_TR_PATH\EMS_OPG\
   ├── database\
   │   ├── ems_opg.db
   │   └── backups\
   ├── logs\
   └── exports\
   ```

3. **Confirm write permissions** on that share for whatever account runs the
   application — `PathManager.create_directories()` will try to create any
   of these that don't already exist, and the app will fail to start if it
   can't.

4. **Confirm `config.json`'s `backup` section** reflects what you want in
   production — `backup_on_shutdown: true` and a sane `max_backups` count.

5. Restart the app after changing `config.json` — `data_root` is resolved
   once at `PathManager.__init__`, not re-read live.

No code changes, no hardcoded paths, no per-environment branching in
`routes.py`. If you find yourself editing a path string in source to point
at the P: drive, something has regressed — `data_root` is the only place
that should change per environment.
