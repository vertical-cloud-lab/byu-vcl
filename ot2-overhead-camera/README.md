# OT-2 Overhead Camera — Optics Test Procedure

Proof-of-concept image capture for the fixed overhead configuration from
[`ot2-overhead-camera-options.md`](../ot2-overhead-camera-options.md)
(Sections 5b and 11): **Raspberry Pi 5 + HQ Camera (IMX477) + 8–50 mm zoom
lens**, imaging a 96-well plate on the OT-2 deck from ~24" (610 mm) through a
plexiglass cutout.

Goal: confirm the optics are good enough (framing, focus, sharpness,
lighting) *before* any permanent mounting or plexiglass cutting. A tripod,
clamp, or even a cardboard jig at roughly the right height is fine for these
tests.

Two scripts, both standalone (no MQTT/S3/AWS credentials needed for this
test — that integration comes later and reuses the
[a1_cam](https://github.com/AccelerationConsortium/ac-dev-lab/tree/main/src/ac_training_lab/a1_cam)
architecture):

| Script | Purpose |
|---|---|
| `preview_server.py` | Live MJPEG stream in a browser over Tailscale, with a numeric focus score printed to the terminal — used to manually zoom/focus (the HQ Camera has **no autofocus**) |
| `capture_still.py` | Full-resolution (4056×3040) timestamped still with focus score, exposure, gain, and lux printed for comparing shots |

---

## 1. Hardware assembly

1. **Fit the C–CS adapter ring** (the ~5 mm spacer that ships with the HQ
   Camera) between the camera body and the lens. The 8–50 mm zoom is a
   **C-mount** lens and the HQ Camera is a CS-mount body — **without the
   adapter the lens will never reach focus.**
2. Make sure the **back-focus ring** on the camera body is at its default
   position and locked with its tiny screw (only adjust it later if you can't
   reach focus at the working distance).
3. Connect the camera to the Pi 5 with the **Pi 5 camera cable** (22-pin
   mini connector on the Pi end, 15-pin on the camera end — this is the
   separate PiShop cable in the order; the cable in the HQ Camera box is
   15-pin-to-15-pin and does *not* fit the Pi 5). Either CAM port works;
   blue tab on the cable faces per the connector markings.
4. Clip on the Active Cooler, insert the microSD (flashed in step 2), and
   power with the 27 W USB-C supply.

## 2. Flash Raspberry Pi OS Lite (headless)

Use the [Raspberry Pi Imager](https://www.raspberrypi.com/software/):

1. Choose **Raspberry Pi OS Lite (64-bit)** (Bookworm) for Raspberry Pi 5.
2. In the OS customization dialog (gear icon / "Edit settings"):
   - hostname: `ot2-cam`
   - enable SSH (password or key auth)
   - set a username/password
   - configure the lab WiFi SSID + password
3. Flash, insert into the Pi, boot, then from your laptop (same network):

   ```bash
   ssh <username>@ot2-cam.local
   sudo apt update && sudo apt full-upgrade -y
   ```

## 3. Tailscale

Same procedure as the streaming cameras
([bookworm-tailscale-instructions](https://github.com/AccelerationConsortium/ac-dev-lab/blob/main/src/ac_training_lab/a1_cam/bookworm-tailscale-instructions.txt)):

```bash
curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt update && sudo apt install -y tailscale
sudo tailscale up
```

`tailscale up` prints a login URL — authenticate with the lab tailnet
account. **@sgbaird may need to approve the device and/or assign it a tag**
on the tailnet admin console before it's reachable; post the device name
(`ot2-cam`) in the thread if you get stuck at that step. Then:

```bash
tailscale ip -4   # note this IP — used for the preview and scp below
```

## 4. Install camera software and get these scripts

```bash
sudo apt install -y git
git clone https://github.com/vertical-cloud-lab/byu-vcl.git
cd byu-vcl/ot2-overhead-camera
```

(If this branch isn't merged yet: `git switch copilot/add-overhead-camera-for-ot-2`.)

Run the setup script — it installs `python3-picamera2`, `rpicam-apps`, and
`python3-numpy` (system packages; do **not** `pip install picamera2`, it must
come from apt) and does a quick camera-detection check:

```bash
chmod +x setup.sh
./setup.sh
```

You should see `imx477` in the camera check. If nothing shows up, power off
and reseat both ends of the camera cable, then re-run `./setup.sh`.

## 5. Zoom and focus (live preview)

Position the camera ~24" (610 mm) above the deck surface, pointing straight
down at a 96-well plate (put something in a few wells — colored liquid,
precipitate, an empty well — so there's real content to judge).

```bash
python3 preview_server.py
```

Open `http://<tailscale-ip>:8000` in a browser. Then, on the lens:

1. **Aperture** ring fully open (F1.4) for max light while focusing.
2. **Zoom** ring until the plate fills ~80–90% of the frame width
   (~28 mm per the research doc).
3. **Focus** ring slowly while watching the focus score in the SSH
   terminal — it prints once per second and **higher = sharper**. Rock back
   and forth past the peak a couple of times, settle on the maximum, then
   lock the focus ring's thumb screw. Because the working distance is fixed,
   this only has to be done once.
4. Stop the aperture down a little (toward F2–F4) if the center is in focus
   but the corners aren't, then re-check focus. Press `Ctrl-C` to quit the
   preview when framing and focus look good.

## 6. Capture full-resolution stills

```bash
# Auto exposure — good first shot:
python3 capture_still.py -o plate_28mm_auto.jpg

# The plate is stationary, so if the image is dim, use a long manual exposure
# instead of cranking gain (less noise):
python3 capture_still.py -o plate_28mm_250ms.jpg --exposure 250 --gain 2
```

Each run saves a **4056×3040** JPEG and prints the focus score, exposure
time, gain, and estimated lux. Grab a few:

- one at your chosen zoom with auto exposure,
- one or two with longer manual exposures (`--exposure 150`, `250`, `500`),
- optionally one zoomed to ~50 mm on a single well to judge per-well detail.

Copy them back to your laptop to post in the thread:

```bash
scp '<username>@ot2-cam.local:~/byu-vcl/ot2-overhead-camera/*.jpg' .
```

## 7. Lighting

Ambient room light is usually enough for a static plate with a long
exposure, but for even, glare-free illumination the research doc
([Section 3b](../ot2-overhead-camera-options.md)) recommends a **USB LED ring
light (~$8–15)** around the plexiglass cutout. If shots look noisy even at
250–500 ms, that's the fix. Avoid a single point light that reflects off the
plexiglass straight into the lens — diffuse, ring, or side lighting works
best.

## 8. What to post back here

Per @sgbaird's request:
- The **captured images** (a few at different zoom/exposure settings).
- A **photo or short video of the setup** — camera on the arm above the
  plexiglass/deck, plate in position.
- The printed **focus scores / exposure / lux values** so we can judge
  sharpness and whether supplemental lighting is needed.

---

## Next step (later): MQTT/S3 integration

Once the optics check out, this Pi drops into the existing `a1_cam`
architecture from
[ac-dev-lab](https://github.com/AccelerationConsortium/ac-dev-lab/tree/main/src/ac_training_lab/a1_cam):
an MQTT `capture_image` command triggers a `picamera2` capture, uploads to
S3, and returns the image URI. The one change for the HQ Camera is that
there's **no autofocus cycle** — drop the `picam2.autofocus_cycle()` call
from `device.py` and rely on the fixed manual focus set in step 5.
`capture_still.py` here is deliberately a thin standalone version of that same
capture path so the optics can be validated before wiring up MQTT.