# DANCERUSH STARDOM to Dance Dash

Convert data of [DANCERUSH STARDOM](https://remywiki.com/AC_DRS) tracks into [Dance Dash](https://store.steampowered.com/app/2005050/Dance_Dash/) beat maps

Curious? @thomasasfk on discord

### Download the tracks here:

- https://mega.nz/file/KbB1DSjb#_sepIa5KmyWVChnCMyaZxqztzQuXXDI3AMgXEdpR7-8 (all songs)

---

### How do I install these?

- Right click Dance Dash on Steam
- Manage > Browse local files (will open explorer)
- Drag `DANCERUSH_STARDOM.zip` into the folder
- Right click > Extract Here (7zip)

Note, if you don't use 7zip - you may need to drag the folder manually.

Target directory for Custom Albums is: `steamapps\common\Dance Dash\Dance Dash_Data\StreamingAssets\NewDLC`


---

### Setup:

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

### Usage:

Generate json files from xml files (needs xml files and a brave soul)

```bash
HAS_XML=1 .venv/Scripts/python drsxml2json.py
```

Generate full DD Beat Map from json files in repository (no --song-id does all)

```bash
.venv/Scripts/python drs2dd.py --song-id 187
```

Generate full DD Beat Map from Feet Saber directory (WIP)

```bash
# WIP when I have time.  https://beatsaver.com/maps/229ed is what i've been using to test.
.venv/Scripts/python fs2dd.py --fs-map-dir "229ed (Yell! (DJ Shimamura Remix) [feat. Moimoi] [Feet saber] - KikaeAeon)"
```

### Feet Saber TODO:

- Map 1-9 x position of notes (model/feetsaber.py:213)
- Map timings and logic for line notes (fs2dd.py:74)