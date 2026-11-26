#!/usr/bin/env python3
"""Hand classification of funders (by the firm's own description of itself; general knowledge, checked where unsure).

Writes data/investor_types.csv (investor, type, group, notes). Types: venture_firm, corporate_venture, accelerator,
growth_pe_hedge (growth equity, crossover, hedge funds, asset managers, private equity, banks investing from balance
sheet in late rounds), public_investor (state, sovereign or public development investors), philanthropy,
government_grant, crowdfunding, crypto_fund_or_dao, bank_or_debt, company (a company investing that has no venture
arm named), other. People are typed `angel` automatically and are not listed here. `group` rolls corporate arms up
to their parent for a group-level count. Run from funders/.
"""
import csv

V = "venture_firm"; C = "corporate_venture"; A = "accelerator"; G = "growth_pe_hedge"; P = "public_investor"
PH = "philanthropy"; GG = "government_grant"; CF = "crowdfunding"; CR = "crypto_fund_or_dao"; B = "bank_or_debt"
CO = "company"; O = "other"
T = {
 # venture firms
 "Accel": V, "Sequoia Capital": V, "Andreessen Horowitz": V, "New Enterprise Associates": V, "Benchmark": V,
 "Index Ventures": V, "CRV": V, "Lightspeed Venture Partners": V, "Amplify Partners": V, "Bessemer Venture Partners": V,
 "OSS Capital": V, "Redpoint Ventures": V, "True Ventures": V, "SV Angel": V, "Nexus Venture Partners": V,
 "Sapphire Ventures": V, "General Catalyst": V, "Battery Ventures": V, "GGV Capital (US arm now Notable Capital)": V,
 "Lux Capital": V, "Bain Capital Ventures": V, "Greylock Partners": V, "Kleiner Perkins": V, "Craft Ventures": V,
 "Felicis": V, "Spark Capital": V, "Georgian": V, "IVP": V, "Khosla Ventures": V, "Madrona Venture Group": V,
 "Menlo Ventures": V, "Costanoa Ventures": V, "Heavybit": V, "Peak XV Partners (formerly Sequoia India)": V,
 "Alumni Ventures": V, "Geodesic Capital": V, "Greycroft": V, "Mango Capital": V, "Mayfield": V, "Pillar VC": V,
 "Matrix Partners": V, "Balderton Capital": V, "Foundry Group": V, "Sutter Hill Ventures": V, "LocalGlobe": V,
 "Meritech Capital Partners": V, "Pace Capital": V, "SignalFire": V, "Thrive Capital": V, "Trinity Ventures": V,
 "8VC": V, "A Capital": V, "Caffeinated Capital": V, "Foundation Capital": V, "K5 Global": V, "Shasta Ventures": V,
 "Uncorrelated Ventures": V, "Yunqi Partners": V, "Canaan Partners": V, "Crane Venture Partners": V, "Dawn Capital": V,
 "Radical Ventures": V, "Vertex Ventures US": V, "468 Capital": V, "AIX Ventures": V, "Addition": V, "Anzu Partners": V,
 "Blossom Capital": V, "Cherry Ventures": V, "Creandum": V, "Decibel": V, "Eclipse Ventures": V, "Emergence Capital": V,
 "First Round Capital": V, "Founders Fund": V, "Headline": V, "Matrix Partners China": V, "OpenView Venture Partners": V,
 "Quiet Capital": V, "Seedcamp": V, "Swift Ventures": V, "TQ Ventures": V, "Tribe Capital": V, "Union Square Ventures": V,
 "Unusual Ventures": V, "Walden Catalyst": V, "137 Ventures": V, "1789 Capital": V, "42CAP": V, "5Y Capital": V, "AVP": V,
 "Avalon Ventures": V, "Avra Capital": V, "Betaworks": V, "Bow Capital": V, "Compound": V, "Counterpart Ventures": V,
 "DCVC": V, "DTCP": V, "Eight Roads": V, "Flex Capital": V, "Frontline Ventures": V, "Gaingels": V, "IDTheory": V,
 "January Capital": V, "Kima Ventures": V, "La Famiglia": V, "Long Journey Ventures": V, "Morgenthaler Ventures": V,
 "Norwest Venture Partners": V, "Preston-Werner Ventures": V, "Root Ventures": V, "S28 Capital": V, "Scale Venture Partners": V,
 "Shine Capital": V, "Sierra Ventures": V, "Slow Ventures": V, "Susa Ventures": V, "TransLink Capital": V, "Uncork Capital": V,
 "Visionaries Club": V, "ZhenFund": V, "Qiming": V, "HongShan (formerly Sequoia China)": V, "JAFCO": V, "Pioneer Fund": V,
 "Initialized Capital": V, "Boldstart Ventures": V, "Essence VC": V, "Work-Bench": V, "Basis Set Ventures": V,
 "Two Sigma Ventures": V, "Point Nine": V, "Atomico": V, "Earlybird": V, "Speedinvest": V, "Northzone": V, "Partech": V,
 "Elaia": V, "Serena": V, "Runa Capital": V, "Mayfield Fund": V, "Afore Capital": V, "Fly Ventures": V, "Conviction": V,
 "Haystack": V, "Kindred Ventures": V, "Wing Venture Capital": V, "Pear VC": V, "Lerer Hippeau": V, "Bloomberg Beta": V,
 "Contrary": V, "Notable Capital": V, "Hummer Winblad": V, "Draper Fisher Jurvetson": V, "DFJ": V, "Ignition Partners": V,
 "Mohr Davidow Ventures": V, "Polaris Partners": V, "North Bridge Venture Partners": V, "Sigma Partners": V,
 "Battery": V, "RRE Ventures": V, "Hyde Park Venture Partners": V, "Plural": V, "Project A": V, "HV Capital": V,
 "Lakestar": V, "Notion Capital": V, "Hoxton Ventures": V, "Hummingbird Ventures": V, "Elad Gil": V,
 "NFDG": V, "AI Grant": A, "Cathay Innovation": V, "Breega": V, "Drive Capital": V, "Acrew Capital": V, "Baseline Ventures": V,
 "Brighton Park Capital": V, "Brave Capital": V, "Buckley Ventures": V, "Cadenza Ventures": V, "Capital Fund Management": V,
 "Crunchfund": V, "Definition Capital": V, "Delphi Ventures": V, "Dorilton Ventures": V, "Dragoneer": G, "eLab Ventures": V,
 "Osage University Partners": V, "Stellar Ventures": V, "TIE Angels Group Seattle": V, "AE Ventures": V, "Blumberg Capital": V,
 "Cypress Growth Capital": B, "Common Metal": V, "PSG Equity": G, "DTCP Growth": G, "Scaleup Europe Fund": V,
 "Prosperity7 Ventures": C, "USIT": V, "Plural Platform": V, "Robot Ventures": CR, "CoinFund": CR, "L1 Digital": CR,
 "North Island Ventures": CR, "Seed Club Ventures": CR, "Protocol Labs": CR, "Paradigm": CR, "Pantera Capital": CR,
 "Polychain Capital": CR, "Multicoin Capital": CR, "Dragonfly": CR, "Electric Capital": CR, "Coinbase Ventures": CR,
 "Binance Labs": CR, "Fenbushi Capital": CR, "Framework Ventures": CR, "1kx": CR, "Placeholder": CR, "Hack VC": CR,
 # growth, crossover, PE, asset managers
 "Tiger Global": G, "Coatue": G, "Insight Partners": G, "Altimeter Capital": G, "Bain Capital": G, "Hillhouse": G,
 "Mirae Asset": G, "Iconiq": G, "Adams Street Partners": G, "Atreides Management": G, "Baillie Gifford": G,
 "BlackRock": G, "DST Global": G, "Eurazeo": G, "Fidelity": G, "Franklin Templeton": G, "Goldman Sachs": G,
 "J.P. Morgan": G, "KKR": G, "Morgan Stanley (Counterpoint Global)": G, "T. Rowe Price": G, "General Atlantic": G,
 "TCV": G, "Silver Lake": G, "Thoma Bravo": G, "Vista Equity Partners": G, "Summit Partners": G, "Warburg Pincus": G,
 "Accel-KKR": G, "D1 Capital Partners": G, "Wellington Management": G, "Durable Capital Partners": G, "Lead Edge Capital": G,
 "Apollo Global Management": G, "Point72 Turion": G, "Alkeon Capital": G, "Franklin Templeton Investments": G,
 "Capital Group": G, "Dragoneer Investment Group": G, "Advent": G, "Blackstone": G, "Carlyle": G, "EQT": G, "Permira": G,
 "Hellman & Friedman": G, "Francisco Partners": G, "Great Hill Partners": G, "Kohlberg Kravis Roberts": G,
 "SoftBank (Vision Fund)": G, "Valor Equity Partners": G, "Greenoaks": G, "Lone Pine Capital": G, "Sands Capital": G,
 # state, sovereign, public
 "GIC": P, "Temasek": P, "Mubadala": P, "QIA": P, "Bpifrance": P, "Export Development Canada": P,
 "European Investment Bank": P, "Beijing AI Industry Investment Fund": P, "Shenzhen Capital Group": P, "In-Q-Tel": P,
 "CPP Investments": P, "MGX": P, "CDP Venture Capital": P, "High-Tech Gründerfonds": P, "KfW Capital": P,
 "European Innovation Council": GG, "EIC Fund": P, "British Business Bank": P, "Ontario Teachers' Pension Plan": P,
 "Canada Pension Plan Investment Board": P, "Abu Dhabi Investment Authority": P, "Public Investment Fund": P,
 # corporate and strategic
 "NVIDIA (incl. NVentures)": C, "Intel Capital": C, "Salesforce Ventures": C, "Samsung": C, "M12": C,
 "Qualcomm Ventures": C, "Cisco Investments": C, "GV": C, "CapitalG": C, "Gradient Ventures": C, "Alibaba": C,
 "Alibaba Cloud": C, "Tencent": C, "Amazon": C, "Dell Technologies Capital": C, "AMD": C,
 "Google": C, "IBM": C, "Robert Bosch Venture Capital": C, "Databricks Ventures": C, "Digital Science": C,
 "Red Hat": C, "Arm": C, "Comcast Ventures": C, "Fujitsu": C, "GitHub": C, "KDDI": C, "LG Electronics": C,
 "MongoDB Ventures": C, "Mozilla Ventures": C, "ServiceNow": C, "VMware": C, "Aramco Ventures (incl. Prosperity7)": C,
 "Citi": C, "Microsoft": C, "Oracle": C, "Snowflake Ventures": C, "Atlassian Ventures": C, "HPE (Hewlett Packard Pathfinder)": C,
 "Renesas": C, "Sony Semiconductor Solutions": C, "Stratasys": C, "ASML": C, "Siemens": C, "Hitachi": C, "SoftBank": G,
 "Samsung Electronics": C, "Hugging Face": C, "Cloudflare": C, "Okta Ventures": C, "Workday Ventures": C,
 "Capital One Ventures": C, "RTX Ventures": C, "Aramco Ventures": C, "Cooler Master": C, "Automattic": C,
 "Meituan": C, "Xiaomi": C, "Baidu": C, "Ant Group": C, "JD.com": C, "ByteDance": C, "Lenovo": C, "Huawei": C,
 "NetApp": C, "Juniper Networks": C, "Ericsson Ventures": C, "Deutsche Telekom": C, "SK Telecom": C, "SK hynix": C,
 "Western Digital": C, "Seagate": C, "Micron": C, "Applied Materials": C, "Lam Research": C, "Toyota": C,
 "Toyota Ventures": C, "BMW i Ventures": C, "Porsche Ventures": C, "Bosch": C, "Shopify": C, "Stripe": C,
 "Datadog": C, "Elastic": C, "HashiCorp": C, "Confluent": C, "Vercel": C, "Supabase": C, "PostHog": C, "Sentry": C,
 # accelerators, studios
 "Y Combinator": A, "500 Global": A, "Techstars": A, "SOSV": A, "Entrepreneur First": A, "Antler": A,
 "South Park Commons": A, "Mozilla Builders": A, "Open Core Ventures": A, "Plug and Play": A, "Alchemist Accelerator": A,
 "Neo": A, "HF0": A, "Founders Inc": A, "Speedrun": A, "German Accelerator": A, "Station F": A, "Berkeley SkyDeck": A,
 # crowdfunding
 "Kickstarter backers": CF, "Crowd Supply backers": CF, "Indiegogo backers": CF, "Community investors": CF,
 # banks and lenders
 "Silicon Valley Bank": B, "Hercules Capital": B, "Western Technology Investment": B, "TriplePoint Capital": B,
}

T.update({
 "IDG Capital": V, "OpenOcean": V, "Lunar Ventures": V, "Sunflower Capital": V, "ISAI": V, "Standard Capital": V,
 "Theory Ventures": V, "BOND": G, "Citi Ventures": C, "FirstMark": V, "Lytical Ventures": V, "Obvious Ventures": V,
 "Thomvest Ventures": V, "Venrock": V, "firstminute capital": V, "First Minute Capital": V, "AME Cloud Ventures": V,
 "Abstract Ventures": V, "Bezos Expeditions": "angel", "DFJ Growth": G, "Factory": V, "Metaplanet": V,
 "Soma Capital": V, "Sorenson Capital": V, "System.One": V, "e.ventures": V, "Harpoon Ventures": V,
})

T.update({
 # venture firms (hand-typed from the second review of unclassified names)
 "Orange Collective": V, "BoxGroup": V, "500 Emerging Europe": V, "Tokyo Black": V, "Transpose Platform": V,
 "83 North": V, "AMP (Anjney Midha)": V, "Alven": V, "Centralway": V, "Cue Ball": V, "Dinghui Baifu": V,
 "Ibex Investors": V, "Inflection.xyz": V, "Innovation X": V, "Jinhuifeng": V, "NFX": V, "Oak HC/FT": V,
 "Pebblebed": V, "Pitango": V, "Planven": V, "Portage": V, "RTP Global": V, "SaxeCap": V, "Square Peg": V,
 "Target Global": V, "Village Global": V, "49 Palms": V, "Ace & Company": V, "AlleyCorp": V, "Amino Collective": V,
 "ArkStream": V, "Astella": V, "BGV": V, "Chapter One": V, "DCM": V, "Disruptive": V, "Draper Associates": V,
 "Evantic": V, "F-Prime": V, "Factorial": V, "Fifty Years": V, "Firestreak": V, "Floodgate": V, "Founder Collective": V,
 "Founder's Co-op": V, "Freestyle": V, "Fundomo": V, "GP Bullhound": V, "GRC SinoGreen": V, "Global Brain": V,
 "Innovation Nest": V, "Innovo": V, "Inovo": V, "Irregular Expression": V, "Irregular Expressions": V, "Kaya": V,
 "LDV Partners": V, "Legend Capital": V, "Wells Fargo": B, "Maverick Silicon": V, "Monashees": V, "Monolith Management": V, "Moonfire": V, "OATV": V,
 "Ora Global": V, "Palm Drive": V, "Parable": V, "Playground Global": V, "Protagonist": V, "Rebel": V,
 "Rebellion": V, "Red Swan": V, "Rheingau Founders": V, "SBI Group": V, "Senovo": V, "Seven Seven Six": V,
 "Sevin Rosen Funds": V, "Skycatcher": V, "Supernode Global": V, "Techammer": V, "Techstart": V, "TenOneTen": V,
 "West Coast Endeavors": V, "World Innovation Lab": V, "Zero Prime": V, "Zobito": V, "ZooCap": V, "Axeleo": V,
 "USIT": V, "Expa": A, "MiraclePlus": A, "Raise Sherpas": CF,
 # growth, crossover, PE, asset managers, endowments, pensions
 "Highland Europe": G, "ACOF": G, "Aspex": G, "Avenir": G, "BDT & MSD": G, "BNP Paribas": G, "Belfius": G,
 "Eastspring": G, "Flow Traders": G, "Hanwha Asset Management": G, "Harvard Management Company": G,
 "Healthcare of Ontario Pension Plan": G, "Lightrock": G, "Millennium New Horizons": G, "Point72": G,
 "Sixth Street Growth": G, "Sofina": G, "Special Situations Investing Group II": G, "Stripes Group": G,
 "XTX Markets": G, "Clayton, Dubilier & Rice": G, "Mitsubishi UFJ Financial Group": G, "Mizuho Financial Group": G,
 "Dai-ichi Life Insurance": G, "ARK Invest": G, "Agostinelli Group": "angel", "WTT Fubon Family": "angel",
 # state, sovereign, public
 "Industrifonden": P, "EDBI": P, "French Tech Souveraineté": P, "Grand Duchy of Luxembourg": P,
 "Greater Bay Area Homeland": P, "Inria Participations": P, "Noshaq": P, "SRIW": P, "Tesi": P,
 "Xiamen ITG Group": P,
 # government grants
 "CDTI": GG, "NGI Zero Core": GG, "NIST": GG, "Region Centre-Val de Loire": GG,
 "Scale AI (Canada's AI supercluster)": GG,
 # philanthropy
 "Breakout Labs": PH, "GiveWell": PH,
 # crypto
 "Distributed Global": CR, "BeakerDAO": CR, "Block1": CR, "Blockwall": CR, "Chorus One": CR, "Collab+Currency": CR,
 "Dialectic": CR, "Digital Currency Group": CR, "GSR Markets": CR, "L2IV": CR, "Matrixport": CR, "OrangeDAO": CR,
 "The LAO": CR, "Spartan": CR, "The Spartan Group": CR, "BAT token buyers": CR, "Sonar community buyers": CR,
 "CoinList participants": CR, "Alameda Research": CR,
 # corporate and strategic
 "China Telecom": C, "Fosun": C, "Huawei Hubble": C, "Hyundai Motor Group": C, "IDC Frontier": C, "Mondragon Group": C,
 "OpenAI": C, "Samsung Securities": C, "Schwarz Group": C, "Sompo Japan Nipponkoa Insurance": C, "Zalando": C,
 "Zhihu": C, "Airbus": C, "Aisan Technology": C, "Amdocs": C, "Amgen": C, "Ant Financial": C, "BlueFocus": C, "CATL": C,
 "Canva": C, "Cursor": C, "Danobatgroup": C, "Devolutions": C, "Docker": C, "DreamHost": C, "EBSCO": C, "EMC": C,
 "Electronic Arts": C, "Eni": C, "Ericsson": C, "Fastweb+Vodafone": C, "Figma": C, "Ford Motor Company": C,
 "Foxconn": C, "Framer": C, "General Electric": C, "GlobalFoundries": C, "Grafana Labs": C, "Hewlett-Packard": C,
 "Huaqin Technology": C, "IREN": C, "ITOCHU": C, "JCDecaux Holding": C, "Jaguar Land Rover": C, "KT": C, "MediaTek": C,
 "MiHoYo": C, "Mitsubishi Electric": C, "Monday.com": C, "Mouser Electronics": C, "NEC": C, "Nature Publishing Group": C,
 "Nebius": C, "Netlify": C, "Novell": C, "OWC": C, "PagsGroup": C, "Pegatron": C, "Prefect": C, "Quest Software": C,
 "Rainmatter": C, "Rheinmetall": C, "SentinelOne": C, "Shikoku Electric Power": C, "Silicon Graphics": C,
 "Sony Music Group": C, "Sprint": C, "Supercell": C, "Synopsys": C, "Teradata": C, "Tokio Marine Group": C,
 "UiPath": C, "Universal Music Group": C, "WPP": C, "Warner Music Group": C, "Williams Advanced Engineering": C,
 "Xiaohongshu": C, "Yahoo": C, "Yamaha Motor": C, "Yandex": C, "Zapier": C, "Zerodha": C, "Zhipu AI": C,
 "Zscaler": C, "Sandisk": C, "Sangfor Technologies": C, "SCB10X": C, "SAP.iO": C, "Singtel Innov8": C,
 "Cox Exponential": C, "Presidio STX": C, "Latacora": C, "For One Red Design Studio": C, "Stratos Technologies": C,
 "Stanford University": O, "University of Michigan": O, "AngelList": O,
})

T.update({"O'Reilly AlphaTech Ventures": V, "Amino Collective": V, "New York Angels": "angel", "Two Small Fish Ventures": V,
          "Silicon Catalyst Angels": "angel", "Portland Seed Fund": V, "Inspiration Ventures": V, "New North Ventures": V,
          "Foresight Williams Technology EIS Fund": V, "Downing Ventures": V, "Ananda Impact Ventures": V,
          "Stellar Ventures": V, "MHS Capital": V, "Siemens Venture Capital": C, "Rho Ventures": V, "Real Ventures": V,
          "Golden Ventures": V, "Two Bear Capital": V, "Big Pi Ventures": V, "Northpond Ventures": V, "Backed VC": V,
          "ZeePrime Capital": CR, "Pfizer Ventures": C, "Denali Growth Partners": G, "Taiwania Capital": V,
          "JME Venture Capital": V, "Clave Capital": V, "Bethnal Green Ventures": A, "Energy Impact Partners": V,
          "Bonfire Ventures": V, "Industry Ventures": V, "Green D Ventures": V, "Sinovation Ventures": V,
          "Capstone Capital": V, "Lingfeng Capital": V, "Stony Creek Capital": V, "Chengwei Capital": V, "Huami": C,
          "SK hynix": C, "Dimension Capital": V, "Thrive Capital": V, "Argon Ventures": V, "Lowercarbon Capital": V,
          "Julian Capital": V, "Future Labs Capital": V, "1517 Fund": V, "Angel Squad": "angel", "Infinite Capital": V,
          "Road Capital": V, "Curve Labs": CR, "Cavalry Ventures": V, "Fuel Capital": V, "Firestreak Partners": V,
          "Digitalis Ventures": V, "Vaal Partners": V, "Avego": V, "Sands Capital": G, "Draper VC": V,
          "European Space Agency": GG, "Innovate UK": GG, "National Science Foundation": GG,
          "National Science Foundation (SBIR)": GG, "U.S. Department of Energy (SBIR)": GG, "National Institutes of Health (NIBIB)": GG,
          "National Institute of Mental Health (SBIR)": GG, "National Institute on Aging (NIH SBIR)": GG, "NASA (SBIR)": GG,
          "U.S. Space Force (SBIR)": GG, "European Union": GG, "Federal Ministry for Economic Affairs and Energy (ZIM)": GG,
          "BAB - Die Foerderbank fuer Bremen und Bremerhaven": P, "Chan Zuckerberg Initiative": PH,
          "Alfred P. Sloan Foundation": PH, "Shuttleworth Foundation": PH, "Knight Foundation": PH,
          "Python Software Foundation": PH, "National Geographic": PH, "Nature Publishing Group": C,
          "Genesis crowdfunding backers": CF, "Librem 13/15 crowdfunding backers": CF, "Librem 5 crowdfunding backers": CF,
          "StartEngine backers": CF, "Kickstarter backers": CF, "Crowd Supply backers": CF, "Community investors": CF})

T.update({"Elad Gil": "angel", "AMD Ventures": C, "AMD": C, "FirstMark": V, "FirstMark Capital": V})

T.update({"PayPal Ventures": C, "Telstra Ventures": C, "Datadog Ventures": C, "Hitachi Ventures": C, "Next47": C,
          "Exor Ventures": C, "Maven 11 Capital": CR, "Innovation Endeavors": V, "Chemistry": V, "New Wave": V,
          "NLnet Foundation": GG, "Adage Capital Management": G, "Blockchain Capital": CR, "Bain Capital Crypto": CR})

T.update({
 "Meta": C, "Accenture": C, "Benchling": C, "China Mobile": C, "Compaq": C, "Contemporary Amperex Technology": C,
 "Geely": C, "GitLab": C, "Kia": C, "Kingsoft": C, "KPMG": C, "Netscape": C, "Nutanix": C, "Progress Software": C,
 "Sumitomo": C, "TAL Education Group": C, "The Attachmate Group": C, "Wipro": C, "Lattice": C, "Boss Zhipin": C,
 "ByteTrade Lab": C, "Coil": C, "Notion": C, "Kaiser Permanente": C, "Sonar": C, "Koch Disruptive Technologies": C,
 "Sonae IM": C, "FUTO": C, "Status": CR, "Strongblock": CR,
 "Jane Street": G, "PSG": G, "Premji Invest": G, "StepStone Group": G, "TPG": G, "Third Point": G, "AllianceBernstein": G,
 "BNY Mellon": G, "Neuberger Berman": G, "UBS": G, "Lehman Brothers": G, "RCM Private Markets": G,
 "Greenspring Associates": G, "Tiger Management": G, "Derayah Financial": G, "7RIDGE": G, "850 Management": G,
 "CPE Asset Management": G, "CPE Yuanfeng": G, "Duff, Ackerman & Goodrich": G, "Rochefort": G,
 "Marathon": V, "Pritzker Group": V, "Woodstock": V, "XAnge": V, "Movac": V, "Episode 1": V, "Bright Pixel": V,
 "10x Founders": V, "8vdx": V, "ARTIS": V, "Aleph": V, "Atlantic Bridge": V, "Black Nova Group": V, "Blast Club": V,
 "BuildGroup": V, "Deep Acre": V, "Disruptive Technology Advisers": V, "Four Rivers": V, "Innovation Engine": V,
 "K1W1": V, "Kerrest & Co": V, "Leonis Investissement": V, "MAKE": V, "MMC": V, "Nascent": V, "Percival": V,
 "Ramprate": V, "Redline": V, "Script": V, "Secure Octane": V, "Seven Seas": V, "Silicon 100": V, "Social Leverage": V,
 "SquareOne": V, "Stonks": V, "TruArrow": V, "Unbound": V, "Wealth Union": V, "WestSummit": V, "WestWave": V,
 "Zebra Good Pte": V, "Zillionize": V, "Accurafy4": V, "Antigravity": V, "Athos": V, "Id4": V, "Kadmos": V, "Noa": V,
 "SNR": V, "Vitamina K": V, "Zypsy": A, "5G Open Innovation Lab": A,
 "CDTI Innvierte": P, "Wallonie Entreprendre": P, "Zhangjiang Group": P,
 "Army Research Lab": GG, "Schmidt Futures": PH,
 "Duke University": O, "MIT": O, "Humboldt University of Berlin": O, "University of Oregon": O, "University of Oxford": O,
 "University of Wisconsin-Madison": O, "Warsaw University of Technology": O, "PTB": O, "QUEST/Uni Hannover": O,
})

# 2026-11-26, after Edison's review: the names still typed only by heuristic or left unclassified, typed from the
# round they appear in (data/deals.csv). Names we could not identify stay "other" rather than being guessed.
T.update({
 "Devonshire Investors": G, "American Express": B, "NatWest": B, "PayPal": B, "WR Hambrecht + Co": G,
 "Riverview Group": G, "Northern Trust": G,
 # Techaro (Anubis): corporate sponsors listed by Edison's audit; money given as sponsorship, not investment
 "Anexia": CO, "Databento": CO, "Gitea": CO, "Prolocation": CO, "Qwertiko": CO, "Raptor Computing Systems": CO,
 "Spur Intelligence": CO, "Synthient": CO, "Terminal Trove": CO, "Uberspace": CO, "Unipromos": CO, "Uvensys": CO,
 "Weblate": CO, "Wenet": CO, "Wildbase": CO, "canine.tools": CO, "embeDD": CO,
 "Endurance": CO, "Second Dinner": CO, "SGI": C, "UMAX": C, "Hyundai CRADLE": C, "Western Digital Capital": C,
 "Buildspace": A, "Pioneer": A, "FONGIT": A,
 "DFG": CR, "Bankless Ventures": CR,
 "DGF": V, "Jingfu Assets": V, "Juniper": V, "Rewired": V, "Start Garden": V, "Step Function": V, "Top Harvest": V,
 "Walden International": V, "Republic Capital": V, "Valor Capital Group": V, "Fidelity Ventures": V,
 "ICEX": GG, "Israel Innovation Authority": GG, "SBRI Healthcare": GG, "UAE AI and Robotics Award for Good": GG,
 "Vinnova": GG, "West of England Combined Authority": GG, "European Regional Development Fund": GG,
 "Business Development Bank of Canada": P, "National AI Industry Investment Fund": P,
 "Government of Canada (via Canada Development Investment Corporation)": P,
 "Office of Strategic Capital (US Department of War)": P,
 # not identified from the pages read
 "Asynch Media": O, "BGZ": O, "Breakers": O, "CCI Group": O, "ESOP": O, "Gandyr Group": O, "GravityRock": O,
 "Hanover": O, "IAG": O, "Latitude": O, "Mesh": O, "PTV": O, "Play Time": O, "Runway": O, "SCM Advisors": O,
 "SGPA": O, "Sequel": O, "TRGC": O, "Universe Software": O, "Victoria": O, "ZMT": O,
 "DCBuilder": "angel",  # pseudonymous crypto researcher (dcbuilder.eth), a person
})

# funders with two or more ventures that the name rules had typed as venture firms; each checked by hand
T.update({"Fathom Capital": V, "Rebel Fund": V, "The House Fund": V, "TLV Partners": V, "Grand Ventures": V, "Zeev Ventures": V, "Eniac Ventures": V, "GL Ventures": V, "Liquid 2 Ventures": V, "Wayfinder Ventures": V, "Webb Investment Network": V, "Zetta Venture Partners": V, "Highland Capital Partners": V, "Nauta Capital": V, "August Capital": V, "Cortical Ventures": V, "Cota Capital": V, "Engineering Capital": V, "First Spark Ventures": V, "Flybridge Capital Partners": V, "Qumra Capital": V, "Race Capital": V, "1984 Ventures": V, "Abstraction Capital": V, "Acequia Capital": V, "Angel Invest": V, "Anthos Capital": V, "Basecase Capital": V, "Bold Capital Partners": V, "DIG Ventures": V, "Day One Ventures": V, "Epic Ventures": V, "Exceptional Capital": V, "Future Capital": V, "GTMFund": V, "Glynn Capital": V, "Gravity Fund": V, "Hustle Fund": V, "Motier Ventures": V, "Outset Capital": V, "Radar Partners": V, "Rain Capital": V, "Ratio Ventures": V, "Rogue Capital": V, "S Ventures": V, "ScaleX Ventures": V, "Shunwei Capital": V, "Sound Ventures": V, "Tekedia Capital": V, "Triangle Peak Partners": V, "Trustbridge Partners": V, "European Commission": GG})

T.update({"SAGE Publishing": C, "O'Reilly Media": C, "Lux Capital (as named for DeepSeek)": V})  # PeerJ (pass h01)


def main():
    with open("data/investor_types.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["investor", "type", "group", "country", "notes"])
        for k, t in sorted(T.items(), key=lambda x: x[0].lower()):
            grp = {"GV": "Alphabet", "CapitalG": "Alphabet", "Gradient Ventures": "Alphabet", "Google": "Alphabet",
                   "M12": "Microsoft", "GitHub": "Microsoft", "Microsoft": "Microsoft", "Alibaba Cloud": "Alibaba",
                   "Alibaba": "Alibaba", "Ant Group": "Alibaba", "Samsung Electronics": "Samsung",
                   "Kima Ventures": "Xavier Niel", "Prosperity7 Ventures": "Saudi Aramco",
                   "Aramco Ventures (incl. Prosperity7)": "Saudi Aramco", "Aramco Ventures": "Saudi Aramco",
                   "Amazon": "Amazon", "NVIDIA (incl. NVentures)": "NVIDIA", "Intel Capital": "Intel",
                   "Salesforce Ventures": "Salesforce", "Samsung": "Samsung", "Tencent": "Tencent",
                   "Citi": "Citigroup", "Citi Ventures": "Citigroup", "Goldman Sachs": "Goldman Sachs",
                   "Dell Technologies Capital": "Dell", "VMware": "Dell",
                   "Hyundai CRADLE": "Hyundai", "Western Digital Capital": "Western Digital",
                   "O'Reilly Media": "O'Reilly", "O'Reilly AlphaTech Ventures": "O'Reilly"}.get(k, "")
            w.writerow([k, t, grp, "", ""])
    print(len(T), "types written")


if __name__ == "__main__":
    main()
