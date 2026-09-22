"""Human-readable explanation of the solving steps."""

from __future__ import annotations

from .board import CELLS, PEERS, parse_grid
from .solver import eliminate


def explain(text: str, max_steps: int = 40) -> list[str]:
    """Solve with constraint propagation, narrating every placement the
    cascade makes (naked singles and hidden singles). If the grid needs
    search beyond propagation, the narration says so."""
    board = parse_grid(text)
    raw: list[str] = []
    for cell in CELLS:
        candidates = list(board.grid[cell])
        if len(candidates) == 1:
            for peer in PEERS[cell]:
                if candidates[0] in board.grid[peer] and not eliminate(
                    board, peer, candidates[0], raw
                ):
                    raw.append("  given cells contradict each other")
                    return _dedupe(raw, max_steps)
    tail = ""
    if board.is_solved():
        placements = sum(1 for line in raw if " = " in line)
        tail = f"solved with {placements} placement(s), no guessing"
    else:
        tail = "propagation exhausted; search (guessing) would be needed"
    steps = _dedupe(raw, max_steps - 1)
    steps.append(tail)
    return steps


def _dedupe(lines: list[str], limit: int) -> list[str]:
    """Keep the first explanation per placement, then cap the list."""
    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        key = line.split(" (")[0] if " = " in line else line
        if key in seen and " = " in line:
            continue
        seen.add(key)
        out.append(line)
        if len(out) >= limit:
            break
    return out
