# rePowder BYU installation details — 2026-09-17 call

- **When:** Thursday 2026-09-17, 08:00–08:57 MDT (56 min)
- **Who:** Bartosz Kalicki (AMAZEMET), Dave Laws (BYU), Gage Erickson, Sterling Baird
- **Source:** Tactiq voice-to-text ([original](https://app.tactiq.io/api/2/u/m/r/cCdF7Qvts5v2gaqYv9ED?o=txt), raw copy in [`tactiq-raw.txt`](tactiq-raw.txt)). The transcript below is corrected for intent: mis-heard words fixed, stutters and filler turns dropped, timestamps kept. Corrections that change a number or a part are listed first so they can be checked against the raw file.

## Corrections worth knowing about

| Raw transcript said | Should be | Why |
| --- | --- | --- |
| "optimizer" | atomizer | throughout |
| "Bartos / bartaj / bhartosh" | Bartosz | pronounced "BAR-tosh" |
| "Liv" (23:28) | Dave | |
| "plaque / plag" | plug | 32 A male plugs on both the atomizer and the chiller |
| "the atomizer takes up to 60" A (07:41) | most likely **16 A** | the point being made is that one 32 A feed is "easily enough for both" the atomizer and the chiller; 60 A would contradict that. Verify with Bartosz. |
| "30 mm hose" (08:11, 08:56, 09:09) | **13 mm = 1/2"** | Bartosz then says "the best will be to use 1/2 inch hoses… we will use the 13 mm connections", and "on my side it was already fitted to half inch". The Tactiq summary's "30 mm / ~3/4 inch" is wrong. |
| "large 25 mm hose" | 25 mm = 1" | the standard (unmodified) heat-exchanger connection; ours was changed to 1/2" |
| "6 per 4 mm" / "22646 per 4mm" | 6/4 mm tubing (6 mm OD, 4 mm ID); two 6/4 mm ports on the back | compressed air and argon both use 6/4 mm push-fit |
| "AT" / "an extra tea" | a T-piece / an extra T | for the argon line |
| "nomadic systems" | pneumatic systems | why 8 bar is needed |
| "set to free bars" | set to three bars | welding regulators are fixed-pressure, flow-only |
| "five N" | 5N = 99.999 % argon | 4.5N usable, but not for Al/Mg |
| "as long as there's not octane" (12:59) | as long as there's no oxygen | |
| "ceiling rod" | sealing (stopper) rod in the crucible | |
| "1212 centimeters" / "1011 centimeters" | 12 cm / 10–11 cm | crucible height |
| "ALS I10MG" | AlSi10Mg | |
| "Valent / Valmet / valenet" | Valimet | Al powder producer; a quote request is already in with them (#161) |
| "plasmark" (34:12) | plasma arc | arc melting |
| "Teen and low melting" | tin and low-melting-point | |
| "induction year" (26:54) | induction unit | training day 1 |
| "fairness" | furnace | |
| "stickers on the floor" | tacky (sticky) mats | at the enclosure exit |
| "error gradient" | AirGradient | #219 |
| "death certificate" (25:36) | desiccant | |
| "Prunus" (43:41) | furnace | |
| "Yeah, it's lower than aluminum" (43:53, Sterling on copper) | **wrong as spoken**: copper melts at 1085 °C, aluminum at 660 °C | Sterling misspoke; the induction unit's ceiling (~1400–1500 °C, see #161) still covers Cu, not stainless |
| "2028" (00:42) | the 28th | |

Tactiq's own "Detailed summary" at the top of the raw file cites timestamps ~22 min later than the transcript's and carries the 30 mm and 60 A errors. Use the summary below instead.

## Summary

**Dates.** Bartosz confirmed **Mon Sep 28** for installation (arriving Saturday to rest), with **Tue Sep 29 – Wed Sep 30** for training. He may need to add a visit elsewhere in the US on the way home (Thu/Fri), which is why he wants the 28th and not later. Install itself is 2–3 h (place, connect power / coolant / air / argon, basic tests, heat-up and coolant-flow check, unpack consumables), then theory. Training: one day is the induction unit ("the necessary parts"), the other is flexible for whatever we want to try. He's flexible on hours and will split the day around Gage's Monday classes (Gage is free ~1–4 pm Monday, all day Tue–Wed; Sterling teaches at noon MWF).

**Site.** Enclosure, dehumidifier, and exhaust ductwork are in; electrical and chilled-water drops are on the wall inside the enclosure; transformer sits next to the room. Bartosz's one addition: tacky mats at the enclosure exit so powder on shoes stays on the mat.

**Power.** Both the atomizer and the chiller ship with 32 A male plugs. Options are a matching female receptacle or hardwiring. Bartosz recommends hardwiring: it's what most customers do, plugs are expensive in the US because of certification, and some states (NY) require it for permanent installs. Our unit was modified so the heat exchanger plugs into the back of the atomizer and there is one power connection for the whole thing; the atomizer draws ~16 A (see corrections) so the one feed covers both. Regardless of plug vs hardwire, Bartosz will **meter the outlet first** (400 V and 230 V present, phase order) before anything is connected, since European wire colours differ.

**Chilled water.** Heat exchanger ↔ atomizer: 1/2" (13 mm) supply and return, **hose included** with the system (it was in a separate package). Facility ↔ heat exchanger: **1"** in and out. We need 1" hose plus adapters from whatever the wall drops are (Dave: probably 3/4" SAE threads) to 1". No garden hose. Unwrap the heat exchanger to confirm which fittings are on it; if the 1/2" adapters aren't there Bartosz brings them. Barry for hoses; Dave will act as runner for parts (Home Depot / Ace is fine for small stuff).

**Compressed air.** 6/4 mm tubing, push-fit, into the back of the atomizer; tubing included. We need the right push fitting on our regulator (Kevin has them).

**Argon.** Bartosz uses **5N (99.999 %)**; 4.5N works for some materials but for Al/Mg go as low-oxygen as possible. Gage had already asked Nick for argon (arriving in a day or two) and will re-confirm the grade. The machine needs **8 bar** for its pneumatics, so the regulator must be an **adjustable 0–10 bar** type, not a welding regulator (fixed ~3 bar, flow-only). We don't have one yet; ask Nick. Also need the regulator-to-6/4 mm adapter. There are two 6/4 mm ports on the back (one pressurizes the furnace, one goes to the valve that fills the chamber) joined by a T; Bartosz will bring a spare T.

**Machine details.** Crucible: max feedstock diameter **20 mm** (gap between the sealing rod and the crucible wall), inner height **~10–12 cm**; material may stand a little proud but must not overfill once molten. It is possible to run without the sealing rod for awkward feedstock, after discussion. Melting can be started with the furnace open, but the locking bolt only engages once the furnace is closed and pressurized, and there's no reason to unless the research needs it. A flap option allows opening mid-run to add material, but only for materials that don't oxidize easily (Au, Ag, Cu); for Al it affects the flow. Bartosz supplied Al 4047 benchmark rods (plus extras); a trial run is ~1 h. Copper needs longer heat-up/cool-down; tin and other low-melting metals go too quickly to be a good demo.

**Powder in the crucible.** Loose powder often does not fully melt: each particle stays discrete and sintered even well above the melting point. It works if some of the charge is already molten so the particles dissolve into it. Induction gives some stirring (the melt pulses once molten) but Bartosz doesn't like relying on it; a **master alloy** is better whenever possible, and a small high-melting addition may just clump in one spot. For making master alloys from powders, an **arc melter** is the better tool (everything melts regardless of melting-point spread).

**PPE and static.** What ships with the system is the ESD coat (Bartosz calls it the anti-static apron; the #124 photo shows Portwest ESD lab coats) with a wrist strap; he's bringing one more. Gloves plus the coat is what they use. A real discharge event needs visible powder suspended in air, so this is precaution, not a routine hazard.

**Storage / glovebox.** Most AMAZEMET customers don't use a glovebox; a clean handling area is enough. Store powder in proper sealed containers (not a plastic tub) with silica-gel packets, or it clumps and oxidizes over time. They use a glovebox only when packing samples to ship, then vacuum-bag; well-passivated powder tolerates a little air. Sterling still wants to look at an enclosure-style box up to ~$4–5k, and wants a check that silica gel can't contaminate the powders it's stored with.

**First experiments (Sterling/Gage after Bartosz left).**
1. Atomize a solid high-purity Al rod.
2. Same rod bored ~3" deep, packed with powder (other elements), capped with a press-fit Al plug so the powder is compacted; try to get a full melt. Bartosz: fine as long as it isn't pure loose powder in the crucible.
3. If (2) doesn't fully melt: compact harder (hydraulic / vacuum press, possibly heated, so particles bond without melting; #104), or arc-melt a master alloy first at the University of Utah (Taylor Sparks) and bring it back. Ideal: have an arc-melted AlSi10Mg (from the powder we already have) ready to atomize while Bartosz is here, then compare against commercial Valimet AlSi10Mg. Scandium is too far out to be part of this.

**Other.** The 2 kg Valimet Al powder quote is still pending (they wanted paperwork signed). Stainless powder on hand can't be melted in this unit; realistically Al and Cu are what the induction furnace handles. Gage floated a visit (or first a call plus a pre-recorded workflow video) to an aluminum powder producer such as Valimet to sanity-check our handling and safety procedures; lab-funded, car rental for 3–5 people or flights for 1–2, revisit in ~a month.

## Action items

| Who | What |
| --- | --- |
| Gage | Re-confirm 5N argon with Nick; get an adjustable 0–10 bar regulator (8 bar needed) and the regulator → 6/4 mm adapter |
| Gage + Dave/Barry | 1" hose + adapters from the wall drops to the heat exchanger; confirm the 1/2" hose and fittings that shipped with the system |
| Gage + Kevin | Push fitting for 6/4 mm on the compressed-air regulator |
| Gage + Barry | Get the dehumidifier running before the 28th to find steady-state RH |
| Gage | Find and order the highest-purity Al rod available (McMaster first, then others; use the Pi via a claude ping): 20 mm OD, plus a smaller diameter that press-fits the bore |
| Gage | Email Taylor Sparks (cc Sterling) about arc-melting AlSi10Mg powder before ~Sep 28–29, and whether a student could help |
| Gage | Claude ping on whether silica-gel desiccant can contaminate stored powders |
| Sterling | Order an AirGradient for inside the enclosure (#219); keep looking at a ~$4–5k glovebox/enclosure option |
| Dave | Runner for parts on install day; on site the 28th |
| Bartosz | Meter the outlet before connecting; bring spare T (and 1/2" adapters if missing); add BYU to AMAZEMET's video/doc database; install + 2 days training; extra ESD coat |
| Sterling/Gage | Record the install for internal use; watch AMAZEMET videos before Tuesday training |

## Transcript (corrected)

00:07 Sterling: Good to put a face to the name, Bartosz. Thanks for all your help so far getting this going.
00:21 Bartosz: No problem. At this point I can confirm we'll go with the 28th. I'm checking whether I'll have to squeeze in a visit to New York on the Thursday/Friday, depending on what they can do. The 28th there would be too soon, so I'll go to Salt Lake City first.
00:57 Dave: Is Gage joining us, Sterling?
00:59 Sterling: Just messaged him; he's typing back, so I'm guessing yes. Thanks to Dave and Gage and many others, all renovations are done, everything that needs to happen for the atomizer, if I'm correct there, Dave.
01:47 Dave: Yeah. I apologize for how long this has taken, Bartosz. We were hoping to get it done quickly, but we're at the mercy of the people here on campus and can only push so hard. Sorry about the delay.
02:08 Bartosz: I fully understand. We had one more system shipped around the same time, and that installation now looks like December because of how much work is needed and they keep pushing it. It all happens. Waiting on electrical work is always a nightmare. That's why we usually go with the transformer supplier we normally use: they deliver within a week, always have stock, and the quality for the money is good. But in general it always takes a long time.
03:03 Bartosz: So in this case I understand we have power for the atomizer, for the induction module, and power for the chiller. The question is: do you want to hardwire it, or do you already have plugs? What's the plan?
03:22 Dave: Right now the main power for the machine actually has a plug. We can make sure we have the correct mating plug for the machine, or we could hardwire it.
03:45 Bartosz: Both the chiller and the atomizer come with a 32 A male plug already. You can either go with the female plug as a direct connection or something on the wall, but honestly hardwiring is the most common. It saves money: here I get the plug for $30–40; in the States they sell for hundreds because of extra certification. Most people just hardwire directly, and in some states like New York it's the law that if the system is permanent it has to be hardwired. That's what I'd recommend.
04:37 Dave: Gage, since you're down there, could you point your camera at the electrical we have set up for it and show the chiller drops? Then Bartosz can comment on what he thinks we should do.
05:02 Gage: Sure, let me join from my phone and walk over.
05:10 Bartosz: In terms of power, the only thing is, depending on your regulations, whether we'll need to swap the phases.
05:26 Dave: Gage, when you get on your phone, pan around and give him an overall mental picture of what he'll be doing.
06:29 Dave: Bartosz, to bring you up to speed: in the space we have, we actually constructed an enclosure within the room.
06:55 Gage: Here's the atomizer, still draped in the wrapping. Here's the chilled water supply and return, this is the compressed air, and here's our electrical down at the bottom.
07:19 Bartosz: OK, so you have the plug directly on the wall. Perfect. Now I remember we did the modification for you to make it easier: you have the heat exchanger, and you have the additional plug on the back for it, so there is one connection for the whole atomizer. That's fine, because the atomizer takes up to about 16 A by itself, so the plug is easily enough for both. Then we'll use that chilled water. It's always about the small details, for example what kind of hose can we connect to the chilled water right now. With the heat exchanger the standard is a pretty large connection, but I think yours was changed to the smaller one, the 13 mm hose.
08:18 Dave: That's something we need to look at, Gage. These are going to be SAE standards, probably 3/4" threads, so we'll make sure we have the appropriate adapters to hook the chilled water to the heat exchanger.
08:42 Bartosz: The heat exchanger should already have the connectors. You can unwrap it and look at the outlets that are there now. If something is missing I can just bring it with me. It should have both options: the large 25 mm hose we normally use and the smaller 13 mm. It's probably set for 13 mm; if not we do the swap, and that's on me. The best will probably be to use 1/2" hoses for everything. We'll use the 13 mm connections; it'll fit well on both ends.
09:30 Dave: Gage, we need to make sure we've got hoses. We'll need to chat with Barry.
09:47 Bartosz: Check how much was supplied with the atomizer itself; there should already be some extra hose in there. Worst case, if small parts are needed, which can be a nightmare on your end, I'll drive to Ace Hardware or Home Depot and get them.
10:07 Dave: We can help with that too; we have pretty good supply here at BYU. My plan for being there is to be a runner for you, to get all the things we need for hookups. As far as hoses go, do we need high-quality industrial hose? I don't feel like we should put garden hose on there, for example.
10:43 Bartosz: No, definitely not garden hose. OK, I see what it is now. We'll need to hook the facility up to the main coolant in and out, and that's 1", so we'll probably need an adapter on your side to go from whatever size you have to 1", and put 1" hose in between. There's nothing there right now. On my side it's already fitted to 1/2", the same size as on the induction module, and that hose should be included with the system. The fitting that was empty was in another package.
11:32 Dave: So that hose is intended for the coolant loop.
11:34 Bartosz: Yes, the smaller one, the 1/2", goes between the exchanger and the atomizer as supply and return. So it seems all we need is a bit of 1" hose to connect the heat exchanger to the facility.
11:48 Dave: We'll make sure we have stuff for that.
12:05 Bartosz: OK, so coolant is fine.
12:06 Dave: And then the compressed-air line is right there on the wall next to the heat-exchanger lines.
12:16 Bartosz: Same thing: just make sure we can connect the 6 mm line directly to the back of the atomizer. The 6/4 mm tubing is already included; it's just making sure you have the right connector, otherwise it's a nightmare to get. You can even get those on Amazon if needed.
12:42 Dave: Gage, I think we need to chat with Kevin. Kevin's got all the push fittings we need for the compressed air.
12:49 Gage: Perfect. I talked to Nick about getting argon; that should be coming in tomorrow or the next day. Although, Bartosz, we had an option between 100 % argon and research-grade argon. Does it matter, as long as there's no oxygen?
13:12 Bartosz: We usually use 5N, 99.999 %. But it depends on the material. Even with many purges we can only reach a certain oxygen level, which depends on the purity of the argon you have. Even 4.5N is still usable, depending on the material. For aluminum and magnesium we definitely want as little oxygen as possible. If you wanted to process copper it wouldn't be such an issue.
13:50 Sterling: So probably we do 5N, given the aluminum.
13:55 Gage: Then I'll check with Nick again about the purity of the argon we ordered.
14:05 Dave: Gage, while you're there, flip your phone again and show Bartosz the transformer; maybe step up the ladder and show what's on top. There's our transformer location, next to the room.
14:25 Bartosz: As long as it gives us the 400 V and 230 V, we're fine. What's important is that when I get on site I'll first measure the voltage at the plug before we connect everything, just to make sure nothing was swapped, because we use slightly different colours.
14:50 Dave: And this is up on top: the dehumidifier and all the ductwork. This isn't specific to you, it's so we can do proper exhaust in that room for everything we're doing inside.
15:07 Bartosz: For work with powder, that's definitely recommended: to have it slightly enclosed. Powder always tends to move around. My only recommendation: if you know where the exit from the enclosure is, put those tacky mats on the floor. When one gets dirty you peel it off and there's another underneath, so anybody leaving the room with powder on their shoes leaves it on the mat.
15:40 Gage: Good idea.
15:42 Bartosz: With such a good enclosure, that's the last recommendation I'd make. For argon, my only thing is that it has to be 8 bar. So you need to make sure the regulator is one that lets you change the pressure, for example over 0–10 bar. If you already have a regulator but it's a welding regulator, they're usually set to three bars and you can only set the flow. This system has quite a lot of pneumatic systems inside that need the higher pressure.
16:20 Sterling: That's 116 psi, I think.
16:20 Dave: Gage, do we already have the regulator for the argon?
16:31 Gage: No, I don't think so.
16:33 Sterling: Doesn't sound familiar.
16:34 Dave: That's a question to ask Nick when you ask about the argon. Let's make sure we've got a proper regulator by the time Bartosz gets here. Like he says, we can get an adjustable one; Nick will be our best source on where. Minimum of eight bar.
17:05 Bartosz: It's usually 0–10 bar. We just need to make sure we can set 8. So that covers argon. Same thing: make sure we have the right connection, the right tube from the tank to the system, so you'll probably also need to find the right adapter to put on the regulator.
17:36 Gage: Does that go directly into the atomizer?
17:40 Bartosz: Look at the back; there should be two 6/4 mm connections. This is where we connect argon, and with the parts there should be a T for it. One pressurizes the furnace itself; the other goes to a valve that lets us fill the chamber. Both are 6/4. I'll make a note to bring an extra T, just in case.
18:28 Dave: And Gage will work to make sure we have all the correct adapters to get from the argon tank to the 6 mm plastic tube.
18:46 Bartosz: All right. We have enough space, everything is planned. If everything is plug-and-play, the installation will take two hours, maybe three tops, just to set it in position, connect it, and do some basic testing, and then we can start the operation. We'll go through some theoretical training. I'll add you to our database system where you'll have access to videos on operating the system. With the system we supplied rods of aluminum 4047, which is the benchmark material we use to showcase the machine. Copper you have to wait longer for heating and cooling; tin and low-melting-point metals just go too quickly, so we usually use aluminum. I added some extra rods so we can do more trials. One trial usually takes one hour, but if you have something in mind you'd like to test together, we can plan time for it.
19:52 Sterling: Yeah, actually, Gage, we should chat about what we might want to try and get a sample ready.
20:12 Bartosz: If you open the furnace part you'll see exactly the area where we can fit the material. The maximum diameter is 20 mm. On the right you have the lock; if you move the foam out you can see the crucible. Inside is the sealing rod, and you fit the material in the space in between, so around 20 mm between the sealing rod and the edge of the crucible. In some cases it's possible to work without the sealing rod if necessary, but we'd have to discuss it. Once you have a bit of experience you can operate that way too, if you have feedstock that's hard to load otherwise, like chunks you need to just drop in.
21:13 Sterling: What height could we go to? I know the crucible dimensions.
21:21 Bartosz: 12 cm, I'd say. The material can even be slightly higher than the crucible. The inner height is around 10–11 cm, but we can go a bit higher than that. You just need to make sure it won't overfill the crucible once everything melts.
21:43 Gage: Do you only turn on the heat once this is closed, or can you start melting with it open?
21:51 Bartosz: You can start melting with it open, but there's no reason to unless it's a very specific kind of research. Once you close the furnace and change the pressure, it automatically locks: a bolt comes in and locks the furnace. If you start fully open, the bolt comes in but can't block anything. There are also options, additions to the flap, that let you open the furnace a little in the middle of an operation to place more material inside. That's fine for gold, silver, maybe copper, materials that don't oxidize so easily. Otherwise I'd avoid it; for aluminum it can affect the flow.
22:55 Dave: Looking forward to seeing you, Bartosz. I need to go to another meeting. I'll be there on the 28th to help wherever I can and make sure we facilitate a smooth transition. Thank you.
23:23 Sterling: Could you stay on for a second, Bartosz? Thank you, Dave.
23:31 Sterling: How do you pronounce your name?
23:38 Bartosz: "Bartosh."
23:40 Sterling: Two other things. Quick note for Gage: I think it would be really good to get the dehumidifier going before installation and see what our steady state is going to be. I'll also order another AirGradient monitor to install inside the enclosure. And Bartosz, one thing we've been behind on is glovebox handling of the powders. In your experience, across different places, if we went with one of the cheaper plexiglass-style gloveboxes that still has an antechamber for bringing things in and out, does that seem sufficient? I'm used to working in a battery glovebox.
24:51 Bartosz: I'd say it is. It depends what you're actually going to work with, but honestly most of the customers we work with do not operate with a glovebox. If you have an area that can be kept clean where you handle the powder, that's generally enough. Just definitely don't store it in a plastic box. Have proper containers, and it's good to put silica-gel packets in the container for storing the powder; that helps a lot. Otherwise it may clump a lot or even oxidize over time.
25:34 Sterling: So put those in the container itself.
25:40 Bartosz: Yes. We sometimes use a glovebox, but only when we pack samples we're shipping. Very often when we pack a sample we put it in a vacuum bag and keep it that way. Even if there's a little bit of air, if the powder is already well passivated it's not a problem at all.
26:17 Gage: Bartosz, you said on the 28th you'll do the installation, two or three hours. How many hours of training is there after that?
26:24 Bartosz: We can still work that first day on the theoretical side and general work, and then for two more days, full hours, I'll be with you and we'll handle the training. Once I'm done with my part we can do whatever you'd like to work on. Usually the training is one day for the induction unit, so one day will be the necessary parts and one day can be more flexible.
26:54 Gage: Do you have an hourly schedule yet for the 28th, what time you plan on being here?
27:17 Bartosz: I don't have my flight yet, but I'll probably arrive a little earlier, maybe on Saturday, to have a bit of rest, and then we can start early. Whatever time is comfortable for you we can start, and same for when we finish. No problem.
27:45 Gage: I've got classes for the majority of the day on Monday, so there'd be maybe two or three hours I could be there, intermittently. I won't be available for most of that day.
28:07 Bartosz: That's OK. Most of the work will be done in the next two days. If I know the schedule we can plan the day: do the installation, take a longer break, and even meet in the afternoon. I'm really flexible on that. Whatever schedule is comfortable on those three days, I'll keep to it.
28:37 Gage: For me, Sterling, I don't know your schedule that day, but 1:00 to 4:00 on Monday I could be here at the atomizer. Outside of one to four I'd be busy.
28:54 Sterling: I teach at noon Monday, Wednesday, Friday. That's my only hard constraint. I think we should be OK on scheduling.
29:08 Bartosz: If we see the work needs to be longer, that's fine. We can start as early as you want; the idea is just to make sure we finish everything during my stay.
29:31 Sterling: A couple more things. One is that we did a test of our vacuum; it seems like we're OK on the explosion-proof vacuum side. Another question, based on what you've seen: anti-static shoes and other things?
30:03 Bartosz: What you get with the system is an anti-static apron. I also have one more of those for you. There's a strap you put on your hand. In general it's advised, especially when handling a large amount of powder, but honestly we're not really doing that. We use gloves and the anti-static aprons. To have a real issue you'd need the powder suspended in the air; you'd need a real visible discharge. It's not something that happens so easily.
30:46 Sterling: So, precaution.
30:49 Bartosz: Definitely. Let's just make sure we handle the powder well, but that's it.
30:50 Sterling: For the samples we want to test, we probably want two runs. One is a high-purity aluminum rod that we try atomizing. The other is a high-purity aluminum rod that's bored out, sort of an inner crucible that we pack powder into, other types of powders to get other elements in there, then cap it, or use a press fit into the inner bore to compress some of the powder down, and try atomizing that and getting a full melt pool.
31:45 Bartosz: As long as you don't put pure powder in the crucible, it should be fine. The problem with pure powder is that very often it's kind of melted, but each single particle doesn't fully melt: it stays as a particle, so it's all sintered together even though you're much higher in temperature than you should be, and you still don't see the melt. But if you have some of the material already melted, then the particles can dissolve into the melt and it should work properly.
32:18 Sterling: Gotcha. I think we'd like to try at least one run where the powder is in the aluminum crucible to see how that goes.
32:37 Bartosz: Sure, we can use the extra time to run those kinds of experiments.
32:41 Sterling: And for mixing: is there induction mixing that happens?
32:58 Bartosz: Yes. It's still nice to have a master alloy whenever possible, but you can see the mixing when we reach temperature: once the material is melted it doesn't just heat up continuously; it makes a pulsation that causes the whole melt to mix a bit. It's not something I love to rely on, so whenever possible having a master alloy is generally better. If it's a small critical addition with a much higher melting point, there's a chance it just clumps in one spot and doesn't dissolve that well. Aluminum plus a bit of master alloy will definitely mix well.
33:58 Sterling: If we make our own master alloy from stock powders, would you recommend a general casting process for that?
34:12 Bartosz: Depending on what you have available, using a plasma arc will usually be better, even for powders. If you have an arc melter that's suitable for powders, that's probably easier, because you can basically mix anything that way. Even with a large melting-point difference, with the arc you'll have everything melted.
34:43 Sterling: That covers all my extra questions. We're looking forward to having you.
34:53 Gage: On the schedule again: was there a specific reason we decided to start on the 28th?
35:02 Bartosz: As I understand it's even better for you to start on the 28th if possible. I want to make sure I have the two days free afterwards, because I may need to visit one more place on my way. So the 28th, 29th, 30th would be preferable, and then I may be able to squeeze something else onto the trip.
35:32 Gage: So you have another responsibility after the 30th, on the 1st?
35:39 Bartosz: It would seem so; if I'm already in the States I may have to visit one more place. I'm still getting the details. But I'll adjust to your schedule.
35:58 Gage: If it's not a big deal for me to be there Monday, that's fine. I'm completely open the rest of the week, so if it came down to starting on the 29th, 30th, and maybe the 1st, I'm free all those days. But if it's a big deal for me to be there on the 28th, that's fine too.
36:18 Bartosz: On the 28th we'll just cover the installation, put everything in place, do the testing, and prepare everything for the training: take all the consumables out of the boxes and organize. I'll want to make sure it heats up fully and the coolant flow works. Nothing very critical.
36:51 Sterling: I think we'll take videos, and Gage, if there's anything that'd be really good for you to see before the Tuesday training, we can watch some of those that evening.
37:04 Bartosz: You'll also get access to the website where we have videos about the operation and how to assemble everything, so no worries.
37:24 Bartosz: Let me know if you have any questions or extra things you'd like to cover and I'll make sure I'm ready for it.
37:37 Sterling: Thanks. See you.

*(Bartosz leaves; Sterling and Gage continue.)*

37:47 Gage: Was this the aluminum you were referring to that you wanted to test?
37:52 Sterling: No, we'll get some. Actually, good point. I was thinking of ordering from McMaster to start with, the highest-purity aluminum rod we can get from there. The outer diameter would be 20 mm. It'd probably be good to talk with the machine-shop folks, though actually I think we're fine going about 3 inches deep into one of these rods. Then ideally order the right size of rod that could be press-fit into it, so two diameters of rod.
38:54 Gage: Two diameters of aluminum rod: one 20 mm, one that fits within the drilled hole. To cap it after you put the powder inside?
39:11 Sterling: Basically, yeah, and to compress the powder down to hopefully make it easier to melt.
39:20 Gage: Is that something you'd like me to find?
39:24 Sterling: Yeah, if you wouldn't mind. We have McMaster credentials on the BYU VCL account, so you can just say, "Look at McMaster using the Raspberry Pi and find the highest-purity aluminum rods there," and also look at other suppliers in case something is higher purity than that.
39:53 Gage: I'll query that. On what he said about powders not mixing very well within the atomizer: I was asking whether we could start melting with the furnace open in order to stir it with something, but I didn't think about the fact that the whole point of the enclosure is to keep oxygen out while melting.
40:24 Sterling: We'll see how things go. If the powders not melting becomes a big issue I think there are some options. One is a vacuum press: really press-fit this thing with a lot of hydraulic pressure to compact the powders, potentially a heated vacuum press, so we're not melting it but getting the particles to adhere to each other more.
41:21 Gage: I wonder if you could do something like friction stir welding. It doesn't melt the metal, it just heats it enough that they bond. Anyway.
41:43 Sterling: Our backup plan would probably be going to the University of Utah, borrowing some of the arc-melting equipment there, making our master alloys with the powder mixture, and bringing it back. It'd be really nice if we could get it to work with powders, though.
42:17 Gage: For real. Especially if we got a high-purity feedstock like this (I know this one isn't high purity, but if it were), that's the base of our alloys; the majority is aluminum anyway. You could clip off the amount you want and pour the powder in after that. You saw the email about the quote from Valimet for 2 kg of aluminum powder?
42:51 Sterling: How much was it?
42:53 Gage: They haven't sent an actual number yet, because they wanted a bunch of papers signed. But maybe we wouldn't want to buy 2 kg of aluminum powder because we'd rather have a solid version.
43:11 Sterling: Yeah. There's definitely going to be some trial and error, and that's part of why it'd be nice to do some of that while Bartosz is here, with the expert.
43:31 Gage: We got all that stainless-steel powder too. We could maybe test something with that. Oh, but we can't melt stainless, can we?
43:38 Sterling: No. It's really only copper and aluminum we'd be doing with the induction furnace, I think.
43:47 Gage: Copper has a pretty high melting point, but I guess not relative to most other things.
43:53 Sterling: [Misspoke: said copper is lower than aluminum. Cu melts at 1085 °C, Al at 660 °C; the point stands that Cu is within the induction unit's range and stainless is not.] So I'll get some issues updated and get you tagged on some. Not in priority order, the things that come to mind: the dehumidifier, if we could try to get that running; ordering the two high-purity aluminum rods, finding the ones we want and ordering them; you'll talk with Nick about the inert gas. I think it would still be good to look into the glovebox / enclosure stuff, see if there's one we can get for a few grand, up to like four or five grand. Thanks for managing all of this.
45:23 Gage: No worries. Let me make sure I understood Bartosz properly on our connections. These are half-inch, and these connect to the heat exchanger. These half-inch tubes we're going to use to connect to the back of the heat exchanger. So I'll work with Dave to get whatever conversions or adapters.
46:18 Gage: It sounded like Bartosz was bringing a tube or pipe for another part; I just can't remember what that was.
46:27 Sterling: I have a transcript, so I can try to link it to track what he was talking about. I didn't record the meeting, but there's a transcript.
46:48 Sterling: Now that I'm thinking about it, it'd also be worth trying to have somebody go up to the University of Utah with one of these powder mixtures and try to make a master alloy: arc-melt some of the powders with some aluminum. Or even if we just took the AlSi10Mg and put that powder in and arc-melted it, just to see what our options are. It'd be really cool if, before Bartosz left, we had a sample we prepped get atomized. Kind of our first experiment.
47:48 Gage: I think it'd be good too, since we already have the AlSi10Mg, to melt that into an alloy and then atomize it ourselves, to compare what that looks like versus what we can do with ours. Was there another specific alloy you wanted to do at the University of Utah?
48:10 Sterling: If we get some of that scandium... no, the scandium's going to take a while, so not that. If we get everything we need to make AlSi10Mg on our own, not from the commercial AlSi10Mg powder, that would be cool. So: University of Utah, seeing if we can use one of their arc melters. That would be through Taylor Sparks; I know he has an arc melter. Trying to get some stock material to bring in. And we'll probably be making a lot of trips to the chem store for containers and such.
49:16 Gage: We got those blue chemical cabinets that we could put powders in.
49:23 Sterling: Right. And I think we want to get a whole bunch of desiccant, including desiccant that's OK to throw in a container.
49:37 Gage: I bought some small desiccant bags from McMaster. Here's one packet; I don't know if that's big enough, but we've got several.
49:50 Sterling: OK. I think we just want to make sure that, since it's usually silica gel, it's not contaminating the powders. We might want a couple of Claude pings on desiccants that wouldn't contaminate the powders we're working with in the container.
50:32 Gage: So ping Claude to check whether silica desiccant will contaminate our powders.
51:03 Gage: It'd be really nice if we could go somewhere like Valimet, or somewhere in industry, to see how they handle their powders and what procedures they have. Then we could copy or mimic those and not just guess whether we're doing too much or not enough.
51:23 Sterling: I agree.
51:31 Gage: Is Valimet the closest one in the industry?
51:35 Sterling: Yeah, especially for aluminum. There are so many things about the workflow, safety and handling wise, that are specific to aluminum. That would probably be our best bet.
51:51 Gage: How would we organize a trip like that? Would it be university funded or from lab funds?
52:00 Sterling: It would be lab funded. It could be a road trip or a flight, with a car rental from BYU depending on how many people. If three to five people go, a car rental makes the most sense; otherwise a flight would be fine for one or two.
52:33 Gage: Is that something you want to think about now or come back to in a month?
52:41 Sterling: Probably a month from now. But it might be worth getting on a call with them initially, to walk them through what we're doing, maybe a pre-recorded video, and say, "Could you look through what we're thinking for our workflows and let us know if anything seems out of place or overkill?" I think that would be a good starting point and a good use of time, if we had our safety video or our workflow described.
53:53 Gage: OK. So I'll talk to Barry to figure out how we get the dehumidifier on, because I don't know. I'll talk to Nick about making sure we get 5N argon. I'll work with Dave for the pipe hookups and all that, if you'll send me the important part of the transcript for that. Do you want me to reach out to Taylor Sparks, or do you want to?
54:38 Sterling: Actually, yeah, if you wouldn't mind. Just make sure to cc me.
54:49 Sterling: I'm getting better at delegating, ever so slightly.
54:53 Gage: That's an important skill, especially in running a business. So I'll just email him: "Sterling and I want to do some arc melting of AlSi10Mg powder. Could we talk about that? What are your thoughts?"
55:19 Sterling: Yeah, like, does it seem feasible to do by the 28th or 29th so we could test it with our atomizer? If so, is there a student we could connect with to help us do that run? And whatever email you send, I might just reply as well and add any extra bits.
55:58 Gage: Perfect, that makes it easy. Then I'll ask Claude about McMaster high-purity aluminum rods, 20 mm and then a smaller one, and figure out a good ratio for that, and also ask Claude about the silica desiccant contaminating powders. Is that everything?
56:27 Sterling: I think that's everything.
56:31 Gage: Productive meeting.
56:34 Sterling: Agreed. Thanks, Gage.
