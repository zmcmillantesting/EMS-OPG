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