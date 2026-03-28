---
name: familysearch
description: |
  Search the FamilySearch historical records database via playwright-cli browser
  automation. Use this skill when searching for genealogical records on
  FamilySearch.org — billions of birth, marriage, death, census, and other
  records worldwide. Triggers on: "search familysearch", "check familysearch",
  "look up on familysearch", "/familysearch", or when you need international
  records beyond Dutch/Belgian archives. Requires login — credentials are in .env.
---

# FamilySearch — Historical Records Search

Search billions of genealogical records worldwide. FamilySearch is free and
nonprofit, with extensive collections including civil registries, church records,
census records, immigration records, and more.

**Requires login** — credentials are stored in `.env` as `FAMILYSEARCH_USER`
and `FAMILYSEARCH_PASSWORD`.

## Browser automation via playwright-cli

All browser interaction uses `playwright-cli` via Bash. Use a named session
to keep the browser open across multiple commands:

```bash
# Open browser (once per session)
playwright-cli -s=familysearch open

# Navigate
playwright-cli -s=familysearch goto "https://www.familysearch.org/en/search/"

# Get page snapshot (returns file path)
playwright-cli -s=familysearch snapshot
# Read the snapshot file to find element refs
cat .playwright-cli/<snapshot-file>.yml

# Interact using refs from snapshot
playwright-cli -s=familysearch fill <ref> "search text"
playwright-cli -s=familysearch click <ref>

# Close when done
playwright-cli -s=familysearch close
```

**Important:** After each action that changes the page (click, fill+submit,
goto), take a new snapshot to get updated refs. Refs change between snapshots.

## When to use FamilySearch vs other sources

- **WieWasWie** — Dutch civil registry records with structured results
- **OpenArchieven** — aggregated Dutch/Belgian archives, wide net
- **Gelders Archief** — Gelderland-specific records with scans
- **FamilySearch** — best for international records, church records,
  collections not indexed elsewhere, and cross-referencing Dutch records
  with a second independent source

## Login workflow

FamilySearch requires authentication. The playwright-cli session persists
cookies, so login is only needed once per browser session. Use
`state-save`/`state-load` to persist auth across sessions.

### 1. Check if already logged in

```bash
playwright-cli -s=familysearch goto "https://www.familysearch.org/en/search/"
playwright-cli -s=familysearch snapshot
```

Read the snapshot file. If it shows `button "Account: Rutger de Knijf"` in
the header, you're already logged in. Skip to step 3.

### 2. Log in (if needed)

```bash
playwright-cli -s=familysearch goto "https://www.familysearch.org/en/"
playwright-cli -s=familysearch snapshot
```

Read the snapshot, find the "Sign In" button ref, then:

```bash
playwright-cli -s=familysearch click <sign-in-ref>
playwright-cli -s=familysearch snapshot
```

On the login page, find the Username and Password field refs:

```bash
playwright-cli -s=familysearch fill <username-ref> "$FAMILYSEARCH_USER"
playwright-cli -s=familysearch fill <password-ref> "$FAMILYSEARCH_PASSWORD"
playwright-cli -s=familysearch click <submit-ref>
```

**Important:** Read credentials from `.env` using the Read tool — do NOT
hardcode them. The password contains special characters (`!@%^`) and
must be used exactly as stored.

After login, you may see a "Please confirm your contact information" page.
Click "Continue" to proceed.

If a cookie consent banner appears, click "Accept".

**Save auth state for reuse:**

```bash
playwright-cli -s=familysearch state-save .playwright-cli/familysearch-auth.json
```

**Load saved auth in future sessions:**

```bash
playwright-cli -s=familysearch open
playwright-cli -s=familysearch state-load .playwright-cli/familysearch-auth.json
```

### 3. Search historical records

```bash
playwright-cli -s=familysearch goto "https://www.familysearch.org/en/search/"
playwright-cli -s=familysearch snapshot
```

The search form has these fields:

- **First Names** — textbox
- **Last Names** — textbox
- **Birth Place** — combobox (type to search, e.g., "Netherlands" or city name)
- **Birth Year** — textbox

Find the refs in the snapshot, fill the fields, then click "Search".

For more filters, click **"More Options"** which expands additional fields:

- Death place and year
- Marriage place and year
- Residence place and year
- Any place and year
- Gender
- Relationship filters (spouse, parents, etc.)

### 4. Search sub-types

The search page has tabs for different record types:

- **Records** — `/en/search` — historical records (primary use)
- **Full Text** — `/en/search/full-text` — full-text search across documents
- **Images** — `/en/records/images` — browse digitized document images
- **Family Tree** — `/en/search/tree` — search the shared family tree
- **Genealogies** — `/en/search/genealogies` — user-submitted genealogies
- **Catalog** — `/en/search/catalog` — library catalog of microfilm/records
- **Books** — `/en/library/books/` — digitized books
- **Wiki** — `/en/wiki/Main_Page` — research guidance wiki

### 5. Read search results

```bash
playwright-cli -s=familysearch snapshot
```

Results show a list with:

- Person name
- Event type and date
- Location
- Collection name

Find the ref for a result and click it to see the full record detail page.

### 6. Record detail page

Shows structured data including:

- Person details (name, gender, age)
- Event date and place
- Related persons (parents, spouse, witnesses)
- Source collection and reference
- Link to browse the original document image (if digitized)

**Important:** FamilySearch often has scanned images of original documents.
Click "View image" or similar links to see the actual document — this
elevates the finding from Tier B to Tier A if you can read the original.

### 7. Search by collection

To search within a specific collection (e.g., "Netherlands, Civil Registration"):

1. On the search page, scroll down to "Find a Collection"
2. Type the collection name in the "Collection Title" combobox
3. Select the matching collection
4. This opens a collection-specific search form

Alternatively, browse all collections:

```bash
playwright-cli -s=familysearch goto "https://www.familysearch.org/en/search/collection/list"
```

### 8. Search by place

To find records for a specific location:

1. On the search page, scroll down to "Search by Place"
2. Type the country/province/state in the combobox
3. This shows available collections and resources for that area

## Key Dutch collections on FamilySearch

- Netherlands, Civil Registration (births, marriages, deaths)
- Netherlands, Church Records (DTB — dopen, trouwen, begraven)
- Netherlands, Population Registers
- Netherlands, Notarial Records
- Netherlands, Military Records

## Output format

```
## FamilySearch Result — [record type]

**Person:** [name]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]
**Spouse:** [name] (if applicable)

**Collection:** [collection name]
**FamilySearch ref:** [record URL or reference]
**Original image:** [available / not available]

**Confidence:** Tier B — indexed record from FamilySearch collection
(Tier A if original image was reviewed)
```

## Tips

- FamilySearch has the largest free collection of Dutch church records (DTB),
  which predate the civil registry (pre-1811)
- Use "Full Text" search for finding names in unindexed documents
- The Family Tree is user-contributed and may contain errors — always verify
  against actual records
- Some record images are restricted to viewing at FamilySearch Centers only
- Wildcard searches: use `*` for partial name matching
- For Dutch names, try both with and without prefixes (e.g., "de Knijf" and "Knijf")
- Use `playwright-cli -s=familysearch screenshot` to capture record images
