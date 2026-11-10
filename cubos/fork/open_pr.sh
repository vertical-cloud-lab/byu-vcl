#!/usr/bin/env bash
# Rebuild vcl/cubxl-local-patches from the patch series next to this script,
# check it against the recorded tree, push it to vertical-cloud-lab/CubOS and
# open a draft PR into that fork's main. See README.md in this directory.
#
#   bash cubos/fork/open_pr.sh --dry-run   # build and verify only, no network writes
#   bash cubos/fork/open_pr.sh             # build, verify, push, open the PR
#
# Credentials: if CUBOS_FORK_PAT is set it is used for both the push and gh,
# through a one-shot credential helper, so it never appears in argv, a remote
# URL or .git/config. Otherwise your own git credentials and gh login are used.
# Never echo the token.
set -euo pipefail

FORK=vertical-cloud-lab/CubOS
BRANCH=vcl/cubxl-local-patches
BASE_COMMIT=496819cec06a83fb97ef75734249809c16dc6fa9   # upstream main, 2026-09-14; what the CubXL Pi runs
EXPECTED_TREE=5cca000fdf1a75c83462004081e21caaa4649137 # 496819c + the four patches == the Pi's ~/CubOS on 2026-11-10
EXPECTED_HEAD=a5fbfb7adae91145277fc19d275cef34cab5a505 # as first built; reproduced when committer is claude[bot]
TITLE="CubXL: the CubOS the lab's Pi runs (496819c + 4 local patches)"

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dry_run=0
[[ "${1:-}" == "--dry-run" ]] && dry_run=1

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
git clone -q --filter=blob:none --no-checkout "https://github.com/$FORK.git" "$work/CubOS"
cd "$work/CubOS"
git -c advice.detachedHead=false checkout -q "$BASE_COMMIT"
git switch -q -c "$BRANCH"

# --keep-cr: upstream stores driver.py with CRLF line endings, and git am
# strips CRs by default, which breaks commit 4. The series' own author lines
# are kept; the committer is fixed so the commit
# hashes come out the same wherever this runs.
GIT_COMMITTER_NAME="claude[bot]" GIT_COMMITTER_EMAIL="41898282+claude[bot]@users.noreply.github.com" \
  git am -q --keep-cr --committer-date-is-author-date "$here"/vcl-cubxl-local-patches/*.patch

tree="$(git rev-parse 'HEAD^{tree}')"
if [[ "$tree" != "$EXPECTED_TREE" ]]; then
  echo "Tree mismatch: built $tree, expected $EXPECTED_TREE. Not pushing." >&2
  exit 1
fi
head="$(git rev-parse HEAD)"
echo "Built $BRANCH at ${head:0:7} (tree ${tree:0:7}, matches the Pi)."
[[ "$head" == "$EXPECTED_HEAD" ]] || echo "Note: commit hashes differ from the first build (${EXPECTED_HEAD:0:7}); the tree is identical."
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

# No force: if the branch already exists with different commits, stop and look.
git "${push_args[@]}" push "https://github.com/$FORK.git" "HEAD:refs/heads/$BRANCH"

existing="$(gh pr list --repo "$FORK" --head "$BRANCH" --state all --json url --jq '.[0].url // empty')"
if [[ -n "$existing" ]]; then
  echo "PR already exists: $existing"
  exit 0
fi
gh pr create --repo "$FORK" --base main --head "$BRANCH" --draft \
  --title "$TITLE" --body-file "$here/PR_BODY.md"
