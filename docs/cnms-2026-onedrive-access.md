# CNMS 2026 deck — programmatic OneDrive/SharePoint access recipe

Working notes for accessing and editing the CNMS 2026 presentation
(`cnms-2026.pptx`, "Agentic Lifestyles in the Era of AI") from GitHub Actions.
Validated 2026-08-11/12 in issue #175. No secrets appear below.

- Sharing link: `https://byu-my.sharepoint.com/:p:/g/personal/sbaird9_byu_edu/IQCHjliOKtGXTZw5H8X9Km0sAX_PnOLHJ6SDsbqdijVtZVc?e=RJaeqI`
- Document UniqueId: `8e588e87-d12a-4d97-9c39-1fc5fd2a6d2c`
- Server-relative path: `/personal/sbaird9_byu_edu/Documents/cnms-2026.pptx`

## Read/download (no password required)

1. `curl -sSL -c cookies.txt -A "Mozilla/5.0 ..." <sharing link>` — lands in the
   web viewer and stores a guest `FedAuth` cookie. The anonymous guest session
   identifies as **"Guest Contributor"** (`/_api/web/currentuser`), i.e. it has
   write permission with no password prompt.
2. Download:
   `curl -b cookies.txt "https://byu-my.sharepoint.com/personal/sbaird9_byu_edu/_api/web/GetFileById(guid'<UniqueId>')/$value" -o cnms-2026.pptx`
   (Note: `GetFileByUniqueId` does not exist on this endpoint; use `GetFileById(guid'...')`.)

## Write path A — REST upload (works only when the file is not open)

1. `POST /_api/contextinfo` with the cookies → `FormDigestValue`.
2. `POST .../GetFileById(guid'...')/$value` with headers `X-HTTP-Method: PUT`,
   `X-RequestDigest: <digest>`, body = new pptx bytes.
3. If someone has the deck open in PowerPoint, this returns **HTTP 423
   `SPFileLockException`** ("locked for shared use") — that is a lock, not a
   permission failure. Retry after the editor closes (lock lingers ~10 min), or
   use path B.

## Write path B — headless-browser co-authoring (works even while locked)

Runner has Chrome; `pip install playwright` and launch with
`channel="chrome"` (no browser download needed). Load the sharing link, wait
~40 s for the Office WOPI editor (`powerpoint.officeapps.live.com` iframe) to
boot — it opens directly in **Editing** mode. Interact with page-level mouse
coordinates (frame-URL matching is unreliable); e.g. the Notes toggle sits in
the status bar bottom-right (~x=1157, y=890 at 1600×900). Typed changes
autosave through co-authoring and merge with any live human session; the
stored blob reflects them within ~1–2 min of closing the browser.

`python-pptx` edits of the downloaded file + path A is the cleaner route for
substantive content changes when the deck is not open.

## Security note

The `ONEDRIVE_EDIT_LINK_PASSWORD` secret was never requested by any flow —
anonymous link holders get edit access outright. Anyone with the URL can view,
download, **and edit** the deck.
