import unittest

from sudoku_solver.board import ALL_UNITS, CELLS, PEERS, UNITS, parse_grid
from sudoku_solver.explain import explain
from sudoku_solver.solver import difficulty, solve, solve_count

EASY = (
    "003020600900305001001806400008102900700000008006708200002609500800203009005010300"
)
HARD = (
    "4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......"
)
# a puzzle with multiple solutions: a single given admits many grids
MULTI = "000000000000000000000000000000000000000000000000000000000000000000000000000000001"
INVALID = "99" + "." * 79


class TestBoard(unittest.TestCase):
    def test_parse_rejects_wrong_length(self):
        with self.assertRaises(ValueError):
            parse_grid("1234")

    def test_units_and_peers(self):
        self.assertEqual(len(UNITS), 81)
        self.assertEqual(len(ALL_UNITS), 27)
        self.assertEqual(len(PEERS["E5"]), 20)
        self.assertNotIn("E5", PEERS["E5"])

    def test_parse_sets_givens(self):
        board = parse_grid(EASY)
        self.assertEqual(board.solved_cells(), 32)


class TestSolve(unittest.TestCase):
    def test_solves_easy_puzzle(self):
        solution, unique = solve(EASY)
        self.assertTrue(solution.is_solved())
        self.assertTrue(unique)

    def test_solves_hard_puzzle(self):
        solution, unique = solve(HARD)
        self.assertTrue(solution.is_solved())
        self.assertTrue(unique)

    def test_solution_respects_units(self):
        solution, _ = solve(EASY)
        one_line = solution.one_line()
        for unit in ALL_UNITS:
            values = {one_line[CELLS.index(cell)] for cell in unit}
            self.assertEqual(values, set("123456789"))

    def test_invalid_grid_reports_no_solution(self):
        with self.assertRaises(ValueError):
            solve(INVALID)

    def test_multiple_solutions_detected(self):
        count = solve_count(MULTI, limit=3)
        self.assertGreaterEqual(count, 2)
        _, unique = solve(MULTI)
        self.assertFalse(unique)

    def test_count_stops_at_limit(self):
        self.assertEqual(solve_count(EASY, limit=2), 1)


class TestDifficulty(unittest.TestCase):
    def test_easy_puzzle_scores_low(self):
        name, score = difficulty(EASY)
        self.assertIn(name, ("trivial", "easy", "medium"))
        self.assertLess(score, 90)

    def test_hard_puzzle_scores_higher_than_easy(self):
        _, easy_score = difficulty(EASY)
        _, hard_score = difficulty(HARD)
        self.assertGreater(hard_score, easy_score)

    def test_names_cover_all_scores(self):
        from sudoku_solver.solver import Difficulty

        for score in (0, 4, 6, 50, 100, 500, 99999):
            self.assertTrue(Difficulty.name_for(score))


class TestExplain(unittest.TestCase):
    def test_explains_easy_puzzle_without_guessing(self):
        steps = explain(EASY)
        self.assertTrue(steps[-1].startswith("solved"))
        self.assertTrue(any("only place" in step for step in steps))

    def test_explains_exhausted_grid(self):
        steps = explain(HARD, max_steps=200)
        self.assertTrue(
            any("search" in step or "solved" in step for step in steps)
        )


if __name__ == "__main__":
    unittest.main()
