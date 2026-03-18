---
name: wiewaswie
description: |
  Search Dutch civil registry records (births, marriages, deaths) on WieWasWie.nl
  via Playwright browser automation. Use this skill whenever you need to look up or
  verify a person in Dutch civil records, check a birth/marriage/death date against
  official archives, or find parents/spouses from indexed Burgerlijke Stand records.
  Triggers on: "look up on wiewaswie", "check the birth record", "find the marriage
  certificate", "verify this date in the civil registry", "/wiewaswie", or any request
  to search Dutch genealogical records for a specific person. Also use when comparing
  GEDCOM data against official sources or when a Tier B verification is needed.
---

# WieWasWie Lookup

Search the WieWasWie database (252M+ indexed Dutch civil registry records) using
Playwright browser tools. This returns official archive-indexed data — Tier B
confidence in the genealogy project's verification framework.

## What to extract from the user's request

- **surname** (required)
- **prefix** — tussenvoegsel like "de", "van", "van de" (optional)
- **first_name** (optional)
- **patronymic** (optional)
- **place** (optional)
- **year_from** / **year_to** (optional)
- **document_type** — geboorte, huwelijk, overlijden (optional)

## Step-by-step workflow

### 1. Navigate to advanced search

```
browser_navigate → https://www.wiewaswie.nl/nl/zoeken/?advancedsearch=1
```

### 2. Fill the search form

Use `browser_fill_form` with these fields:

| Field | Label | Type | Notes |
|-------|-------|------|-------|
| Surname | "Achternaam" | textbox | |
| Prefix | "Tussenvoegsel" | textbox | "de", "van", etc. |
| First name | "Voornaam" | textbox | |
| Patronymic | "Patroniem" | textbox | |
| Year from | first spinbutton | spinbutton | These are spinbuttons, not textboxes — Playwright needs the right type |
| Year to | second spinbutton | spinbutton | Same — spinbutton |
| Place | "Plaats" | textbox | Use the municipality name (see place names section below) |

### 3. Submit and read results

Click the "Zoek" button, then take a snapshot. Results appear as a table:
Achternaam, Voornaam, Patroniem, Plaats, Datum, Documenttype, Scan.

If there are multiple results, list them so the right one can be picked.

### 4. Open a result's details

Click the result row. The detail view loads **inside an iframe** — take a
snapshot after clicking to read its content. This is easy to miss because
the snapshot looks like nothing changed until you look inside the iframe.

### 5. Extract structured data

The iframe uses term/definition pairs (`<dt>`/`<dd>`). What's available
depends on the document type:

**BS Geboorte (birth):**
Kind (child), Geslacht (gender), Vader (father) with beroep and leeftijd,
Moeder (mother) with beroep, Gebeurtenisdatum, Gebeurtenisplaats, Registratiedatum.

**BS Huwelijk (marriage):**
Bruidegom (groom) and Bruid (bride) each with age, birthplace, occupation.
Both sets of parents (Vader/Moeder bruidegom, Vader/Moeder bruid). Date and place.

**BS Overlijden (death):**
Overledene (deceased) with age, Partner, Vader/Moeder, date and place.

**Always extract the archive reference:**
Erfgoedinstelling, Archief number, Registratienummer, Aktenummer, Collectie.

### 6. Check for linked records

At the bottom of the detail view, look for links labeled things like
"Huwelijk ouders" (parents' marriage) — these connect to related civil
records and are very useful for extending family lines. Also grab the
"Naar bron" link if present — it goes to the original scanned document
at the archive's website.

## Birth date vs registration date

Dutch civil records carry two dates, and confusing them is a common source
of errors in family trees:

- **Gebeurtenisdatum** = the actual event date (when the baby was born)
- **Registratiedatum** = when the event was declared at the town hall

Births were typically registered 1–3 days after the actual birth. The results
table in WieWasWie shows the *registration* date. The detail view shows both.
For GEDCOM, use the **gebeurtenisdatum** (the actual birth date).

## Place names

Dutch civil records use the **municipality** (gemeente), not the village.
If a village name returns no results, try the municipality instead:

- Bennekom, Lunteren, Otterlo → **Ede**
- Voorthuizen, Garderen, Barneveld village, Harselaar → **Barneveld**
- Zwartebroek → **Barneveld** or **Nijkerk**

## Output format

```
## WieWasWie Result — [document type]

**Person:** [name]
**Event:** [type], [gebeurtenisdatum] in [gebeurtenisplaats]
**Registered:** [registratiedatum] in [akteplaats]

**Father:** [name], [occupation], age [age]
**Mother:** [name], [occupation]

**Archive:** [erfgoedinstelling], archief [nr], reg [nr], akte [nr]
**Collection:** [collectie]
**Scan:** [naar bron URL if available]
**Linked records:** [list any gelinkte akten]

**Confidence:** Tier B — official civil registry record from [archive name]
```

## Login status

Playwright uses its own browser profile, so it's not logged in to CBG.
Basic search works fine without login. Premium features (wildcards, searching
two people at once) aren't available. To narrow large result sets, add place
or tighten the date range rather than relying on wildcards.
