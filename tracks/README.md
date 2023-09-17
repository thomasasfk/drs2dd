# Tracks!  Come back later.

```bash
ls -l . | grep -c '^d'
```

```bash
# remove 10 seconds from all mp3 files
find . -type f -name "*.mp3" -exec sh -c 'DURATION=$(ffprobe -i "$0" -show_entries format=duration -v quiet -of csv="p=0"); TRIM_TIME=$(awk "BEGIN {print $DURATION - 10}"); ffmpeg -ss 0 -t $TRIM_TIME -i "$0" "${0%.mp3}-fixed.mp3"' {} \;
```

```bash
# move the fixed mp3 files to the original file name
find . -type f -name '*-fixed.mp3' -exec sh -c 'mv "$0" "${0%-fixed.mp3}.mp3"' {} \;
```