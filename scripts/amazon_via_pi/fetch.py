#!/usr/bin/env python3
"""Fetch Amazon pages through a lab Pi's residential IP, paced and rate-capped.

Amazon answers a GitHub Actions runner (a datacenter IP) with bot checks, so the
request is made on the Pi with curl, over Tailscale SSH, and the gzip-compressed
page is streamed straight back to the runner. Nothing is written on the Pi.

    python3 -I fetch.py <outdir> search "chest harness magsafe" "neck mount phone"
    python3 -I fetch.py <outdir> dp B0CLRHYNP4 B0D3DRXLN9

Which Pi: --pi-env PREFIX reads ${PREFIX}_USERNAME and ${PREFIX}_HOSTNAME from
the environment (default CUBXL_PI, the Pi 5 with the most headroom; the
stream-cam Pis are carrying live streams). Hostnames are never printed.

Pacing: FETCH_GAP="lo,hi" seconds between requests (default 15,25). At 8-14 s,
search pages started coming back as Amazon's ~1.4 kB JavaScript interstitial
(bm-verify) after about ten requests; product pages were not challenged at
15-25 s, though the two searches right after the first block were blocked too.
parse_search.py reports a blocked page as zero results.
"""
import argparse, os, random, shlex, subprocess, time, urllib.parse

UA = ("Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

ap = argparse.ArgumentParser()
ap.add_argument("outdir")
ap.add_argument("kind", choices=["search", "dp"])
ap.add_argument("items", nargs="+")
ap.add_argument("--pi-env", default="CUBXL_PI")
args = ap.parse_args()

os.makedirs(args.outdir, exist_ok=True)
host = f'{os.environ[args.pi_env + "_USERNAME"]}@{os.environ[args.pi_env + "_HOSTNAME"]}'
lo, hi = map(float, os.environ.get("FETCH_GAP", "15,25").split(","))
for i, item in enumerate(args.items):
    if args.kind == "search":
        url = "https://www.amazon.com/s?k=" + urllib.parse.quote_plus(item)
        name = "s_" + "".join(c if c.isalnum() else "_" for c in item)[:60]
    else:
        url = f"https://www.amazon.com/dp/{item}"
        name = "dp_" + item
    remote = ("curl -s --max-time 40 --limit-rate 300k "  # rate cap: the Pi is on Wi-Fi
              f"-A {shlex.quote(UA)} "
              "-H 'Accept-Language: en-US,en;q=0.9' "
              "-H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' "
              "-H 'Accept-Encoding: gzip' "
              f"{shlex.quote(url)}")
    path = os.path.join(args.outdir, name + ".html.gz")
    with open(path, "wb") as f:
        r = subprocess.run(["ssh", "-o", "ConnectTimeout=20", "-o", "BatchMode=yes", host, remote],
                           stdout=f, stderr=subprocess.DEVNULL, timeout=90)
    print(f"[{i + 1}/{len(args.items)}] rc={r.returncode} {os.path.getsize(path):>7} B  {name}", flush=True)
    if i + 1 < len(args.items):
        time.sleep(random.uniform(lo, hi))
