# Job shop (COP) — wide, pretty ASCII Gantt using full terminal width
# - Dots for idle, digits (job id) for busy
# - Auto-scales to terminal width
# - Shows compact segment list + full-width Gantt per machine

import shutil
from math import ceil
from ortools.sat.python import cp_model

def jobshop():
    # -------- Instance --------
    jobs = [
        [(0, 3), (1, 2), (2, 2)],  # Job 0
        [(0, 2), (2, 1), (1, 4)],  # Job 1
        [(1, 4), (2, 3), (0, 2)],  # Job 2
    ]
    J = len(jobs)
    M = 1 + max(m for job in jobs for (m, _) in job)  # machines
    horizon = sum(d for job in jobs for (_, d) in job)

    # -------- Model --------
    model = cp_model.CpModel()
    start, end, interval = {}, {}, {}
    for j in range(J):
        for k, (m, d) in enumerate(jobs[j]):
            s = model.NewIntVar(0, horizon, f"s[{j},{k}]")
            e = model.NewIntVar(0, horizon, f"e[{j},{k}]")
            itv = model.NewIntervalVar(s, d, e, f"itv[{j},{k}]")
            start[(j, k)], end[(j, k)], interval[(j, k)] = s, e, itv

    for j in range(J):
        for k in range(len(jobs[j]) - 1):
            model.Add(start[(j, k+1)] >= end[(j, k)])
    for m in range(M):
        model.AddNoOverlap([interval[(j, k)]
                            for j in range(J)
                            for k, (mm, _) in enumerate(jobs[j]) if mm == m])

    makespan = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(makespan, [end[(j, len(jobs[j]) - 1)] for j in range(J)])
    model.Minimize(makespan)

    # -------- Solve --------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("No schedule found.")
        return

    ms = solver.Value(makespan)

    # -------- Collect segments per machine --------
    per_machine = {m: [] for m in range(M)}
    for j in range(J):
        for k, (m, d) in enumerate(jobs[j]):
            s = solver.Value(start[(j, k)])
            e = solver.Value(end[(j, k)])
            per_machine[m].append((s, e, j, k, d))
    for m in range(M):
        per_machine[m].sort(key=lambda x: x[0])

    # -------- Pretty print: segment list --------
    for m in range(M):
        segs = [f"J{j}: [{s}..{e})" for (s, e, j, k, d) in per_machine[m]]
        print(f"M{m}: " + " | ".join(segs))
    print()

    # -------- Pretty print: full-width Gantt --------
    # Compute usable width
    term_cols = shutil.get_terminal_size(fallback=(100, 24)).columns
    label_width = len(f"M{M-1}: ")  # left label per line
    min_chart = 40
    chart_width = max(min_chart, term_cols - label_width - 1)

    # Scale time -> columns
    scale = max(1, ceil(ms / chart_width))           # time units per column
    cols = max(1, ceil(ms / scale))                  # columns actually used

    # Time ruler (tens and ones for the *start* of each column)
    tens = []
    ones = []
    for c in range(cols):
        t0 = c * scale
        tens.append(str((t0 // 10) % 10) if t0 % 10 == 0 else " ")
        ones.append(str(t0 % 10))
    # print("T:  " + "".join(tens))
    print("T:  " + "".join(ones))
    print("    " + "-" * cols)

    def draw_machine(m):
        line = ["." for _ in range(cols)]
        for (s, e, j, k, d) in per_machine[m]:
            c1 = s // scale
            c2 = max(c1, (e - 1) // scale)  # inclusive end col, ensure >= c1
            c1 = max(0, min(cols - 1, c1))
            c2 = max(0, min(cols - 1, c2))
            for c in range(c1, c2 + 1):
                line[c] = str(j % 10)
        return "".join(line)

    for m in range(M):
        print(f"M{m}: " + draw_machine(m))

    print(f"\nMakespan: {ms}  (scale: 1 col = {scale} time unit{'s' if scale>1 else ''})")

if __name__ == "__main__":
    jobshop()
