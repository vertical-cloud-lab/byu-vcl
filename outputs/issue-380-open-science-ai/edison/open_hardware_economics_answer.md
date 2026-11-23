# Edison job-futurehouse-paperqa3-high: open_hardware_economics

Task `0d82b186-f8e8-4e5a-98f7-271aeabfdaea` · status success

**Query.** What does the research literature show about the economics and commercialization of open-source hardware, especially scientific and laboratory hardware? Include studies on cost savings and return on investment of open-source scientific hardware (e.g., Joshua Pearce's work), business models and survival of open hardware companies (e.g., Arduino, Prusa Research, MakerBot, LulzBot/Aleph Objects, Adafruit, SparkFun, Opentrons), open hardware licensing (CERN OHL), OSHWA certification trends, and comparisons with open-source software commercialization. Give quantitative results where available.

---

Question: What does the research literature show about the economics and commercialization of open-source hardware, especially scientific and laboratory hardware? Include studies on cost savings and return on investment of open-source scientific hardware (e.g., Joshua Pearce's work), business models and survival of open hardware companies (e.g., Arduino, Prusa Research, MakerBot, LulzBot/Aleph Objects, Adafruit, SparkFun, Opentrons), open hardware licensing (CERN OHL), OSHWA certification trends, and comparisons with open-source software commercialization. Give quantitative results where available.

## Economics and Commercialization of Open-Source Hardware: A Literature Review

### 1. Cost Savings of Open-Source Scientific Hardware

A substantial body of work, led primarily by Joshua Pearce, has quantified the economic advantages of free and open-source hardware (FOSH) for scientific and laboratory applications. A comprehensive review of 119 open-source hardware articles from the HardwareX and PLOS Open Source Toolkit repositories found that FOSH provides **average savings of 87%** compared with functionally equivalent proprietary equipment (pearce2020economicsavingsfor pages 9-10, pearce2020economicsavingsfor pages 1-2). Savings varied by enabling technology: devices built with Arduino-based electronics averaged **89% savings**, those using RepRap-class 3-D printing averaged **92%**, and devices combining both technologies averaged **94%** (pearce2020economicsavingsfor pages 9-10, pearce2020economicsavingsfor pages 1-2). These figures compare direct material costs against commercial purchase prices and may understate total value because proprietary cost equivalents were available for only 37.8% of the reviewed devices—some open-source tools had no commercial counterpart (pearce2020economicsavingsfor pages 9-10).

Individual case studies show even more dramatic savings. An open-source spectrophotometer alternative costing $6 replaced a $1,113 commercial system (~99.5% savings), a multi-fluorescence imaging system costing $250 replaced $10,000 equipment (97.5%), and an open-source selective laser sintering system at $10,000 replaced a $400,000 proprietary system (97.5%) (pearce2020economicsavingsfor pages 7-9). An educational optics setup costing approximately $500 replaced $15,000 of commercial equipment, a 96.7% reduction that, if scaled nationally, could save more than $66 million across U.S. physics laboratories, more than $500 million across U.S. secondary schools, and over $1 billion globally (pearce2020economicsavingsfor pages 13-14).

The following table summarizes documented cost comparisons:

| Device category | Open-source cost | Proprietary cost | Percentage savings | Source |
|---|---:|---:|---:|---|
| Overall reviewed scientific hardware | Average below $1,500 | Average above $20,000 | **87% average** | Pearce (2020), 119 open-hardware articles; comparable prices available for 37.8% of devices (pearce2020economicsavingsfor pages 9-10, pearce2020economicsavingsfor pages 2-4) |
| Arduino-based scientific hardware | Varies by device | Functionally comparable equipment | **89% average** | Pearce (2020) (pearce2020economicsavingsfor pages 9-10, pearce2020economicsavingsfor pages 1-2) |
| 3D-printed scientific hardware | Varies by device | Functionally comparable equipment | **92% average** | Pearce (2020) (pearce2020economicsavingsfor pages 9-10, pearce2020economicsavingsfor pages 1-2) |
| Combined Arduino and 3D-printed hardware | Varies by device | Functionally comparable equipment | **94% average** | Pearce (2020) (pearce2020economicsavingsfor pages 9-10, pearce2020economicsavingsfor pages 1-2) |
| Open-source syringe pump—single | $97 materials; approximately $107 including stated assembly labor | $260–$1,509 | **Approximately 59%–93%** | Pearce (2015, 2016); absolute savings of $153–$1,402 per pump (pearce2016returnoninvestment pages 3-4, pearce2015quantifyingthevalue pages 5-6) |
| Open-source syringe pump—double | $154 materials; approximately $164 including stated assembly labor | $1,800–$2,606 | **Approximately 91%–94%** | Pearce (2015, 2016); absolute savings of $1,636–$2,442 per pump (pearce2016returnoninvestment pages 3-4, pearce2015quantifyingthevalue pages 5-6) |
| Educational optics setup | Approximately $500 | Approximately $15,000 | **96.7%** | Pearce (2020) (pearce2020economicsavingsfor pages 13-14) |
| Open-source spectrophotometer | $6 | $1,113 | **Approximately 99.5%** | Pearce (2020) (pearce2020economicsavingsfor pages 7-9) |
| Multi-fluorescence imaging system | $250 | $10,000 | **97.5%** | Pearce (2020) (pearce2020economicsavingsfor pages 7-9) |
| Probe positioner | Less than $5 | $100 | **More than 95%** | Pearce (2020) (pearce2020economicsavingsfor pages 10-12) |
| Selective laser-sintering system | $10,000 | $400,000 | **97.5%** | Pearce (2020) (pearce2020economicsavingsfor pages 7-9) |
| Programmable microfluidics system | Approximately $2,000 | More than $20,000 | **Approximately 90% or more** | Pearce (2020) (pearce2020economicsavingsfor pages 12-13) |


*Table: Documented comparisons show average savings of 87%–94% for major open-hardware technology groups, with several individual laboratory instruments approaching or exceeding 95%. These estimates generally compare direct material costs with commercial purchase prices and may omit fabrication labor.*

### 2. Return on Investment for Open-Source Scientific Hardware Development

Pearce (2016) demonstrated that publicly funded open-source hardware development can yield extraordinary returns on investment. Using an open-source syringe pump library as a case study, the development cost was estimated at approximately $30,000. Based on download statistics and estimated savings of $153–$1,402 for a single pump and $1,636–$2,442 for a double pump, the total value of the design library exceeded $168,000 within one month and reached more than $2.5 million within one year. This corresponded to calculated ROI values of **460% to more than 8,300%**. When the 52% national-average overhead typically charged to conventional equipment was included, the ROI increased to **750% to more than 12,000%** (pearce2016returnoninvestment pages 3-4). The study characterized these as conservative estimates because they excluded benefits from improved equipment, education, and scientific productivity.

Pearce (2026) further analyzed four financial models for open hardware development: (1) a philanthropy model where funders bear all design risks; (2) a standard investor model; (3) a crowd-sourced model; and (4) a novel "decoupled risk investor model" that separates design risk from ROI risk by introducing a guarantor. In a hypothetical case study, 100 proprietary bottle rollers costing $2,439 each ($243,925 total) could be replaced with open-source units at approximately $150 each after a $100,000 development investment, saving over $100,000 (pearce2026deriskingthefinance pages 3-7). The article argues that FOSH reduces costs generally by **more than 90%** for equivalent or lesser proprietary hardware while accelerating development through collaborative design (pearce2026deriskingthefinance pages 3-7).

### 3. Business Models and Commercial Viability of Open Hardware Companies

Research literature documents several viable business models for open-source hardware firms. These include: (1) kit and component sales, (2) specialty component manufacturing, (3) consulting and integration services, (4) trademark licensing, (5) subscription services, (6) education and training, (7) secondary supplier/complementary market strategies, and (8) validation and certification services (pearce2026deriskingthefinance pages 3-7, pearce2017emergingbusinessmodels pages 6-7). Li and Seering (2019) studied 31 open-source hardware firms over an average of 2.3 years and identified a four-phase growth pattern: starting the firm, identifying core competencies, business model improvement, and business maturation (li2019buildyourfirm pages 7-8, li2019buildyourfirm pages 8-9).

The following table summarizes financial and strategic data for prominent open hardware companies:

| Company | Founded / origin | Business model | Key financial or operating evidence | Open-source status / outcome |
|---|---|---|---|---|
| Arduino | 2005; began with €3,000 for 200 boards | Board sales, consulting/integration, education/community, and trademark licensing | Sales rose from 200 boards in 2005 to 5,000 in 2006, 30,000 in 2007, and more than 150,000 by Q1 2010. Trademark fees represented 10% of revenue in 2013. (thompson2011buildit.share pages 1-4, thompson2011buildit.share pages 4-6, li2019buildyourfirm pages 8-9, abbondandoloUnknownyeartheroleofa pages 5-7) | Designs remained open while the Arduino trademark protected quality and captured value; an archetype of commercialization through brand, expertise, and ecosystem rather than design exclusivity. |
| SparkFun | Circa 2003 | Sales of components, boards, kits, and third-party products; marketplace and manufacturing services; rapid product iteration | Revenue reportedly grew from $846,881 in 2005 to $4 million in 2007 and nearly $7 million in 2008. The supplied literature does not substantiate the proposed $75 million cumulative-sales figure. (cruz2017exploringtheopen pages 159-162, cruz2017exploringtheopena pages 159-162) | Remained committed to open hardware; competed with clones through trusted manufacturing, community support, branding, and releasing improved versions faster than imitators. (pearce2017emergingbusinessmodels pages 6-7, lock2013opensourcehardwarecan pages 86-89) |
| Adafruit Industries | 2005 | Kits, components, finished boards, tutorials, media, and education | MintyBoost sold about 8,000 units at approximately $20 each—roughly $160,000 in gross product sales. The supplied research evidence does not establish the proposed company-wide $50 million revenue estimate. (thompson2011buildit.share pages 4-6) | Sustained an open-source model in which documentation and customer participation improve products and provide community-based technical support. |
| MakerBot | 2009; emerged from RepRap | Desktop 3-D-printer sales, later moving toward proprietary printers, software, patented modules, and a razor-and-blades strategy | Acquired by Stratasys for $403 million in 2013. Following its proprietary turn, the literature reports declining sales, layoffs, outsourced manufacturing, retail closures, a class-action lawsuit, and only 1,421 printers sold in the cited period. (pearce2017emergingbusinessmodels pages 8-9, viseur20223dprinterbuilders’ pages 3-4) | Initially open, then substantially proprietary. Community backlash and subsequent decline make it a prominent—but not causally conclusive—warning about sacrificing ecosystem trust. |
| Aleph Objects / LulzBot | RepRap-derived open-source 3-D printers | Printer, component, and support sales combined with domestic printer-farm manufacturing | Reported $5.8 million revenue in Q2 2016, four consecutive profitable quarters, 83% year-over-year growth, 2,782% three-year growth, 146 employees, and rank 122 on the 2016 *Inc. 500*. The supplied literature does not document the proposed 2019 bankruptcy claim. (pearce2017emergingbusinessmodels pages 8-9) | Continued an open-source strategy during the documented high-growth period, contrasting with MakerBot’s proprietary pivot. |
| Prusa Research | Founded in Prague in 2012 from the RepRap movement | Kits and assembled printers, filament and resin, spare parts, upgrades, software, support, and printer-farm services | In 2024, five operating companies reported about CZK 6.6 billion in combined revenue before intragroup eliminations; the group processed about 300,000 orders and employed more than 1,000 people. Prusa Manufacturing revenue rose from CZK 1.687 billion to CZK 2.116 billion in 2024. (guhathakurta2026prusa3dsopensourcemanufacturing pages 1-4, guhathakurta2026prusa3dsopensourcemanufacturing pages 9-12) | Historically strongly open, but now layered or partially open: software, firmware, schematics, and printed parts vary in openness, while some manufacturing data and bills of materials are withheld and newer licensing restricts commercial resale. (guhathakurta2026prusa3dsopensourcemanufacturing pages 4-7, viseur20223dprinterbuilders’ pages 4-5) |
| Opentrons | Laboratory-automation venture built around open liquid-handling robots | Sales of assembled robots and related laboratory-automation products, with support and ecosystem services | The reviewed literature identifies Opentrons as an open-hardware vendor but supplies no independently verified revenue, valuation, funding, profitability, or survival figures. (pearce2026deriskingthefinance pages 3-7) | Illustrates commercialization of scientific open hardware through professionally manufactured, supported laboratory instruments rather than requiring laboratories to self-build. |


*Table: Comparison of prominent open-hardware firms, their value-capture models, reported scale, and trajectories. It distinguishes quantitative evidence in the reviewed literature from financial claims that the available sources do not substantiate.*

**Arduino** is the archetypal open hardware success. Founded in 2005 with an initial investment of €3,000, it grew from 200 boards to over 150,000 by Q1 2010 (thompson2011buildit.share pages 1-4, abbondandoloUnknownyeartheroleofa pages 5-7). Arduino's designs are released under Creative Commons Attribution-ShareAlike licensing, while the Arduino trademark is protected to maintain brand quality and generate licensing revenue. By 2013, trademark fees constituted approximately 10% of total revenue (li2019buildyourfirm pages 8-9). The founders' primary income derived from consulting for clients developing Arduino-based products, while the growing community contributed free improvements and technical support (thompson2011buildit.share pages 1-4, thompson2011buildit.share pages 4-6).

**SparkFun Electronics** grew from $846,881 in revenue in 2005 to $4 million in 2007 and nearly $7 million in 2008 (cruz2017exploringtheopen pages 159-162, cruz2017exploringtheopena pages 159-162). SparkFun's CEO argued that companies relying too heavily on intellectual property become "intellectually unfit" and that continuous innovation outpaces cloners—by the time competitors clone a board and list it on eBay, SparkFun already has the next version in the pipeline (pearce2017emergingbusinessmodels pages 6-7).

**MakerBot vs. Aleph Objects/LulzBot** provides a natural experiment in open vs. closed strategies. MakerBot was acquired by Stratasys in 2013 for **$403 million** but subsequently abandoned its open-source model, provoking community backlash, boycotts, and reverse-engineering efforts (pearce2017emergingbusinessmodels pages 8-9, viseur20223dprinterbuilders’ pages 3-4). Its proprietary "Smart Extruder" led to a class-action lawsuit, and the company experienced sharply declining sales, layoffs, outsourced manufacturing, and retail closures, selling only 1,421 printers during the cited period (pearce2017emergingbusinessmodels pages 8-9). By contrast, **Aleph Objects** (LulzBot), which maintained its open-source model, reported **$5.8 million in Q2 2016 revenue**, four consecutive profitable quarters, 83% year-over-year revenue growth, **2,782% three-year revenue growth**, and ranked **#122 on the 2016 Inc. 500** with 146 employees (pearce2017emergingbusinessmodels pages 8-9).

**Prusa Research**, founded in Prague in 2012 from the RepRap movement, grew into a substantial enterprise. By 2024, five operating companies reported combined revenue of approximately **CZK 6.6 billion** (roughly USD $280 million) before intra-group eliminations, the group processed about 300,000 orders per year, and employed more than 1,000 people (guhathakurta2026prusa3dsopensourcemanufacturing pages 1-4). Prusa Manufacturing's revenue rose from CZK 1.687 billion to CZK 2.116 billion in 2024, with operating profit increasing from CZK 9.5 million to CZK 66.3 million (guhathakurta2026prusa3dsopensourcemanufacturing pages 9-12). However, Prusa's openness has become increasingly layered: while software, firmware, and printed-part files are published, some manufacturing data and bills of materials are withheld, and its newer Open Community License restricts commercial resale (guhathakurta2026prusa3dsopensourcemanufacturing pages 4-7, viseur20223dprinterbuilders’ pages 4-5).

**Opentrons** is identified in the literature as a commercial vendor of open-source liquid-handling robots serving laboratory automation, representing the science-specific segment of the market (pearce2026deriskingthefinance pages 3-7), though detailed financial data were not available in the reviewed academic sources.

### 4. Open Hardware Licensing: The CERN OHL

The **CERN Open Hardware Licence (CERN OHL)** was published in 2011 and was drafted collaboratively by CERN engineer Javier Serrano and legal expert Myriam Ayass. It was built upon the earlier Tucson Amateur Packet Radio (TAPR) Open Hardware License, which was designed primarily for digital telecommunication devices (murillo2018assemblingopenhardware pages 4-8, bonvoisin2020standardisationofpractices pages 1-3). As the concept of "open hardware" expanded beyond electronics to include mechanics, textiles, and other technologies, broader licenses including the CERN OHL and SolderPad License emerged (bonvoisin2020standardisationofpractices pages 1-3).

The CERN OHL was designed to give licensees rights to study, extend, and commercially use digital designs while imposing conditions on derivative works (murillo2018assemblingopenhardware pages 4-8). The license now provides **three sharing variants**: strongly reciprocal (CERN-OHL-S, requiring derivative works to be shared under the same terms), weakly reciprocal (CERN-OHL-W), and permissive (CERN-OHL-P) (miljkovic2109towardsfairprinciples pages 3-6, monton2020onlicensesfor pages 3-4). Many prominent open hardware projects, including Arduino, have continued using Creative Commons Attribution-ShareAlike licenses that predate the establishment of dedicated open-hardware licenses (miljkovic2109towardsfairprinciples pages 3-6).

### 5. OSHWA Certification Trends

The **Open Source Hardware Association (OSHWA)** provides a certification program and maintains a registry of certified open hardware projects, assigning unique identifiers to certified designs. OSHWA certification experienced rapid growth: **977 certified projects** were registered as of August 24, 2020, increasing to **1,601 by July 19, 2021**—a **64% increase** in approximately one year (miljkovic2109towardsfairprinciples pages 1-3). Certification requires separate licenses for a project's design, software, and documentation (miljkovic2109towardsfairprinciples pages 3-6). The OSHWA certification has become an important tool for combating misuse of the "open source" label by companies that do not genuinely release open designs (pearce2017emergingbusinessmodels pages 6-7).

### 6. Comparison with Open-Source Software Commercialization

Open-source hardware and software commercialization share fundamental principles—community-driven development, collaborative innovation, and service-based revenue models—but differ materially due to the physicality of hardware (ferreira2010typesofmarket pages 69-76, lock2013opensourcehardwarecan pages 25-28). The parallels are most apparent in service models: just as Red Hat grew to a **$1.79 billion/year** company by providing services on top of free and open-source software (pearce2017emergingbusinessmodels pages 6-7), open hardware firms can sell consulting, training, subscriptions, and support (parker2021thepotentialfor pages 13-16, mies2024potentialandchallenges pages 88-90).

Key differences include:

- **Manufacturing costs**: Software has near-zero marginal cost of distribution, while hardware requires physical production, inventory, storage, and distribution (lock2013opensourcehardwarecan pages 25-28, lock2013opensourcehardwarecan pages 13-19).
- **Licensing limitations**: Copyright provides strong enforcement for software, while many hardware elements are not copyrightable, leaving open-hardware licenses closer to permissive academic licenses. Patent-based reciprocity is possible but costly (lock2013opensourcehardwarecan pages 25-28, lock2013opensourcehardwarecan pages 86-89).
- **Regulatory compliance**: Commercial hardware must meet EMC, RoHS, CE, and FCC regulations, imposing compliance costs absent from most software (lock2013opensourcehardwarecan pages 25-28).
- **Tool heterogeneity**: Hardware development requires expensive, specialized CAD tools, making collaboration harder than with text-based software source code (lock2013opensourcehardwarecan pages 25-28).
- **Interdependence**: 86% of open-source hardware market offers were enabled by projects that depended on open-source software, and 96% of surveyed OSH companies had at least one offer enabled by projects using highly restrictive licenses (ferreira2010typesofmarket pages 69-76).

A survey of open hardware market offers found that hardware-specific revenue categories—finished products, tools, parts, and kits—have no direct open-source software equivalents, while both sectors share revenue from documentation, support, training, and licensing (ferreira2010typesofmarket pages 69-76). The principal OSH-specific advantage is that intellectual-property cost constitutes a lower proportion of total product cost compared to software, since manufacturing contributes substantially to expenses, reducing the relative impact of open-sourcing the design (ferreira2010typesofmarket pages 69-76).

### 7. Broader Market Context and Future Directions

The open-source hardware market collectively reached tens of millions of dollars in revenue by 2010, when roughly a dozen startups together made approximately $50 million (cruz2017exploringtheopen pages 27-30). Li and Seering (2019) found through interviews with 37 open-source hardware company leaders and 12 community members that community building is a key element of firm success—it increases customer-perceived value, decreases product development and sales costs, shortens go-to-market time, and incubates startups with knowledge and resources (li2019buildyourfirm pages 7-8). These advantages can compensate for the risks associated with open-source strategies, making open design a viable product development approach for hardware startups.

However, significant challenges remain. The lack of strong IP protection means cloning is a persistent threat, as demonstrated by MakerBot's experience and the broader pattern of Chinese manufacturers replicating open designs at lower cost (viseur20223dprinterbuilders’ pages 3-4). Some firms, including Prusa Research, have responded by adopting layered openness—publishing some elements while withholding manufacturing data and imposing restrictions on commercial use (guhathakurta2026prusa3dsopensourcemanufacturing pages 4-7). Open hardware funding also remains challenging; most scientific hardware development funding follows proprietary models, creating a gap between scientists' ability to purchase expensive proprietary equipment and their inability to finance lower-cost open alternatives (pearce2026deriskingthefinance pages 3-7).

In summary, the research literature demonstrates that open-source scientific hardware can deliver cost savings of 87–94% on average, generate ROI of hundreds to thousands of percent for public funders, and support profitable commercial enterprises ranging from small component sellers to companies with over 1,000 employees and hundreds of millions of dollars in revenue. The field continues to mature through evolving licensing frameworks (CERN OHL), growing certification programs (OSHWA), and business models that adapt open-source software commercialization strategies to the unique challenges of physical products.

References

1. (pearce2020economicsavingsfor pages 9-10): Joshua M. Pearce. Economic savings for scientific free and open source technology: a review. HardwareX, 8:e00139, Oct 2020. URL: https://doi.org/10.1016/j.ohx.2020.e00139, doi:10.1016/j.ohx.2020.e00139. This article has 198 citations and is from a peer-reviewed journal.

2. (pearce2020economicsavingsfor pages 1-2): Joshua M. Pearce. Economic savings for scientific free and open source technology: a review. HardwareX, 8:e00139, Oct 2020. URL: https://doi.org/10.1016/j.ohx.2020.e00139, doi:10.1016/j.ohx.2020.e00139. This article has 198 citations and is from a peer-reviewed journal.

3. (pearce2020economicsavingsfor pages 7-9): Joshua M. Pearce. Economic savings for scientific free and open source technology: a review. HardwareX, 8:e00139, Oct 2020. URL: https://doi.org/10.1016/j.ohx.2020.e00139, doi:10.1016/j.ohx.2020.e00139. This article has 198 citations and is from a peer-reviewed journal.

4. (pearce2020economicsavingsfor pages 13-14): Joshua M. Pearce. Economic savings for scientific free and open source technology: a review. HardwareX, 8:e00139, Oct 2020. URL: https://doi.org/10.1016/j.ohx.2020.e00139, doi:10.1016/j.ohx.2020.e00139. This article has 198 citations and is from a peer-reviewed journal.

5. (pearce2020economicsavingsfor pages 2-4): Joshua M. Pearce. Economic savings for scientific free and open source technology: a review. HardwareX, 8:e00139, Oct 2020. URL: https://doi.org/10.1016/j.ohx.2020.e00139, doi:10.1016/j.ohx.2020.e00139. This article has 198 citations and is from a peer-reviewed journal.

6. (pearce2016returnoninvestment pages 3-4): Joshua M. Pearce. Return on investment for open source scientific hardware development. Science and Public Policy, 43:192-195, Apr 2016. URL: https://doi.org/10.1093/scipol/scv034, doi:10.1093/scipol/scv034. This article has 186 citations and is from a domain leading peer-reviewed journal.

7. (pearce2015quantifyingthevalue pages 5-6): Joshua M. Pearce. Quantifying the value of open source hard-ware development. Modern Economy, 06:1-11, Jan 2015. URL: https://doi.org/10.4236/me.2015.61001, doi:10.4236/me.2015.61001. This article has 155 citations.

8. (pearce2020economicsavingsfor pages 10-12): Joshua M. Pearce. Economic savings for scientific free and open source technology: a review. HardwareX, 8:e00139, Oct 2020. URL: https://doi.org/10.1016/j.ohx.2020.e00139, doi:10.1016/j.ohx.2020.e00139. This article has 198 citations and is from a peer-reviewed journal.

9. (pearce2020economicsavingsfor pages 12-13): Joshua M. Pearce. Economic savings for scientific free and open source technology: a review. HardwareX, 8:e00139, Oct 2020. URL: https://doi.org/10.1016/j.ohx.2020.e00139, doi:10.1016/j.ohx.2020.e00139. This article has 198 citations and is from a peer-reviewed journal.

10. (pearce2026deriskingthefinance pages 3-7): Joshua M. Pearce. Derisking the finance of open source hardware development. Journal of Open Hardware, Feb 2026. URL: https://doi.org/10.5206/joh.v10i1.24454, doi:10.5206/joh.v10i1.24454. This article has 0 citations.

11. (pearce2017emergingbusinessmodels pages 6-7): Joshua M. Pearce. Emerging business models for open source hardware. ArXiv, Mar 2017. URL: https://doi.org/10.5334/joh.4, doi:10.5334/joh.4. This article has 160 citations.

12. (li2019buildyourfirm pages 7-8): Zhuoxuan Li and Warren Seering. Build your firm with strangers?: longitudinal studies on open source hardware firm growth. Volume 7: 31st International Conference on Design Theory and Methodology, Aug 2019. URL: https://doi.org/10.1115/detc2019-97618, doi:10.1115/detc2019-97618. This article has 6 citations.

13. (li2019buildyourfirm pages 8-9): Zhuoxuan Li and Warren Seering. Build your firm with strangers?: longitudinal studies on open source hardware firm growth. Volume 7: 31st International Conference on Design Theory and Methodology, Aug 2019. URL: https://doi.org/10.1115/detc2019-97618, doi:10.1115/detc2019-97618. This article has 6 citations.

14. (thompson2011buildit.share pages 1-4): C Thompson. Build it. share it. profit. can open source hardware work. Unknown journal, 2011.

15. (thompson2011buildit.share pages 4-6): C Thompson. Build it. share it. profit. can open source hardware work. Unknown journal, 2011.

16. (abbondandoloUnknownyeartheroleofa pages 5-7): RG Abbondandolo. The role of open source hardware in harnessing user entrepreneurship in developing countries. Unknown journal, Unknown year.

17. (cruz2017exploringtheopen pages 159-162): A Marroquin Cruz. Exploring the open source hardware phenomenon: empirical essays on the role of user communities in the creation of innovation, organizations and markets. Unknown journal, 2017.

18. (cruz2017exploringtheopena pages 159-162): A Marroquin Cruz. Exploring the open source hardware phenomenon: empirical essays on the role of user communities in the creation of innovation, organizations and markets. Unknown journal, 2017.

19. (lock2013opensourcehardwarecan pages 86-89): J Lock. Open source hardware-can embedded electronics companies thrive through the use and/or development of open source hardware? Unknown journal, 2013.

20. (pearce2017emergingbusinessmodels pages 8-9): Joshua M. Pearce. Emerging business models for open source hardware. ArXiv, Mar 2017. URL: https://doi.org/10.5334/joh.4, doi:10.5334/joh.4. This article has 160 citations.

21. (viseur20223dprinterbuilders’ pages 3-4): Robert Viseur and Nicolas Jullien. 3d printer builders’ open-hardware strategies. Proceedings of the 18th International Symposium on Open Collaboration, pages 1-8, Sep 2022. URL: https://doi.org/10.1145/3555051.3555069, doi:10.1145/3555051.3555069. This article has 2 citations.

22. (guhathakurta2026prusa3dsopensourcemanufacturing pages 1-4): R Guhathakurta and R Nag. Prusa3d's open-source manufacturing and rapid prototyping: scaling community-driven innovation in a cost-competitive global market. Unknown journal, 2026.

23. (guhathakurta2026prusa3dsopensourcemanufacturing pages 9-12): R Guhathakurta and R Nag. Prusa3d's open-source manufacturing and rapid prototyping: scaling community-driven innovation in a cost-competitive global market. Unknown journal, 2026.

24. (guhathakurta2026prusa3dsopensourcemanufacturing pages 4-7): R Guhathakurta and R Nag. Prusa3d's open-source manufacturing and rapid prototyping: scaling community-driven innovation in a cost-competitive global market. Unknown journal, 2026.

25. (viseur20223dprinterbuilders’ pages 4-5): Robert Viseur and Nicolas Jullien. 3d printer builders’ open-hardware strategies. Proceedings of the 18th International Symposium on Open Collaboration, pages 1-8, Sep 2022. URL: https://doi.org/10.1145/3555051.3555069, doi:10.1145/3555051.3555069. This article has 2 citations.

26. (murillo2018assemblingopenhardware pages 4-8): Luis Felipe R. Murillo. Assembling open hardware at cern. ArXiv, Jul 2018. URL: https://doi.org/10.31235/osf.io/tqwef, doi:10.31235/osf.io/tqwef. This article has 6 citations.

27. (bonvoisin2020standardisationofpractices pages 1-3): Jérémy Bonvoisin, Jenny Molloy, Martin Haeuer, and Tobias Wenzel. Standardisation of practices in open source hardware. Text, Jan 2020. URL: https://doi.org/10.48550/arxiv.2004.07143, doi:10.48550/arxiv.2004.07143. This article has 61 citations and is from a peer-reviewed journal.

28. (miljkovic2109towardsfairprinciples pages 3-6): Nadica Miljković, Ana Trisovic, and Limor Peer. Towards fair principles for open hardware. Text, Jan 2021. URL: https://doi.org/10.48550/arxiv.2109.06045, doi:10.48550/arxiv.2109.06045. This article has 7 citations and is from a peer-reviewed journal.

29. (monton2020onlicensesfor pages 3-4): Marius Monton and Xavier Salazar. On licenses for [open] hardware. In 2020 XXXV Conference on Design of Circuits and Integrated Systems (DCIS), 1-6. IEEE, Nov 2020. URL: https://doi.org/10.1109/dcis51330.2020.9268619, doi:10.1109/dcis51330.2020.9268619. This article has 4 citations.

30. (miljkovic2109towardsfairprinciples pages 1-3): Nadica Miljković, Ana Trisovic, and Limor Peer. Towards fair principles for open hardware. Text, Jan 2021. URL: https://doi.org/10.48550/arxiv.2109.06045, doi:10.48550/arxiv.2109.06045. This article has 7 citations and is from a peer-reviewed journal.

31. (ferreira2010typesofmarket pages 69-76): Edy Ferreira. Types of market offers enabled by open source hardware. ArXiv, 2010. URL: https://doi.org/10.22215/etd/2010-08862, doi:10.22215/etd/2010-08862. This article has 1 citations.

32. (lock2013opensourcehardwarecan pages 25-28): J Lock. Open source hardware-can embedded electronics companies thrive through the use and/or development of open source hardware? Unknown journal, 2013.

33. (parker2021thepotentialfor pages 13-16): A Parker and J Spaulding. The potential for low-cost and open source hardware solutions to scale. Unknown journal, 2021.

34. (mies2024potentialandchallenges pages 88-90): Robert Mies. Potential and challenges of open source hardware development. Text, Jan 2024. URL: https://doi.org/10.14279/depositonce-22385, doi:10.14279/depositonce-22385. This article has 0 citations and is from a peer-reviewed journal.

35. (lock2013opensourcehardwarecan pages 13-19): J Lock. Open source hardware-can embedded electronics companies thrive through the use and/or development of open source hardware? Unknown journal, 2013.

36. (cruz2017exploringtheopen pages 27-30): A Marroquin Cruz. Exploring the open source hardware phenomenon: empirical essays on the role of user communities in the creation of innovation, organizations and markets. Unknown journal, 2017.
