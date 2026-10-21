# Look-only Remote Desktop to the EZstat Pro PC

Scripts for a look-only Remote Desktop session to the EZstat Pro's Windows 7 PC
(`192.168.231.10`), with screenshots, made from the CubXL Pi, which is cabled to the PC
([#231](https://github.com/vertical-cloud-lab/byu-vcl/issues/231)). They need
`CUBXL_PI_USERNAME`, `CUBXL_PI_HOSTNAME`, `POTENTIOSTAT_PC_USERNAME` and
`POTENTIOSTAT_PC_PASSWORD`. Only `freerdp3-x11` and `xvfb` are needed on the Pi, and both
are already installed.

```bash
S=scripts/ezstat-pc-rdp
$S/rdp_look.sh start                          # copy the helper to /dev/shm on the Pi, connect
$S/rdp_look.sh peek /tmp/ezrdp/raw/peek1      # current frame + FreeRDP log (redacted)
$S/rdp_look.sh shots /tmp/ezrdp/raw/shots 38 2   # 38 frames, 2 s apart; repeats dropped
$S/rdp_look.sh stop                           # disconnect, check, clean up
python $S/xwd_to_png.py /tmp/ezrdp/raw/shots/f0.xwd.gz /tmp/ezrdp/raw/shot1.png
python $S/redact_png.py /tmp/ezrdp/raw/shot1.png docs/images/ezstat-pc/<name>.png [x0,y0,x1,y1 ...]
```

Keep raw frames outside the repo. Commit only the output of `redact_png.py`, after looking at it.

## How it keeps to "look only"

- **Credentials:** built with bash's `printf` builtin and sent over SSH's stdin to
  `xfreerdp3 /args-from:stdin`, so they never appear in argv or on disk on either machine.
  They're passed on fd 7, because `xvfb-run` uses fd 3 and closes it for its command.
- **No redirection:** `-clipboard` turns the clipboard off, and drives and printers are off
  unless requested. FreeRDP still loads its audio channel, with a silent ("fake") backend.
- **No input from us:** nothing drives the virtual display's keyboard or mouse, and
  `-mouse-motion` would drop pointer motion anyway. FreeRDP itself sends a little input when
  the session starts, as mstsc does: a Tab key *release*, a toggle-key sync (Caps, Num and
  Scroll Lock off), another Tab release, and a pointer move to the virtual pointer at the
  screen centre. It sends these twice, whatever the X focus is (`freerdp_focus_required` →
  `xf_keyboard_focus_in` in FreeRDP 3.15's `xf_client.c`). There are no key presses or
  clicks.
- **Disconnect, never log off:** `stop` sends SIGTERM to `xfreerdp3`. Its exit code 145 is
  `XF_EXIT_CONNECT_CANCELLED`; a log-off would be 2. The Windows session stays signed in,
  in the disconnected state.
- **Safety net:** the session runs under `timeout 360`. If `stop` never comes, that kills
  `xfreerdp3` and Xvfb, and the temp directory is deleted.
- **Screenshots** are copies of Xvfb's `-fbdir` framebuffer file, in XWD format. **The XWD
  header contains the Pi's hostname**, so convert to PNG and never commit an XWD.

**It still takes over the PC's screen.** Windows 7 allows one session. Connecting moves the
signed-in session off the PC's own monitor, so anyone at the PC sees the sign-in screen.
Signing in there brings back the same session, with everything still running.

## Run of 2026-10-21

| | |
|---|---|
| Connected | 23:49:34 UTC. The desktop had drawn 5 s later. There was no sign-in screen and no "another user" dialog |
| Screenshots | [`2026-10-21-rdp-desktop-1.png`](../../docs/images/ezstat-pc/2026-10-21-rdp-desktop-1.png) at 23:50:53.7 and [`-2.png`](../../docs/images/ezstat-pc/2026-10-21-rdp-desktop-2.png) at 23:51:03.8 UTC. The only change between them is the taskbar clock, 5:50 → 5:51 PM ([crop](../../docs/images/ezstat-pc/2026-10-21-rdp-clock-1-vs-2.png)) |
| Redaction | OCR found no instance of the username. 13 desktop labels that are people's names or look like user IDs were blacked out, since this repo is public |
| Disconnected | 23:51:41 UTC, `xfreerdp3` exit 145 |
| Afterwards | `deckcam` active (same PID, no restarts). No `xfreerdp3`, `Xvfb`, `xvfb-run` or temp files left on the Pi |
