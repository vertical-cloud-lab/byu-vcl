# Addendum: community and press voices on openness in AI for science (fetched 2026-11-23)

These four pages were found and fetched through the lab Pi's browser (searches logged in
[`pi-browser/queries_batch6_physsci_voices.tsv`](../pi-browser/queries_batch6_physsci_voices.tsv) and
[`search_log.jsonl`](../pi-browser/search_log.jsonl)). Commenters are opinions, not evidence. Quotes are
verbatim and short.

| Source | Type | What it shows |
| --- | --- | --- |
| [HN: "AlphaFold3 – why did Nature publish it without its code?"](https://news.ycombinator.com/item?id=40444168) (2024-05-22, 50 points, 19 comments; links Nature's editorial) | forum | Scientists read Nature's exception as a double standard: "If your pockets are deep enough and/or your work is compelling enough, you can ignore those requirements." Another commenter: companies publish "because it benefits them to", since researchers prefer employers that allow publishing. |
| [HN: "AlphaFold 3 Code"](https://news.ycombinator.com/item?id=42106906) (2024-11-11, 137 points) | forum | The code was released six months later, but the weights went out under a prohibited-use policy barring use "on behalf of a commercial organization or in connection with any commercial activities". A commenter noted it "Wasn't a relevant question for AlphaFold2, as the weights for it were CC BY 4.0 license." |
| [r/comp_chem: "AlphaFold3 vs the open clones (Boltz-1/2, Chai-1, Protenix, HelixFold3)"](https://www.reddit.com/r/comp_chem/comments/1u86k60/alphafold3_vs_the_open_clones_boltz12_chai1/) (2026) | forum | By 2026 practitioners compare 15 structure-prediction models partly on licensing, "including the catch that AlphaFold3's weights are non-commercial and gated". In the replies, one commenter says "AF3 was recently released under Apache 2.0", and another corrects that you can download the code but not use the weights commercially. |
| [Nature: "Inside the 'self-driving' lab revolution"](https://www.nature.com/articles/d41586-026-00974-2) (2026-03-30, technology feature) | press | It frames SDLs on cost and capability ("Evidence is mounting that autonomous labs can be more cost-effective than conventional approaches are"), citing a Ginkgo cloud lab plus GPT-5 that cut the cost per gram of protein production by 40%. It also notes the Acceleration Consortium's C$200M grant. Openness isn't a theme, as in the SDL talk in [`voices_digest.md`](voices_digest.md). |

**Reading.** In protein structure prediction, restricting AlphaFold 3 (2024) set off a fast cycle of open
re-implementations: Boltz, Chai-1, Protenix, HelixFold3 and OpenFold3. Licensing became a selection
criterion for users. This is the AI-for-science version of the software forks in the main report: when a
widely used scientific capability closes, the community rebuilds it in the open from the open data it
was trained on (the PDB). See group I in the [casebook](../companies/CASEBOOK.md) for each model's
licence history.
