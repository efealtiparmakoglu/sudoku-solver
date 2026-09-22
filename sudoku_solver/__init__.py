"""Sudoku solver with constraint propagation, uniqueness checking and
difficulty scoring."""

from .board import Board, parse_grid
from .solver import solve, solve_count, Difficulty
from .explain import explain

__version__ = "1.0.0"

__all__ = ["Board", "parse_grid", "solve", "solve_count", "Difficulty", "explain"]
