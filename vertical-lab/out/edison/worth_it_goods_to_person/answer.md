Question: Goods-to-person versus person-to-goods order picking in manufacturing and warehousing, with vertical lift modules in particular: travel-time and throughput models for VLMs (for example Meller and Klote 2004; Dukic, Opetuk and Lerher 2015; Rosi et al. 2016; Sgarbossa, Calzavara and Persona 2019; Calzavara et al.), dual-command cycle times as a function of height, vertical speed and acceleration, typical trays per hour for one access opening, dual-tray (two-level) openings, the conditions under which a VLM is economical (number of stock-keeping units, pick frequency, floor cost) and when it is not, and comparisons with shelving, horizontal carousels, mini-load AS/RS, shuttle systems and autonomous mobile robots.

# Goods-to-person versus person-to-goods picking: the VLM decision

**The central trade-off is walking time versus equipment time and cost.** With shelving, people travel to stock; a vertical lift module (VLM) stores items on trays and brings a requested tray to a stationary picker. A VLM can therefore reduce walking and use building height, but its lift and access opening impose a finite delivery rate. The appropriate comparison is **completed order lines per paid hour and annual cost for the same inventory and demand**, not a machine’s advertised tray rate versus a shelving picker’s line rate. (đukic2021singletrayvlmvsa pages 1-2, munoz2025taxonomicclassificationand pages 39-43, azadeh2019robotizedandautomated pages 5-8)

## Travel-time and throughput models

Meller and Klote (2004) developed an analytical throughput model for carousel/VLM *pods* with human pickers and order batching; their VLM representation has a single presentation position. Building on that work and mini-load AS/RS models, Đukić, Opetuk and Lerher (2015) modeled a VLM with **one lift and two vertically separated tray positions**. Rosi and colleagues (2016) instead simulated a **single-tray, single-opening** VLM using its lift-speed profile. Sgarbossa, Calzavara and Persona (2019) examined throughput under different dual-bay configurations, storage assignments and retrieval sequences; Calzavara, Sgarbossa and Persona (2019) examined the economic choice against conventional carton racks. The original full texts of those last two 2019 papers, and of the 2004 and 2015 papers, were not available for direct numerical extraction here; their scope is corroborated by accessible subsequent studies. (rosi2016simulationbasedperformanceanalysis pages 3-6, đukic2021singletrayvlmvsa pages 1-2, đukic2021singletrayvlmvsa pages 2-3, munoz2025taxonomicclassificationand pages 48-51)

For a lift that starts and stops at each level, with vertical travel distance *d*, maximum speed *v* and equal acceleration/deceleration magnitude *a*, the physically consistent motion time is

\[
t(d)=\begin{cases}
2\sqrt{d/a},&d\leq v^{2}/a,\\
d/v+v/a,&d>v^{2}/a.
\end{cases}
\]

The first case never reaches maximum speed; the second does. The boundary follows because acceleration and braking each require distance \(v^{2}/(2a)\). **Check the source equation before implementing it:** the text extraction of Rosi et al. prints \(v^{2}/(2a)\) as the profile boundary, which is the distance for *one* acceleration leg, not the full start–stop movement. The two stated time expressions meet at \(d=v^{2}/a\). (rosi2016simulationbasedperformanceanalysis pages 3-6, rosi2016simulationbasedperformanceanalysis pages 6-10)

Let *z* be access-opening height, and let independently requested old and new trays occupy heights *X* and *Y*. For a steady-state **dual-command machine cycle**—return the just-picked tray, travel between storage locations, then fetch and present the next tray—a useful explicit model is

\[
T_{\rm DC}(X,Y)=t(|z-X|)+t(|X-Y|)+t(|Y-z|)+4t_{\rm transfer}.
\]

Here the four transfers represent taking/placing the old and new trays; any door, identification or control delays must be added separately. Average over actual tray heights and request/slotting probabilities, rather than assuming that every trip spans the full machine height *H*. Under a simplified uniform distribution with an opening at the bottom, mean geometric travel distances are \(H/2\), \(H/3\) and \(H/2\), respectively. One must average **\(t(d)\)**, not apply \(t\) to those mean distances, when acceleration matters. Rosi et al.’s three-zone model accounts for a non-bottom opening and writes its single-tray system time as picking time plus four transfer times and the three travel components, with theoretical delivered-tray rate \(3600/E[T]\). These are steady-state rates: the first and final operations of a finite batch need separate single-command treatment. (rosi2016simulationbasedperformanceanalysis pages 6-10, đukic2021singletrayvlmvsa pages 1-2, đukic2021singletrayvlmvsa pages 2-3)

For **one opening**, lift work and human work are predominantly sequential: \(T_{\rm single}\approx E[T_{\rm DC}]+p\), where *p* is time spent picking and confirming work on the presented tray. For a **two-level opening**, the lift can exchange trays at one position while the picker works at the other; the approximate lower bound becomes \(T_{\rm dual}\gtrsim\max(E[T_{\rm DC}],p)\), plus switching and blocking delays. Thus a dual opening hides, rather than eliminates, machine travel. Đukić and colleagues model the variability of both activities; their calculated improvement is largest when picker and lift cycle times are comparable, not invariably a factor of two. A double extractor, a next-tray buffer and a second independent lift are **different architectures** from simply providing two pick levels. (dukic2019influenceofpicka pages 2-3, vanhauwermeiren2021pickcapacitymodel pages 2-4, đukic2021singletrayvlmvsa pages 1-2)

## What the rates actually measure

Rosi et al.’s single-opening simulation covers **2.8–5.4 m** machine heights, five lift profiles from **1.0 m/s, 0.5 m/s²** to **2.0 m/s, 2.0 m/s²**, and **5, 15 or 30 seconds of picker time per tray**. Its Table III reports **62–145 delivered trays/hour**, depending on configuration—not 62–145 order lines/hour. For its 5.4 m machine, the slowest profile yields **110, 84 and 62 trays/hour** at 5, 15 and 30 seconds of picking; the fastest yields **134, 98 and 69**. For the 2.8 m machine under the fastest profile, the respective results are **145, 103 and 72 trays/hour**. The cropped original table provides the numerical comparison. Faster lift motion and shorter height matter most when picking is quick; longer human work absorbs much of the motion-time difference. (rosi2016simulationbasedperformanceanalysis pages 6-10, rosi2016simulationbasedperformanceanalysis media 8e8de338)

For a two-level opening, a later direct model comparison by Đukić et al. (2021) reports a **63.57%–88.55% throughput advantage** over its single-level comparator in the illustrated **6 m-high, 1 m/s** configuration for the pick-time cases shown near the machine-cycle range. The advantage falls for much shorter or longer picking times. This is a **case-specific modeled percentage**, not a universal dual-tray multiplier or a measured absolute dual-tray tray/hour rate. In a separate dual-tray study, modeled **machine-plus-fixed** times range from **27.29 seconds** at 4.5 m and 1.5 m/s to **45.40 seconds** at 9 m and 0.5 m/s under its assumptions; those times alone must not be converted into completed-line throughput, because the picker can overlap machine work and picking-time distributions affect waiting. (dukic2019influenceofpicka pages 2-3, đukic2021singletrayvlmvsa pages 3-5, đukic2021singletrayvlmvs pages 3-5)

A tray may serve **several SKUs or several orders** in a batch. Conversely, one order may require several trays. Convert the forecast tray rate into line rate using the expected **distinct useful lines completed per tray visit**, measured under the proposed slotting, batching, replenishment and order mix. Vanhauwermeiren et al. (2021) emphasize precisely this difference between tray-delivery capacity and actual pick capacity, and compare single bay, double bay, double extractor, buffer and independent two-lift architectures. Published secondary claims of **125–350 items/hour** for “standard VLMs” are item/pick claims, not evidence that any one opening delivers 125–350 *different trays* each hour. (vanhauwermeiren2021pickcapacitymodel pages 2-4, vanhauwermeiren2021pickcapacitymodel pages 4-5, munoz2025taxonomicclassificationand pages 39-43)

## When the investment pays

**There is no defensible universal minimum SKU count, picks-per-SKU cutoff or floor-price threshold.** SKU count determines required tray sectors and capacity; pick frequency determines whether travel savings keep the machine occupied and whether its opening is sufficient. Two warehouses with the same SKU count may therefore reach opposite decisions. The published carton-rack versus dual-tray VLM economic work considers storage volume, throughput, labor hours and wages, floor-space cost and equipment cost. The accessible review reports that conventional racks win at **low VLM utilization**, potentially including a machine used for only one shift daily, while expensive floor area can favor the VLM. It does not supply a verified numerical SKU, frequency or currency-per-square-metre break-even value. (munoz2025taxonomicclassificationand pages 48-51, munoz2025taxonomicclassificationandc pages 73-76)

A transparent screening calculation is to annualize each option on the **same forecast workload**:

\[
\Delta C=\Delta C_{\rm capital+maintenance+energy+software}
 +c_A(A_{\rm VLM}-A_{\rm shelves})
 +c_L(L_{\rm VLM}-L_{\rm shelves}),
\]

where \(c_A\) is annual effective cost per unit of usable floor area and \(c_L\) is fully burdened annual labor cost. Include replenishment, order consolidation, exceptions, maintenance downtime and any retained manual overflow in *L*, rather than counting only time at the pick window. A VLM is economical when \(\Delta C<0\) **and** its modeled opening capacity meets peak demand with an adequate queueing margin. If \(A_{\rm shelves}>A_{\rm VLM}\), an equivalent floor-cost threshold is

\[
c_A>\frac{\Delta C_{\rm capital+maintenance+energy+software}
+c_L(L_{\rm VLM}-L_{\rm shelves})}{A_{\rm shelves}-A_{\rm VLM}}.
\]

These are **decision-accounting equations**, not numerical thresholds reported by Calzavara et al. Their inputs must be established for the facility. High SKU variety in compact parts, substantial walking in the shelving layout, scarce/expensive floor area, valuable controlled inventory and sustained work across shifts strengthen the case for a VLM. A small conveniently located assortment, low request volume, cheap abundant floor area, bulky or awkward loads, frequent unplanned direct access, or peak demand exceeding one opening’s capacity weaken it. High-frequency items can also justify a separate forward-pick shelf rather than consuming VLM cycles; batching can change that choice. (vanhauwermeiren2021pickcapacitymodel pages 4-5, đukic2021singletrayvlmvsa pages 2-3, munoz2025taxonomicclassificationand pages 48-51, novara2020anewdecision pages 44-47)

## Choosing among technologies

The following is an **application comparison**, not a ranking by purportedly interchangeable “picks/hour” figures. It distinguishes a machine’s mechanical constraint from the flexibility of adding stations or vehicles. (azadeh2019robotizedandautomated pages 5-8, novara2020anewdecision pages 44-47)

| System | Movement / bottleneck | Best fit | Principal downside |
|---|---|---|---|
| Manual static shelving | Person-to-goods; picker walking, searching, reaching, and congestion dominate. | Low utilization, low capital budget, changing assortment, or operations where automation cannot be kept busy. | Labor- and travel-intensive; weaker density and ergonomics than goods-to-person systems. |
| Single-level VLM | One lift presents one tray at one opening; lift travel and picking are largely sequential. Rosi et al.’s modeled cases produced **62–145 trays/h** with 5–30 s pick times—**not lines/h**. | Small/medium items, many slow movers, valuable or controlled stock, and expensive floor space where vertical density matters. | One lift/opening is a throughput bottleneck; high capital and maintenance burden when utilization is low. (rosi2016simulationbasedperformanceanalysis pages 6-10, rosi2016simulationbasedperformanceanalysis media 8e8de338) |
| Two-level dual-tray VLM | One lift alternates between two vertically separated presentation levels, preparing one tray while the operator picks from the other; performance is governed by the slower of human picking and machine service. | Repetitive goods-to-person work where pick time is near the lift’s dual-command cycle, allowing effective overlap. | Not twice as fast universally: for the illustrative **6 m, 1 m/s** case, the reported advantage was **63.57–88.55%** near the modeled cycle-time range and fell at extreme pick times. (đukic2021singletrayvlmvs pages 3-5, vanhauwermeiren2021pickcapacitymodel pages 2-4) |
| Horizontal carousels | An entire horizontal loop rotates inventory to the picker; pods can let one unit move while another is picked. Rotation, picker work, and pod coordination constrain output. | High-activity small-item picking with batching and enough horizontal floor area; pods can keep a picker supplied. | Large horizontal footprint and limited vertical-space exploitation; moving the whole loop adds inertia and creates a shared mechanical bottleneck. |
| Mini-load crane AS/RS | A fixed aisle crane moves cartons or totes horizontally and vertically; crane, transfer point, and conveyor capacity constrain each aisle. | Large tote/carton inventories, high racks, buffering, and stable high-volume operations requiring dense storage. | High fixed investment and limited incremental scalability: additional throughput generally requires another crane/aisle or major equipment. (munoz2025taxonomicclassificationandf pages 30-35, azadeh2019robotizedandautomated pages 8-12) |
| Shuttle tote AS/RS | Multiple shuttles work in parallel within rack tiers; shared lifts and input/output stations connect tiers and can become bottlenecks. | High-turnover tote inventory, short order cycles, and operations needing higher parallelism than a single-crane system. | More complex controls and interfaces; lift, station, and aisle congestion can cap gains from adding shuttles. (munoz2025taxonomicclassificationand pages 55-58, munoz2025taxonomicclassificationandd pages 30-35, azadeh2019robotizedandautomated pages 8-12) |
| Rack-carrying AMRs | Independent robots bring movable racks to stations; capacity scales by adding robots and stations until traffic, charging, or station queues bind. | Variable or growing demand, rapid deployment, reconfigurable layouts, and operations valuing modular expansion. | Lower storage density than fixed high-bay systems and growing congestion/coordination complexity as the fleet expands. (azadeh2019robotizedandautomated pages 5-8, azadeh2019robotizedandautomated pages 8-12) |


*Table: Comparison of movement logic, best-fit conditions, and principal limitations across manual shelving and major goods-to-person technologies. VLM figures are explicitly identified as modeled trays per hour or case-specific improvements, not universal line-picking rates.*

A horizontal-carousel **pod** can let one carousel position stock while the operator picks from another; it is an alternative when horizontal floor length, rather than usable building height, is available. Mini-load cranes serve cartons/totes across rack aisles and suit larger, stable, integrated storage systems; an aisle’s crane and interfaces are shared resources. Shuttle systems distribute transport among vehicles but must still size shared lifts and stations. Rack-carrying AMRs move shelving to pickers and permit incremental fleet deployment, although traffic and station queues must be modeled. Manual shelving remains a serious baseline rather than an obsolete comparator: if pick density is high and walking is already short, replacing walking with machinery may save little. Travel-time equations alone cannot capture parallel-resource queues; queuing or discrete-event simulation is appropriate for peak throughput and waiting-time verification. (vanhauwermeiren2021pickcapacitymodel pages 2-4, azadeh2019robotizedandautomated pages 5-8, azadeh2019robotizedandautomated pages 8-12, novara2020anewdecision pages 44-47)

**Practical conclusion.** Specify *H*, opening height, *v*, *a*, transfer time, tray layout, empirical pick-time distribution and peak request sequence; estimate steady-state dual-command travel, then simulate picker–machine overlap and queueing. Finally compare **annualized cost per completed line at required service level**, alongside space, ergonomics and resilience. The accessible original modeling supports concrete single-opening rates and a conditional dual-opening benefit, but not a universal SKU or real-estate-price threshold. (rosi2016simulationbasedperformanceanalysis pages 6-10, dukic2019influenceofpicka pages 2-3, rosi2016simulationbasedperformanceanalysis media 8e8de338, munoz2025taxonomicclassificationand pages 48-51, azadeh2019robotizedandautomated pages 5-8)

References

1. (đukic2021singletrayvlmvsa pages 1-2): G Đukić, T Opetuk, B Gajšek, and T Lerher. Single-tray vlm vs dual-tray vlm: quantitative throughput comparison. Unknown journal, 2021.

2. (munoz2025taxonomicclassificationand pages 39-43): AA Alvaro Munoz. Taxonomic classification and decision support system for vertical lift modules: a systemic and systematic approach. Unknown journal, 2025.

3. (azadeh2019robotizedandautomated pages 5-8): Kaveh Azadeh, René De Koster, and Debjit Roy. Robotized and automated warehouse systems: review and recent developments. Transportation Science, 53:917-945, Jul 2019. URL: https://doi.org/10.1287/trsc.2018.0873, doi:10.1287/trsc.2018.0873. This article has 871 citations and is from a domain leading peer-reviewed journal.

4. (rosi2016simulationbasedperformanceanalysis pages 3-6): Bojan Rosi, L. Grašič, Goran Đukić, Tihomir Opetuk, and T. Lerher. Simulation-based performance analysis of automated single-tray vertical lift module. International Journal of Simulation Modelling, 15:97-108, Mar 2016. URL: https://doi.org/10.2507/ijsimm15(1)8.328, doi:10.2507/ijsimm15(1)8.328. This article has 50 citations.

5. (đukic2021singletrayvlmvsa pages 2-3): G Đukić, T Opetuk, B Gajšek, and T Lerher. Single-tray vlm vs dual-tray vlm: quantitative throughput comparison. Unknown journal, 2021.

6. (munoz2025taxonomicclassificationand pages 48-51): AA Alvaro Munoz. Taxonomic classification and decision support system for vertical lift modules: a systemic and systematic approach. Unknown journal, 2025.

7. (rosi2016simulationbasedperformanceanalysis pages 6-10): Bojan Rosi, L. Grašič, Goran Đukić, Tihomir Opetuk, and T. Lerher. Simulation-based performance analysis of automated single-tray vertical lift module. International Journal of Simulation Modelling, 15:97-108, Mar 2016. URL: https://doi.org/10.2507/ijsimm15(1)8.328, doi:10.2507/ijsimm15(1)8.328. This article has 50 citations.

8. (dukic2019influenceofpicka pages 2-3): G Dukic, T Opetuk, H Cajner, and B Gajsek. Influence of pick time distribution on expected throughput of dual-tray vlms. Unknown journal, 2019.

9. (vanhauwermeiren2021pickcapacitymodel pages 2-4): Pieter Vanhauwermeiren, Marc Juwet, and Eric Demeester. Pick capacity model for cutting machine tools stored in a next generation vertical storage machine. Procedia Manufacturing, 55:479-486, Jan 2021. URL: https://doi.org/10.1016/j.promfg.2021.10.065, doi:10.1016/j.promfg.2021.10.065. This article has 3 citations and is from a peer-reviewed journal.

10. (rosi2016simulationbasedperformanceanalysis media 8e8de338): Bojan Rosi, L. Grašič, Goran Đukić, Tihomir Opetuk, and T. Lerher. Simulation-based performance analysis of automated single-tray vertical lift module. International Journal of Simulation Modelling, 15:97-108, Mar 2016. URL: https://doi.org/10.2507/ijsimm15(1)8.328, doi:10.2507/ijsimm15(1)8.328. This article has 50 citations.

11. (đukic2021singletrayvlmvsa pages 3-5): G Đukić, T Opetuk, B Gajšek, and T Lerher. Single-tray vlm vs dual-tray vlm: quantitative throughput comparison. Unknown journal, 2021.

12. (đukic2021singletrayvlmvs pages 3-5): G Đukić, T Opetuk, B Gajšek, and T Lerher. Single-tray vlm vs dual-tray vlm: quantitative throughput comparison. Unknown journal, 2021.

13. (vanhauwermeiren2021pickcapacitymodel pages 4-5): Pieter Vanhauwermeiren, Marc Juwet, and Eric Demeester. Pick capacity model for cutting machine tools stored in a next generation vertical storage machine. Procedia Manufacturing, 55:479-486, Jan 2021. URL: https://doi.org/10.1016/j.promfg.2021.10.065, doi:10.1016/j.promfg.2021.10.065. This article has 3 citations and is from a peer-reviewed journal.

14. (munoz2025taxonomicclassificationandc pages 73-76): AA Alvaro Munoz. Taxonomic classification and decision support system for vertical lift modules: a systemic and systematic approach. Unknown journal, 2025.

15. (novara2020anewdecision pages 44-47): V Novara. A new decision making tool for automated industrial storage systems selection. Unknown journal, 2020.

16. (munoz2025taxonomicclassificationandf pages 30-35): AA Alvaro Munoz. Taxonomic classification and decision support system for vertical lift modules: a systemic and systematic approach. Unknown journal, 2025.

17. (azadeh2019robotizedandautomated pages 8-12): Kaveh Azadeh, René De Koster, and Debjit Roy. Robotized and automated warehouse systems: review and recent developments. Transportation Science, 53:917-945, Jul 2019. URL: https://doi.org/10.1287/trsc.2018.0873, doi:10.1287/trsc.2018.0873. This article has 871 citations and is from a domain leading peer-reviewed journal.

18. (munoz2025taxonomicclassificationand pages 55-58): AA Alvaro Munoz. Taxonomic classification and decision support system for vertical lift modules: a systemic and systematic approach. Unknown journal, 2025.

19. (munoz2025taxonomicclassificationandd pages 30-35): AA Alvaro Munoz. Taxonomic classification and decision support system for vertical lift modules: a systemic and systematic approach. Unknown journal, 2025.
