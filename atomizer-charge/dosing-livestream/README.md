# Livestream snippets of the dosed cups (#264, powder-doser#186)

Two cups of the [composition spread](../README.md#composition-spread-4047-powder-in-6063-cups-264) have been
dosed with 4047 so far, both on the powder doser and both **as-made (thick-wall) cups**. No thin-wall cups have
been machined, so `wf6g` (22.5 wt%) and `k2ka` (30 wt%) have no cups yet.

| Bag | Cup | Ping (powder-doser#186) | Dose, UTC | Livestream | Snippet |
|---|---|---|---|---|---|
| `gd4e` | 7.5 wt%: 3.0432 g of powder in a 32.5074 g cup (7.506 wt% with the computed 4.995 g plug) | [sgbaird, 10-19](https://github.com/vertical-cloud-lab/powder-doser/issues/186#issue-5933011605) | 10-19 23:24–23:27: `a5fdadaa` stalls at 0.2028 g | [`Y9FUMxor5Fo` 4:23:29](https://youtu.be/Y9FUMxor5Fo?t=15809) | [4×](gd4e_2026-10-19_dose-a_4x.mp4) |
| | | [retry: tilt, speed and taps](https://github.com/vertical-cloud-lab/powder-doser/issues/186#issuecomment-6280913960) | 10-20 01:20–01:25: 60° and 75°, 2.9 and 8.3 mg | [6:19:23](https://youtu.be/Y9FUMxor5Fo?t=22763) | [4×](gd4e_2026-10-20_tilt-retries_4x.mp4) |
| | | [reverse the auger](https://github.com/vertical-cloud-lab/powder-doser/issues/186#issuecomment-6281865650) | 10-20 02:34–02:49: the outlet frees at ~02:38, then stepwise to 2.8272 g | [7:33:42](https://youtu.be/Y9FUMxor5Fo?t=27222) | [8×](gd4e_2026-10-20_reverse-and-finish_8x.mp4) |
| `8mmz` | 15 wt%: 6.5676 g of powder in a 37.2151 g cup + plug (15.000 wt%) | [williamulbz, 10-20](https://github.com/vertical-cloud-lab/powder-doser/issues/186#issuecomment-6301399315) | 10-20 21:07:48–21:12:08: `cb3096e9` stalls at 2.2421 g | [`3CvBrmkv2xE` 1:55:21](https://youtu.be/3CvBrmkv2xE?t=6921) | [4×](8mmz_2026-10-20_first-dose_4x.mp4) |
| | | (same ping) | 10-20 21:13–21:41: unclog steps and two more doses, to 5.3120 g | not recorded | — |
| | | [continue after clearing the auger](https://github.com/vertical-cloud-lab/powder-doser/issues/186#issuecomment-6302880128) | 10-20 22:15–22:21: `5851b6d6` and a top-up, to 6.5676 g | not recorded | — |

The masses and trial ids are from the powder-doser sessions' records
([`data/opt/production-al4047-atomizer-cups/`](https://github.com/vertical-cloud-lab/powder-doser/tree/34c043c/data/opt/production-al4047-atomizer-cups)).
The `8mmz` total counts 0.0765 g that was on the balance before the last dose as powder in the cup; William's
weighing of the plugged cup (43.7827 g expected) is the check.

- **The `picam-d1pr` stream froze at 21:12:40 UTC on 10-20,** half a minute after `cb3096e9` stopped, and was still
  frozen when these were fetched (10-21 00:18 UTC). The rest of the `8mmz` dose and the bagging aren't on video.
- **The clock burned into the frames is lab local time (UTC−6).** On `Y9FUMxor5Fo` it reads 8 s behind
  `release_timestamp` + offset at all four points checked, so the links above go by the clock.
- **`3CvBrmkv2xE` was still listed as live.** Its link uses the live DVR's time (2 s per media-sequence number),
  which the archive should keep. Check it once YouTube has finished the archive.
- **The snippets are 360p** (format 230, portrait), sped up 4× or 8×, with no audio. Open the YouTube link for 720p.

## How they were made

`clips.py` ran on a stream-cam Pi, because YouTube refuses player extraction from an Actions runner. It takes
the windows in `jobs.json`, fetches the HLS segments with urllib at up to 1 MB/s, and writes one `.ts` per window.
Archive windows are found by walking `#EXTINF`; live ones by media-sequence number from the playlist's
`#EXT-X-PROGRAM-DATE-TIME`. The `.ts` files were then encoded on the runner:

```
ffmpeg -i in.ts -vf "setpts=(PTS-STARTPTS)/4" -r 30 -an -c:v libx264 -preset slow -crf 27 \
  -pix_fmt yuv420p -movflags +faststart out_4x.mp4
```
