#!/usr/bin/env python3
"""Compact Memorix Genealogy API wrapper for LLM consumption.

Searches 6 Dutch archives that share the Memorix platform, returning minimal
text instead of verbose JSON. Saves the LLM from reading skill files,
constructing curl commands, and parsing metadata-heavy responses.

Supported archives:
    bhic          BHIC (Brabant) — 24.1M records
    amsterdam     Amsterdam Stadsarchief
    drents        Drents Archief — 6.7M records
    zutphen       Erfgoedcentrum Zutphen
    leiden        Erfgoed Leiden en Omstreken
    gouda         Streekarchief Midden-Holland (Gouda)

Usage:
    python scripts/memorix_search.py bhic "van der Kant"
    python scripts/memorix_search.py bhic "van der Kant" --place Schijndel --type "DTB doopakte"
    python scripts/memorix_search.py bhic --deed 5d9d0c5e-e486-8ebd-e444-e1f60da61f1d
    python scripts/memorix_search.py amsterdam "Loois" --firstname Aalbert
    python scripts/memorix_search.py --list-archives
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request

API_BASE = "https://webservices.memorix.nl/genealogy"

ARCHIVES = {
    "bhic": {
        "key": "24c66d08-da4a-4d60-917f-5942681dcaa1",
        "name": "BHIC (Brabant)",
        "coverage": "North Brabant: Schijndel, Den Bosch, Eindhoven, Tilburg, Breda, etc.",
    },
    "amsterdam": {
        "key": "eb37e65a-eb47-11e9-b95c-60f81db16c0e",
        "name": "Amsterdam Stadsarchief",
        "coverage": "Amsterdam: DTB, civil registry, population registers, person cards",
    },
    "drents": {
        "key": "a85387a2-fdb2-44d0-8209-3635e59c537e",
        "name": "Drents Archief",
        "coverage": "Drenthe province: civil registry, DTB, population registers, notarial",
    },
    "zutphen": {
        "key": "509544d0-1c67-11e4-9016-c788dee409dc",
        "name": "Erfgoedcentrum Zutphen",
        "coverage": "Brummen, Lochem, Voorst, Zutphen: civil registry, DTB, population registers",
    },
    "leiden": {
        "key": "3288aeb2-c2a5-40b4-941b-f9beb2089511",
        "name": "Erfgoed Leiden en Omstreken",
        "coverage": "Leiden region: civil registry, DTB, notarial records",
    },
    "gouda": {
        "key": "99a56f3a-da0b-11e9-9805-d77cd3614b0e",
        "name": "Streekarchief Midden-Holland",
        "coverage": "Gouda, Haastrecht, Schoonhoven, Waddinxveen, etc.",
    },
}


def api_get(url: str) -> dict:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def search(archive: str, query: str, *, firstname: str = "", place: str = "",
           deed_type: str = "", limit: int = 25, page: int = 1) -> dict:
    cfg = ARCHIVES[archive]
    params = {"apiKey": cfg["key"], "q": query, "rows": limit, "page": page}

    fq_parts = []
    if firstname:
        fq_parts.append(f'search_t_voornaam:"{firstname}"')
    if place:
        fq_parts.append(f'search_s_register_gemeente:"{place}"')
    if deed_type:
        fq_parts.append(f'search_s_deed_type_title:"{deed_type}"')
    if fq_parts:
        params["fq"] = " AND ".join(fq_parts)

    url = f"{API_BASE}/person?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"
    return api_get(url)


def get_deed(archive: str, deed_id: str) -> dict:
    cfg = ARCHIVES[archive]
    url = f"{API_BASE}/deed/{deed_id}?apiKey={cfg['key']}"
    return api_get(url)


def get_person_detail(archive: str, person_id: str) -> dict:
    cfg = ARCHIVES[archive]
    url = f"{API_BASE}/person/{person_id}?apiKey={cfg['key']}"
    return api_get(url)


def get_deed_persons(archive: str, deed_id: str) -> dict:
    """Get all persons mentioned in a deed."""
    cfg = ARCHIVES[archive]
    params = {
        "apiKey": cfg["key"],
        "q": "*:*",
        "fq": f"deed_id:{deed_id}",
        "rows": 50,
    }
    url = f"{API_BASE}/person?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"
    return api_get(url)


def format_person(p: dict) -> str:
    """Format a single person result into a compact line."""
    m = p.get("metadata", {})
    name = m.get("person_display_name", "?")
    role = m.get("type_title", "?")
    deed_type = m.get("deed_type_title", "?")
    date = m.get("datum", "")
    place = m.get("plaats", "")
    municipality = m.get("register_gemeente", "")
    register = m.get("register_naam", "")
    profession = m.get("beroep", "")
    age = m.get("leeftijd", "")

    # Normalize date (can be int like 18591024 or string like "1859-10-24")
    if isinstance(date, int):
        s = str(date)
        if len(s) == 8:
            date = f"{s[:4]}-{s[4:6]}-{s[6:]}"
        else:
            date = s

    parts = [f"{name} ({role})"]
    parts.append(deed_type)
    if date:
        parts.append(str(date))
    if place and place != municipality:
        parts.append(place)
    if municipality:
        parts.append(f"gem. {municipality}")
    if register:
        parts.append(register)
    if profession:
        parts.append(f"beroep: {profession}")
    if age:
        parts.append(f"leeftijd: {age}")

    deed_id = p.get("deed_id", "")
    if deed_id:
        parts.append(f"deed:{deed_id}")

    return " | ".join(parts)


def format_search_results(data: dict, archive: str) -> str:
    total = data.get("metadata", {}).get("pagination", {}).get("total", 0)
    persons = data.get("person", [])
    if not persons:
        return f"No results found (total: {total})"

    lines = [f"Found {total} records ({ARCHIVES[archive]['name']}):\n"]
    for i, p in enumerate(persons, 1):
        lines.append(f"  {i}. {format_person(p)}")
    return "\n".join(lines)


def format_deed(data: dict) -> str:
    """Format deed detail into compact text."""
    deeds = data.get("deed", [])
    if not deeds:
        return "No deed found"

    deed = deeds[0]
    m = deed.get("metadata", {})
    lines = []
    lines.append(f"Deed: {m.get('type_title', '?')}")
    if m.get("register_naam"):
        lines.append(f"Register: {m['register_naam']}")
    if m.get("pagina"):
        lines.append(f"Page: {m['pagina']}")

    # Scan URLs
    assets = deed.get("asset", [])
    if assets:
        lines.append("")
        lines.append("Scans:")
        for a in assets:
            download = a.get("download", "")
            title = a.get("dc_title", "")
            lines.append(f"  - {title}: {download}")

    return "\n".join(lines)


def format_deed_persons(data: dict, deed_data: dict | None = None) -> str:
    """Format all persons in a deed into compact text (like OpenArchieven detail)."""
    persons = data.get("person", [])
    if not persons:
        return "No persons found for this deed"

    # Get deed metadata from first person
    first = persons[0].get("metadata", {})
    lines = []
    lines.append(f"Deed: {first.get('deed_type_title', '?')}")
    lines.append(f"Date: {first.get('datum', '?')}")
    municipality = first.get("register_gemeente", "")
    place = first.get("plaats", "")
    if place and place != municipality:
        lines.append(f"Place: {place} (gem. {municipality})")
    elif municipality:
        lines.append(f"Place: {municipality}")
    lines.append(f"Register: {first.get('register_naam', '?')}")
    lines.append("")
    lines.append("Persons:")

    for p in persons:
        m = p.get("metadata", {})
        name = m.get("person_display_name", "?")
        role = m.get("type_title", "?")
        extras = []
        if m.get("beroep"):
            extras.append(f"beroep: {m['beroep']}")
        if m.get("leeftijd"):
            extras.append(f"leeftijd: {m['leeftijd']}")
        if m.get("plaats_geboorte"):
            extras.append(f"geb. {m['plaats_geboorte']}")
        extra_str = f" ({', '.join(extras)})" if extras else ""
        lines.append(f"  - {role}: {name}{extra_str}")

    # Diversen (transcription notes) from deed
    if deed_data:
        deeds = deed_data.get("deed", [])
        if deeds:
            diversen = deeds[0].get("metadata", {}).get("diversen", "")
            if diversen:
                lines.append("")
                lines.append(f"Notes: {diversen}")
            # Scan
            assets = deeds[0].get("asset", [])
            if assets:
                lines.append("")
                lines.append("Scan:")
                for a in assets:
                    lines.append(f"  {a.get('download', a.get('thumb.large', ''))}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Search Memorix-based Dutch archives",
        epilog="Archives: " + ", ".join(ARCHIVES.keys()),
    )
    parser.add_argument("archive", nargs="?", help="Archive code (bhic, amsterdam, etc.)")
    parser.add_argument("name", nargs="?", help="Person name to search")
    parser.add_argument("--firstname", default="", help="First name filter")
    parser.add_argument("--place", default="", help="Municipality filter")
    parser.add_argument("--type", default="", help="Deed type filter (e.g. 'BS Geboorte', 'DTB doopakte')")
    parser.add_argument("--limit", type=int, default=25, help="Max results")
    parser.add_argument("--page", type=int, default=1, help="Page number")
    parser.add_argument("--deed", default="", help="Fetch deed detail by ID")
    parser.add_argument("--person", default="", help="Fetch person detail by ID")
    parser.add_argument("--list-archives", action="store_true", help="List available archives")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if args.list_archives:
        for code, info in ARCHIVES.items():
            print(f"  {code:12s}  {info['name']:40s}  {info['coverage']}")
        return

    if not args.archive:
        parser.print_help()
        sys.exit(1)

    if args.archive not in ARCHIVES:
        print(f"Unknown archive: {args.archive}", file=sys.stderr)
        print(f"Available: {', '.join(ARCHIVES.keys())}", file=sys.stderr)
        sys.exit(1)

    if args.deed:
        deed_data = get_deed(args.archive, args.deed)
        persons_data = get_deed_persons(args.archive, args.deed)
        if args.json:
            print(json.dumps({"deed": deed_data, "persons": persons_data}, indent=2))
        else:
            print(format_deed_persons(persons_data, deed_data))
    elif args.person:
        data = get_person_detail(args.archive, args.person)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(json.dumps(data, indent=2))  # TODO: format person detail
    elif args.name:
        data = search(args.archive, args.name, firstname=args.firstname,
                       place=args.place, deed_type=args.type,
                       limit=args.limit, page=args.page)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(format_search_results(data, args.archive))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
