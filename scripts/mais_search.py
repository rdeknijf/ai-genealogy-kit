#!/usr/bin/env python3
"""Compact MAIS archive search wrapper for LLM consumption.

Searches 4 Dutch archives on the MAIS/Archieven.nl platform, parsing the
HTML table response into compact text. Returns minimal output instead of
forcing the LLM to parse HTML with regex.

Supported archives:
    hua           Het Utrechts Archief — Utrecht province (13.9M records)
    ecal          ECAL — Achterhoek en Liemers (2.4M records)
    alphen        Gemeentearchief Alphen aan den Rijn
    dordrecht     Regionaal Archief Dordrecht (3M+ records)

Usage:
    python scripts/mais_search.py hua "Knijf"
    python scripts/mais_search.py hua "Knijf" --firstname Gijsbert --place Woerden
    python scripts/mais_search.py ecal "Peters" --year-from 1800 --year-to 1850
    python scripts/mais_search.py dordrecht "van Leeuwen" --limit 10
    python scripts/mais_search.py --list-archives
"""

import argparse
import html as html_mod
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request

ARCHIVES = {
    "hua": {
        "name": "Het Utrechts Archief",
        "base_url": "https://hetutrechtsarchief.nl/onderzoek/resultaten/personen-mais",
        "mivast": 39,
        "miadt": 39,
        "coverage": "Utrecht province: Woerden, Utrecht, Amersfoort, Zeist — 13.9M records",
        "ssl_verify": True,
    },
    "ecal": {
        "name": "ECAL (Achterhoek en Liemers)",
        "base_url": "https://www.ecal.nu/archieven/maisi_proxy.php",
        "mivast": 26,
        "miadt": 26,
        "coverage": "Eastern Gelderland: Doetinchem, Winterswijk, Aalten, Berkelland — 2.4M records",
        "ssl_verify": True,
    },
    "alphen": {
        "name": "Gemeentearchief Alphen aan den Rijn",
        "base_url": "https://gemeentearchief.alphenaandenrijn.nl/components/com_maisinternet/maisi_ajax_proxy.php",
        "mivast": 105,
        "miadt": 105,
        "coverage": "Alphen aan den Rijn, Aarlanderveen, Hazerswoude, Koudekerk",
        "ssl_verify": False,  # SSL cert issues
    },
    "dordrecht": {
        "name": "Regionaal Archief Dordrecht",
        "base_url": "https://www.regionaalarchiefdordrecht.nl/archief/",
        "mivast": 46,
        "miadt": 46,
        "coverage": "Dordrecht, Zwijndrecht, Dubbeldam, Papendrecht, Sliedrecht — 3M+ records",
        "ssl_verify": True,
    },
}


def fetch_html(url: str, verify_ssl: bool = True) -> str:
    if not verify_ssl:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        ctx = None
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; genealogy-research/1.0)",
    })
    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        return resp.read().decode("utf-8", errors="replace")


def search(archive: str, surname: str = "", firstname: str = "",
           prefix: str = "", place: str = "",
           year_from: int = 0, year_to: int = 0,
           limit: int = 20) -> list[dict]:
    cfg = ARCHIVES[archive]
    params: dict = {
        "mivast": cfg["mivast"],
        "mizig": 100,
        "miadt": cfg["miadt"],
        "miview": "tbl",
        "milang": "nl",
        "mires": limit,
    }
    if surname:
        params["mip1"] = surname
    if prefix:
        params["mip2"] = prefix
    if firstname:
        params["mip3"] = firstname
    if place:
        params["mip5"] = place
    if year_from:
        params["mibj"] = year_from
    if year_to:
        params["miej"] = year_to

    url = f"{cfg['base_url']}?{urllib.parse.urlencode(params)}"
    content = fetch_html(url, cfg["ssl_verify"])
    return parse_mais_table(content)


def parse_mais_table(html: str) -> list[dict]:
    """Parse the MAIS HTML table into a list of person dicts."""
    results = []
    # Find all data rows (those with detail links)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    for row in rows:
        # Only process rows with detail links (miview=ldt)
        if 'miview=ldt' not in row and 'miview%3Dldt' not in row:
            continue
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) < 5:
            continue

        # Clean HTML from cells
        cleaned = []
        for c in cells:
            text = re.sub(r'<[^>]+>', '', c)
            text = html_mod.unescape(text).strip()
            cleaned.append(text)

        # Extract detail URL
        detail_match = re.search(r'href="([^"]*miview[=|%3D]ldt[^"]*)"', row)
        detail_url = html_mod.unescape(detail_match.group(1)) if detail_match else ""

        # Standard MAIS columns: [link/type], Voornaam, Achternaam, Rol, Plaats, Datum
        # But column 0 might have the record type embedded
        result = {
            "firstname": cleaned[1] if len(cleaned) > 1 else "",
            "surname": cleaned[2] if len(cleaned) > 2 else "",
            "role": cleaned[3] if len(cleaned) > 3 else "",
            "place": cleaned[4] if len(cleaned) > 4 else "",
            "date": cleaned[5] if len(cleaned) > 5 else "",
            "detail_url": detail_url,
        }
        results.append(result)

    return results


def format_results(results: list[dict], archive: str) -> str:
    if not results:
        return "No results found"

    name = ARCHIVES[archive]["name"]
    lines = [f"Found {len(results)} results ({name}):\n"]
    for i, r in enumerate(results, 1):
        name_str = f"{r['firstname']} {r['surname']}".strip()
        parts = [name_str]
        if r["role"]:
            parts[0] = f"{name_str} ({r['role']})"
        if r["date"]:
            parts.append(r["date"])
        if r["place"]:
            parts.append(r["place"])
        lines.append(f"  {i}. {' | '.join(parts)}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Search MAIS-based Dutch archives",
    )
    parser.add_argument("archive", nargs="?", help="Archive code (hua, ecal, alphen, dordrecht)")
    parser.add_argument("surname", nargs="?", help="Surname to search")
    parser.add_argument("--firstname", default="", help="First name filter")
    parser.add_argument("--prefix", default="", help="Tussenvoegsel (de, van, van der)")
    parser.add_argument("--place", default="", help="Place filter")
    parser.add_argument("--year-from", type=int, default=0, help="Start year")
    parser.add_argument("--year-to", type=int, default=0, help="End year")
    parser.add_argument("--limit", type=int, default=20, help="Max results")
    parser.add_argument("--list-archives", action="store_true", help="List available archives")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.list_archives:
        for code, info in ARCHIVES.items():
            print(f"  {code:12s}  {info['name']:40s}  {info['coverage']}")
        return

    if not args.archive or not args.surname:
        parser.print_help()
        sys.exit(1)

    if args.archive not in ARCHIVES:
        print(f"Unknown archive: {args.archive}", file=sys.stderr)
        print(f"Available: {', '.join(ARCHIVES.keys())}", file=sys.stderr)
        sys.exit(1)

    results = search(args.archive, surname=args.surname,
                      firstname=args.firstname, prefix=args.prefix,
                      place=args.place, year_from=args.year_from,
                      year_to=args.year_to, limit=args.limit)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(format_results(results, args.archive))


if __name__ == "__main__":
    main()
