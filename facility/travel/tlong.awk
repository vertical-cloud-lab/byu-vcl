# inputs: sitemap.tsv destmap.tsv transit_raw.tsv (id, dur, window, lines, origin, dest)
BEGIN { FS = OFS = "\t" }
FILENAME ~ /sitemap/ { no[$1] = $2; nm[$1] = $3; city[$1] = $4; next }
FILENAME ~ /destmap/ { dn[$1] = $2; next }
{
  id = $1; sub(/^X/, "", id); split(id, p, "_"); sid = p[1]; did = p[2];
  if (!(sid in no)) next;
  t = (p[3] == "am") ? "07:30" : (p[3] == "pm") ? "17:00" : "13:00";
  dir = (p[4] == "out") ? "site to destination" : "destination to site";
  m = ($2 == "none" || $2 == "") ? "" : tomin($2);
  print no[sid], nm[sid], city[sid], dn[did], "Tue 2026-11-17 " t, dir, ($2 == "" ? "not read" : $2), m, $3, $4, $5, $6
}
