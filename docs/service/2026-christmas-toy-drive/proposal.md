# Proposal: students printing toy-drive toys on the lab's printers

*For Sterling to decide. Nothing here has been announced, and nobody has been contacted.*

The aim is to let students in the machine design class earn the extra credit without needing a
printer of their own. The lab prints the toys. Students choose them and carry them to the ME
office. Here is how each step could work, with my recommendation first and the alternatives
after it.

## 1. How files come in

**Recommended: students choose from the [shortlist](README.md#toys-we-can-print-here).** Each
toy on it has been checked against the limits and the avoid list and sliced for the A1 mini. Its
license allows printing copies to give away. A request is then just a toy name and a colour,
with nothing to check.

Students who want to **design their own toy**, or bring a model that isn't on the list, would
send a link to the model page (or their own STL) and say which toy type from the details sheet it
is. Those go through step 2 before they join the queue.

**Where requests go:** this repo is public, and who is earning extra credit in a class shouldn't
be posted in public. So take requests where the class already handles its work (Learning Suite,
or a form), and keep the print queue in the lab without names. Each queue entry gets a number,
and the student writes that number on their tag.

## 2. Who checks them against the limits

- **Shortlist toys:** they are already checked, so there's nothing to do.
- **Anything else:** two checks.
  - *The mechanical check* can be a `@claude` run on a new issue: slice it with
    [`toys/slice_toys.py`](toys/slice_toys.py) for the printer it will run on, and read the
    grams, cost and time against the limits (PLA, at most 210 g at our price, $4, 8 h). Then
    confirm that it is one piece or print-in-place and that its license allows giving prints
    away. That run would get the model page link and the file, but no student's name.
  - *The judgement check* is for a person: whether the toy has sharp edges, is a weapon, is
    appropriate, or could shed small pieces (see [the avoid list](README.md#items-to-avoid)).
    Sterling or a TA, a minute per design.

## 3. Who queues and watches the prints

A person has to be at the printer for every plate. The A1 mini doesn't clear its own bed, and
the printing rules in `CLAUDE.md` want someone nearby while a print runs. That person matters
more than the software. The robot-arms trial with
[Rexagons](README.md#multi-color-rexagons-on-the-a1-mini) may take the plate-clearing off them
for the A1 mini, though not the check of each toy.

**Recommended:** one lab member or TA owns the queue for the three weeks:

- **Batching.** They start prints at fixed times, such as morning, midday and before leaving,
  and choose long toys for overnight only if someone will be in early. Small toys go several to
  a plate (nine 40 mm worry stones fit easily on the A1 mini's 180 mm bed).
- **Sending.** Either they send from Bambu Studio themselves, or they ask in a `@claude-print`
  run. That run works through the existing gates: a `bambu-print-approvers` member approves each
  run, a fresh camera frame shows the plate, the nozzles are read, and there is a 90-second
  hold. Sending from Studio directly is simpler for a queue this repetitive. `@claude-print`
  helps when nobody is at a computer with Studio.
- **Watching.** They check the first layer of each plate and the camera now and then. They take
  each toy off, flex every joint, and set aside any toy that broke or has a stringy, sharp or
  fused spot.
- **Pick-up.** Each finished toy goes in a labelled bag with its queue number. The student
  collects it, ties on the tag and drops it off at 350 EB. The sticker on the office's tree
  poster is visible evidence for the extra credit.

Alternative: students print their own toy on the lab printer during set hours, with the lab
member there. That is more hands-on and better for an engineering class. It also needs printer
training and lab access for each student, which is a lot to set up before December 10.

## 4. Which filament

- **Ours:** Bambu PLA Basic. On 2026-11-26 the A1 mini's AMS Lite held dark blue and black PLA
  Basic (and a white PETG Basic, which the drive doesn't allow). Earlier print logs show white
  PLA Basic on the H2D. That is enough to start, but the colours are dull for toys.
- **The department's free filament:** the flyer offers free filament for prints in the
  Prototyping Lab. Whether some of it could be used on our printers would have to be asked.
  I haven't asked anyone.
- **Buy colours:** a 1 kg PLA Basic refill is $14.99 on Bambu's US store today, on sale from a
  typical $18.99. At about 30 to 70 g a toy, four bright spools (say red, yellow, green, orange)
  make roughly 60 to 130 toys for about $60. That is a purchase for Sterling to decide on. The
  sale price may not last.

## 5. How much the printers can do

The shortlist's toys take 31 minutes to just under 5 hours on the A1 mini, about 2 hours on
average. The limit is how often someone clears the plate, more than print time. If the arm in robot-arms
learns to clear the A1 mini's plate (the [Rexagon trial](README.md#multi-color-rexagons-on-the-a1-mini)),
print time becomes the limit again, within working hours. With the plate
cleared three or four times a day, the A1 mini manages three or four plates a day. Over the 13
weekdays from December 1 to December 17 that is roughly 40 to 50 plates, and more toys than that
when small toys share a plate. The H2D could roughly double that once someone reads its nozzle
diameters in Studio. It refused the LAN login
on 2026-11-26, and the printing rules don't allow sending to a printer whose nozzles haven't
been read. For the December 10 delivery, the toys need to be off the printer by December 9.

## Decisions for Sterling

- [ ] Shortlist only, or also student-designed toys (with the check in step 2)?
- [ ] Who owns the queue, and when plates get cleared
- [ ] Which printers: the A1 mini only, or the H2D too (someone reads its nozzles in Studio first)
- [ ] Filament: ours as it is, ask the department about its free filament, or buy colours
- [ ] Where requests come in (Learning Suite or a form), and what counts as proof for the extra
      credit (the sticker on the office poster, or a photo of the tagged toy on the shelf)
- [ ] Rexagons: ask PinkyWings for permission to give prints away, or keep them in the lab.
      MakerWorld's Standard Digital File License forbids handing printed copies on
- [ ] A third PLA colour for the A1 mini's empty AMS Lite slot, for three-colour Rexagons
- [ ] robot-arms: add `allowed_bots: vcl-bot` and byu-vcl's sender-filter lines to its
      `claude.yml` so `@claude-super` can hand it work, or post the plate-clearing request there
      by hand
