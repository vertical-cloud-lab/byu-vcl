# inputs: sitemap.tsv destmap.tsv drive_raw.tsv ; output long TSV
BEGIN { FS = OFS = "\t" }
FILENAME ~ /sitemap/ { no[$1] = $2; nm[$1] = $3; city[$1] = $4; addr[$1] = $5; next }
FILENAME ~ /destmap/ { dn[$1] = $2; next }
{
  split($1, p, "_"); sid = p[1]; did = p[2]; combo = p[3] "_" p[4];
  if (!(sid in no) || $4 == "") next;
  t = (p[3] == "am") ? "07:30" : (p[3] == "pm") ? "17:00" : "13:00";
  dir = (p[4] == "out") ? "site to destination" : "destination to site";
  range($4); mi = $5; sub(/ miles?$/, "", mi); via = $6; sub(/^via /, "", via);
  print no[sid], nm[sid], city[sid], dn[did], "Tue 2026-11-17 " t, dir, LO, HI, mi, via, $4, $2, $3
}
