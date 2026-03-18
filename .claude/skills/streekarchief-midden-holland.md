---
name: streekarchief-midden-holland
description: |
  Search indexed person records at Streekarchief Midden-Holland (samh.nl)
  via Playwright browser automation. Based in Gouda, covers municipalities:
  Gouda, Haastrecht, Schoonhoven, Waddinxveen, Noord-Waddinxveen,
  Moerkapelle, Moordrecht, Ammerstol, Broek, Vlist, and surrounding areas
  in the Midden-Holland region of South Holland. 3M+ person records with
  DTB (doop/trouw/begraven), BS (geboorte/huwelijk/overlijden), and
  Inschrijvingaktes. Uses the Memorix platform (same as Erfgoed Leiden).
  36 Knijf results found, including Gijsbert de Knijf records in Gouda and
  van der Knijf in Waddinxveen. Scans available for most records. Triggers
  on: "search Gouda archive", "Streekarchief Midden-Holland", "SAMH",
  "Haastrecht records", "Schoonhoven records", "/streekarchief-midden-holland",
  or any genealogy research in the Gouda/Midden-Holland area. No login
  required.
---

# Streekarchief Midden-Holland — Gouda Region Archive

Search indexed person records from the regional archive of Midden-Holland,
based in Gouda at the Chocoladefabriek.

No login required for viewing indexed records and scans.

## Coverage

3,061,801 person records. Municipalities: Gouda, Haastrecht, Schoonhoven,
Waddinxveen, Noord-Waddinxveen, Moerkapelle, Moordrecht, Ammerstol,
Broek c.a., Vlist, and surrounding areas.

**Knijf records:** 36 results — de Knijf in Gouda/Haastrecht, van der
Knijf in Noord-Waddinxveen/Broek/Moerkapelle, Knijf in Gouda/Schoonhoven/
Waddinxveen/Vlist.

## Workflow

### 1. Navigate to person search

```
browser_navigate → https://samh.nl/bronnen/genealogie/persons
```

### 2. Simple search

Fill the "Zoek in alle velden" textbox and click "Zoeken".

URL parameter search:

```
https://samh.nl/bronnen/genealogie/persons?ss={"q":"knijf"}
```

The `ss` parameter takes a JSON object with `"q"` as the search term
(same Memorix platform as Erfgoed Leiden).

### 3. Advanced search

Click "Uitgebreid zoeken" to expand the advanced search panel.

Fields available (typical Memorix person search):
- Voornaam
- Patroniem
- Achternaam
- Tussenvoegsel
- Rol

### 4. Facet filters

After searching, results can be filtered using sidebar facet buttons:

| Filter | Description |
|--------|-------------|
| **Bron** | Source collection |
| **Soort akte** | Record type (Doopakte, Geboorteakte, Huwelijksakte, Overlijdensakte, Inschrijvingaktes) |
| **Plaats** | Municipality |
| **Rol** | Role in record (Vader, Moeder, Overledene, Getuige, etc.) |
| **naam Register** | Register name |
| **Periode** | Date range |

### 5. Read results

Results table columns: Voornaam, Patroniem, Achternaam, Rol, Datum, Plaats,
Soort Akte, scan indicator.

25 results per page by default (options: 25/50/100/250). Pagination at
top and bottom.

Scan indicators:
- "Er is een scan beschikbaar, gekoppeld aan de akte!" — direct scan link
- "Er zijn scans van het register beschikbaar!" — register scans

### 6. View record details

Click a result row to expand/navigate to record details. Shows structured
data with all persons in the record, archive reference, and scan links.

### 7. Browse registers

Link at top: "Ga naar bladeren door bronnen" → browse DTB registers by
municipality and date range. Useful for browsing doopboeken page by page
when no indexed records exist for a surname.

## Other collections

The archive also has:
- **Archieven** — archive inventories
- **Bouwtekeningen** — building permits
- **Beeldbank** — image bank
- **Kranten** — newspapers (at kranten.samh.nl)
- **Bibliotheek** — library catalog

## When to use vs other sources

| Source | Use for |
|--------|---------|
| **Streekarchief Midden-Holland** | Gouda, Haastrecht, Schoonhoven, Waddinxveen, Moerkapelle area |
| RHC Rijnstreek | Woerden, Bodegraven, Lopik, Montfoort, Oudewater |
| Erfgoed Leiden | Leiden, Ter Aar, Nieuwkoop, Hillegom |
| Gemeentearchief Alphen | Alphen aan den Rijn, Aarlanderveen, Benthuizen |
| Het Utrechts Archief | Utrecht province (Woerden overlaps with RHC Rijnstreek) |

## Output format

```
## Streekarchief Midden-Holland Result — [record type]

**Person:** [name]
**Role:** [role]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Archive ref:** [reference]
**Scan available:** Yes/No

**Confidence:** Tier B — official archive record from Streekarchief Midden-Holland
```
