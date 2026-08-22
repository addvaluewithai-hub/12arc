from __future__ import annotations

import argparse
import json

from .benchmark import (
    read_task_ids,
    validate_development_dataset,
    verify_split_manifest,
    write_split_manifest,
)
from .policy import validate_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="arc-lab")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate-policy")

    split = sub.add_parser("split-task-ids")
    split.add_argument("ids_file", help="text file with one public-training task id per line")
    split.add_argument("--output")
    split.add_argument("--source-commit")

    verify = sub.add_parser("verify-split-manifest")
    verify.add_argument("ids_file")
    verify.add_argument("manifest_file")

    dev = sub.add_parser("validate-development")
    dev.add_argument("training_dir")
    dev.add_argument("--ids-file")

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.cmd == "validate-policy":
        missing = validate_repository()
        if missing:
            raise SystemExit("missing required files: " + ", ".join(missing))
        print("ARC lab policy: OK")
        return

    if args.cmd == "split-task-ids":
        if args.output:
            payload = write_split_manifest(
                args.ids_file, args.output, source_commit=args.source_commit
            )
            print(json.dumps(payload["counts"], sort_keys=True))
        else:
            from .splits import build_split_manifest

            ids = read_task_ids(args.ids_file)
            print(
                json.dumps(
                    build_split_manifest(ids, source_commit=args.source_commit),
                    indent=2,
                    sort_keys=True,
                )
            )
        return

    if args.cmd == "verify-split-manifest":
        verify_split_manifest(args.ids_file, args.manifest_file)
        print("split manifest: OK")
        return

    if args.cmd == "validate-development":
        expected = read_task_ids(args.ids_file) if args.ids_file else None
        print(
            json.dumps(
                validate_development_dataset(args.training_dir, expected_task_ids=expected),
                sort_keys=True,
            )
        )
        return


if __name__ == "__main__":
    main()
