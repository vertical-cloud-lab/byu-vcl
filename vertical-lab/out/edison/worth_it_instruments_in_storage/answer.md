Question: Has anyone housed powered, operating laboratory or production instruments (not passive inventory such as samples, reagents, tools or spare parts) inside the trays or carriers of a vertical lift module (VLM), vertical carousel, paternoster or other automated storage and retrieval system, so that the storage machine brings the instrument to a fixed access opening where a person or robot loads it, and the instrument keeps running (with power, data, gas or exhaust) while its tray is stored? Include laboratory automation, biobanks, pharmacies, incubator hotels, burn-in and test racks in electronics manufacturing, server or battery-cycling racks, and patents.

No. ## Conclusion

**Yes as a patent disclosure; not yet verified as an installed laboratory or production system.** Two Vidir Solutions patent families directly describe bringing a carrier bearing an *electrically operating device* to a fixed access location and powering that carrier inside a vertical storage machine. The stronger match is a **vertical carousel** that supplies power continuously to moving shelves and explicitly proposes refrigerators and chargers as shelf-mounted loads. A separate **vertical-lift-module (VLM)** design powers devices on trays *after the trays are returned to storage*, but does not establish uninterrupted operation during tray retrieval. Neither patent, by itself, demonstrates that a customer has built or operated the claimed configuration. (CA3162492C pages 1-3, CA3162492C pages 3-6, CA3162492C pages 6-8, CA3162492C pages 8-9, US20240116714A1 pages 9-11, US20240116714A1 pages 15-17)

**How the two direct disclosures work.** In *CA3162492C, Storage system with movable platforms and internal electrical power distribution system* (2025), a motor-driven vertical carousel circulates shelves to an access opening in its fixed housing. The specification names refrigerators, lighting and chargers as devices on the shelves and proposes refrigerated vaccines, battery charging and preheating molds. Stationary, loop-shaped conductors follow the carousel path; sliding electrical contacts, slip rings and shelf-mounted outlets deliver power as each shelf moves and pivots. This is a substantive answer for **powered operating equipment**, rather than simply samples kept cold by a stationary refrigerator. The named uses are proposed uses, however, not documented installations. (CA3162492C pages 1-3, CA3162492C pages 3-6, CA3162492C pages 6-8, CA3162492C pages 8-9)

In *US20240116714A1, Vertical tray storage system with internal electrical power distribution system* (2024), an elevator presents removable trays at a user-retrieval space and returns them to vertically stacked rack positions. Each position has a fixed power port; its mating tray port feeds receptacles for devices *on that tray*. The controller confirms that the tray is stowed, then delays energization to reduce arcing; the specification also mentions rack ventilation to dissipate electrical heat. It does **not** name a particular laboratory instrument or demonstrate power continuity while the elevator is moving the tray. The applicant’s statement that it sells a VLM must not be read as evidence that it sells this electrified version. (US20240116714A1 pages 1-4, US20240116714A1 pages 4-6, US20240116714A1 pages 13-15, US20240116714A1 pages 15-17)

The comparison below separates these disclosures from superficially similar automated stores.

| Evidence / year | Moving payload and fixed access | Electricity while stored / moving | Classification and critical caveat |
|---|---|---|---|
| **Vidir CA3162492C (2025), vertical carousel** | Movable shelves carrying claimed refrigerators, chargers, lighting, or mold-heating equipment circulate to a fixed frame access opening. | **Stored: yes. Moving: yes.** An endless busbar, sliding contacts, shelf outlets, converters, and slip rings maintain power throughout the carousel path. (CA3162492C pages 1-3, CA3162492C pages 6-8, CA3162492C pages 8-9) | **Direct patent match.** It expressly covers operating electrical devices on moving storage carriers, but is a patent disclosure—not evidence of a built or deployed installation. |
| **Vidir US20240116714A1 (2024), VLM** | Elevator transfers removable trays between rack locations and a fixed user-retrieval space. Trays may carry electrical devices. | **Stored: yes. Moving: not shown.** Rack and tray contacts mate after stow; a timed safety interlock then energizes the tray receptacle. Rack ventilation dissipates generated heat. (US20240116714A1 pages 6-9, US20240116714A1 pages 15-17) | **Direct architecture, incomplete use case.** Specific instruments are not identified, and operation during elevator travel is unsupported. Patent application, not documented use. |
| **WO2025262586A1 (2025), battery-conditioning warehouse** | Lift moves trays of electrochemical cells between a fixed loading opening, conditioning locations, and fixed test stations. | Cells connect to fixed formation/test electronics at stations. Tray-integrated thermal circuits dock through liquid quick couplings; utilities disconnect for transport. (WO2025262586A1 pages 4-7, WO2025262586A1 pages 26-28) | **Near analogue—not a moving instrument.** Cells and trays move; formation modules and test instruments remain fixed. Patent disclosure only. |
| **US20070040570A1 (2007), semiconductor handler** | Burn-in/test boards move from a storage cassette to loading and electrical-test positions, then return to the cassette or go to separate burn-in equipment. | Boards are energized at test equipment, not shown powered while stored or transported. (US20070040570A1 pages 9-10, US20070040570A1 pages 10-11) | **Not a match.** A movable test fixture carries DUTs, but the operating tester is fixed and live operation in storage is absent. Patent disclosure only. |
| **US8083994B2 (2011), biobank/sample store** | A vertical carousel aligns specimen trays with a shuttle, which transfers samples to fixed processing modules. | No powered instrument is carried on a stored tray; the payload is passive sample inventory. (US8083994B2 pages 1-4) | **Excluded.** This is automated specimen storage and retrieval, not storage of operating instruments. Patent disclosure only. |


*Table: Comparison of direct powered-carrier patent disclosures with battery, semiconductor, and biobank systems that move products or samples to fixed equipment. It distinguishes power in storage from power during movement and patent proposals from documented deployments.*

## Why the other sectors do not establish the same configuration

- **Laboratory automation and biobanks:** A Brooks Automation patent uses a vertical carousel to align *sample trays* with a shuttle and fixed sample-processing modules. Automated cell-culture incubator patents likewise move culture vessels or assay plates to imaging and handling equipment; they do not show an entire operating microscope or incubator riding a stored tray to the access opening. These are genuine automated laboratory systems, but the **samples move, not the powered instruments**. (US8083994B2 pages 1-4, US20240409871A1 pages 101-103, US12098358B2 pages 13-17)
- **Pharmacies and refrigerated inventory:** The carousel patent expressly proposes operating a shelf-mounted refrigerator to keep vaccines refrigerated—closer to the requested configuration than a climate-controlled cabinet containing passive vaccine containers. It remains a *proposed patent embodiment*, not a verified pharmacy installation. (CA3162492C pages 3-6, CA3162492C pages 8-9)
- **Electronics burn-in:** The semiconductor handler moves burn-in boards from a cassette to a loading and electrical-test position; populated boards subsequently go to separate burn-in apparatus. Its test circuit is not shown operating on a board while that board sits in its storage cassette. A test board is an active-test fixture *when connected to a tester*, but this is not evidence of a continuously operating stored fixture. (US20070040570A1 pages 9-10, US20070040570A1 pages 10-11)
- **Battery formation and cycling:** A 2025 battery-conditioning warehouse patent provides an operator-accessible transfer opening and a lift that moves cell trays among vertically arranged stations. At those stations, fixed formation/test equipment connects to the cells; the trays can also mate with station plumbing through quick-disconnect liquid connectors for thermal conditioning. This demonstrates useful **utility docking in storage**, but the formation/test instruments themselves are not carried to the opening on the trays. (WO2025262586A1 pages 4-7, WO2025262586A1 pages 26-28)

**Evidence boundary.** The retrieved material supports electrical power to moving carousel shelves and electrical power to *stowed* VLM trays. It does not verify a deployed VLM/carousel carrying a running analytical instrument, bioreactor, burn-in tester, server or battery cycler, nor a carrier-level arrangement that maintains instrument data, gas or exhaust connections through storage and presentation. A patent establishes that someone **described and claimed** a configuration; it does not establish that anyone **housed and operated** the specified equipment in a real installation. (CA3162492C pages 1-3, CA3162492C pages 6-8, US20240116714A1 pages 9-11, US20240116714A1 pages 15-17, WO2025262586A1 pages 4-7)

References

1. (CA3162492C pages 1-3): Delmer Plett. Storage system with movable platforms and internal electrical power …. Patent (US,CA), 2025.

2. (CA3162492C pages 3-6): Delmer Plett. Storage system with movable platforms and internal electrical power …. Patent (US,CA), 2025.

3. (CA3162492C pages 6-8): Delmer Plett. Storage system with movable platforms and internal electrical power …. Patent (US,CA), 2025.

4. (CA3162492C pages 8-9): Delmer Plett. Storage system with movable platforms and internal electrical power …. Patent (US,CA), 2025.

5. (US20240116714A1 pages 9-11): Dimitri Warlet Caldeira. Vertical tray storage system with internal electrical power distribution system. Patent (US,CA), 2024.

6. (US20240116714A1 pages 15-17): Dimitri Warlet Caldeira. Vertical tray storage system with internal electrical power distribution system. Patent (US,CA), 2024.

7. (US20240116714A1 pages 1-4): Dimitri Warlet Caldeira. Vertical tray storage system with internal electrical power distribution system. Patent (US,CA), 2024.

8. (US20240116714A1 pages 4-6): Dimitri Warlet Caldeira. Vertical tray storage system with internal electrical power distribution system. Patent (US,CA), 2024.

9. (US20240116714A1 pages 13-15): Dimitri Warlet Caldeira. Vertical tray storage system with internal electrical power distribution system. Patent (US,CA), 2024.

10. (US20240116714A1 pages 6-9): Dimitri Warlet Caldeira. Vertical tray storage system with internal electrical power distribution system. Patent (US,CA), 2024.

11. (WO2025262586A1 pages 4-7): Claudio Rossi. Warehouse for at least partially conditioning electrochemical cells and method …. Patent (WO,IT), 2025.

12. (WO2025262586A1 pages 26-28): Claudio Rossi. Warehouse for at least partially conditioning electrochemical cells and method …. Patent (WO,IT), 2025.

13. (US20070040570A1 pages 9-10): Ballson Gopal. Method for testing semiconductor devices and an apparatus therefor. Patent (WO,US,JP,KR), 2007.

14. (US20070040570A1 pages 10-11): Ballson Gopal. Method for testing semiconductor devices and an apparatus therefor. Patent (WO,US,JP,KR), 2007.

15. (US8083994B2 pages 1-4): Robert K. Neeper. System and method for selectively extracting individual vials from an array of …. Patent (WO,EP,US,CN,DK), 2011.

16. (US20240409871A1 pages 101-103): Alan Blanchard. Automated incubator with robotic transport. Patent (US), 2024.

17. (US12098358B2 pages 13-17): Alan Blanchard. Automated incubator with robotic transport. Patent (WO,EP,US,CN,JP), 2024.
