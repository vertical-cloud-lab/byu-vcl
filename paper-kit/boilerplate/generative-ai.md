# Generative-AI disclosure: one paragraph, four publishers

The paragraph is
[`manuscript/declarations/genai.tex`](../manuscript/declarations/genai.tex).
Its wording works for Elsevier, Springer Nature, RSC and ASME. The publishers
disagree about where it goes, so each `main-*.tex` puts it where its
publisher asks (table below). Research use of AI, such as writing analysis
code, goes in Methods for all four, through
[`genai-methods.tex`](../manuscript/declarations/genai-methods.tex).

All quotations below were read on **2026-10-10** at the URLs given, and the
key sentences were re-checked against the live pages that day. Policies
change, so re-read them at G5 (submission) and update this file if they
have.

## The paragraph

> During the preparation of this work, the authors used [tool and version]
> ([developer]; accessed through [the web interface, the API or an editor
> extension]; used on [dates]) in order to [purpose, e.g. edit the grammar and
> readability of author-written text] in [sections]. [The prompts are listed
> in Supplementary Section N.] The tool was not used to generate data,
> analyses, conclusions, references, figures or images. After using this
> tool, the authors reviewed and edited the content as needed and take full
> responsibility for the content and integrity of the published article.

What it is built to satisfy:

| Requirement | Who asks | Where in the paragraph |
|---|---|---|
| Tool name and purpose; authors reviewed and take responsibility | Elsevier (template), RSC (template) | the first and last sentences, close to each template |
| Version, developer ("manufacturer"), how accessed, dates, which portions | ASME | the first sentence |
| Prompts | RSC (in Methods); ASME (for research use of LLMs) | the optional second sentence |
| "Clearly describe use and confirm author accountability" | Springer Nature | the whole paragraph |
| No AI images | ASME bans them; the other three restrict them | the third sentence |
| Responsibility for *integrity* | ASME | the last sentence |

If no tool was used at all, replace the paragraph with "No generative AI or
AI-assisted tool was used in preparing this manuscript." ASME also asks you
to confirm this in the submission system.

## Where it goes

| Publisher | Paragraph goes in | Also |
|---|---|---|
| Elsevier (incl. HardwareX) | its own section, "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process", at the end, immediately before the references | research use in Methods; AI in an explanatory image goes in that image's caption too |
| Springer Nature (incl. JOM, IMMI, *Metall. Mater. Trans.*) | Methods ("or a suitable alternative part" if there is none) | any AI visual content disclosed in its caption or legend |
| RSC | Experimental / Materials and Methods, with the prompts; the tool name and version (the paragraph's first sentence) also in Acknowledgements | declare it in the cover letter at submission |
| ASME | Acknowledgment | research use described in Methods; confirm in the submission system |

## The four places disagree on two points, and the paragraph takes the strict side

1. **Copy-editing.** RSC says AI copy-editing "does not need to be declared",
   and so do some Springer journal pages. Elsevier exempts only "basic checks
   of grammar, spelling and punctuation". ASME exempts only rules-based spell
   check, and Springer Nature's new framework asks for a declaration even at
   its lowest-risk level. **Declare it.**
2. **What may be AI-made at all.** ASME prohibits AI-drafted text, data,
   analysis and images; it allows AI only to edit text the authors wrote.
   The other three allow more, with disclosure. A paper whose text an agent
   drafted, as several lab manuscripts have been, must be rewritten by its
   authors before it goes to an ASME journal, or go elsewhere. The tracker
   asks about this at G1, when the journal is chosen.

## The publishers' wording

### Elsevier

<https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals>,
read 2026-10-10 (the page says "Policy updated June 2026"):

- Where: "you must include a separate declaration section at the end of
  your manuscript, immediately before the references, titled for instance:
  'Declaration of generative AI and AI-assisted technologies in the
  manuscript preparation process.'"
- Template: "Title of section: Declaration of generative AI and AI-assisted
  technologies in the manuscript preparation process. Statement: During the
  preparation of this work, the author(s) used [NAME OF TOOL / SERVICE] in
  order to [REASON]. After using this tool/service, the author(s) reviewed
  and edited the content as needed and take(s) full responsibility for the
  content of the published article."
- What: "Authors should document their use of AI, including the name of the
  AI tool used, the purpose of its use, and the extent of their oversight."
- Research use: "Where AI tools are used as part of the research process
  rather than manuscript preparation, this use should be described in detail
  in the Methods section."
- Exemption: "Basic checks of grammar, spelling and punctuation do not need
  a declaration statement. However, when an AI tool makes substantive
  changes to sentence structure or organization of a part of the text, this
  should be disclosed."
- Authorship: "Authors should not list AI tools as an author or co-author,
  nor cite AI tools as an author."
- Images: "AI tools must not be used to create or alter images that
  represent primary observed or experimental data that were not directly
  obtained in the research."

Older Elsevier guides name the section "...in the writing process"; the
current page says "...in the manuscript preparation process". The HardwareX
guide for authors could not be read (403, a robot check), so its own wording
is unchecked. Use the current heading.

### Springer Nature

<https://www.springernature.com/gp/policies/editorial-policies/ai-manuscript-preparation>,
read 2026-10-10. The policy is now a green, amber and red risk framework.
For the lowest-risk (green) uses, "Grammar and language editing; improving
readability and flow; formatting; translation; summarising author-written
text", the declaration column reads: "Clearly describe use and confirm author
accountability". On images: "Where AI-generated or AI-assisted visual content
is published, information about the AI system used, the purpose of its use,
and the extent of its contribution should be provided in an AI Declaration in
your manuscript. Specific disclosure should be provided within the caption or
legend of the visual content." And: "AI generated visual content that is not
derived from independently verifiable data, source material, methods,
computational outputs or author-developed content is considered opaque and is
not permitted by Springer Nature policy."

<https://www.nature.com/nature-portfolio/editorial-policies/ai>, read
2026-10-10. Under "Not permitted" it lists "Assigning authorship or
accountability to AI systems or tools".

Journal pages, for example
<https://www.nature.com/srep/author-instructions/submission-guidelines>, read
2026-10-10: "Large Language Models (LLMs), such as ChatGPT, do not currently
satisfy our authorship criteria." and "Use of an LLM should be properly
documented in the Methods section (and if a Methods section is not
available, in a suitable alternative part) of the manuscript."

### Royal Society of Chemistry

<https://www.rsc.org/publishing/journals/processes-and-policies/author-responsibilities>,
read 2026-10-10:

- "Artificial intelligence (AI) tools, such as ChatGPT or other Large
  Language Models, cannot be listed as an author on a submitted work."
- "If GenAI tools have been used when generating any part of the manuscript
  (for example when drafting text, translating content, formatting data,
  creating or editing figures, visualising results, refining code, or
  compiling references) this must be declared at submission within the
  cover letter. Authors should also include a statement within the
  Experimental/Materials and Methods section outlining how the tool was
  used, including prompts. Details of the AI tool such as the name and
  specific model or version (e.g., GPT-4 or Claude 3.5 Sonnet) should be
  included in the Acknowledgements section. If there is no
  Experimental/Materials and Methods section, all details must be included
  in the Acknowledgements section."
- "The use of an LLM (or other AI-tool) for "AI assisted copy editing"
  purposes does not need to be declared."
- "Recommended statement in Acknowledgements section: "During the
  preparation of this manuscript/study, the author(s) used [tool name,
  version information] for the purposes of [description of use]. The
  authors have reviewed and edited the output and take full responsibility
  for the content of this publication.""
- "Where graphics have been created using AI for illustrative or aesthetic
  purposes only, a brief description of AI use should be included in the
  figure caption to explain to readers how the image was created."

### ASME

<https://www.asme.org/publications-submissions/journals/information-for-authors/ai-position-statement>,
read 2026-10-10. The page reads, in full: "ASME prohibits the use of
generative AI in the creation of content for journal submissions. Authors are
required to confirm that AI was not used in the development of their original
work and acknowledge that they have reviewed the ASME Position Statement on
the Use of Artificial Intelligence (AI). Please note that ASME does not
consider basic tools, such as rules‐based spell check in word processing, as
AI tools."

The position statement it links,
<https://www.asme.org/getmedia/22767fd2-0158-4feb-96ff-cbeb990b5b84/Position-Statement-Use-of-AI-ASME-External-Content.pdf>
read 2026-10-10:

- "ASME will not accept external content that lists AI or AI technologies
  as an author or co‐author."
- "AI Tools may be used to modify, edit, review, revise, translate, polish,
  improve readability, stylize, or otherwise change any of the
  Author‐created materials in External Content, but any use of such tools
  must be fully reported by the Author".
- "The Author shall report any use of AI Tools within the content in the
  Acknowledgements section (or other appropriate place, if no
  Acknowledgements section exists within the External Content)."
- The report includes the tool's name, "Version and extension numbers, if
  available", "Manufacturer", "How the tool was accessed", "Date(s) of use",
  "how the AI was used and on what portions of the manuscript", and "A
  statement confirming that the Author(s) take responsibility for the
  integrity of the content generated".
- "AI Tools shall not be used by Authors to create images or video in
  External Content."

The journal page ("confirm that AI was not used in the development of their
original work") is stricter than the position statement, which allows
reported editing. If a paper used AI for anything beyond editing, ask the
journal before submitting.
