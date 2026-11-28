---
name: tailscale-policy
description: Tailscale tailnet policy for the VCL Pis and CI runners - the CI OAuth client's tag pair (tag:stream-cam-test, tag:rpi-5-des4), the vertical-cloud-lab/tailscale-policy repo, grants vs ssh rules, the tcp:22 port inventory, SSH check mode, first-match rule order, and rotating the OAuth client. Use when an SSH or tailnet join is refused, or before changing tags, grants or ACLs.
---

# Tailnet policy and the CI OAuth client

The rules in the root `CLAUDE.md` apply throughout: never print a credential, hostname or IP, and treat every Pi as a live production device.

**An OAuth client with several tags must request every one of them.** The CI credential is
authorized for two tags, and asking for a subset is refused outright with `requested tags
[...] are invalid or not permitted` — the same error you get for a tag the client does not
own at all, which makes it look like a permissions problem rather than an all-or-nothing
one. That is why `claude.yml` passes `tags: tag:stream-cam-test,tag:rpi-5-des4` as a pair;
dropping either one breaks the join for both. Tags are fixed when a client is created —
the console offers only create, revoke and delete — so widening a client's reach means
minting a **new** client and rotating `TS_OAUTH_CLIENT_ID`/`TS_OAUTH_SECRET` in both GitHub
and `.claude/settings.local.json`. Two small console quirks cost real time: credential
descriptions are capped at 50 characters and reject anything non-alphanumeric (no hyphens),
and the same alphanumeric rule applies to auth-key descriptions created through the API.

**The policy file lives in `vertical-cloud-lab/tailscale-policy`, not the console.**
`policy.hujson` there is the source of truth: a pull request runs
`tailscale/gitops-acl-action` in `test` mode to validate it, and merging to `main` runs
`apply`, which replaces the live policy. Auth is OIDC workload identity, so there is no
long-lived secret. Edit by PR; editing in the admin console just gets overwritten by the
next merge.

`grants` was `src: ["*"], dst: ["*"], ip: ["*"]` until 12 September 2026 — every node could
reach every other node on every port, which made the `ssh` block the only real boundary
despite governing Tailscale SSH alone. It now mirrors the `ssh` block: people reach
everything, devices reach only their own tag group, and only on `tcp:22`. Tailscale needs
**both** a grant and an `ssh` rule for a connection, so `grants` must never be narrower than
`ssh` or SSH breaks with no useful error.

`tcp:22` is backed by an inventory, not a guess: `ss -tulnH` on every Pi (12 September 2026)
found SSH to be the only service bound to a tailnet-facing address. The stream cams *push*
RTMP to YouTube and serve nothing; CubOS listens on `127.0.0.1:8742` only; code-server on the
powder doser likewise. So a service that starts listening on a Pi is **unreachable from
other devices, CI runners included, until a port is added to that tag's grant** — deliberate,
and the reason to bind new services to loopback unless they genuinely need the tailnet.
Humans keep `"*"`. `cb154-01`, the CAEDM workstation in CB154, is deliberately outside all
of this: it carries `tag:caedm`, which no `ssh` rule and no device grant reference, so
Tailscale SSH to it is denied by policy even though the daemon still advertises it. Its
accounts are personal and university-managed, and tailnet identity must not stand in for
CAEDM's own login. `sudo tailscale set --ssh=false` on the machine itself is the remaining
belt-and-braces step.

Check mode on the stream cams is per user, per device, for the policy's `checkPeriod`
(default 12h): the first SSH prints a `login.tailscale.com/a/...` URL and holds the session
open until it is approved in a browser, after which further sessions in the window go
straight through. Running the SSH in the background with output to a file, then opening the
URL from the file, is what makes that workable from an agent session.

**SSH rules are first-match-wins, and the general `check` rule sits at the top.** A specific
`accept` rule further down does not override it: any `autogroup:member` reaching a device
tagged `tag:tailscale-ssh` gets check mode, whatever later rules say. Adding
`tag:tailscale-ssh` to a Pi that already had a user-scoped `accept` rule is therefore enough
to put browser re-authentication back in front of it — which is what happened to the CubXL
Pi. It also makes the `williamulbz@github` → `tag:tailscale-ssh` rule dead code. Tagged
sources are unaffected, so CI never sees check mode. If a named user should skip the
prompt, their rule has to move *above* the check rule.
