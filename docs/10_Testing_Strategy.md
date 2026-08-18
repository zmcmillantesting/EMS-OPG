# Testing Strategy
## Rerforming Tests

We are using pytest to perform testing.

With that in mind because of environment variables the best way to run testing is by running the following terminal command.

```
python -m pytest tests/...
```
or 

```
pytest -v
```
for results on all tests (plan on automating once MVP is done)

---

## What to test

For this application every core service, config, database and logging feature must be tested indivually. 

---

## What to test

For this application every core service, config, database and logging feature must be tested indivually. 

---

## Pre-Production Database Cleanup

Before compiling/shipping, `database/ems_opg.db` and the old `backup/*.db` snapshots are still
tracked in git from early development - they carry leftover dev/test data and don't belong in
a production build. `.gitignore` only stops *new* files from being tracked; it does not untrack
files that are already committed, so these need to be removed from git's index explicitly:

```
git rm --cached database/ems_opg.db "backup/*.db"
```

Note the quotes around `backup/*.db` - without them, zsh expands the glob itself before git ever
sees it, and errors with `no matches found` if nothing in your local working copy happens to match
that pattern. Quoting it hands the raw pattern to `git rm`, which does its own matching against
everything tracked in the index (not just what's sitting on disk locally), so it works regardless
of what your local `backup/` folder currently looks like.

After that, commit the removal. The files stay in old commit history (that's fine, it's not
sensitive data) but stop being part of the working tree going forward - `database/ems_opg.db`
gets recreated automatically as a clean, empty-schema file the next time the app starts against
a `data_root` with no existing database there.

Once you're back on the production network share, also run a clean `init_db` + `load_database.py`
pass so the real production database doesn't inherit any of the dev/test MAC pool or order data
either.

---

## When in production mode:
- Dev can run `EMS_OPG_NO_WINDOW=1 python app.py` in zsh to run in developer mode which skips PyWebView and runs straight to `http:127.0.0.1:5000` if 5000 is available. Debug can be run here without disurpting production workflow
    - make sure the config is pointed at separate db as to not effect prod db
    - make sure to end web browser when not in use using `Ctrl+C` any other command can/will leave port 5000 open.

To check if port 5000 is open/running
```
lsof -i:5000
```
Use to kill port 5000
```
kill -9 <PID>
```
PID: seen when running lsof command

Example:
```
lsof -i:5000                     
COMMAND   PID      USER FD   TYPE  DEVICE SIZE/OFF NODE NAME
python  **87622** zmcmillan 7u  IPv4 1578069      0t0  TCP localhost:5000 (LISTEN)
python  **87622** zmcmillan 8u  IPv4 1558377      0t0  TCP localhost:5000->localhost:58952 (ESTABLISHED)
```