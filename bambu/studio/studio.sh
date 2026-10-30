#!/bin/bash
# Bambu Studio GUI on the Xvfb display, software GL, WebKit without compositing.
export DISPLAY=:99 GDK_BACKEND=x11 LIBGL_ALWAYS_SOFTWARE=1 \
       WEBKIT_DISABLE_COMPOSITING_MODE=1 WEBKIT_DISABLE_DMABUF_RENDERER=1 NO_AT_BRIDGE=1
exec /home/runner/bambu/squashfs-root/AppRun "$@"
