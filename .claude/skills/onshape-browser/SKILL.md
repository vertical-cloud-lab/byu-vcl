---
name: onshape-browser
description: Onshape in a browser with the lab account (ONSHAPE_USERNAME / ONSHAPE_PASSWORD, or the ONSHAPE_ADMIN_* pair in @claude-onshape-admin runs) - the SOCKS-tunnel browser rig through a lab Pi, attaching Playwright over CDP, sign-in selectors, exporting STL/STEP/Parasolid, sketching on the WebGL canvas, and sign-out and cleanup (rig.sh stop in its own Bash call). Use for any Onshape task the REST API can't do.
---

# Onshape in the browser

The Onshape rules in the root `CLAUDE.md` (and, for the admin account, its `@claude-onshape-admin` section) apply throughout.

**The route that works** is the one byu-vcl used on 2026-09-26
([PR 234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5842335279)):
headed Chrome on a virtual display on the runner, with its traffic sent out through a lab Pi
over an SSH SOCKS tunnel, so that Onshape sees the BYU network instead of a datacenter. Its
rig script is on that PR's branch; fetch it pinned, into `/tmp`, never into this checkout:

```bash
B=https://raw.githubusercontent.com/vertical-cloud-lab/byu-vcl/49677cfff31a67765d9182c01765bfa994a7545d/ot2-overhead-camera/lid-mount/onshape
mkdir -p /tmp/onshape-rig/record /tmp/onshape-rig/pi
curl -fsSL "$B/record/rig.sh" -o /tmp/onshape-rig/record/rig.sh && chmod +x /tmp/onshape-rig/record/rig.sh
curl -fsSL "$B/pi/xshot.py" -o /tmp/onshape-rig/pi/xshot.py
/tmp/onshape-rig/record/rig.sh start
/tmp/onshape-rig/record/rig.sh check    # the tunnel's exit network (ASN and org only), and a screenshot of the display
```

`rig.sh start` brings up Xvfb on `:99`, the tunnel on `127.0.0.1:1080` and Chrome with DevTools
on `127.0.0.1:9222`. Attach with Playwright's `chromium.connect_over_cdp("http://127.0.0.1:9222")`.

The tunnel goes through the CubXL Pi (`CUBXL_PI_USERNAME` / `CUBXL_PI_HOSTNAME`), as on
2026-09-26. The Pi only relays traffic: nothing is installed or written on it. If it is off
the tailnet, any other Pi this run can reach will do (set `PI_USER` and `PI_HOST`).

Signing in ([`sign_in()` in `onshape_ui.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/49677cf/ot2-overhead-camera/lid-mount/onshape/onshape_ui.py#L255-L276), selectors checked live):

1. Go to `https://cad.onshape.com/signin`. Click `input[name='username']`, type the e-mail and
   click `button.continue-button`.
2. Click `input[name='password']`, type the password and click `button.os-signin-button`.
3. Wait up to 60 s for the URL to contain `/documents`.

- **Read the values from the environment inside the script.** Never print them, pass them as
  command-line arguments, or take a screenshot while the form is filled in. Only take
  screenshots after you reach `/documents`.
- **Stop at the first failure: don't retry in a loop.** That covers a reCAPTCHA, a code
  prompt (`input[name='totpCode']`) and an error message. Take one screenshot, then report
  what you saw. Repeated failed sign-ins can lock the account, and every repo uses it.
- **To export,** use Onshape's own Export dialog (right-click the part or tab, then *Export*).
  The browser saves the file, so set a download directory under `/tmp`. Driving that dialog
  in headless Chrome worked on
  [digital-alloy-lab PR 174](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/174#issuecomment-6532349145).
- **Sketching and modelling are WebGL on a canvas.** DOM selectors don't reach the geometry,
  so use pointer moves and drags at screen coordinates, with a screenshot between moves.
  byu-vcl's `onshape_ui.py` has the techniques that worked.
- **Keep sessions short.** Do only what the request needs. Onshape's terms forbid automated
  access (§4(a)(ix)), so use the REST API whenever it can do the job.
- **Only open Onshape in the tunnelled browser.** The tunnel relays everything the browser
  loads, so any other site would reach the Pi's network too.
- **Clean up every time:** sign out from Onshape's user menu (*Sign out*). The redirect
  lags by a few seconds: wait about 5 s before checking that `/documents` sends you to
  `/signin`, or check that `/api/v6/users/sessioninfo` returns 204. Then run `rig.sh stop`,
  which deletes the browser profile, **in a Bash call of its own**. Its `pkill -f` patterns
  also match any shell whose command line contains the same text, so a `pgrep` naming the
  profile path in the same call gets that shell killed (digital-alloy-lab PR 180, 2026-11-10).
  Never save cookies or storage state outside `/tmp`, and never commit them.
