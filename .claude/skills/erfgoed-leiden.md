---
name: erfgoed-leiden
description: |
  Search indexed person records and scanned documents at Erfgoed Leiden en
  Omstreken (erfgoedleiden.nl) via Playwright browser automation. Covers the
  Leiden region of South Holland province including: Hillegom, Katwijk, Kaag en
  Braassem, Leiden, Leiderdorp, Lisse, Nieuwkoop, Noordwijk, Oegstgeest,
  Teylingen, Zoeterwoude. Also has records for Ter Aar, Zevenhoven, Nieuwveen,
  Woubrugge, Sassenheim, Rijnsburg, Leimuiden, Hoogmade, Alkemade, and
  Achttienhoven. Does NOT cover Alphen aan den Rijn. 398+ Knijf person records
  found here, mainly in Ter Aar (179) and Nieuwkoop (67). Record types include
  DTB (Dopen/Trouwen/Begraven), BS (Geboorte/Huwelijk/Overlijden),
  Bevolkingsregister, Notariële akten, and more. Triggers on: "search Erfgoed
  Leiden", "look up in Leiden archive", "check Leiden records", "Ter Aar
  records", "Nieuwkoop records", "/erfgoed-leiden", or any genealogy research in
  the Leiden/South Holland region. No login required.
---

# Erfgoed Leiden en Omstreken — Leiden Region Archive

Search indexed person records and scanned documents from Erfgoed Leiden en
Omstreken. Covers the Leiden region of South Holland province.

No login required for viewing indexed records and scanned documents.

## Coverage

**Municipalities with Knijf records:** Ter Aar (179), Leiden (75), Nieuwkoop
(67), Hillegom (29), Zevenhoven (14), Lisse (6), Nieuwveen (6), Woubrugge (6),
Leiderdorp (3), Leimuiden (3), Noordwijk (2), Rijnsburg (2), Sassenheim (2),
Achttienhoven (1), Alkemade (1), Hoogmade (1), Voorhout (1).

**NOT covered:** Alphen aan den Rijn (separate archive), Woerden (Het Utrechts
Archief / RHC Rijnstreek), Gouda (Streekarchief Midden-Holland).

## Workflow

### 1. Navigate to person search

```
browser_navigate → https://www.erfgoedleiden.nl/collecties/personen/zoek-op-personen
```

### 2. Simple search

The page has a search box at the top. Type a surname and click "Zoeken".

URL parameter search works:

```
https://www.erfgoedleiden.nl/collecties/personen/zoek-op-personen?ss={"q":"knijf"}
```

The `ss` parameter takes a JSON object with `"q"` as the search term.

### 3. Advanced search

Click **"Uitgebreid zoeken"** to expand the advanced search panel.

**Eerste persoon (First person):**

| Field | Description |
|-------|-------------|
| Voornaam | First name |
| Patroniem | Patronymic |
| Tussenvoegsel | Prefix ("de", "van", etc.) |
| Achternaam | Surname |
| Rol | Role dropdown (see Role options below) |

**Tweede persoon (Second person):** Same fields as first person — useful for
finding couples.

**Registratie type checkboxes:**

| Type | Description | Era |
|------|-------------|-----|
| DTB Dopen | Baptism records | Pre-1811 |
| DTB Trouwen | Marriage records | Pre-1811 |
| DTB Begraven | Burial records | Pre-1811 |
| BS Geboorte | Birth certificates | Post-1811 |
| BS Huwelijk | Marriage certificates | Post-1811 |
| BS Overlijden | Death certificates | Post-1811 |
| BS Echtscheiding | Divorce records | Post-1811 |
| Bevolkingsregister | Population register | Various |
| Notariële akten | Notarial deeds | Various |
| Militieregisters | Military registers | 19th century |
| Adresboeken | Address books | Various |
| Attestaties Doopsgezinden | Mennonite attestations | Various |
| Bonboeken | Receipt books | Various |
| Borgbrieven | Surety letters | Various |
| Collaterale successie | Collateral inheritance | Various |
| Kohier Gedwongen Leningen | Forced loan registers | Various |
| Lijfrente | Annuity records | Various |
| Oud Rechterlijke Akten | Old judicial records | Pre-1811 |
| Paspoorten | Passports | Various |
| Politierapporten | Police reports | Various |
| Poorterboeken | Citizenship registers | Various |
| Transportregisters | Property transfer registers | Various |

**Role dropdown options:** aangever, arrestant, begunstigde, borg, bruid,
bruidegom, dader, eerdere man, eerdere vrouw, ex-man, ex-vrouw, genoemd,
geregistreerde, getuige, heffer, kind, koper, lidmaat, lijk, loteling, moeder,
moeder bruid, moeder bruidegom, nachtverblijver, ontvanger, overledene, partner,
plaatsvervanger, poorter, relatie, slachtoffer, vader, vader bruid, vader
bruidegom, verdachte, verkoper.

### 4. Facet filters

After searching, results can be filtered using sidebar facet buttons:

| Filter | Description |
|--------|-------------|
| **Bron** | Source type (BS Geboorte, DTB Dopen, etc.) |
| **Gemeente** | Municipality |
| **Plaats** | Place within municipality |
| **Rol** | Role in record |
| **Periode** | Date range |

Click a filter button to expand options with counts. Click an option to filter.
Active filters appear under "Actieve filters:" and can be removed by clicking
them.

### 5. Read results

Results appear in a table with columns: Voornaam, Patroniem, Achternaam, Plaats,
Rol, Datum, Type registratie.

25 results per page. Pagination at top and bottom with page number input and
Volgende/Vorige links.

Scan indicator icons:
- "Er is een scan beschikbaar, gekoppeld aan de akte!" — direct scan of the
  record
- "Er zijn scans van het register beschikbaar!" — scans of the register (not
  linked to specific page)

### 6. View record details

Click a result row to expand inline details showing:

- **Source heading** (e.g., "Overlijdensregister van Nieuwkoop, 1853 - 1862;")
- **Soort registratie** and **Gemeente**
- **Bijzonderheden** — additional details (aktenaam, timestamps, remarks)
- **Archive reference** — link to Inventarisnummer/Archiefnummer
- **Person list** with roles (Overledene, Relatie, Vader, Moeder, etc.)
- **Bronvermelding** — full citation with archive/inventory/akte numbers
- **Scan thumbnails** — click "Bekijk akte" to view, "Download scan" to download
- **Paginaweergave** link — opens full page view of the record

### 7. Full page view

The "Paginaweergave" link opens a dedicated page at:

```
/collecties/personen/zoek-op-personen/deeds/[UUID]?person=[UUID]
```

This shows the same data in a full-page layout with larger scan viewer.

## URL structure

**Search URL:**

```
https://www.erfgoedleiden.nl/collecties/personen/zoek-op-personen?ss={"q":"search term"}
```

**With facet filter:**

```
https://www.erfgoedleiden.nl/collecties/personen/zoek-op-personen/persons?f={"search_s_deed_type_title":{"v":"DTB Dopen"}}&ss={"q":"knijf"}
```

**Pagination:**

```
&page=2
```

## Global search

The site also has a global search at:

```
https://www.erfgoedleiden.nl/zoekresultaten?trefwoord=knijf
```

This shows results across all collections: Archieven, Beelden, Kranten (493
newspaper hits!), Personen, Monumenten, Bibliotheek, etc. Click "Personen" to go
to person results.

## Knijf records overview

The 398 Knijf records break down as:
- **BS Overlijden:** 128 (death certificates)
- **BS Geboorte:** 113 (birth certificates)
- **BS Huwelijk:** 79 (marriage certificates)
- **DTB Dopen:** 27 (baptisms, mostly Leiden branch — Arie/Abraham Knijf)
- **DTB Begraven:** 21 (burials)
- **Notariële akten:** 18 (notarial deeds, Leiden)
- **DTB Trouwen:** 9 (marriages)
- **Others:** Bevolkingsregister (1), Militieregisters (1), Adresboeken (1)

The Leiden DTB records appear to be a separate "de Knijf" branch (Abraham de
Knijf, Arie Knijf) centered in Leiden, NOT the Woerden patrilineal line.

## When to use vs other sources

| Source | Use for |
|--------|---------|
| **Erfgoed Leiden** | Leiden region, Ter Aar, Nieuwkoop, Zevenhoven records |
| Het Utrechts Archief | Utrecht province (Woerden, Utrecht city, Amersfoort) |
| RHC Rijnstreek | Woerden, Bodegraven, Lopik, Montfoort area |
| Gelders Archief | Gelderland province (Ede, Barneveld, Apeldoorn) |
| WieWasWie | National coverage, structured person lookups |
| OpenArchieven | Wide net across all Dutch/Belgian archives |

## Output format

```
## Erfgoed Leiden Result — [record type]

**Person:** [name]
**Role:** [role]
**Event:** [type], [date] in [place]

**Father:** [name]
**Mother:** [name]

**Archive ref:** Archiefnummer [nr], Inventarisnummer [nr], Aktenummer [nr]
**Scan available:** Yes/No

**Confidence:** Tier B — official archive record from Erfgoed Leiden
```
