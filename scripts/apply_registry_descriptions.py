#!/usr/bin/env python3
"""Apply DOMAIN_META registry_description into sibling domain repos' server.json.

The official MCP Registry rejects body.description longer than 100 characters.
Daily domain bumps must run this (or copy from DOMAIN_META) so tool-count
updates cannot ship an over-long description again.

Usage:
  python3 scripts/apply_registry_descriptions.py            # check only
  python3 scripts/apply_registry_descriptions.py --write     # write into ../panda-*-tools
  python3 scripts/apply_registry_descriptions.py --write --root /path/to/workspace
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from panda_federation_tools.domains import (  # noqa: E402
    DOMAIN_META,
    REGISTRY_DESCRIPTION_MAX,
    validate_registry_descriptions,
)


def domain_repo_path(workspace: Path, package: str) -> Path:
    return workspace / package


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write registry_description into each domain repo server.json",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT.parent,
        help="Workspace that contains panda-*-tools checkouts (default: parent of this repo)",
    )
    args = parser.parse_args()

    validate_registry_descriptions()

    errors: list[str] = []
    for domain, meta in DOMAIN_META.items():
        desc = meta["registry_description"]
        if len(desc) > REGISTRY_DESCRIPTION_MAX:
            errors.append(f"{domain}: {len(desc)} > {REGISTRY_DESCRIPTION_MAX}")
            continue
        package = meta["package"]
        server = domain_repo_path(args.root, package) / "server.json"
        if not server.is_file():
            errors.append(f"{domain}: missing {server}")
            continue
        data = json.loads(server.read_text(encoding="utf-8"))
        current = data.get("description", "")
        if current == desc:
            print(f"ok  {package}: len={len(desc)} (unchanged)")
            continue
        print(f"{'write' if args.write else 'diff'} {package}: {len(current)} -> {len(desc)}")
        print(f"  was: {current}")
        print(f"  new: {desc}")
        if args.write:
            data["description"] = desc
            server.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    if errors:
        print("ERROR:\n  " + "\n  ".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
