#!/usr/bin/env python3
"""Compact OpenArchieven API wrapper for LLM consumption.

Searches 363M+ records across dozens of Dutch archives that feed into
OpenArchieven. Returns minimal text instead of raw JSON.

Supported archive shortcuts (or use any archive_code directly):
    gld          Gelders Archief — Gelderland province
    nha          Noord-Hollands Archief — Haarlem + North Holland
    hco          Collectie Overijssel — Overijssel province
    ghn          Nationaal Archief — national records, WWII, CABR
    nim          NIMH — military history: stamboeken, personnel
    hua          Het Utrechts Archief — Utrecht province (limited in OA)
    (none)       Search ALL archives

Usage:
    python scripts/openarchieven_search.py "Aalbert Loois" --place Apeldoorn
    python scripts/openarchieven_search.py "Knijf" --archive gld --type "BS Geboorte"
    python scripts/openarchieven_search.py --detail gld:E42F4078-A7DC-4D51-AD22-5DAFDC72DE59
    python scripts/openarchieven_search.py --list-archives
    python scripts/openarchieven_search.py "Loois" --period 1800-1860
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request

API_BASE = "https://api.openarchieven.nl/1.1/records"

# Well-known archive codes with descriptions
ARCHIVES = {
    "gld": "Gelders Archief — Gelderland: Apeldoorn, Arnhem, Nijmegen, Zutphen, etc.",
    "nha": "Noord-Hollands Archief — Haarlem, North Holland: 12.7M records",
    "hco": "Collectie Overijssel — Zwolle, Deventer, Kampen, Enschede: 2M+ records",
    "ghn": "Nationaal Archief — national records, WWII CABR, colonial",
    "nim": "NIMH — military history: stamboeken (141K), persoonskaarten (64K)",
    "hua": "Het Utrechts Archief — Utrecht province (limited coverage in OA)",
    "cod": "Centraal Bureau voor Genealogie",
    "wba": "West-Brabants Archief — Breda, Bergen op Zoom",
    "sad": "Stadsarchief Dordrecht — Dordrecht region",
    "raa": "Regionaal Archief Alkmaar",
    "gar": "Gemeentearchief Rotterdam",
    "saa": "Stadsarchief Amsterdam (via OA)",
    "ran": "Regionaal Archief Nijmegen — Nijmegen city: BS, DTB, bevolkingsregister, Vierdaagse",
    "gae": "Gemeentearchief Ede — Ede, Bennekom, Lunteren: BS, bevolkingsregister, militieregisters",
    "gab": "Gemeentearchief Barneveld — Barneveld, Voorthuizen: militieregisters 1813-1941",
}


def api_get(url: str) -> dict:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def search(name: str, *, place: str = "", source_type: str = "",
           archive: str = "", limit: int = 20,
           period_start: int = 0, period_end: int = 0) -> dict:
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
    if archive:
        params["archive_code"] = archive
    if period_start:
        params["period_start"] = period_start
    if period_end:
        params["period_end"] = period_end
    url = f"{API_BASE}/search.json?{urllib.parse.urlencode(params)}"
    return api_get(url)


def detail(archive_code: str, identifier: str) -> dict:
    params = {
        "identifier": identifier,
        "archive_code": archive_code,
        "lang": "nl",
    }
    url = f"{API_BASE}/show.json?{urllib.parse.urlencode(params)}"
    return api_get(url)


def format_date(d: dict | None) -> str:
    if not d:
        return "?"
    if isinstance(d, str):
        return d
    day = d.get("day") or d.get("Day", "")
    month = d.get("month") or d.get("Month", "")
    year = d.get("year") or d.get("Year", "")
    parts = [str(p) for p in [day, month, year] if p]
    return "-".join(parts) if parts else "?"


def format_search_results(data: dict) -> str:
    docs = data.get("response", {}).get("docs", [])
    n = data.get("response", {}).get("number_found", 0)
    if not docs:
        return f"No results found (0/{n})"

    lines = [f"Found {n} records:\n"]
    for i, doc in enumerate(docs, 1):
        date = format_date(doc.get("eventdate"))
        ep = doc.get("eventplace", [])
        place = ", ".join(ep) if isinstance(ep, list) else str(ep) if ep else ""
        ref = f"{doc.get('archive_code', '?')}:{doc.get('identifier', '?')}"
        lines.append(
            f"  {i}. {doc.get('eventtype', '?')} | {date} | {place} | "
            f"{doc.get('personname', '?')} ({doc.get('relationtype', '?')}) | "
            f"{doc.get('sourcetype', '')} | ref: {ref}"
        )
    return "\n".join(lines)


def format_detail(data: dict) -> str:
    lines = []

    # Persons and their roles — API returns dict for single items, list for multiple
    persons = data.get("Person", [])
    if isinstance(persons, dict):
        persons = [persons]
    relations = data.get("RelationEP", [])
    if isinstance(relations, dict):
        relations = [relations]
    role_map = {r["PersonKeyRef"]: r.get("RelationType", "?") for r in relations}

    event = data.get("Event", {})
    lines.append(f"Event: {event.get('EventType', '?')}")
    lines.append(f"Date: {format_date(event.get('EventDate'))}")
    ep = event.get("EventPlace", {})
    if isinstance(ep, list):
        place = ", ".join(e.get("Place", "?") for e in ep if isinstance(e, dict))
    elif isinstance(ep, dict):
        place = ep.get("Place", "?")
    else:
        place = str(ep) if ep else "?"
    lines.append(f"Place: {place}")
    lines.append("")

    lines.append("Persons:")
    for p in persons:
        pid = p.get("@pid", "")
        name_obj = p.get("PersonName", {})
        first = name_obj.get("PersonNameFirstName", "")
        last = name_obj.get("PersonNameLastName", "")
        prefix = name_obj.get("PersonNamePrefixLastName", "")
        full = f"{first} {prefix} {last}".replace("  ", " ").strip()
        role = role_map.get(pid, "?")
        prof = p.get("Profession", "")
        age_raw = p.get("Age", "")
        if isinstance(age_raw, dict):
            age = age_raw.get("PersonAgeLiteral", "")
        else:
            age = str(age_raw) if age_raw else ""
        extras = []
        if prof:
            extras.append(f"beroep: {prof}")
        if age:
            extras.append(f"leeftijd: {age}")
        extra_str = f" ({', '.join(extras)})" if extras else ""
        lines.append(f"  - {role}: {full}{extra_str}")

    # Source reference
    source = data.get("Source", {})
    ref = source.get("SourceReference", {})
    if ref:
        lines.append("")
        lines.append("Source:")
        lines.append(f"  Archive: {ref.get('InstitutionName', '?')}")
        lines.append(f"  Collection: {ref.get('Collection', '?')}")
        lines.append(f"  Book: {ref.get('Book', '?')}")
        lines.append(f"  Registry: {ref.get('RegistryNumber', '?')}")
        lines.append(f"  Document: {ref.get('DocumentNumber', '?')}")

    # Scan URL
    scan = source.get("SourceAvailableScans", {})
    if scan:
        scan_url = scan.get("Scan", "")
        if isinstance(scan_url, list):
            scan_url = scan_url[0] if scan_url else ""
        if isinstance(scan_url, dict):
            scan_url = scan_url.get("Uri", "")
        if scan_url:
            lines.append(f"  Scan: {scan_url}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search OpenArchieven records")
    parser.add_argument("name", nargs="?", help="Person name to search")
    parser.add_argument("--place", default="", help="Event place filter")
    parser.add_argument("--type", default="", help="Source type (e.g. 'BS Geboorte')")
    parser.add_argument("--archive", default="", help="Archive code (e.g. 'gld')")
    parser.add_argument("--period", default="", help="Year range (e.g. '1800-1860')")
    parser.add_argument("--limit", type=int, default=20, help="Max results")
    parser.add_argument("--detail", help="Fetch detail: 'archive_code:identifier'")
    parser.add_argument("--list-archives", action="store_true", help="List known archives")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if args.list_archives:
        for code, desc in ARCHIVES.items():
            print(f"  {code:6s}  {desc}")
        return

    period_start = period_end = 0
    if args.period:
        parts = args.period.split("-")
        if len(parts) == 2:
            period_start, period_end = int(parts[0]), int(parts[1])

    if args.detail:
        parts = args.detail.split(":", 1)
        if len(parts) != 2:
            print("Error: --detail format is 'archive_code:identifier'", file=sys.stderr)
            sys.exit(1)
        data = detail(parts[0], parts[1])
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(format_detail(data))
    elif args.name:
        data = search(args.name, place=args.place, source_type=args.type,
                       archive=args.archive, limit=args.limit,
                       period_start=period_start, period_end=period_end)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(format_search_results(data))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
