#!/usr/bin/env python3
"""Open a YouTube video in the Pi-tunnelled headed Chrome, expand the description and click
"Show transcript" with real mouse moves, then save the transcript text. Usage: pi_youtube_transcript.py VIDEO_ID OUT.json"""
import sys, json, time, random, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pi_browse as pb
import pi_search as ps
from playwright.sync_api import sync_playwright

vid, out = sys.argv[1], sys.argv[2]
tok = ps.acquire("youtube")
try:
    with sync_playwright() as p:
        br = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = br.new_context(viewport={"width": 1500, "height": 950}, locale="en-US"); page = ctx.new_page()
        page.goto(f"https://www.youtube.com/watch?v={vid}", wait_until="domcontentloaded", timeout=60000)
        time.sleep(4); pb.consent(page)
        title = page.title()
        try: page.keyboard.press("k")   # pause playback
        except Exception: pass
        page.mouse.wheel(0, 500); time.sleep(1.5)
        for sel in ["tp-yt-paper-button#expand", "#description-inline-expander #expand", "#expand"]:
            try:
                b = page.locator(sel).first
                if b.is_visible(timeout=2000): pb.human_move_click(page, b); break
            except Exception: pass
        time.sleep(1.5)
        clicked = False
        for sel in ["ytd-video-description-transcript-section-renderer button", "button[aria-label='Show transcript']", "text=Show transcript"]:
            try:
                b = page.locator(sel).first
                if b.is_visible(timeout=3000): pb.human_move_click(page, b); clicked = True; break
            except Exception: pass
        time.sleep(5)
        try:
            page.wait_for_selector("ytd-transcript-segment-renderer, transcript-segment-view-model", timeout=15000)
        except Exception:
            pass
        segs = page.evaluate("""() => [...document.querySelectorAll('ytd-transcript-segment-renderer, transcript-segment-view-model')].map(s => {
              const t = s.querySelector('.segment-timestamp, .ytwTranscriptSegmentViewModelTimestamp, [class*=Timestamp]'); const x = s.querySelector('.segment-text, [class*=SegmentText], span[role=text]');
              return [(t?t.innerText:'').trim(), (x?x.innerText:s.innerText).trim()] })""")
        meta = page.evaluate("() => ({channel: document.querySelector('ytd-channel-name a')?.innerText||'', date: document.querySelector('#info-strings yt-formatted-string, #info span:nth-child(3)')?.innerText||''})")
        page.screenshot(path=f"/tmp/pishots/yt_transcript_{vid}.png")
        json.dump(dict(video_id=vid, url=f"https://www.youtube.com/watch?v={vid}", title=title, clicked_show_transcript=clicked, n_segments=len(segs),
                       channel=meta.get("channel"), segments=segs), open(out, "w"))
        print(vid, "segments", len(segs), "clicked", clicked, title[:70])
        ctx.close()
finally:
    ps.release(tok)
