# DANCERUSH STARDOM Track Annotator

Convert videos of DANCERUSH STARDOM tracks into a defined data schema.

## Stuff

### Completed:

- [x] Detect right & left notes, including position & timing
- [x] Define models based on dd & drs schemas
- [x] Fetch metadata from data store (https://arcade-songs.zetaraku.dev/drs/)
- [x] Simple BepinEx plugin to launch Dance Dash w/o VR

### To-Do:

- [ ] Detect down and jump notes (?)
- [ ] Determine final data schema
- [ ] Write tests based on total note count (https://remywiki.com/AC_DRS)

---

Setup:

- Install Python 3.10 (pyenv recommended)

- Install the required Python packages
```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

- Install pre-commit hooks
```bash
pre-commit install
```
