# Genealogy Research Kit

AI-assisted genealogy research using [Claude Code](https://claude.ai/claude-code).
Built for Dutch genealogy but the methodology applies to any region.

## What's in the box

- **20+ archive skills** — Claude Code skills that search Dutch civil registries,
  church records, newspaper archives, cemetery databases, and more via Playwright
  browser automation. Each skill teaches Claude how to navigate a specific archive,
  fill search forms, and extract structured results.

- **Research methodology** — A systematic "harden first, then extend" workflow with
  confidence tiers (A-D) that prevents bad data from entering your tree. Claude
  verifies every person against official records before extending further back.

- **Gramps Web sync** — Scripts to push/pull your GEDCOM to a self-hosted
  [Gramps Web](https://gramps-project.org/web/) instance for sharing with family.

- **40+ data source catalog** — Comprehensive reference of Dutch genealogy archives,
  what they contain, and how to access them (`research/DATA_SOURCES.md`).

- **GEDCOM analysis tools** — Python scripts for parsing, analyzing, and comparing
  GEDCOM files.

## Prerequisites

- [Claude Code](https://claude.ai/claude-code) with a Claude Pro/Max subscription
- [Playwright MCP server](https://github.com/anthropics/claude-code/tree/main/packages/playwright-mcp)
  configured in your Claude Code settings
- Python 3.12+ and [uv](https://docs.astral.sh/uv/) for running analysis scripts
- (Optional) A [Gramps Web](https://gramps-project.org/web/) instance for publishing

## Getting started

```bash
# Clone
git clone https://github.com/rdeknijf/genealogy.git
cd genealogy

# Configure credentials
cp .env.example .env
# Edit .env with your Gramps Web and/or MyHeritage credentials

# Place your GEDCOM
cp /path/to/your/tree.ged tree.ged

# Set sync state
echo "local" > .tree-state

# (Optional) Create personal config for Claude
cp CLAUDE.local.example.md CLAUDE.local.md
# Edit CLAUDE.local.md with your Gramps Web URL, MyHeritage details, etc.

# Start researching
claude
```

Then try:

- `/harden-line` — verify a family line against official records
- `/scorecard` — compare your tree against a baseline to see discoveries
- `/onboard-datasource` — add a new archive as a searchable skill
- Ask Claude to look up a person on WieWasWie, OpenArchieven, Delpher, etc.

## Archive skills included

| Skill | Archive | What it searches |
|-------|---------|-----------------|
| `wiewaswie` | WieWasWie.nl | 252M+ Dutch civil registry records |
| `openarchieven` | OpenArchieven.nl | 150M+ indexed records from 70+ archives |
| `familysearch` | FamilySearch.org | Global genealogy records |
| `delpher` | Delpher.nl | 2M+ historical Dutch newspapers |
| `gelders-archief` | Gelders Archief | Gelderland regional archive |
| `het-utrechts-archief` | Het Utrechts Archief | Utrecht regional archive |
| `erfgoed-s-hertogenbosch` | Erfgoed 's-Hertogenbosch | Den Bosch/Rosmalen archive |
| `erfgoedcentrum-zutphen` | Erfgoedcentrum Zutphen | Zutphen regional archive |
| `cbg-familienamen` | CBG Familienamen | Dutch surname database (320K+ names) |
| `online-begraafplaatsen` | Online Begraafplaatsen | 1.2M+ Dutch cemetery records |
| `genealogie-online` | Genealogie Online | Published Dutch family trees |
| `myheritage` | MyHeritage | Record matches, Smart Matches, SuperSearch |
| `oktober44` | Stichting Oktober 44 | Putten WWII razzia victims |
| `oorlogsbronnen` | Oorlogsbronnen.nl | 12M+ WWII sources |
| `hansknijff-com` | hansknijff.com | Knijff family genealogy research |
| + 5 more | Regional archives | Leiden, Alphen, Rijnstreek, etc. |

## How it works

1. **You ask Claude to research a family line** — e.g., "harden the Van den Hul line"
2. **Claude parses your GEDCOM** to extract everyone in that line
3. **Claude searches archives** using the skills, one person at a time
4. **Findings go to `research/FINDINGS.md`** with confidence tiers
5. **Only Tier A/B evidence** gets applied to the GEDCOM (with your approval)

The confidence tier system prevents Claude from polluting your tree with
unverified data. AI inference is always Tier D — noted but never applied.

## File organization

```
├── .claude/skills/        # Archive lookup + workflow skills
├── scripts/               # GEDCOM analysis and Gramps Web sync
├── research/
│   ├── DATA_SOURCES.md    # 40+ Dutch archive catalog
│   └── FINDINGS.md        # Your research findings (gitignored)
├── sources/               # Scanned documents (gitignored)
├── tree.ged               # Your GEDCOM (gitignored)
├── CLAUDE.md              # Project instructions for Claude Code
├── CLAUDE.local.md        # Your personal config (gitignored)
├── .env                   # Credentials (gitignored)
└── .env.example           # Credential template
```

## Contributing

Found a Dutch archive that should have a skill? Use `/onboard-datasource`
to create one, then submit a PR. Skills should prefer API/HTTP access
over browser automation where possible.

## License

MIT
