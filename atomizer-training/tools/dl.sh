#!/bin/bash
# Runs on the Pi: subs first (tiny), then audio for all, then 360p video for all. Rate-capped.
cd ~/atomizer-dl
Y=~/.venvs/ytframes/bin/yt-dlp
for pass in subs audio video; do
  while read id; do
    [ -z "$id" ] && continue
    case $pass in
      subs)  $Y --js-runtimes node -q --no-warnings --skip-download --write-auto-subs --write-subs --sub-langs en --sub-format vtt -o "%(id)s.%(ext)s" "https://www.youtube.com/watch?v=$id" ;;
      audio) [ -s "$id.m4a" ] || $Y --js-runtimes node -q --no-warnings --limit-rate 3M -f "ba[ext=m4a]/ba" -o "%(id)s.%(ext)s" "https://www.youtube.com/watch?v=$id" ;;
      video) [ -s "$id.v360.mp4" ] || $Y --js-runtimes node -q --no-warnings --limit-rate 3M -f "bv*[height<=360][ext=mp4]/bv*[height<=360]" -o "%(id)s.v360.%(ext)s" "https://www.youtube.com/watch?v=$id" ;;
    esac
    echo "$(date -u +%H:%M:%S) $pass $id exit=$?"
  done < ids.txt
done
echo "ALL DONE $(date -u +%H:%M:%S)"
