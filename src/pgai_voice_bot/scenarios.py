from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENARIO_FILE = ROOT / "scenarios.json"


@dataclass(frozen=True)
class Scenario:
    id: str
    goal: str
    persona: str
    facts: list[str]
    edge: str

    def instructions(self) -> str:
        facts = "\n".join(f"- {fact}" for fact in self.facts)
        return f"""
You are calling a medical-practice AI phone agent as a realistic patient simulator.
You are not an assistant to the practice; you are the patient on the phone.

Scenario id: {self.id}
Patient persona: {self.persona}
Conversation goal: {self.goal}
Known facts:
{facts}
Edge-case focus: {self.edge}

Behavior rules:
- Speak naturally and briefly, like a real caller.
- Let the practice agent lead intake, but actively steer toward the scenario goal.
- Do not reveal that this is a test unless directly asked if you are a bot.
- If the agent asks for unavailable personal data, provide plausible placeholders.
- If the agent gives unsafe, contradictory, or impossible guidance, ask one calm follow-up.
- End the call politely once the goal is complete or the agent cannot proceed.
"""


def load_scenarios(path: Path = DEFAULT_SCENARIO_FILE) -> list[Scenario]:
    rows = json.loads(path.read_text())
    return [Scenario(**row) for row in rows]


def get_scenario(scenario_id: str, path: Path = DEFAULT_SCENARIO_FILE) -> Scenario:
    for scenario in load_scenarios(path):
        if scenario.id == scenario_id:
            return scenario
    raise KeyError(f"Unknown scenario id: {scenario_id}")
