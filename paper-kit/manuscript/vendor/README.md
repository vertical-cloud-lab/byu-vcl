# vendor/: publisher templates that are not in TeX Live

`make fetch` downloads two templates here and checks each against the
SHA-256 of the version this kit was tested with (both read 2026-10-10):

| Folder | Template | Source | Licence as stated |
|---|---|---|---|
| `sn-jnl/` | Springer Nature LaTeX template v3.1 (December 2024): `sn-jnl.cls`, the `sn-*.bst` styles, the sample and user manual | [LaTeX author support](https://www.springernature.com/gp/authors/campaigns/latex-author-support) | the class carries LaTeX's stock LPPL 1.3c notice; the manual says only "Copyright Springer Nature" |
| `rsc/` | RSC article template: one `main.tex`, `rsc.bst`, the `head_foot/` header images | [RSC article templates](https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/article-templates) | "Copyright The Royal Society of Chemistry 2016"; no terms given |

Neither clearly allows redistribution, so neither is committed (the folder's
contents are git-ignored). `make fetch` also writes `rsc/rsc-preamble.tex` and
`rsc/rsc-pagesetup.tex`, RSC's preamble and page set-up cut unchanged from
its `main.tex`, which `main-rsc.tex` inputs.

`elsarticle` (Elsevier, HardwareX) and `asmejour` (ASME) come with TeX Live.
`asmejour` needs the `newtx` and `inconsolata` fonts: on Debian or Ubuntu,
`texlive-fonts-extra`, `tex-gyre` and `texlive-plain-generic`.

When a publisher updates a template, `make fetch` fails at the checksum.
Build with the new one, look at the PDF, and if it is fine, update
`SNJNL_SHA` or `RSC_SHA` (and the URL) in the Makefile.
