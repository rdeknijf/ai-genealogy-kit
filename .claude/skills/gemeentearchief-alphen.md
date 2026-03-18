---
name: gemeentearchief-alphen
description: |
  Search indexed person records at Gemeentearchief Alphen aan den Rijn
  (gemeentearchief.alphenaandenrijn.nl) via Playwright browser automation. Uses
  the same MAIS/Archieven.nl platform as Het Utrechts Archief and Gelders
  Archief. Covers municipalities: Alphen aan den Rijn, Aarlanderveen,
  Benthuizen, Hazerswoude, Koudekerk, and surrounding areas in the Rijnstreek
  region of South Holland. Has DTB records, Burgerlijke Stand, Bevolkingsregister,
  and Notariële Akten. Known to have "de Knijf" / "van der Knijf" records from
  Aarlanderveen and Benthuizen. Triggers on: "search Alphen archive", "look up
  in Alphen aan den Rijn", "Aarlanderveen records", "Benthuizen records",
  "/gemeentearchief-alphen", or any genealogy research in the Alphen aan den
  Rijn area. No login required.
---

# Gemeentearchief Alphen aan den Rijn

Search indexed person records from the municipal archive of Alphen aan den Rijn.
Uses the MAIS/Archieven.nl platform (same as Het Utrechts Archief, Gelders
Archief).

No login required for viewing indexed records.

## Coverage

Municipalities: Alphen aan den Rijn, Aarlanderveen, Benthuizen, Hazerswoude,
Koudekerk, and surrounding areas.

**Knijf records:** 863 total person results, mostly "de Knijf" from
Aarlanderveen. 14 DTB results (all begraafinschrijvingen from Benthuizen and
Aarlanderveen — "van der Knijf" branch). Zero doopinschrijvingen for Knijf.

## Workflow

### 1. Navigate to person search

**All persons (across all record types):**

```
browser_navigate → https://gemeentearchief.alphenaandenrijn.nl/index.php/collectie?mivast=105&mizig=100&miadt=105&miview=tbl&milang=nl
```

**DTB records only (Doop-, trouw- en begraafinschrijvingen):**

```
browser_navigate → https://gemeentearchief.alphenaandenrijn.nl/index.php/collectie?mivast=105&mizig=323&miadt=105&miview=tbl&milang=nl
```

**Civil registry only (Burgerlijke Stand):**

```
browser_navigate → https://gemeentearchief.alphenaandenrijn.nl/index.php/collectie?mivast=105&mizig=324&miadt=105&miview=tbl&milang=nl
```

### 2. Simple search

Fill in the "Alle velden" textbox and click "Zoek".

URL parameter: `&mizk_alle=knijf`

### 3. Advanced search

Click **"Uitgebreid zoeken"** to expand the advanced search panel.

**Persoon fields:**

| Field | Description |
|-------|-------------|
| Achternaam | Surname |
| Tussenvoegsel | Prefix ("de", "van der", etc.) |
| Voornaam | First name |
| Rol | Role (Dopeling, Vader, Moeder, Getuige, etc.) |

Note: This archive does NOT have a Patroniem field (unlike Erfgoed Leiden).

**Overige fields:**

| Field | Description |
|-------|-------------|
| Plaats | Municipality |
| Bron | Source type dropdown |
| Periode | Date range (dd-mm-yyyy, mm-yyyy, or yyyy) |

**Bron dropdown options:**

| Option | Description | Era |
|--------|-------------|-----|
| Doopinschrijving | Baptism | Pre-1811 |
| Trouwinschrijving | Marriage | Pre-1811 |
| Begraafinschrijving | Burial | Pre-1811 |
| Geboorteakte | Birth certificate | Post-1811 |
| Huwelijksakte | Marriage certificate | Post-1811 |
| Overlijdensakte | Death certificate | Post-1811 |
| Echtscheidingsakte | Divorce | Post-1811 |
| Erkenningsakte | Recognition deed | Post-1811 |
| Persoon in akte | Person in deed | Various |
| Persoon in bevolkingsregister | Population register | Various |
| Bouwdossier | Building permit | Various |

**Bron URL parameter:** `&mib1=156` (Doopinschrijving), same MAIS codes as other
archives.

### 4. Read results

Results table: columns vary by search type.

- **All persons:** Voornaam, Achternaam, Rol, Plaats, Datum
- **DTB:** Registratiedatum, Beschrijving, Gemeente

Facet filters available: Bron, Gemeente (for DTB), Rol (for all persons).

### 5. View record details

Click a result row to expand inline details (same MAIS interface as other
archives). Shows structured data, archive reference, and scan links.

### 6. Scans

Records link to scans when available. The archive holds originals of DTB records
dating from 1661–1812.

## URL parameters

Same MAIS platform as Het Utrechts Archief. Key parameters:

| Parameter | Value | Description |
|-----------|-------|-------------|
| mivast | 105 | Archive ID |
| mizig | 100 | All persons search |
| mizig | 323 | DTB search |
| mizig | 324 | Civil registry search |
| mizig | 328 | Notarial deeds search |
| miadt | 105 | Archive ID (repeated) |
| miview | tbl | Table view |
| milang | nl | Language |
| mizk_alle | | "Alle velden" search term |
| mib1 | 156 | Doopinschrijving filter |

## Other collections

The Personen page also links to:

- **Bevolkingsregister** (`mizig=94`)
- **Notariële Akten** (`mizig=328`)
- **Gerechtelijke akten** (`mizig=329`)

## When to use vs other sources

| Source | Use for |
|--------|---------|
| **Gemeentearchief Alphen** | Alphen, Aarlanderveen, Benthuizen, Hazerswoude, Koudekerk records |
| Erfgoed Leiden | Leiden, Ter Aar, Nieuwkoop, Hillegom — does NOT cover Alphen |
| Het Utrechts Archief | Utrecht province (Woerden, Utrecht city) — does NOT cover Alphen |
| RHC Rijnstreek | Woerden, Bodegraven, Lopik area |

## Output format

```
## Gemeentearchief Alphen Result — [record type]

**Person:** [name]
**Role:** [role]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Archive ref:** [reference numbers]
**Scan available:** Yes/No

**Confidence:** Tier B — official archive record from Gemeentearchief Alphen aan den Rijn
```
