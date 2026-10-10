# The atomizer, start to finish: every recorded step, in one cut

A raw compilation of the 26 atomizer videos, reorganised into the order of a run and joined end to end, as a starting
point for anything more polished. Nothing in it is narrated, stabilised, cross-faded or re-timed: it is the footage,
with three things added so that it can be navigated: the source and running source time of every clip in the top bar,
the timestamp log's own note for each moment as a yellow lower third, and Whisper subtitles. The conversations stay in.

| | |
| --- | --- |
| The clip list, with a link to every source moment | [`edl.md`](edl.md) |
| Where each chapter and clip starts in the uploads | [`chapters.json`](chapters.json) |
| The uploads (unlisted, two parts) | [`uploads.json`](uploads.json) |
| The script that plans, fetches, builds and uploads it | [`build_stitch.py`](build_stitch.py) |

## How the cut is made

The raw material is the timestamp log, 799 rows across the 26 videos ([`../timestamps.md`](../timestamps.md), one row
per substantive moment, from the per-video indexes in [`../notes/`](../notes/)).

1. **Every row is assigned a chapter** of the procedure (`ASSIGN` in the script: per video, from which second on which
   chapter applies, with rows of a different kind pulled out individually). The chapters follow the SOP's outline:

   | # | Chapter | # | Chapter |
   | --- | --- | --- | --- |
   | 1 | Installation and commissioning | 9 | Before a run: furnace, nozzle, crucible and loading |
   | 2 | The machine: a tour of the module | 10 | Before a run: chamber, plate guard, bowl and container |
   | 3 | The HMI: pages, scan, program and pressure logic | 11 | During a run: gas wash and heating |
   | 4 | Materials, boosters and particle size | 12 | During a run: the pour |
   | 5 | Safety and PPE | 13 | After a run: shutdown, cooldown, venting, powder out |
   | 6 | Before a run: power-up and utilities | 14 | Cleaning between runs |
   | 7 | Before a run: the ultrasonic stack | 15 | Tools, consumables and spares |
   | 8 | Charge preparation: cups, rods and dosing | 16 | Lessons, planning and support |

   Rows whose phase is *chatter* are not shown; they still end the window before them. Theory that explains the step at
   hand stays with the step (booster theory during the stack build, purge theory during the gas wash); general material
   and particle-size talk is chapter 4.
2. **Each row becomes a window** of its video, from 1.5 s before the row to the next row, or to a cap if the next row is
   further away: 60 s for an action row, 45 s for conversation (theory, parts, lessons, admin), 30 s for a row read from
   frames of a video with no speech. Time between rows beyond the cap is what the cut skips: waiting for a purge or a
   melt, silent camera, chatter.
3. **Touching windows of the same chapter merge** into one clip, so a continuous piece of work plays continuously, and
   the merged clip's notes change as the footage reaches each row. A lone row shorter than 6 s is extended.
4. **Cuts snap to sentence boundaries** (or pauses longer than 0.7 s) found by the word-timed Whisper transcripts, within
   about 3 s of the requested time, so clips do not start or end mid-word. The three videos with no speech are cut
   exactly on their rows.
5. **Order**: by chapter, then by the recording order of the videos, then by time. Within a chapter you therefore see
   every day's version of the same step in sequence (the Sep 29 stack build, then the Sep 30 reverse-booster rebuild,
   then the Oct 2 run), each labelled with its video and day.

The recording order is not the upload order (the training videos were uploaded in batches). It is read from what is
said: *Training (Sterling's phone)* says "8:30 a.m. start tomorrow" and "to try Wednesday", so it is Monday Sep 28,
the commissioning day; Video 1 (tour and furnace prep) opens Sep 29, Video 4 (insulation, loading, chamber) runs straight
into Video 5 (container, stack, first rod run: "first rod run through this machine"); Video 2's setpoint "had gone
straight to 1000" from Video 5's melt, and it ends with "for tomorrow drill nozzles" and the plan to change to the 1:1
booster, which Video 3 then does, ending "done for today". On Sep 30 the cartridge cleaning (sample cup filled, scan
"a little bit off") precedes the cup run (*Atomizing AlSi10Mg-Al6063*, "parameters I used yesterday"), then Video 7
(reverse booster, "earlier resonance explained"), Video 8 (nozzle, furnace reassembly) and Video 9 (the run, the
consumables tour, the certificate). The dosing sessions prepare the cups used the next day.

## Output

Two uploads, because one file would be close to seven hours: **part 1** is chapters 1–10 (the machine, and before a
run), **part 2** chapters 11–16 (during and after). Each opens with a title card and has a card before every chapter;
the chapter times are in the video descriptions (YouTube chapters) and in [`chapters.json`](chapters.json). 1280×720,
30 fps, H.264 (libx264 veryfast, CRF 23), AAC. Portrait phone video sits over a blurred copy of itself rather than black
bars. Clips are encoded once each and the parts are joined without re-encoding.

## Sources and how they were fetched

Video comes from the best HLS stream YouTube has for each video (720p for most; 1080p for the two portrait installation
clips), fetched on the stream-cam Pi with [`../tools/hls_sections.py`](../tools/hls_sections.py) as one window per clip
(the clip plus 6 s either side), at ≤3 MB/s, and pulled to the runner over Tailscale window by window; about 6.4 GB for
the 254 windows. Audio is the full m4a track of each video, already on the Pi from the first download pass. A clip whose
window did not arrive falls back to the 360p copy and says so in its corner.

```
python build_stitch.py plan      # clips and minutes per chapter
python build_stitch.py jobs      # hls_sections.py job list (only the windows not fetched yet); run it on the Pi
python build_stitch.py edl       # edl.md and chapters.json
python build_stitch.py build     # the clip segments, waiting for each window to arrive
python build_stitch.py concat    # join the parts from the cached segments
python build_stitch.py upload    # unlisted, chapters in the description
```

`ATOMIZER_DL` is the folder with `<id>.m4a` (and `<id>.v360.mp4`), `ATOMIZER_HLS` the folder of fetched windows.

## Knobs

The whole cut is a function of the timestamp log and a few constants at the top of the script: the caps (`CAP`,
`CAP_CONV`, `CAP_KEYFRAME`), the lead-in, the merge gap, and `ASSIGN`. Moving a row to another chapter, or changing
where a chapter starts in a video, is a one-line change there; `python build_stitch.py plan` shows the effect before
anything is fetched or encoded. Rows the log does not have are not in the cut: to include a moment, add its row to
the video's index in [`../notes/`](../notes/) and rebuild [`../timestamps.md`](../timestamps.md).
