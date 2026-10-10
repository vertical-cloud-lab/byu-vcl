#!/usr/bin/env python3
"""Check the burned text against the phone safe areas, without rendering anything.

Rebuilds every on-screen phrase exactly as make_reels.py would (same chunking, same
auto-fit, same fixed line breaks), measures it with the real font metrics, and reports
the extreme right edge and the extreme bottom edge across the whole set -- the two
numbers that decide whether a word ends up behind the like/comment/share column or the
caption/handle strip. Platform overlay extents are published industry figures, not
measured on a device; they are listed so the margin is explicit.

Usage: python3 qa_layout.py [--edl reels-edl.json]
"""
import argparse, json
from pathlib import Path

import make_reels as mr

# approximate lower edge of the platform's own chrome, in a 1920-tall frame
UI_BOTTOM = {"YouTube Shorts": 1600, "Instagram Reels": 1490, "TikTok": 1440}
UI_RIGHT = {"Instagram Reels / TikTok action column": 860}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edl", default=str(Path(__file__).resolve().parent / "reels-edl.json"))
    args = ap.parse_args()
    edl = json.load(open(args.edl))

    worst_r = worst_b = None
    sizes, line_counts = [], []
    for reel in edl["reels"]:
        for item in reel["items"]:
            words, _ = mr.item_words_local(item)
            it = {"words": words, "visual": item.get("visual", "card")}
            phrases = mr.item_phrases(it)
            fitted = [mr.wrap_phrase([w[2] for w in ph]) for ph in phrases]
            size = min((f[0] for f in fitted), default=mr.QUOTE_SIZES[0])
            sizes.append(size)
            for ph in phrases:
                texts = [w[2] for w in ph]
                _, lines = mr.wrap_phrase(texts, size)
                line_counts.append(len(lines))
                bottom = mr.QUOTE_Y + len(lines) * size * mr.LINE_H
                if worst_b is None or bottom > worst_b[0]:
                    worst_b = (bottom, reel["id"], item["id"], len(lines), size)
                for ln in lines:
                    right = mr.SAFE_L + mr.text_w(" ".join(texts[j] for j in ln),
                                                  mr.FONT_QUOTE, size)
                    if worst_r is None or right > worst_r[0]:
                        worst_r = (right, reel["id"], item["id"], size)

    print(f"quote type sizes used: {sorted(set(sizes), reverse=True)}  "
          f"(median {sorted(sizes)[len(sizes) // 2]} px)")
    print(f"lines per phrase: max {max(line_counts)} (cap {mr.MAX_LINES}), "
          f"mean {sum(line_counts) / len(line_counts):.2f}")
    print(f"widest line  x={worst_r[0]:.0f}px  [{worst_r[1]} {worst_r[2]} @{worst_r[3]}px]")
    for name, edge in UI_RIGHT.items():
        print(f"    vs {name:<44} {edge}px  ->  "
              f"{'OK' if worst_r[0] < edge else 'COLLIDES'} ({edge - worst_r[0]:+.0f}px)")
    print(f"lowest text  y={worst_b[0]:.0f}px  [{worst_b[1]} {worst_b[2]} "
          f"{worst_b[3]} lines @{worst_b[4]}px]")
    for name, edge in sorted(UI_BOTTOM.items(), key=lambda kv: kv[1]):
        print(f"    vs {name:<44} {edge}px  ->  "
              f"{'OK' if worst_b[0] < edge else 'COLLIDES'} ({edge - worst_b[0]:+.0f}px)")
    ok = worst_r[0] < min(UI_RIGHT.values()) and worst_b[0] < min(UI_BOTTOM.values())
    print("\nsafe areas:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
