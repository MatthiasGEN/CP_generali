# Hospital roster (COP) — minimal OR-Tools CP-SAT with per-week caps and schedule
from math import ceil
from ortools.sat.python import cp_model

def roster():
    model = cp_model.CpModel()

    # --- Instance (feasible toy case) ---
    E, D, S = 7, 14, 3            # employees, days, shifts/day
    req = [2, 2, 1]               # required headcount per shift: [M, D, N]
    shift_names = ["M", "D", "N"]

    week_len = 7                  # days per week
    max_per_week = 5              # cap per employee per week

    # --- 1) Decisions & domains ---
    x = [[[model.NewBoolVar(f"x[e{e},d{d},s{s}]") for s in range(S)]
          for d in range(D)] for e in range(E)]

    # --- 2) Rules (hard constraints) ---
    # Coverage: sum_e x[e,d,s] == req[s] for each day/shift
    for d in range(D):
        for s in range(S):
            model.Add(sum(x[e][d][s] for e in range(E)) == req[s])

    # At most one shift per day per employee
    for e in range(E):
        for d in range(D):
            model.Add(sum(x[e][d][s] for s in range(S)) <= 1)

    # Per-week cap (handles final short week if D % week_len != 0)
    weeks = [(w, min(w + week_len, D)) for w in range(0, D, week_len)]
    for e in range(E):
        for (lo, hi) in weeks:
            days_in_window = hi - lo
            cap = ceil(max_per_week * days_in_window / week_len)
            model.Add(sum(x[e][d][s] for d in range(lo, hi) for s in range(S)) <= cap)

    # Weekly load over full horizon (for fairness objective)
    t = [model.NewIntVar(0, D, f"t[e{e}]") for e in range(E)]
    for e in range(E):
        model.Add(t[e] == sum(x[e][d][s] for d in range(D) for s in range(S)))

    # --- 3) Objective: minimize fairness gap max(t) - min(t) ---
    T_max = model.NewIntVar(0, D, "T_max")
    T_min = model.NewIntVar(0, D, "T_min")
    model.AddMaxEquality(T_max, t)
    model.AddMinEquality(T_min, t)
    gap = model.NewIntVar(0, D, "gap")
    model.Add(gap == T_max - T_min)
    model.Minimize(gap)

    # --- 4) Solve ---
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    status = solver.Solve(model)

    status_names = {
        cp_model.OPTIMAL: "OPTIMAL",
        cp_model.FEASIBLE: "FEASIBLE",
        cp_model.INFEASIBLE: "INFEASIBLE",
        cp_model.MODEL_INVALID: "MODEL_INVALID",
        cp_model.UNKNOWN: "UNKNOWN",
    }
    print(f"Status: {status_names.get(status, 'UNKNOWN')}")

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("gap =", solver.Value(gap), "loads:", [solver.Value(v) for v in t])
        # Employee x Day grid (M/D/N or '-')
        header = "    " + " ".join(f"D{d:02d}" for d in range(D))
        print(header)
        for e in range(E):
            row = []
            for d in range(D):
                assigned = "-"
                for s in range(S):
                    if solver.Value(x[e][d][s]):
                        assigned = shift_names[s]
                        break
                row.append(assigned)
            print(f"E{e} " + " ".join(f"{c:>3}" for c in row))
    else:
        print("No schedule (check feasibility/caps/req).")

if __name__ == "__main__":
    roster()
