#!/usr/bin/env python3
"""Convert GEDCOM to Betty-compatible Gramps XML.

Pipeline: GEDCOM → Gramps CLI → strip media → gzipped Gramps XML

Usage: python scripts/gedcom_to_betty.py private/tree.ged private/tree.gramps
"""
import gzip
import subprocess
import sys
import tempfile
from pathlib import Path

from lxml import etree


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.ged> <output.gramps>")
        sys.exit(1)

    ged_path = Path(sys.argv[1]).resolve()
    out_path = Path(sys.argv[2]).resolve()

    if not ged_path.is_file():
        print(f"Error: {ged_path} not found")
        sys.exit(1)

    # Step 1: Convert GEDCOM to Gramps XML via gramps CLI
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_gramps = Path(tmpdir) / "tree.gramps"
        print(f"Converting {ged_path.name} to Gramps XML...")
        result = subprocess.run(
            ["gramps", "-i", str(ged_path), "-e", str(tmp_gramps), "-f", "gramps"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Gramps export failed:\n{result.stderr}")
            sys.exit(1)

        # Step 2: Read the gzipped Gramps XML
        with gzip.open(tmp_gramps) as f:
            xml = f.read()

    tree = etree.ElementTree(etree.fromstring(xml))
    root = tree.getroot()
    ns = root.tag.split("}")[0] + "}"

    # Step 3: Remove media objects (files are on the server, not local)
    # Remove <objects> section entirely
    objects_section = root.find(f"{ns}objects")
    if objects_section is not None:
        count = len(objects_section)
        root.remove(objects_section)
        print(f"Stripped {count} media objects (files not available locally)")

    # Remove all objref elements throughout the tree
    for objref in root.iter(f"{ns}objref"):
        parent = objref.getparent()
        if parent is not None:
            parent.remove(objref)

    # Step 4: Fix repositories missing <rname> (Betty requires it)
    repos_fixed = 0
    for repo in root.iter(f"{ns}repository"):
        rname = repo.find(f"{ns}rname")
        if rname is None:
            rname = etree.SubElement(repo, f"{ns}rname")
            rid = repo.get("id", "unknown")
            rname.text = f"Repository {rid}"
            repos_fixed += 1
    if repos_fixed:
        print(f"Fixed {repos_fixed} repositories with missing names")

    # Step 5: Write gzipped output
    xml_out = etree.tostring(tree, xml_declaration=True, encoding="UTF-8")
    with gzip.open(out_path, "wb") as f:
        f.write(xml_out)

    size_kb = out_path.stat().st_size / 1024
    print(f"Written {out_path} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
