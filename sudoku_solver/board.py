"""Grid model: 81 cells, peers, and text parsing."""

from __future__ import annotations

ROWS = "ABCDEFGHI"
COLS = "123456789"
CELLS = [r + c for r in ROWS for c in COLS]

UNITS: dict[str, list[str]] = {}
PEERS: dict[str, set[str]] = {}

for _r in ROWS:
    row = [_r + c for c in COLS]
    for _c in row:
        UNITS.setdefault(_c, []).append(row)
for _c in COLS:
    col = [r + _c for r in ROWS]
    for _r in ROWS:
        cell = _r + _c
        UNITS.setdefault(cell, []).append(col)
for _br in range(3):
    for _bc in range(3):
        box = [ROWS[_br * 3 + i] + COLS[_bc * 3 + j] for i in range(3) for j in range(3)]
        for cell in box:
            UNITS.setdefault(cell, []).append(box)

for _cell in CELLS:
    peers: set[str] = set()
    for unit in UNITS[_cell]:
        peers.update(unit)
    peers.discard(_cell)
    PEERS[_cell] = peers

ALL_UNITS: list[list[str]] = []
_seen: set[tuple[str, ...]] = set()
for _units in UNITS.values():
    for _unit in _units:
        _key = tuple(_unit)
        if _key not in _seen:
            _seen.add(_key)
            ALL_UNITS.append(_unit)


class Board:
    """A grid where each cell holds a set of candidate digits.

    Solved cells hold exactly one candidate; contradiction is an empty set.
    """

    def __init__(self) -> None:
        self.grid: dict[str, set[str]] = {cell: set("123456789") for cell in CELLS}

    def clone(self) -> "Board":
        copy = Board.__new__(Board)
        copy.grid = {cell: set(cands) for cell, cands in self.grid.items()}
        return copy

    def solved_cells(self) -> int:
        return sum(1 for cell in CELLS if len(self.grid[cell]) == 1)

    def is_solved(self) -> bool:
        return all(len(self.grid[cell]) == 1 for cell in CELLS)

    def render(self) -> str:
        lines = []
        for r in ROWS:
            row = ""
            for c in COLS:
                cell = r + c
                cands = self.grid[cell]
                row += next(iter(cands)) if len(cands) == 1 else "."
                if c in "36":
                    row += "|"
            lines.append(row)
            if r in "CF":
                lines.append("------+-------+------")
        return "\n".join(lines)

    def one_line(self) -> str:
        return "".join(
            next(iter(self.grid[cell])) if len(self.grid[cell]) == 1 else "."
            for cell in CELLS
        )


def parse_grid(text: str) -> Board:
    """Parse a grid from 81 characters; 0 and . mean empty."""
    board = Board()
    digits = [ch for ch in text if ch in "1234567890."]
    if len(digits) != 81:
        raise ValueError(f"expected 81 grid characters, got {len(digits)}")
    for cell, ch in zip(CELLS, digits):
        if ch in "123456789":
            board.grid[cell] = {ch}
    return board
