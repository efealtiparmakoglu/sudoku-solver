"""Constraint propagation + MRV backtracking, uniqueness counting and
difficulty scoring. The propagation core follows Norvig's approach: every
elimination cascades, and when a digit has only one possible place left in
a unit, it is assigned there immediately."""

from __future__ import annotations

from .board import ALL_UNITS, CELLS, PEERS, UNITS, Board, parse_grid

DIGITS = "123456789"


def assign(board: Board, cell: str, digit: str, trace: list | None = None) -> bool:
    """Fix `digit` at `cell`, eliminating the rest; False on contradiction."""
    others = board.grid[cell] - {digit}
    return all(eliminate(board, cell, other, trace) for other in others)


def eliminate(board: Board, cell: str, digit: str, trace: list | None = None) -> bool:
    if digit not in board.grid[cell]:
        return True
    board.grid[cell].discard(digit)

    remaining = board.grid[cell]
    if len(remaining) == 0:
        return False  # contradiction: no candidate left
    if len(remaining) == 1:
        only = next(iter(remaining))
        if trace is not None:
            trace.append(f"{cell} = {only} (last candidate in cell)")
        if not all(eliminate(board, peer, only, trace) for peer in PEERS[cell]):
            return False
    # hidden single: when `digit` fits nowhere else in a unit of `cell`,
    # place it; this keeps the propagation cascade tight
    for unit in UNITS[cell]:
        places = [other for other in unit if digit in board.grid[other]]
        if len(places) == 0:
            return False
        if len(places) == 1 and len(board.grid[places[0]]) > 1:
            if trace is not None:
                trace.append(
                    f"{places[0]} = {digit} (only place in {_unit_name(cell, unit)})"
                )
            if not assign(board, places[0], digit, trace):
                return False
    return True


def _unit_name(cell: str, unit: list[str]) -> str:
    if len([c for c in unit if c[0] == cell[0]]) == 9:
        return f"row {cell[0]}"
    if len([c for c in unit if c[1] == cell[1]]) == 9:
        return f"column {cell[1]}"
    br = "ABCDEFGHI".index(cell[0]) // 3
    bc = "123456789".index(cell[1]) // 3
    return f"box {br * 3 + bc + 1}"


def propagate(board: Board, cycles: dict | None = None) -> bool:
    """Drive elimination cascades until the solved-cell count stabilizes.

    Key step: single-candidate cells push their digit out to every peer —
    this is what starts the cascade from the parsed givens.
    """
    if cycles is not None:
        cycles["rounds"] += 1
    before = -1
    while before != board.solved_cells():
        if cycles is not None:
            cycles["rounds"] += 1
        before = board.solved_cells()
        for cell in CELLS:
            candidates = list(board.grid[cell])
            if len(candidates) == 0:
                return False
            if len(candidates) == 1:
                only = candidates[0]
                for peer in PEERS[cell]:
                    if only in board.grid[peer] and not eliminate(board, peer, only):
                        return False
    return True


def _mrv_cell(board: Board) -> str:
    return min(
        (c for c in CELLS if len(board.grid[c]) > 1),
        key=lambda c: len(board.grid[c]),
    )


def search(board: Board) -> Board | None:
    """MRV backtracking on top of propagation."""
    if not propagate(board):
        return None
    if board.is_solved():
        return board
    cell = _mrv_cell(board)
    for digit in sorted(board.grid[cell]):
        trial = board.clone()
        if assign(trial, cell, digit):
            result = search(trial)
            if result is not None:
                return result
    return None


def solve(text: str) -> tuple[Board, bool]:
    """Solve a grid; returns (solution, unique). unique=True when exactly
    one solution exists."""
    board = parse_grid(text)
    solution = search(board)
    if solution is None:
        raise ValueError("no solution exists")
    unique = solve_count(text, limit=2) == 1
    return solution, unique


def solve_count(text: str, limit: int = 2) -> int:
    """Count solutions up to `limit` by branching on the most-constrained
    cell."""
    return _count_from(parse_grid(text), limit)


def _count_from(board: Board, limit: int) -> int:
    if not propagate(board):
        return 0
    if board.is_solved():
        return 1
    cell = _mrv_cell(board)
    count = 0
    for digit in sorted(board.grid[cell]):
        trial = board.clone()
        if assign(trial, cell, digit):
            count += _count_from(trial, limit - count)
            if count >= limit:
                break
    return count


def difficulty(text: str) -> tuple[str, int]:
    """Score: propagation rounds + 30 per forced guess."""
    board = parse_grid(text)
    stats = {"guesses": 0, "rounds": 0}

    def run(board: Board) -> Board | None:
        if not propagate(board, stats):
            return None
        if board.is_solved():
            return board
        cell = _mrv_cell(board)
        for digit in sorted(board.grid[cell]):
            stats["guesses"] += 1
            trial = board.clone()
            if assign(trial, cell, digit):
                result = run(trial)
                if result is not None:
                    return result
        return None

    run(board)
    score = stats["guesses"] * 30 + stats["rounds"]
    return Difficulty.name_for(score), score


class Difficulty:
    BANDS = [
        ("trivial", 5),
        ("easy", 40),
        ("medium", 90),
        ("hard", 200),
        ("expert", 10_000),
    ]

    @staticmethod
    def name_for(score: int) -> str:
        for name, hi in Difficulty.BANDS:
            if score < hi:
                return name
        return "expert"
