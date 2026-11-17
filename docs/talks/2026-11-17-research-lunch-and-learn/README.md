# Research lunch and learn, 2026-11-17: doing research with AI agents

A six-minute lightning talk, prepared in [#350](https://github.com/vertical-cloud-lab/byu-vcl/issues/350)
from a voice memo.

| File | What it is |
| --- | --- |
| [`outline.md`](outline.md) | **The outline.** Doumont's design template filled in, with draft opening and closing lines, a slide plan, a time budget, and the open items to fill in |
| [`transcript.md`](transcript.md) | The voice memo, transcribed with Whisper large-v3 (two passes, reconciled) |
| [`doumont-method.md`](doumont-method.md) | Jean-luc Doumont's method for structuring a talk, quoted from his own PDFs, with links |
| [`whisper/`](whisper/) | Both raw Whisper passes, with settings and timing |
| [`follow-ups.md`](follow-ups.md) | **The follow-up searches**, mapped onto the outline's gaps: CAD, meetings, prompt pairs and pings, the CES subscription, Taylor's post, and what the literature says |
| [`cad/`](cad/README.md) | 111 agent-made CAD designs from 13 lab repos, rendered as turntable GIFs, with exploded views for assemblies; a [gallery](cad/gallery.md), a contact sheet and an animated grid |
| [`meetings.md`](meetings.md) | Meetings with outside people that trace back to an agent ping, with the evidence |
| [`prompts-and-pings.md`](prompts-and-pings.md) | Real good and not-so-good prompt pairs, and atomizer-workflow pings, for slides 5 and 6 |
| [`edison/`](edison/) | Edison literature answers (teaching AI use, using agents well, LLM-generated CAD, open provenance), with the full task records |

To transcribe another recording: `pip install faster-whisper`, then
`python scripts/transcribe_whisper.py AUDIO OUT_DIR --no-condition-on-previous-text`.

To re-render the CAD or rebuild the gallery, see [`cad/README.md`](cad/README.md#how-it-was-made).
To fetch Edison answers that were still running, run `python -I edison/fetch.py`.
