"""Scenario generation service."""

from __future__ import annotations

from typing import List

from core.models import Scenario
from core.openai_service import OpenAIService
from prompts.scenario_prompts import build_scenario_prompt


class ScenarioGenerator:
    """Generates scenarios through OpenAIService."""

    def __init__(self, openai_service: OpenAIService) -> None:
        self.openai_service = openai_service

    def generate(self, pillar: str, module: str, concept: str, difficulty: str, historical_weak_concepts: List[str]) -> Scenario:
        prompt = build_scenario_prompt(pillar, module, concept, difficulty, historical_weak_concepts)
        payload = self.openai_service.generate_json(
            prompt,
            schema_name="scenario",
            expected_fields=[
                "title",
                "pillar",
                "module",
                "primary_concepts",
                "difficulty",
                "scenario_text",
                "background_context",
                "data_points",
                "question_to_user",
                "ideal_reasoning_targets",
            ],
        )
        if "error" in payload:
            payload = self.openai_service.generate_json("", schema_name="scenario")
        return Scenario.from_dict(payload)
