# OneDrive/SharePoint PowerPoint — programmatic access recipe

Working notes for downloading and editing a PowerPoint file shared via a
OneDrive/SharePoint sharing link, from a headless environment such as a CI
runner. Validated against a real password-protected OneDrive for Business
sharing link. No secrets appear below.

Terms used throughout:

- **Sharing link**: `https://<tenant>-my.sharepoint.com/:p:/g/personal/<owner>/<share-token>`
  (password-protected, view+edit)
- **Link password**: injected as an environment variable / workflow secret
  (e.g. `ONEDRIVE_EDIT_LINK_PASSWORD`) — never print it
- **Document UniqueId**: the file's GUID in the document library (visible in
  the `Doc.aspx` viewer URL after unlock, or via `/_api/web` once
  authenticated)
- **Site base**: `https://<tenant>-my.sharepoint.com/personal/<owner>`

## Step 1 — unlock the link (password required for ALL access)

Anonymous GET of the sharing link returns the `guestaccess.aspx` password page
(a standard ASP.NET form). Submit the password as a postback; on success the
response redirects to `Doc.aspx` (the PowerPoint web viewer) and the cookie
jar gains a guest `FedAuth` cookie that authorizes the REST API. A wrong
password stays on the page with "Link password is incorrect."

```python
import os, re, html, urllib.request, urllib.parse, http.cookiejar

pw = os.environ["ONEDRIVE_EDIT_LINK_PASSWORD"]
base = "https://<tenant>-my.sharepoint.com"
share_url = base + "/:p:/g/personal/<owner>/<share-token>"

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

On an edit-enabled link, the unlocked guest session identifies as
**"Guest Contributor"** (`/_api/web/currentuser`) with the `EditListItems`
permission bit set — i.e. the password gates entry, and entry grants edit.

## Step 2 — download

With the same opener/cookie jar:

```python
data = op.open(base + "/personal/<owner>/_api/web/"
               "GetFileById(guid'<unique-id>')/$value").read()
```

(`GetFileByUniqueId` does not exist on this endpoint; use
`GetFileById(guid'...')`.)

## Write path A — REST upload (works only when the file is not open)

1. `POST /_api/contextinfo` with the cookies → `FormDigestValue`.
2. `POST .../GetFileById(guid'...')/$value` with headers `X-HTTP-Method: PUT`,
   `X-RequestDigest: <digest>`, body = new pptx bytes.
3. If someone has the file open in PowerPoint, this returns **HTTP 423
   `SPFileLockException`** ("locked for shared use") — a lock, not a
   permission failure. Retry after the editor closes (lock lingers ~10 min),
   or use path B.

## Write path B — headless-browser co-authoring (works even while locked)

If the environment has system Chrome, `pip install playwright` and launch with
`channel="chrome"` (no browser download needed). Load the sharing link — the
password page renders first, so fill `#txtPassword` and click
`#btnSubmitPassword` — then wait ~40 s for the Office WOPI editor
(`powerpoint.officeapps.live.com` iframe) to boot; it opens directly in
**Editing** mode. Interact with page-level mouse coordinates (frame-URL
matching is unreliable). Typed changes autosave through co-authoring and merge
with any live human session; the stored blob reflects them within ~1–2 min of
closing the browser.

`python-pptx` edits of the downloaded file + path A is the cleaner route for
substantive content changes when the file is not open.

### Precision drawing via co-authoring

Validated by building a multi-shape diagram slide entirely in the web editor
while the file's owner was editing live (REST upload stays 423-locked the
whole time). Key facts:

- **Skip the password page in the browser**: inject the `FedAuth` cookie from
  the Step-1 unlock into the Playwright context (`ctx.add_cookies`) before
  loading the sharing link — lands directly in Editing mode.
- **Exact sizes**: the contextual **Shape** ribbon tab has numeric
  Width/Height fields; triple-click the field, type e.g. `0.34"`, Enter.
  (Verify it took — a missed click followed by a canvas drag can grab a resize
  handle and stretch the shape.)
- **Exact positions**: the slide maps linearly to canvas pixels. Measure the
  slide's white bounding box on a screenshot to derive the px/inch scale and
  slide origin for your viewport/zoom. Insert the shape, size it numerically,
  then mouse-drag its center to the computed pixel target; shapes snap onto
  thin guide lines cleanly. Verify positions by thresholding a screenshot
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

## Verifying persistence

Always confirm an edit landed by re-downloading the stored blob (Step 2)
~1–2 minutes after editing and inspecting the pptx XML. Do not trust the web
editor's "Saved" indicator or an apparently-successful upload alone.
