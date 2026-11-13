# input: long TSV (no, site, city, dest, depart, dir, lo, hi, mi, via, ...) -> markdown tables
BEGIN { FS = "\t"; split("BYU Engineering Building|U of U Warnock Engineering Building|Provo Airport (PVU)|Salt Lake City International (SLC)", D, "|");
  short["BYU Engineering Building"] = "BYU"; short["U of U Warnock Engineering Building"] = "Warnock";
  short["Provo Airport (PVU)"] = "PVU"; short["Salt Lake City International (SLC)"] = "SLC" }
$1 == "site_no" { next }
{
  n = $1; site[n] = $2; city[n] = $3; d = $4; t = substr($5, 16, 5); o = ($6 ~ /^site/) ? "out" : "in";
  k = n SUBSEP d SUBSEP t SUBSEP o; lo[k] = $7; hi[k] = $8;
  if (o == "out" && t == "13:00") { mi[n, d] = $9; via[n, d] = $10 }
  seen[n] = 1
}
function cell(n, d, t, o,   k) { k = n SUBSEP d SUBSEP t SUBSEP o; return (k in lo) ? (lo[k] == hi[k] ? lo[k] : lo[k] "–" hi[k]) : "n/a" }
function rush(n, d,   i, t, o, k, a, b, m) { a = 9999; b = 0; m = 0;
  split("07:30 out|07:30 in|17:00 out|17:00 in", R, "|");
  for (i = 1; i <= 4; i++) { split(R[i], z, " "); k = n SUBSEP d SUBSEP z[1] SUBSEP z[2]; if (k in lo) { m++; if (lo[k] < a) a = lo[k]; if (hi[k] > b) b = hi[k] } }
  return m ? a "–" b : "n/a" }
END {
  for (n in seen) ns[++N] = n + 0; asort(ns);
  if (mode == "summary") {
    print "| # | Site | City | BYU Engineering Bldg | U of U Warnock Bldg | Provo Airport | SLC Airport |";
    print "| --: | --- | --- | --- | --- | --- | --- |";
    for (i = 1; i <= N; i++) { n = ns[i]; line = "| " n " | " site[n] " | " city[n];
      for (j = 1; j <= 4; j++) line = line " | " cell(n, D[j], "13:00", "out") " · " rush(n, D[j]);
      print line " |" }
  } else {
    for (j = 1; j <= 4; j++) { d = D[j]; s = short[d];
      print "### " d; print "";
      print "| # | Site | Miles | 1 PM, site → " s " | 1 PM, " s " → site | 7:30 AM, " s " → site | 7:30 AM, site → " s " | 5 PM, site → " s " | 5 PM, " s " → site | Route (1 PM, from site) |";
      print "| --: | --- | --: | --: | --: | --: | --: | --: | --: | --- |";
      for (i = 1; i <= N; i++) { n = ns[i];
        print "| " n " | " site[n] " | " mi[n, d] " | " cell(n, d, "13:00", "out") " | " cell(n, d, "13:00", "in") " | " cell(n, d, "07:30", "in") " | " cell(n, d, "07:30", "out") " | " cell(n, d, "17:00", "out") " | " cell(n, d, "17:00", "in") " | " via[n, d] " |" }
      print "" }
  }
}
