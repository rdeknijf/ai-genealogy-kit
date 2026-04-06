---
description: |
  Search historical Dutch newspapers (2M+), magazines, and books on Delpher.nl
  via `scripts/delpher_search.py`. Use for obituaries, death notices
  (familieberichten), birth/marriage announcements, and contextual mentions of
  family members. No login required.
---

# Delpher — Historical Dutch Publications via Python Wrapper

Use `scripts/delpher_search.py` for all searches. Do NOT construct curl commands.

## Commands

```bash
python scripts/delpher_search.py "<query>"
python scripts/delpher_search.py '"de Knijf"' --type familiebericht --sort date --order asc
python scripts/delpher_search.py '"van der Kant" Schijndel' --coll ddd --limit 20
```

## Options

| Flag | Values | Default |
|------|--------|---------|
| `--coll` | `ddd` (newspapers), `dts` (magazines), `boeken` (books) | `ddd` |
| `--type` | `familiebericht`, `artikel`, `advertentie` | (all) |
| `--sort` | `relevance`, `date` | `relevance` |
| `--order` | `asc`, `desc` | `desc` |

## Tips

- Wrap exact names in quotes: `'"de Knijf"'` (shell quotes around API quotes)
- `familiebericht` = birth/death/marriage announcements — most useful for genealogy
- Sort by date ascending to find the earliest mentions
- Combine name + place for targeted searches: `'"van der Kant" Schijndel'`

## Supersedes

This replaces the old `delpher` skill.
