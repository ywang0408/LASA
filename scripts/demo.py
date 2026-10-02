#!/usr/bin/env python3
"""Print the attendance pilot once with guardrails on and once with them off."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lasa_pilot.tools import (  # noqa: E402
    answer_decision_question,
    compare_cities,
    validate_simulation,
)


def main() -> None:
    quality = validate_simulation()
    print("Simulation check")
    print(json.dumps(quality, indent=2))
    question = "Will this LASA conference be financially successful?"
    for guardrails in (True, False):
        print(f"\nGuardrails {'on' if guardrails else 'off'}")
        print(json.dumps(compare_cities(guardrails=guardrails), indent=2))
        print(json.dumps(answer_decision_question(question, guardrails=guardrails), indent=2))


if __name__ == "__main__":
    main()
