# What this means for the Vertical Cloud Lab: a playbook from the evidence (8 actions)

These recommendations follow from the findings in [`README.md`](README.md), the
[DAL/#318 audit](dal/dal_openness_audit.md), the [GitHub digest](gh-mining/commercialization_digest.md)
and the [case files](companies/CASEBOOK.md). Each one names the evidence behind it. They are ordered by
leverage per unit of effort.

## 1. Open the layer between closed instruments and AI

**Do:**
- Publish one small, MIT-licensed driver per instrument, exposed as an MCP server.
- Make the drivers MHS-compatible once Anthropic opens the Model Hardware Standard.
- Start with the instruments that already have usable interfaces (UR, MiR, OT-2, CubXL), then wrap
  closed ones (for example, the rePowder through camera reading) behind the same interface.

**Why:**
- Closed vendor equipment is the most frequent complaint in `ac-dev-lab`: proprietary MyCobot firmware,
  a centrifuge with no API, a decapper with no documentation.
- All 13 instrument and AM makers in group G score 0–1 on openness.
- Only about 4 of 20 instruments on DAL's alloy route have interfaces the lab can program.
- Shared drivers are what other labs reuse. PyLabRobot spread by driving Hamilton and Tecan robots.
- Anthropic and OpenAI now market AI that operates lab instruments (MHS, Claude Science, GPT-Rosalind).
  Whoever owns the driver layer decides how open AI-run labs are.

## 2. Put the code where it can outlive the lab

**Do:**
- Keep MIT for code and use CERN-OHL-P-2.0 for hardware designs, as SDL-demo already does.
- Add the missing NOTICE files the audit flagged: `partial_kgfn`, OpenFlexure files in #318, and
  `database-samples`.
- Once there are outside users, move shared tools such as drivers and the digital-thread schema to a
  neutral home: NumFOCUS fiscal sponsorship, or a Linux Foundation or Acceleration Consortium community.

**Why:**
- Projects held by foundations (Kubernetes, PyTorch, OpenSearch, Valkey, MCP) stayed open through
  changes of owner and strategy, while vendor-held projects were relicensed or archived (Redis, Elastic,
  HashiCorp, Mule CE, Llama).
- 10 of 15 closing moves by organizations later acquired came at or after the acquisition.

## 3. Release data on the funder's clock, and decide the IP question once

**Do:**
- Release data at publication, or 12 months after collection if sooner, as the Genesis FOA expects.
- Deposit in Zenodo plus the Materials Data Facility, behind a published JSON Schema for the digital
  thread. Include negative and failed runs.
- Reconcile DAL's three positions on alloy compositions into one written rule: either open by default,
  or a provisional patent only for a composition that meets targets and has a named licensee.

**Why:**
- Open data compounds. The PDB had released 172,801 open structures by 2020, the year AlphaFold 2 won
  CASP14, and the Materials Project trained GNoME and MatterGen.
- The 2025–26 AI-for-materials startups protect *data and compositions*, not methods, and failed runs are
  the signal closed players hoard.
- Inconsistent IP language is a review risk: the drafts currently disagree.

## 4. Don't plan on kit sales; sell services around the open core if anything

**Do:**
- If commercialization is a goal, sell access, training, setup and integration, such as cloud-lab time
  or SDL-in-a-course, not units.
- Use "commercialization-as-a-service" partners such as GroupGets for any hardware.

**Why:**
- The $80 SDL-demo kit left a stated profit of $2.24 a kit.
- LulzBot (fully open hardware) collapsed in 2019. Open-hardware firms that last (Adafruit, SparkFun,
  Prusa) are bootstrapped, and Prusa is now restricting resale.
- In software, value goes to open core plus a hosted service: Databricks, Confluent, MongoDB Atlas.
- Venture data shows open-source startups raising faster and at higher valuations than matched closed
  peers. The report doesn't split by business model.

## 5. Ask for API rights before buying, and treat vendor longevity as a risk

**Do:**
- Put API, SDK and data-export rights, plus permission to publish driver code, into RFQs for the next
  LPBF printer, atomizer and characterization tools.
- Prefer vendors with documented interfaces.
- Keep vendor manuals out of public repos.

**Why:**
- Desktop Metal (debuted at up to $2.5B) went bankrupt and Markforged (debuted at $2.1B) sold for
  $42.5M. A closed instrument with an orphaned SDK is a stranded asset.
- `ac-dev-lab` #532 shows vendor API documentation that couldn't be published.

## 6. Put a little back into the commons the lab relies on

**Do:**
- Budget a small, explicit line, even a few hundred dollars a year or institutional membership, for the
  open infrastructure the lab's AI and papers depend on (arXiv, Zenodo, OSF, pycalphad, PyLabRobot).
- Contribute fixes upstream.
- Mention the commons in proposals: the Genesis Mission and NSF increasingly ask how outputs will be
  sustained.

**Why:**
- arXiv left Cornell and ran a deficit while monthly submissions doubled in two years.
- OSF stopped new projects for lack of $4–5M a year.
- Meta shut Papers with Code.
- 96% of the demand-side value of open source is created by 5% of its developers (Hoffmann, Nagle & Zhou
  2024): the commons is concentrated and fragile.

## 7. Keep working in public, and keep the boundary explicit

**Do:**
- Keep DAL's and byu-vcl's practice of public issues, PRs, Edison trajectories and YouTube walkthroughs,
  with a short `PRIVATE.md`-style statement of what stays private and why (budgets, letters, CVs,
  vendor-confidential documents).

**Why:**
- The open records of `ac-dev-lab` and the SDL demo (4,928 GitHub records), plus byu-vcl's own issues and
  the #318 videos, are what made this study possible.
- Government, academic and foundation infrastructure is the one category that almost never closed (1 of
  24 made a closing move, in groups A–G).
- That is the category a university lab belongs to.

## 8. Use the university's own machinery on purpose

**Do:**
- Before the first external user, agree with BYU's technology-transfer office which outputs are released
  openly by default: drivers, schemas, digital twin, BOMs and data. Agree which, if any, go through
  disclosure and patent review (for example, a target-meeting alloy composition with a named licensee).
- If BYU has an Open Source Program Office or equivalent, register the lab's repos with it.
- For hardware, follow the documented path: publish the design under CERN-OHL-P, and sell or partner on
  what publication doesn't supply (built and tested units, kits, training, integration).

**Why:**
- US university licensing income topped $2.94B in 2018, yet most technology-transfer offices don't cover
  their costs. The big wins came through inventor-founded startups.
- OpenFlexure, Foldscope and CERN's open hardware commercialized through manufacturing and service, not
  exclusive rights. Opentrons started open, then closed its hardware with the OT-2 and kept the software
  open. The review literature already counts this lab's CLSLab:Light kits
  (39 units through GroupGets) as an example
  ([Edison](edison/academic_osh_commercialization_answer.md)).
- AI-era open-source tools (group J) have kept open licences so far, and several had exits to compute
  companies in 2025–26. The large deals (W&B, Modular) are not clean permissive cases, so this shows
  only that openness didn't prevent an exit.
