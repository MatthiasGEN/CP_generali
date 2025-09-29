# Sudoku (CSP) — minimal OR-Tools CP-SAT example
from ortools.sat.python import cp_model

def sudoku():
    model = cp_model.CpModel()

    # 1) Decisions & domains
    X = [[model.NewIntVar(1, 9, f"x[{r}][{c}]") for c in range(9)] for r in range(9)]

    # 2) Rules (constraints)
    # Rows / Columns
    for r in range(9):
        model.AddAllDifferent(X[r])
    for c in range(9):
        model.AddAllDifferent([X[r][c] for r in range(9)])
    # 3x3 Boxes
    for br in range(3):
        for bc in range(3):
            box = [X[r][c]
                   for r in range(br*3, br*3+3)
                   for c in range(bc*3, bc*3+3)]
            model.AddAllDifferent(box)

    # (Optional) A tiny puzzle (0 = unknown)
    givens = [
        [5,3,0, 0,7,0, 0,0,0],
        [6,0,0, 1,9,5, 0,0,0],
        [0,9,8, 0,0,0, 0,6,0],
        [8,0,0, 0,6,0, 0,0,3],
        [4,0,0, 8,0,3, 0,0,1],
        [7,0,0, 0,2,0, 0,0,6],
        [0,6,0, 0,0,0, 2,8,0],
        [0,0,0, 4,1,9, 0,0,5],
        [0,0,0, 0,8,0, 0,7,9],
    ]
    for r in range(9):
        for c in range(9):
            if givens[r][c] != 0:
                model.Add(X[r][c] == givens[r][c])

    # 3) Objective: none (CSP)

    # 4) Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    status = solver.Solve(model)

    # Minimal output
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for r in range(9):
            print(" ".join(str(solver.Value(X[r][c])) for c in range(9)))

if __name__ == "__main__":
    sudoku()
