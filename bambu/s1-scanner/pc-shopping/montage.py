from PIL import Image, ImageDraw, ImageFont
import glob
rows = [
    ("Desktops, RTX 2060 6 GB (meets the minimum)", ["desk2060_860126737002", "desk2060_366779698656"]),
    ("Desktops, RTX 3060 Ti 8 GB / RTX 3060 12 GB (meets the recommended GPU)", ["desk3060_336910955873", "desk3060_366779713222"]),
    ("Laptops, RTX 2060 6 GB (bottom of the minimum: laptop GPUs are slower)", ["lap2060_940100076991", "lap2060_237132570103"]),
    ("Laptops, RTX 3060 6 GB (meets the minimum VRAM)", ["lap3060_227570528159", "lap3060_377648602713"]),
]
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
title_f, head_f = ImageFont.truetype(FB, 26), ImageFont.truetype(FB, 22)
small_f = ImageFont.truetype(F, 18)
cards = {k: Image.open(f"/tmp/pcshop-out/card_{k}.png").convert("RGB") for _, ks in rows for k in ks}
cw = max(c.width for c in cards.values()); ch = max(c.height for c in cards.values())
pad, head_h, top = 20, 40, 90
W = pad * 3 + cw * 2
H = top + len(rows) * (head_h + ch + pad) + 40
img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
d.text((pad, 15), "Used PCs for the Bambu S1: eBay Buy It Now listings, US sellers", font=title_f, fill="black")
d.text((pad, 52), "Seen 2026-11-28 ~09:33 UTC from the BYU network (via the CubXL Pi). Prices to Utah; seller names hidden.", font=small_f, fill="#555")
y = top
for label, ks in rows:
    d.text((pad, y + 8), label, font=head_f, fill="#1a4f8b"); y += head_h
    for i, k in enumerate(ks):
        img.paste(cards[k], (pad + i * (cw + pad), y))
    y += ch + pad
img.save("/tmp/pcshop-final/ebay-used-pc-listings-2026-11-28.png", optimize=True)
print(img.size)
