import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lasa_pilot.tools import (  # noqa: E402
    answer_decision_question,
    compare_cities,
    estimate_attendance,
    estimate_travel_cost,
    flag_confidence,
    lookup_historical_attendance,
    validate_simulation,
)


class ToolTests(unittest.TestCase):
    def test_simulation_passes_its_own_rules(self):
        report = validate_simulation()
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["row_count"], 8)

    def test_lookup_finds_simulated_barcelona_rows(self):
        result = lookup_historical_attendance(city="Barcelona")
        self.assertEqual(len(result["matches"]), 2)
        self.assertTrue(all(row["data_source"] == "simulated" for row in result["matches"]))

    def test_travel_cost_uses_the_supplied_scenario(self):
        result = estimate_travel_cost("Barcelona", usd_per_km=0.1, hubs=("Madrid",))
        distance = result["by_hub"][0]["distance_km"]
        self.assertEqual(result["by_hub"][0]["scenario_cost_usd"], round(distance * 0.1, 2))
        self.assertIn("not a live airfare", result["note"])

    def test_unseen_city_has_no_point_estimate_when_guarded(self):
        guarded = estimate_attendance("Rome", guardrails=True)
        unguarded = estimate_attendance("Rome", guardrails=False)
        self.assertIsNone(guarded["estimate"])
        self.assertIsNotNone(unguarded["estimate"])
        self.assertEqual(flag_confidence("Rome")["flag"], "no_comparable_host")

    def test_comparison_does_not_rank(self):
        result = compare_cities(guardrails=True)
        self.assertIsNone(result["predictive_rank"])
        rome = next(row for row in result["rows"] if row["city"] == "Rome")
        barcelona = next(row for row in result["rows"] if row["city"] == "Barcelona")
        self.assertIsNone(rome["attendance_estimate"])
        self.assertIsNotNone(barcelona["attendance_estimate"])
        self.assertEqual(rome["host_feasibility"], "unverified")

    def test_profitability_question_is_refused_when_guarded(self):
        question = "Will Rome be financially successful?"
        guarded = answer_decision_question(question, guardrails=True)
        unguarded = answer_decision_question(question, guardrails=False)
        self.assertTrue(guarded["refused"])
        self.assertIn("paid-registration", guarded["answer"])
        self.assertFalse(unguarded["refused"])
        self.assertIn("Guardrails are off", unguarded["answer"])


if __name__ == "__main__":
    unittest.main()
