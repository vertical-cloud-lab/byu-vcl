# Voices digest: open-source business, relicensing, open hardware and open-weight AI

Prepared for [vertical-cloud-lab/byu-vcl#380](https://github.com/vertical-cloud-lab/byu-vcl/issues/380), "The value of open science in the age of AI". One row per source is in `voices_index.csv` in this folder.

## (a) Method note

Everything below was captured on 2026-11-23 through the lab Raspberry Pi's headed browser (a residential IP): the visible text of 15 pages (6 Reddit threads, 3 Hacker News threads, 5 blog or research pages and 1 forum thread) and the transcripts of 6 YouTube videos, opened by clicking *Show transcript*. One capture came back empty and was made again the same way on 2026-11-24 (Y6). Quotes are verbatim from that capture: YouTube auto-captions keep their transcription errors, timestamps link to the caption segment where a quote starts, and Reddit pages showed only their first ~25 comments, so comment tallies are approximate. Reddit, HN and forum comments are opinions, not evidence; numbers that appear in them, or in vendor blogs, are reported as claims and were not checked independently.

## (b) Source-by-source digest

### YouTube talks

#### Y1. Keynote: The Economic Value of Open Source (Frank Nagle)

- **Link:** https://www.youtube.com/watch?v=L4H5NRldNs0 · **Type:** YouTube keynote, The Linux Foundation channel (auto-captions, 169 segments) · **Date:** not shown

1. **Open source is worth almost $9 trillion, and that's an underestimate.** Nagle multiplies a replacement cost (the COCOMO II model, driven by lines of code) by usage observed in the Census data, which covers over 12 million observations at tens of thousands of firms. The data misses things like the Linux kernel. "open source is worth $9 trillion" ([20:44](https://www.youtube.com/watch?v=L4H5NRldNs0&t=1244s))
2. **Without open source, firms would spend 3.5x more on software.** "companies would spend about three and a half times more on software than they currently do" ([11:47](https://www.youtube.com/watch?v=L4H5NRldNs0&t=707s)). An earlier one-project study valued the Apache web server at about $12B. That is about 9% of 2013 US spending on prepackaged software, and an almost 20% return on the government supercomputing centres it came out of ([5:41](https://www.youtube.com/watch?v=L4H5NRldNs0&t=341s)).
3. **A few contributors create most of the value.** "about 5% of the the contributors to all these most widely used projects were creating about 96% of this value" ([12:04](https://www.youtube.com/watch?v=L4H5NRldNs0&t=724s))
4. **Contributing, not just using, pays.** "those that contribute end up getting two times more productive value back from using open source than their freeriding peers who use it but don't contribute" ([14:02](https://www.youtube.com/watch?v=L4H5NRldNs0&t=842s)). Startups that contribute more raise larger VC rounds, reach higher valuations and exit more often. A French policy that nudged firms to contribute raised IT employment and startup formation.
5. **But not always.** He lists five conditions under which contributing makes most sense ([15:51](https://www.youtube.com/watch?v=L4H5NRldNs0&t=951s)): very early or very late in the technology life cycle, low in the stack, markets that won't be winner-take-all (or whose standard you can control), very high or very low competition, and low social acceptance of the technology. "We want to collaborate on the core and compete on the edges." ([20:53](https://www.youtube.com/watch?v=L4H5NRldNs0&t=1253s))
6. **AI and hardware are next.** He puts today's open collaboration in AI down to low public acceptance and unclear regulation. His group is extending the valuation to open-source AI (data, weights and inference as well as code) and to open hardware, which he calls under-studied ([19:50](https://www.youtube.com/watch?v=L4H5NRldNs0&t=1190s)). "that's in my opinion why we're seeing more collaboration and more open source happening in AI right now" ([17:31](https://www.youtube.com/watch?v=L4H5NRldNs0&t=1051s))

#### Y2. Mike Olson: Open Source Business Models (Stanford eCorner)

- **Link:** https://www.youtube.com/watch?v=T_UM5PYk9NA · **Type:** YouTube clip, Stanford eCorner (auto-captions, 44 segments) · **Date:** not shown · **Speaker:** Mike Olson of Cloudera, drawing on his own earlier companies, Illustra and Sleepycat

1. **Open source is now infrastructure, like electricity: nobody needs a strategy for it.** "I believe open source software is the same way." ([0:20](https://www.youtube.com/watch?v=T_UM5PYk9NA&t=20s))
2. **Making a fork proprietary forfeits the community.** Illustra took Postgres closed and sold it like Oracle did. In doing so "you surrender the contributions of a global community" ([1:09](https://www.youtube.com/watch?v=T_UM5PYk9NA&t=69s)).
3. **A services-only model starves the product.** "services companies don't drive real high margins and it doesn't leave that much money to invest in making the core product better" ([1:53](https://www.youtube.com/watch?v=T_UM5PYk9NA&t=113s)). He notes that Red Hat also ran a proprietary hosted management service, Red Hat Network, on top of its free OS ([2:11](https://www.youtube.com/watch?v=T_UM5PYk9NA&t=131s)).
4. **Dual licensing starts every customer relationship with a threat.** "it's kind of like distributing the poison and selling the antidote" ([3:12](https://www.youtube.com/watch?v=T_UM5PYk9NA&t=192s))
5. **Cloudera's answer is proprietary management and security software on an open ecosystem, with the revenue fed back in.** "it gives us a recurring revenue stream that we can then invest back in the open source" ([4:21](https://www.youtube.com/watch?v=T_UM5PYk9NA&t=261s)). His template is IBM, which contributes to Linux and sells the software that runs on top of it.

#### Y3. Keynote: Commercial Open Source Business Models (Sid Sijbrandij, GitLab)

- **Link:** https://www.youtube.com/watch?v=G6ZupYzr_Zg · **Type:** YouTube keynote, The Linux Foundation channel (auto-captions, 142 segments; the captions garble *buyer-based open core* in places) · **Date:** not shown. The talk mentions MongoDB withdrawing its license from OSI review "on Friday" and AWS's Elasticsearch distribution "yesterday", which places it around March 2019 (our inference).

1. **The main threat is hyperclouds wrapping open-source projects as services.** "the biggest challenge that commercial open source software companies face today is how to deal with the hyper clouds" ([2:50](https://www.youtube.com/watch?v=G6ZupYzr_Zg&t=170s))
2. **Licenses that forbid competing services aren't open source, but he won't rule them out.** He accepts that such a license no longer counts as open source ([4:03](https://www.youtube.com/watch?v=G6ZupYzr_Zg&t=243s)), but adds: "I'm not saying no to them I understand why these companies did it" ([4:56](https://www.youtube.com/watch?v=G6ZupYzr_Zg&t=296s)).
3. **Clouds can fork and commoditize an open-core product.** AWS's Elasticsearch distribution open-sourced paid features such as encryption: "they went directly after the value that people pay elasticsearch for" ([5:22](https://www.youtube.com/watch?v=G6ZupYzr_Zg&t=322s)). Commoditization is more likely when there are few paid features, when users work through an API, when buyers are price-sensitive, or when the users who want the paid features also contribute code ([6:27](https://www.youtube.com/watch?v=G6ZupYzr_Zg&t=387s)).
4. **GitLab tried almost everything else first.** Donations came to about $7 a month, spent on ice cream. Paid feature development stalled, support contracts were cancelled unused, and single-tenant hosting proved hard. On consulting: "the easier we made that the more we added to our documentation the fewer people wanted our consultancy services so we put ourselves out of a job" ([9:17](https://www.youtube.com/watch?v=G6ZupYzr_Zg&t=557s))
5. **Open core won on margins.** "it's a great business model it's 90 plus percent margins it's almost all profit" ([11:28](https://www.youtube.com/watch?v=G6ZupYzr_Zg&t=688s)). Splitting features by lifecycle stage, company size or organisational maturity either hurt adoption or didn't match who was willing to pay.
6. **Buyer-based open core.** There is a free core and three paid tiers, from $4 to $99 per user per month, a 5x step between tiers. Each feature goes in the tier of the person who wants it (individual contributor, manager or executive), which he argues resists commoditization ([13:06](https://www.youtube.com/watch?v=G6ZupYzr_Zg&t=786s)). "buyer base open core means putting features and pay tiers and the type of persona that would buy determines where things go" ([14:17](https://www.youtube.com/watch?v=G6ZupYzr_Zg&t=857s)). GitLab also counts over 2,000 code contributors ([1:52](https://www.youtube.com/watch?v=G6ZupYzr_Zg&t=112s)).

#### Y4. Limor Fried, Founder & CEO, Adafruit Industries (MAKERS)

- **Link:** https://www.youtube.com/watch?v=D27U3wHN8fs · **Type:** YouTube profile, MAKERS (auto-captions, 34 segments, about 4.5 minutes, no financial data) · **Date:** not shown

1. **She sees openness as an obligation, a view she picked up from MIT's open-source culture.** "if you are creating new technology new capabilities you have to give it away otherwise you're kind of being selfish" ([1:06](https://www.youtube.com/watch?v=D27U3wHN8fs&t=66s)). She applied open-source software practice to hardware.
2. **The business grew out of demand for kits.** People who read about her open projects asked her to bundle the parts: "can you just sell me a kit" ([1:30](https://www.youtube.com/watch?v=D27U3wHN8fs&t=90s)).
3. **Adafruit shares everything and publishes it free.** "at Adafruit we share everything I share all the plans schematics I design the files of the code it's all online" ([3:01](https://www.youtube.com/watch?v=D27U3wHN8fs&t=181s)). A weekly live show-and-tell feeds new ideas back into free published projects.
4. **Running the business had to be learned; widening who becomes an engineer is the payoff.** "I was taught engineering but you don't really know how to run a business" ([2:13](https://www.youtube.com/watch?v=D27U3wHN8fs&t=133s)). She started at 25, in a condemned apartment, and counts her community, people who don't fit the traditional image of an engineer, as the reward ([4:01](https://www.youtube.com/watch?v=D27U3wHN8fs&t=241s)).

#### Y5. Accelerated Materials Discovery Through Self-Driving Labs (Radical AI, at Cornell Tech)

- **Link:** https://www.youtube.com/watch?v=UAKI1TBDsWI · **Type:** YouTube talk, Cornell Tech channel (auto-captions, 104 segments) · **Date:** not shown (mentions SAM 2, so mid-2024 or later) · **Speaker:** a Radical AI co-founder, not named in the captured transcript

1. **The physical sciences still work serially, at human pace.** "Material science and really all physical sciences have not really adapted over the last hundreds of years." ([2:01](https://www.youtube.com/watch?v=UAKI1TBDsWI&t=121s))
2. **Radical AI builds the whole closed loop in-house.** Machine learning proposes experiments, robots run them and the data flows back to the models. "we think we are the only company that is focused on building every single component in this flywheel" ([2:59](https://www.youtube.com/watch?v=UAKI1TBDsWI&t=179s))
3. **Off-the-shelf foundation models failed on real lab hardware.** For computer vision on an automated vacuum arc melter running at 3,500 °C: "Our team attempted SAM 2 and others and they completely failed." ([5:24](https://www.youtube.com/watch?v=UAKI1TBDsWI&t=324s)). Their own pipeline is reported as 80x faster and more accurate.
4. **LLM agents replaced Bayesian optimization, and in-house data made them work.** Gaussian-process optimization was judged a poor fit for open formulation spaces, so they built an actor–critic pair of LLMs. "the design agent or the actor agent has access to over a thousand uh synthesized experiments that ran in our lab" ([8:08](https://www.youtube.com/watch?v=UAKI1TBDsWI&t=488s)). Without that context the agent's proposals scattered; with it they converged ([11:03](https://www.youtube.com/watch?v=UAKI1TBDsWI&t=663s)).
5. **They claim the agents beat human scientists (self-reported; no methods shown).** On a combined hardness and oxidation target, mean hardness rose by almost a third and oxidation protection by over 25%. The agent even queued an experiment on its own at 4 a.m. "very directly they crush humans." ([9:40](https://www.youtube.com/watch?v=UAKI1TBDsWI&t=580s))
6. **The goal is to cut decades of materials R&D to months.** "take a process that typically takes us decades the R&D process for a new material discovery and compress it down to 6 months" ([12:46](https://www.youtube.com/watch?v=UAKI1TBDsWI&t=766s)). Openness, shared data and open hardware never come up.

#### Y6. How do open source projects make money? (Travis Oliphant and Lex Fridman)

- **Link:** https://www.youtube.com/watch?v=17ngZtwwgE8 · **Type:** YouTube clip, Lex Clips channel (auto-captions, 58 segments). The first capture came back empty, and a second, made the same way on 2026-11-24, worked · **Date:** not shown · **Speakers:** Travis Oliphant and Lex Fridman. Auto-captions don't mark who is speaking, so attributions follow the conversation.
- **Background, not from the clip** ([Wikipedia](https://en.wikipedia.org/wiki/Travis_Oliphant)): Oliphant created NumPy in 2005 and contributed to SciPy. He was an assistant professor of electrical and computer engineering at BYU from 2001 to 2007, then president of Enthought, co-founder and CEO of Continuum Analytics (now Anaconda), and founder of Quansight and OpenTeams. The six years at a university he mentions match his BYU years.

1. **He isn't a zealot; his objection was to closed dependencies in published work.** "i'm actually not an open source zealot i love open source for the what it brings but i also see the role for proprietary software" ([0:02](https://www.youtube.com/watch?v=17ngZtwwgE8&t=2s)). What he disliked was "the fact that i would develop code and publish it and then effectively telling somebody here to run my code you have to have this proprietary software" ([0:02](https://www.youtube.com/watch?v=17ngZtwwgE8&t=2s)), with MATLAB as the example.
2. **For him, the business question is still open.** He frames it as "how do you connect the ethos of cooperative development with the necessity of of creating profits" ([0:43](https://www.youtube.com/watch?v=17ngZtwwgE8&t=43s)), and of his own case says "it didn't really resolve itself it sort of started a journey that i'm continuing on" ([5:06](https://www.youtube.com/watch?v=17ngZtwwgE8&t=306s)).
3. **Stallman's answer didn't work for a graduate student with children.** He recalls Stallman's advice as "just be like me and don't have kids" ([1:23](https://www.youtube.com/watch?v=17ngZtwwgE8&t=83s)) and his own reaction: "okay this is a train i can't get on" ([1:38](https://www.youtube.com/watch?v=17ngZtwwgE8&t=98s)). The reply (the captions don't mark the speaker): "there has to be a way to preserve the culture of open source and still be able to make sufficient money to feed you" ([1:38](https://www.youtube.com/watch?v=17ngZtwwgE8&t=98s)).
4. **The value is created, not captured.** He went in knowing "people might use it and i might not get paid for it and i'll have to figure something else out to get paid" ([5:20](https://www.youtube.com/watch?v=17ngZtwwgE8&t=320s)), and he is "not bitter that a lot of people have used stuff that i've written and i haven't necessarily benefited economically from it" ([5:29](https://www.youtube.com/watch?v=17ngZtwwgE8&t=329s)). His aim: "i want to create systems that let people like me who might have these desires to do things let them benefit" ([5:37](https://www.youtube.com/watch?v=17ngZtwwgE8&t=337s)). Fridman, as a user: "i wish there was mechanisms for me to reward whoever created scipy and numpy" ([5:53](https://www.youtube.com/watch?v=17ngZtwwgE8&t=353s)).
5. **Economics, then entrepreneurship, took him out of academia.** Reading economics, including von Mises on prices as signals, led him to "entrepreneurship matters so i love software but entrepreneur but we need more entrepreneurs" ([7:14](https://www.youtube.com/watch?v=17ngZtwwgE8&t=434s)), "even though i was on a trajectory to go to a tenure track position at a university" ([7:28](https://www.youtube.com/watch?v=17ngZtwwgE8&t=448s)). The clip ends before he names a funding mechanism.

### Reddit threads

#### R1. Qualcomm has quietly rewritten Arduino's terms and conditions, and its not looking good (r/hardware)

- **Link:** https://www.reddit.com/r/hardware/comments/1p321yr/qualcomm_has_quietly_rewritten_arduinos_terms_and/ · **Type:** Reddit link post (to a molecularist.com article) · **Date:** 2025-11-21 (from the page's top-posts-of-the-day link; shown as "1y ago")

1. **Commenters read the change as the start of Arduino's decline under Qualcomm.** "Arduino died the day they were acquired. It's inevitable." (a commenter)
2. **The sharpest legal worry is patents.** "Arduino now explicitly states that using their platform grants you no patent licenses whatsoever." (a commenter, who fears Qualcomm could assert patents against projects built with Arduino tools; that reading was not checked against the terms)
3. **Leaving is cheap.** Commenters suggest clones, Raspberry Pi Picos or Seeed boards. "Every hobbyist uses clones anyway and it's like a five dollar board running a fifty cent chip." (a commenter)
4. **The IDE is the remaining lock-in.** "The IDE is literally the only thing I care about, and that only for the ease of flashing microcontrollers." (a commenter). Another says clones still need the official IDE.
5. **The reaction elsewhere was bigger.** The page's related-posts list shows an r/arduino post on the update (3.8K upvotes, 314 comments) and an r/embedded post predicting Arduino's death (602 upvotes, 72 comments). One commenter here mocks the linked article's wordiness.

- **Balance:** 23 visible comments not by the poster (37 more replies were collapsed). About 11 are on topic, and every one of those is critical of Qualcomm or pessimistic about Arduino. About 7 are tangents (WiMax, Mirasol, Microsoft) and the rest are neutral questions. None defends the new terms.

#### R2. OpenTofu Is 3 Years Old. Terraform Still Has a 77x Search Advantage. (r/Terraform)

- **Link:** https://www.reddit.com/r/Terraform/comments/1tku0gr/opentofu_is_3_years_old_terraform_still_has_a_77x/ · **Type:** Reddit discussion · **Date:** ~2026-05 (shown as "6mo ago")

1. **The poster reads Google Trends as showing that the license change barely moved users.** Search trends suggest "enterprises and practitioners either stayed with Terraform or simply didn't care enough about the license change to switch".
2. **Commenters say search volume is a poor proxy for use.** "Search volume reflects documentation habits as much as adoption" (a commenter). Several OpenTofu users say they still search under Terraform's name to find provider docs. The same commenter says registry downloads or Terraform Cloud subscriptions would be better signals, but neither side has been transparent about them.
3. **Many report running OpenTofu, for concrete reasons.** These include encrypted state, Terraform Cloud's per-resource pricing, and Crossplane archiving its Terraform provider. "I switched to OpenTofu explicitly so I could encrypt my tfstate at rest." (a commenter)
4. **For many firms the license change never bit.** In one commenter's experience, organisations that weighed a switch in 2023 mostly stayed, because "the BSL restrictions didn't actually affect their usage pattern" (a commenter). Internal infrastructure-as-code with no competing product was never the license's target.
5. **Views on OpenTofu's momentum are mixed.** One commenter says its development has slowed. Another says: "at least tofu is adding features people actually want instead of only those that can be monetized."

- **Balance:** 23 visible comments not by the poster (36 replies collapsed). About 11 say they run, are migrating to, or plan to adopt OpenTofu. About 6 dispute that search share measures adoption, about 4 say the license change did not affect them, and 1 says OpenTofu has slowed. The audience is self-selected Terraform practitioners.

#### R3. OpenAI released gpt-oss 350 days ago. Will we ever see another open-weight model from them? (r/LocalLLaMA)

- **Link:** https://www.reddit.com/r/LocalLLaMA/comments/1v258lo/openai_released_gptoss_350_days_ago_will_we_ever/ · **Type:** Reddit discussion · **Date:** ~2026-07 (shown as "4mo ago")

1. **The poster asks whether gpt-oss will ever get a successor.** "Nearly a year later, we've had safeguard fine-tunes but no general-purpose base model or successor." They wonder whether Kimi, Qwen and GLM will force OpenAI's hand.
2. **Most commenters think gpt-oss was PR.** "It was a marketing stunt." (a commenter). Others say it was a reaction to Chinese local models or to a court case; neither claim is verified.
3. **The economics point the other way.** "It's a lot more profitable to charge by the token than release their models for free." (a commenter)
4. **Some allege lobbying (unverified).** "They are fully lobbying atm to ban open weight from outside" (a commenter). Another accuses OpenAI's rhetoric of encouraging bans on other open-weight models.
5. **OpenAI is still seen as more open than Anthropic.** "They're definitely more open than Anthropic which doesn't even release the harness source code or allows other harnesses." (a commenter)
6. **Some credit the model and think open weights are catching up.** Two commenters praise gpt-oss, and one recounts a hallway hint at ICML of a new open model. "once Kimi goes open it’s basically officially a month gap between closed source and open source" (a commenter)

- **Balance:** 25 visible comments (about 50 replies collapsed). About 17 are cynical about OpenAI's open-weight intentions and about 4 praise gpt-oss or hope for more. The rest are jokes or a debate over "open source" versus "free software".

#### R4. Anthropic wants to ban open source models. Of course they do (r/OS_AI)

- **Link:** https://www.reddit.com/r/OS_AI/comments/1xxxiag/anthropic_wants_to_ban_open_source_models_of/ · **Type:** Reddit post (a video; its content is not in the captured text) · **Date:** ~2026-11-16 (shown as "7d ago")

1. **The premise is disputed.** The comments imply a clip of Dario Amodei. One commenter seems to suspect an AI-generated clip (naming Seedance 2.5 and ElevenLabs v4). Another: "Except he didn't say that but I know nuance is hard for folks"
2. **Most commenters read it as margins, not safety.** "they're scared of open-source models running locally on consumer GPUs for free and killing their API margins" (a commenter)
3. **Others frame it as regulatory capture.** "Closed labs always push for heavy regulation the moment open weights start closing the gap" (a commenter)
4. **Open models are seen as inevitable and as a price ceiling.** "Open weight models will put a roof on what they can charge for everyday AI use." (a commenter, who in the same comment worries about Chinese open models being used to hack Western systems). Others say there is no undoing released weights.
5. **One commenter corrects the terminology.** "these models are not open source, they are open weight." (a commenter)
6. **The related-posts list shows the framing recurs.** Post titles there (unverified headlines) include an r/LocalLLaMA post alleging that OpenAI and Anthropic quietly lobby regulators against open models (1.2K upvotes), and another, posted about four months before the capture, ending "Now the gaslighting begins: “Nobody is trying to ban open source.”"

- **Balance:** 20 visible comments not by the poster, who replied only with emoji. About 12 are hostile to Anthropic or Amodei, 2 question the premise or the clip, and 1 is mixed. The rest are jokes, the terminology correction, or empty.

#### R5. How did your open source startup make money? (I WILL NOT PROMOTE) (r/startups)

- **Link:** https://www.reddit.com/r/startups/comments/1y18b2t/how_did_your_open_source_startup_make_money_i/ · **Type:** Reddit discussion · **Date:** ~2026-11-20 (shown as "3d ago")

1. **The case: a bootstrapped founder open-sourced an email inbox app so users can trust or self-host it.** He plans to use AGPL and studies Plausible, Cal.com and Supabase.
2. **Commenters say to decide the paid line first and charge for what self-hosters don't want to run.** "self-hosters mostly won't convert, so charge for what they don't want to run themselves, like hosting, support or team features." (a commenter). Another lists SSO, audit logs, priority support and managed hosting.
3. **Self-hosters are marketing, not lost revenue.** "Self-hosters were never going to pay you anyway, they're more like free marketing" (a commenter)
4. **AGPL deters resellers; add a CLA now if dual licensing might come later.** "If you might ever want a commercial license or dual licensing, add a CLA for contributors now, it's painful to add later." (a commenter, who also says Plausible moved from MIT to AGPL in 2020 to stop hosted resale; not verified)
5. **Skeptics put customers first.** "before you write another paragraph about AGPL go get one person to hand you 20 bucks" (a commenter). Another notes that VC-funded Cal.com and Supabase can subsidise free tiers in a way a bootstrapped founder can't.

- **Balance:** 14 comments not by the poster. 8 give constructive advice that converges on an open core plus paid hosting. 5 warn that he has no paying customers yet, or that open source is not a business model in itself, and 1 is deleted. Nobody argues against open-sourcing as such.

#### R6. How can Anthropic be valued at over $1.3 trillion at its IPO when it doesn't own physical infrastructure and has nearly $900B in compute bills? (r/NoStupidQuestions)

- **Link:** https://www.reddit.com/r/NoStupidQuestions/comments/1y2e298/how_can_anthropic_be_valued_at_over_13_trillion/ · **Type:** Reddit discussion · **Date:** ~2026-11-21 (shown as "2d ago")

1. **The poster's reading of the IPO filing (unverified):** a valuation of about $1.3T; revenue growing from under $5B last year to an $81B annual pace by October; about $900B of long-term compute contracts; and over $200B in cash after the IPO. "Are investors assuming Claude becomes a permanent monopoly, or is there something about how giant IPOs get priced that I am missing?"
2. **The bull case, as commenters put it:** "They're basically betting on Anthropic becoming plumbing for the entire digital economy" (a commenter)
3. **Some doubt any one company can win.** "every AI company is assuming the same thing. They are pricing their stocks as if they are the last one standing" (a commenter)
4. **Others are cynical about who bears the risk.** "Socialism of risk, not gains." (a commenter)
5. **The related-posts headlines are unverified.** They mention a record $81.3B IPO raise, and a chart post saying the IPO priced at 31x revenue, about the typical multiple at the 2000 dot-com peak (2.5K upvotes).
6. **Openness isn't discussed.** Even so, a valuation that depends on durable dominance is exactly what cheap open-weight models threaten (our inference; compare the price-ceiling comment in R4).

- **Balance:** 25 visible comments. About 10 explain the valuation as a bet on future recurring revenue, about 12 are skeptical or cynical, 1 is bullish and 2 are tangents or empty.

### Hacker News threads

#### H1. Valkey Is Rapidly Overtaking Redis (HN, linking a devops.com article)

- **Link:** https://news.ycombinator.com/item?id=40092449 · **Type:** HN discussion (192 points, 85 comments, all visible) · **Date:** 2024-04-19

1. **Commenters say trust, not license text, drives switching.** "People are switching because at this point they think they can’t trust Redis Labs not to do more dumb stuff later." (a commenter). Others note that Redis's creator had retired and that Redis Labs never employed most contributors.
2. **The vendor's dilemma is acknowledged.** "You're trapped between AWS eating you or having to relicense and AWS eating you." (a commenter). The reply: very few source-available projects ever take off.
3. **History favours forks.** "attempting to make free non-free will result in a fork taking over." (a commenter, citing Hudson and Jenkins). Others mention XFree86 and OpenOffice.org.
4. **The lesson is in license design.** "(L)GPL with no CLA cannot be changed later." (a commenter). Another notes that Redis Labs required contributors to sign a CLA handing over their copyright.
5. **The early metrics are contested.** One commenter's tool counted 14 Redis versus 48 Valkey pull-request contributors; another counted 8 versus 41 commit authors in a month. Skeptics answered that "a fork in its inception will have a burst of activity".
6. **One commenter notes an irony.** "Seemingly a bunch of companies are happy to start paying for open source, when weeks ago many were passive consumers." AWS was described as a major Valkey backer.

- **Balance:** Of 85 comments, about 24 back the fork or criticise Redis Labs, and about 5 defend Redis's need to earn money against cloud providers. About 10 doubt the headline and the early numbers (one calls the article propaganda), plus a run of jokes. A side thread of about 12 debates whether to contribute to company-backed projects at all.

#### H2. Anthropic's War on open source AI (HN, linking an X/Twitter post)

- **Link:** https://news.ycombinator.com/item?id=49332564 · **Type:** HN discussion (152 points, 59 comments) · **Date:** ~2026-08 (shown as "3 months ago"); a commenter dates the linked post to June 2026

1. **Most of the thread is about the post's form.** Many read it as AI-generated. "I would genuinely like to hear from anyone who considers these 5000-word-plus AI-authored posts to be worthwhile, persuasive, and/or impressive." (a commenter)
2. **The post's claims reach the thread only through one commenter's AI-generated summary (unverified).** They allege anticompetitive conduct: cutting off rivals, terms against training on Claude outputs, and allegedly degraded output for AI-development work. They also allege safety and national-security framing used to shape regulation and "dismiss Chinese open models as a security threat rather than competing on openness".
3. **Some see the safety case as a bid for control.** "Anthropic's argument inherently leads to the conclusion that there is actually a dictator, and that dictator is Anthropic." (a commenter, after reading Dario Amodei's essay *Machines of Loving Grace*)
4. **Some argue the weights should go to everyone.** "Why should frontier companies be the ones controlling access to the model weights and gatekeeping research?" (a commenter, who argues that concentrating models raises risk rather than lowering it)
5. **Regulation is read as capture.** "Regulated AI right now is a grift game." (a commenter). A more deflating comment says Anthropic simply lobbies the government, as others do.
6. **The defence is faint.** One commenter urges reading Anthropic's own writing; while conceding it is a cult, he says "they have been relatively transparent with their views".

- **Balance:** About two-thirds of the 57 visible comments are about AI-written prose or X's logged-out experience. Nearly all of the ~17 substantive comments are critical of Anthropic, and none cites Anthropic's published position on open weights.

#### H3. OpenTF is now OpenTofu (HN, linking github.com/opentofu)

- **Link:** https://news.ycombinator.com/item?id=37581132 · **Type:** HN discussion (438 points, 246 comments, 222 visible) · **Date:** 2023-09-20

1. **The fork launched under the Linux Foundation.** A commenter identifying as OpenTofu's interim tech lead announced "we're officially part of the Linux Foundation". Its steering committee has seats for Gruntwork, Harness, Spacelift, env0 and Scalr.
2. **Commenters disagree about why HashiCorp relicensed.** "Open Source businesses have no future in a world where big tech can gulp your product for free." (a commenter). Others reply that HashiCorp's enterprise pricing was the problem, not Amazon.
3. **Some ask why HashiCorp skipped copyleft.** "Surely it would have been a good idea to try a strong copyleft licence like AGPL first." (a commenter). The reply: many companies won't touch AGPL.
4. **Some doubt how broad the fork's support is.** "It feels like this support comes from the vocal minority and competitors." (a commenter). Supporters point to about 19 full-time engineers on the fork, more than HashiCorp had on Terraform.
5. **One commenter foresaw the switching calculus.** "If your corporation(s) don’t resell service deriving from Terraform, then there’s no financial reason to switch" (a commenter). That is the same dynamic the 2026 r/Terraform thread (R2) reports.
6. **The rename was about trademarks.** "The name OpenTofu was adopted out of concern for, as you might have already guessed, trademark litigation." (a commenter quoting The Register)

- **Balance:** By a rough keyword count, about a third of the 222 visible comments touch on licensing, pricing, governance or HashiCorp; most of the rest are about the name, the website or jokes. Substantive comments mostly back the fork or blame HashiCorp's pricing. A minority defends HashiCorp's right to relicense, or argues that sustainable open source needs some proprietary part.

### Blogs and research pages

#### B1. Open-source relicensing in 2026: what actually happened (FlowVerify)

- **Link:** https://www.flowverify.co/blog/open-source-relicensing-2026-what-happened · **Type:** vendor blog. FlowVerify sells e-signature and contract software in India; the byline is "FlowVerify Editorial Team", and the on-page headline differs: "Open-source business models in 2026: what the dust finally settled on". · **Date:** 2026-05-10

1. **Thesis:** "The cloud providers won, the forks are real and healthy, and license reversals did not reverse community migration"
2. **Redis and Valkey (the blog's figures, unsourced on the page):** Redis added AGPLv3 in May 2025. Valkey averages 80 pull requests a month to Redis's 42, a 2025 Percona survey found 83% of large enterprises testing or running Valkey, and Aiven migrated 15,000 servers. "trust is not restored by a licence file change."
3. **HashiCorp and OpenTofu:** IBM bought HashiCorp for $6.4B (February 2025) and kept the BSL. OpenTofu is nearing 10 million downloads and has 160+ active contributors, and Fidelity migrated 4 million resources. OpenTofu's adoption is still modest, and Terraform keeps the larger share: "Overall IaC practitioner adoption sits around 12%, with 27% of teams planning to evaluate or expand it"
4. **What the surviving forks share:** cloud-provider or infrastructure-vendor backing from day one, Linux Foundation governance, OSI-approved licenses and real enterprise migrations. The caveat: "Smaller projects forked under similar pressure have mostly gone quiet."
5. **Its advice:** "AGPL is the new default defensive licence" (a section heading), and choosing infrastructure is now a governance decision.
6. **Accuracy flag:** the post says "All three forks use Apache 2.0." The tracker (B2) lists Valkey as BSD and OpenTofu as MPL 2.0. Those are the licenses that forking Redis's BSD code and Terraform's MPL 2.0 code would produce, so treat the blog's other figures as unverified.

#### B2. Open Source Relicensing Tracker 2026: Dates, Licenses, Forks (OpenSource Risk Experts)

- **Link:** https://opensourcelicenserisk.com/research/state-of-relicensing-exposure-2026/ · **Type:** research page of a license-risk consultancy that works for buyers; it sells exposure reviews and says it does not give legal advice · **Date:** updated 2026-06-25

1. **The tracker's table:**
   - MongoDB went from AGPLv3 to SSPLv1 in October 2018. It has no OSI-approved option; the listed alternative is FerretDB.
   - Elasticsearch and Kibana went from Apache 2.0 to SSPL plus the Elastic License in 2021 (version 7.11). An AGPLv3 option followed in September 2024; the fork is OpenSearch.
   - HashiCorp's tools went from MPL 2.0 to BSL 1.1 in August 2023, with no OSI option. The fork is OpenTofu (MPL 2.0, Linux Foundation/CNCF).
   - Redis went from BSD-3 to RSALv2 plus SSPLv1 in March 2024. An AGPLv3 option arrived in May 2025 (Redis 8); the fork is Valkey (BSD, Linux Foundation).
2. **The outcomes split.** "Two, HashiCorp and MongoDB, remain source available with no OSI approved open option."
3. **For buyers, relicensing is an exposure.** "In every case the license changed after the software was already running in production, which is what turns a licensing decision into an exposure."
4. **AGPL is not a free pass.** "AGPLv3, which Elastic and Redis added, is OSI approved but is strong copyleft", so it can impose obligations the old permissive license didn't.
5. **The page is short and commercial.** About 3,700 characters, ending in an offer of a free exposure review.

#### B3. Open-sourcing CORE One CAD Files Under the New Open Community License (OCL) (Prusa blog)

- **Link:** https://blog.prusa3d.com/core-one-cad-files-release-under-the-new-open-community-license-ocl_127290/ · **Type:** company blog post by Josef Průša, with 27 reader comments · **Date:** 2025-12-19

1. **What is released, and on what terms.** The full STEP and Fusion files for the CORE One and CORE One L frames are out under the OCL. It allows inspecting and modifying the files and sharing changes under the same license, using them commercially in-house, and making spare parts. It does not allow selling machines or remixes without a separate agreement: "you just can’t make money selling the machines."
2. **The new license responds to cloning and patent trolling.** A foreign entity obtained a US design patent (D1055176) on Soozafone's Creative-Commons-licensed Dummy 13 figure and has demanded fees of over $10,000 a year. Prusa is funding a reexamination. "Proving prior art against spam of foreign patents costs thousands of dollars per case and takes months or years."
3. **The post is honest about the license's limits.** "Would OCL have stopped the patent from being granted? The short answer is: No." What the OCL adds is an explicit patent grant and a breach-of-contract remedy. It also has an anti-AI/data-mining clause and writes in a right to repair.
4. **The software stays open.** PrusaSlicer and the firmware stay GPL, and the OpenPrintTag RFID standard is MIT. On the forked software: "it wouldn’t be hard to rewrite the rest and close it down. But that would be against everything we stand for."
5. **Prusa now files patents and offers a coalition.** It files utility and design patents and offers cross-licensing to companies that contribute. "These patents exist to stop industrial clones, not your garage workshop." iFixit's Kyle Wiens endorses the balance.
6. **Reader comments (27):** 7 are spam. Of the other 20, 11 are supportive. 5, from 4 people, object to calling a license that isn't OSI-approved open source ("This is just the Prusa Commercial Restrictive License 1.0."). 4 raise specific concerns: overlap with CERN-OHL-S, the anti-data-mining clause versus archiving and search indexing, prior art for Prusa's own cooling patent, and paying community contributors to the MMU.

#### B4. The Arduino Terms of Service and Privacy Policy update: setting the record straight (Arduino blog)

- **Link:** https://blog.arduino.cc/2025/11/21/the-arduino-terms-of-service-and-privacy-policy-update-setting-the-record-straight/ · **Type:** company blog post (Arduino Team) · **Date:** 2025-11-21, the same day as the R1 thread

1. **Arduino reassures users.** "Let us be absolutely clear: we have been open-source long before it was fashionable." It says the Qualcomm acquisition changes neither how user data is handled nor its open-source principles.
2. **The reverse-engineering limits apply only to its cloud software.** "Restrictions on reverse-engineering apply specifically to our Software-as-a-Service cloud applications. Anything that was open, stays open."
3. **The stated reasons for the update:** clearer data-practice disclosures, AI features, billing terms for its paid Premium services, and US privacy law and export controls. On AI: "As we introduce optional AI-powered features, such as those in the Arduino UNO Q and Arduino App Lab, we needed to update our terms"
4. **User content and minors:** published content stays the user's, and inactive accounts are deactivated after 24 months, with forum usernames kept for attribution.
5. **What the post leaves out:** it does not mention patents, the change one R1 commenter called the most dangerous.

#### B5. OSHWA Annual Survey (OSHWA community archive)

- **Link:** https://community.oshwa.org/t/oshwa-annual-survey/534/ · **Type:** listed as a blog in `sources.tsv`, but actually a post in OSHWA's read-only community-forum archive · **Date:** 2022-10-06

1. **The page is nearly empty.** It is about 1,000 characters: an announcement of the 2022 survey (5–20 minutes to complete) and a preview of the Google Forms link.
2. **It has no results.** There is no survey data on the page, so the captured material holds no quantitative evidence about open-hardware businesses or communities.
3. **Follow-up:** any survey results OSHWA published would need a separate fetch.

### Forum

#### F1. Prusa 3D lays off nearly twenty five percent of developers due to financial issues (Prusa forum)

- **Link:** https://forum.prusa3d.com/forum/english-forum-general-discussion-announcements-and-releases/prusa-3d-lays-off-nearly-twenty-five-percent-of-developers-due-to-financial-issues/ · **Type:** forum thread (only page 1 of 4 was captured) · **Date:** started 2026-03-15

1. **The memo, as translated by the poster from a screenshot (staff later confirmed it is real):** Prusa had 1,144 staff, and since the start of the year sales had not reached even 90% of target. It cites high fixed costs, more competition and a weaker dollar, and announces job cuts plus cost controls to restore 2024 margins. "our costs are increasing faster than our revenues"
2. **Staff dispute the headline figure.** A forum admin passed on a colleague's Reddit post: "the post is real but the 25% fact is totally off base". The same colleague had already called the 25% figure untrue on the forum.
3. **Members blame competition.** They point to Bambu Lab's easy machines and Prusa's late products (Core One, INDX). "People just want to print rather then tinker, and Bambu do have that cracked." (a member)
4. **Some now see open source as a liability.** "I've felt for a long time that although the spirit behind OSS is admirable, the long term outlook is rather bleak." (a member, who wonders whether PrusaSlicer will stay open and argues a European maker can't out-manufacture China). Another says Prusa's hardware stopped being open with the XL.
5. **Others defend it.** They want open firmware and software kept. "It's also a huge benefit to be able to print repair parts and modified parts." (a member)

- **Balance (page 1 only):** 20 posts from 13 people, mostly sympathetic to Prusa. 2 posts from forum admins dispute the 25% figure. On openness, 2 members would accept Prusa closing more and 2 defend open firmware, software and repairability.

## (c) Cross-source synthesis

**(1) Business models: what actually works.** The talks agree that openness alone doesn't pay. Olson found that services-only firms starve the core product and called dual licensing "distributing the poison and selling the antidote"; Cloudera sold proprietary tools on top of open Hadoop. GitLab tried donations, consulting, paid features and support before settling on open core (about 90% margins), priced by the buyer's seniority. The 2026 r/startups advice is the same model for the SaaS era: an open core, paid hosting and team features, and self-hosters treated as marketing. Nagle supplies the macro case: about $9 trillion of value, contributors earning twice the return of free riders, and a rule to "collaborate on the core and compete on the edges". Oliphant, who wrote NumPy while a BYU professor, gives the scientific-software view: openness matters most where published work would otherwise need proprietary software to run, and the people who write widely used code still have no good way to be paid for it.

**(2) Relicensing and forks.** The pattern: a permissive project, a cloud provider selling it as a service, a vendor moving to SSPL, BSL or RSAL, then a fork hosted by a foundation. Sijbrandij described the clouds' "fork and commoditize" answer back in 2019. The outcomes differ. Elastic and Redis later added AGPLv3; HashiCorp (now IBM) and MongoDB did not. Valkey, backed by the hyperscalers, spread fast: FlowVerify cites 83% of large enterprises testing or running it, an unverified figure. OpenTofu, backed by smaller Terraform-automation vendors, sits near 12% of practitioners by the same source, and a 77x search gap persists (partly a documentation artefact, commenters say). An HN commenter foresaw why in 2023: the BSL never touched internal users. Reaction centres on trust ("trust is not restored by a licence file change") and on structure. Copyleft without a CLA cannot be relicensed, which sits awkwardly with the r/startups advice to add a CLA early.

**(3) Open hardware economics and trust.** Hardware openness is narrowing to repair, modification and software. Prusa's OCL opens the CORE One CAD files but bars selling machines or remixes. It adds a patent grant and an anti-data-mining clause, and comes with new Prusa patents, because "prior art is not a shield"; four readers objected to calling it open source. In March 2026 a leaked memo, confirmed by staff (who disputed the 25% figure), described costs outrunning revenue amid competition that members attribute to Bambu Lab; two members called open source a liability. Arduino's post-Qualcomm terms met near-uniform hostility. Its reply ("Anything that was open, stays open.") skipped the patent clause an R1 commenter feared, and with clones a click away, that trust is fragile. Adafruit is the counter-model: publish everything and sell kits. Nagle calls open hardware under-studied, and the captured OSHWA page holds no data.

**(4) Open-weight AI: perception versus stated positions.** In the captured threads, Anthropic is seen as the lab most hostile to open weights, its safety arguments read as regulatory capture or margin protection. OpenAI's gpt-oss is remembered as a one-off "marketing stunt", yet one commenter still rates OpenAI "more open than Anthropic". Anthropic's 2026-07-27 post says it "has never advocated for a ban on open-weights models" and calls open-weight models without dangerous capabilities "a public good". No captured comment cites that post, not even in November's r/OS_AI thread, whose premise rests on a disputed video. A related-post title from about four months earlier had already called a denial "gaslighting". The gap has visible causes: commenters see Anthropic releasing nothing open, critics cite its terms against training on Claude outputs, and the qualifier about dangerous capabilities is easily heard as a ban (our reading). The IPO thread (about $1.3T, per its poster) shows the commercial stakes behind that distrust.

**(5) Self-driving labs and the physical sciences.** The Radical AI talk shows where the value sits in a self-driving lab. Off-the-shelf foundation models (SAM 2) failed on the arc melter, and Gaussian-process Bayesian optimization suited open formulation spaces poorly. What worked was a vertically integrated loop whose LLM agents converged only once given 1,000+ in-house experiments as context. Openness never comes up: the moat is the proprietary flywheel of data and hardware. Our inference: shared experimental datasets and open, repairable lab hardware are the commons worth funding, or self-driving-lab gains will compound inside firms. Nagle's evidence that contributing pays, and Prusa's OCL, point to middle paths.

## (d) Summary table

| # | Source | Type | Stance on openness | One-line takeaway |
|---|---|---|---|---|
| Y1 | Nagle, The Economic Value of Open Source | youtube | pro | About $9T of value, contributors get twice the benefit; collaborate on the core, compete on the edges. |
| Y2 | Olson, Open Source Business Models | youtube | mixed | Services-only firms languish and dual licensing starts with a threat; sell proprietary tools on an open core. |
| Y3 | Sijbrandij, Commercial Open Source Business Models | youtube | mixed | Donations, consulting and support failed; buyer-based open core (90%+ margins) is GitLab's hedge against hyperclouds. |
| Y4 | Fried, Adafruit (MAKERS) | youtube | pro | Publish everything; the business grew from requests for kits and from community. |
| Y5 | Radical AI, Self-Driving Labs (Cornell Tech) | youtube | n/a | Closed, in-house lab loop; generic models failed; agents worked once fed in-house experiment data. |
| Y6 | Oliphant and Fridman clip | youtube | mixed | NumPy's creator, not "an open source zealot": published code shouldn't need proprietary software to run, and paying the people who write widely used code is unsolved. |
| R1 | Arduino terms (r/hardware) | reddit | pro | Uniformly hostile to Qualcomm's terms; one commenter flags the patent clause; clones make leaving easy. |
| R2 | OpenTofu's 77x search gap (r/Terraform) | reddit | mixed | Search share understates OpenTofu use, but the BSL rarely affected internal users. |
| R3 | gpt-oss, 350 days on (r/LocalLLaMA) | reddit | pro | gpt-oss seen as one-off PR; little expectation of a successor. |
| R4 | "Anthropic wants to ban open source models" (r/OS_AI) | reddit | pro | Anthropic seen as using regulation to protect margins; a few dispute the premise. |
| R5 | Open-source startup revenue (r/startups) | reddit | pro | Open for trust; charge for hosting, operations and team features; AGPL plus an early CLA. |
| R6 | Anthropic's $1.3T IPO (r/NoStupidQuestions) | reddit | n/a | Valuation read as a bet on lasting dominance; mostly skeptical. |
| H1 | Valkey overtaking Redis (HN, 2024) | hn | pro | Trust broke and forks win when contributors and clouds move; a few defend Redis's dilemma. |
| H2 | Anthropic's war on open source AI (HN, 2026) | hn | pro | Mostly complaints about an AI-written post; substantive comments see the safety case as control. |
| H3 | OpenTF is now OpenTofu (HN, 2023) | hn | pro | Fork welcomed under the Linux Foundation, with doubts that its backing goes beyond rivals; much talk of the name. |
| B1 | FlowVerify, relicensing in 2026 | blog | pro | Forks healthy, clouds won, AGPL the new defensive default; contains license errors. |
| B2 | Relicensing tracker 2026 | blog | mixed | Relicensing is an exposure for buyers; MongoDB and HashiCorp still lack an OSI option. |
| B3 | Prusa, Open Community License | blog | mixed | Source-available hardware license: repair and in-house use allowed, resale not; patents as a shield. |
| B4 | Arduino, setting the record straight | blog | pro | "Anything that was open, stays open."; silent on patents. |
| B5 | OSHWA Annual Survey | blog (forum archive) | n/a | 2022 survey announcement only; no data. |
| F1 | Prusa layoffs thread | forum | mixed | Memo confirmed, 25% figure disputed; some members now see open source as a liability. |

*n/a* means the source does not address openness, or was not captured. The stance column for threads describes the prevailing commenter view. No captured source opposes openness as such: the critical voices are about who controls it, and on what terms.

**About `voices_index.csv`:** `chars_or_segments` is the number of caption segments for YouTube rows and the number of characters of captured page text for the rest. In `date_if_known`, a `~` marks dates worked out from relative times ("6mo ago") as of 2026-11-23, and `inferred` marks a date deduced from the content.
