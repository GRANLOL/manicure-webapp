import argparse
import sys
import unittest
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run project test suite.")
    parser.add_argument(
        "target",
        nargs="?",
        default="tests",
        help="Test module, package, or start directory. Default: tests",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        type=int,
        default=2,
        help="unittest verbosity level",
    )
    args = parser.parse_args()

    loader = unittest.defaultTestLoader
    project_root = Path(__file__).resolve().parent
    if args.target == "tests" or "/" in args.target or "\\" in args.target:
        suite = loader.discover(
            start_dir=str(project_root / args.target),
            pattern="test*.py",
            top_level_dir=str(project_root),
        )
    else:
        suite = loader.loadTestsFromName(args.target)
    result = unittest.TextTestRunner(verbosity=args.verbosity).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
