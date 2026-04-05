---
name: henk-beijers
description: |
  Search Henk Beijers Archiefcollectie (henkbeijersarchiefcollectie.nl), a vast
  collection of transcribed historical documents from Brabant, primarily Schijndel
  and surrounding villages. 1,000+ Word documents containing full transcriptions
  of schepenprotocollen (1530-1811), notarial records, Bosch Protocol extracts,
  Resoluties Raad van State, cijnsregisters, tiendarchief, and more. Uniquely
  valuable for pre-1811 Brabant research — these are human transcriptions of
  original handwritten records, not indexes. Covers Schijndel, Veghel, Esch,
  Vught, 's-Hertogenbosch, and the broader Meierij van 's-Hertogenbosch region.
  Use this skill whenever researching pre-1811 families in eastern Brabant,
  looking up property transfers, estate divisions, witness lists, or civic
  administration records. Especially valuable for Van der Kant/Cant and de
  Keteler research in Schijndel. Triggers on: "search Henk Beijers", "Schijndel
  schepenprotocol", "Brabant transcriptions", "oud archief Schijndel",
  "Bosch Protocol", "/henk-beijers", or any research needing pre-1811 Brabant
  source transcriptions. No login required. No API — content is static HTML
  pages linking to Word documents (.doc/.docx).
---

# Henk Beijers Archiefcollectie

Search transcribed historical documents from Brabant archives, primarily
Schijndel and surrounding villages. This is a personal archive collection
by researcher Henk Beijers, containing full transcriptions of original
handwritten records from the 14th-19th centuries.

No login required. No API. Content is static HTML with downloadable Word
documents. Search via Google site search or direct document download.

**Important:** The site's TLS certificate is invalid for `www.henkbeijers...`.
Always use plain HTTP: `http://www.henkbeijersarchiefcollectie.nl/`.

## Coverage

**Region:** Eastern North Brabant (Meierij van 's-Hertogenbosch)

**Primary villages:** Schijndel, Veghel, Esch, Vught, 's-Hertogenbosch

**Time period:** ~1300-1811 (some newer material to ~1960)

**1,000+ transcription documents** across record types:

- **Schepenprotocollen** (aldermen's protocols) — property transfers, estate
  divisions, debt acknowledgments, witness lists, legal disputes. Schijndel
  inv.nrs. 41-184 (1530-1811), systematically transcribed.
- **Bosch Protocol** — 's-Hertogenbosch schepenbank records concerning
  Schijndel, 1501-1793. 5,772 deeds across 481 pages. Complete 10-year project.
- **Resoluties Raad van State** — 264 documents covering governance of the
  Meierij (Generaliteitslanden).
- **Resoluties Staten Generaal** — 51 documents.
- **Kwartier Peelland** — 131 documents on Peelland quarter administration.
- **Leen- en Tolkamer** — 41 documents on feudal and toll records.
- **Raad en Rentmeester Generaal** — 56 documents.
- **Tiendarchief Leuven** — Leuven University tithe archive for Schijndel.
- **Cijnsregisters** — ground rent registers.
- **Notarissen** — notarial records for Schijndel.
- **Parochie-archief** — parish archive including Reformed church records.
- **Databases** — Excel databases of names, houses, notarial protocols.

**Key municipalities for current research:**
Schijndel (Van der Kant/Cant, de Keteler lines), Veghel, Esch, Vught,
's-Hertogenbosch, Sint-Oedenrode, Helmond.

## Access method

Static website built with Microsoft FrontPage. No API, no search endpoint.
Two access methods, in order of preference:

### Method 1: Google site search (fastest for name lookup)

Use WebSearch with `site:henkbeijersarchiefcollectie.nl` to find pages
and documents mentioning a specific name or topic. Google indexes both the
HTML pages and the content of the Word documents.

### Method 2: Direct document download and text extraction

Download specific .doc/.docx files via curl and extract text with Python.
Use when you know which document you need, or want to search systematically
across a set of documents.

### Method 3: Browse index pages

Fetch HTML index pages to discover available documents for a section.

## Workflow

### Step 1: Search via Google site search

```bash
# Use WebSearch tool with site: restriction
# Examples:
#   "site:henkbeijersarchiefcollectie.nl van der Kant"
#   "site:henkbeijersarchiefcollectie.nl Keteler schepenprotocol"
#   "site:henkbeijersarchiefcollectie.nl schepenprotocol Schijndel 1650"
```

WebSearch returns direct links to matching HTML pages and .doc/.docx files.

### Step 2: Identify relevant documents

From the search results, identify which documents are relevant. Key sections:

| Section | URL path | Content |
|---------|----------|---------|
| Schepenprotocollen (genealogie) | `genealogie/protocol.NNN.doc` | Name indexes + transcriptions inv. 41-184 |
| Oud archief Schijndel | `historisch_onderzoek/Schijndel_oud_archief/RS.NNN.doc` | Schepenbankarchief transcriptions |
| ORA Schijndel (.docx) | `historisch_onderzoek/Schijndel_oud_archief/ORA Schijndel NNN.docx` | Newer transcriptions (structured) |
| Bosch Protocol | `historisch_onderzoek/erfgoed_s-hertogenbosch/` | 's-Hertogenbosch schepenbank re: Schijndel |
| Veghel | `historisch_onderzoek/Veghel/` | Veghel archive transcriptions |
| Vught | `historisch_onderzoek/Vught/` | Vught archive transcriptions |
| Esch | `historisch_onderzoek/Esch/` | Esch archive transcriptions |
| Resoluties RvS | `historisch_onderzoek/Resoluties_RVS/RRS.NNN.doc` | Raad van State |
| Kwartier Peelland | `historisch_onderzoek/kwartier_peelland/` | Peelland quarter |
| Notarissen | `historisch_onderzoek/notarissen/` | Schijndel notarial records |
| Databases | `historisch_onderzoek/databases/` | Excel databases |

### Step 3: Download and extract text from documents

**For .docx files (preferred — structured, reliable parsing):**

```bash
curl -s -L -o /tmp/henk_doc.docx 'http://www.henkbeijersarchiefcollectie.nl/historisch_onderzoek/Schijndel_oud_archief/ORA%20Schijndel%20120.docx'
```

```python
from docx import Document

doc = Document('/tmp/henk_doc.docx')
text = '\n'.join(p.text for p in doc.paragraphs)

# Search for a family name
for line in text.split('\n'):
    if 'Cant' in line or 'Kant' in line:
        print(line[:300])
```

**For .doc files (older format — use strings extraction):**

```bash
curl -s -L -o /tmp/henk_doc.doc 'http://www.henkbeijersarchiefcollectie.nl/genealogie/protocol.142.doc'
```

```bash
# Extract text with strings (works for all .doc files)
strings /tmp/henk_doc.doc | grep -i 'van der Cant'
```

The `strings` command extracts readable text from binary .doc files.
It captures the document text reliably for searching, though formatting
is lost.

### Step 4: Browse an index page for document discovery

```bash
# Fetch the index page for a section
curl -s -L 'http://www.henkbeijersarchiefcollectie.nl/historisch_onderzoek/oud_archief.htm' -o /tmp/henk_index.html

# Extract all document links
grep -oP 'href="[^"]*\.(doc|docx)"' /tmp/henk_index.html | sed 's/href="//' | sed 's/"$//'
```

**Key index pages:**

- Schepenprotocollen: `http://www.henkbeijersarchiefcollectie.nl/genealogie/genealogie.htm`
- Oud archief: `http://www.henkbeijersarchiefcollectie.nl/historisch_onderzoek/oud_archief.htm`
- Archief Schijndel: `http://www.henkbeijersarchiefcollectie.nl/historisch_onderzoek/archief_schijndel.htm`
- Bosch Protocol: `http://www.henkbeijersarchiefcollectie.nl/historisch_onderzoek/erfgoed_s-hertogenbosch_stadsarchief.htm`
- Veghel: `http://www.henkbeijersarchiefcollectie.nl/historisch_onderzoek/archief_veghel.htm`

### Step 5: Systematic search across multiple documents

For thorough research on a family, download and search multiple documents:

```python
import subprocess
from docx import Document

# Example: search all ORA Schijndel .docx files for a name
target = "van der Kant"
for inv_nr in [120, 121, 126, 127]:
    url = f"http://www.henkbeijersarchiefcollectie.nl/historisch_onderzoek/Schijndel_oud_archief/ORA%20Schijndel%20{inv_nr}.docx"
    path = f"/tmp/ora_{inv_nr}.docx"
    subprocess.run(["curl", "-s", "-L", "-o", path, url])
    try:
        doc = Document(path)
        text = '\n'.join(p.text for p in doc.paragraphs)
        hits = [l for l in text.split('\n') if target in l]
        if hits:
            print(f"\n=== ORA Schijndel {inv_nr}: {len(hits)} hits ===")
            for h in hits[:3]:
                print(f"  {h[:250]}")
    except Exception as e:
        print(f"  Error reading {inv_nr}: {e}")
```

## Document naming conventions

| Prefix | Meaning | Section |
|--------|---------|---------|
| `RS.NNN` | Rechterlijk archief Schijndel (BHIC 5122) | Schepenbankarchief |
| `ORA Schijndel NNN` | Oud Rechterlijk Archief Schijndel | Newer transcriptions |
| `protocol.NNN` | Schepenprotocol inv.nr. NNN | Genealogie section |
| `HAH.NNN` | Helmond archief (cijnsregisters) | Cijnsregisters |
| `LEU.NNN` | Tiendarchief Leuven | Leuven tithe records |
| `RRS.NNN` | Resoluties Raad van State | Governance |
| `BHIC 5122 inv.nr.NN` | BHIC schepenprotocol scans | Gescande bronnen |
| `BP NNNN` | Bossche Protocollen folio number | Bosch Protocol |

## Schepenprotocol inventory numbers for Schijndel

The schepenprotocollen (BHIC access 5122) are numbered by inventory:

- **inv. 41-46**: Oldest protocols (~1530s-1550s), in `genealogie/` section
- **inv. 55-66**: Protocols 1582-1626, transcribed from BHIC scans
- **inv. 87**: Name list available separately
- **inv. 120-127**: Late protocols (~1790s-1811), in ORA .docx format
- **inv. 131-141**: Registers on protocols (elders gepasseerde akten)
- **inv. 142-184**: Main series 1663-1811, systematically transcribed

## Output format

When reporting findings from Henk Beijers Archiefcollectie:

```
**Source:** Henk Beijers Archiefcollectie — [document name]
**Archive ref:** BHIC 5122 inv.nr. [number] (or other archive reference from document)
**Record:** [transcription extract with names, dates, transaction type]
**Document URL:** http://www.henkbeijersarchiefcollectie.nl/[path to document]
**Confidence:** Tier C — volunteer transcription from Henk Beijers Archiefcollectie
(upgrade to Tier B if cross-referenced with BHIC scan)
```

## Confidence tiers

- **Tier C** by default — these are volunteer transcriptions, not official
  indexed records. Henk Beijers is a respected researcher but transcription
  errors exist (he notes this himself on the site).
- **Upgrade to Tier B** when the transcription can be cross-referenced with
  the original scan at BHIC (many of the BHIC 5122 inventory numbers have
  digitized scans available).
- **Treat as Tier D** if the transcription contains uncertain readings
  (marked with `[?]`, `[denk ik]`, or similar notations in the text).

## Limitations

- **No search API** — the site is static HTML + Word documents. Google site
  search is the only way to search across all content without downloading
  individual files.
- **Mixed file formats** — older documents are .doc (Word 97-2003), newer
  ones are .docx. The .doc format requires `strings` extraction; .docx can
  be parsed with `python-docx`.
- **TLS certificate invalid** — always use `http://` not `https://` for
  curl. WebSearch and WebFetch may auto-upgrade to HTTPS and fail; use
  curl directly.
- **Transcription quality varies** — some older documents have typos
  (letters stuck to wrong words, as noted by the author). Cross-reference
  important findings with BHIC scans.
- **Not all names indexed** — the schepenprotocol transcriptions often only
  list the main parties (buyers, sellers). Witnesses, neighbors mentioned
  in boundary descriptions, and other names may only appear in the full
  text, not in register indexes.
- **Encoding** — HTML pages use Windows-1252 encoding. Some diacritics may
  display incorrectly when fetched with curl; this rarely affects name
  searches.
- **Some .doc files are actually WordPerfect** — a few older documents
  (especially Resoluties) are WordPerfect format despite .doc extension.
  `strings` extraction still works for these.
