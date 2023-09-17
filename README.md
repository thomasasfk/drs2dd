# DANCERUSH STARDOM to Dance Dash

Convert data of [DANCERUSH STARDOM](https://remywiki.com/AC_DRS) tracks into [Dance Dash](https://store.steampowered.com/app/2005050/Dance_Dash/) beat maps

Curious? @thomasasfk on discord or join [drs2dd](https://discord.gg/JVWx6zmtft) and ask!

https://github.com/thomasasfk/drs2dd/assets/22506439/8e2953c5-3c39-423f-971a-47bc1f6a717d

## Stuff

### Completed:

- [x] Parse XML files into JSON files
- [x] Parse JSON files into DD info metadata
- [x] Create DD beat map folder structure with song & cover
- [x] Parse notes & lines into DD beat map
- [x] Parse shuffles into DD beat map

### To-Do:

- [ ] Parse down and jump notes into DD beat map
- [ ] Test folder structure, sort bmp, note speed, order, etc.
- [ ] Create album specifically for these tracks (does DD support this yet?)

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

Generate full DD Beat Map from json files in repository (does not map notes atm, todo)

```bash
.venv/Scripts/python drs2dd.py --song-id 187
```

Generate all DD Beat Maps from json files in repository (does not map notes atm, todo)

```bash
.venv/Scripts/python drs2dd_all.py
```
