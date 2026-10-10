# Paper kit: figures, manuscript builds and the checks before review.
#
#   make figures              every figures/fig*.py: reads data/, writes figures/out/
#   make pdf J=asme           clean PDF for one journal skeleton, todonotes hidden
#   make todos J=asme         review PDF: margin notes and a list of todos
#   make diff J=asme REV=v1   latexdiff PDF against a git revision (tag, branch, commit)
#   make journals             clean PDFs of every skeleton (build test)
#   make check                figure and data conventions; lists what is left to fill
#   make submission-check     the same, failing on any placeholder left
#   make colorblind           colour-vision simulations into figures/out/cvd/
#   make rebuild-check        clean-environment rebuild of every figure (fresh venv)
#   make credit               CRediT statement and table from declarations/credit.csv
#   make fetch                publisher classes not in TeX Live (sn-jnl, RSC)
#   make clean                LaTeX build output
#
# J is one of: springer-nature  elsevier  hardwarex  rsc  asme
# Delete the main-*.tex of journals you are not targeting; keep the one you are.

J        ?= asme
REV      ?= HEAD
PY       ?= python3
LATEXMK  ?= latexmk
JOURNALS := springer-nature elsevier hardwarex rsc asme

MS       := manuscript
BUILD    := $(CURDIR)/build
VENDOR   := $(CURDIR)/$(MS)/vendor
# Publisher classes fetched into manuscript/vendor/<name>/ are found from there.
export TEXINPUTS := $(VENDOR)//:$(TEXINPUTS)
export BSTINPUTS := $(VENDOR)//:$(BSTINPUTS)
LMK      := $(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error -file-line-error \
            -outdir=$(BUILD)
# The repository-relative path of this folder, for git archive in make diff.
PREFIX   := $(shell git rev-parse --show-prefix 2>/dev/null)

FIGS     := $(sort $(wildcard figures/fig*.py))

.PHONY: help figures pdf todos diff journals check submission-check colorblind \
        rebuild-check credit fetch clean

help:
	@sed -n '2,19p' Makefile | sed 's/^# \{0,1\}//'

figures:
	@test -n "$(FIGS)" || { echo "no figures/fig*.py"; exit 1; }
	@for f in $(FIGS); do echo "$$f"; VCL_STRICT_DATA=1 $(PY) $$f || exit 1; done

$(MS)/main-$(J).tex:
	@echo "no $(MS)/main-$(J).tex: J is one of $(JOURNALS)"; exit 1

pdf: $(MS)/main-$(J).tex
	cd $(MS) && $(LMK) -jobname=main-$(J) -usepretex='\def\TODOOPTS{disable}' main-$(J).tex
	@echo "-> build/main-$(J).pdf"

todos: $(MS)/main-$(J).tex
	cd $(MS) && $(LMK) -jobname=main-$(J)-todos -usepretex='\def\TODOOPTS{}' main-$(J).tex
	@echo "-> build/main-$(J)-todos.pdf"

# Flatten the old and new manuscripts (\input files included) and mark the
# changes; the old one comes from git archive, so uncommitted edits count as new.
diff: $(MS)/main-$(J).tex
	@git rev-parse --verify --quiet "$(REV)^{commit}" >/dev/null || \
	  { echo "REV=$(REV) is not a git revision"; exit 1; }
	@git cat-file -e "$(REV):$(PREFIX)$(MS)/main-$(J).tex" 2>/dev/null || \
	  { echo "$(MS)/main-$(J).tex did not exist at REV=$(REV)"; exit 1; }
	rm -rf $(BUILD)/old && mkdir -p $(BUILD)/old
	git -C "$$(git rev-parse --show-toplevel)" archive --format=tar "$(REV)" -- "$(PREFIX)$(MS)" \
	  | tar -x -C $(BUILD)/old
	latexdiff --flatten --math-markup=whole \
	  $(BUILD)/old/$(PREFIX)$(MS)/main-$(J).tex $(MS)/main-$(J).tex > $(MS)/main-$(J)-diff.tex
	cd $(MS) && $(LMK) -jobname=main-$(J)-diff -usepretex='\def\TODOOPTS{disable}' main-$(J)-diff.tex
	@echo "-> build/main-$(J)-diff.pdf (changes since $(REV))"

journals:
	@for j in $(JOURNALS); do \
	  if [ -f $(MS)/main-$$j.tex ]; then $(MAKE) --no-print-directory pdf J=$$j || exit 1; fi; \
	done

check:
	$(PY) scripts/check_kit.py

submission-check:
	$(PY) scripts/check_kit.py --submission

colorblind:
	$(PY) scripts/colorblind.py

rebuild-check:
	$(PY) scripts/clean_rebuild.py

credit:
	$(PY) scripts/credit.py

# Classes that are not in TeX Live (elsarticle and asmejour are). Their licences
# do not clearly allow redistribution, so they are fetched, checked against the
# SHA-256 of the version this kit was tested with, and never committed. When a
# publisher updates a template the check fails: compare, then update the hash.
SNJNL_URL ?= https://resource-cms.springernature.com/springer-cms/rest/v1/content/18782940/data/v12
SNJNL_SHA ?= 812e76dcaa9c28dc1bff1fb6065d51729b67d4ea140552a05088317414a3ecae
RSC_URL   ?= https://www.rsc.org/getContentAsset/5484c665-5d01-46eb-9b23-121b16e8ecd4/f4c91d86-ac3e-4675-bdf3-f8325ded9710/royal-society-of-chemistry-article-template.zip
RSC_SHA   ?= e481548ff4c520b25e341dcf84a55bc58752064fd1e584a834f7c2767174b6c5
fetch:
	mkdir -p $(VENDOR)/sn-jnl $(VENDOR)/rsc
	curl -fsSL "$(SNJNL_URL)" -o $(VENDOR)/sn-jnl.zip
	echo "$(SNJNL_SHA)  $(VENDOR)/sn-jnl.zip" | sha256sum -c --quiet
	unzip -oq -j $(VENDOR)/sn-jnl.zip -d $(VENDOR)/sn-jnl && rm $(VENDOR)/sn-jnl.zip
	curl -fsSL "$(RSC_URL)" -o $(VENDOR)/rsc.zip
	echo "$(RSC_SHA)  $(VENDOR)/rsc.zip" | sha256sum -c --quiet
	unzip -oq $(VENDOR)/rsc.zip -d $(VENDOR)/rsc && rm $(VENDOR)/rsc.zip
	@# RSC ships one main.tex; main-rsc.tex inputs its preamble (minus the sample
	@# bibliography preamble) and its in-document page set-up, unchanged.
	sed -n '1,/^\\begin{document}/p' $(VENDOR)/rsc/main.tex | sed '$$d' \
	  | sed '/^%%%%%%%%% Preamble of the bibliography/,/^%%%%%%%%% *$$/d' > $(VENDOR)/rsc/rsc-preamble.tex
	sed -n '/^\\begin{document}/,/^%%%END OF FIGURE SETUP%%%/p' $(VENDOR)/rsc/main.tex | sed '1d' \
	  > $(VENDOR)/rsc/rsc-pagesetup.tex
	@echo "classes in $(MS)/vendor/ (not committed: see $(MS)/vendor/README.md)"

clean:
	rm -rf $(BUILD) $(MS)/*-diff.tex
