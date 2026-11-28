# Round 6: the used-equipment survey in the automated lab's build-out

Made by `python out/twin6/checks/used_market.py`, from `out/twin6/market/summary.csv` (sha256 `51ba653a9cf41261…`) and the engine at this commit. The parallel plan, the grid's 16 seeds. Everything is simulated.

| Seed | Bought used, round 5's stand-ins | Bought used, the survey | Cell integrated (day), stand-ins / survey | Last station online (day) | Capital paid ($M) |
|---|---|---|---|---|---|
| 0 | chamber, edm, instron, nanoindenter | edm, instron | 212 / 212 | 313 / 313 | 4.62 / 4.68 |
| 1 | chamber, edm, instron, nanoindenter | edm (faulty), instron | 161 / 161 | 254 / 254 | 4.70 / 4.71 |
| 2 | chamber, edm, instron, nanoindenter | edm, instron | 206 / 206 | 305 / 305 | 4.63 / 4.68 |
| 3 | chamber, edm, instron, nanoindenter | edm (faulty), instron (faulty) | 171 / 171 | 224 / 224 | 4.65 / 4.73 |
| 4 | chamber, edm, instron, nanoindenter | edm, instron | 201 / 201 | 201 / 201 | 4.62 / 4.68 |
| 5 | chamber, edm, instron, nanoindenter | edm, instron | 248 / 248 | 248 / 248 | 4.62 / 4.68 |
| 6 | chamber, edm, instron, nanoindenter | edm, instron (faulty) | 194 / 194 | 414 / 414 | 4.66 / 4.69 |
| 7 | chamber, edm, instron, nanoindenter | edm, instron | 246 / 246 | 246 / 246 | 4.66 / 4.68 |
| 8 | chamber, edm, instron, nanoindenter | edm, instron | 201 / 201 | 308 / 308 | 4.62 / 4.68 |
| 9 | chamber, edm, instron, nanoindenter | edm (faulty), instron | 233 / 233 | 266 / 266 | 4.70 / 4.71 |
| 10 | chamber, edm, instron, nanoindenter | edm (faulty), instron | 191 / 191 | 227 / 227 | 4.70 / 4.71 |
| 11 | chamber, edm, instron, nanoindenter | edm, instron | 194 / 194 | 260 / 260 | 4.62 / 4.68 |
| 12 | chamber, edm, instron, nanoindenter | edm, instron | 208 / 208 | 214 / 214 | 4.63 / 4.68 |
| 13 | chamber, edm, instron, nanoindenter | edm, instron | 191 / 191 | 226 / 226 | 4.66 / 4.68 |
| 14 | chamber, edm, instron, nanoindenter | edm, instron | 212 / 212 | 216 / 216 | 4.66 / 4.68 |
| 15 | chamber, edm, instron, nanoindenter | edm (faulty), instron | 185 / 185 | 231 / 231 | 4.66 / 4.71 |

Medians over the 16 seeds, stand-ins against the survey: stations bought used 4 against 2; cell integrated on day 201 against 201; last station online on day 247 against 247; capital $4.66M against $4.68M.

## Each station the automated lab buys

The survey's verdict (`market`: `yes` a market the lab would buy from; `thin` too few listings to count on; `none` no listing of the model or its line; `n/a (new only)` not surveyed: commodity or building work), and round 5's rule with the survey's numbers. A station bought partly used (`yes (parts)`) is on site when its new parts are, so its lead is theirs.

| Station | What | New lead (weeks) | Market | Used OK | Listings | Used lead (weeks, after the PO) | Price (fraction of new) | Fault risk | Expected days saved | Bought used |
|---|---|---|---|---|---|---|---|---|---|---|
| cameras | Tray, bay and security cameras with their Pi 5s and switches | 4 | n/a (new only) | no | 0 | 2 | 0.45 | 0.25 | 0 | no |
| carvera | Makera Carvera desktop CNC | 3 | none | no | 0 | 2 | 0.45 | 0.25 | -3.5 | no |
| chamber | Instron 3119-608 environmental chamber | 16 | thin | no | 4 | 2.5 | 0.09 | 0.17 | 28.5 | no |
| couplings | CombiTac docks and tray plates on 12 powered trays and 2 bays | 8 | yes | yes | 6 | 2 | 0.18 | 0.25 | 0 | no |
| doser | Multi-doser carousel, A&D HR-202i balance, Specac Atlas Autotouch 15T with vacuum dies and an Edwards RV3 pump | 16 | yes (balance, pump) | yes | 62 | 14 | 0.94 | 0.44 | -12.7 | no |
| ebsd | EBSD detector on the SEM | 16 | thin | no | 2 | 5 | 0.04 | 0.30 | 21.5 | no |
| edm | FANUC ROBOCUT wire EDM | 18 | yes | yes | 117 | 3 | 0.20 | 0.31 | 32 | **yes** |
| eds | Oxford Instruments AZtecOne EDS for the TM4000 | 10 | thin | no | 1 | 2.5 | 0.45 | 0.30 | -10.5 | no |
| floor_unit | Third MiR250 unit for the floor, with a Nilfisk CFM 118EXP explosion-proof vacuum | 14 | yes (mir, arm, vacuum) | yes | 53 | 12 | 0.65 | 0.53 | -21.8 | no |
| furnaces | Nabertherm NAT 15/65 forced-convection furnaces | 8 | yes | yes | 65 | 2 | 0.21 | 0.28 | -3.5 | no |
| glovebox | Inert PureLab HE glovebox with purifier, O2 and dew-point sensors | 12 | yes | yes | 14 | 2.5 | 0.31 | 0.28 | -3 | no |
| hardness | Mitutoyo HM-220 micro-Vickers with AVPAK | 8 | yes | yes | 26 | 2 | 0.12 | 0.23 | -3.5 | no |
| hoods | Ducted 6 ft fume hoods, installed | 10 | yes (hood) | yes | 13 | 2.5 | 0.75 | 0.34 | -7 | no |
| icpms | Agilent 7850 ICP-MS with SPS 4, chiller, trace-metals hood, hot block and dilutor | 14 | yes (instrument) | yes | 95 | 12 | 0.60 | 0.19 | -24.5 | no |
| instron | Instron 68FM-100 floor frame with grips and extensometer | 16 | yes | yes | 61 | 3 | 0.12 | 0.29 | 21.5 | **yes** |
| machining | Machining cell | 22 | yes (lathe, bar_feeder, robot_arm) | yes | 105 | 20 | 0.85 | 0.60 | -39.2 | no |
| mastersizer | Malvern Mastersizer 3000 with Aero S | 10 | yes | yes | 69 | 2.5 | 0.18 | 0.25 | -10.5 | no |
| midi | Aconity3D AconityMIDI+ laser powder-bed fusion | 18 | none | no | 82 | 2 | 0.45 | 0.25 | 4 | no |
| mxlab | InssTek MX-Lab blown-powder DED | 26 | none | no | 4 | 2 | 0.45 | 0.25 | 60 | no |
| nanoindenter | KLA iMicro nanoindenter | 16 | thin | no | 3 | 2.5 | 0.10 | 0.37 | 21.5 | no |
| pip | Plastometrex PLX-Benchtop | 12 | none | no | 0 | 2 | 0.45 | 0.25 | 0.5 | no |
| polish | LECO PX500 grinder/polisher, MX400 mounting press, sectioning saw | 8 | yes (polisher, press, saw) | yes | 33 | 2 | 0.22 | 0.53 | -3.5 | no |
| sem | Hitachi TM4000PlusII benchtop SEM | 10 | yes | yes | 18 | 3.5 | 0.20 | 0.12 | -10.5 | no |
| shuttle | Kardex Shuttle XP 500, 9.15 m | 14 | thin | no | 35 | 9 | 0.45 | 0.24 | -3.2 | no |
| sieve_cell | Sieve cell: Retsch AS 200, tipper, wash module, downdraft enclosure | 12 | yes (shaker) | yes | 43 | 10 | 0.95 | 0.26 | -8.9 | no |
| units | MiR250 + UR12e + Robotiq 2F-85 mobile manipulator, with cabinet, cameras, Class D unit, integration | 14 | yes (mir, arm) | yes | 46 | 12 | 0.63 | 0.33 | -16.2 | no |
| ups | UPSs on the powered trays | 6 | n/a (new only) | no | 0 | 2 | 0.45 | 0.25 | 0 | no |
| vhx | Keyence VHX-7000 with VHX-S750E stand and EA-300 LIBS head | 6 | yes (microscope) | yes | 21 | 4 | 0.69 | 0.33 | -3.5 | no |
| xrd | Rigaku MiniFlex 600-C benchtop XRD with prep station | 10 | yes | yes | 8 | 2.5 | 0.24 | 0.30 | -10.5 | no |
| xrf | Bruker S2 PUMA Series 2 EDXRF with XY autochanger | 12 | yes | yes | 18 | 2.5 | 0.12 | 0.28 | -6.5 | no |
| zwick | ZwickRoell zwickiLine Z5.0 TN with testControl II | 10 | yes | yes | 32 | 3 | 0.38 | 0.17 | -3.5 | no |

**No used market the lab would buy from** (`round6.no_used_market()`): cameras (n/a (new only)); carvera (none); chamber (thin); ebsd (thin); eds (thin); midi (none); mxlab (none); nanoindenter (thin); pip (none); shuttle (thin); ups (n/a (new only)).
