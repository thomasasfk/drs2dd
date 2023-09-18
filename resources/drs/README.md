```bash
# Find all files in the current directory and its subdirectories, and list only the file extensions, sorted uniquely.
find . -type f | sed 's/.*\.//' | sort -u
```

```bash
# Find all XML files in the current directory and its subdirectories.
find . -type f -name "*.xml"
```

```bash
# Count the number of XML files in the current directory and its subdirectories.
find . -type f -name "*.xml" | wc -l
```

```bash
# Count the number of M4A audio files in the current directory and its subdirectories.
find . -type f -name "*.m4a" | wc -l
```

```bash
# Find all XML files in the current directory and its subdirectories, then filter those that have a pattern like '_[0-9][a-zA-Z].xml' at the end, sort them, and list them uniquely.
find . -type f -name '*.xml' | grep -Eo '_[0-9][a-zA-Z]\.xml$' | sort | uniq
```

```bash
# Find all files named "song.json" in the current directory and its subdirectories, and remove them.
find . -type f -name "song.json" -exec rm -f {} \;
```

```bash
# Find all M4A audio files in the current directory and its subdirectories, and convert them to ogg format using ffmpeg.
find . -type f -name "*.m4a" -exec sh -c 'ffmpeg -y -i "$1" "${1%.m4a}.ogg"' sh {} \;
```

```bash
# remove 10 seconds from all ogg files
find . -type f -name "*.ogg" -exec sh -c 'DURATION=$(ffprobe -i "$0" -show_entries format=duration -v quiet -of csv="p=0"); TRIM_TIME=$(awk "BEGIN {print $DURATION - 10}"); ffmpeg -ss 0 -t $TRIM_TIME -i "$0" "${0%.mp3}-fixed.ogg"' {} \;
```

```bash
# move the fixed ogg files to the original file name
find . -type f -name '*-fixed.ogg' -exec sh -c 'mv "$0" "${0%-fixed.mp3}.ogg"' {} \;
```
