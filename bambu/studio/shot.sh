#!/bin/bash
# shot.sh NAME [scale%]: grab the Xvfb screen to /tmp/shots/NAME.png
DISPLAY=:99 import -window root "/tmp/shots/$1.png" && [ -n "$2" ] && mogrify -resize "$2%" "/tmp/shots/$1.png"; echo "/tmp/shots/$1.png"
