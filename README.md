# DANCERUSH STARDOM to Dance Dash

Convert videos of DANCERUSH STARDOM tracks into Dance Dash beat maps

Curious? @thomasasfk on discord or join [drs2dd](https://discord.gg/JVWx6zmtft) and ask!

## Stuff

### Completed:

- Video converter:
  - [x] Detect right & left notes, including position & timing
  - [x] Define models based on dd & drs schemas
  - [x] Fetch metadata from data store (https://arcade-songs.zetaraku.dev/drs/)
  - [x] Simple BepinEx plugin to launch Dance Dash w/o VR

- Parser
  - [x] Parse XML files into JSON files
  - [x] Parse JSON files into DD info metadata
  - [x] Create DD beat map folder structure with song & cover

### To-Do:

- Video converter (don't know if we'll even do this now...)
  - [ ] Detect down and jump notes (?)
  - [ ] Detect hold notes (? hard)
  - [ ] Write tests based on total note count (?) (https://remywiki.com/AC_DRS)
  - [ ] Generate other metadata json file

- Parser
  - [ ] Actually parse notes & lines into DD beat map
  - [ ] Parse down and jump notes into DD beat map
  - [ ] Test folder structure, sort bmp, note speed, order, etc.

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

Convert a DRS track video to a DD beat map

```bash
# grab video of DRS track from youtube
yt-dlp -f bv[ext=webm] https://youtu.be/o7I0scmptmo -o "drs_video.webm"

# grab song-id from "resources\data.json" or https://arcade-songs.zetaraku.dev/drs/
.venv/Scripts/python drsvideo2dd.py "drs_video.webm" --song-id "BOOMBAYAH-JP Ver.-"
```

Generate json files from xml files (needs xml files and a brave soul)

```bash
HAS_XML=1 .venv/Scripts/python drsxml2json.py
```

Generate full DD Beat Map from json files in repository (does not map notes atm, todo)

```bash
.venv/Scripts/python drs2dd.py --song-id 187
```
