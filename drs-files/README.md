```bash
find . -type f | sed 's/.*\.//' | sort -u
```

```bash
find . -type f -name "*.xml"
```

```bash
find . -type f -name "*.xml" | wc -l
```

```bash
find . -type f -name "*.m4a" | wc -l
```

```bash
find . -type f -name '*.xml' | grep -Eo '_[0-9][a-zA-Z]\.xml$' | sort | uniq
```

```bash
find . -type f -name "song.json" -exec rm -f {} \;
```
