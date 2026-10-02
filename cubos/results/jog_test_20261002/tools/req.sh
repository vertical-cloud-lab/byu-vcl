#!/bin/bash
# req.sh <id> <request...>: append a request for grbl_xy.py and wait for its result.
id="$1"; shift; out=/tmp/jog_20261002
echo "$id $*" >> "$out/cmds.txt"
for i in $(seq 1 300); do
  if grep -qE "(DONE|FAIL) $id( |$)" "$out/grbl.log"; then break; fi
  sleep 0.2
done
grep -E "request $id:|(DONE|FAIL) $id( |$)" "$out/grbl.log" | tail -2
