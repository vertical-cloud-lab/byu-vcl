# Claude Science vs. our `@claude` GitHub Actions setup

Research for [#326](https://github.com/vertical-cloud-lab/byu-vcl/issues/326), 2026-11-05.
Sources: the [Claude Science docs](https://claude.com/docs/claude-science/overview) for
version 0.1.71 (27 October 2026), Anthropic's public GitHub repositories, coverage
outside Anthropic, and the workflow files of every `vertical-cloud-lab` repository that
runs Claude.

## Short answer

- **Claude Science is a local workbench around the same Claude models, not a new model.**
  Anthropic told TechCrunch it is "not a new AI model and not a more capable model for
  biology"
  ([TechCrunch, 30 June](https://techcrunch.com/2026/06/30/anthropics-claude-science-bets-on-workflow-not-a-new-model-to-win-over-scientists/)).
  The app is the product: sandboxed Python/R/shell kernels, a curated set of connectors
  and skills, versioned artifacts with a provenance record, and a background reviewer.
- **The pieces that matter most to us are closed.** The reviewer, the provenance store and
  the app itself are not published. The formats are open: connectors are MCP servers, and
  skills are the same `SKILL.md` folders Claude Code uses. Most of the curated connectors
  and skills are not published, and nearly all of them are for the life sciences.
- **It can't replace `@claude` on GitHub.** Sign-in is a claude.ai subscription login in
  a browser, and there is no API-key, headless or CI mode. Linux builds are x64 only, so
  it can't run on our arm64 Pis. Its sessions and files stay in `~/.claude-science` on one
  computer instead of landing in git and an issue thread.
- **It shares usage limits with Claude Code.** The docs say "Your Claude Science usage
  counts toward the same usage limits as the rest of your Claude plan, including Claude
  Code". All 10 repos authenticate with `CLAUDE_CODE_OAUTH_TOKEN`. If that token belongs to
  the same account someone uses for Claude Science, the two draw on the same 5-hour and
  weekly limits.
- **What to do:** keep `@claude` as the backbone. Pilot Claude Science for interactive
  analysis and literature work, where a person is at the keyboard. Bring its two best ideas
  into our workflows: skills that load on demand, and a reviewer pass. Separately, move
  four repos' Tailscale login to workload identity, as two repos already do.

## What Claude Science is

Timeline, from the [changelog](https://claude.com/docs/claude-science/changelog):

- **30 June 2026, version 0.1.14:** public beta on macOS and Linux
  ([announcement](https://www.anthropic.com/news/claude-science-ai-workbench)).
- **10 September 2026, version 0.1.47:** Windows support.
- **27 October 2026, version 0.1.71:** current release.

During development it was codenamed "Operon"
([TestingCatalog](https://www.testingcatalog.com/anthropic-tests-claude-operon-for-scientific-research-in-biology/)).

| Part | What it does | Docs |
| --- | --- | --- |
| App and access | Desktop app, or `claude-science serve`, which serves a web UI on `127.0.0.1`. For a server, you reach it through an SSH tunnel. Linux must be **x64 with glibc**: "arm64 and musl-based distributions such as Alpine aren't supported". You sign in with a Pro, Max, Ultra, Team or Enterprise account; "No API key is required", and none can be used. | [get started](https://claude.com/docs/claude-science/get-started), [remote Linux server](https://claude.com/docs/claude-science/run-on-remote-linux-server), [CLI](https://claude.com/docs/claude-science/command-line-settings) |
| Sandbox and permissions | Code runs in an OS sandbox: bubblewrap and socat on Linux. Network access is denied by default, behind a local proxy with an allowlist. Each new folder, network host, connector tool or remote job gets a permission card. Auto mode lets a safety classifier approve routine steps. `--dangerously-skip-approvals` exists but is meant only for disposable machines. | [core concepts](https://claude.com/docs/claude-science/core-concepts), [auto mode](https://claude.com/docs/claude-science/auto-mode) |
| Kernels and environments | Python and R kernels persist across steps and stop after about 30 minutes idle. Packages come from conda, pip, CRAN and Bioconductor; there is no `apt` or `sudo`. GPUs on Linux hosts can be used. | [tools and environments](https://claude.com/docs/claude-science/tools-and-environments) |
| Connectors (MCP) | Featured connectors are on by default and read-only, mostly life-sciences databases (Ensembl, UniProt, gnomAD, PDB/AlphaFold DB, GEO, cBioPortal, PubChem/ChEBI, openFDA). Two are general: **Literature Graph** (OpenAlex, arXiv) and **Research Resources** (Grants.gov, Antibody Registry). Four come from the claude.ai directory: PubMed, Clinical Trials, ChEMBL, bioRxiv. You can add any MCP server as a remote URL or a local command. | [connectors and skills](https://claude.com/docs/claude-science/connectors-and-skills), [custom connectors](https://claude.com/docs/claude-science/custom-connectors) |
| Skills | Featured skills: literature review, indication dossier, and model skills for AlphaFold2, Boltz-2, Chai-1, ESMFold2, OpenFold3, ProteinMPNN, DiffDock, ESM-2, Evo 2, Borzoi, scGPT and scvi-tools. You can write, upload or **import skills from GitHub**, or have Claude turn a finished session into a skill. Admins share skills by keeping "one `skills/<name>/SKILL.md` folder per skill" in a repository. | [connectors and skills](https://claude.com/docs/claude-science/connectors-and-skills), [admin controls](https://claude.com/docs/claude-science/admin-controls) |
| Artifacts and provenance | Every saved file is versioned. Each version has a Provenance view with five tabs: Messages, Code (download as a script or notebook), Execution Log ("the authoritative record of what ran"), Environment (every package version) and Review. | [artifacts](https://claude.com/docs/claude-science/artifacts) |
| Reviewer and specialists | An independent agent rereads the responses, the plan, the artifacts and the execution record, and flags claims that don't match what ran: uncomputed results, wrong values, unsupported citations, DOIs that resolve to other papers, skipped plan steps. It "doesn't re-run analyses". You can add your own criteria under Settings > Specialists. | [the reviewer](https://claude.com/docs/claude-science/the-reviewer), [glossary](https://claude.com/docs/claude-science/glossary) |
| Compute | SSH hosts read from `~/.ssh/config`, with Slurm `sbatch` if the host has it. "Remote jobs run outside the sandbox, as your user on the host." Also your own Modal account, and model endpoints such as NVIDIA BioNeMo NIM. | [remote compute clusters](https://claude.com/docs/claude-science/remote-compute-clusters), [compute providers](https://claude.com/docs/claude-science/compute-providers) |
| Literature access | Open-access full text first: Unpaywall, Semantic Scholar, PMC, then CrossRef. Then publisher API keys (Elsevier, Springer Nature) or a library EZproxy URL plus a session cookie. | [literature access](https://claude.com/docs/claude-science/literature-access) |
| Other | Projects with custom instructions, delegation to parallel sub-agents, local memory, comments pinned to artifacts, S3/GCS/Azure storage. | [core concepts](https://claude.com/docs/claude-science/core-concepts), [cloud storage](https://claude.com/docs/claude-science/cloud-storage) |

**Data.** Files stay on the computer, but anything Claude reads goes to Anthropic as part
of the conversation. Zero data retention, a HIPAA business associate agreement (BAA), and
inference "through a third-party cloud platform or your own cloud tenancy" are not available
([data page](https://claude.com/docs/claude-science/how-claude-science-works-with-your-data)).
Plans are the same as for Claude Code. The
[Team plan for scientists](https://claude.com/programs/team-plan-for-scientists) is a
discounted academic option. The launch post also announced an AI for Science programme:
up to 50 projects, up to $30,000 in credits, and up to $2,000 of Modal compute for
selected projects.

## Where the "special sauce" is, and what is open

| Piece | Open? | Where it lives |
| --- | --- | --- |
| Models | The same Claude models as everywhere else | Biology safety filters can stop a session, or switch it to another model ([safeguards](https://claude.com/docs/claude-science/safeguards)) |
| Connector protocol (MCP) | Open standard | Any MCP server works in Claude Code, Claude Science and claude.ai |
| Featured connectors (Ensembl, UniProt, PubChem, OpenAlex/arXiv, …) | **Not published.** No source in the `anthropics` org. | Bundled with the app |
| Directory connectors (PubMed, Clinical Trials, ChEMBL, bioRxiv) | Hosted. They can also be used from claude.ai and Claude Code. | [claude.com/connectors](https://claude.com/connectors) |
| Earlier life-sciences MCP plugins | Removed from [`anthropics/life-sciences`](https://github.com/anthropics/life-sciences) on 23 October 2026; still in its history at [`e96556b`](https://github.com/anthropics/life-sciences/blob/e96556b/.claude-plugin/marketplace.json) | 10x Genomics, PubMed, BioRender, Synapse, Wiley, bioRxiv, ClinicalTrials.gov, ChEMBL, Owkin, Open Targets, ToolUniverse, Medidata, Consensus, Cortellis, AdisInsight |
| Skill format (`SKILL.md`) | Open; the same format Claude Code uses ([`anthropics/skills`](https://github.com/anthropics/skills)) | Claude Science imports skills straight from GitHub |
| Featured science skills (literature review, indication dossier, AlphaFold2/Boltz-2/…) | **Not published** | Bundled with the app |
| Published science skills | `anthropics/life-sciences`, Apache-2.0: `clinical-trial-protocol`, `scientific-problem-selection`, `binder-gauntlet`, and `clinical-trial-forecast`, which runs only in Claude Science with Delegation on | The repository's [README](https://github.com/anthropics/life-sciences) |
| Removed skills, still in git history | `scvi-tools`, `single-cell-rna-qc`, `nextflow-development`, and `instrument-data-to-allotrope`, which converts instrument files to the Allotrope format and is the closest to lab automation | [`e96556b`](https://github.com/anthropics/life-sciences/tree/e96556b) |
| Protein and genomics inference kits | [`anthropics/uplifting-biomolecular-modeling`](https://github.com/anthropics/uplifting-biomolecular-modeling), Apache-2.0: 36 speed-up kits for structure-prediction and protein-design tools, published as "not maintained" | Accompanies a blog post |
| Sandbox | The same Linux requirements (bubblewrap ≥ 0.8, socat, proxy-filtered network) as Anthropic's open-source [`sandbox-runtime`](https://github.com/anthropics/sandbox-runtime), which Claude Code uses. The docs don't say the code is shared. | |
| Reviewer, provenance graph, artifact store, the app | **Closed** | A third-party teardown is the best public description (below) |

[Dissecting Claude Science](https://feitong.phd/essays/dissecting-claude-science/) took apart
version 0.1.15-dev on 6 July 2026. It found:

- **Structure:** a background daemon runs the analysis kernels and a separate control REPL
  that uses only the standard library. Only the control REPL can call MCP; data reaches
  the analysis kernels as JSON handoff files.
- **Reviewer:** read-only, and its first rule is "Trace, don't recompute".
- **Export:** an exported notebook replays recorded model and connector responses from
  `operon_tape.json`. The author calls this "portability, not full recomputation".

A GitHub repository claims to hold the app's system prompts. Its source is undocumented,
so it isn't used here.

**Verdict:** most of the difference lies in the harness (sandbox, permissions, kernels,
provenance, reviewer, UI) and in the curated content. The formats are open, but the curated
connectors and skills are mostly closed and mostly not about our fields. We can copy the
ideas, but there's nothing to download and drop in.

## What people say

A search pass on 2026-11-05 collected this. **[O]** marks opinion or a single anecdote.

- **Attention.** The main Hacker News thread
  ([item 48735770](https://news.ycombinator.com/item?id=48735770)) drew 564 points and 174
  comments on launch day. Little else got traction. Reddit and Bluesky were not reachable
  from the runner, so this is a gap, not evidence of silence.
- **Wins [O].**
  - Stephen Turner had it work unattended for about 2 hours and called it "a step change"
    ([blog](https://blog.stephenturner.us/p/test-driving-claude-science)).
  - An HN user built a gene-model assessment in "about 15 minutes" on "about 10% of a
    Claude Max subscription's tokens".
  - Early users in
    [The Scientist](https://www.the-scientist.com/early-verdicts-on-claude-science-faster-workflows-but-gaps-remain-74745)
    all said they would keep using it.
- **Usage limits.** Turner hit his 5-hour limit after two prompts and paid about $50 in
  extra usage **[O]**. Version 0.1.17 fixed idle sessions consuming usage.
- **The reviewer helps, but it is the same model checking itself.**
  - TechCrunch made that point **[O]**.
  - A single-run review found that the reviewer caught a false "verified citation" claim
    but missed a result credited to the wrong marker: "Provenance raised the ceiling on what
    you can inspect. It did not raise the floor on what is correct"
    ([Future Stack Reviews](https://future-stack-reviews.com/claude-science-review/)) **[O]**.
- **Safety filters block legitimate biology.** One example is a virologist blocked from
  dating Ebola genomes (estimating their most recent common ancestor) **[O]**. An issue
  also reports a session falling back from Opus to Haiku, which then hallucinated. The
  WebFetch tool used for this research refused to summarise the Hacker News thread for the
  same `[bio]` reason, which shows how broad these filters are.
- **Few connectors outside biology [O].**
  - "zero connectors for non biology" (HN).
  - A chemist found major chemical databases missing
    ([Northeastern](https://news.northeastern.edu/2026/06/30/anthropic-claude-science-launch/)).
- **Rough edges.** Reported bugs:
  - ARM64 Linux was served the x86 build.
  - NFS inode numbers above 2^63 break the sandbox.
  - WSL2 can't pass the GPU through to the sandbox.

  There is no public issue tracker for the app.
- **Comparisons [O].**
  - "like Claude Cowork for Science"
  - "Doesn't seem like much value-add beyond pointing Claude code at org mode"
  - Defenders point to the reviewer, and to the local-server design for locked-down data
    environments.
  - Open-source look-alikes exist, such as `ai4s-research/open-science`.
- **Lab automation.** Nothing was found about it driving robots or a self-driving-lab
  loop. Anthropic's own
  [enzyme work](https://www.anthropic.com/research/claude-discovers-novel-enzyme-system)
  says "We do our work in Claude Science and Claude Code… All of the lab work is
  performed by human scientists".

## What we already run

Workflow files from every repository in `vertical-cloud-lab` that runs Claude.
`BambuStudio` and `opentrons` are upstream forks running upstream CI and are left out.
This lists only the secret **names** referenced in YAML. Values are not readable, and this
run's token can't see private repos (such as `tailscale-policy`) or `sgbaird/*`.

| Repo | Claude workflows | Secrets referenced (claude.yml) | Tailscale tags |
| --- | --- | --- | --- |
| byu-vcl | `claude`, `claude-print`, `claude-youtube`, `post-queued-comments` | 48 | `stream-cam-test`, `rpi-5-des4` |
| powder-doser | `claude`, `claude-print` | 28 | `powder-doser-test` |
| robot-arms | `claude`, `claude-print`, `tailscale-check` | 26 | `rpi-5-eufi`, `rpi-5-76zj`, `rpi-5-mpzy` |
| tensegrity-optimization | `claude`, `claude-print`, `claude-code-review` | 18 | `ot2-stream-cam` |
| streamingLambda | `claude`, `claude-youtube`, `deploy`, `copilot-setup-steps` | 16 | `stream-cam-test` |
| digital-alloy-lab | `claude`, `tailscale-check` | 9 | `rpi-5-3ray`, `rpi-5-6ktj`, `rpi-zero2w-ex3f` |
| caliber | `claude`, `claude-print` | 8 | none |
| custom-induction-furnace, digital-wetlab, vclv | `claude` | 4 each | none |

Secret families and where they appear:

| Family | Repos |
| --- | --- |
| `CLAUDE_CODE_OAUTH_TOKEN`, `EDISON_PLATFORM_API_KEY`, `GH_READ_PAT_STAGING` | all 10 |
| Tailscale: `TS_OAUTH_CLIENT_ID` + long-lived `TS_OAUTH_SECRET` (+ `TAILNET_ID`) | byu-vcl, powder-doser, streamingLambda, tensegrity-optimization |
| Tailscale: `TS_OAUTH_CLIENT_ID` + `TS_AUDIENCE` (workload identity, no stored secret) | robot-arms, digital-alloy-lab |
| Bambu login (`BAMBU_*`, `bambu-print` environment) + printer serials | byu-vcl, caliber, powder-doser, robot-arms, tensegrity-optimization |
| Printer LAN access (`H2D_*`, `A1_MINI_*` IP and access code) | byu-vcl, powder-doser, robot-arms |
| Zenodo (production; sandbox and base URLs in 4 of the 5) | byu-vcl, caliber, powder-doser, robot-arms, tensegrity-optimization |
| Onshape API keys (plus login in byu-vcl and robot-arms) | byu-vcl, powder-doser, robot-arms, tensegrity-optimization |
| MongoDB | byu-vcl, powder-doser (`PI_MONGODB_URI` too) |
| MQTT (HiveMQ, four credential pairs), `OT2_SERIAL`, `PICO_ID` | byu-vcl |
| YouTube tokens (`*_PICKLE_B64`) | byu-vcl, robot-arms, streamingLambda |
| Pi passwords (stream cams, CubXL, powder doser, arm and camera Pis, HMI, panel and room cams) | per repo |
| Hugging Face `HF_TOKEN` | byu-vcl, robot-arms |
| AWS (Lambda deploy), `LAMBDA_FUNCTION_URL` | streamingLambda, robot-arms |
| One-offs: `AIRGRADIENT_API_KEY`, `HEALTHCHECKS_IO_URL`, `POTENTIOSTAT_PC_*`, `ONEDRIVE_EDIT_LINK_PASSWORD` (byu-vcl); `MCMASTER_*` (powder-doser); `PPT_EDIT_*` (tensegrity-optimization) | |

Observations:

1. **Every run authenticates with a subscription token** (`CLAUDE_CODE_OAUTH_TOKEN`), not an
   API key. That is the same pool Claude Science bills against.
2. **Repo knowledge lives in `CLAUDE.md`, not in skills.** byu-vcl's file is 45 KB and loads
   into every run, whether the run is about printing, the Pico W or a meeting post. Only
   digital-alloy-lab has skills: four proposal-writing skills in `.github/skills/`. No repo
   has `.claude/skills/`, `.mcp.json` or plugin configuration.
3. **Two Tailscale login styles exist.** robot-arms and digital-alloy-lab already use
   workload identity (`audience:` plus the client ID, no stored secret). The other four
   still pass a long-lived OAuth client secret.
4. **byu-vcl's secret inventory has drifted.** Its `claude.yml` passes
   `AIRGRADIENT_API_KEY` and `HEALTHCHECKS_IO_URL`, which aren't in CLAUDE.md's
   *Secret inventory*. `EDISON_PLATFORM_API_KEY` is described only in the Edison section.
5. **Model choice:** byu-vcl defaults to Opus at `max` effort, selectable per comment
   (`@claude+<model>:<effort>`). The print and YouTube workflows pin Opus.

## Where Claude Science fits for us

**Where it doesn't fit:**

- **Anything triggered from GitHub, or touching hardware or lab secrets.** Claude Science
  can't be driven by an `@claude` comment and has no headless mode. Third-party patches
  that bypass its login exist; don't use them.
- **On the Pis.** They are arm64, which Claude Science doesn't support. Adding a Pi as an
  SSH host means jobs run "outside the sandbox, as your user on the host". That conflicts
  with treating the Pis as live production devices.
- **As the lab's shared record.** Sessions, artifacts and memory stay on one computer and
  don't sync. Our current pattern is a commit and an issue comment per run, which the whole
  lab can see and link to.
- **Our databases.** The Featured connectors are almost all life sciences. For alloys,
  powders, the atomizer and OT-2 colour mixing, only Literature Graph (OpenAlex, arXiv),
  Chemistry (PubChem and others) and Research Resources apply. Materials Project, OQMD,
  NOMAD and Thermo-Calc would each need a custom MCP connector.

**Where it fits:**

- **Interactive, exploratory analysis with a person at the keyboard.** Examples: XRD
  patterns, AS7341 sensor runs pulled from MongoDB, alloy composition work. It offers a
  persistent kernel, figures next to the chat, provenance for each figure, and the
  reviewer.
- **Literature reviews behind paywalls.** It can use BYU's library EZproxy and publisher
  keys, which a CI runner can't.
- **Heavy compute.** It can submit Slurm jobs to an HPC account over SSH, or run them on
  Modal.

## Recommendations

**Try:**

1. **Pilot Claude Science with one person on one real analysis.** Use an x64 laptop or
   workstation, or a VM through the SSH tunnel. Keep lab credentials out of it, and keep
   it off the Pis. Use a different claude.ai account from the one behind
   `CLAUDE_CODE_OAUTH_TOKEN`, or watch usage, so an interactive session can't use up the
   limits the `@claude` runs depend on. Decide after two weeks whether the reviewer and
   provenance earn their place.
2. **Look into the academic Team plan for scientists and the AI for Science credits.**

**Bring into the GitHub workflows (cheap, and it makes us more Claude-Science-ready):**

3. **Split CLAUDE.md into skills.** Move topic sections into `.claude/skills/<topic>/SKILL.md`:
   Bambu printing, the Pico W and AS7341 sensor, the OT-2, the CubXL and potentiostat,
   stream cams and YouTube, Edison, Hugging Face Spaces. Keep CLAUDE.md for the always-on
   rules: secrets hygiene, the token deadline, Pi safety. Claude Code reads only a skill's
   short description until a task needs it, so runs carry less unrelated context. Claude
   Science can import the same folders, which gives one source for both.
   - Before moving content, test that `claude-code-action` loads project skills.
   - Claude Science's admin docs describe a `skills/<name>/SKILL.md` layout. It is
     unverified whether the importer finds a `.claude/skills/` folder.
4. **Add a reviewer pass to `claude.yml`.** After the main step, a short second Claude step
   would read the final comment, the commits and the run log, and flag mismatches:
   - a number that differs from the file it came from;
   - a step reported as run that never ran;
   - a DOI that doesn't resolve to the cited paper;
   - a checklist item ticked but not done.

   Use Claude Science's rule as the prompt: "trace, don't recompute". This is a workflow
   edit, so it needs a human commit.
5. **Record provenance with every result.** Commit the script, its output and an
   environment snapshot (`pip freeze`/`conda list`) together, and link them by the 7-character
   hash as CLAUDE.md already asks. That gives a git-native version of the Code, Execution
   Log and Environment tabs.
6. **Optionally, add MCP servers for literature** (OpenAlex/arXiv, PubMed) through
   `claude_args --mcp-config`. This is low priority, since runs can already reach those
   APIs directly.

**Change regardless of Claude Science (workflow edits, so human commits):**

7. **Move four repos to Tailscale workload identity.** Switch byu-vcl, powder-doser,
   streamingLambda and tensegrity-optimization from `TS_OAUTH_SECRET` to `audience:` with
   `TS_AUDIENCE`, as robot-arms and digital-alloy-lab do. Then retire the client secret.
   byu-vcl's CLAUDE.md says the env block also exposes the secret "for direct API use", so
   check that nothing depends on it first.
8. **Bring the byu-vcl secret inventory up to date.** Add `AIRGRADIENT_API_KEY`,
   `HEALTHCHECKS_IO_URL` and `EDISON_PLATFORM_API_KEY` to it. Also consider whether every
   `@claude` run needs all 48 secrets, or whether rarely used ones could move into
   environments the way `bambu-print` and `youtube-admin` already have.

**Leave alone:**

- **`@claude` on GitHub stays the backbone** for hardware, Pis, printers, MQTT, MongoDB,
  Zenodo and anything that should leave a public record.
- **Don't copy lab secrets into Claude Science's credentials or connector settings.** The
  environment variables of local connectors are stored unencrypted.
