---
name: verify-scans
description: |
  Generate a scan verification page for the user to review AI-extracted
  genealogy findings against actual document scans. The user clicks through
  records, confirms or rejects each one, and confirmed records become Tier A
  evidence in the research database. Use this skill when: "verify scans", "show me
  what needs verifying", "review pending scans", "scan verification",
  "/verify-scans", or when the user wants to upgrade research findings
  from Tier C/D to Tier A by visually confirming document scans. Also use
  after a research session that produced scan-backed findings that need
  human confirmation.
---

# Verify Scans — Human-in-the-Loop Tier A Verification

Generate an interactive HTML page where the user reviews document scans
alongside AI analysis, then feed confirmed verdicts back into the research
database as Tier A evidence.

## When to use

After any research session that found records with viewable scans (IIIF
images, archive thumbnails, etc.). The AI reads the scan and writes what
it sees; the user confirms by looking at the actual image.

## Workflow

### 1. Collect pending verifications

Check for existing verification JSON files:

```
private/research/*-verification.json
```

If none exist, or if the user asks to verify results from a specific
research session, query the DB for Tier C/D findings with scan URLs:

```bash
python scripts/research_db.py search "scan" --limit 50
```

Or query directly: findings with tier C/D and raw_markdown containing URLs.

### 2. Build the verification JSON

Each record needs this structure:

```json
{
  "id": "unique-id",
  "iiifUrl": "https://...",
  "name": "Person Name",
  "collection": "Source name",
  "expect": "What the reviewer should look for",
  "aiAnalysis": "What the AI read from the scan (HTML ok)",
  "aiConfidence": "high|medium|low",
  "aiConfidenceText": "90% — brief explanation",
  "metadata": {"key": "value"},
  "sourceUrl": "https://link-to-original"
}
```

**To populate `aiAnalysis`:** Download the scan image to /tmp and use the
Read tool to view it. Describe what you see — names, dates, places. Be
specific about which parts are legible and which are uncertain.

**Confidence levels:**
- `high` (green): 80%+ — text clearly legible, key facts confirmed
- `medium` (yellow): 50-80% — partially legible, main facts likely correct
- `low` (red): <50% — poor quality, uncertain reading

### 3. Generate and open the HTML page

```bash
python scripts/generate_verification.py INPUT.json OUTPUT.html --download
```

The `--download` flag saves images locally so the page works offline.
Then open it:

```bash
xdg-open OUTPUT.html
```

Tell the user:
- Arrow keys or buttons to navigate between records
- **Confirm →** marks as verified and advances
- **Reject →** marks as rejected and advances
- **F** key opens full-resolution lightbox
- **Export verdicts** button (top right) saves results to a JSON file
- Progress saves to localStorage automatically

### 4. Process verdicts

After the user finishes reviewing, read back the verdicts. The user can
either:

a. Click "Export verdicts" in the HTML — saves a `-verdicts.json` file
b. Tell you they're done — read the localStorage state isn't possible,
   so ask them to export first

Read the exported verdicts JSON. For each record:

- **status: "verified"** → Update finding in DB to Tier A via:
  ```bash
  python scripts/research_db.py add-finding '<json with tier A, status VERIFIED>'
  ```
  If the scan was downloaded, copy it to `private/sources/` for archival.

- **status: "rejected"** → Update finding in DB to status REJECTED with
  a note explaining the discrepancy. Keep as Tier D.

- **status: "pending"** → Skip, leave for next verification session.

- **note** field → Include the user's note in the finding record.

### 5. Update the GEDCOM (if applicable)

For verified Tier A records, follow the standard GEDCOM update process:
- Edit the GEDCOM with source citations
- Include the archive reference and scan location

## Image sources that work with this tool

Any URL that serves a JPEG/PNG image works. IIIF is ideal because the
script auto-generates display (1200px) and full-resolution URLs from the
base. Known working sources:

- **CBG Verzamelingen** — IIIF at `cbg.hosting.deventit.net/iiif/image/3.0/{id}/...`
  (thumbnails public, full-res may need subscription)
- **Gelders Archief** — IIIF viewer, extract image URLs from viewer page
- **OpenArchieven** — links to source archive scan viewers
- **WieWasWie** — links to source archive scan viewers
- **Delpher** — newspaper page scans via IIIF

## File locations

- Script: `scripts/generate_verification.py`
- Example JSON: `scripts/example_verification.json`
- Verification JSONs: `private/research/*-verification.json`
- Generated HTML: `private/research/*-verification.html`
- Downloaded images: `private/research/*_images/`
- Verdicts export: saved by user via the HTML export button
