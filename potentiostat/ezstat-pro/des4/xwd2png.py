"""Convert Xvfb's -fbdir framebuffer (XWD, 24/32 bpp TrueColor) to PNG. Stdlib only.

usage: python3 xwd2png.py <Xvfb_screen0> <out.png> [x y w h]
"""
import struct, sys, zlib

src, dst = sys.argv[1], sys.argv[2]
data = open(src, 'rb').read()
h = struct.unpack('>25I', data[:100])
header_size, depth, width, height = h[0], h[3], h[4], h[5]
byte_order, bpp, bpl, ncolors = h[7], h[11], h[12], h[19]
red_mask = h[14]
if bpp != 32:
    sys.exit('unsupported bits_per_pixel %d' % bpp)
off = header_size + ncolors * 12
x0, y0, w, hh = 0, 0, width, height
if len(sys.argv) == 7:
    x0, y0, w, hh = map(int, sys.argv[3:7])
# byte positions of R, G, B within a 4-byte pixel
if byte_order == 0:  # LSBFirst: little-endian 0x00RRGGBB -> B G R X
    ri, gi, bi = (2, 1, 0) if red_mask == 0xff0000 else (0, 1, 2)
else:
    ri, gi, bi = (1, 2, 3) if red_mask == 0xff0000 else (3, 2, 1)
raw = bytearray()
for y in range(y0, y0 + hh):
    row = data[off + y * bpl + x0 * 4: off + y * bpl + (x0 + w) * 4]
    rgb = bytearray(w * 3)
    rgb[0::3] = row[ri::4]
    rgb[1::3] = row[gi::4]
    rgb[2::3] = row[bi::4]
    raw += b'\x00' + rgb


def chunk(tag, body):
    c = struct.pack('>I', len(body)) + tag + body
    return c + struct.pack('>I', zlib.crc32(tag + body) & 0xffffffff)


png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, hh, 8, 2, 0, 0, 0))
png += chunk(b'IDAT', zlib.compress(bytes(raw), 6)) + chunk(b'IEND', b'')
open(dst, 'wb').write(png)
print('%s: %dx%d' % (dst, w, hh))
