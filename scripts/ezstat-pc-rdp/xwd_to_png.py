"""Convert an Xvfb -fbdir framebuffer snapshot (XWD, optionally gzipped) to PNG.

Only the pixels are kept. The XWD header carries the Pi's hostname, so publish
the PNG, never the XWD.

    python xwd_to_png.py FRAME.xwd[.gz] OUT.png
"""

import gzip
import struct
import sys

import numpy as np
from PIL import Image


def read_xwd(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rb") as f:
        data = f.read()
    (header_size, version, pixmap_format, _depth, width, height, _xoffset,
     byte_order, _unit, _bit_order, _pad, bits_per_pixel, bytes_per_line,
     _visual, red_mask, green_mask, blue_mask, _bits_per_rgb, _cmap_entries,
     ncolors, *_window) = struct.unpack(">25I", data[:100])
    if version != 7 or pixmap_format != 2 or bits_per_pixel != 32:
        raise ValueError(f"unsupported XWD: version {version}, format "
                         f"{pixmap_format}, {bits_per_pixel} bpp")
    offset = header_size + 12 * ncolors
    dtype = "<u4" if byte_order == 0 else ">u4"
    words = np.frombuffer(data, dtype=dtype, count=bytes_per_line // 4 * height,
                          offset=offset).reshape(height, bytes_per_line // 4)
    words = words[:, :width]

    def channel(mask):
        shift = (mask & -mask).bit_length() - 1
        return ((words & mask) >> shift).astype(np.uint8)

    return np.dstack([channel(red_mask), channel(green_mask), channel(blue_mask)])


if __name__ == "__main__":
    Image.fromarray(read_xwd(sys.argv[1]), "RGB").save(sys.argv[2], optimize=True)
