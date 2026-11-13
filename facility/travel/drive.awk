# stripped text lines of a driving page -> "duration \t distance \t via" for the first route listed
/^Copy link$/ { s = 1; next }
s == 1 && (/^typically / || /^([0-9]+ hr)?( ?[0-9]+ min)$/) { d = $0; s = 2; next }
s == 2 && / (miles|mi|ft)$/ { m = $0; s = 3; next }
s == 3 && /^via / { printf "%s\t%s\t%s", d, m, $0; s = 4; exit }
