#!/bin/bash
# usage: run_native.sh <scad> <out.stl> [openscad args...]
SCAD="$1"; OUT="$2"; shift 2
OSC=/tmp/openflexure/openscad_nightly/squashfs-root/AppRun
cd "$(dirname "$SCAD")"
start=$(date +%s)
timeout 1500 "$OSC" --backend=manifold "$@" -o "$OUT" "$(basename "$SCAD")" > /tmp/openflexure/work/logs/delta_$(basename "$OUT" .stl).log 2>&1
echo "$(basename "$OUT") rc=$? $(( $(date +%s) - start ))s"
