# DANCERUSH STARDOM to Dance Dash

Convert data of [DANCERUSH STARDOM](https://remywiki.com/AC_DRS) tracks into [Dance Dash](https://store.steampowered.com/app/2005050/Dance_Dash/) beat maps

Curious? @thomasasfk on discord

### Download the tracks here:

- https://mega.nz/file/KbB1DSjb#_sepIa5KmyWVChnCMyaZxqztzQuXXDI3AMgXEdpR7-8 (all songs)

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
.venv/Scripts/python fs2dd.py ...  # WIP when I have time.
```
