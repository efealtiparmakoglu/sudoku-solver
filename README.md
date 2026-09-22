# sudoku-solver

Sudoku solver with **constraint propagation + MRV backtracking**,
uniqueness checking, difficulty scoring and step narration. Pure
standard library.

```text
$ sudoku-solver solve "4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......"
417|369|825
632|158|947
958|724|316
------+-------+------
825|437|169
791|586|432
346|912|758
------+-------+------
289|643|571
573|291|684
164|875|293
unique

$ sudoku-solver explain "003020600900305001001806400008102900700000008006708200002609500800203009005010300"
A6 = 1 (only place in row A)
I6 = 7 (only place in column 6)
...
solved with 54 placement(s), no guessing
```

## How it works

- **Constraint propagation** (Norvig-style): assigning a digit eliminates
  it from peers; a cell dropping to one candidate cascades further, and
  when a digit has only one possible home in a unit it is placed
  immediately. The cascade starts from the givens and repeats until the
  solved-cell count stabilizes.
- **Search** — when propagation stalls, backtracking branches on the
  most-constrained cell (fewest candidates first).
- **Uniqueness** — `count` searches for a second solution and stops at
  two; `solve` reports whether the puzzle is proper.
- **Difficulty** — score = propagation rounds + 30 per forced guess,
  banded trivial / easy / medium / hard / expert.
- **Explain** — narrates the cascade's placements ("A6 = 1 — only place
  in row A") so human players can follow; easy grids solve without a
  single guess.

## Usage

```
sudoku-solver solve "<81-char grid>"
sudoku-solver explain "<grid>"
sudoku-solver count "<grid>"
sudoku-solver difficulty "<grid>"
```

Grid: 81 characters row by row, `.` or `0` for empties; line breaks and
box-drawing pipes are tolerated. Exit codes: 0 ok, 1 invalid/unsolvable
grid, 2 usage error.

## Development

```console
$ python3 -m unittest discover -s tests   # 14 tests
```

The test suite covers the AI Escargot puzzle (solves instantly once
propagation is wired correctly — wiring it incorrectly costs 113
seconds, ask the test author).

## License

MIT — see [LICENSE](LICENSE).
