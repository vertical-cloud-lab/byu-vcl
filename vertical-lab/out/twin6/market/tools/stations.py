"""Station keys of the twin (twin/econ.py at 4bb91b1), what each buys new, and which listings fit its role.

For each key: the twin's item and price, and three patterns over a listing's title (and model line):
``exact`` the twin's own model, ``family`` the same maker's line (other generations or sizes that do the same job),
``sub`` another maker's instrument that does the same job at the station. ``excl`` drops parts, accessories,
consumables and other things that only share a word. A listing that matches none is not kept.
``wt`` is the shipping class used for the freight and rigging estimate (freight.py).
"""
import re

S = {}


def st(key, name, qty, new_usd, labs, wt, exact, family="", sub="", excl="", note="", comp=None):
    S[key] = dict(key=key, name=name, qty=qty, new_usd=new_usd, labs=labs, wt=wt,
                  exact=re.compile(exact, re.I) if exact else None,
                  family=re.compile(family, re.I) if family else None,
                  sub=re.compile(sub, re.I) if sub else None,
                  excl=re.compile(excl, re.I) if excl else None, note=note, comp=comp)


PARTS = (r"\b(parts? only|for parts|spare parts?|part no\b|p/n\b|pcb|board\b|circuit|cable|cord|manual\b|manuals\b|"
         r"brochure|catalog|software only|license only|dongle|filter\b|filters\b|o-?rings?|gaskets?|seal kit|"
         r"knob|fuse|fan\b|bulb|lamp\b|bracket|cover only|panel only|power supply\b|psu\b|adapter|adaptor|"
         r"replacement|repair kit|kit for|consumables?|toner|wire spool|spools?|stubs?\b|sample holder|"
         r"holder\b|grips? only|jaw faces|chuck jaws?|collets?\b|insert\b|inserts\b|tooling only|"
         r"lot of (?!\d+ ?(?:sem|edm))|assorted|miscellaneous|misc\.?\b)")

# ---------------------------------------------------------------------------------------------- tray instruments
st("sem", "Hitachi TM4000PlusII benchtop SEM", 1, 100_000, "vertical", "bench_sens",
   r"\bTM\s?-?4000\s?plus\s?(ii|2)\b|\bTM\s?-?4000\s?(ii|2)\b",
   r"\bTM\s?-?(4000|3030|3000|1000)\b|hitachi.*(table\s?top|bench\s?top|desktop).*(sem|electron)",
   r"phenom.*(sem|electron|microscope|pro\s?x?\b|\bxl\b|pure|\bg[1-6]\b|desktop)|(sem|electron).*phenom|neoscope|\bJCM-?\d{4}|coxem|\bEM-30|\bSNE-?\d{4}|(table\s?top|bench\s?top|desktop|compact)\s+(sem|scanning electron)",
   PARTS + r"|\bstub|carbon tape|sputter|coater|\btem\b|transmission electron|filament|cathode|turbo|"
           r"detector only|bse detector|stage only|chiller only|\bpump\b(?!.*(sem|microscope))|catheter|medtronic|"
           r"boston scientific|stent|guidewire|sheath|semiconductor wafer",
   note="tray instrument: only benchtop SEMs fit the tray; full-size SEMs are kept as 'floor' substitutes")
st("sem_floor", "full-size SEM (does not fit a tray; a substitute for the SEM role, and the host EBSD needs)", 0, 0,
   "vertical", "floor_sens",
   r"$^", r"$^",
   r"\b(JSM|JIB)-?\s?\d{3,4}|\bIT\s?(100|200|300|500|700|800)\b.*jeol|jeol.*\b(sem|scanning electron)|"
   r"\b(EVO|Sigma|Merlin|Ultra|Supra|Auriga|Gemini)\b.*(zeiss|sem)|zeiss.*(sem|scanning electron)|"
   r"\b(Quanta|Inspect|Nova|Helios|Apreo|Prisma|Scios|Versa|Teneo|XL ?30|Sirion)\b|"
   r"\b(Vega|Mira|Lyra|Maia|Clara|Amber)\b.*tescan|tescan|\bS-?(3400|3500|3700|4300|4700|4800|5500|8000|8200)N?\b|"
   r"\bSU-?\d{4}\b|hitachi.*scanning electron|scanning electron microscope|\bsem\b",
   PARTS + r"|\bstub|carbon tape|sputter|coater|\btem\b|transmission electron|filament|cathode|turbo|"
           r"detector only|stage only|chiller only|phenom|table\s?top|bench\s?top|desktop|\bTM\s?-?\d{4}",
   note="kept for the SEM role in a conventional lab and as EBSD's host; excluded from the tray SEM's statistics")
st("eds", "Oxford Instruments AZtecOne EDS for the TM4000", 1, 55_000, "vertical", "bench_sens",
   r"aztec\s?one",
   r"oxford.*\b(eds|edx|x-?max|ultim|x-?act|inca|swift|aztec)\b|\b(x-?max|ultim max|x-?act)\b",
   r"\b(eds|edx|edax|xflash|quantax|octane|apollo|element eds|ultradry|noran|pathfinder|bruker eds)\b",
   PARTS + r"|\bxrf\b|x-ray fluorescence|handheld|\bvanta\b|\bniton\b",
   note="EDS is often sold mounted on a used SEM; such bundles are listed under the SEM")
st("ebsd", "EBSD detector on the SEM", 1, 120_000, "vertical", "bench_sens",
   r"symmetry",
   r"oxford.*(ebsd|nordlys|c-?nano|c-?swift)|nordlys|c-?nano",
   r"\bebsd\b|hikari|velocity.*edax|digiview|e-?flash|electron backscatter diffraction|\btsl\b",
   PARTS, note="an EBSD detector needs a full-size SEM with a 70 degree tilt, not a benchtop SEM")
st("xrd", "Rigaku MiniFlex 600-C benchtop XRD with prep station", 1, 105_000, "vertical", "bench_sens",
   r"miniflex\s?-?600|miniflex\s?6g",
   r"miniflex|rigaku.*(bench|desktop|compact).*(xrd|diffract)",
   r"\bd2 phaser\b|\baeris\b|\bAXRD\b|equinox\s?(100|1000)|(bench\s?top|benchtop|desktop|compact)\s+(xrd|x-?ray diffract)|"
   r"\bxrd\b|x-?ray diffract|diffractometer|\bD8\b|\bD5000\b|x'?pert|empyrean|smartlab|ultima\s?(iv|iii|\+)|"
   r"\bXRD-?\d{4}\b|\bARL X'?TRA\b|bruker.*advance",
   PARTS + r"|x-?ray tube only|\btube\b(?!.*(diffract|xrd))|goniometer only|detector only|single crystal|"
           r"x-?ray (inspection|imaging|cabinet|film|source|generator)|radiograph|dental|veterinary|baggage|faxitron",
   note="tray instrument: benchtop units fit the tray; floor diffractometers are kept as 'floor' substitutes")
st("xrf", "Bruker S2 PUMA Series 2 EDXRF with XY autochanger", 1, 120_000, "vertical", "bench_sens",
   r"s2\s?puma",
   r"bruker.*(s2|s8|ranger|tiger|xrf)|s2\s?ranger|s8\s?tiger",
   r"\bNEX\s?(CG|DE|QC|DE VS)\b|epsilon\s?[1345]|\bminipal\b|quant'?x|\bEDX-?\s?(7000|8000|720|800|900|8100|7200)|"
   r"\bEA-?1000|x-?supreme|xepos|midex|spectro.*xrf|\b(edxrf|wdxrf|xrf spectrometer|x-?ray fluorescence)\b|"
   r"\bAxios\b|\bZSX\b|supermini|\bxrf\b",
   PARTS + r"|handheld|hand-?held|\bvanta\b|\bdelta\b|\bniton\b|\bxl[23t]\b|s1 titan|\btitan\b|tracer|sci-?aps|"
           r"\bx-?met\b|olympus innov|analyzer gun|portable|coating thickness|fischerscope|xdal|xdv|thick800",
   note="handheld analysers are left out: they don't do the station's job (lab EDXRF with an autochanger)")
st("mastersizer", "Malvern Mastersizer 3000 with Aero S", 1, 110_000, "vertical", "bench_sens",
   r"mastersizer\s?3000",
   r"mastersizer|malvern.*(laser diffraction|particle size)",
   r"\bLA-?(9[0-9]0|300|350|920)\b|horiba.*(laser|particle size)|\bLS\s?13\s?320|\bLS\s?230|beckman.*particle size|"
   r"microtrac|\bS3500\b|sympatec|\bHELOS\b|cilas|\bSALD-?\d{3,4}|analysette\s?22|"
   r"(laser diffraction|laser particle size|particle size analy[sz]er)",
   PARTS + r"|zetasizer|\bzeta\b|nanosight|morphologi|dls\b|dynamic light|sieve|camsizer|coulter counter|"
           r"multisizer|accusizer|particle counter|hiac|liquid particle|air particle|aerosol|met one|climet|lasair",
   note="the Aero S (dry dispersion) is the part that matters for powder; a wet-only unit needs one added")
st("hardness", "Mitutoyo HM-220 micro-Vickers with AVPAK", 1, 70_000, "vertical", "bench",
   r"\bHM-?220\b",
   r"\bHM-?(2\d\d|1\d\d)\b|mitutoyo.*(micro\s?-?vickers|micro\s?hardness|hardness)",
   r"micro\s?-?vickers|micro\s?-?hardness|\btukon\b|\bVH\s?(1102|1202|3100|3300)\b|\bLM\s?-?(100|110|247|248|300|310|700|800)(at)?\b|"
   r"\bAMH\s?-?\d+|clemex|duramin|durascan|\bqness\b|\bQ(10|30|60)\s?A?\b|\bFM-?(7|8|1)\d0e?\b|\bHMV-?(G|2|1)|"
   r"knoop|vickers",
   PARTS + r"|rockwell|brinell|shore|durometer|\bleeb\b|portable|test block|indenter only|\bindenter\b(?!.*tester)|"
           r"tablet|calibration block|nano",
   note="Rockwell, Brinell and portable testers are left out")
st("nanoindenter", "KLA iMicro nanoindenter", 1, 250_000, "vertical", "bench_sens",
   r"\bimicro\b",
   r"\bG200\b|nano\s?indenter\s?(xp|g200|dcm)|\binano\b|keysight.*nano|agilent.*nano\s?indent|\bmts nano|kla.*indent",
   r"nano\s?-?indent|hysitron|\bTI\s?-?(9[0-9]0|750|premier)\b|triboindenter|\bNHT\s?[23]?\b|\bUNHT|nanotest|"
   r"anton paar.*(indent|nht)|csm instruments|nanovea|micro materials|nano\s?-?hardness",
   PARTS + r"|afm\b|atomic force|tip only|probe only",
   note="")
st("pip", "Plastometrex PLX-Benchtop (indentation plastometry)", 1, 130_000, "vertical", "bench",
   r"plx-?benchtop|plastometrex",
   r"indentation plastometry|\bplx\b",
   r"\bfrontics\b|automated ball indentation|\bAIS\s?\d{4}\b",
   PARTS, note="a new product (2019 onward); the nearest technique is automated ball indentation (Frontics AIS)")
st("vhx", "Keyence VHX-7000 with VHX-S750E stand and EA-300 LIBS head", 1, 190_000, "vertical", "bench",
   r"\bVHX-?7\d{3}\b|\bVHX-?X1\b",
   r"\bVHX-?\d{3,4}F?\b|keyence.*digital microscope|\bEA-?300\b",
   r"\bDSX\s?-?(1000|510|500|110|100)\b|\bDVM\s?-?[56]\b|smartzoom|hirox|\bRH-?(2000|8800|5500)\b|\bKH-?(7700|8700)\b|"
   r"digital microscope",
   PARTS + r"|usb microscope|handheld|dino-?lite|celestron|toy|kids|loupe|lens only|zoom lens only|"
           r"\bVK-?X?\d+|laser (scanning|confocal)|\bVR-?\d{4}|\bIM-?\d{4}|\bLJ-?\w+|\bCV-?\w+|\bIV-?\w+",
   note="the EA-300 LIBS head is half the station's price and is rare used")
st("polish", "LECO PX500 grinder/polisher, MX400 mounting press and a sectioning saw", 1, 55_000, "vertical", "bench",
   r"\bPX\s?-?500\b|\bMX\s?-?400\b",
   r"leco.*(px|mx|msx|spectrum system|grinder|polisher|mounting press|cut-?off|saw|sectioning)|\bMSX\s?-?2\d\d\b|"
   r"spectrum system",
   r"automet|ecomet|vector|beta\b.*buehler|buehler.*(grinder|polisher|press|saw|cutter|abrasimet|isomet|simplimet)|"
   r"simplimet|abrasimet|abrasimatic|isomet|tegramin|tegrapol|tegraforce|labopol|labosystem|rotopol|secotom|discotom|"
   r"labotom|accutom|citopress|prontopress|metprep|techpress|techcut|allied.*(polisher|grinder|saw)|"
   r"grinder\s?/?\s?polisher|polisher\s?/?\s?grinder|metallograph\w* (polisher|grinder|saw|press)|mounting press|"
   r"abrasive (cut-?off|cutter|saw)|precision (saw|cutter)|sectioning saw|lapping",
   PARTS + r"|polishing cloth|pads?\b|abrasive (discs?|paper|wheels?)\b(?!.*(saw|cutter))|blades?\b(?!.*saw)|"
           r"polishing (suspension|compound)|resin|epoxy|bakelite|floor (polisher|buffer|burnisher)|car |auto |"
           r"concrete|stone|jewelry|rock|lapidary|tumbler|bench grinder|angle grinder|belt sander|knife",
   comp=dict(polisher=r"px\s?-?500|polisher|grinder|automet|ecomet|tegramin|tegrapol|labopol|rotopol|metprep|vector|"
                      r"spectrum system|lapping",
             press=r"mx\s?-?400|press|simplimet|citopress|prontopress|techpress",
             saw=r"saw|cut|abrasimet|abrasimatic|isomet|secotom|discotom|labotom|accutom|msx"),
   note="three machines: priced as polisher + press + saw")
st("furnaces", "Nabertherm NAT 15/65 forced-convection furnace (to 650 C)", 2, 20_000, "vertical", "bench_heavy",
   r"\bNAT?\s?15/65\b",
   r"nabertherm.*\b(NA|NAT|N)\s?\d+/(65|45|85)\b|nabertherm.*(forced convection|air circulation|recirculat)|"
   r"\b(NA|NAT)\s?\d+/(65|45|85)\b",
   r"forced[- ]convection (furnace|oven)|air[- ]circulat\w* (furnace|oven)|recirculating air (furnace|oven)|"
   r"(despatch|blue m|lindberg|thermcraft|carbolite|grieve|wisconsin oven).*(furnace|oven)|"
   r"(box|muffle|chamber|bench\s?top|benchtop|heat treat\w*) (furnace|oven)|nabertherm|thermolyne|"
   r"\bF\d{5}\b|\bBF\d{5}\b|\bLHT\b|\bCWF\b|\bRHF\b|\bELF\b|furnace",
   PARTS + r"|heating element|thermocouple only|controller only|crucible|kiln (shelf|furniture)|ceramic kiln|"
           r"pottery|glass kiln|dental|tube furnace|rotary|vacuum furnace|induction|melting furnace|forge|"
           r"hvac|gas furnace|home furnace|residential|propane|natural gas|btu|trane|lennox|carrier|goodman|"
           r"rheem|york|furnace filter|incubator|drying oven|vacuum oven|toaster|pizza|convection oven(?!.*(furnace|\d{3,4}\s?°?\s?c))|"
           r"bakery|kitchen|food|smoker|reflow|curing oven|paint",
   note="the vertical lab's two NAT 15/65; a box furnace is a substitute for heat treatment above 650 C")
st("furnace", "Box furnace (about 1,200 C) and a forced-convection ageing oven", 1, 30_000, "conventional", "bench_heavy",
   r"$^", r"$^",
   r"(box|muffle|chamber|bench\s?top|benchtop|heat treat\w*) furnace|thermolyne|lindberg|carbolite|nabertherm|"
   r"\bF\d{5}\b|\bBF\d{5}\b|\bLHT\b|\bCWF\b|\bRHF\b|\bELF\b|vulcan|neytech|thermcraft|\bfurnace\b",
   PARTS + r"|heating element|thermocouple only|controller only|crucible|kiln (shelf|furniture)|ceramic kiln|"
           r"pottery|glass kiln|dental|rotary|induction|melting furnace|forge|hvac|gas furnace|home furnace|"
           r"residential|propane|natural gas|btu|trane|lennox|carrier|goodman|rheem|york|furnace filter|reflow",
   note="the conventional lab's furnace; the same listings serve both labs' furnace roles")
st("sieve_cell", "Sieve cell: Retsch AS 200, tipper, wash module, downdraft enclosure", 1, 60_000, "vertical", "bench",
   r"\bAS\s?200\b",
   r"retsch.*(sieve|shaker|AS\s?\d{3})|\bAS\s?(300|400|450)\b",
   r"sieve shaker|ro-?tap|\bRX-?(29|30|812|86)\b|gilson.*(sieve|shaker)|endecotts|octagon (200|digital)|"
   r"analysette\s?3|fritsch.*sieve|test sieve shaker|vibratory sieve|sieving machine|\bSS-?(8|15|23)R?\b",
   PARTS + r"|sieves? only|test sieves?\b(?!.*shaker)|sieve pans?|lids?\b|stainless sieves?\b(?!.*shaker)|"
           r"flour|kitchen|garden|soil sifter|screen\b(?!.*shaker)",
   note="the shaker is the only part with a used market; the tipper, wash module and enclosure are custom")
st("sieve", "Retsch AS 200 sieve shaker and a set of sieves", 1, 8_000, "conventional", "bench",
   r"\bAS\s?200\b",
   r"retsch.*(sieve|shaker|AS\s?\d{3})|\bAS\s?(300|400|450)\b",
   r"sieve shaker|ro-?tap|\bRX-?(29|30|812|86)\b|gilson.*(sieve|shaker)|endecotts|octagon (200|digital)|"
   r"analysette\s?3|fritsch.*sieve|test sieve shaker|vibratory sieve|sieving machine|\bSS-?(8|15|23)R?\b",
   PARTS + r"|sieves? only|sieve pans?|lids?\b|flour|kitchen|garden|soil sifter",
   note="the conventional lab's shaker: the same listings as sieve_cell")
st("doser", "Multi-doser carousel, A&D HR-202i balance, Specac Atlas Autotouch 15T, Edwards RV3", 1, 50_000,
   "vertical", "bench",
   r"atlas\s?autotouch|\bHR-?202i\b",
   r"specac.*(press|atlas)|atlas.*(15|25|40)\s?t|\bHR-?(202|250|150|100)\w*\b|edwards\s?rv\s?-?[35]\b",
   r"carver.*press|\bcarver\b|laboratory (hydraulic )?press|hydraulic (pellet|laboratory|lab) press|pellet press|"
   r"\bcrushir\b|semi-?micro balance|analytical balance|\b(XS|XP|XPE|XSR|XPR|MS|ME|ML|AB|AG)\s?\d{3}\w?\b.*(balance|mettler)|"
   r"mettler.*balance|sartorius.*balance|cubis|quintix|secura|\brv\s?[35]\b|rotary vane (vacuum )?pump",
   PARTS + r"|weights?\b(?!.*balance)|calibration weight|scale\b(?!.*(analytical|lab))|platform scale|floor scale|"
           r"bathroom|kitchen|jewelry|postal|counting scale|shop press|arbor press|h-?frame|rosin|heat press|"
           r"t-?shirt|garage|automotive|bearing press|log splitter|oil only|pump oil",
   comp=dict(press=r"press|atlas|crushir|carver", balance=r"balance|HR-?2|cubis|quintix|secura|mettler|sartorius",
             pump=r"pump|rv\s?[35]"),
   note="the carousel is custom (BoM $2,362); the balance, press and pump have used markets")
st("density", "Density balance kit and a stereo microscope", 1, 12_000, "conventional", "bench",
   r"$^", r"$^",
   r"density (kit|determination)|stereo\s?-?(zoom )?microscope|\bSZX\s?\d+|\bSZ61\b|\bSMZ\s?-?\d+|\bM(80|125|165|205)\b.*leica|"
   r"leica.*\b(S6|S8|S9|M80|M125|M165|MZ\s?\d+)\b|stemi|dissecting microscope",
   PARTS + r"|biological|compound microscope|student|kids|toy|usb|camera only|ring light only|boom stand only",
   note="")
st("glovebox", "Inert PureLab HE glovebox with purifier, O2 and dew-point sensors", 1, 55_000, "both", "floor",
   r"purelab\s?he|inert.*purelab",
   r"\binert\b.*(glove\s?box|i-?lab|purelab)|innovative technology.*glove",
   r"mbraun|m\.? braun|labstar|unilab|labmaster|vacuum atmospheres|\bVAC\b.*(glove|nexus|omni|genesis)|omni-?lab|"
   r"nexus (ii|one)|jacomex|lc technology|glovebox technology|\bGS (glove|mega)|etelux|vigor|mikrouna|"
   r"(inert|argon|nitrogen).*(glove\s?box|glovebox)|(glove\s?box|glovebox).*(purifier|inert|argon|recirculat)|"
   r"glove\s?box|glovebox",
   PARTS + r"|gloves?\b(?!\s?box)|glove ports?|o-?rings?|regeneration gas|catalyst|molecular sieve|sensor only|"
           r"acrylic|plas-?labs|isolator|anaerobic|coy\b|biological|pcr|sandblast|blast cabinet|bead blast|"
           r"abrasive blast|cleanroom|clean bench|\bbsc\b|laminar|hood\b",
   note="acrylic boxes without a purifier are left out; they can't hold ppm-level O2 and H2O")
st("hoods", "Ducted 6 ft fume hood, installed", 2, 35_000, "both", "floor",
   r"\b6\s?(ft|')\b.*fume hood|fume hood.*\b6\s?(ft|')|72\s?(\"|in|inch).*fume hood|fume hood.*72\s?(\"|in)",
   r"\b[4-8]\s?(ft|')\b.*fume hood|fume hood.*\b[4-8]\s?(ft|')|fume hood.*(48|60|72|96)\s?(\"|in)",
   r"fume hood|chemical hood|labconco.*(protector|xstream|premier|hood)|kewaunee.*hood|hamilton.*(safeaire|hood)|"
   r"hemco|mott.*hood|jamestown.*hood|\bfisher hamilton\b",
   PARTS + r"|ductless|filter|carbon|biological safety|\bbsc\b|biosafety|laminar|clean bench|pcr|"
           r"range hood|kitchen|hood vent|car hood|truck hood|exhaust fan only|sash only|base cabinet only|"
           r"weighing|powder hood|balance enclosure|downdraft table",
   note="installation, ducting and the exhaust fan are most of a ducted hood's installed cost, used or new")
st("icpms", "Agilent 7850 ICP-MS with SPS 4, chiller, trace-metals hood, hot block and dilutor", 1, 260_000,
   "vertical", "floor_sens",
   r"\b78[05]0\b.*(icp|agilent)|agilent.*\b78[05]0\b",
   r"agilent.*\b(7900|7800|7700x?|7700e|7500\w*|8800|8900|7850)\b|\b(7900|7700x|7500cx|7500ce|8800|8900)\b.*icp",
   r"icp-?\s?ms|nexion|icap\s?(q|rq|tq)|elan\s?(6000|6100|9000|drc)|\bx\s?series\s?(ii|2)|plasmaquant ms|"
   r"\bICPMS-?2030|\bicpms\b",
   PARTS + r"|cones?\b|torch\b|nebuli[sz]er|spray chamber|injector|autosampler only|\bsps\s?4\b only|"
           r"icp-?oes|optima|icap\s?(6000|7000|pro)|\b5100\b|\b5110\b|\b5800\b|\b5900\b|\b720\b|\b730\b|"
           r"vista|mp-?aes|aas\b|atomic absorption|gc-?ms|lc-?ms|quadrupole only|turbo pump",
   note="ICP-OES is a different instrument and left out")
st("instron", "Instron 68FM-100 floor frame (100 kN) with grips and extensometer", 1, 175_000, "vertical",
   "floor_heavy",
   r"\b68FM-?100\b",
   r"instron.*\b(68FM|68TM|59(82|85|89)|33(82|84|86)|44(82|85|86|04|05|65|66|67|68|69)|55(82|85|86|65|66|67|68|69)|"
   r"45\d\d|42\d\d|11\d\d|5500R|4200|4400)\b|\b(59(82|85|89)|33(82|84|86)|44(82|85|86)|55(82|85|86))\b",
   r"\bmts\b.*(criterion|insight|sintech|alliance|qtest|frame|universal|tensile|load frame)|criterion\s?(4[3-5]|6[4-6])|"
   r"zwick.*\bZ\s?(050|100|150|250)\b|\bZ\s?(050|100|150|250)\b|shimadzu.*(ag-?x|ags-?x|ag-?i|ag-?is|autograph)|"
   r"tinius olsen|super l|\bH\d{2,3}K[SUT]\b|admet|united testing|test resources|universal test\w*|tensile test\w*|"
   r"load frame|testing machine|materials test\w*|\butm\b|satec|baldwin|tensile tester|instron",
   PARTS + r"|load cell only|load cell\b(?!.*(frame|tester|machine))|extensometer\b(?!.*(frame|tester|machine))|"
           r"grips?\b(?!.*(frame|tester|machine))|wedge|fixture|platens?|controller only|\b8800 controller\b|"
           r"hardness|impact|charpy|izod|torsion|compression only|concrete|cement|asphalt|soil|"
           r"\b34SC|\b33(42|43|44|45)\b|\b59(42|43|44)\b|\b55(42|43|44)\b|\b34TM|single column|table\s?top|"
           r"tensile strength tester for|paper|textile|bottle|cap torque|peel|seal strength",
   note="floor frames of 50 kN and up; single-column and table-top frames are the zwick station's")
st("chamber", "Instron 3119-608 environmental chamber (to 600 C)", 1, 50_000, "vertical", "bench_heavy",
   r"\b3119-?6\d\d\b",
   r"\b3119-?\d{3}\b|instron.*(environmental chamber|furnace|temperature chamber|heating chamber)",
   r"(environmental|temperature|thermal|heating) chamber.*(instron|mts|zwick|tensile|testing machine|load frame|utm)|"
   r"(instron|mts|zwick|tensile|testing machine|load frame|utm).*(environmental|temperature|thermal|heating) chamber|"
   r"(split|high temperature).*furnace.*(tensile|creep|instron|mts|testing)|\bMTS 651\b|\b653\b.*mts",
   PARTS, note="only chambers made for a load frame; product-test chambers (Thermotron, ESPEC) are left out")
st("zwick", "ZwickRoell zwickiLine Z5.0 TN with testControl II", 1, 35_000, "vertical", "bench",
   r"zwickiline\s?Z?\s?5|\bZ\s?5\.0\s?TN\b",
   r"zwickiline|zwick.*\bZ\s?(0\.5|1\.0|2\.5|5\.0|005|010|2\.5)\b|\bZ\s?(005|010|2\.5)\b|zwick",
   r"instron.*\b(34SC|33(42|43|44|45)|59(42|43|44)|55(42|43|44)|34TM)\b|\b(34SC|33(42|43|45)|59(42|43|44)|55(42|43|44))\b|"
   r"criterion\s?42|\bEZ-?(LX|SX|S|L|test)\b|shimadzu.*(ez|table)|mark-?10.*(esm|test stand)|\bESM\s?\d{3,4}\b|"
   r"tinius olsen.*\bH\d{1,2}KS|single column|table\s?top (tensile|testing|universal)|lloyd|ametek.*(ls\d|lr\d)|"
   r"testometric|tensile tester|universal test\w*",
   PARTS + r"|load cell only|load cell\b(?!.*(frame|tester|machine))|extensometer\b(?!.*(frame|tester|machine))|"
           r"grips?\b(?!.*(frame|tester|machine))|wedge|fixture|controller only|hardness|impact|charpy|izod|"
           r"concrete|cement|asphalt|soil|paper|textile|bottle|cap torque|\bforce gauge\b",
   note="table-top frames up to about 10 kN")
# ---------------------------------------------------------------------------------------------- floor machines
st("edm", "FANUC ROBOCUT wire EDM", 1, 230_000, "vertical", "machine",
   r"robocut.*\bC\s?-?(400|600|800)\s?i\s?C\b|\bC(400|600|800)iC\b",
   r"robocut|fanuc.*\b(wire|edm)\b|\bfanuc\s?w[0-3]\b|\ba-?(0|1|C)i[ABCDE]\b.*fanuc",
   r"wire\s?-?edm|wire (eroding|erosion|electrical discharge)|wire cut|wire-?cut|\bsodick\b.*\b(AQ|AG|ALC|ALN|VZ|SL|EXC)\d*|"
   r"\b(AQ|AG|ALC|ALN|VL)\s?\d{3}\w*\b.*sodick|mitsubishi.*\b(MV|MP|FA|NA|BA|PA|MX)\s?\d{4}|\b(MV|MP)\d{4}\w*\b|"
   r"makino.*\b(U|UP|SP|UPJ|DUO)\s?\d|charmilles|agie|\bcut\s?(200|300|400|e|p|x)\b|seibu|accutex|chmer|excetek|"
   r"\bONA\b|hitachi.*edm|brother.*hs-?\d{3,4}",
   PARTS + r"|sinker|\bram\b|die sinker|hole (popper|drill)|small hole|edm drill|super drill|ziggy|"
           r"wire (only|spool|reel)|brass wire|resin|deionizer|diamond guides?|power feed contact|"
           r"\bfilters?\b|electrode|graphite",
   note="wire EDMs only (no sinker or hole drill)")
st("machining", "Machining cell (PR 373): Haas ST-10 bar-fed lathe, pedestal UR10e, wash, dryer, gauge", 1, 275_000,
   "vertical", "machine",
   r"\bST\s?-?10\b(?!0)|\bST-?10Y\b",
   r"haas.*\b(ST\s?-?1[05]|ST\s?-?20|TL\s?-?1|TL\s?-?15|DS\s?-?30|ST\s?-?15Y?)\b|haas.*bar feeder|"
   r"\bur\s?(10|12|16)e?\b|universal robots.*\bur\s?\d+e?\b",
   r"(okuma|doosan|dn solutions|mazak|hardinge|romi|hurco|nakamura|miyano|mori seiki|dmg|kia|hwacheon|samsung|"
   r"daewoo|femco|takisawa|tsugami|citizen|star\b|eurotech|leadwell|victor|feeler|nexturn|hanwha).*(lathe|turn|"
   r"lb\s?\d|lynx|puma|qtn|quick turn|nl\s?\d|cl\s?\d|gs\s?\d|conquest)|cnc (lathe|turning)|turning (center|centre)|"
   r"bar feeder|lns\b|edge (patriot|technologies)|iemca|\bSL-?(10|20)\b.*(haas|lathe)",
   PARTS + r"|tool holder|toolholder|turret disc|chuck\b(?!.*lathe)|collet chuck|spindle only|"
           r"manual lathe|engine lathe|toolroom lathe(?!.*haas)|wood lathe|metal lathe(?!.*cnc)|mini lathe|"
           r"swiss(?!.*bar)|gang tool|teach pendant only|pendant only|controller only|robot cable",
   comp=dict(lathe=r"lathe|turn|\bST\b|\bTL\b|lynx|puma|qtn|quick turn|conquest|\bSL-?\d",
             bar_feeder=r"bar feeder|lns|edge|iemca",
             robot_arm=r"\bur\s?\d|universal robots"),
   note="the lathe, bar feeder and arm have used markets; the wash, dryer, weigh module, gauge and integration don't")
st("carvera", "Makera Carvera desktop CNC (tray M)", 1, 5_799, "vertical", "bench",
   r"carvera(?!\s?air)", r"carvera\s?air|makera",
   r"desktop cnc|bantam tools|othermill|pocket\s?nc|nomad 3",
   PARTS + r"|end mills?|bits?\b|collets?|probe only|spoil ?board|enclosure only",
   note="")
st("units", "MiR250 + UR12e + Robotiq 2F-85 mobile manipulator, with cabinet, cameras, Class D unit, integration",
   2, 140_000, "vertical", "machine_light",
   r"\bmir\s?-?250\b|\bur\s?-?12e\b|2f-?85",
   r"\bmir\s?-?(100|200|500|600|1000|1350)\b|mobile industrial robots|\bur\s?-?(10e?|16e|5e|3e|20|30|15)\b|"
   r"universal robots|2f-?140|hand-?e\b|robotiq",
   r"\botto\s?(100|1500|600)\b|omron.*\b(LD|HD)-?\d+|\bLD-?(60|90|250)\b.*omron|fetch robotics|"
   r"(fanuc|doosan|abb|techman|kuka|kinova|aubo|elite|jaka).*(crx|cobot|collaborative|gofa|tm\s?\d+|lbr|\bM\d{4}\b)|"
   r"\bcrx-?\d+|\bgofa\b|onrobot|\brg[26]\b|cobot|collaborative robot|autonomous mobile robot|\bamr\b",
   PARTS + r"|teach pendant only|pendant only|controller only|control box only|robot cable|battery only|"
           r"charger only|top module only|shelf carrier only|cart only|hook only|gripper fingers?|finger tips|"
           r"pads only|\bfor ur\b|ur (compatible|mount|flange)|adapter plate|weld|palletiz|screwdriv|sanding|"
           r"dispens|cell\b|cart\b|\bon (a )?(cart|amr)\b",
   comp=dict(mir=r"mir|mobile industrial|otto|omron|ld-|amr|autonomous mobile|fetch",
             arm=r"\bur\s?\d|universal robots|crx|gofa|cobot|collaborative|techman|doosan|kinova|aubo",
             gripper=r"2f-?|hand-?e|robotiq|onrobot|rg[26]|gripper"),
   note="each unit is a MiR250, a UR12e (the UR10e until May 2025) and a 2F-85, plus integration")
st("floor_unit", "Third MiR250 unit for the floor, with a Nilfisk CFM 118EXP explosion-proof vacuum", 1, 155_000,
   "vertical", "machine_light",
   r"\bCFM\s?118\s?EXP?\b|\b118\s?EXP?\b.*nilfisk",
   r"nilfisk.*\b(CFM|VHS|VHC|ATEX|EXP|explosion|class (ii|2)|combustible)\b|\bCFM\s?\d{3,4}\s?EXP?\b",
   r"(explosion[- ]proof|atex|combustible dust|class ii.*div|haz\w*[- ]location).*(vacuum|vac\b)|"
   r"(vacuum|vac\b).*(explosion[- ]proof|atex|combustible dust)|ruwac|tiger-?vac|goodway.*ex",
   PARTS + r"|filter|hose only|bags?\b|wand|nozzle|attachment|floor scrubber|carpet|wet/dry(?!.*(explosion|atex))|"
           r"shop-?vac|backpack|robot vacuum|roomba|pool",
   comp=dict(vacuum=r"vac|nilfisk|ruwac|cfm", mir=r"mir|mobile"),
   note="the MiR is priced with the units; this key adds the explosion-proof vacuum")
st("shuttle", "Kardex Shuttle XP 500, 9.15 m (30 ft), 2450 x 864 mm trays", 2, 210_000, "vertical", "vlm",
   r"shuttle\s?xp\s?-?500|\bxp\s?-?500\b.*kardex",
   r"kardex.*\b(shuttle|xp\s?-?\d{3,4}|xplus|remstar)\b|remstar|shuttle\s?xp",
   r"vertical lift (module|storage)|\bvlm\b|lean-?lift|h[aä]nel|modula\s?(lift|ml|mc)?|logimat|ferlift|"
   r"vertical (storage|lift) (system|machine)|storage lift|tower storage",
   PARTS + r"|tray only|trays only|tray dividers?|bin dividers?|controller only|keypad|light curtain only|"
           r"carousel|horizontal carousel|vertical carousel|lektriever|megamat|lr\s?35|paternoster|"
           r"file (cabinet|carousel)|pallet rack|shelving",
   note="a used VLM is dismantled, shipped in pieces and re-erected; height and tray size have to fit the room")
st("couplings", "Staubli CombiTac docks and tray plates (each)", 14, 4_000, "vertical", "parcel",
   r"combi\s?-?tac", r"st[aä]ubli.*(coupl|connector|tool changer|mps|rbe)",
   r"ati.*(tool changer|qc-?\d+)|robotic tool changer|multi-?coupling",
   PARTS + r"(?!.*combitac)", note="")
st("repowder", "AMAZEMET rePowder ultrasonic atomizer, with its optimizer and chiller", 1, 350_000, "both", "machine",
   r"repowder", r"amazemet",
   r"(gas|ultrasonic|plasma|centrifugal|metal|powder).*atomi[sz](er|ation|ing)|atomi[sz](er|ation).*(metal|powder|gas|alloy)|"
   r"hermiga|blue power|\bAUG\s?\d{3,4}|arcast|atomizing systems|\bVIGA\b|\bEIGA\b|powder production (plant|system)|"
   r"metal powder (plant|system|machine)",
   PARTS + r"|paint|spray gun|humidifier|mist|fogger|nebuli[sz]er|perfume|airbrush|agricultur|pesticide|"
           r"atomizer nozzle|ultrasonic cleaner|vape|e-?cig|coating|medical",
   note="lab-scale gas and ultrasonic atomizers; the twin's is ultrasonic")
st("midi", "Aconity3D AconityMIDI+ laser powder-bed fusion", 1, 700_000, "vertical", "machine",
   r"aconity\s?midi", r"aconity",
   r"\bEOS\b.*\bM\s?-?(100|270|280|290|300|400)\b|\bEOS\s?M\s?\d{3}\b|\bEOSINT\s?M\s?\d+|"
   r"\bSLM\s?(125|250|280|500)(hl)?\b|slm solutions|renishaw.*\bAM\s?(250|400|500)|\bAM\s?(250|400|500)\b.*renishaw|"
   r"concept laser|\bmlab\b|\bM2 cusing\b|cusing|truprint|trumpf.*(1000|2000|3000).*print|"
   r"\bDMP\s?(flex|factory)?\s?\d+|prox\s?(dmp\s?)?(100|200|300|320)|sisma|mysint|xact metal|\bXM\s?200|"
   r"farsoon|\bBLT-?S\d+|or laser|orlas|\bAddUp\b|velo3d|\bDMLS\b|direct metal laser|selective laser melting|"
   r"laser (powder bed|melting)|\blpbf\b|\bslm\b|metal (3d|additive) (printer|manufacturing)",
   PARTS + r"|resin|\bsla\b|\bfdm\b|fff|filament|ultimaker|markforged|desktop metal|binder jet|exone|"
           r"formlabs|stratasys|prusa|creality|polyjet|objet|nylon|sls\b(?!.*metal)|formiga|\bP\s?(100|110|396|500|770)\b|"
           r"recoater blade|build plate|powder only|filter cartridge|camera only",
   note="small to mid-size LPBF machines; polymer printers (EOS Formiga, P-series) are left out")
st("mxlab", "InssTek MX-Lab blown-powder DED", 1, 300_000, "vertical", "machine",
   r"mx-?lab", r"insstek|\bMX-?(mini|grande|600|1000|450)\b",
   r"optomec|\blens\s?(450|750|850|mr-?7|cs\s?\d+)\b|beam modulo|\bmodulo\b|lasertec\s?\d+\s?3d|"
   r"formalloy|directed energy deposition|\bded\b|laser metal deposition|\blmd\b|laser cladding|blown powder|"
   r"powder (fed|feeder) laser|huffman",
   PARTS + r"|wire|meltio|arc|waam|weld(?!.*laser)|plasma|thermal spray|cold spray|powder feeder only|nozzle only|"
           r"chiller only|camera",
   note="powder-fed DED only (wire-fed and arc machines are left out)")
NA = {
    "ups": "commodity UPSs, bought new with the trays; not surveyed",
    "cameras": "commodity cameras and Pi 5s; not surveyed",
    "services": "the room's fit-out (gas lines, N2 generator, chillers, power, dust collection): building work, not "
                "equipment on a used market",
    "cubxl": "owned (DAL's own CubXL is used from day 0)",
}


MAKERS = (r"haas|kardex|remstar|fanuc|robots|hitachi|instron|zwick|zwickroell|nabertherm|retsch|struers|buehler|leco|"
          r"keyence|rigaku|bruker|malvern|mitutoyo|agilent|sodick|mitsubishi|makino|eos|trumpf|renishaw|optomec|"
          r"insstek|aconity|nilfisk|staubli|doosan|okuma|mazak|phenom|jeol|zeiss|tescan|horiba|shimadzu|"
          r"carbolite|thermolyne|lindberg|mbraun|labconco|specac|carver|edwards|matra|charmilles|agie|"
          r"slm|concept laser|sisma|farsoon|amazemet|mir")
MAKER_RE = re.compile(r"\b(?i:(" + MAKERS + r"))(?=[A-Z0-9])")


def norm(title):
    """Machineseeker runs the maker into the model ('HAASST-10', 'Universal RobotsUR10e'): put the space back."""
    return MAKER_RE.sub(r"\1 ", title or "")


def classify(key, title, extra=""):
    s = S[key]
    title = norm(title)
    t = f"{title} {norm(extra)}"
    if s["excl"] and s["excl"].search(title):
        return None
    for lvl in ("exact", "family", "sub"):
        p = s[lvl]
        if p and p.search(t):
            return lvl
    return None


def component(key, title):
    c = S[key].get("comp")
    if not c:
        return ""
    for name, pat in c.items():
        if re.search(pat, title, re.I):
            return name
    return ""
