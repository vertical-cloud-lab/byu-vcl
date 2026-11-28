#!/usr/bin/env python3
"""Screenshot a whole X display to PNG using only libX11 (ctypes) and zlib.

    DISPLAY=:99 python3 xshot.py out.png
"""
import ctypes
import ctypes.util
import os
import struct
import sys
import zlib


class XImage(ctypes.Structure):          # the leading fields of Xlib's XImage
    _fields_ = [("width", ctypes.c_int), ("height", ctypes.c_int), ("xoffset", ctypes.c_int),
                ("format", ctypes.c_int), ("data", ctypes.c_void_p), ("byte_order", ctypes.c_int),
                ("bitmap_unit", ctypes.c_int), ("bitmap_bit_order", ctypes.c_int),
                ("bitmap_pad", ctypes.c_int), ("depth", ctypes.c_int),
                ("bytes_per_line", ctypes.c_int), ("bits_per_pixel", ctypes.c_int)]


def grab(display: str | None = None) -> tuple[int, int, bytes]:
    x = ctypes.CDLL(ctypes.util.find_library("X11"))
    x.XOpenDisplay.restype = ctypes.c_void_p
    x.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x.XDefaultRootWindow.restype = ctypes.c_ulong
    x.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
    x.XDefaultScreen.argtypes = [ctypes.c_void_p]
    x.XDisplayWidth.argtypes = x.XDisplayHeight.argtypes = [ctypes.c_void_p, ctypes.c_int]
    x.XGetImage.restype = ctypes.POINTER(XImage)
    x.XGetImage.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_int,
                            ctypes.c_uint, ctypes.c_uint, ctypes.c_ulong, ctypes.c_int]
    dpy = x.XOpenDisplay((display or os.environ["DISPLAY"]).encode())
    if not dpy:
        raise SystemExit("cannot open display")
    scr = x.XDefaultScreen(dpy)
    w, h = x.XDisplayWidth(dpy, scr), x.XDisplayHeight(dpy, scr)
    img = x.XGetImage(dpy, x.XDefaultRootWindow(dpy), 0, 0, w, h, 0xFFFFFFFF, 2).contents  # ZPixmap
    if img.bits_per_pixel != 32:
        raise SystemExit(f"unsupported depth: {img.bits_per_pixel} bpp")
    raw = ctypes.string_at(img.data, img.bytes_per_line * h)
    rgb = bytearray()
    for row in range(h):                  # BGRX, little-endian -> RGB, one filter byte per row
        line = raw[row * img.bytes_per_line: row * img.bytes_per_line + 4 * w]
        out = bytearray(3 * w)
        out[0::3], out[1::3], out[2::3] = line[2::4], line[1::4], line[0::4]
        rgb += b"\0" + out
    return w, h, bytes(rgb)


def png(w: int, h: int, rows: bytes) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows, 6)) + chunk(b"IEND", b""))


if __name__ == "__main__":
    w, h, rows = grab()
    with open(sys.argv[1], "wb") as fh:
        fh.write(png(w, h, rows))
    print(f"{sys.argv[1]}: {w}x{h}")
