* **Most instruments and lab tools have a real used market in North America, at a fraction of the twin's new
  prices.** Benchtop SEMs, XRF, laser diffraction, micro-Vickers, the Keyence microscope, prep machines, furnaces, sieve
  shakers, gloveboxes, fume hoods, ICP-MS, tensile frames and wire EDMs all had several listings that fit, most of them
  priced. Delivered (asking price plus freight and rigging), the median `price_frac` across the stations with a real
  market is {pf_med} (round 5 assumed 0.45 for every station), from {pf_min} to {pf_max}. The twin's own models are dearer than
  that median: an Agilent 7800 or 7850 ICP-MS is $67-100k refurbished with a warranty against about $190k new, a 2014
  Haas ST-10 $24,900 against $64,995 new, a 2021-2024 FANUC ROBOCUT α-C400iC about €89,000 in Europe against $230k.
* **The automation and the printers are a different story.** No used Plastometrex PIP, AMAZEMET rePowder, InssTek
  MX-Lab or Aconity MIDI was listed anywhere. Used LPBF machines are common (EOS M 270/280/290, SLM 125/280, Concept
  Laser M2 and Mlab, TruPrint 1000; {midi_n} listings, {midi_na} in North America), but none is the twin's open research
  machine, and each needs its maker's recommissioning and a licence transfer, so `midi` is priced on like-for-like
  listings only and stays new. Kardex Shuttle XP 500s are plentiful in Europe, almost absent in the US, and their prices
  are on request; `shuttle` stays new too. UR cobot arms and MiR AMRs do have a market ({arm_n} UR arms and {mir_n} MiRs
  listed), which makes the robot units part-used.
* **Used saves little time where new is quick.** The Haas ST-10 is in stock new (16 available, one week), the Carvera
  ships in seven business days and UR cobots in one to four weeks. Where the twin's new leads are long (8-16 weeks for
  instruments, 18 for the EDM), a domestic used unit is on site about {lead_med} weeks after the purchase order, and working
  {saved_med} weeks sooner than new (median over the stations with a real market; `order_to_working_used_w` against
  `order_to_working_new_w`, before the facility window).
* **The fault risk is about round 5's.** With the listings' mix of conditions, `p_fault` has a median of {pfa_med} (round 5:
  0.25): lower where refurbished units with a warranty are common (SEM, ICP-MS), higher at government and university
  auctions (sold as-is) and for stations bought as several used machines (prep, the doser, the robot units), any one of
  which can arrive faulty. A lab that buys the best-condition unit near the median price gets {pfb_med} (`p_fault_best`).
* **`USED_OK` changes.** {lost_txt} {gained_txt}
* **Where the market can't say:** eBay (blocked) and closed auctions would have given sale prices; these are asking
  prices. Several stations have only a handful of priced listings (`n_priced` in `summary.csv`), and the fault rates per
  condition are assumptions.
