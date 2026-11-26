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
 "Shine Capital": V, "Sierra Ventures": V, "Slow Ventures": V, "Susa Ventures": V, "Translink Capital": V, "Uncork Capital": V,
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
 "Alibaba Cloud": C, "Tencent": C, "SAP Ventures": C, "Amazon": C, "Dell Technologies Capital": C, "AMD": C,
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


def main():
    with open("data/investor_types.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["investor", "type", "group", "country", "notes"])
        for k, t in sorted(T.items(), key=lambda x: x[0].lower()):
            grp = {"GV": "Alphabet", "CapitalG": "Alphabet", "Gradient Ventures": "Alphabet", "Google": "Alphabet",
                   "M12": "Microsoft", "GitHub": "Microsoft", "Microsoft": "Microsoft", "Alibaba Cloud": "Alibaba",
                   "Alibaba": "Alibaba", "Ant Group": "Alibaba", "SAP Ventures": "SAP", "Samsung Electronics": "Samsung",
                   "Kima Ventures": "Xavier Niel", "Prosperity7 Ventures": "Saudi Aramco",
                   "Aramco Ventures (incl. Prosperity7)": "Saudi Aramco", "Aramco Ventures": "Saudi Aramco",
                   "Amazon": "Amazon", "NVIDIA (incl. NVentures)": "NVIDIA", "Intel Capital": "Intel",
                   "Salesforce Ventures": "Salesforce", "Samsung": "Samsung", "Tencent": "Tencent",
                   "Citi": "Citigroup", "Citi Ventures": "Citigroup", "Goldman Sachs": "Goldman Sachs",
                   "Dell Technologies Capital": "Dell", "VMware": "Dell"}.get(k, "")
            w.writerow([k, t, grp, "", ""])
    print(len(T), "types written")


if __name__ == "__main__":
    main()
