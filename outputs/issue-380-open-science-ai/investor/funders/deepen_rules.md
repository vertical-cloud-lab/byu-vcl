# Deepening pass: complete the funding history of well-funded ventures

A first pass already recorded some rounds for each of your ventures (listed in your `existing_<pass>.md`). These
ventures raised a lot, but the first pass found few investors or missed early rounds, often because the session's
web-search budget ran out. Your job is to **fill the gaps**: every round from the first seed or angel money to the
latest round or exit, and every investor each announcement names.

Follow `deal_rules.md` for fields and investor names, with these differences:

- **Record only what is new.** Don't repeat a round already listed in `existing_<pass>.md`. If you find more
  investors for a round that is already listed, record a round with the same type, date and amount, listing only
  the additional names, and put `adds to existing round` in its `note`.
- If you think an existing round is wrong (wrong company, wrong investor), don't change it: say so in the venture's
  `notes`, starting with `CHECK:`.
- Copy `key`, `venture` and `universe` from your input; give `funding_found` `yes` if you add any round, and fill
  `status`, `country`, `founded` and `open_basis` only if you are sure.

## Where to look (no WebSearch: the session's budget is spent)

1. The company's own newsroom or blog: try `/blog`, `/news`, `/press`, `/newsroom`, `/company`, `/about`, and its
   funding posts (e.g. "announcing our Series B"). Each usually names the lead and all participants.
2. Wikipedia: the company's article and the URLs in its references (fetch the cited articles: TechCrunch,
   VentureBeat, GeekWire, Reuters, Bloomberg, Forbes, WSJ, FT, InfoWorld). `python3 scripts/find_pages.py
   "<Company>" --site <https://company-site>` prints TechCrunch, SiliconANGLE, BetaKit, TechNode, Hacker News and
   Wikipedia matches at once.
3. The lead investors' own announcement posts and portfolio pages.
4. For companies that listed in the US: the S-1/F-1 "Principal Stockholders" table and "Description of Capital
   Stock" (SEC EDGAR, curl with header `User-Agent: research script admin@example.com`).
5. Dead pages: `https://web.archive.org/web/2020*/<url>` (or fetch `https://archive.org/wayback/available?url=<url>`).

Use WebFetch, or `curl -sL -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124
Safari/537.36' '<url>'` via Bash for pages WebFetch can't read. Spend up to ~8 fetches on a big company.

Append through `python3 scripts/append_deals.py <pass> <<'JSON' ... JSON` from the `funders/` folder, 2–4 ventures
per call, as you go. Never record a name or number from memory. When done, reply in at most 10 lines: ventures
improved, rounds added, anything uncertain. Don't repeat the data.
