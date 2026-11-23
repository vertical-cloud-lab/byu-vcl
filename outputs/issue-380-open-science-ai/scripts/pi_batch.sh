#!/bin/bash
# Run a TSV (engine<TAB>query) through pi_search.py one query at a time.
cd "$(dirname "$0")"
while IFS=$'\t' read -r eng q; do
  [ -z "$eng" ] && continue; case "$eng" in \#*) continue;; esac
  echo "=== [$eng] $q"
  PI_WHO=${PI_WHO:-main-batch} timeout 240 python3 pi_search.py --engine "$eng" "$q" | head -40
done < "$1"
