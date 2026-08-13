# CNMS 2026 deck — programmatic OneDrive/SharePoint access recipe

Working notes for accessing and editing the CNMS 2026 presentation
(`cnms-2026.pptx`) from GitHub Actions. Originally validated 2026-08-11 in
issue #175; **updated 2026-08-12 for the new password-protected sharing
link**. No secrets appear below.

- Sharing link (password-protected, view+edit):
  `https://byu-my.sharepoint.com/:p:/g/personal/sbaird9_byu_edu/IQCHjliOKtGXTZw5H8X9Km0sAbUEOuhNuORHw6sU-cXFJhg`
- Link password: workflow secret `ONEDRIVE_EDIT_LINK_PASSWORD` (never print it)
- Document UniqueId: `8e588e87-d12a-4d97-9c39-1fc5fd2a6d2c`
- Server-relative path: `/personal/sbaird9_byu_edu/Documents/cnms-2026.pptx`
- The original unprotected link (`...AX_PnOLHJ6SDsbqdijVtZVc`) has been
  **removed** — it now returns "This link has been removed." All access goes
  through the password gate.

## Step 1 — unlock the link (password required for ALL access)

Anonymous GET of the sharing link returns the `guestaccess.aspx` password page
(a standard ASP.NET form). Submit the password as a postback; on success the
response redirects to `Doc.aspx` (the PowerPoint web viewer) and the cookie
jar gains a guest `FedAuth` cookie that authorizes the REST API. A wrong
password stays on the page with "Link password is incorrect."

```python
import os, re, html, urllib.request, urllib.parse, http.cookiejar

pw = os.environ["ONEDRIVE_EDIT_LINK_PASSWORD"]
base = "https://byu-my.sharepoint.com"
share_url = base + "/:p:/g/personal/sbaird9_byu_edu/IQCHjliOKtGXTZw5H8X9Km0sAbUEOuhNuORHw6sU-cXFJhg"

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")]

page = op.open(share_url).read().decode("utf-8", "replace")
action = base + html.unescape(
    re.search(r'action="([^"]*guestaccess\.aspx[^"]*)"', page).group(1))
f = lambda n: (lambda m: html.unescape(m.group(1)) if m else "")(
    re.search(r'name="%s"[^>]*value="([^"]*)"' % n, page))
data = {
    "__EVENTTARGET": "btnSubmitPassword", "__EVENTARGUMENT": "",
    "SideBySideToken": f("SideBySideToken"),
    "__VIEWSTATE": f("__VIEWSTATE"),
    "__VIEWSTATEGENERATOR": f("__VIEWSTATEGENERATOR"),
    "__VIEWSTATEENCRYPTED": "",
    "__EVENTVALIDATION": f("__EVENTVALIDATION"),
    "txtPassword": pw,
}
resp = op.open(urllib.request.Request(
    action, urllib.parse.urlencode(data).encode(), method="POST"))
assert "Doc.aspx" in resp.url  # success → PowerPoint viewer + FedAuth cookie
```

The unlocked guest session identifies as **"Guest Contributor"**
(`/_api/web/currentuser`) with the `EditListItems` permission bit set — i.e.
the password gates entry, and entry grants edit.

## Step 2 — download

With the same opener/cookie jar:

```python
data = op.open(base + "/personal/sbaird9_byu_edu/_api/web/"
               "GetFileById(guid'8e588e87-d12a-4d97-9c39-1fc5fd2a6d2c')/$value").read()
```

(`GetFileByUniqueId` does not exist on this endpoint; use
`GetFileById(guid'...')`.)

## Write path A — REST upload (works only when the file is not open)

1. `POST /_api/contextinfo` with the cookies → `FormDigestValue`.
2. `POST .../GetFileById(guid'...')/$value` with headers `X-HTTP-Method: PUT`,
   `X-RequestDigest: <digest>`, body = new pptx bytes.
3. If someone has the deck open in PowerPoint, this returns **HTTP 423
   `SPFileLockException`** ("locked for shared use") — a lock, not a
   permission failure. Retry after the editor closes (lock lingers ~10 min),
   or use path B.

## Write path B — headless-browser co-authoring (works even while locked)

Runner has Chrome; `pip install playwright` and launch with
`channel="chrome"` (no browser download needed). Load the sharing link — the
password page renders first, so fill `#txtPassword` and click
`#btnSubmitPassword` — then wait ~40 s for the Office WOPI editor
(`powerpoint.officeapps.live.com` iframe) to boot; it opens directly in
**Editing** mode. Interact with page-level mouse coordinates (frame-URL
matching is unreliable); e.g. the Notes toggle sits in the status bar
bottom-right (~x=1157, y=890 at 1600×900). Typed changes autosave through
co-authoring and merge with any live human session; the stored blob reflects
them within ~1–2 min of closing the browser.

`python-pptx` edits of the downloaded file + path A is the cleaner route for
substantive content changes when the deck is not open.

### Precision drawing via co-authoring (validated 2026-08-12)

Used to build the 5-node horizontal timeline slide entirely in the web editor
while the owner was editing live (REST upload stays 423-locked the whole time).
Key facts:

- **Skip the password page in the browser**: inject the `FedAuth` cookie from
  the Step-1 unlock into the Playwright context (`ctx.add_cookies`) before
  loading the sharing link — lands directly in Editing mode.
- **Exact sizes**: the contextual **Shape** ribbon tab has numeric
  Width/Height fields; triple-click the field, type e.g. `0.34"`, Enter.
  (Verify it took — a missed click followed by a canvas drag can grab a resize
  handle and stretch the shape.)
- **Exact positions**: the slide maps linearly to canvas pixels (measure the
  slide's white bbox on a screenshot; ≈92.3 px/in at 96 % zoom, slide origin
  ≈(400,181) at 1780×960 viewport). Insert the shape, size it numerically,
  then mouse-drag its center to the computed pixel target; shapes snap onto
  the 4.5 pt spine cleanly. Verify positions by thresholding a screenshot
  (dark-pixel column profile) rather than trusting the drag.
- Arrow-key nudge moves a shape only ~0.01" per press — fine-tune only.
- `Arrange > Align` (Align to Slide) gives exact horizontal/vertical
  centering; keyboard shortcuts work (`Ctrl+A`/`Ctrl+E` inside a text box);
  if driving via an HTTP bridge, URL-encode `+` in key combos as `%2B`.
- **Slide masters/layouts CANNOT be edited in PowerPoint for the web**
  (Microsoft limitation — no Slide Master view). To make a built slide into a
  reusable layout: desktop PowerPoint (View → Slide Master, paste shapes into
  a new layout), or python-pptx + write path A once the file is closed.
  Duplicating the finished slide is a workflow-equivalent substitute.

Timeline slide geometry (as persisted; spine y = 4.60", 4.5 pt, x 0.90–12.44";
nodes evenly spaced 2.4" apart, diameters growing 0.22→0.46"; labels 2.2" wide
starting y = 4.96"): node centers x = 1.60, 4.00, 6.40, 8.80, 11.20 in.

## Security status (2026-08-12)

- New link: password enforced for view, download, and edit alike; wrong
  passwords rejected. ✅
- Old unprotected link: removed, returns an access-removed error. ✅
