---
description: |
  Search 4 Dutch archives on the MAIS platform via `scripts/mais_search.py`.
  Covers Het Utrechts Archief (Utrecht province incl. Woerden), ECAL (Achterhoek),
  Gemeentearchief Alphen, and Regionaal Archief Dordrecht. Use for DTB, civil
  registry, and population register searches in these regions. No login required.
---

# MAIS Archives — 4 Dutch Archives via Python Wrapper

Use `scripts/mais_search.py` for all searches. Do NOT construct URLs or parse HTML.

## Archives

| Code | Archive | Coverage |
|------|---------|----------|
| `hua` | Het Utrechts Archief (13.9M) | Utrecht province: Woerden, Utrecht, Amersfoort, Zeist |
| `ecal` | ECAL (2.4M) | Eastern Gelderland: Doetinchem, Winterswijk, Aalten |
| `alphen` | Gemeentearchief Alphen | Alphen aan den Rijn, Aarlanderveen, Hazerswoude |
| `dordrecht` | Regionaal Archief Dordrecht (3M+) | Dordrecht, Zwijndrecht, Papendrecht, Sliedrecht |

## Commands

```bash
python scripts/mais_search.py <archive> "<surname>"
python scripts/mais_search.py <archive> "<surname>" --firstname Jan --place Woerden
python scripts/mais_search.py <archive> "<surname>" --year-from 1800 --year-to 1850
python scripts/mais_search.py --list-archives
```

## Tips

- HUA is the primary archive for Woerden DTB records (Knijf family pre-1811)
- MAIS returns role, place, date — no parent names in search results
- For parent details, use the record's detail URL (not yet wrapped — use WebFetch)
- ECAL is important for Peters/Remmers lines in the Achterhoek
