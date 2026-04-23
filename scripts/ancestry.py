"""Shared ancestry traversal and coverage scoring.

Extracted from fan_chart.py for reuse across the project. Provides:
- Ahnentafel tree building from GEDCOM individuals/families dicts
- Tier derivation from GEDCOM source citations and the research database
- Coverage score computation that weights verification tiers by generation
"""

from __future__ import annotations

import math
import re
import sqlite3
import sys
from pathlib import Path

# Tier weight for coverage scoring
TIER_WEIGHTS: dict[str, float] = {
    "A": 1.0,
    "B": 0.8,
    "C": 0.2,
    "D": 0.05,
}


# ---------------------------------------------------------------------------
# Ahnentafel tree building
# ---------------------------------------------------------------------------


def build_ahnentafel(
    root_id: str,
    individuals: dict,
    families: dict,
    max_gen: int,
) -> dict[int, str]:
    """Build Ahnentafel numbering: 1=root, 2=father, 3=mother, 4=pat.grandfather, etc.

    Returns {ahnentafel_number: person_id}.
    """
    ahnen: dict[int, str] = {1: root_id}
    for n in sorted(ahnen.copy().keys()):
        _fill_ahnen(ahnen, n, individuals, families, max_gen)
    return ahnen


def _fill_ahnen(
    ahnen: dict[int, str],
    n: int,
    individuals: dict,
    families: dict,
    max_gen: int,
) -> None:
    """Recursively fill Ahnentafel positions."""
    gen = int(math.log2(n)) if n > 0 else 0
    if gen >= max_gen:
        return

    pid = ahnen.get(n)
    if not pid:
        return
    person = individuals.get(pid)
    if not person:
        return

    for fam_id in person.get("famc", []):
        fam = families.get(fam_id)
        if not fam:
            continue
        if fam["husb"] and 2 * n not in ahnen:
            ahnen[2 * n] = fam["husb"]
            _fill_ahnen(ahnen, 2 * n, individuals, families, max_gen)
        if fam["wife"] and 2 * n + 1 not in ahnen:
            ahnen[2 * n + 1] = fam["wife"]
            _fill_ahnen(ahnen, 2 * n + 1, individuals, families, max_gen)


# ---------------------------------------------------------------------------
# Tier derivation
# ---------------------------------------------------------------------------


def derive_tiers_from_gedcom(records: dict, individuals: dict) -> dict[str, str]:
    """Derive verification tiers from GEDCOM source citations.

    Source ID conventions in this project:
    - S600xxx = archive research (civil records with akte numbers) -> Tier B
    - S_PLxxx = Playwright/web verified sources -> Tier B
    - S00xx   = manual/original sources -> Tier B
    - S500xxx = MyHeritage import (other users' trees) -> Tier D

    Returns {person_id: tier} based on best source quality found.
    """
    tier_rank = {"A": 0, "B": 1, "C": 2, "D": 3}
    person_tiers: dict[str, str] = {}

    for pid, person_lines in records.items():
        if pid not in individuals:
            continue

        source_ids: set[str] = set()
        for line in person_lines:
            m = re.search(r"SOUR @([^@]+)@", line)
            if m:
                source_ids.add(m.group(1))

        if not source_ids:
            continue

        best_tier: str | None = None
        for sid in source_ids:
            if sid.startswith("S600") or sid.startswith("S_PL") or re.match(r"S\d{4}$", sid):
                tier = "B"
            elif sid.startswith("S500"):
                tier = "D"
            else:
                tier = "D"

            if best_tier is None or tier_rank.get(tier, 99) < tier_rank.get(best_tier, 99):
                best_tier = tier

        if best_tier:
            person_tiers[pid] = best_tier

    return person_tiers


def tiers_from_db(db_path: str) -> dict[str, str]:
    """Query best tier per person from the research database."""
    tier_rank = {"A": 0, "B": 1, "C": 2, "D": 3}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT fp.person_id, f.tier FROM findings f "
        "JOIN finding_persons fp ON f.id = fp.finding_id "
        "WHERE f.tier IS NOT NULL AND (f.status IS NULL OR f.status != 'REJECTED')"
    ).fetchall()
    conn.close()

    person_tiers: dict[str, list[str]] = {}
    for r in rows:
        pid = r["person_id"]
        if pid not in person_tiers:
            person_tiers[pid] = []
        person_tiers[pid].append(r["tier"])

    return {
        pid: min(tiers, key=lambda t: tier_rank.get(t, 99))
        for pid, tiers in person_tiers.items()
    }


# ---------------------------------------------------------------------------
# Coverage score
# ---------------------------------------------------------------------------


def coverage_score(
    db_path: str,
    gedcom_path: str | None = None,
    root_id: str = "I0000",
    max_gen: int = 7,
    *,
    individuals: dict | None = None,
    families: dict | None = None,
) -> dict:
    """Compute a weighted coverage score for the ancestor tree.

    Accepts either a ``gedcom_path`` to parse, or pre-built ``individuals``
    and ``families`` dicts.  Tiers come from the research database (and
    optionally GEDCOM source citations when a GEDCOM path is given).

    Score formula per filled ancestor slot:
        contribution = (100 / 2^generation) * tier_weight

    Tier weights: A=1.0, B=0.8, C=0.2, D=0.05, unverified=0.

    Returns::

        {
            "total_score": float,
            "max_possible": float,
            "coverage_pct": float,
            "per_generation": {
                1: {"slots": 2, "filled": 2, "verified": 1, "score": 40.0},
                ...
            },
        }
    """
    # Resolve individuals/families from GEDCOM if not provided directly
    if individuals is None or families is None:
        if gedcom_path is None:
            msg = "Either gedcom_path or both individuals and families must be provided"
            raise ValueError(msg)
        # Import here to avoid circular dependency when fan_chart also imports ancestry
        sys.path.insert(0, str(Path(__file__).parent))
        from analyze_gedcom import get_families, get_individuals, parse_gedcom

        records = parse_gedcom(gedcom_path)
        individuals = get_individuals(records)
        families = get_families(records)

    # Build Ahnentafel tree
    ahnen = build_ahnentafel(root_id, individuals, families, max_gen)

    # Collect tiers
    person_tiers: dict[str, str] = {}

    # GEDCOM-derived tiers (base layer)
    if gedcom_path is not None:
        sys.path.insert(0, str(Path(__file__).parent))
        from analyze_gedcom import parse_gedcom

        records = parse_gedcom(gedcom_path)
        person_tiers = derive_tiers_from_gedcom(records, individuals)

    # DB tiers override GEDCOM-derived ones
    db_tiers = tiers_from_db(db_path)
    person_tiers.update(db_tiers)

    # Compute score
    total_score = 0.0
    max_possible = 0.0
    per_generation: dict[int, dict] = {}

    for gen in range(1, max_gen):
        num_slots = 2**gen
        slot_value = 100.0 / (2**gen)

        filled = 0
        verified = 0
        gen_score = 0.0

        for i in range(num_slots):
            ahnen_num = 2**gen + i
            pid = ahnen.get(ahnen_num)
            if pid is None:
                continue

            filled += 1
            max_possible += slot_value

            tier = person_tiers.get(pid)
            if tier is not None:
                verified += 1
                gen_score += slot_value * TIER_WEIGHTS.get(tier, 0.0)

        total_score += gen_score
        per_generation[gen] = {
            "slots": num_slots,
            "filled": filled,
            "verified": verified,
            "score": gen_score,
        }

    coverage_pct = (total_score / max_possible * 100.0) if max_possible > 0 else 0.0

    return {
        "total_score": total_score,
        "max_possible": max_possible,
        "coverage_pct": coverage_pct,
        "per_generation": per_generation,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Compute research coverage score for the ancestor tree."
    )
    parser.add_argument(
        "--db",
        default="private/genealogy.db",
        help="Path to research database (default: private/genealogy.db)",
    )
    parser.add_argument(
        "--gedcom",
        default=None,
        help="Path to GEDCOM file (optional — uses DB tiers only when omitted)",
    )
    parser.add_argument(
        "--root",
        default="I0000",
        help="Root individual ID (default: I0000)",
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=7,
        help="Number of generations (default: 7)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Print only the coverage percentage as a float",
    )
    args = parser.parse_args()

    if not Path(args.db).exists():
        print(f"Database not found: {args.db}", file=sys.stderr)
        sys.exit(1)

    result = coverage_score(
        db_path=args.db,
        gedcom_path=args.gedcom,
        root_id=args.root,
        max_gen=args.generations,
    )

    if args.quiet:
        print(f"{result['coverage_pct']:.1f}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
