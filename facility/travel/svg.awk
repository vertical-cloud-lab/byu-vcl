# long TSV -> SVG small multiples: rows = sites, panels = destinations; midday range + rush envelope
BEGIN { FS = "\t"; split("BYU Engineering Building|U of U Warnock Engineering Building|Provo Airport (PVU)|Salt Lake City International (SLC)", D, "|");
  split("BYU Engineering Bldg|U of U Warnock Bldg|Provo Airport|SLC Airport", T, "|");
  W = 1316; L = 300; PW = 215; PG = 36; X0 = 0; XMAX = 120; RH = 28; TOP = 112; GAP = 18 }
$1 == "site_no" { next }
{ n = $1; site[n] = $2; city[n] = $3; d = $4; t = substr($5, 16, 5); seen[n] = 1;
  if (t == "13:00" && $6 ~ /^site/) { mlo[n, d] = $7; mhi[n, d] = $8 }
  else if (t != "13:00") { if (!((n, d) in rlo) || $7 < rlo[n, d]) rlo[n, d] = $7; if ($8 > rhi[n, d]) rhi[n, d] = $8 } }
function px(v, j) { return L + (j - 1) * (PW + PG) + v / XMAX * PW }
function grp(n) { return (n <= 5) ? 1 : (n <= 13) ? 2 : 3 }
END { for (n in seen) ns[++N] = n + 0; asort(ns);
  y = TOP; prev = 0;
  for (i = 1; i <= N; i++) { n = ns[i]; if (grp(n) != prev) { y += (prev ? GAP : 0); gy[grp(n)] = y; prev = grp(n) } ry[n] = y; y += RH }
  H = y + 52;
  printf "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"%d\" height=\"%d\" viewBox=\"0 0 %d %d\" font-family=\"Helvetica, Arial, sans-serif\">\n", W, H, W, H;
  printf "<rect width=\"%d\" height=\"%d\" fill=\"#fcfcfb\"/>\n", W, H;
  printf "<text x=\"16\" y=\"30\" font-size=\"19\" font-weight=\"700\" fill=\"#0b0b0b\">Drive time from each candidate site, minutes (Google's typical range, Tue 17 Nov 2026)</text>\n";
  # legend
  printf "<rect x=\"16\" y=\"48\" width=\"34\" height=\"7\" rx=\"3.5\" fill=\"#2a78d6\"/><text x=\"58\" y=\"56\" font-size=\"14\" fill=\"#0b0b0b\">Midday, 1:00 PM, site to destination</text>\n";
  printf "<rect x=\"350\" y=\"48\" width=\"34\" height=\"7\" rx=\"3.5\" fill=\"#eb6834\"/><text x=\"392\" y=\"56\" font-size=\"14\" fill=\"#0b0b0b\">Rush hours, 7:30 AM and 5:00 PM, both directions: lowest to highest</text>\n";
  for (j = 1; j <= 4; j++) {
    x1 = px(0, j); printf "<text x=\"%.1f\" y=\"%d\" font-size=\"14\" font-weight=\"700\" fill=\"#0b0b0b\">%s</text>\n", x1, TOP - 18, T[j];
    for (g = 0; g <= XMAX; g += 30) { gx = px(g, j);
      printf "<line x1=\"%.1f\" y1=\"%d\" x2=\"%.1f\" y2=\"%d\" stroke=\"%s\" stroke-width=\"1\"/>\n", gx, TOP - 8, gx, H - 44, (g == 0 ? "#b9b8b3" : "#e6e5e1");
      printf "<text x=\"%.1f\" y=\"%d\" font-size=\"12\" fill=\"#52514e\" text-anchor=\"middle\">%d</text>\n", gx, H - 28, g }
  }
  split("Lehi|Utah County, south of Lehi|Salt Lake County", G, "|");
  for (g = 1; g <= 3; g++) if (g in gy) printf "<text x=\"16\" y=\"%d\" font-size=\"11\" font-weight=\"700\" fill=\"#52514e\" letter-spacing=\"0.5\">%s</text>\n", gy[g] - 2, toupper(G[g]);
  for (i = 1; i <= N; i++) { n = ns[i]; yy = ry[n];
    nm = site[n]; sub(/Holbrook Industrial Park Bldg 5/, "Holbrook Bldg 5 (and 2)", nm); sub(/Fluke Industrial and AF Industrial Bldg 1/, "Fluke and AF Industrial 1", nm); if (length(nm) > 30) nm = substr(nm, 1, 28) "…";
    printf "<text x=\"16\" y=\"%d\" font-size=\"13\" fill=\"#0b0b0b\">%d  %s</text>\n", yy + 16, n, nm;
    printf "<text x=\"%d\" y=\"%d\" font-size=\"12\" fill=\"#52514e\" text-anchor=\"end\">%s</text>\n", L - 12, yy + 16, city[n];
    for (j = 1; j <= 4; j++) { d = D[j];
      if ((n, d) in mlo) { a = px(mlo[n, d], j); b = px(mhi[n, d], j); if (b - a < 7) b = a + 7;
        printf "<rect x=\"%.1f\" y=\"%d\" width=\"%.1f\" height=\"7\" rx=\"3.5\" fill=\"#2a78d6\"><title>%s to %s, 1 PM: %d-%d min</title></rect>\n", a, yy + 4, b - a, site[n], T[j], mlo[n, d], mhi[n, d] }
      if ((n, d) in rlo) { a = px(rlo[n, d], j); b = px(rhi[n, d] > XMAX ? XMAX : rhi[n, d], j); if (b - a < 7) b = a + 7;
        printf "<rect x=\"%.1f\" y=\"%d\" width=\"%.1f\" height=\"7\" rx=\"3.5\" fill=\"#eb6834\"><title>%s and %s, rush hours: %d-%d min</title></rect>\n", a, yy + 13, b - a, site[n], T[j], rlo[n, d], rhi[n, d];
        if (rhi[n, d] > XMAX) printf "<text x=\"%.1f\" y=\"%d\" font-size=\"11\" fill=\"#52514e\" text-anchor=\"end\">%d</text>\n", b - 2, yy + 11, rhi[n, d] } } }
  printf "<text x=\"16\" y=\"%d\" font-size=\"11\" fill=\"#52514e\">Source: Google Maps directions with Depart at set, read 2026-11-13. Each bar spans Google's \"typically X to Y min\" for the first route listed. Numbers are the map's site numbers.</text>\n", H - 8;
  print "</svg>" }
