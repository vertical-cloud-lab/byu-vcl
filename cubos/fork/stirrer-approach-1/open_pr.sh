#!/usr/bin/env bash
# Rebuild vcl/stirrer-approach-1 from the patch series next to this script,
# check it against the tested tree, push it to vertical-cloud-lab/CubOS and
# open a draft PR into that fork's main. See README.md in this directory.
#
#   bash cubos/fork/stirrer-approach-1/open_pr.sh --dry-run   # build and verify only
#   bash cubos/fork/stirrer-approach-1/open_pr.sh             # build, verify, push, open the PR
#
# The series is built on upstream main 6e5cffe (2026-11-22). The fork's main
# was upstream b4f18ec (2026-11-08), 28 commits behind, when this was staged.
# If the fork's main doesn't contain the base yet, the script fast-forwards it
# to upstream main first (`gh repo sync`, which is what GitHub's "Sync fork"
# button does and which refuses anything but a fast-forward), so the PR shows
# only the stirrer commits. It stops instead if the fork's main has commits of
# its own. Pass --no-sync to stop rather than sync.
#
# Credentials: if CUBOS_FORK_PAT is set it is used for the push, the sync and
# gh, through a one-shot credential helper, so it never appears in argv, a
# remote URL or .git/config. Otherwise your own git credentials and gh login
# are used. Never echo the token.
set -euo pipefail

UPSTREAM=Ursa-Laboratories/CubOS
FORK=vertical-cloud-lab/CubOS
BRANCH=vcl/stirrer-approach-1
BASE_COMMIT=6e5cffe49e32639c3cb2b8c0499521d9fc3af2b6   # upstream main, 2026-11-22
EXPECTED_TREE=7409d6d4fdee282da3b2acff45a030ee2a37d285 # the tree the tests ran on (2026-11-26)
TITLE="Deck-mounted stirrer instrument and stir command (approach 1, byu-vcl#133)"

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dry_run=0
sync=1
for arg in "$@"; do
  case "$arg" in
    --dry-run) dry_run=1 ;;
    --no-sync) sync=0 ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
git clone -q --filter=blob:none --no-checkout "https://github.com/$UPSTREAM.git" "$work/CubOS"
cd "$work/CubOS"
git -c advice.detachedHead=false checkout -q "$BASE_COMMIT"
git switch -q -c "$BRANCH"

# The series' own author lines are kept; the committer and dates are fixed so
# the commit hashes come out the same wherever this runs.
GIT_COMMITTER_NAME="claude[bot]" GIT_COMMITTER_EMAIL="41898282+claude[bot]@users.noreply.github.com" \
  git am -q --keep-cr --committer-date-is-author-date "$here"/patches/*.patch

tree="$(git rev-parse 'HEAD^{tree}')"
if [[ "$tree" != "$EXPECTED_TREE" ]]; then
  echo "Tree mismatch: built $tree, expected $EXPECTED_TREE. Not pushing." >&2
  exit 1
fi
head="$(git rev-parse HEAD)"
echo "Built $BRANCH at ${head:0:7} (tree ${tree:0:7}, the tested tree)."
git log --oneline "$BASE_COMMIT..HEAD"

if (( dry_run )); then
  echo "Dry run: not pushing."
  exit 0
fi

push_args=()
if [[ -n "${CUBOS_FORK_PAT:-}" ]]; then
  # The helper string is single-quoted, so the token is expanded only inside
  # git's helper subprocess, from the environment.
  push_args=(-c credential.helper= -c 'credential.helper=!f() { echo username=x-access-token; echo "password=$CUBOS_FORK_PAT"; }; f')
  export GH_TOKEN="$CUBOS_FORK_PAT"
fi

# Does the fork's main already contain the base? If it is merely behind
# upstream, fast-forward it; if it has diverged, stop and let a person look.
git fetch -q "https://github.com/$FORK.git" main:refs/remotes/fork/main
if ! git merge-base --is-ancestor "$BASE_COMMIT" fork/main; then
  git fetch -q origin main:refs/remotes/upstream/main
  if ! git merge-base --is-ancestor fork/main upstream/main; then
    echo "The fork's main ($(git rev-parse --short fork/main)) has commits upstream doesn't. Not syncing; rebase or retarget by hand." >&2
    exit 1
  fi
  if (( ! sync )); then
    echo "The fork's main ($(git rev-parse --short fork/main)) lacks $BASE_COMMIT. Sync the fork (fast-forward) and rerun, or drop --no-sync." >&2
    exit 1
  fi
  echo "Fast-forwarding $FORK main $(git rev-parse --short fork/main) -> upstream main $(git rev-parse --short upstream/main)."
  gh repo sync "$FORK" --source "$UPSTREAM" --branch main
fi

# No force: if the branch already exists with different commits, stop and look.
git "${push_args[@]}" push "https://github.com/$FORK.git" "HEAD:refs/heads/$BRANCH"

existing="$(gh pr list --repo "$FORK" --head "$BRANCH" --state all --json url --jq '.[0].url // empty')"
if [[ -n "$existing" ]]; then
  echo "PR already exists: $existing"
  exit 0
fi
gh pr create --repo "$FORK" --base main --head "$BRANCH" --draft \
  --title "$TITLE" --body-file "$here/PR_BODY.md"
