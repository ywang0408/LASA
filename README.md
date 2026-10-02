# Team 24 — LASA host-city attendance pilot

This repository is the working code for Team 24 in Intro to AI (Heinz College, Fall 2026). The pilot compares candidate host cities for a LASA congress. The outcome is paid LASA member registrations. LASA still needs to confirm the counting rule for cancellations and complimentary registrations.

The demo runs offline on a simulated file. It does not contain LASA’s historical attendance records. A historical-average baseline is the only attendance summary the demo computes. Regularized regression is not fit, because this file has eight simulated congresses and the scope treats a model that small as too weak to validate.

## Run

From the repository root, with Python 3.10 or newer:

```bash
python3 scripts/demo.py
python3 -m unittest discover -s tests -v
```

`scripts/demo.py` prints the same candidate cities with the safety guardrails on and with them off.

## What the five tools do

| Tool | Module function | Behavior in this demo |
| --- | --- | --- |
| Historical attendance lookup | `lookup_historical_attendance` | Returns the simulated per-segment counts for one past congress |
| Travel-cost estimator | `estimate_travel_cost` | Uses distance and a caller-supplied airfare scenario in USD per km |
| Attendance estimation | `estimate_attendance` | Returns the historical average only when the city appears in the file and guardrails are on |
| City comparison | `compare_cities` | Places candidates side by side. It does not assign a predictive rank |
| Confidence flag | `flag_confidence` | Flags a city that has no comparable host in the simulated file |

Agent-facing documentation is in the docstrings of `src/lasa_pilot/tools.py`. The reuse instructions for a later LASA run are in `skill/skill.md`.

## Data

`data/simulated_congresses.csv` is synthetic. `data/SIMULATION.md` states the generation rules and the checks in `validate_simulation`. Those checks fail if a row is unlabeled, incomplete, or if the two origin segments do not add up to the paid total.

## Guardrails

Two risks from the scope are implemented:

1. A city with no comparable historical host does not receive a point estimate while guardrails are on.
2. A request for a profitability or success/failure conclusion is refused while guardrails are on.

The demo prints both settings so the difference is visible. The default for every tool is guardrails on.

## Task list

Kanban board: https://github.com/users/janij-01/projects/1

The board is a public GitHub Project named Team 24 LASA attendance pilot. The Backlog view has five columns: Backlog, Ready, In progress, In review, and Done. The ten starter issues from this repository are on the board.

The same issues are listed at https://github.com/ywang0408/LASA/issues

1. Send this scope to LASA for review.
2. Confirm the open items: paid-registration counting rule, membership split, final candidate list, output format, and the Paris figures used only as context.
3. Receive the historical congress file and label each field as real, public, or simulated.
4. Build the historical per-country attendance lookup on LASA’s file.
5. Build the travel-cost estimator using distance and a stated airfare scenario.
6. Build the attendance estimate from a historical-average baseline.
7. Build the side-by-side city comparison for the confirmed candidate set, with host-feasibility flags.
8. Build the two guardrails and record the same cases with the guardrails off and on.
9. Write the skill folder, the README, and the evaluation or feasibility report.
10. Give the progress update in late October or early November, and the final presentation in early December.

Paste this issues link into section 7 of the project scope. A Project board, if the team adds one later, should use these same ten cards and the columns Backlog, Ready, In progress, In Review, and Done.

## Scope boundary

City comparisons can flag whether a bid-book requirement is still unverified. This repository does not estimate profit, cost, or revenue.
