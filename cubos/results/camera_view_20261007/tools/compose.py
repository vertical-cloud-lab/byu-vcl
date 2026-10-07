"""2 x 2 figure: camera 0 at home (real) and at the origin (predicted), for both spots.
usage: compose.py <out_dir>   (reads <tag>_{home,origin}_overlay.jpg from origin_view.py)"""
import sys, site
sys.path.append(site.getusersitepackages())
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]
W, H = 960, 540
small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
rows = [('f6', '16:12 spot (49 cm up)'), ('c', '16:33 spot, now (38 cm up)')]
cols = [('home', 'head at home (where it is now): real picture'), ('origin', 'head at origin (0, 0): predicted')]
sheet = Image.new('RGB', (W * 2, H * 2 + 60), (255, 255, 255)); d = ImageDraw.Draw(sheet)
for r, (tag, rl) in enumerate(rows):
    for c, (nm, cl) in enumerate(cols):
        sheet.paste(Image.open(f'{out}/{tag}_{nm}_overlay.jpg').resize((W, H)), (c * W, r * H))
        label = f'{rl}, {cl}'
        d.rectangle([c * W, r * H, c * W + d.textlength(label, font=small) + 16, r * H + 32], fill=(0, 0, 0))
        d.text((c * W + 8, r * H + 5), label, fill=(255, 255, 255), font=small)
d.text((10, 2 * H + 15), 'yellow: deck plate    blue: area the capper can reach (deck 0-361 x 0-278 mm)    red: head parts that move with the camera    grey: off the plate, not predicted',
       fill=(0, 0, 0), font=small)
sheet.save(f'{out}/origin_views.jpg', quality=85)
