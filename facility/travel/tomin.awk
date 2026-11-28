# convert "1 hr 15 min" / "45 min" / "1 hr" / "28" to minutes
function tomin(s,   n, a, i, t) {
  t = 0; n = split(s, a, " ");
  if (n == 1 && a[1] ~ /^[0-9]+$/) return a[1] + 0;
  for (i = 1; i <= n; i++) {
    if (a[i+1] == "hr" || a[i+1] == "hrs" || a[i+1] == "h") t += a[i] * 60;
    else if (a[i+1] == "min" || a[i+1] == "mins") t += a[i];
  }
  return t;
}
# dur: "typically 28–45 min", "typically 35 min to 1 hr", "45 min"
function range(dur,   s, p, l, r, unit) {
  s = dur; sub(/^typically /, "", s);
  if (index(s, " to ") > 0) { p = index(s, " to "); l = substr(s, 1, p - 1); r = substr(s, p + 4); }
  else if (index(s, "–") > 0) { p = index(s, "–"); l = substr(s, 1, p - 1); r = substr(s, p + length("–")); }
  else { l = s; r = s; }
  LO = tomin(l); HI = tomin(r);
  if (l ~ /^[0-9]+$/) { if (r ~ /^[0-9]+ min$/) LO = l + 0; else if (r ~ /^[0-9]+ hr$/ ) LO = l * 60; else LO = l + 0; }
}
