# DANCERUSH STARDOM to Dance Dash

Convert videos of DANCERUSH STARDOM tracks into Dance Dash beat maps

## Stuff

### Completed:

- [x] Detect right & left notes, including position & timing
- [x] Define models based on dd & drs schemas
- [x] Fetch metadata from data store (https://arcade-songs.zetaraku.dev/drs/)
- [x] Simple BepinEx plugin to launch Dance Dash w/o VR

### To-Do:

- [ ] Detect down and jump notes (?)
- [ ] Detect hold notes (? hard)
- [ ] Write tests based on total note count (?) (https://remywiki.com/AC_DRS)
- [ ] Generate other metadata json file

---

Setup:

- Install Python 3.10 (pyenv recommended)

- Install the required Python packages
```bash
python -m venv .venv
. .venv/bin/activate # or .venv\Scripts\activate.bat on Windows
python -m pip install -r requirements.txt
```

- Install pre-commit hooks
```bash
pre-commit install
```

---

Usage:

```bash
# grab video of DRS track from youtube
yt-dlp -f bv[ext=webm] https://youtu.be/o7I0scmptmo -o "drs_video.webm"

# grab song-id from "resources\data.json" or https://arcade-songs.zetaraku.dev/drs/
.venv/Scripts/python drsvideo2dd.py "drs_video.webm" --song-id "BOOMBAYAH-JP Ver.-"
```

```bash
# you will need relevant xml files (not from DRS, that's illegal...)
.venv/Scripts/python drsxml2drsjson.py
```
