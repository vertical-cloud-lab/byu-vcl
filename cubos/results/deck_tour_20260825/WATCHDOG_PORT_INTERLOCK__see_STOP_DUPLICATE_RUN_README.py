import fcntl, os, termios, time, serial
D = "/home/vcl/run_20260825_deck_tour"
LOG, REL = D + "/watchdog_interlock.log", D + "/RELEASE_INTERLOCK"
def log(m):
    with open(LOG, "a") as f:
        f.write(time.strftime("%H:%M:%S", time.gmtime()) + " UTC  " + m + "\n")
log("v2 interlock: opening port + kernel TIOCEXCL (all other opens will EBUSY)")
try:
    s = serial.Serial("/dev/ttyUSB0", 115200, timeout=1.0)
    fcntl.ioctl(s.fd, termios.TIOCEXCL)
except Exception as e:
    log("FAILED: %r" % (e,)); raise SystemExit(1)
time.sleep(2.0)
log("post-open read: %r" % (s.read(300),))
for cmd in (b"?", b"$I\n", b"$$\n"):
    try:
        s.reset_input_buffer(); s.write(cmd); time.sleep(1.2)
        log("%r -> %r" % (cmd, s.read(1200)))
    except Exception as e:
        log("%r error: %r" % (cmd, e))
deadline, last = time.time() + 90 * 60, 0.0
while time.time() < deadline and not os.path.exists(REL):
    if time.time() - last >= 30:
        try:
            s.reset_input_buffer(); s.write(b"?")
            log("status probe: %r" % (s.read(200),))
        except Exception as e:
            log("probe error (usb gone?): %r" % (e,)); break
        last = time.time()
    time.sleep(2)
log("releasing interlock, closing port")
s.close()
