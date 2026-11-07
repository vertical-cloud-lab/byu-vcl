#!/bin/bash
# usage: run_part.sh <scad> <outdir> <part> [extra -D args]
SCAD="$1"; OUT="$2"; P="$3"; shift 3
OSC=/tmp/openflexure/openscad_nightly/squashfs-root/AppRun
cd "$(dirname "$SCAD")"
start=$(date +%s)
timeout 1500 "$OSC" --backend=manifold -D "PART=\"$P\"" "$@" -o "$OUT/$P.stl" "$(basename "$SCAD")" > /tmp/openflexure/work/logs/$(basename "$OUT")_$P.log 2>&1
rc=$?
echo "$P rc=$rc $(( $(date +%s) - start ))s"
