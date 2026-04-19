---
name: arolsen-archives
description: |
  Search Arolsen Archives (collections.arolsen-archives.org) — the
  world's largest collection of documents on victims of Nazi persecution,
  ~30M names across concentration camps, forced labor, DP records, and
  ITS tracing files. Free, no account needed. Uses the site's JSON-over-
  HTTP ASMX backend directly — no browser. Use this skill for WWII-era
  research: forced labor, deportations, concentration camp records,
  Amersfoort/Vught/Westerbork transit camp inmates, displaced persons,
  ITS tracing. Directly relevant for Herman Knijf (Neuengamme /
  forced-labor trail) and any ancestor moved through a Nazi-era
  administrative system. Tier A evidence (primary-source camp documents
  with downloadable scans).
---

# Arolsen Archives — Nazi persecution records

The International Tracing Service (ITS), now the Arolsen Archives,
holds ~30M documents on persons persecuted by the Nazi regime:
concentration camp lists, forced labor cards, DP registrations,
Gestapo files, post-war tracing requests. The web collection at
`collections.arolsen-archives.org` is free and fully open — no account,
no paywall, no rate limit observed.

## Access method

**JSON-over-HTTP ASMX backend** at
`https://collections-server.arolsen-archives.org/ITS-WS.asmx/`.
The Angular SPA is a thin client over this legacy IIS/ASMX service.
Plain `curl` works — **no Playwright needed**.

CORS-open. All endpoints need `Content-Type: application/json` and
`Origin: https://collections.arolsen-archives.org`.

**Critical gotcha:** the server holds query state under an
`ASP.NET_SessionId` cookie. You **must** persist cookies across calls
with `curl -c jar.txt -b jar.txt`, or `GetPersonList` returns `{"d":[]}`
even for common names.

Responses are wrapped in `{"d": ...}`. Decode `d` as the real payload.

## Workflow (verified end-to-end)

### 1. Build the query

```bash
curl -c /tmp/arolsen.jar -b /tmp/arolsen.jar \
  -X POST 'https://collections-server.arolsen-archives.org/ITS-WS.asmx/BuildQueryGlobalForAngular' \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://collections.arolsen-archives.org' \
  -d '{"uniqueId":"abc123","lang":"en","archiveIds":[],"strSearch":"Knijf","synSearch":true}'
```

`synSearch:true` enables phonetic variants — always use it for Dutch
surnames (German clerks transcribed them phonetically: Knyf, Kneyff,
Knejf, de Knijf, de Knyf).

### 2. Count hits

```bash
curl -c /tmp/arolsen.jar -b /tmp/arolsen.jar \
  -X POST 'https://collections-server.arolsen-archives.org/ITS-WS.asmx/GetCount' \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://collections.arolsen-archives.org' \
  -d '{"uniqueId":"abc123","lang":"en","searchType":"person","useFilter":false}'
# -> {"d":"18"}
```

Unfiltered `GetCount` returns `33708578` — the real total name index.

### 3. Fetch results

```bash
curl -c /tmp/arolsen.jar -b /tmp/arolsen.jar \
  -X POST 'https://collections-server.arolsen-archives.org/ITS-WS.asmx/GetPersonList' \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://collections.arolsen-archives.org' \
  -d '{"uniqueId":"abc123","lang":"en","rowNum":0,"orderBy":"LastName","orderType":"asc"}'
```

Returns person list with `ObjId`, `DescId`, dates, places, signature.

### 4. Per-record detail + scans

```bash
# Document detail (no cookie needed)
curl -X POST 'https://collections-server.arolsen-archives.org/ITS-WS.asmx/GetFileByObj' \
  -H 'Content-Type: application/json' \
  -d '{"objId":"76567490","lang":"en"}'

# Archive-series context
curl -X POST 'https://collections-server.arolsen-archives.org/ITS-WS.asmx/GetArchiveInfo' \
  -H 'Content-Type: application/json' \
  -d '{"descId":"915146","level":1,"lang":"en"}'
```

### 5. Download scans directly

Scan images are served from
`https://collections-server.arolsen-archives.org/G/SIMS1/SIMS3/.../NNN.jpg`
**with no auth, no cookie**. You can pipe them straight into
`private/sources/` attached to a Tier A finding.

Human-readable URLs for reference in findings:

```
https://collections.arolsen-archives.org/en/search/person/{ObjId}?s={query}&t={DescId}&p=0
https://collections.arolsen-archives.org/en/document/{ObjId}
```

## Verified example — Knijf search

18 Knijf persons found including:

- **Cornelius KNEJF KNIJF** b. 23 Apr 1923, Amsterdam — signature
  7.5.7 Bundesarchiv "foreigners employed on former Reich territory",
  unit 7648000145 "Jensen–Kuznetsow", subject index: **Forced labour**.
  ObjId 76567490, 2 scan pages, direct JPG download confirmed.
- **Theodorus KNIJF** b. 2 Aug 1920, prisoner #9331 — signature 1.1.1.2
  **Amersfoort Police Transit Camp** individual prisoner files.
- **Christianus KNIJF** b. 5 Mar 1907 — signature 2.1.1.1.

The Amersfoort transit camp series and forced-labor series both have
Knijf hits — directly relevant to the Herman Knijf hardening workflow.

## Signature cheatsheet (top-level series)

| Signature | Content |
|-----------|---------|
| 1.1.x.x | Incarceration / prison records |
| 1.1.1.2 | Amersfoort Police Transit Camp (PDA) |
| 2.1.1.1 | Individual documents, various |
| 7.5.7 | Bundesarchiv — foreigners employed on former Reich territory (forced labor) |

Full schema at collections.arolsen-archives.org/en/archive — but all
endpoints return the signature in the record, so you rarely need it.

## Output format

```
**Source:** Arolsen Archives — {signature} {series name}
**Person:** {LastName} {FirstName} b. {date}, {place of birth}
**ObjId:** {ObjId}
**DescId:** {DescId}
**Document:** https://collections.arolsen-archives.org/en/document/{ObjId}
**Scan URLs:** {direct JPG links}
**Confidence:** Tier A — primary source scan of original camp/forced-labor
administrative document
```

## Limitations

- **Session cookie is load-bearing** — #1 foot-gun. Persist it across
  all four call phases.
- **Dutch surnames are transcribed phonetically** by German clerks —
  always search with `synSearch:true` and try multiple spellings
  (Knyf, Kneyff, de Knijf, de Knyf).
- **No OpenAPI / Swagger** — endpoints were reverse-engineered from
  the Angular SPA. They may change, but are currently stable.
- **Legacy ASMX, not REST** — responses wrapped in `{"d": ...}`.
