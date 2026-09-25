#!/usr/bin/env bash
# item.sh ITEMID -- open an eBay listing, screenshot it, copy the page text, save the
# rendered HTML (Ctrl+S, no extra request) to find the seller-description frame, then
# open that frame and copy its text. Outputs land in $HB_WORK as item-ID.{txt,html}
# and desc-ID.txt.
#
# Don't swap Ctrl+S for view-source: -- several raw view-source fetches in a row is
# what tripped eBay's "Checking your browser" interstitial on 2026-09-25.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
HB="$HERE/../hb.py"
WORK=${HB_WORK:-/tmp/hb}
ID=$1
"$HB" click 700 63; "$HB" key ctrl+a; "$HB" type "ebay.com/itm/$ID"; "$HB" key Return
"$HB" wait "${WAIT:-8}"
"$HB" shot "itm-$ID" >/dev/null
"$HB" scroll 4 600 600; "$HB" wait 1.5; "$HB" scroll -4 600 600
"$HB" click 1040 300   # the listing title: plain text, puts focus on the page body
"$HB" text > "$WORK/item-$ID.txt"
"$HB" click 1040 300
"$HB" key ctrl+s; "$HB" wait 2
"$HB" click 740 72; "$HB" key ctrl+a; "$HB" type "$WORK/item-$ID.html"; "$HB" click 1231 844
"$HB" wait 3
DESC=$(grep -oE 'https://[a-z.]*ebaydesc\.com/itmdesc/[^"'"'"' >]+' "$WORK/item-$ID.html" | head -1 | sed 's/&amp;/\&/g' || true)
if [ -n "$DESC" ]; then
  "$HB" click 700 63; "$HB" key ctrl+a; xdotool type --delay 5 "$DESC"; "$HB" key Return
  "$HB" wait 4
  "$HB" click 1300 850
  "$HB" text > "$WORK/desc-$ID.txt"
  "$HB" click 27 63   # back button
  "$HB" wait 3
fi
echo "== $ID: $WORK/item-$ID.txt${DESC:+, $WORK/desc-$ID.txt}"
