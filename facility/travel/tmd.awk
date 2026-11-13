BEGIN { FS = "\t"; split("BYU Engineering Building|U of U Warnock Engineering Building|Provo Airport (PVU)|Salt Lake City International (SLC)", D, "|") }
$1 == "site_no" { next }
{ n = $1; site[n] = $2; city[n] = $3; t = substr($5, 16, 5); k = n SUBSEP $4 SUBSEP t; v[k] = ($7 == "none") ? "none" : ($8 == "" ? "?" : hm($8)); seen[n] = 1 }
function hm(x) { return int(x / 60) ":" sprintf("%02d", x % 60) }
function c(n, d, t,   k) { k = n SUBSEP d SUBSEP t; return (k in v) ? v[k] : "?" }
END { for (n in seen) ns[++N] = n + 0; asort(ns);
  print "| # | Site | City | BYU Engineering Bldg | U of U Warnock Bldg | Provo Airport | SLC Airport |";
  print "| --: | --- | --- | --- | --- | --- | --- |";
  for (i = 1; i <= N; i++) { n = ns[i]; line = "| " n " | " site[n] " | " city[n];
    for (j = 1; j <= 4; j++) line = line " | " c(n, D[j], "07:30") " · " c(n, D[j], "13:00") " · " c(n, D[j], "17:00");
    print line " |" } }
