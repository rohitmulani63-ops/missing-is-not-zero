"""Command line for the grader.

    python -m grader check
    python -m grader score results/runs/<run-id>
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from . import check_data, score


def _build_parser():
    parser = argparse.ArgumentParser(
        prog="python -m grader",
        description="Missing Is Not Zero: rule-based grader.",
    )
    sub = parser.add_subparsers(dest="command")

    p_check = sub.add_parser("check", help="validate cases/ against keys/key.json")
    p_check.add_argument("--root", default=".", help="repository root (default: .)")

    p_score = sub.add_parser("score", help="grade every model in a run directory")
    p_score.add_argument("run_dir", help="for example results/runs/<run-id>")
    p_score.add_argument("--root", default=".", help="repository root (default: .)")
    p_score.add_argument("--key", default=None, help="key file (default: <root>/keys/key.json)")
    p_score.add_argument("--json", dest="json_out", default=None, help="also write the full result as JSON to this file")
    p_score.add_argument("--md", dest="md_out", default=None, help="also write the Markdown table to this file")
    return parser


def _run_score(args):
    key_path = args.key or os.path.join(args.root, "keys", "key.json")
    try:
        key = score.load_key(key_path)
        run = score.load_run(args.run_dir)
    except (OSError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    result = score.score_run(key, run)
    markdown = score.to_markdown(result)
    print(markdown, end="")
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    if args.md_out:
        with open(args.md_out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(markdown)
    return 0


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "check":
        return check_data.main(args.root)
    if args.command == "score":
        return _run_score(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
