#!/usr/bin/env python3
"""Compact Delpher search wrapper for LLM consumption.

Searches historical Dutch newspapers (2M+), magazines (500K), and books (200K)
on Delpher.nl via the JSON API. Returns minimal text instead of raw JSON.

Usage:
    python scripts/delpher_search.py "de Knijf"
    python scripts/delpher_search.py "de Knijf" --type familiebericht
    python scripts/delpher_search.py "van der Kant Schijndel" --coll ddd --limit 10
    python scripts/delpher_search.py "de Knijf" --sort date --order asc
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request


API_URL = "https://www.delpher.nl/nl/api/results"


def api_get(url: str) -> dict:
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; genealogy-research/1.0)",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def search(query: str, *, coll: str = "ddd", article_type: str = "",
           limit: int = 20, page: int = 1,
           sort: str = "relevance", order: str = "desc") -> dict:
    params: dict = {
        "query": query,
        "coll": coll,
        "page": page,
        "maxperpage": limit,
        "sortfield": sort,
        "order": order,
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    if article_type:
        url += f"&facets%5Btype%5D%5B%5D={urllib.parse.quote(article_type)}"
    return api_get(url)


def format_results(data: dict) -> str:
    total = data.get("numberOfRecords", 0)
    records = data.get("records", [])
    if not records:
        return f"No results found (total: {total})"

    lines = [f"Found {total} records:\n"]
    for i, r in enumerate(records, 1):
        date = r.get("date", "")[:10]
        paper = r.get("papertitle", "")
        title = r.get("title", "").strip()
        art_type = r.get("type", "")
        key = r.get("metadataKey", "")

        # Truncate long titles
        if len(title) > 80:
            title = title[:77] + "..."

        parts = [date, paper]
        if art_type:
            parts.append(art_type)
        parts.append(title)
        parts.append(f"key:{key}")

        lines.append(f"  {i}. {' | '.join(parts)}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search Delpher historical publications")
    parser.add_argument("query", nargs="?", help="Search query (use quotes for exact phrases)")
    parser.add_argument("--coll", default="ddd",
                        help="Collection: ddd (newspapers), dts (magazines), boeken (books)")
    parser.add_argument("--type", default="",
                        help="Article type: familiebericht, artikel, advertentie")
    parser.add_argument("--limit", type=int, default=20, help="Max results")
    parser.add_argument("--page", type=int, default=1, help="Page number")
    parser.add_argument("--sort", default="relevance", help="Sort: relevance, date")
    parser.add_argument("--order", default="desc", help="Order: asc, desc")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        sys.exit(1)

    data = search(args.query, coll=args.coll, article_type=args.type,
                   limit=args.limit, page=args.page,
                   sort=args.sort, order=args.order)

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(format_results(data))


if __name__ == "__main__":
    main()
