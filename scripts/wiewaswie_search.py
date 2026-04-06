#!/usr/bin/env python3
"""Compact WieWasWie search wrapper for LLM consumption.

Searches 252M+ indexed Dutch civil registry records via the WieWasWie
JSON API. Falls back to OpenArchieven API if Cloudflare blocks the request.

Usage:
    python scripts/wiewaswie_search.py "Knijf"
    python scripts/wiewaswie_search.py "Knijf" --firstname Gijsbert --place Woerden
    python scripts/wiewaswie_search.py "Knijf" --prefix de --type "BS Geboorte"
    python scripts/wiewaswie_search.py "Knijf" --year-from 1800 --year-to 1850
    python scripts/wiewaswie_search.py --detail 55972978
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request

WWW_API = "https://www.wiewaswie.nl/Umbraco/Api/nl-NL/Service"
OA_API = "https://api.openarchieven.nl/1.1/records"


def api_post(url: str, data: dict) -> dict:
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; genealogy-research/1.0)",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def api_get(url: str) -> dict:
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; genealogy-research/1.0)",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def search_wiewaswie(surname: str, *, firstname: str = "", prefix: str = "",
                     place: str = "", doc_type: str = "",
                     year_from: str = "", year_to: str = "",
                     limit: int = 25) -> dict | None:
    """Search via WieWasWie JSON API. Returns None if Cloudflare blocks."""
    payload = {
        "SearchTerm": "",
        "Page": 1,
        "IsAdvancedSearch": True,
        "PersonA": {
            "Achternaam": surname,
            "Tussenvoegsel": prefix,
            "Voornaam": firstname,
            "Patroniem": "",
            "Beroep": "",
            "Rol": "",
            "VoornaamSearchType": 3,
            "TussenvoegselSearchType": 3,
            "AchternaamSearchType": 3,
            "PatroniemSearchType": 3,
            "BeroepSearchType": 3,
            "WithoutTussenvoegsel": False,
        },
        "PersonB": {
            "Voornaam": "", "Tussenvoegsel": "", "Achternaam": "",
            "Patroniem": "", "Beroep": "", "Rol": "",
            "VoornaamSearchType": 3, "TussenvoegselSearchType": 3,
            "AchternaamSearchType": 3, "PatroniemSearchType": 3,
            "BeroepSearchType": 3, "WithoutTussenvoegsel": False,
        },
        "PeriodeVan": year_from,
        "PeriodeTot": year_to,
        "Land": "",
        "Regio": "",
        "Plaats": place,
        "PlaatsSearchType": 3,
        "DocumentType": doc_type,
        "SortColumn": "lastname.sort",
        "SortDirection": 1,
        "FacetCollectieGebied": "",
        "FacetOrganisatie": "",
        "FacetRol": "",
    }
    try:
        return api_post(f"{WWW_API}/GetSearchResults", payload)
    except Exception:
        return None


def search_openarchieven(surname: str, *, firstname: str = "", place: str = "",
                          source_type: str = "", limit: int = 25) -> dict:
    """Fallback: search via OpenArchieven API."""
    name = f"{firstname} {surname}".strip() if firstname else surname
    params: dict = {
        "name": name,
        "number_show": limit,
        "lang": "nl",
        "sort": 1,
    }
    if place:
        params["eventplace"] = place
    if source_type:
        params["sourcetype"] = source_type
    url = f"{OA_API}/search.json?{urllib.parse.urlencode(params)}"
    return api_get(url)


def get_detail(source_doc_id: str) -> dict | None:
    """Get record detail from WieWasWie."""
    try:
        url = f"{WWW_API}/GetSourceDetail?sourceDocumentId={source_doc_id}"
        return api_get(url)
    except Exception:
        return None


def format_www_results(data: dict) -> str:
    total = data.get("Total", 0)
    persons = data.get("Persons", [])
    if not persons:
        return f"No results found (total: {total})"

    lines = [f"Found {total} records (WieWasWie):\n"]
    for i, p in enumerate(persons, 1):
        name_parts = []
        if p.get("Voornaam"):
            name_parts.append(p["Voornaam"])
        if p.get("HasTussenvoegsel") and p.get("Tussenvoegsel"):
            name_parts.append(p["Tussenvoegsel"])
        if p.get("Achternaam"):
            name_parts.append(p["Achternaam"])
        name = " ".join(name_parts)

        parts = [name]
        if p.get("DocumentType"):
            parts.append(p["DocumentType"])
        if p.get("AkteDatum"):
            parts.append(p["AkteDatum"])
        if p.get("AktePlaats"):
            parts.append(p["AktePlaats"])
        if p.get("Rol"):
            parts.append(f"rol: {p['Rol']}")
        scan = "scan" if p.get("HasScan") else ""
        if scan:
            parts.append(scan)
        parts.append(f"id:{p.get('SourceDocumentId', '?')}")

        lines.append(f"  {i}. {' | '.join(parts)}")

    return "\n".join(lines)


def format_oa_results(data: dict) -> str:
    docs = data.get("response", {}).get("docs", [])
    n = data.get("response", {}).get("number_found", 0)
    if not docs:
        return f"No results found (OpenArchieven fallback, total: {n})"

    lines = [f"Found {n} records (OpenArchieven fallback):\n"]
    for i, doc in enumerate(docs, 1):
        date_obj = doc.get("eventdate", {})
        if isinstance(date_obj, dict):
            date = f"{date_obj.get('day','')}-{date_obj.get('month','')}-{date_obj.get('year','')}"
        else:
            date = str(date_obj)
        place = ", ".join(doc.get("eventplace", []))
        ref = f"{doc.get('archive_code', '?')}:{doc.get('identifier', '?')}"
        lines.append(
            f"  {i}. {doc.get('personname', '?')} | {doc.get('eventtype', '?')} | "
            f"{date} | {place} | {doc.get('sourcetype', '')} | ref: {ref}"
        )

    return "\n".join(lines)


def format_detail(data: dict) -> str:
    if not data:
        return "Detail not available"

    lines = []
    # Source info
    if data.get("BronNaam"):
        lines.append(f"Source: {data['BronNaam']}")
    if data.get("AkteType"):
        lines.append(f"Type: {data['AkteType']}")
    if data.get("AkteDatum"):
        lines.append(f"Date: {data['AkteDatum']}")
    if data.get("AktePlaats"):
        lines.append(f"Place: {data['AktePlaats']}")
    if data.get("Collectie"):
        lines.append(f"Collection: {data['Collectie']}")

    # Persons
    persons = data.get("Personen", [])
    if persons:
        lines.append("")
        lines.append("Persons:")
        for p in persons:
            name_parts = []
            if p.get("Voornaam"):
                name_parts.append(p["Voornaam"])
            if p.get("Tussenvoegsel"):
                name_parts.append(p["Tussenvoegsel"])
            if p.get("Achternaam"):
                name_parts.append(p["Achternaam"])
            name = " ".join(name_parts)
            role = p.get("Rol", "?")
            extras = []
            if p.get("Beroep"):
                extras.append(f"beroep: {p['Beroep']}")
            if p.get("Leeftijd"):
                extras.append(f"leeftijd: {p['Leeftijd']}")
            extra_str = f" ({', '.join(extras)})" if extras else ""
            lines.append(f"  - {role}: {name}{extra_str}")

    # Archive reference
    if data.get("Registernaam"):
        lines.append("")
        lines.append(f"Register: {data['Registernaam']}")
    if data.get("Aktenummer"):
        lines.append(f"Akte: {data['Aktenummer']}")

    return "\n".join(lines) if lines else "No detail data"


def main():
    parser = argparse.ArgumentParser(description="Search WieWasWie civil records")
    parser.add_argument("surname", nargs="?", help="Surname to search")
    parser.add_argument("--firstname", default="", help="First name filter")
    parser.add_argument("--prefix", default="", help="Tussenvoegsel (de, van, van der)")
    parser.add_argument("--place", default="", help="Place filter")
    parser.add_argument("--type", default="", help="Document type: 'BS Geboorte', 'BS Huwelijk', 'BS Overlijden'")
    parser.add_argument("--year-from", default="", help="Start year")
    parser.add_argument("--year-to", default="", help="End year")
    parser.add_argument("--limit", type=int, default=25, help="Max results")
    parser.add_argument("--detail", default="", help="Get detail by SourceDocumentId")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if args.detail:
        data = get_detail(args.detail)
        if args.json:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(format_detail(data))
        return

    if not args.surname:
        parser.print_help()
        sys.exit(1)

    # Map document type to OA sourcetype for fallback
    type_map = {
        "BS Geboorte": "BS Geboorte",
        "BS Huwelijk": "BS Huwelijk",
        "BS Overlijden": "BS Overlijden",
    }

    # Try WieWasWie first
    data = search_wiewaswie(
        args.surname, firstname=args.firstname, prefix=args.prefix,
        place=args.place, doc_type=args.type,
        year_from=args.year_from, year_to=args.year_to,
        limit=args.limit,
    )

    if data and data.get("Persons") is not None:
        if args.json:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(format_www_results(data))
    else:
        # Fallback to OpenArchieven
        print("(WieWasWie blocked by Cloudflare, using OpenArchieven fallback)\n",
              file=sys.stderr)
        oa_data = search_openarchieven(
            args.surname, firstname=args.firstname, place=args.place,
            source_type=type_map.get(args.type, ""), limit=args.limit,
        )
        if args.json:
            print(json.dumps(oa_data, indent=2, ensure_ascii=False))
        else:
            print(format_oa_results(oa_data))


if __name__ == "__main__":
    main()
