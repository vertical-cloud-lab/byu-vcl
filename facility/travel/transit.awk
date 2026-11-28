# stripped text lines of a transit page -> "dur \t window \t lines" of first option, or "none"
BEGIN { state = 0 }
/^Sorry, we could not calculate transit directions/ { none = 1 }
state == 0 && /^Copy link$/ { state = 1; next }
state == 1 && /^([0-9]+ hr)?( ?[0-9]+ min)?$/ && $0 != "" { dur = $0; state = 2; next }
state == 2 { win = $0; state = 3; next }
state == 3 {
  if ($0 ~ /^[0-9]{1,2}:[0-9]{2} [AP]M$/ || $0 ~ /^Details$/ || $0 ~ /^([0-9]+ hr)?( ?[0-9]+ min)?$/ || $0 ~ /^Explore nearby/) { state = 4; next }
  lines = (lines == "") ? $0 : lines " > " $0; next }
END { if (none && dur == "") print "none\t\t"; else print dur "\t" win "\t" lines }
