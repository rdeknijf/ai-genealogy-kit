---
name: story
description: >
  Create annotated genealogy narrative PDFs with Typst — engaging family
  stories with academic footnotes, historical images, and beautiful typography.
  Use this skill when: "write a story about the X line", "create a story for Y",
  "make a PDF about this family", "/story", "story for my parents", or any request
  to produce a narrative document about a family line or ancestor. Also trigger
  when the user wants to turn research findings into a presentable document for
  family members. Language defaults to Dutch unless specified otherwise.
---

# Genealogy Story Creator

Create engaging, source-annotated family history narratives as beautiful PDFs.
The output is meant for sharing with family — it should read like a book chapter,
not a research report. Every factual claim gets a footnote citing its source.

## Process

### 1. Scope the story

Ask the user:

- Which family line or person to focus on?
- Who is the audience? (parent, sibling, cousin — this affects framing)
- What language? (default: Dutch)
- Any specific themes to emphasize? (military, migration, occupation, mystery)

### 2. Gather facts

Read the GEDCOM file and research findings. Use `scripts/gedcom_query.py`
if available to trace the line programmatically.

Extract for each person in the line:

- Name, birth/death dates and places, occupation
- Source citations (archive, register, akte number)
- Any colorful details (witnesses, occupations, cause of death, migration)

### 3. Find images

Search Wikimedia Commons for period-appropriate illustrations:

- City views/maps for locations mentioned (prefer 17th-19th century art)
- Occupational illustrations (paper mills, tailors, soldiers)
- Landscape paintings of the regions
- Church buildings where baptisms/marriages occurred

Download to a `story-images/` directory next to the `.typ` file with
descriptive filenames. Use `curl -L` for Wikimedia URLs. Aim for 5-8 images.

### 4. Write the Typst document

Structure:

```
Title page → Narrative chapters → "What we know/don't know" → Genealogy table → Colophon
```

#### Complete starter template

```typst
// Version history:
//   v1 — 2026-03-27 — First edition
#let story-version = "v1 — 27 maart 2026"

// --- Page and font setup ---
#set page(paper: "a4", margin: (top: 3cm, bottom: 3cm, left: 2.8cm, right: 2.8cm))
#set text(font: "New Computer Modern", size: 11pt, lang: "nl")
#set par(justify: true, leading: 0.7em, first-line-indent: 1em)
#set heading(numbering: none)
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  v(2cm)
  text(size: 22pt, weight: "bold")[#it.body]
  v(0.8cm)
}
#show heading.where(level: 2): it => {
  v(0.6cm)
  text(size: 14pt, weight: "bold")[#it.body]
  v(0.3cm)
}

// --- Title page ---
#align(center)[
  #v(4cm)
  #text(size: 28pt, weight: "bold")[De Familie Van Voorbeeld]
  #v(0.5cm)
  #text(size: 14pt, fill: rgb("#555"))[_Acht generaties uit de Veluwe_]
  #v(1cm)
  #line(length: 40%, stroke: 0.5pt + rgb("#ccc"))
  #v(1cm)
  #text(size: 12pt)[Een familiegeschiedenis voor Jan]
  #v(3cm)
  #text(size: 8pt, fill: rgb("#bbb"))[#story-version]
]

// --- Chapter example ---
= De oudste sporen

#set par(first-line-indent: 0em)
_Voorst, Gelderland --- begin negentiende eeuw_
#set par(first-line-indent: 1em)

De oudste voorouder die we met zekerheid kennen is Hendrik van Voorbeeld,
geboren op 14 februari 1804 in Voorst.#footnote[BS Geboorte Voorst, 14 feb.
1804. Gelders Archief, inv 0207, reg 5312.02, akte 39.] Hij trouwde op
23 mei 1830 met Johanna Pieters.#footnote[BS Huwelijk Voorst, 23 mei 1830.
Gelders Archief, akte 18. Vader bruidegom: Willem van Voorbeeld, moeder:
Aaltje Jansen.]

// --- Figure example ---
#figure(
  image("story-images/voorst-1850.jpg", width: 100%),
  caption: [_Gezicht op Voorst_ — lithografie, ca. 1850.
    Wikimedia Commons, publiek domein.],
)

// --- What we know / don't know ---
= Wat we weten --- en wat niet

// Use this section to be honest about gaps and uncertainty.
// Readers trust a story more when it admits what it doesn't know.

// --- Genealogy summary table ---
= Overzicht

#table(
  columns: (auto, 1fr, 1fr, auto),
  fill: (_, row) => if row == 0 { rgb("#f0f0f0") } else { none },
  table.header(
    [*Gen.*], [*Naam*], [*Geboren*], [*Overleden*],
  ),
  [1], [Hendrik van Voorbeeld], [14-02-1804, Voorst], [03-11-1879, Voorst],
  [2], [Willem van Voorbeeld], [~1770], [?],
)

// --- Colophon ---
#v(1fr)
#line(length: 100%, stroke: 0.5pt + rgb("#ccc"))
#set text(size: 8pt, fill: rgb("#888"))
Samengesteld met behulp van Claude Code (Anthropic). Alle genealogische
gegevens zijn geverifieerd tegen originele akten in de genoemde archieven.
Historische context is gecontroleerd door onafhankelijke verificatie.

#story-version
```

#### Font notes

The template uses "New Computer Modern" which is bundled with Typst —
no installation needed. For a warmer look, "Libertinus Serif" works well
but must be installed on the system. Change the `#set text(font: ...)` line.

#### Versioning

Every story file must have a `story-version` variable and version history
in comments. Display the version on the title page (small, gray). Increment
on every content change.

#### Footnote rules

Every factual claim needs a source. Group related facts into one footnote
when they come from the same record. Use these patterns:

| Fact type | Footnote format |
|-----------|----------------|
| Civil record (BS) | `BS Geboorte/Huwelijk/Overlijden [plaats], [datum]. [Archief], inv [X], reg [Y], akte [Z].` |
| Church record (DTB) | `DTB Dopen/Trouwen/Begraven [kerk], [archief], reg [X], akte [Y].` |
| Published genealogy | `[Auteur], "[Titel]," _[Publicatie]_ ([Uitgever], [Jaar]).` |
| Database | `[Database naam], record [ID]. URL: [link].` |
| Oral history | `Familieoverlevering.` |
| Historical context | `Zie [Auteur], _[Boektitel]_ ([Stad], [Jaar]).` |

#### Writing style

- Write in the past tense for historical events, present for analysis
- Address the reader directly when connecting to the audience
- Include sensory/occupational details (what did this work feel like?)
- Be honest about uncertainty — "we don't know" is better than speculation
- Use `---` for em-dashes (Typst renders them correctly)
- Historical context paragraphs: temporarily disable first-line-indent

### 5. Compile

```bash
typst compile story-{name}.typ story-{name}.pdf
```

If `typst` is not installed:

- **macOS:** `brew install typst`
- **Linux:** `cargo install typst-cli` or check your distro's package manager
- **Windows:** `winget install typst` or `cargo install typst-cli`

### 6. Fact-check

After writing, verify all non-genealogical claims (historical context,
geographic descriptions, etymological arguments) using independent sources.
If you have access to multiple AI tools, send the full narrative with
these instructions:

> "This is a genealogy narrative. All genealogical data (birth/death dates,
> marriage records, archive references, family relationships) has been
> independently verified against civil and church records. Do NOT re-verify
> those. Instead: (1) identify all historical context claims and verify
> them — wars, sieges, population numbers, biographical details of non-family
> historical figures, etymological arguments, geographic descriptions; (2)
> think for yourself whether anything else in the text needs verification
> that isn't genealogical data. For each claim you check, state TRUE, FALSE,
> or UNCERTAIN with a brief explanation."

The key insight: let the reviewer **discover** what needs checking rather
than hand-picking claims for them. This catches things you might miss.

## Dependencies

- **Typst CLI** — see install instructions in step 5
- **Font:** New Computer Modern (bundled with Typst, no install needed)
- **Images:** downloaded to `story-images/` next to the `.typ` file
- **GEDCOM tools:** `scripts/gedcom_query.py` (optional, for tracing lines)
