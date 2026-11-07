#!/usr/bin/env python3
"""Validate DarkHacker extension package. Stdlib only, zero dependencies.

Checks:
  - manifest.json parses and has required MV3 fields
  - version looks like MAJOR.MINOR.PATCH
  - homepage_url points at the canonical repo
  - every file referenced by the manifest exists on disk
  - README links to the canonical repo

Exit 0 iff all checks pass. Prints PASS/FAIL per check.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "manifest.json"
README = ROOT / "README.md"
CANONICAL_REPO = "https://github.com/Wilkywayre/DarkHacker"

failures = []


def check(name, ok, detail=""):
    print(("PASS" if ok else "FAIL"), "-", name, detail)
    if not ok:
        failures.append(name)


def main():
    try:
        manifest = json.loads(MANIFEST.read_text())
    except Exception as exc:
        check("manifest.json parses", False, str(exc))
        return 1
    check("manifest.json parses", True)

    check("manifest_version == 3", manifest.get("manifest_version") == 3)
    check("name non-empty", bool(manifest.get("name")))
    version = str(manifest.get("version", ""))
    check("version is MAJOR.MINOR.PATCH", bool(re.fullmatch(r"\d+\.\d+\.\d+", version)), version)
    check("description non-empty", bool(manifest.get("description")))
    check(
        "homepage_url points at canonical repo",
        manifest.get("homepage_url") == CANONICAL_REPO,
        str(manifest.get("homepage_url")),
    )

    referenced = []
    for icon_set in [manifest.get("icons", {}), manifest.get("action", {}).get("default_icon", {})]:
        referenced.extend(icon_set.values())
    for cs in manifest.get("content_scripts", []):
        referenced.extend(cs.get("css", []))
        referenced.extend(cs.get("js", []))

    if not referenced:
        check("manifest references at least one file", False)
    else:
        missing = [f for f in referenced if not (ROOT / f).is_file()]
        check(
            "all manifest-referenced files exist",
            not missing,
            ("missing: " + ", ".join(missing)) if missing else f"({len(referenced)} files)",
        )

    try:
        readme = README.read_text()
    except OSError as exc:
        check("README.md readable", False, str(exc))
        return 1
    check("README links to canonical repo", CANONICAL_REPO in readme)

    print("OK" if not failures else f"{len(failures)} check(s) failed")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
