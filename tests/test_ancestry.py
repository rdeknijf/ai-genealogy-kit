"""Tests for scripts/ancestry.py — Ahnentafel tree traversal and coverage scoring."""

import sqlite3

import pytest
from ancestry import build_ahnentafel, coverage_score, tiers_from_db

# ---------------------------------------------------------------------------
# Fixtures: mock individuals/families dicts (no GEDCOM file needed)
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_individuals():
    return {
        "I0000": {"name": "Root", "famc": ["F0001"], "fams": []},
        "I0001": {"name": "Father", "famc": ["F0002"], "fams": ["F0001"]},
        "I0002": {"name": "Mother", "famc": ["F0003"], "fams": ["F0001"]},
        "I0003": {"name": "GF Pat", "famc": [], "fams": ["F0002"]},
        "I0004": {"name": "GM Pat", "famc": [], "fams": ["F0002"]},
        "I0005": {"name": "GF Mat", "famc": [], "fams": ["F0003"]},
        "I0006": {"name": "GM Mat", "famc": [], "fams": ["F0003"]},
    }


@pytest.fixture
def mock_families():
    return {
        "F0001": {"husb": "I0001", "wife": "I0002", "chil": ["I0000"]},
        "F0002": {"husb": "I0003", "wife": "I0004", "chil": ["I0001"]},
        "F0003": {"husb": "I0005", "wife": "I0006", "chil": ["I0002"]},
    }


# ---------------------------------------------------------------------------
# build_ahnentafel
# ---------------------------------------------------------------------------


class TestBuildAhnentafel:
    def test_simple(self, mock_individuals, mock_families):
        ahnen = build_ahnentafel("I0000", mock_individuals, mock_families, max_gen=3)

        assert ahnen[1] == "I0000"  # root
        assert ahnen[2] == "I0001"  # father
        assert ahnen[3] == "I0002"  # mother
        assert ahnen[4] == "I0003"  # paternal grandfather
        assert ahnen[5] == "I0004"  # paternal grandmother
        assert ahnen[6] == "I0005"  # maternal grandfather
        assert ahnen[7] == "I0006"  # maternal grandmother
        assert len(ahnen) == 7  # all 7 slots filled

    def test_missing_parent(self, mock_individuals, mock_families):
        """One parent missing — verify the gap propagates."""
        # Remove mother's family link so she has no parents
        individuals = {**mock_individuals}
        individuals["I0002"] = {**individuals["I0002"], "famc": []}

        ahnen = build_ahnentafel("I0000", individuals, mock_families, max_gen=3)

        assert ahnen[1] == "I0000"
        assert ahnen[2] == "I0001"  # father still present
        assert ahnen[3] == "I0002"  # mother still present
        assert ahnen[4] == "I0003"  # paternal grandfather
        assert ahnen[5] == "I0004"  # paternal grandmother
        assert 6 not in ahnen  # maternal grandfather missing
        assert 7 not in ahnen  # maternal grandmother missing
        assert len(ahnen) == 5


# ---------------------------------------------------------------------------
# tiers_from_db
# ---------------------------------------------------------------------------


class TestTiersFromDb:
    def test_tiers_from_db(self, populated_db):
        """populated_db has two Tier B findings linked to I0003."""
        tiers = tiers_from_db(str(populated_db))

        assert "I0003" in tiers
        assert tiers["I0003"] == "B"
        # No other persons have findings
        assert len(tiers) == 1

    def test_rejected_excluded(self, populated_db):
        """REJECTED findings should not contribute tiers."""
        conn = sqlite3.connect(populated_db)
        conn.execute("UPDATE findings SET status = 'REJECTED' WHERE id = 'F-001'")
        conn.commit()
        conn.close()

        tiers = tiers_from_db(str(populated_db))

        # F-002 is still OPEN/Tier B, so I0003 should still be B
        assert tiers.get("I0003") == "B"

    def test_all_rejected(self, populated_db):
        """When all findings are REJECTED, no tiers returned."""
        conn = sqlite3.connect(populated_db)
        conn.execute("UPDATE findings SET status = 'REJECTED'")
        conn.commit()
        conn.close()

        tiers = tiers_from_db(str(populated_db))
        assert len(tiers) == 0


# ---------------------------------------------------------------------------
# coverage_score
# ---------------------------------------------------------------------------


class TestCoverageScore:
    def test_basic(self, populated_db, mock_individuals, mock_families):
        """3-generation tree, only I0003 has Tier B from DB."""
        result = coverage_score(
            str(populated_db),
            root_id="I0000",
            max_gen=3,
            individuals=mock_individuals,
            families=mock_families,
        )

        # Gen 1: 2 slots * 50 pts each = 100
        # Gen 2: 4 slots * 25 pts each = 100
        # max_possible = 200
        assert result["max_possible"] == pytest.approx(200.0)

        # Only I0003 (gen 2, Tier B, weight 0.8): 25 * 0.8 = 20
        assert result["total_score"] == pytest.approx(20.0)
        assert result["coverage_pct"] == pytest.approx(10.0)

        # Per-generation checks
        gen1 = result["per_generation"][1]
        assert gen1["slots"] == 2
        assert gen1["filled"] == 2
        assert gen1["verified"] == 0
        assert gen1["score"] == pytest.approx(0.0)

        gen2 = result["per_generation"][2]
        assert gen2["slots"] == 4
        assert gen2["filled"] == 4
        assert gen2["verified"] == 1
        assert gen2["score"] == pytest.approx(20.0)

    def test_empty_tree(self, db_path, mock_individuals, mock_families):
        """Root only, no ancestors — score should be 0."""
        # Use only root with no family links
        individuals = {"I0000": {"name": "Root", "famc": [], "fams": []}}
        families = {}

        result = coverage_score(
            str(db_path),
            root_id="I0000",
            max_gen=3,
            individuals=individuals,
            families=families,
        )

        assert result["total_score"] == 0.0
        assert result["max_possible"] == 0.0
        assert result["coverage_pct"] == 0.0

        # Every generation should have 0 filled
        for gen in range(1, 3):
            assert result["per_generation"][gen]["filled"] == 0
            assert result["per_generation"][gen]["score"] == 0.0

    def test_all_verified(self, db_path, mock_individuals, mock_families):
        """All ancestors Tier A — score should equal max_possible."""
        # Add Tier A findings for every ancestor
        conn = sqlite3.connect(db_path)
        for i, pid in enumerate(["I0001", "I0002", "I0003", "I0004", "I0005", "I0006"]):
            fid = f"F-T{i:03d}"
            conn.execute(
                "INSERT INTO findings (id, title, tier, status, raw_markdown) "
                "VALUES (?, ?, 'A', 'APPLIED', ?)",
                (fid, f"Record for {pid}", f"## {fid}"),
            )
            conn.execute(
                "INSERT INTO finding_persons (finding_id, person_id, role) "
                "VALUES (?, ?, 'subject')",
                (fid, pid),
            )
        conn.commit()
        conn.close()

        result = coverage_score(
            str(db_path),
            root_id="I0000",
            max_gen=3,
            individuals=mock_individuals,
            families=mock_families,
        )

        assert result["total_score"] == pytest.approx(200.0)
        assert result["max_possible"] == pytest.approx(200.0)
        assert result["coverage_pct"] == pytest.approx(100.0)

        # All ancestors verified
        assert result["per_generation"][1]["verified"] == 2
        assert result["per_generation"][2]["verified"] == 4
