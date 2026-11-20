# UR10e or UR12e? The same arm, renamed (round 14, run D)

Sterling on PR #318 (2026-11-20): "I think UR10e-s have been replaced by UR12e-s (apparently a rebrand of the UR10e
maybe?). Not sure if that affects the CAD model, but the naming should probably be updated throughout, which will be a
big lift to try to do this **everywhere** and might lead to confusion when trying to reuse historical content where
UR10e is fixed."

## What changed: the name, not the arm

- **The rename.** Universal Robots raised the UR10e's rated payload from 10 kg to 12.5 kg in 2021 at no change in
  price ([UR news](https://www.universal-robots.com/news-and-media/news-center/universal-robots-unveils-enhanced-ur10e-with-25-greater-payload/)),
  then in June 2025 renamed it the **UR12e** "to reflect this change", as it renamed the UR5e (5 kg, now 7.5 kg) the
  UR7e ([Automation World, 5 June 2025](https://www.automationworld.com/factory/robotics/news/55293382/universal-robots-unveils-latest-cobot-tech-in-collaboration-with-nvidia)).
- **Mechanically unchanged.** UR's FAQ: the UR5e and UR10e "were renamed UR7e and UR12e to reflect the payloads they
  actually carry, 7.5 kg and 12.5 kg ... The robots themselves are mechanically unchanged"
  ([UR FAQ](https://www.universal-robots.com/products/faq)). Robotiq: "The UR12e is mechanically and technically
  identical to the UR10e", and everything that works with the UR10e (software, URCaps, accessories) works with the UR12e
  ([Robotiq](https://blog.robotiq.com/knowledge/understanding-the-difference-between-ur10e-and-ur12e)).
- **The same figures:** 12.5 kg payload, 1300 mm reach, 33.5 kg, Ø 190 mm base, ±0.05 mm repeatability, IP54
  ([UR12e on CB5](https://www.universal-robots.com/products/ur12e-cb5/)). This repo has used 12.5 kg since round 4, so
  no reach, payload or tipping figure changes.
- **And the newest names carry the reach:** with its Gen 7 platform (2026) UR names arms by payload and reach, so the
  same arm is also listed as the **UR12e-1300** (UR's FAQ: "The number after the dash is reach in millimeters"; the
  reach figures come "from a revised measurement method rather than any change to the arms").

So the kinematics in `ur_arm.py` (the `ur10e` entry of Universal Robots' own ROS 2 description, pinned) are the UR12e's.
Nothing in the model, the IK or the collision checks changes.

## What this run changed, and what it left

- **On screen, from now on: "UR12e".** `scene.py` draws every title, status line, leader label and caption through
  `scene.shown()`, which maps "UR10e" to "UR12e" (`scene.ON_SCREEN`). The two names are the same length with digits of
  the same width, so no layout moves. Every clip rendered after this commit says UR12e, with no change to the ~20
  files that write the label; clips rendered before it still say UR10e until they are re-rendered.
- **The long-form's text:** the opening card says "A UR12e arm (the UR10e, renamed in 2025)", the atomizer chapter's
  card "MiR250 + UR12e", the YouTube description "two UR12e arms (the UR10e, renamed in 2025)". The narration says
  "a Universal Robots arm", and `longform.SAY` speaks "UR12e" as "U R twelve E" where it appears. Uploads are tagged
  with both names (`youtube_upload.TAGS`), so a search for either finds them.
- **Left as they are:** code identifiers (`animate.ROBOT = "ur10e"`, `ur_arm.MODELS["ur10e"]`, `UR10E_PAYLOAD`, cache
  and file names), the notes and README sections of earlier rounds, `out/` JSON records, and YouTube descriptions of
  past uploads. Renaming those would break the pinned ROS description's file names and make old records disagree with
  the clips they describe.
- **New notes and text** should say UR12e, with "(the UR10e, renamed)" the first time in a document.
