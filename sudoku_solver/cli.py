"""CLI: solve a grid, count solutions, score difficulty, explain steps."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .board import parse_grid
from .explain import explain
from .solver import difficulty, solve, solve_count

USAGE = """sudoku-solver v%(version)s — constraint propagation + MRV backtracking

USAGE
  sudoku-solver solve "<81-char grid>"     solve and verify uniqueness
  sudoku-solver explain "<grid>"           narrate the propagation steps
  sudoku-solver count "<grid>"             count solutions (up to 2)
  sudoku-solver difficulty "<grid>"        print difficulty name + score
  -h | --help | -V | --version

Grid format: 81 characters, row by row; . or 0 for empty cells.
Optional line breaks and pipes are ignored."""


def clean_grid(text: str) -> str:
    return "".join(ch for ch in text if ch not in "\n\r|-+ ")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("command", nargs="?")
    parser.add_argument("grid", nargs="?")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-V", "--version", action="store_true")
    args = parser.parse_args(argv)

    if args.help:
        print(USAGE % {"version": __version__})
        return
    if args.version:
        print("sudoku-solver", __version__)
        return
    if not args.command or not args.grid:
        parser.exit(2, "sudoku-solver: missing command or grid\n")
    grid = clean_grid(args.grid)

    try:
        board = parse_grid(grid)
        _ = board  # validation happens here
        if args.command == "solve":
            solution, unique = solve(grid)
            print(solution.render())
            print("unique" if unique else "NOT unique — puzzle has multiple solutions")
        elif args.command == "explain":
            for line in explain(grid):
                print(line)
        elif args.command == "count":
            print(f"{solve_count(grid, limit=2)} solution(s) (search stops at 2)")
        elif args.command == "difficulty":
            name, score = difficulty(grid)
            print(f"{name} (score {score})")
        else:
            parser.exit(2, f"sudoku-solver: unknown command \"{args.command}\"\n")
    except ValueError as error:
        print(f"sudoku-solver: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main(sys.argv[1:])
