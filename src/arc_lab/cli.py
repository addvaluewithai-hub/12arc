from __future__ import annotations

import argparse
import json
from pathlib import Path

from .policy import validate_repository
from .splits import partition


def main() -> None:
    parser = argparse.ArgumentParser(prog="arc-lab")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate-policy")
    split = sub.add_parser("split-task-ids")
    split.add_argument("ids_file", help="text file with one public-training task id per line")
    split.add_argument("--output")

    args = parser.parse_args()
    if args.cmd == "validate-policy":
        missing = validate_repository()
        if missing:
            raise SystemExit("missing required files: " + ", ".join(missing))
        print("ARC lab policy: OK")
        return

    ids = [line.strip() for line in Path(args.ids_file).read_text().splitlines() if line.strip()]
    payload = json.dumps(partition(ids), indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(payload + "\n")
    else:
        print(payload)


if __name__ == "__main__":
    main()
