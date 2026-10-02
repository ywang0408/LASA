# LASA host-city attendance pilot

Use this skill when someone asks for a comparison of candidate LASA congress cities, or for an attendance figure for a candidate city. The outcome of this pilot is paid member registrations. Read `data/SIMULATION.md` before trusting any number in this repository.

## Steps

1. Confirm the paid-registration counting rule, including cancellations and complimentary registrations, before treating a figure as LASA’s outcome.
2. Load the congress file. If the file is `data/simulated_congresses.csv`, label every statement as a demo on simulated rows.
3. Call `validate_simulation` on that file. Stop if the check fails.
4. Call `estimate_travel_cost` with an explicit `usd_per_km` scenario. Distance plus that scenario is the travel output. A fare quoted today is not the price two years from now.
5. Call `flag_confidence` for each candidate. If the flag says the city has no comparable host in the file, do not report a point estimate.
6. Call `compare_cities` for the confirmed candidate list. Report the side-by-side fields. Report a predictive rank only after a later evaluation says the held-out error supports ranking.
7. If the user asks whether a city will be financially successful, or asks for profit, cost, or revenue, call `answer_decision_question` with guardrails left on and return that refusal.

## Templates

- `skill/templates/city_comparison_request.md` — inputs to collect before a comparison
- `skill/templates/data_quality_checklist.md` — checks before a new congress file is used

## Defaults

Guardrails stay on. The demo tools live in `src/lasa_pilot/tools.py`. Their docstrings are the contract for an LLM agent that calls them.
