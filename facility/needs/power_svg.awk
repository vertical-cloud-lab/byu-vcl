# Bars: each site's listed service (light) and a 20,000 ft2 suite's pro-rata share (solid), in kVA,
# against the lab's needs (dashed lines). Input TSV: label, whole_kva, share_kva, note.
# -v n1=<kVA> -v l1=<label> -v n2=<kVA> -v l2=<label> -v xmax=<kVA>
BEGIN { FS = "\t"; W = 1000; L = 300; R = 40; T = 118; RH = 36; BH = 22 }
NR == 1 { next }
{ n++; lab[n] = $1; whole[n] = $2; share[n] = $3; note[n] = $4 }
function X(v) { return L + (W - L - R) * v / xmax }
END {
  H = T + n * RH + 64
  printf "<svg xmlns='http://www.w3.org/2000/svg' width='%d' height='%d' viewBox='0 0 %d %d' font-family='Helvetica, Arial, sans-serif'>\n", W, H, W, H
  print "<rect width='100%' height='100%' fill='#fcfcfb'/>"
  print "<text x='24' y='34' font-size='19' font-weight='bold' fill='#0b0b0b'>Power a site could give the lab, against what the lab needs</text>"
  print "<text x='24' y='58' font-size='13' fill='#52514e'>kVA at 480 V three-phase. Light bar: the whole building's listed service. Dark bar: a 20,000 ft&#178; suite's share,</text>"; print "<text x='24' y='76' font-size='13' fill='#52514e'>pro rata by floor area, or the whole service where the deal is the whole building. Dashed lines: the lab's need, with 25 % margin.</text>"
  # grid and axis
  for (v = 0; v <= xmax; v += 500) {
    x = X(v)
    printf "<line x1='%.1f' y1='%d' x2='%.1f' y2='%d' stroke='#e6e5e0' stroke-width='1'/>\n", x, T - 8, x, T + n * RH
    printf "<text x='%.1f' y='%d' font-size='12' fill='#52514e' text-anchor='middle'>%s</text>\n", x, T + n * RH + 18, v
  }
  printf "<text x='%.1f' y='%d' font-size='12' fill='#52514e' text-anchor='middle'>kVA</text>\n", X(xmax / 2), T + n * RH + 38
  for (i = 1; i <= n; i++) {
    y = T + (i - 1) * RH + (RH - BH) / 2
    printf "<text x='%d' y='%.1f' font-size='13' fill='#0b0b0b' text-anchor='end'>%s</text>\n", L - 10, y + BH / 2 + 4.5, lab[i]
    if (whole[i] > 0) printf "<rect x='%d' y='%.1f' width='%.1f' height='%d' rx='4' fill='#c1d7f1'><title>%s: whole service %d kVA</title></rect>\n", L, y, X(whole[i]) - L, BH, lab[i], whole[i]
    if (share[i] > 0) printf "<rect x='%d' y='%.1f' width='%.1f' height='%d' rx='4' fill='#2a78d6'><title>%s: 20,000 ft2 share %d kVA</title></rect>\n", L, y + 4, X(share[i]) - L, BH - 8, lab[i], share[i]
    if (note[i] != "") printf "<text x='%.1f' y='%.1f' font-size='12' fill='#52514e'>%s</text>\n", X(whole[i]) + 6, y + BH / 2 + 4.5, note[i]
  }
  # need lines
  split(n1 "|" n2, nv, "|"); split(l1 "|" l2, nl, "|")
  for (k = 1; k <= 2; k++) {
    if (nv[k] == "") continue
    x = X(nv[k])
    printf "<line x1='%.1f' y1='%d' x2='%.1f' y2='%d' stroke='#0b0b0b' stroke-width='2' stroke-dasharray='%s'/>\n", x, T - 14, x, T + n * RH, (k == 1 ? "6 4" : "2 3")
    printf "<text x='%.1f' y='%d' font-size='12' fill='#0b0b0b' text-anchor='%s'>%s</text>\n", x + (k == 1 ? -4 : 4), T - 18, (k == 1 ? "end" : "start"), nl[k]
  }
  print "</svg>"
}
