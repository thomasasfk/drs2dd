# DANCERUSH STARDOM to Dance Dash

Convert data of [DANCERUSH STARDOM](https://remywiki.com/AC_DRS) tracks into [Dance Dash](https://store.steampowered.com/app/2005050/Dance_Dash/) beat maps

Curious? @thomasasfk on discord

## Quick Start (Players)

### Download the tracks here:
- https://mega.nz/file/KbB1DSjb#_sepIa5KmyWVChnCMyaZxqztzQuXXDI3AMgXEdpR7-8 (all songs)

### How to Install:
1. Right click Dance Dash on Steam
2. Click Manage > Browse local files (will open explorer)
3. Drag `DANCERUSH_STARDOM.zip` into the folder
4. Right click > Extract Here (7zip)

Note: If you don't use 7zip, you may need to drag the folder manually.

Target directory for Custom Albums is: `steamapps\common\Dance Dash\Dance Dash_Data\StreamingAssets\NewDLC`

---

## Development Setup (Only needed if modifying/creating beat maps)

If you just want to play the songs, you can ignore everything below this section. The following instructions are only necessary if you want to modify existing beat maps or create new ones.

### Prerequisites:
- Python 3.10 (pyenv recommended)

### Install Development Dependencies:
```bash
python -m venv .venv
. .venv/bin/activate # or .venv\Scripts\activate.bat on Windows
python -m pip install -r requirements.txt
```

### Install pre-commit hooks:
```bash
pre-commit install
```

### Development Usage:

Generate json files from xml files (needs xml files):
```bash
HAS_XML=1 .venv/Scripts/python drsxml2json.py
```

Generate full DD Beat Map from json files in repository (no --song-id does all):
```bash
.venv/Scripts/python drs2dd.py --song-id 187
```

Generate full DD Beat Map from Feet Saber directory (WIP):
```bash
.venv/Scripts/python fs2dd.py --fs-map-dir "path/to/map/folder"
.venv/Scripts/python fs2dd.py --fs-map-id 229ed
.venv/Scripts/python fs2dd.py --fs-map-ids 229ed,299b5
.venv/Scripts/python fs2dd.py --fs-playlist-id 3474
```