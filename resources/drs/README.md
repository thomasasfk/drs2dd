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
# remove 10 seconds from all m4as and convert to ogg files
find . -type f -name "*.m4a" -exec sh -c 'DURATION=$(ffprobe -i "$0" -show_entries format=duration -v quiet -of csv="p=0"); TRIM_TIME=$(awk "BEGIN {print $DURATION - 10}"); ffmpeg -y -ss 0 -t $TRIM_TIME -i "$0" "${0%.m4a}.ogg"' {} \;
```

```bash
#!/bin/bash
find . -type f -name "*.2dx" -exec sh -c '
  dir=$(dirname "$0")
  filename=$(basename "$0")
  file_without_extension="${filename%.*}"

  if echo "$filename" | grep -qE "clip|pre"; then
    echo "Skipping $filename"
    exit 0
  fi

  cd "$dir" || exit 1
  2dxdump "$filename"
  ffmpeg -y -i "0.wav" "${file_without_extension}clip1.ogg"
' {} \;
```

```bash
find . -type f -name "1.wav" -exec rm -f {} \;
```

```bash
#!/bin/bash
find . -type f -name "*.s3p" -exec sh -c '
  dir=$(dirname "$0")
  filename=$(basename "$0")
  file_without_extension="${filename%.*}"

  output_file="${file_without_extension}clip1.ogg"

  if echo "$filename" | grep -qE "clip|pre"; then
    echo "Skipping $filename"
    exit 0
  fi

  cd "$dir" || exit 1
  if [ -f "$output_file" ]; then
    echo "Skipping as $output_file already exists."
    exit 0
  fi

  # uhh yea deal with it lol
  ../../../../../.venv/Scripts/python ../../../../../s3p_unpack.py --input "$filename"
  ffmpeg -y -i "0.wma" "$output_file"
' {} \;
```